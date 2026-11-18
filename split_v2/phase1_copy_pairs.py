"""
Phase 1: One consolidated copy list
SESSION_SPLIT_V2 - DECAFIA Paper 1

Computes 64-bit DCT pHash with min-dihedral distance over all 2315 images,
classifies pairs into Tier A (merge) and Tier B (verify), runs SIFT on Tier B
cross-split pairs, and outputs copy_pairs.csv + contact sheets.

No imagehash dependency - DCT pHash implemented via cv2.dct.
"""

import os, sys, json, time
from pathlib import Path
import numpy as np
import cv2
import pandas as pd
from collections import defaultdict
import random

REPO          = Path("C:/Users/luise/temp/decafia-research")
DATASET_ROOT  = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
SPLIT_V2_DIR  = REPO / "split_v2"
CACHE_DIR     = REPO / "_cache"
SPLIT_V2_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = SPLIT_V2_DIR / "PROGRESS.md"

def log(msg):
    print(msg, flush=True, end="\n")

def update_progress(**kwargs):
    lines = ["# PROGRESS.md\n", f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
    # read existing
    existing = {}
    if PROGRESS_FILE.exists():
        for line in PROGRESS_FILE.read_text().splitlines():
            if line.startswith("- "):
                k, _, v = line[2:].partition(": ")
                existing[k] = v
    existing.update(kwargs)
    for k, v in existing.items():
        lines.append(f"- {k}: {v}\n")
    PROGRESS_FILE.write_text("".join(lines))

update_progress(**{"Phase 1 - hash computation": "in_progress"})

# ── 1. Load assignments ───────────────────────────────────────────────────────
log("\n=== Phase 1: loading assignments ===")
assign_df = pd.read_csv(REPO / "splits/grouped_v1/assignments.csv")
# split_old = physical directory on disk; split_new = logical v1 assignment
assign_df = assign_df.rename(columns={"split_new": "split_v1", "split_old": "split_disk"})

def image_path(stem, split_disk):
    """Images are stored by split_old (physical location), not split_new (logical)."""
    return DATASET_ROOT / "images" / split_disk / f"{stem}.jpg"

# Verify all images exist
missing = [str(image_path(r.stem, r.split_disk))
           for r in assign_df.itertuples() if not image_path(r.stem, r.split_disk).exists()]
if missing:
    log(f"[FAIL] {len(missing)} images missing. First 5: {missing[:5]}")
    sys.exit(1)

stems       = assign_df["stem"].tolist()
splits      = assign_df["split_v1"].tolist()   # logical v1 split (used for copy detection)
splits_disk = assign_df["split_disk"].tolist() # physical dir (used for imread)
stem_to_split_disk = dict(zip(stems, splits_disk))
N      = len(stems)
log(f"All {N} images found. Logical split counts: {assign_df['split_v1'].value_counts().to_dict()}")

# ── 2. DCT pHash ──────────────────────────────────────────────────────────────
def dct_phash_64(img_bgr):
    """64-bit DCT perceptual hash using cv2.dct (no imagehash needed)."""
    gray    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    dct     = cv2.dct(resized)
    top64   = dct[:8, :8].flatten()      # 64 coefficients incl. DC
    ac      = top64[1:]                   # exclude DC for mean
    mean_ac = ac.mean()
    bits    = (top64 > mean_ac)
    val     = np.uint64(0)
    for i, b in enumerate(bits):
        if b:
            val |= (np.uint64(1) << np.uint64(i))
    return val

def eight_dihedral(img_bgr):
    """8 dihedral variants: (flip=0,1) x (rot=0,90,180,270)."""
    out = []
    for flip in (None, 1):
        base = cv2.flip(img_bgr, flip) if flip is not None else img_bgr
        for rot in range(4):
            v = np.rot90(base, rot)
            out.append(np.ascontiguousarray(v))
    return out  # 8 variants

# ── 3. Compute / load hashes ──────────────────────────────────────────────────
HASH_CACHE       = CACHE_DIR / "dihedral_hashes_u64.npy"
HASH_CACHE_STEMS = CACHE_DIR / "dihedral_hashes_stems.json"

need_recompute = True
if HASH_CACHE.exists() and HASH_CACHE_STEMS.exists():
    if json.loads(HASH_CACHE_STEMS.read_text()) == stems:
        hashes_u64 = np.load(HASH_CACHE)
        hashes_u64 = hashes_u64.astype(np.uint64)  # ensure correct dtype
        log(f"[cache] Loaded hashes {hashes_u64.shape} dtype={hashes_u64.dtype}")
        need_recompute = False
    else:
        log("[cache] Stems changed, recomputing hashes")

if need_recompute:
    log(f"Computing 64-bit DCT pHash for {N} images x 8 transforms...")
    # Store as uint64 view of uint8 array to avoid object dtype
    # We'll accumulate as Python list of int then convert
    hash_list = []  # list of list of int (N x 8)
    t0 = time.time()
    for i, (stem, split) in enumerate(zip(stems, splits_disk)):
        img = cv2.imread(str(image_path(stem, split)))
        if img is None:
            log(f"[WARN] Cannot read {stem}")
            hash_list.append([0] * 8)
            continue
        row = [int(dct_phash_64(v)) & 0xFFFFFFFFFFFFFFFF for v in eight_dihedral(img)]
        hash_list.append(row)
        if (i + 1) % 500 == 0:
            log(f"  {i+1}/{N}  {time.time()-t0:.1f}s")
    # Store as uint64 - values are 64-bit patterns so uint64 is correct dtype
    hashes_u64 = np.array(hash_list, dtype=np.uint64)   # (N, 8)
    np.save(HASH_CACHE, hashes_u64)
    HASH_CACHE_STEMS.write_text(json.dumps(stems))
    log(f"Hashes saved. Elapsed: {time.time()-t0:.1f}s")

# ── 4. All-pairs min-dihedral distance (vectorized) ───────────────────────────
log(f"\nComputing all-pairs min-dihedral Hamming distance (N={N})...")
update_progress(**{"Phase 1 - hash computation": "done", "Phase 1 - all-pairs distance": "in_progress"})

PAIRS_CACHE = CACHE_DIR / "candidate_pairs_le12.csv"

if PAIRS_CACHE.exists():
    log(f"[cache] Loading candidate pairs from {PAIRS_CACHE}")
    cand_df = pd.read_csv(PAIRS_CACHE)
    log(f"[cache] {len(cand_df)} pairs loaded")
else:
    # LUT: popcount of single byte
    lut = np.array([bin(i).count('1') for i in range(256)], dtype=np.uint8)

    def popcount_u64_matrix(xor_matrix):
        """(N, N) uint64 → (N, N) uint8 Hamming distances via byte LUT."""
        # view each uint64 as 8 bytes; sum popcount per byte
        x = xor_matrix.view(np.uint8).reshape(xor_matrix.shape[0], xor_matrix.shape[1], 8)
        return lut[x].sum(axis=2).astype(np.uint8)

    h0 = hashes_u64[:, 0]  # (N,) base hash per image (uint64)
    # d1[i, j] = min_k hamming(h0[i], hashes_u64[j, k])
    # We compute as uint8 (max 64 fits in uint8)
    d1 = np.full((N, N), 64, dtype=np.uint8)
    t0 = time.time()
    for k in range(8):
        hk = hashes_u64[:, k]        # (N,)
        xor_k = h0[:, None] ^ hk[None, :]  # (N, N) uint64
        dist_k = popcount_u64_matrix(xor_k)
        d1 = np.minimum(d1, dist_k)
        log(f"  transform k={k}: {time.time()-t0:.1f}s")

    # Symmetrize: d_sym[i,j] = min(d1[i,j], d1[j,i])
    d_sym = np.minimum(d1, d1.T)
    np.fill_diagonal(d_sym, 64)   # exclude self-pairs

    THRESHOLD = 12
    rows_i, rows_j = np.where((d_sym <= THRESHOLD) &
                               (np.arange(N)[:, None] < np.arange(N)[None, :]))
    log(f"Found {len(rows_i)} pairs with min-dihedral distance <= {THRESHOLD} in {time.time()-t0:.1f}s")

    rows = []
    for i, j in zip(rows_i, rows_j):
        rows.append({
            "stem_a":   stems[i],
            "split_a":  splits[i],
            "stem_b":   stems[j],
            "split_b":  splits[j],
            "min_dihedral_dist": int(d_sym[i, j]),
        })
    cand_df = pd.DataFrame(rows)
    cand_df.to_csv(PAIRS_CACHE, index=False)
    log(f"Candidate pairs saved to {PAIRS_CACHE}")

update_progress(**{"Phase 1 - all-pairs distance": "done"})

# ── 5. Augment with September SIFT-verified pairs ────────────────────────────
log("\nLoading September SIFT-verified pairs...")
sept_sift = pd.read_csv(REPO / "audits/augmented_copies/sift_results.csv")
# RANSAC-verified: inliers >= 30, hull_coverage >= 0.50
sept_verified = sept_sift[(sept_sift["inliers"] >= 30) & (sept_sift["hull_coverage"] >= 0.50)].copy()
log(f"September verified pairs: {len(sept_verified)}, unique queries: {sept_verified['query_stem'].nunique()}")

# Build set of September verified pair keys (stem_a, stem_b) normalized
sept_pairs_set = set()
sept_backdrop_set = set()
for _, row in sept_verified.iterrows():
    a, b = row["query_stem"], row["train_stem"]
    key = tuple(sorted([a, b]))
    sept_pairs_set.add(key)
    if row["backdrop_flag"]:
        sept_backdrop_set.add(key)
log(f"Unique September verified pair keys: {len(sept_pairs_set)}, backdrop: {len(sept_backdrop_set)}")

# November pairs
log("Loading November integrity pairs...")
nov_df = pd.read_csv(
    Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/paper1/integrity/near_copy_pairs_d_le_12.csv")
)
# Columns: a, split_a, b, split_b, min_dihedral_phash_dist, identity_phash_dist
nov_pairs_set = set()
for _, row in nov_df.iterrows():
    key = tuple(sorted([row["a"], row["b"]]))
    nov_pairs_set.add(key)
log(f"November pairs: {len(nov_df)}, unique keys: {len(nov_pairs_set)}")

# ── 6. Build unified candidate set ────────────────────────────────────────────
log("\nBuilding unified candidate set...")

# Start from our fresh pHash pairs <= 12
our_pairs = {}
for _, row in cand_df.iterrows():
    key = tuple(sorted([row["stem_a"], row["stem_b"]]))
    our_pairs[key] = {
        "stem_a": row["stem_a"], "split_a": row["split_a"],
        "stem_b": row["stem_b"], "split_b": row["split_b"],
        "min_dihedral_dist": row["min_dihedral_dist"],
    }

# Add September SIFT-verified pairs not in our set (with distance -1 = SIFT-only)
stem_to_split = dict(zip(stems, splits))  # logical split lookup

sift_only_added = 0
for _, row in sept_verified.iterrows():
    a, b = row["query_stem"], row["train_stem"]
    key = tuple(sorted([a, b]))
    if key not in our_pairs:
        sa = stem_to_split.get(a, "unknown")
        sb = stem_to_split.get(b, "unknown")
        our_pairs[key] = {
            "stem_a": a, "split_a": sa,
            "stem_b": b, "split_b": sb,
            "min_dihedral_dist": -1,  # not found by pHash, only by SIFT
        }
        sift_only_added += 1
log(f"Added {sift_only_added} SIFT-only pairs not found by pHash <= 12")

log(f"Total unified candidates: {len(our_pairs)}")

# ── 7. Classify: Tier A / Tier B / within-split ───────────────────────────────
log("\nClassifying pairs into tiers...")

def is_cross_split(split_a, split_b):
    return split_a != split_b

# For green leaf HSV mask fraction - needed for Tier A RANSAC check
# We'll compute it lazily during SIFT verification

rows_out = []
tier_a_cross = []
tier_b_cross = []

for key, pair in our_pairs.items():
    a, b   = pair["stem_a"], pair["stem_b"]
    sa, sb = pair["split_a"], pair["split_b"]
    d      = pair["min_dihedral_dist"]
    cross  = is_cross_split(sa, sb)

    # In-September-verified?
    in_sept = key in sept_pairs_set
    is_backdrop = key in sept_backdrop_set

    # In-November?
    in_nov = key in nov_pairs_set

    # Determine tier
    # Tier A: d <= 4, OR (Sept-RANSAC verified AND NOT backdrop)
    if d != -1 and d <= 4:
        tier = "A"
        reason = f"pHash_dist={d}<=4"
    elif in_sept and not is_backdrop:
        tier = "A"
        reason = "sept_sift_verified_leaf"
    elif (d != -1 and 5 <= d <= 8) or (in_sept and is_backdrop):
        tier = "B"
        reason = f"pHash_dist={d}" if d != -1 else "sept_backdrop"
    elif d != -1 and d <= 12:
        tier = "C"   # too far, only catalog; not merged
        reason = f"pHash_dist={d}>8"
    else:
        tier = "C"
        reason = "sift_only_no_phash"

    rows_out.append({
        "stem_a": a, "split_a": sa,
        "stem_b": b, "split_b": sb,
        "cross_split": cross,
        "min_dihedral_dist": d,
        "in_sept_verified": in_sept,
        "is_sept_backdrop": is_backdrop,
        "in_nov": in_nov,
        "tier": tier,
        "decision": "pending" if (tier in ("A", "B") and cross) else ("merge" if tier == "A" else "reject"),
        "inliers": np.nan, "hull_coverage": np.nan,
        "reason": reason,
    })
    if cross:
        if tier == "A":
            tier_a_cross.append((a, b, sa, sb, d))
        elif tier == "B":
            tier_b_cross.append((a, b, sa, sb, d))

log(f"Tier A total: {sum(1 for r in rows_out if r['tier']=='A')}")
log(f"Tier A cross-split: {len(tier_a_cross)}")
log(f"Tier B total: {sum(1 for r in rows_out if r['tier']=='B')}")
log(f"Tier B cross-split: {len(tier_b_cross)}")
log(f"Tier C (catalog only): {sum(1 for r in rows_out if r['tier']=='C')}")

# Mark all Tier A cross-split as merge
for r in rows_out:
    if r["tier"] == "A" and r["cross_split"]:
        r["decision"] = "merge"
    elif r["tier"] == "A" and not r["cross_split"]:
        r["decision"] = "merge_within"

# ── 8. SIFT verification for Tier B cross-split pairs ────────────────────────
log(f"\n=== SIFT verification for {len(tier_b_cross)} Tier B cross-split pairs ===")
update_progress(**{"Phase 1 - SIFT Tier B": "in_progress"})

def green_leaf_mask(img_bgr):
    """HSV green-leaf mask: H∈[35,85], S>40, V>40."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = (
        (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85) &
        (hsv[:, :, 1] >  40) &
        (hsv[:, :, 2] >  40)
    ).astype(np.uint8) * 255
    return mask

def sift_verify_pair(path_a, path_b, min_inliers=30, min_coverage=0.50,
                     best_dihedral_k=None):
    """
    Run SIFT+RANSAC on a pair restricted to leaf mask.
    Tries all 8 dihedral variants of image b, picks best.
    Returns (inliers, hull_coverage, variant_k) or (0, 0.0, -1) if failed.
    """
    img_a = cv2.imread(str(path_a))
    img_b = cv2.imread(str(path_b))
    if img_a is None or img_b is None:
        return 0, 0.0, -1

    # Resize to max 1024px on longest side
    def resize_max(img, max_side=1024):
        h, w = img.shape[:2]
        s = max_side / max(h, w)
        if s < 1.0:
            img = cv2.resize(img, (int(w*s), int(h*s)), interpolation=cv2.INTER_AREA)
        return img

    img_a = resize_max(img_a)

    sift = cv2.SIFT_create()
    mask_a = green_leaf_mask(img_a)
    kp_a, des_a = sift.detectAndCompute(img_a, mask_a if mask_a.any() else None)
    if des_a is None or len(kp_a) < 4:
        return 0, 0.0, -1

    best_inliers, best_cov, best_k = 0, 0.0, -1
    variants = eight_dihedral(img_b)

    for k_idx, v in enumerate(variants):
        v = resize_max(v)
        mask_b = green_leaf_mask(v)
        kp_b, des_b = sift.detectAndCompute(v, mask_b if mask_b.any() else None)
        if des_b is None or len(kp_b) < 4:
            continue

        bf = cv2.BFMatcher()
        matches_raw = bf.knnMatch(des_a, des_b, k=2)
        good = [m for m, n in matches_raw if m.distance < 0.75 * n.distance]
        if len(good) < 4:
            continue

        pts_a = np.float32([kp_a[m.queryIdx].pt for m in good])
        pts_b = np.float32([kp_b[m.trainIdx].pt for m in good])
        H, mask_inlier = cv2.findHomography(pts_a, pts_b, cv2.RANSAC, 4.0)
        if mask_inlier is None:
            continue
        n_inliers = int(mask_inlier.sum())
        if n_inliers < 4:
            continue

        # Hull coverage over leaf mask of image a
        inlier_pts = pts_a[mask_inlier.ravel() == 1]
        if len(inlier_pts) >= 3:
            hull = cv2.convexHull(inlier_pts.astype(np.float32))
            hull_area = cv2.contourArea(hull)
            # Reference: leaf mask area of img_a
            leaf_area = float(mask_a.sum()) / 255.0
            if leaf_area < 100:
                # fallback: image area
                leaf_area = float(img_a.shape[0] * img_a.shape[1])
            cov = hull_area / leaf_area if leaf_area > 0 else 0.0
        else:
            cov = 0.0

        if n_inliers > best_inliers:
            best_inliers, best_cov, best_k = n_inliers, cov, k_idx

    return best_inliers, best_cov, best_k

# Map pair keys to their row index for updating
key_to_row_idx = {}
for idx, r in enumerate(rows_out):
    key = tuple(sorted([r["stem_a"], r["stem_b"]]))
    key_to_row_idx[key] = idx

t0 = time.time()
sift_merge_count = 0
sift_reject_count = 0

for n_done, (a, b, sa, sb, d) in enumerate(tier_b_cross):
    path_a = image_path(a, stem_to_split_disk[a])
    path_b = image_path(b, stem_to_split_disk[b])
    inliers, cov, best_k = sift_verify_pair(path_a, path_b)

    key = tuple(sorted([a, b]))
    idx = key_to_row_idx[key]

    rows_out[idx]["inliers"] = inliers
    rows_out[idx]["hull_coverage"] = cov

    if inliers >= 30 and cov >= 0.50:
        rows_out[idx]["decision"] = "merge"
        rows_out[idx]["reason"] += f";sift_leaf_verified(inliers={inliers},cov={cov:.2f})"
        sift_merge_count += 1
    else:
        rows_out[idx]["decision"] = "reject"
        rows_out[idx]["reason"] += f";sift_failed(inliers={inliers},cov={cov:.2f})"
        sift_reject_count += 1

    if (n_done + 1) % 20 == 0:
        log(f"  SIFT [{n_done+1}/{len(tier_b_cross)}] merge={sift_merge_count} reject={sift_reject_count} {time.time()-t0:.1f}s")

log(f"SIFT Tier B done: merged={sift_merge_count}, rejected={sift_reject_count}")
update_progress(**{"Phase 1 - SIFT Tier B": "done"})

# ── 9. Write copy_pairs.csv ───────────────────────────────────────────────────
log("\nWriting copy_pairs.csv...")
copy_pairs_df = pd.DataFrame(rows_out, columns=[
    "stem_a", "split_a", "stem_b", "split_b", "cross_split",
    "min_dihedral_dist", "in_sept_verified", "is_sept_backdrop", "in_nov",
    "tier", "decision", "inliers", "hull_coverage", "reason"
])
# Only write pairs that are either merged or Tier B (catalogued)
out_csv = SPLIT_V2_DIR / "copy_pairs.csv"
copy_pairs_df.to_csv(out_csv, index=False)
log(f"Saved {len(copy_pairs_df)} rows to {out_csv}")

# Summary
merged_cross = copy_pairs_df[(copy_pairs_df["cross_split"]) & (copy_pairs_df["decision"] == "merge")]
log(f"\nMerged cross-split pairs: {len(merged_cross)}")
log(f"Decision counts:\n{copy_pairs_df[copy_pairs_df['cross_split']]['decision'].value_counts()}")

# ── 10. Comparison table: September vs November vs ours ──────────────────────
log("\nBuilding audit comparison table...")

# September: verified pairs (all, any split combo)
our_cross_a4 = set(tuple(sorted([r["stem_a"], r["stem_b"]]))
                   for r in rows_out
                   if r["cross_split"] and r["min_dihedral_dist"] != -1 and r["min_dihedral_dist"] <= 4)

# November cross-split <= 4
nov_cross_4 = set(
    tuple(sorted([row["a"], row["b"]]))
    for _, row in nov_df.iterrows()
    if row["split_a"] != row["split_b"] and row["min_dihedral_phash_dist"] <= 4
)

# September SIFT verified cross-split
sept_cross_verified = set(
    tuple(sorted([r["query_stem"], r["train_stem"]]))
    for _, r in sept_verified.iterrows()
    if r["query_split"] != "train"  # query is test/val
)

overlap_our_nov   = our_cross_a4 & nov_cross_4
only_our          = our_cross_a4 - nov_cross_4
only_nov          = nov_cross_4 - our_cross_a4
overlap_sept_our  = sept_cross_verified & (our_cross_a4 | set(
    tuple(sorted([r["stem_a"], r["stem_b"]]))
    for r in rows_out if r["cross_split"] and r["tier"] in ("A","B") and r["in_sept_verified"]
))

comparison = {
    "our_cross_split_d_le_4": len(our_cross_a4),
    "nov_cross_split_d_le_4": len(nov_cross_4),
    "overlap_our_and_nov": len(overlap_our_nov),
    "only_in_our": len(only_our),
    "only_in_nov": len(only_nov),
    "sept_sift_verified_cross_split": len(sept_cross_verified),
    "overlap_sept_and_our_tiers_AB": len(overlap_sept_our),
}

log("Audit comparison:")
for k, v in comparison.items():
    log(f"  {k}: {v}")

comp_path = SPLIT_V2_DIR / "audit_comparison.json"
comp_path.write_text(json.dumps(comparison, indent=2))

# ── 11. SANAS_NUEVAS vs SANAS_SOCORRO analysis ───────────────────────────────
log("\nSANAS_NUEVAS vs SANAS_SOCORRO analysis...")
sanas_pairs = copy_pairs_df[
    copy_pairs_df["stem_a"].str.startswith("SANAS_") &
    copy_pairs_df["stem_b"].str.startswith("SANAS_")
].copy()

# Cross-prefix pairs
def get_prefix(stem):
    return "_".join(stem.split("_")[:2])  # SANAS_NUEVAS or SANAS_SOCORRO

sanas_pairs["prefix_a"] = sanas_pairs["stem_a"].apply(get_prefix)
sanas_pairs["prefix_b"] = sanas_pairs["stem_b"].apply(get_prefix)
cross_prefix_sanas = sanas_pairs[sanas_pairs["prefix_a"] != sanas_pairs["prefix_b"]]
cross_prefix_cross_split = cross_prefix_sanas[cross_prefix_sanas["cross_split"]]

log(f"SANAS cross-prefix pairs (any split): {len(cross_prefix_sanas)}")
log(f"SANAS NUEVAS↔SOCORRO cross-split pairs: {len(cross_prefix_cross_split)}")
log(f"  ... at d<=4: {len(cross_prefix_cross_split[cross_prefix_cross_split['min_dihedral_dist'] <= 4])}")
log(f"  ... merged: {len(cross_prefix_cross_split[cross_prefix_cross_split['decision']=='merge'])}")

sanas_answer = {
    "question": "Are SANAS_NUEVAS images transformed copies of SANAS_SOCORRO images?",
    "nuevas_socorro_cross_prefix_any_split_pairs_d_le_4": int(len(cross_prefix_cross_split[cross_prefix_cross_split["min_dihedral_dist"] <= 4])),
    "nuevas_socorro_cross_split_merged_pairs": int(len(cross_prefix_cross_split[cross_prefix_cross_split["decision"] == "merge"])),
    "note": "Counts only; whether this represents systematic generation is not asserted from images alone."
}
(SPLIT_V2_DIR / "sanas_analysis.json").write_text(json.dumps(sanas_answer, indent=2))
log(f"SANAS answer: {sanas_answer}")

# ── 12. Contact sheets ────────────────────────────────────────────────────────
log("\nGenerating contact sheets...")
update_progress(**{"Phase 1 - contact sheets": "in_progress"})

def make_contact_sheet(pairs_list, out_path, seed=42, max_pairs=40, title=""):
    """pairs_list: list of (stem_a, split_a, stem_b, split_b, label)"""
    if not pairs_list:
        log(f"[skip] No pairs for contact sheet: {title}")
        return
    rng = random.Random(seed)
    if len(pairs_list) > max_pairs:
        pairs_list = rng.sample(pairs_list, max_pairs)

    thumb_w, thumb_h = 200, 150
    gap = 4
    n = len(pairs_list)
    sheet_w = (thumb_w * 2 + gap * 3)
    sheet_h = (thumb_h + gap) * n + gap + 20
    sheet = np.ones((sheet_h, sheet_w, 3), dtype=np.uint8) * 240

    for i, (sa, spa, sb, spb, label) in enumerate(pairs_list):
        y = gap + i * (thumb_h + gap)
        for j, (stem, split) in enumerate([(sa, spa), (sb, spb)]):
            img = cv2.imread(str(image_path(stem, stem_to_split_disk[stem])))
            if img is None:
                thumb = np.zeros((thumb_h, thumb_w, 3), dtype=np.uint8)
            else:
                thumb = cv2.resize(img, (thumb_w, thumb_h))
            x = gap + j * (thumb_w + gap)
            sheet[y:y+thumb_h, x:x+thumb_w] = thumb
        # label
        cv2.putText(sheet, label[:40], (gap, y + thumb_h + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)

    cv2.imwrite(str(out_path), sheet)
    log(f"  Saved {out_path} ({n} pairs)")

# All Tier A cross-split pairs
tier_a_pairs = [
    (r["stem_a"], r["split_a"], r["stem_b"], r["split_b"],
     f"d={r['min_dihedral_dist']} {r['split_a']}↔{r['split_b']}")
    for r in rows_out
    if r["tier"] == "A" and r["cross_split"]
]
make_contact_sheet(tier_a_pairs, SPLIT_V2_DIR / "contact_tier_a_cross.png",
                   max_pairs=len(tier_a_pairs), title="Tier A cross-split")

# Random 40 merged Tier B cross-split
tier_b_merged = [
    (r["stem_a"], r["split_a"], r["stem_b"], r["split_b"],
     f"d={r['min_dihedral_dist']} inl={r['inliers']:.0f}")
    for r in rows_out
    if r["tier"] == "B" and r["cross_split"] and r["decision"] == "merge"
]
make_contact_sheet(tier_b_merged, SPLIT_V2_DIR / "contact_tier_b_merged.png",
                   seed=42, max_pairs=40, title="Tier B merged (40 random)")

# Random 40 rejected Tier B cross-split
tier_b_rejected = [
    (r["stem_a"], r["split_a"], r["stem_b"], r["split_b"],
     f"d={r['min_dihedral_dist']} inl={r['inliers']:.0f} cov={r['hull_coverage']:.2f}")
    for r in rows_out
    if r["tier"] == "B" and r["cross_split"] and r["decision"] == "reject"
]
make_contact_sheet(tier_b_rejected, SPLIT_V2_DIR / "contact_tier_b_rejected.png",
                   seed=42, max_pairs=40, title="Tier B rejected (40 random)")

update_progress(**{"Phase 1 - contact sheets": "done", "Phase 1": "COMPLETE"})
log("\n=== Phase 1 complete ===")

# Print final summary for REPORT
log(f"""
Phase 1 Summary:
  Total candidate pairs (d<=12): {len(our_cross_a4)} cross-split d<=4
  Tier A cross-split (merge):   {len(tier_a_pairs)}
  Tier B cross-split merged:    {sift_merge_count}
  Tier B cross-split rejected:  {sift_reject_count}
  SANAS NUEVAS↔SOCORRO cross-split merged: {sanas_answer['nuevas_socorro_cross_split_merged_pairs']}
""")
