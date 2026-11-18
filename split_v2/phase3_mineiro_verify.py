"""
Phase 3: MINEIRO_99 Component Verification
SESSION_FIX_V2 - DECAFIA Paper 1

Verifies every cross-group edge inside and around the MINEIRO_99 component
using SIFT+RANSAC with foreground-appropriate masks.

Steps:
  1. Anatomy of MINEIRO_99 component
  2. Verify each cross-group merge edge with SIFT+RANSAC
  3. Rebuild components with verified edges only
  4. Check Path A conditions

Output: split_v2/mineiro99_verification.json

NOTE on UF faithfulness to phase2:
  - phase2 Step A: union all stems with same group_root
  - phase2 Step B: union only pairs where decision == 'merge' (NOT merge_within)
    merge_within pairs are already within the same group_root so they're
    already handled by Step A.
  - Rebalancing: we replicate the same greedy rebalancing from phase2 for cond4.
"""

import sys, json, time
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import cv2
import pandas as pd

REPO         = Path("C:/Users/luise/temp/decafia-research")
DATASET_ROOT = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
SPLIT_V2_DIR = REPO / "split_v2"

def log(msg):
    print(msg, flush=True)

log("=== Phase 3: MINEIRO_99 Component Verification ===")
log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# ── 1. Load data ───────────────────────────────────────────────────────────────
assign_df = pd.read_csv(REPO / "splits/grouped_v1/assignments.csv")
assign_df = assign_df.rename(columns={"split_new": "split_v1", "split_old": "split_disk"})

copy_pairs = pd.read_csv(SPLIT_V2_DIR / "copy_pairs.csv")

stems         = assign_df["stem"].tolist()
N             = len(stems)
stem_to_idx   = {s: i for i, s in enumerate(stems)}

stem_to_split_v1   = dict(zip(assign_df["stem"], assign_df["split_v1"]))
stem_to_split_disk = dict(zip(assign_df["stem"], assign_df["split_disk"]))
stem_to_group      = dict(zip(assign_df["stem"], assign_df["group_root"]))
stem_to_prefix     = dict(zip(assign_df["stem"], assign_df["prefix"]))
stem_to_roya       = dict(zip(assign_df["stem"], assign_df["roya"]))
stem_to_coco       = dict(zip(assign_df["stem"], assign_df["coco"]))
stem_to_minador    = dict(zip(assign_df["stem"], assign_df["minador"]))

log(f"Loaded {N} images, {assign_df['group_root'].nunique()} v1 groups")

def image_path(stem):
    disk = stem_to_split_disk[stem]
    return DATASET_ROOT / "images" / disk / f"{stem}.jpg"

# ── 2. Union-Find utilities ────────────────────────────────────────────────────
def make_uf(n):
    return list(range(n))

def uf_find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def uf_union(parent, x, y):
    px, py = uf_find(parent, x), uf_find(parent, y)
    if px != py:
        parent[px] = py
        return True
    return False

def build_uf_step_a(parent):
    """Union all images within the same v1 group_root (phase2 Step A)."""
    groups = defaultdict(list)
    for stem, grp in stem_to_group.items():
        if stem in stem_to_idx:
            groups[grp].append(stem_to_idx[stem])
    for grp, idxs in groups.items():
        for idx in idxs[1:]:
            uf_union(parent, idxs[0], idx)

# Phase2 uses only 'merge' decision (cross-split pairs), NOT 'merge_within'
# 'merge_within' pairs are already within same group_root, covered by Step A
merge_df = copy_pairs[copy_pairs["decision"] == "merge"].copy()

# ── 3. Step 1: Anatomy of MINEIRO_99 ─────────────────────────────────────────
log("\n--- Step 1: Anatomy of MINEIRO_99 ---")

# Build full UF (identical to phase2)
parent_full = make_uf(N)
build_uf_step_a(parent_full)

for _, row in merge_df.iterrows():
    a, b = row["stem_a"], row["stem_b"]
    if a in stem_to_idx and b in stem_to_idx:
        uf_union(parent_full, stem_to_idx[a], stem_to_idx[b])

if "MINEIRO_99" not in stem_to_idx:
    log("[FAIL] MINEIRO_99 not found in assignments!")
    sys.exit(1)

mineiro99_root_full = uf_find(parent_full, stem_to_idx["MINEIRO_99"])
comp_full = [stems[i] for i in range(N) if uf_find(parent_full, i) == mineiro99_root_full]

log(f"MINEIRO_99 component size (before reverification): {len(comp_full)}")

comp_splits    = Counter(stem_to_split_v1[s] for s in comp_full)
comp_prefixes  = Counter(stem_to_prefix[s] for s in comp_full)
comp_roya      = sum(stem_to_roya.get(s, 0) for s in comp_full)
comp_coco      = sum(stem_to_coco.get(s, 0) for s in comp_full)
comp_minador   = sum(stem_to_minador.get(s, 0) for s in comp_full)

log(f"  Splits (v1): {dict(comp_splits)}")
log(f"  Prefixes: {dict(comp_prefixes)}")
log(f"  Annotations: roya={comp_roya}, coco={comp_coco}, minador={comp_minador}")

# Identify all cross-group merge edges that touch this component
# A cross-group edge is one where stem_a and stem_b have different group_roots
cross_group_in_comp = []
for _, row in merge_df.iterrows():
    a, b = row["stem_a"], row["stem_b"]
    if a not in stem_to_idx or b not in stem_to_idx:
        continue
    root_a = uf_find(parent_full, stem_to_idx[a])
    root_b = uf_find(parent_full, stem_to_idx[b])
    if root_a != mineiro99_root_full and root_b != mineiro99_root_full:
        continue
    # This edge touches the MINEIRO_99 component
    gr_a = stem_to_group.get(a, "")
    gr_b = stem_to_group.get(b, "")
    if gr_a != gr_b:
        cross_group_in_comp.append({
            "stem_a": a, "stem_b": b,
            "split_a": row["split_a"], "split_b": row["split_b"],
            "phash_dist": row["min_dihedral_dist"],
            "tier": row["tier"],
        })

log(f"Cross-group edges touching MINEIRO_99 component: {len(cross_group_in_comp)}")

# Edge breakdown
tier_a_phash = [e for e in cross_group_in_comp if e["tier"] == "A" and e["phash_dist"] >= 0]
tier_a_sift  = [e for e in cross_group_in_comp if e["tier"] == "A" and e["phash_dist"] < 0]
tier_b_sift  = [e for e in cross_group_in_comp if e["tier"] == "B"]
log(f"  (a) V1 intra-group-root edges: handled by step A (kept as-is)")
log(f"  (b) Tier A pHash d<=4: {len(tier_a_phash)}")
log(f"  (b) Tier A SIFT-verified (sept/nov): {len(tier_a_sift)}")
log(f"  (c) Tier B SIFT-verified: {len(tier_b_sift)}")

# ── 4. SIFT+RANSAC verification ───────────────────────────────────────────────
log("\n--- Step 2: SIFT+RANSAC Verification of Cross-Group Edges ---")

LAB_PREFIXES = {"MINEIRO", "MINADO_RECORTES"}

def is_lab_image(stem):
    prefix = stem_to_prefix.get(stem, "")
    return prefix in LAB_PREFIXES

def white_bg_mask(img_bgr):
    """Non-white pixel mask for white-background lab images.
    Foreground = NOT (R>220 AND G>220 AND B>220).
    """
    b, g, r = img_bgr[:, :, 0], img_bgr[:, :, 1], img_bgr[:, :, 2]
    white = (r.astype(np.int32) > 220) & (g.astype(np.int32) > 220) & (b.astype(np.int32) > 220)
    mask = (~white).astype(np.uint8) * 255
    return mask

def green_leaf_mask(img_bgr):
    """HSV green-leaf mask: H in [35,85], S>40, V>40."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = (
        (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85) &
        (hsv[:, :, 1] >  40) &
        (hsv[:, :, 2] >  40)
    ).astype(np.uint8) * 255
    return mask

def get_fg_mask(img_bgr, stem):
    if is_lab_image(stem):
        return white_bg_mask(img_bgr), "white_bg"
    else:
        return green_leaf_mask(img_bgr), "green_leaf"

def eight_dihedral(img_bgr):
    out = []
    for flip in (None, 1):
        base = cv2.flip(img_bgr, flip) if flip is not None else img_bgr
        for rot in range(4):
            v = np.rot90(base, rot)
            out.append(np.ascontiguousarray(v))
    return out

def resize_max(img, max_side=1024):
    h, w = img.shape[:2]
    s = max_side / max(h, w)
    if s < 1.0:
        img = cv2.resize(img, (int(w*s), int(h*s)), interpolation=cv2.INTER_AREA)
    return img

def sift_verify_pair_fg(stem_a, stem_b, min_inliers=30, min_coverage=0.50):
    """
    SIFT+RANSAC verification with foreground-appropriate mask.
    For image_a: determine mask type based on stem_a prefix.
    Returns (inliers, hull_cov, fg_type, passes).
    """
    path_a = image_path(stem_a)
    path_b = image_path(stem_b)

    img_a = cv2.imread(str(path_a))
    img_b = cv2.imread(str(path_b))

    if img_a is None:
        log(f"  [WARN] Cannot read {path_a}")
        return 0, 0.0, "unknown", False
    if img_b is None:
        log(f"  [WARN] Cannot read {path_b}")
        return 0, 0.0, "unknown", False

    img_a = resize_max(img_a)
    mask_a, fg_type_a = get_fg_mask(img_a, stem_a)

    # If mask_a is all zero (no foreground found), use full image
    if mask_a.sum() == 0:
        mask_a_use = None
        fg_area = float(img_a.shape[0] * img_a.shape[1])
    else:
        mask_a_use = mask_a
        fg_area = float(mask_a.sum()) / 255.0

    sift = cv2.SIFT_create()
    kp_a, des_a = sift.detectAndCompute(img_a, mask_a_use)
    if des_a is None or len(kp_a) < 4:
        return 0, 0.0, fg_type_a, False

    best_inliers, best_cov = 0, 0.0
    variants = eight_dihedral(img_b)

    for v in variants:
        v = resize_max(v)
        mask_b, _ = get_fg_mask(v, stem_b)
        mask_b_use = mask_b if mask_b.sum() > 0 else None

        kp_b, des_b = sift.detectAndCompute(v, mask_b_use)
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

        inlier_pts = pts_a[mask_inlier.ravel() == 1]
        if len(inlier_pts) >= 3:
            hull = cv2.convexHull(inlier_pts.astype(np.float32))
            hull_area = cv2.contourArea(hull)
            ref_area = max(fg_area, 100.0)
            cov = hull_area / ref_area
        else:
            cov = 0.0

        if n_inliers > best_inliers:
            best_inliers, best_cov = n_inliers, cov

    passes = (best_inliers >= min_inliers) and (best_cov >= min_coverage)
    return best_inliers, best_cov, fg_type_a, passes

# Run verification on all cross-group edges in MINEIRO_99 component
log(f"Verifying {len(cross_group_in_comp)} cross-group edges...")

verified_results = []
t0 = time.time()
n_pass = 0
n_fail = 0

for n_done, edge in enumerate(cross_group_in_comp):
    a, b = edge["stem_a"], edge["stem_b"]
    log(f"  [{n_done+1}/{len(cross_group_in_comp)}] {a} <-> {b}  tier={edge['tier']} d={edge['phash_dist']}")

    inliers, hull_cov, fg_type, passes = sift_verify_pair_fg(a, b)

    result = {
        "stem_a": a,
        "stem_b": b,
        "split_a": edge["split_a"],
        "split_b": edge["split_b"],
        "phash_dist": edge["phash_dist"],
        "tier": edge["tier"],
        "inliers": inliers,
        "hull_cov": round(hull_cov, 4),
        "fg_type": fg_type,
        "passes": bool(passes),
    }
    verified_results.append(result)

    status = "PASS" if passes else "FAIL"
    log(f"    -> inliers={inliers}, hull_cov={hull_cov:.3f}, fg={fg_type}: {status}")

    if passes:
        n_pass += 1
    else:
        n_fail += 1

log(f"\nVerification complete: {n_pass} pass, {n_fail} fail in {time.time()-t0:.1f}s")

# ── 5. Step 3: Rebuild with verified edges only ────────────────────────────────
log("\n--- Step 3: Rebuild components with verified edges only ---")

# Build verified-only UF:
#   Step A: v1 intra-group-root (always kept, same as phase2)
#   Step B: 'merge' edges EXCEPT those that:
#            - touch MINEIRO_99 component AND
#            - cross group_roots AND
#            - failed SIFT verification
#   (Non-MINEIRO_99 cross-group merges are kept unchanged)

parent_verified = make_uf(N)
build_uf_step_a(parent_verified)

# Set of reverified edge keys (stem pairs we tested)
reverified_keys = set()
passing_keys = set()
for r in verified_results:
    key = tuple(sorted([r["stem_a"], r["stem_b"]]))
    reverified_keys.add(key)
    if r["passes"]:
        passing_keys.add(key)

for _, row in merge_df.iterrows():
    a, b = row["stem_a"], row["stem_b"]
    if a not in stem_to_idx or b not in stem_to_idx:
        continue
    key = tuple(sorted([a, b]))
    if key in reverified_keys:
        # Apply only if SIFT passed
        if key in passing_keys:
            uf_union(parent_verified, stem_to_idx[a], stem_to_idx[b])
        # else: skip (failed verification)
    else:
        # Not in MINEIRO_99 component: keep original merge unchanged
        uf_union(parent_verified, stem_to_idx[a], stem_to_idx[b])

# Component stats
comp_members_verified = defaultdict(list)
for i in range(N):
    comp_members_verified[uf_find(parent_verified, i)].append(i)

comp_sizes_v = sorted([len(v) for v in comp_members_verified.values()], reverse=True)
largest_verified = comp_sizes_v[0]
n_components_verified = len(comp_sizes_v)

log(f"Components after verification: {n_components_verified}")
log(f"Largest component: {largest_verified}")
log(f"Top 5 component sizes: {comp_sizes_v[:5]}")

# MINEIRO_99 component after verification
mineiro99_root_v = uf_find(parent_verified, stem_to_idx["MINEIRO_99"])
comp_verified_members = [stems[i] for i in range(N) if uf_find(parent_verified, i) == mineiro99_root_v]
log(f"MINEIRO_99 component after verification: {len(comp_verified_members)}")

# Fragment report: components containing minador test images
minador_frags = {}
for root, idxs in comp_members_verified.items():
    min_test = sum(stem_to_minador.get(stems[i], 0)
                   for i in idxs if stem_to_split_v1[stems[i]] == "test")
    if min_test > 0:
        minador_frags[stems[root]] = {
            "size": len(idxs),
            "minador_test_instances": int(min_test),
        }

log(f"Components with minador test instances: {len(minador_frags)}")
for root_s, v in sorted(minador_frags.items(), key=lambda x: -x[1]["minador_test_instances"])[:10]:
    log(f"  root={root_s}: size={v['size']}, minador_test={v['minador_test_instances']}")

# ── 6. Step 4: Path A conditions (with rebalancing, matching phase2 logic) ────
log("\n--- Step 4: Path A Conditions ---")

TARGET_FRACS = {"train": 0.681, "val": 0.165, "test": 0.154}
TOLERANCE    = 0.02

def assign_splits_with_rebalance(comp_members_dict, stems_list, stem_to_split_v1_dict, N_total):
    """
    Minimal-movement split assignment with greedy rebalancing,
    identical to phase2_build_split.py logic.
    """
    # Majority vote per component
    comp_split = {}
    for root, idxs in comp_members_dict.items():
        split_counts = Counter(stem_to_split_v1_dict[stems_list[i]] for i in idxs)
        majority = max(split_counts, key=lambda s: (split_counts[s], s == "train"))
        comp_split[root] = majority

    # Greedy rebalance (same as phase2)
    target_counts = {s: int(TARGET_FRACS[s] * N_total) for s in TARGET_FRACS}

    # Movable = single-v1-group components (can be moved without splitting a cross-group merge)
    def component_is_movable(idxs):
        groups_in_comp = set(stem_to_group[stems_list[i]] for i in idxs)
        return len(groups_in_comp) == 1

    movable = {root: idxs for root, idxs in comp_members_dict.items()
               if component_is_movable(idxs)}

    for _attempt in range(2):
        movable_sorted = sorted(movable.items(), key=lambda x: len(x[1]))
        for root, idxs in movable_sorted:
            current_split = comp_split[root]
            n_comp = len(idxs)
            current_actual = Counter()
            for r, ilist in comp_members_dict.items():
                current_actual[comp_split[r]] += len(ilist)

            best_move = None
            best_score = sum(abs(current_actual[s] - target_counts[s]) for s in TARGET_FRACS)
            for new_split in TARGET_FRACS:
                if new_split == current_split:
                    continue
                hyp = dict(current_actual)
                hyp[current_split] -= n_comp
                hyp[new_split] += n_comp
                score = sum(abs(hyp[s] - target_counts[s]) for s in TARGET_FRACS)
                if score < best_score:
                    best_score = score
                    best_move = new_split
            if best_move is not None:
                comp_split[root] = best_move

        # Check tolerance
        split_counts = Counter()
        for root, idxs in comp_members_dict.items():
            for i in idxs:
                split_counts[comp_split[root]] += 1
        ok = all(abs(split_counts[s] / N_total - TARGET_FRACS[s]) <= TOLERANCE
                 for s in TARGET_FRACS)
        if ok:
            break

    stem_to_split_new = {}
    for root, idxs in comp_members_dict.items():
        for i in idxs:
            stem_to_split_new[stems_list[i]] = comp_split[root]
    return stem_to_split_new

stem_to_split_new = assign_splits_with_rebalance(
    comp_members_verified, stems, stem_to_split_v1, N
)
split_counts_new = Counter(stem_to_split_new.values())
log(f"Split counts after rebalancing: {dict(split_counts_new)}")

# Condition 1: Zero cross-split verified copies
n_cross_split_verified = 0
cross_split_examples = []
# Check all 'merge' edges in the new split assignment
for _, row in merge_df.iterrows():
    a, b = row["stem_a"], row["stem_b"]
    if a not in stem_to_split_new or b not in stem_to_split_new:
        continue
    key = tuple(sorted([a, b]))
    # Only count edges that are actually applied in the verified UF
    if key in reverified_keys and key not in passing_keys:
        continue  # This edge was removed
    new_split_a = stem_to_split_new[a]
    new_split_b = stem_to_split_new[b]
    if new_split_a != new_split_b:
        n_cross_split_verified += 1
        cross_split_examples.append((a, new_split_a, b, new_split_b))

cond1 = (n_cross_split_verified == 0)
log(f"Cond 1 (zero cross-split copies): {'PASS' if cond1 else 'FAIL'} ({n_cross_split_verified} remaining cross-split merged pairs)")
if cross_split_examples:
    for cp in cross_split_examples[:5]:
        log(f"  {cp}")

# Condition 2: Max component < 10% of dataset
threshold_10pct = int(0.1 * N)
cond2 = (largest_verified < threshold_10pct)
log(f"Cond 2 (max component < {threshold_10pct}): {'PASS' if cond2 else 'FAIL'} (largest={largest_verified})")

# Condition 3: All classes >= 100 test instances
test_stems_new = [s for s, sp in stem_to_split_new.items() if sp == "test"]
test_roya    = sum(stem_to_roya.get(s, 0) for s in test_stems_new)
test_coco    = sum(stem_to_coco.get(s, 0) for s in test_stems_new)
test_minador = sum(stem_to_minador.get(s, 0) for s in test_stems_new)
cond3 = all(x >= 100 for x in [test_roya, test_coco, test_minador])
log(f"Cond 3 (all classes >= 100 test): {'PASS' if cond3 else 'FAIL'} (roya={test_roya}, coco={test_coco}, minador={test_minador})")

# Condition 4: Proportions within 2pp
cond4 = True
for s, target_frac in TARGET_FRACS.items():
    actual_frac = split_counts_new[s] / N
    drift = abs(actual_frac - target_frac)
    if drift > TOLERANCE:
        cond4 = False
    log(f"  {s}: {split_counts_new[s]} ({100*actual_frac:.1f}% vs target {100*target_frac:.1f}%, drift {100*drift:.2f}pp)")
log(f"Cond 4 (proportions within 2pp): {'PASS' if cond4 else 'FAIL'}")

path_a_feasible = all([cond1, cond2, cond3, cond4])
failing_conditions = []
if not cond1: failing_conditions.append("cond1_zero_cross_split_copies")
if not cond2: failing_conditions.append("cond2_max_component_lt_10pct")
if not cond3: failing_conditions.append("cond3_all_classes_ge_100_test")
if not cond4: failing_conditions.append("cond4_proportions_within_2pp")

# ── 7. Write output JSON ───────────────────────────────────────────────────────
log("\n--- Writing output ---")

output = {
    "component_before_verification": {
        "size": len(comp_full),
        "splits": dict(comp_splits),
        "prefixes": dict(comp_prefixes),
        "n_cross_group_edges": len(cross_group_in_comp),
        "annotations": {
            "roya": int(comp_roya),
            "coco": int(comp_coco),
            "minador": int(comp_minador),
        },
        "edge_breakdown": {
            "v1_intra_group": "kept_as_is",
            "tier_a_phash_d_le_4": len(tier_a_phash),
            "tier_a_sift_verified_sept_nov": len(tier_a_sift),
            "tier_b_sift_verified": len(tier_b_sift),
        },
    },
    "cross_group_edges_verified": [
        {
            "stem_a": r["stem_a"],
            "stem_b": r["stem_b"],
            "split_a": r["split_a"],
            "split_b": r["split_b"],
            "phash_dist": int(r["phash_dist"]),
            "tier": r["tier"],
            "inliers": int(r["inliers"]),
            "hull_cov": float(r["hull_cov"]),
            "fg_type": r["fg_type"],
            "passes": r["passes"],
        }
        for r in verified_results
    ],
    "edges_pass": n_pass,
    "edges_fail": n_fail,
    "mineiro99_component_after_size": len(comp_verified_members),
    "largest_component_after": int(largest_verified),
    "n_components_after": n_components_verified,
    "path_a_feasible": bool(path_a_feasible),
    "conditions": {
        "cond1": bool(cond1),
        "cond2": bool(cond2),
        "cond3": bool(cond3),
        "cond4": bool(cond4),
    },
    "failing_conditions": failing_conditions,
    "test_instances_after": {
        "roya": int(test_roya),
        "coco": int(test_coco),
        "minador": int(test_minador),
    },
    "split_counts_after": dict(split_counts_new),
    "minador_frags_after": minador_frags,
}

out_path = SPLIT_V2_DIR / "mineiro99_verification.json"
out_path.write_text(json.dumps(output, indent=2))
log(f"Written: {out_path}")

# ── 8. Summary ─────────────────────────────────────────────────────────────────
log("\n" + "="*60)
log("SUMMARY")
log("="*60)
log(f"Cross-group edges total:  {len(cross_group_in_comp)}")
log(f"Cross-group edges pass:   {n_pass}")
log(f"Cross-group edges fail:   {n_fail}")
log(f"Largest component before: {len(comp_full)}")
log(f"Largest component after:  {largest_verified}")
log(f"MINEIRO_99 comp before:   {len(comp_full)}")
log(f"MINEIRO_99 comp after:    {len(comp_verified_members)}")
log(f"Path A feasible:          {'YES' if path_a_feasible else 'NO'}")
if failing_conditions:
    log(f"Failing conditions:       {', '.join(failing_conditions)}")
else:
    log("All 4 conditions pass.")
log("="*60)

if path_a_feasible:
    log("\nResult: Path A feasible")
else:
    log("\nResult: Path B confirmed")
    for fc in failing_conditions:
        log(f"  FAILED: {fc}")

log(f"\nDone: {time.strftime('%Y-%m-%d %H:%M:%S')}")
