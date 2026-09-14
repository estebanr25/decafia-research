"""
DECAFIA provenance corrections and documentation.
Parts 1-4.
"""
import csv, re, subprocess
from pathlib import Path
from collections import defaultdict
from datetime import date

BASE   = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset")
CLEAN  = BASE / "decafia_clean"
ORIG   = BASE / "decafia_yolo_original"
MANIFEST = BASE / "provenance_manifest.csv"
TODAY  = "2026-09-11"

SPLITS = ("train", "val", "test")

def get_prefix(stem):
    m = re.match(r"^([A-Za-z_]+)", stem)
    return m.group(1).rstrip("_") if m else "(none)"


# =============================================================================
# PART 1 — Correct ROYA_RECORTES provenance
# =============================================================================
print("=" * 70)
print("PART 1 — Correcting ROYA_RECORTES provenance")
print("=" * 70)

with open(MANIFEST, newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
fieldnames = list(rows[0].keys())

changed = 0
updated = []
for r in rows:
    row = dict(r)
    pfx = get_prefix(Path(row["filename"]).stem)
    if pfx == "ROYA_RECORTES":
        row["inferred_source"]     = "rust_and_leaf_miner"
        row["provenance_evidence"] = "declared_by_author"
        changed += 1
    updated.append(row)

with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(updated)

print(f"\n  ROYA_RECORTES rows corrected: {changed}")

# Verify totals
src_counts = defaultdict(int)
for r in updated:
    src_counts[r["inferred_source"]] += 1
total = sum(src_counts.values())

print("\n  Final manifest source totals:")
for src in sorted(src_counts):
    status = "OK" if src_counts[src] == {"own_field": 1705,
                                          "rust_and_leaf_miner": 610,
                                          "rocole": 454}[src] else "MISMATCH"
    print(f"    {src:<25} {src_counts[src]}  {status}")
print(f"    {'TOTAL':<25} {total}  {'OK' if total == 2769 else 'MISMATCH'}")

assert src_counts["own_field"]           == 1705, f"own_field mismatch: {src_counts['own_field']}"
assert src_counts["rust_and_leaf_miner"] == 610,  f"r&lm mismatch: {src_counts['rust_and_leaf_miner']}"
assert src_counts["rocole"]              == 454,  f"rocole mismatch: {src_counts['rocole']}"
assert total                             == 2769, f"total mismatch: {total}"
print("  All assertions passed.")

# Check every row has declared_by_author
not_declared = [r for r in updated if r["provenance_evidence"] != "declared_by_author"]
if not_declared:
    print(f"\n  WARNING — {len(not_declared)} rows WITHOUT declared_by_author:")
    for r in not_declared:
        pfx = get_prefix(Path(r["filename"]).stem)
        print(f"    {pfx}: {r['provenance_evidence']}")
else:
    print("\n  All 2769 rows carry provenance_evidence=declared_by_author. OK")


# =============================================================================
# PART 2 — Remove spurious coco annotation from MINEIRO_111.txt in clean
# =============================================================================
print("\n" + "=" * 70)
print("PART 2 — Remove spurious annotation from MINEIRO_111 (test split)")
print("=" * 70)

lbl_path = CLEAN / "labels" / "test" / "MINEIRO_111.txt"
assert lbl_path.exists(), f"Label not found: {lbl_path}"

original_lines = lbl_path.read_text(encoding="utf-8").splitlines()
print(f"\n  Original label content ({len(original_lines)} lines):")
for line in original_lines:
    print(f"    {line!r}")

# Identify the spurious line: class 1 (coco) with bbox ~(0.65625, 0.825, 0.071429, 0.033333)
spurious = []
kept = []
for line in original_lines:
    stripped = line.strip()
    if not stripped:
        continue
    parts = stripped.split()
    cid = int(parts[0])
    if cid == 1:  # coco — the only coco line in this file
        spurious.append(stripped)
    else:
        kept.append(stripped)

assert len(spurious) == 1, f"Expected exactly 1 coco line, found {len(spurious)}: {spurious}"
print(f"\n  Line to delete: {spurious[0]!r}")
print(f"  Lines to keep:  {len(kept)}")

# Write corrected label
lbl_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

verification = lbl_path.read_text(encoding="utf-8").splitlines()
print(f"\n  Corrected label content ({len(verification)} lines):")
for line in verification:
    print(f"    {line!r}")

# Confirm no coco (class 1) lines remain
assert not any(l.strip().startswith("1 ") for l in verification), "Coco line still present!"
print("  Verification: no coco lines remain. OK")

# Write CORRECTIONS.md
corrections_path = CLEAN / "CORRECTIONS.md"
corrections_md = f"""# DATASET_CORRECTIONS

## {TODAY} — Deleted spurious coco annotation from MINEIRO_111.txt (test split)

**File:** `labels/test/MINEIRO_111.txt`
**Deleted line:** `1 0.65625 0.825 0.071429 0.033333`
**Class deleted:** 1 (coco / Curculionidae)
**Bounding box size:** approx. 33 × 31 px in a 448 × 960 image

**Reason:**
MINEIRO images originate from the Silva et al. "rust and leaf miner" dataset
(DOI 10.17632/vfxf4trtcg.5). That dataset contains only roya (rust) and
minador (leaf miner) damage — Curculionidae (coco) is absent from its class
schema. The 33 × 31 px bounding box at image position (277, 776)–(310, 807)
is consistent with a mislabelled annotation artefact, not a genuine coco
infestation documented in the source dataset.

The image (`images/test/MINEIRO_111.jpg`) and all remaining annotations
(minador / class 2) are retained unchanged.
"""
corrections_path.write_text(corrections_md, encoding="utf-8")
print(f"\n  Written: {corrections_path}")


# =============================================================================
# Collect updated stats for DATASET_CARD regeneration
# =============================================================================
print("\n" + "=" * 70)
print("Collecting updated stats")
print("=" * 70)

CLASS_NAMES = {0: "roya", 1: "coco", 2: "minador"}

# Build filename->source from updated manifest
fname_to_src = {r["filename"]: r["inferred_source"] for r in updated}

def count_split(dataset_root, split):
    lbl_dir = dataset_root / "labels" / split
    img_dir = dataset_root / "images" / split
    cls_cnt  = defaultdict(int)
    bg       = 0
    ann_total= 0
    for lbl in lbl_dir.iterdir():
        lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            bg += 1
        else:
            for line in lines:
                cid = int(line.split()[0])
                cls_cnt[cid] += 1
                ann_total += 1
    return {
        "images":      len(list(img_dir.iterdir())),
        "class_counts": dict(cls_cnt),
        "background":  bg,
        "total_ann":   ann_total,
    }

card_stats = {s: count_split(CLEAN, s) for s in SPLITS}

t_img  = sum(card_stats[s]["images"]               for s in SPLITS)
t_roya = sum(card_stats[s]["class_counts"].get(0,0) for s in SPLITS)
t_coco = sum(card_stats[s]["class_counts"].get(1,0) for s in SPLITS)
t_min  = sum(card_stats[s]["class_counts"].get(2,0) for s in SPLITS)
t_ann  = sum(card_stats[s]["total_ann"]             for s in SPLITS)
t_bg   = sum(card_stats[s]["background"]            for s in SPLITS)
all_inst = t_roya + t_coco + t_min

print("\n  Per-split stats (after Part 2 correction):")
for s in SPLITS:
    cc = card_stats[s]["class_counts"]
    print(f"    {s}: imgs={card_stats[s]['images']} "
          f"roya={cc.get(0,0)} coco={cc.get(1,0)} minador={cc.get(2,0)} "
          f"bg={card_stats[s]['background']} ann={card_stats[s]['total_ann']}")
print(f"    TOTAL: imgs={t_img} roya={t_roya} coco={t_coco} minador={t_min} "
      f"bg={t_bg} ann={t_ann}")

# Source x class breakdown (from CLEAN labels, mapped via manifest)
src_class = defaultdict(lambda: defaultdict(int))
for split in SPLITS:
    lbl_dir = CLEAN / "labels" / split
    img_dir = CLEAN / "images" / split
    for lbl in lbl_dir.iterdir():
        fname = lbl.stem + ".jpg"
        src = fname_to_src.get(fname, "unknown")
        for line in lbl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                cid = int(line.split()[0])
                src_class[src][cid] += 1

print("\n  Source x class instance counts:")
for src in sorted(src_class):
    d = src_class[src]
    print(f"    {src}: roya={d.get(0,0)} coco={d.get(1,0)} minador={d.get(2,0)}")

# Assert the cross-source outliers are gone
assert src_class["own_field"].get(2, 0) == 0, \
    f"Still a minador in own_field: {src_class['own_field'].get(2,0)}"
assert src_class["rust_and_leaf_miner"].get(1, 0) == 0, \
    f"Still a coco in rust_and_leaf_miner: {src_class['rust_and_leaf_miner'].get(1,0)}"
print("  Cross-source outlier assertions: both 0. OK")

# roya percentages
roya_own = src_class["own_field"].get(0, 0)
roya_rlm = src_class["rust_and_leaf_miner"].get(0, 0)
print(f"\n  Roya breakdown: own_field={roya_own} ({100*roya_own//t_roya}%) "
      f"rust_and_leaf_miner={roya_rlm} ({100*roya_rlm//t_roya}%)")


def pct(n, total):
    return f"{100 * n / total:.1f}%" if total else "0%"


# =============================================================================
# PART 3 — Regenerate DATASET_CARD.md
# =============================================================================
print("\n" + "=" * 70)
print("PART 3 — Regenerating DATASET_CARD.md")
print("=" * 70)

lines = []
A = lines.append

A("# DECAFIA Clean Dataset Card")
A("")
A(f"**Generated:** {TODAY}  ")
A("**Source:** `01_dataset/decafia_yolo_original/`  ")
A("**Split seed:** 42  ")
A("**Split ratio:** 70 / 15 / 15 (stratified by class-presence signature)")
A("")
A("---")
A("")
A("## 1. Image and Annotation Counts")
A("")
A("| Split | Images | Roya ann. | Coco ann. | Minador ann. | Total ann. | Background imgs |")
A("|-------|-------:|----------:|----------:|-------------:|-----------:|----------------:|")
for s in SPLITS:
    cc = card_stats[s]["class_counts"]
    A(f"| {s} | {card_stats[s]['images']} | {cc.get(0,0)} | {cc.get(1,0)} "
      f"| {cc.get(2,0)} | {card_stats[s]['total_ann']} | {card_stats[s]['background']} |")
A(f"| **TOTAL** | **{t_img}** | **{t_roya}** | **{t_coco}** | **{t_min}** "
  f"| **{t_ann}** | **{t_bg}** |")
A("")
A("*Class IDs: 0 = roya, 1 = coco, 2 = minador.*  ")
A("*Background images carry empty label files (healthy-leaf examples).*")
A("")
A("---")
A("")
A("## 2. Source x Class Breakdown")
A("")
A("Instance counts after class-ID remapping, summed across all splits.")
A("")
A("| Source | Roya | % of roya | Coco | % of coco | Minador | % of minador | Total instances |")
A("|--------|-----:|----------:|-----:|----------:|--------:|-------------:|----------------:|")
for src in sorted(src_class):
    r_ = src_class[src].get(0, 0)
    c_ = src_class[src].get(1, 0)
    m_ = src_class[src].get(2, 0)
    t_ = r_ + c_ + m_
    A(f"| {src} | {r_} | {pct(r_, t_roya)} | {c_} | {pct(c_, t_coco)} "
      f"| {m_} | {pct(m_, t_min)} | {t_} |")
A(f"| **TOTAL** | **{t_roya}** | 100% | **{t_coco}** | 100% "
  f"| **{t_min}** | 100% | **{all_inst}** |")
A("")
A("**Key observations:**")
A("")
A(f"- **Coco** ({t_coco} annotations): 100% own_field images from Socorro, Santander. "
  "No coco annotations exist in any external dataset used here.")
A(f"- **Minador** ({t_min} annotations): 100% from Silva et al. (rust and leaf miner). "
  "This means minador performance measures *cross-country generalisation* "
  "(Brazil training conditions vs. Colombian deployment) rather than "
  "in-field Colombian performance.")
A(f"- **Roya** ({t_roya} annotations): {pct(roya_own, t_roya)} own_field, "
  f"{pct(roya_rlm, t_roya)} Silva et al. The majority of roya annotations "
  "come from the external dataset; own-field roya coverage is limited.")
A("")
A("---")
A("")
A("## 3. Exclusion Rules and Rationale")
A("")
A("### Excluded: RoCoLe subset")
A("")
A("| Prefix | Images excluded | Reason |")
A("|--------|----------------:|--------|")
A("| SANAS_ROCOLE | 454 | Laboratory white-background images; domain mismatch; "
  "source of all 5 SHA256 cross-split duplicates |")
A("")
A("RoCoLe (Parraga-Alava et al., DOI 10.17632/c5yvn32dzg.2) provides only "
  "healthy-leaf images photographed against a plain white background under "
  "controlled conditions. This distribution does not match Socorro field "
  "conditions. Own-field healthy images (SANAS_NUEVAS, SANAS_SOCORRO) are "
  "retained instead.")
A("")
A("### Cross-source outlier removed")
A("")
A("One spurious coco annotation was deleted from `labels/test/MINEIRO_111.txt` "
  "(33x31 px box in a 448x960 image). Coco is absent from the Silva et al. "
  "class schema; this was a labelling artefact. See `CORRECTIONS.md`.")
A("")
A("### Class 'sano' is NOT a detection class")
A("")
A("Healthy leaves appear as **background images with empty label files**. "
  "The model predicts 3 classes only: roya, coco, minador.")
A("")
A("At inference time the system reports a leaf as healthy by the **absence of "
  "detections above the confidence threshold (0.50)**. No bounding box is "
  "predicted for healthy tissue and no fabricated 'sano' confidence score "
  "is emitted.")
A("")
A(f"Background images (empty label files): **{t_bg}** ({pct(t_bg, t_img)} of dataset).")
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
A("Santander, Colombia. Not publicly released separately. Available here under")
A("CC BY 4.0.")
A("")
A("Prefixes: SANAS_NUEVAS, SANAS_SOCORRO, COCO_RECORTE, COCO_M_A, COCO_Muy_A,")
A("COCO_P_A, ROYA_P_A, ROYA_MA, ROYA_Muy_A.")
A("")
A("### RoCoLe (excluded)")
A("")
A("> Parraga-Alava, Jorge, et al.")
A("> *RoCoLe: A Robusta Coffee Leaf Images Dataset.*")
A("> Mendeley Data, V2.")
A("> DOI: [10.17632/c5yvn32dzg.2](https://doi.org/10.17632/c5yvn32dzg.2)")
A("> License: CC BY 4.0")
A("")
A("Excluded from `decafia_clean`. Preserved in `decafia_yolo_original/`.")
A("")
A("---")
A("")
A("## 5. Class ID Mapping")
A("")
A("| Original ID | New ID | Class | Notes |")
A("|:-----------:|:------:|-------|-------|")
A("| 0 | 0 | roya | unchanged |")
A("| 1 | 1 | coco | unchanged |")
A("| 3 | 2 | minador | remapped from 3 |")
A("| 2 | — | sano | background; no label emitted |")
A("")
A("---")
A("")
A("## 6. File Layout")
A("")
A("```")
A("decafia_clean/")
A("  data.yaml           # nc=3, names=[roya, coco, minador]")
A("  DATASET_CARD.md     # this file")
A("  CORRECTIONS.md      # log of post-build annotation deletions")
A("  images/")
A("    train/  val/  test/")
A("  labels/")
A("    train/  val/  test/   # YOLO format; empty = background (healthy leaf)")
A("```")

card_path = CLEAN / "DATASET_CARD.md"
card_path.write_text("\n".join(lines), encoding="utf-8")
print(f"  Written: {card_path}  ({len(lines)} lines)")


# =============================================================================
# PART 4 — Disambiguate dataset directories
# =============================================================================
print("\n" + "=" * 70)
print("PART 4 — Disambiguate dataset directories")
print("=" * 70)

# Count images and annotations for each dataset
def dataset_stats(root, split_names=("train","val","test"), lbl_subdir="labels"):
    img_total = 0
    ann_total = 0
    for s in split_names:
        img_dir = root / "images" / s
        lbl_dir = root / lbl_subdir / s
        if img_dir.exists():
            img_total += len(list(img_dir.iterdir()))
        if lbl_dir.exists():
            for lbl in lbl_dir.iterdir():
                for line in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.strip():
                        ann_total += 1
    return img_total, ann_total

clean_imgs, clean_ann   = dataset_stats(CLEAN)
orig_imgs,  orig_ann    = dataset_stats(ORIG)

# splits/ has a different layout: splits/train/images, splits/train/labels
splits_dir = BASE / "splits"
splits_imgs = 0
splits_ann  = 0
if splits_dir.exists():
    for s in SPLITS:
        img_dir = splits_dir / s / "images"
        lbl_dir = splits_dir / s / "labels"
        if img_dir.exists():
            splits_imgs += len(list(img_dir.iterdir()))
        if lbl_dir.exists():
            for lbl in lbl_dir.iterdir():
                for line in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.strip():
                        splits_ann += 1

print(f"\n  decafia_clean:         {clean_imgs} imgs, {clean_ann} annotations")
print(f"  decafia_yolo_original: {orig_imgs} imgs,  {orig_ann} annotations")
print(f"  splits/:               {splits_imgs} imgs,  {splits_ann} annotations")

# --- Write 01_dataset/README.md ---
readme_lines = []
R = readme_lines.append

R("# 01_dataset — Dataset Directory Index")
R("")
R(f"Last updated: {TODAY}")
R("")
R("Three image datasets coexist in this directory. Use the table below to")
R("identify which to use for which purpose.")
R("")
R("---")
R("")
R("## Dataset Summary")
R("")
R("| Directory | Status | Images | Annotations | Classes | Use |")
R("|-----------|--------|-------:|------------:|---------|-----|")
R(f"| `decafia_clean/` | **CANONICAL** | {clean_imgs} | {clean_ann} | 3 (roya, coco, minador) | All training and evaluation |")
R(f"| `decafia_yolo_original/` | **SOURCE** | {orig_imgs} | {orig_ann} | 4 (roya, coco, sano, minador) | Reference / provenance audit only |")
R(f"| `splits/` | **ARCHIVED** | {splits_imgs} | {splits_ann} | 4 (roya, coco, sano, minador) | Do not use — see splits/DO_NOT_USE.md |")
R("")
R("---")
R("")
R("## Detailed Records")
R("")
R("### `decafia_clean/` — CANONICAL")
R("")
R(f"**Full path:** `C:\\Users\\luise\\OneDrive\\Documentos\\DECAFIA_v2\\01_dataset\\decafia_clean`  ")
R(f"**Images:** {clean_imgs} (train={card_stats['train']['images']}, val={card_stats['val']['images']}, test={card_stats['test']['images']})  ")
R(f"**Annotations:** {clean_ann} instance lines (roya={t_roya}, coco={t_coco}, minador={t_min})  ")
R(f"**Background images:** {t_bg} (empty label files = healthy leaves)  ")
R("**Class scheme:** nc=3, IDs 0=roya 1=coco 2=minador (minador remapped from original ID 3)  ")
R("**Split:** 70/15/15 stratified by class presence, seed=42  ")
R("**Sources:** own_field (Socorro, Colombia) + Silva et al. rust-and-leaf-miner  ")
R("**Excluded:** RoCoLe (454 images, domain mismatch + cross-split leakage)  ")
R("**Status:** CANONICAL — use this for all training, fine-tuning, and evaluation.")
R("")
R("### `decafia_yolo_original/` — SOURCE")
R("")
R(f"**Full path:** `C:\\Users\\luise\\OneDrive\\Documentos\\DECAFIA_v2\\01_dataset\\decafia_yolo_original`  ")
R(f"**Images:** {orig_imgs} (train=1934, val=549, test=286)  ")
R(f"**Annotations:** {orig_ann} instance lines  ")
R("**Class scheme:** nc=4, IDs 0=roya 1=coco 2=sano 3=minador  ")
R("**Status:** SOURCE — untouched copy of the production dataset as received.")
R("Read-only reference. Do not train from this directly: it contains 454 RoCoLe")
R("images with cross-split SHA256 duplicates and the 4-class scheme including sano boxes.")
R("")
R("### `splits/` — ARCHIVED")
R("")
R(f"**Full path:** `C:\\Users\\luise\\OneDrive\\Documentos\\DECAFIA_v2\\01_dataset\\splits`  ")
R(f"**Images:** {splits_imgs}  ")
R(f"**Annotations:** {splits_ann} instance lines  ")
R("**Class scheme:** nc=4, IDs 0=roya 1=coco 2=sano 3=minador (same as original, unverified)  ")
R("**Status:** ARCHIVED — do not use for training or evaluation.")
R("See `splits/DO_NOT_USE.md` for full explanation.")
R("")
R("---")
R("")
R("## Other Files and Directories")
R("")
R("| Path | Contents |")
R("|------|----------|")
R("| `provenance_manifest.csv` | One row per image in decafia_yolo_original: sha256, source, evidence |")
R("| `DUPLICATES.csv` | 5 SHA256 duplicate pairs found in decafia_yolo_original |")
R("| `DATASET_AUDIT.md` | Pre-build audit report |")
R("| `DATASET SUBCLASES/` | Raw images before partitioning, with subcategory folders |")
R("| `DATASET Y JSON SEGMENTACION/` | Segmentation-format version of the dataset |")
R("| `splits_clean/` | Earlier cleaned split attempt (superseded by decafia_clean) |")
R("| `raw_images/` | Miscellaneous raw images, 51 files |")
R("| `provenance_check/` | Cropped outlier images from provenance audit |")

readme_path = BASE / "README.md"
readme_path.write_text("\n".join(readme_lines), encoding="utf-8")
print(f"\n  Written: {readme_path}")

# --- Write splits/DO_NOT_USE.md ---
do_not_use_lines = []
D = do_not_use_lines.append

D("# DO NOT USE THIS DIRECTORY FOR TRAINING OR EVALUATION")
D("")
D(f"Last reviewed: {TODAY}")
D("")
D("This `splits/` directory is **ARCHIVED**. It has been superseded by")
D("`../decafia_clean/`. The following problems were identified:")
D("")
D("## Problems")
D("")
D("### 1. Cross-split SHA256 duplicates (data leakage)")
D("")
D("At least 3 image pairs with identical SHA256 hashes appear in both train")
D("and test/val splits (all within the SANAS_ROCOLE / RoCoLe subset).")
D("Training on this directory and evaluating on its test split produces")
D("optimistic metrics due to test-set contamination.")
D("")
D("### 2. Four-class scheme with sano boxes")
D("")
D("Labels include class ID 2 (sano / healthy). The production DECAFIA app")
D("does not predict a sano bounding box — it infers health from the absence")
D("of detections above threshold. Training with explicit sano boxes teaches")
D("the model a behaviour inconsistent with the inference pipeline.")
D("")
D("### 3. Unverified annotation count")
D("")
D(f"This directory contains {splits_ann} annotation lines, compared to 12,810")
D("in `decafia_yolo_original` (which covers the same image set). The discrepancy")
D("is unexplained and was flagged during the September 2026 audit. The")
D("annotation set has not been verified.")
D("")
D("### 4. RoCoLe domain mismatch")
D("")
D("Includes 454 RoCoLe images (SANAS_ROCOLE prefix) photographed against a")
D("plain white background under laboratory conditions. This distribution does")
D("not match the Socorro, Santander field conditions the model targets.")
D("")
D("## What to Use Instead")
D("")
D("Use `../decafia_clean/` for all training and evaluation:")
D("")
D("- Cross-split duplicates removed")
D("- RoCoLe excluded")
D("- 3-class scheme (roya, coco, minador); healthy = empty label file")
D("- Provenance verified per image")
D("- 70/15/15 stratified split, seed=42")

do_not_use_path = splits_dir / "DO_NOT_USE.md"
do_not_use_path.write_text("\n".join(do_not_use_lines), encoding="utf-8")
print(f"  Written: {do_not_use_path}")

# --- Check for data.yaml files pointing at splits/ ---
print("\n  Scanning for data.yaml files that reference splits/...")
root = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2")
yaml_hits = []
for yaml_path in root.rglob("data.yaml"):
    try:
        content = yaml_path.read_text(encoding="utf-8", errors="replace")
        if "splits" in content:
            yaml_hits.append((yaml_path, content))
    except Exception:
        pass

if yaml_hits:
    print(f"\n  Found {len(yaml_hits)} data.yaml file(s) referencing 'splits':")
    for ypath, content in yaml_hits:
        # Determine if it's an archived run config
        in_run = any(part in str(ypath) for part in ("runs", "02_training", "wandb", "results"))
        tag = "archived run config" if in_run else "ACTIVE — REVIEW NEEDED"
        print(f"\n    [{tag}]")
        print(f"    Path: {ypath}")
        for line in content.splitlines():
            if "splits" in line:
                print(f"    Line: {line.strip()!r}")
else:
    print("  No data.yaml files reference splits/. OK")

print("\n" + "=" * 70)
print("ALL PARTS COMPLETE")
print("=" * 70)
