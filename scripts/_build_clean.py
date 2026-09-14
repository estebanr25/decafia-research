"""
DECAFIA clean dataset builder.
Steps 1-3: correct manifest, build decafia_clean, write DATASET_CARD.md
"""
import csv, re, shutil, random, hashlib
from pathlib import Path
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset")
SRC_DS = BASE / "decafia_yolo_original"
DST_DS = BASE / "decafia_clean"
MANIFEST = BASE / "provenance_manifest.csv"

# ── Author-declared prefix mapping ────────────────────────────────────────────
PREFIX_MAP = {
    "SANAS_NUEVAS":    ("own_field",           "declared_by_author"),
    "SANAS_SOCORRO":   ("own_field",           "declared_by_author"),
    "COCO_RECORTE":    ("own_field",           "declared_by_author"),
    "COCO_M_A":        ("own_field",           "declared_by_author"),
    "COCO_Muy_A":      ("own_field",           "declared_by_author"),
    "COCO_P_A":        ("own_field",           "declared_by_author"),
    "ROYA_RECORTES":   ("own_field",           "declared_by_author"),
    "ROYA_P_A":        ("own_field",           "declared_by_author"),
    "ROYA_MA":         ("own_field",           "declared_by_author"),
    "ROYA_Muy_A":      ("own_field",           "declared_by_author"),
    "ROYA_FONDO":      ("rust_and_leaf_miner", "declared_by_author"),
    "MINADOR":         ("rust_and_leaf_miner", "declared_by_author"),
    "MINADO_RECORTES": ("rust_and_leaf_miner", "declared_by_author"),
    "MINEIRO":         ("rust_and_leaf_miner", "declared_by_author"),
    "SANAS_ROCOLE":    ("rocole",              "declared_by_author"),
}

CLASS_NAMES = {0: "roya", 1: "coco", 2: "minador"}

# class 3 (minador original) -> 2; class 2 (sano) dropped
REMAP = {"0": "0", "1": "1", "3": "2"}


def get_prefix(stem):
    m = re.match(r"^([A-Za-z_]+)", stem)
    return m.group(1).rstrip("_") if m else "(none)"


def pct(n, total):
    return f"{100 * n / total:.1f}%" if total else "0%"


def remap_label_line(line):
    parts = line.strip().split()
    if not parts:
        return line
    if parts[0] not in REMAP:
        raise ValueError(f"Unexpected class id {parts[0]!r} in: {line!r}")
    parts[0] = REMAP[parts[0]]
    return " ".join(parts)


# =============================================================================
# STEP 1 — Correct provenance manifest
# =============================================================================
print("=" * 70)
print("STEP 1 — Correcting provenance manifest")
print("=" * 70)

with open(MANIFEST, newline="", encoding="utf-8") as fh:
    orig_rows = list(csv.DictReader(fh))

fieldnames = [
    "filename", "split", "inferred_source", "provenance_evidence",
    "sha256", "n_annotations", "class_ids_present", "width", "height",
]

updated = []
for r in orig_rows:
    pfx = get_prefix(Path(r["filename"]).stem)
    if pfx in PREFIX_MAP:
        src, evd = PREFIX_MAP[pfx]
    else:
        src, evd = r["inferred_source"], "unknown"
    updated.append({
        "filename":           r["filename"],
        "split":              r["split"],
        "inferred_source":    src,
        "provenance_evidence": evd,
        "sha256":             r["sha256"],
        "n_annotations":      r["n_annotations"],
        "class_ids_present":  r["class_ids_present"],
        "width":              r["width"],
        "height":             r["height"],
    })

with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(updated)

print(f"  Written {len(updated)} rows -> {MANIFEST}")

src_counts = defaultdict(int)
for r in updated:
    src_counts[r["inferred_source"]] += 1

print("\n  Corrected source totals:")
total = 0
for src in sorted(src_counts):
    print(f"    {src:<25} {src_counts[src]}")
    total += src_counts[src]
print(f"    {'TOTAL':<25} {total}")
assert total == 2769, f"Total mismatch: {total}"
print("  Sum check: 2769 OK")

# Highlight the MINEIRO correction
mineiro_rows = [r for r in updated if get_prefix(Path(r["filename"]).stem) == "MINEIRO"]
print(f"\n  MINEIRO correction: {len(mineiro_rows)} images "
      f"now labelled rust_and_leaf_miner (was rocole)")


# =============================================================================
# STEP 2 — Build decafia_clean
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2 — Building decafia_clean")
print("=" * 70)

eligible = [r for r in updated if r["inferred_source"] != "rocole"]
excluded = [r for r in updated if r["inferred_source"] == "rocole"]
print(f"\n  Excluded (rocole): {len(excluded)}")
print(f"  Eligible:          {len(eligible)}")
assert len(excluded) == 454, f"Expected 454 rocole rows, got {len(excluded)}"
print("  Exclusion count check: 454 OK")

# --- 2b. Verify duplicate pairs ---
dup_path = BASE / "DUPLICATES.csv"
with open(dup_path, newline="", encoding="utf-8") as fh:
    dup_rows = list(csv.DictReader(fh))

eligible_fnames = {r["filename"] for r in eligible}
print(f"\n  Checking {len(dup_rows)} duplicate pairs vs eligible set:")
remaining_dups = []
for d in dup_rows:
    a_in = d["file_a"] in eligible_fnames
    b_in = d["file_b"] in eligible_fnames
    if a_in and b_in:
        remaining_dups.append(d)
        print(f"  REMAINING DUP: {d['file_a']} <-> {d['file_b']}")
    else:
        status = "both excluded" if not a_in and not b_in else "one side excluded"
        print(f"  [{status}] {d['file_a']} | {d['file_b']}")

if remaining_dups:
    to_drop = set()
    for d in remaining_dups:
        drop = d["file_b"] if d["split_a"] == "train" else d["file_a"]
        to_drop.add(drop)
        print(f"  DROPPING non-train copy: {drop}")
    eligible = [r for r in eligible if r["filename"] not in to_drop]
    print(f"  After manual dedup: {len(eligible)} images")
else:
    print("  All 5 duplicate pairs fully removed by rocole exclusion. OK")

# --- 2c. Stratified re-split 70/15/15, seed=42 ---
groups = defaultdict(list)
for r in eligible:
    sig = r["class_ids_present"]
    groups[sig].append(r)

print(f"\n  Stratification groups (class_ids_present -> count):")
for sig in sorted(groups):
    label = sig if sig else "(background)"
    print(f"    [{label}]: {len(groups[sig])}")

random.seed(42)

train_rows, val_rows, test_rows = [], [], []
for sig, items in groups.items():
    random.shuffle(items)
    n = len(items)
    n_test  = max(1, round(n * 0.15))
    n_val   = max(1, round(n * 0.15))
    n_train = n - n_test - n_val
    test_rows  += items[:n_test]
    val_rows   += items[n_test:n_test + n_val]
    train_rows += items[n_test + n_val:]

print(f"\n  Split sizes:")
print(f"    train : {len(train_rows)}")
print(f"    val   : {len(val_rows)}")
print(f"    test  : {len(test_rows)}")
print(f"    total : {len(train_rows) + len(val_rows) + len(test_rows)}")

# --- 2d. Assert zero filename collisions ---
split_lookup = {}
for sname, srows in [("train", train_rows), ("val", val_rows), ("test", test_rows)]:
    for r in srows:
        split_lookup[r["filename"]] = (sname, r)

fname_seen = {}
fn_collisions = []
for fname, (sname, _) in split_lookup.items():
    if fname in fname_seen:
        fn_collisions.append(f"{fname}: {fname_seen[fname]} AND {sname}")
    fname_seen[fname] = sname
if fn_collisions:
    raise AssertionError("FILENAME COLLISIONS DETECTED:\n" + "\n".join(fn_collisions))
print("  Filename collision check: 0 OK")

# --- 2e. Assert zero SHA256 collisions ---
sha_map = defaultdict(list)
eligible_sha = {r["filename"]: r["sha256"] for r in eligible}
for fname in split_lookup:
    sha_map[eligible_sha[fname]].append(fname)
sha_collisions = {k: v for k, v in sha_map.items() if len(v) > 1}
if sha_collisions:
    raise AssertionError("SHA256 COLLISIONS DETECTED:\n" +
                         "\n".join(f"{k}: {v}" for k, v in sha_collisions.items()))
print("  SHA256 collision check: 0 OK")

# --- 2f. Create directory structure ---
if DST_DS.exists():
    shutil.rmtree(DST_DS)
for split_name in ("train", "val", "test"):
    (DST_DS / "images" / split_name).mkdir(parents=True)
    (DST_DS / "labels" / split_name).mkdir(parents=True)

# --- 2g. Copy images + remap labels ---
print("\n  Copying images and remapping labels...")
for fname, (sname, row) in split_lookup.items():
    src_img = SRC_DS / "images" / row["split"] / fname
    dst_img = DST_DS / "images" / sname / fname
    shutil.copy2(src_img, dst_img)

    stem    = Path(fname).stem
    src_lbl = SRC_DS / "labels" / row["split"] / (stem + ".txt")
    dst_lbl = DST_DS / "labels" / sname / (stem + ".txt")

    if src_lbl.exists():
        raw_lines = src_lbl.read_text(encoding="utf-8", errors="replace").splitlines()
        out_lines = []
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if parts[0] == "2":   # sano annotation — skip
                continue
            out_lines.append(remap_label_line(line))
        dst_lbl.write_text("\n".join(out_lines) + ("\n" if out_lines else ""),
                           encoding="utf-8")
    else:
        dst_lbl.write_text("", encoding="utf-8")

# --- 2h. Write data.yaml ---
yaml_txt = (
    "# DECAFIA clean dataset - own_field + rust_and_leaf_miner only\n"
    "# Generated from decafia_yolo_original; rocole subset excluded.\n"
    "# seed=42, stratified 70/15/15 by class presence\n"
    "path: .\n"
    "train: images/train\n"
    "val:   images/val\n"
    "test:  images/test\n"
    "\n"
    "nc: 3\n"
    "names:\n"
    "  0: roya\n"
    "  1: coco\n"
    "  2: minador\n"
)
(DST_DS / "data.yaml").write_text(yaml_txt, encoding="utf-8")
print("  Written data.yaml")

# --- 2i. Verify final file counts ---
print("\n  Final counts in decafia_clean:")
for sname in ("train", "val", "test"):
    ni = len(list((DST_DS / "images" / sname).iterdir()))
    nl = len(list((DST_DS / "labels" / sname).iterdir()))
    print(f"    {sname}: {ni} images, {nl} labels")


# =============================================================================
# Collect stats for DATASET_CARD.md
# =============================================================================
print("\n" + "=" * 70)
print("Collecting stats for DATASET_CARD.md")
print("=" * 70)

card_stats = {}
for sname in ("train", "val", "test"):
    lbl_dir   = DST_DS / "labels" / sname
    img_dir   = DST_DS / "images" / sname
    cls_cnt   = defaultdict(int)
    background = 0
    total_ann  = 0
    for lbl in lbl_dir.iterdir():
        lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            background += 1
        else:
            for line in lines:
                cid = int(line.split()[0])
                cls_cnt[cid] += 1
                total_ann += 1
    card_stats[sname] = {
        "images":      len(list(img_dir.iterdir())),
        "class_counts": dict(cls_cnt),
        "background":  background,
        "total_ann":   total_ann,
    }

# Source x class instance counts
src_class = defaultdict(lambda: defaultdict(int))
for fname, (sname, row) in split_lookup.items():
    src = row["inferred_source"]
    lbl_path = DST_DS / "labels" / sname / (Path(fname).stem + ".txt")
    if lbl_path.exists():
        for line in lbl_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                cid = int(line.split()[0])
                src_class[src][cid] += 1

# Aggregate totals
t_img  = sum(card_stats[s]["images"] for s in card_stats)
t_roya = sum(card_stats[s]["class_counts"].get(0, 0) for s in card_stats)
t_coco = sum(card_stats[s]["class_counts"].get(1, 0) for s in card_stats)
t_min  = sum(card_stats[s]["class_counts"].get(2, 0) for s in card_stats)
t_ann  = sum(card_stats[s]["total_ann"] for s in card_stats)
t_bg   = sum(card_stats[s]["background"] for s in card_stats)
all_inst = t_roya + t_coco + t_min

print("\n  Per-split stats:")
for sname in ("train", "val", "test"):
    s = card_stats[sname]
    cc = s["class_counts"]
    print(f"    {sname}: {s['images']} imgs | "
          f"roya={cc.get(0,0)} coco={cc.get(1,0)} minador={cc.get(2,0)} "
          f"bg={s['background']} ann={s['total_ann']}")

print(f"\n  Totals: imgs={t_img} roya={t_roya} coco={t_coco} minador={t_min} "
      f"bg={t_bg} ann={t_ann}")

print("\n  Source x class totals:")
for src in sorted(src_class):
    r = src_class[src].get(0, 0)
    c = src_class[src].get(1, 0)
    m = src_class[src].get(2, 0)
    print(f"    {src}: roya={r} coco={c} minador={m}")


# =============================================================================
# STEP 3 — Write DATASET_CARD.md
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3 — Writing DATASET_CARD.md")
print("=" * 70)

lines = []
A = lines.append

A("# DECAFIA Clean Dataset Card")
A("")
A("**Generated:** 2026-09-11  ")
A("**Source:** `01_dataset/decafia_yolo_original/`  ")
A("**Split seed:** 42  ")
A("**Split ratio:** 70 / 15 / 15 (stratified by class-presence signature)")
A("")
A("---")
A("")
A("## 1. Image and Annotation Counts")
A("")
A("### Per-split summary")
A("")
A("| Split | Images | Roya ann. | Coco ann. | Minador ann. | Total ann. | Background imgs |")
A("|-------|-------:|----------:|----------:|-------------:|-----------:|----------------:|")
for sname in ("train", "val", "test"):
    s  = card_stats[sname]
    cc = s["class_counts"]
    A(f"| {sname} | {s['images']} | {cc.get(0,0)} | {cc.get(1,0)} | {cc.get(2,0)} "
      f"| {s['total_ann']} | {s['background']} |")
A(f"| **TOTAL** | **{t_img}** | **{t_roya}** | **{t_coco}** | **{t_min}** "
  f"| **{t_ann}** | **{t_bg}** |")
A("")
A("*Class IDs in label files: 0 = roya, 1 = coco, 2 = minador.*  ")
A("*Background images have empty label files (healthy leaves, no annotated instances).*")
A("")
A("---")
A("")
A("## 2. Source x Class Breakdown")
A("")
A("Instance counts after class-ID remapping, summed across all splits.")
A("")
A("| Source | Roya | % of roya | Coco | % of coco | Minador | % of minador | Total |")
A("|--------|-----:|----------:|-----:|----------:|--------:|-------------:|------:|")
for src in sorted(src_class):
    r = src_class[src].get(0, 0)
    c = src_class[src].get(1, 0)
    m = src_class[src].get(2, 0)
    t = r + c + m
    A(f"| {src} | {r} | {pct(r, t_roya)} | {c} | {pct(c, t_coco)} "
      f"| {m} | {pct(m, t_min)} | {t} |")
A(f"| **TOTAL** | **{t_roya}** | 100% | **{t_coco}** | 100% "
  f"| **{t_min}** | 100% | **{all_inst}** |")
A("")
A("**own_field** = field images collected by Andrey Salom and Esteban Rosas "
  "in coffee-growing farms in Socorro, Santander, Colombia (unpublished).  ")
A("**rust_and_leaf_miner** = images from Silva et al. public dataset "
  "(DOI 10.17632/vfxf4trtcg.5, CC BY 4.0).")
A("")
A("---")
A("")
A("## 3. Exclusion Rules and Rationale")
A("")
A("### Excluded: RoCoLe subset (`inferred_source = rocole`)")
A("")
A("| Prefix | Count |")
A("|--------|------:|")
A("| SANAS_ROCOLE | 454 |")
A("")
A("**Why these images were excluded:**")
A("")
A("1. **Domain mismatch.** RoCoLe images (Parraga-Alava et al., "
  "DOI 10.17632/c5yvn32dzg.2) are healthy-leaf photographs taken under "
  "controlled laboratory conditions against a plain white background. "
  "The DECAFIA model targets field conditions in Socorro, Santander. "
  "Retaining these images would bias the background distribution.")
A("")
A("2. **Redundancy.** Healthy leaves are already represented by 1138 "
  "own_field images (SANAS_NUEVAS and SANAS_SOCORRO) with matching field conditions.")
A("")
A("3. **Split leakage.** All 5 SHA256 duplicate pairs in DUPLICATES.csv "
  "were within SANAS_ROCOLE (3 cross-split train/test or train/val leaks, "
  "2 intra-train duplicates). Exclusion eliminates all leakage.")
A("")
A("### Duplicate pair disposition")
A("")
A("All 5 pairs from `DUPLICATES.csv` were fully removed by the rocole exclusion. "
  "No additional deduplication step was required.")
A("")
A("### Class 'sano' is NOT a detection class")
A("")
A("**Healthy leaves are included as background examples with empty label files.**")
A("The model is trained on 3 detection classes only: roya, coco, minador.")
A("")
A("At inference time the system reports a leaf as healthy by the **absence of detections** "
  "above the confidence threshold (0.50). This means:")
A("")
A("- No bounding box is predicted for healthy tissue.")
A("- No fabricated confidence score is emitted for 'sano'.")
A("- The correct interpretation is: *no pathology found at the given threshold*.")
A("")
A(f"Background images (empty label files) account for **{t_bg} images** "
  f"({pct(t_bg, t_img)} of the dataset).")
A("")
A("---")
A("")
A("## 4. Attribution")
A("")
A("### Silva et al. — rust and leaf miner (used in this dataset)")
A("")
A("> Brito Silva, Lucas, et al.")
A("> *Dataset of images for training artificial intelligence models to detect")
A("> coffee leaf rust and leaf miner.*")
A("> Mendeley Data, V5.")
A("> DOI: [10.17632/vfxf4trtcg.5](https://doi.org/10.17632/vfxf4trtcg.5)")
A("> License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)")
A("")
A("Contributes images under prefixes: ROYA_FONDO, ROYA_MA, ROYA_Muy_A, ROYA_P_A,")
A("ROYA_RECORTES, MINADOR, MINADO_RECORTES, MINEIRO.")
A("")
A("### Own-field images (used in this dataset)")
A("")
A("Collected by Andrey Salom and Esteban Rosas in coffee farms in Socorro,")
A("Santander, Colombia. Not publicly released separately.")
A("Available here under CC BY 4.0.")
A("")
A("Prefixes: SANAS_NUEVAS, SANAS_SOCORRO, COCO_RECORTE, COCO_M_A, COCO_Muy_A,")
A("COCO_P_A, ROYA_RECORTES, ROYA_P_A, ROYA_MA, ROYA_Muy_A.")
A("")
A("### RoCoLe (excluded, preserved in decafia_yolo_original only)")
A("")
A("> Parraga-Alava, Jorge, et al.")
A("> *RoCoLe: A Robusta Coffee Leaf Images Dataset.*")
A("> Mendeley Data, V2.")
A("> DOI: [10.17632/c5yvn32dzg.2](https://doi.org/10.17632/c5yvn32dzg.2)")
A("> License: CC BY 4.0")
A("")
A("Excluded from `decafia_clean` — see Section 3. Present in `decafia_yolo_original/`.")
A("")
A("---")
A("")
A("## 5. Class ID Mapping")
A("")
A("| Original ID (decafia_yolo_original) | New ID (decafia_clean) | Class   |")
A("|:-----------------------------------:|:----------------------:|---------|")
A("| 0 | 0 | roya    |")
A("| 1 | 1 | coco    |")
A("| 3 | 2 | minador |")
A("| 2 | — | sano (background; no label emitted in decafia_clean) |")
A("")
A("---")
A("")
A("## 6. File Layout")
A("")
A("```")
A("decafia_clean/")
A("  data.yaml           # nc=3, names=[roya, coco, minador]")
A("  DATASET_CARD.md     # this file")
A("  images/")
A("    train/  val/  test/")
A("  labels/")
A("    train/  val/  test/   # YOLO format; empty = background (healthy leaf)")
A("```")

card_text = "\n".join(lines)
card_path = DST_DS / "DATASET_CARD.md"
card_path.write_text(card_text, encoding="utf-8")
print(f"  Written: {card_path}")

print("\n" + "=" * 70)
print("ALL STEPS COMPLETE")
print("=" * 70)
