import pathlib
import csv
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

print("=" * 60)
print("STEP A4 — Merge, Contact Sheets, REPORT.md")
print("=" * 60)

output_dir = pathlib.Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")
dataset_root = pathlib.Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean")
provenance_path = pathlib.Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\provenance_manifest.csv")

splits = ["train", "val", "test"]
class_names = {0: "roya", 1: "coco", 2: "minador"}

# 1. Read provenance manifest
print("\n[1] Reading provenance manifest...")
manifest = {}
with open(provenance_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    manifest_fields = reader.fieldnames
    print(f"  Manifest fields: {manifest_fields}")
    for row in reader:
        # Key by stem (filename without extension)
        stem = pathlib.Path(row.get("filename", row.get("file", row.get("image", "")))).stem
        if not stem:
            # Try first column
            for k, v in row.items():
                if v:
                    stem = pathlib.Path(v).stem
                    break
        manifest[stem] = row

print(f"  Manifest rows loaded: {len(manifest)}")
if manifest:
    sample_key = next(iter(manifest))
    print(f"  Sample row (stem={sample_key}): {manifest[sample_key]}")

# Helper: get source from manifest
def get_source(stem):
    row = manifest.get(stem, {})
    # Try common field names for source
    for field in ["source", "origin", "dataset", "batch", "collection"]:
        if field in row and row[field]:
            return row[field]
    # Return all fields joined if no clear source
    if row:
        return str(row)
    return "UNKNOWN"

# Helper: get image prefix (chars before first underscore or digit)
def get_prefix(stem):
    prefix = ""
    for ch in stem:
        if ch == "_" or ch.isdigit():
            break
        prefix += ch
    return prefix if prefix else stem[:4]

# Count labels per class for a stem in given split
def get_label_counts(stem, split):
    lbl_path = dataset_root / "labels" / split / (stem + ".txt")
    counts = {"roya": 0, "coco": 0, "minador": 0}
    if lbl_path.exists():
        with open(lbl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cls_id = int(line.split()[0])
                    name = class_names.get(cls_id, f"cls{cls_id}")
                    if name in counts:
                        counts[name] += 1
    return counts

# 2. Read SIFT results
print("\n[2] Reading sift_results.csv...")
sift_results = []
with open(output_dir / "sift_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sift_results.append(row)
print(f"  SIFT results rows: {len(sift_results)}")

# Build merged near_duplicate_pairs.csv
print("\n[2b] Building near_duplicate_pairs.csv...")
merged_rows = []
unreadable = []

for i, row in enumerate(sift_results):
    path_a = row["path_a"]
    path_b = row["path_b"]
    split_a = row["split_a"]
    split_b = row["split_b"]
    stem_a = row["stem_a"]
    stem_b = row["stem_b"]

    # Verify images loadable (only check, don't load full resolution here)
    for p in [path_a, path_b]:
        pp = pathlib.Path(p)
        if not pp.exists():
            unreadable.append(f"NOT_EXISTS: {p}")
        elif pp.stat().st_size == 0:
            unreadable.append(f"ZERO_BYTES: {p}")

    prefix_a = get_prefix(stem_a)
    prefix_b = get_prefix(stem_b)
    source_a = get_source(stem_a)
    source_b = get_source(stem_b)

    label_a = get_label_counts(stem_a, split_a)
    label_b = get_label_counts(stem_b, split_b)

    merged_rows.append({
        "img_a_path": path_a,
        "img_a_split": split_a,
        "img_a_stem": stem_a,
        "img_a_prefix": prefix_a,
        "img_a_source": source_a,
        "img_b_path": path_b,
        "img_b_split": split_b,
        "img_b_stem": stem_b,
        "img_b_prefix": prefix_b,
        "img_b_source": source_b,
        "label_count_a_roya": label_a["roya"],
        "label_count_a_coco": label_a["coco"],
        "label_count_a_minador": label_a["minador"],
        "label_count_b_roya": label_b["roya"],
        "label_count_b_coco": label_b["coco"],
        "label_count_b_minador": label_b["minador"],
        "phash_dist": row["min_phash_dist"],
        "dhash_dist": row["dhash_dist"],
        "cosine_sim": row["cosine_sim"],
        "sift_inliers": int(row["ransac_inliers"]),
        "containment_a_in_b": row["containment_a_in_b"],
        "containment_b_in_a": row["containment_b_in_a"],
    })

    if (i + 1) % 1000 == 0:
        print(f"  Processed {i + 1}/{len(sift_results)}...")

print(f"  Merged rows: {len(merged_rows)}")

# Sort by sift_inliers descending
merged_rows.sort(key=lambda r: r["sift_inliers"], reverse=True)

out_csv = output_dir / "near_duplicate_pairs.csv"
fieldnames_merged = [
    "img_a_path", "img_a_split", "img_a_stem", "img_a_prefix", "img_a_source",
    "img_b_path", "img_b_split", "img_b_stem", "img_b_prefix", "img_b_source",
    "label_count_a_roya", "label_count_a_coco", "label_count_a_minador",
    "label_count_b_roya", "label_count_b_coco", "label_count_b_minador",
    "phash_dist", "dhash_dist", "cosine_sim", "sift_inliers",
    "containment_a_in_b", "containment_b_in_a"
]
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames_merged)
    writer.writeheader()
    for r in merged_rows:
        writer.writerow(r)
print(f"  Saved {len(merged_rows)} rows to {out_csv}")

# 3. Write unreadable_images.txt
unreadable_path = output_dir / "unreadable_images.txt"
with open(unreadable_path, "w", encoding="utf-8") as f:
    if unreadable:
        for u in unreadable:
            f.write(u + "\n")
    else:
        f.write("No unreadable images found.\n")
print(f"  Unreadable images: {len(unreadable)}")

# 4. Generate contact sheets
print("\n[4] Generating contact sheets...")

cross_rows = [r for r in merged_rows if r["img_a_split"] != r["img_b_split"]]

def make_contact_sheet(pairs, output_path, max_w=300):
    """Generate contact sheet: each pair = side-by-side tile with labels."""
    if not pairs:
        print(f"  No pairs for {output_path.name}, skipping.")
        return

    TILE_W = max_w * 2 + 20  # two images + gap
    TILE_H = max_w + 60       # image + label text area
    COLS = 2
    n = len(pairs)
    rows_count = (n + COLS - 1) // COLS
    canvas_w = TILE_W * COLS + 20
    canvas_h = TILE_H * rows_count + 20

    canvas = Image.new("RGB", (canvas_w, canvas_h), color=(40, 40, 40))
    draw = ImageDraw.Draw(canvas)

    # Try to get a font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()

    for idx, pair in enumerate(pairs):
        col = idx % COLS
        row_idx = idx // COLS
        x0 = col * TILE_W + 10
        y0 = row_idx * TILE_H + 10

        for side, img_path, img_split, img_stem in [
            ("A", pair["img_a_path"], pair["img_a_split"], pair["img_a_stem"]),
            ("B", pair["img_b_path"], pair["img_b_split"], pair["img_b_stem"])
        ]:
            offset_x = x0 if side == "A" else x0 + max_w + 10
            try:
                img = Image.open(img_path).convert("RGB")
            except Exception as e:
                img = Image.new("RGB", (max_w, max_w), color=(200, 50, 50))

            # Resize preserving aspect ratio to fit in max_w x max_w
            ow, oh = img.size
            scale = min(max_w / ow, max_w / oh)
            nw, nh = int(ow * scale), int(oh * scale)
            img_resized = img.resize((nw, nh), Image.LANCZOS)

            # Paste onto tile background
            tile_bg = Image.new("RGB", (max_w, max_w), color=(80, 80, 80))
            paste_x = (max_w - nw) // 2
            paste_y = (max_w - nh) // 2
            tile_bg.paste(img_resized, (paste_x, paste_y))
            canvas.paste(tile_bg, (offset_x, y0))

        # Draw label text below the pair
        inliers = pair["sift_inliers"]
        cos = float(pair["cosine_sim"])
        phash = pair["phash_dist"]
        label = (f"A:{pair['img_a_stem'][:14]} ({pair['img_a_split']})  "
                 f"B:{pair['img_b_stem'][:14]} ({pair['img_b_split']})  "
                 f"inliers={inliers} cos={cos:.3f} ph={phash}")
        text_y = y0 + max_w + 2
        draw.text((x0, text_y), label, fill=(220, 220, 100), font=font)

    canvas.save(str(output_path))
    print(f"  Saved {output_path.name} ({n} pairs, canvas {canvas_w}x{canvas_h})")

# Top 40 cross-split pairs ranked by sift_inliers descending
top40 = cross_rows[:40]
make_contact_sheet(top40, output_dir / "contact_sheet_top40.png")

# 20 pairs with inliers 15-29
above15 = [r for r in cross_rows if 15 <= r["sift_inliers"] <= 29][:20]
make_contact_sheet(above15, output_dir / "contact_sheet_above15.png")

# 20 pairs with inliers 5-14
below15 = [r for r in cross_rows if 5 <= r["sift_inliers"] <= 14][:20]
make_contact_sheet(below15, output_dir / "contact_sheet_below15.png")

# 5. Build statistics for REPORT.md
print("\n[5] Computing statistics for REPORT.md...")

# Cross-split pair counts by method and threshold
def count_cross_by_threshold(rows, field, thresholds, op=">="):
    result = {}
    for t in thresholds:
        if op == ">=":
            result[t] = sum(1 for r in rows if float(r[field]) >= t)
        else:
            result[t] = sum(1 for r in rows if float(r[field]) <= t)
    return result

cross_sift_counts = count_cross_by_threshold(cross_rows, "sift_inliers", [15, 30, 60])
cross_cos_counts  = count_cross_by_threshold(cross_rows, "cosine_sim", [0.90, 0.95, 0.99])
cross_ph_counts   = count_cross_by_threshold(cross_rows, "phash_dist", [0, 4, 8, 12], op="<=")

# Breakdown by split pair
def split_pair_label(a, b):
    pair = tuple(sorted([a, b]))
    return f"{pair[0]}↔{pair[1]}"

split_pair_counts_sift15 = {}
for r in cross_rows:
    if r["sift_inliers"] >= 15:
        lbl = split_pair_label(r["img_a_split"], r["img_b_split"])
        split_pair_counts_sift15[lbl] = split_pair_counts_sift15.get(lbl, 0) + 1

split_pair_counts_cos95 = {}
for r in cross_rows:
    if float(r["cosine_sim"]) >= 0.95:
        lbl = split_pair_label(r["img_a_split"], r["img_b_split"])
        split_pair_counts_cos95[lbl] = split_pair_counts_cos95.get(lbl, 0) + 1

# Breakdown by prefix
prefix_counts_sift30 = {}
for r in cross_rows:
    if r["sift_inliers"] >= 30:
        px = r["img_a_prefix"]
        prefix_counts_sift30[px] = prefix_counts_sift30.get(px, 0) + 1

# How many TEST images have likely duplicate in TRAIN
test_train_rows = [r for r in cross_rows if
                   (r["img_a_split"] == "test" and r["img_b_split"] == "train") or
                   (r["img_a_split"] == "train" and r["img_b_split"] == "test")]

def get_test_stem(r):
    if r["img_a_split"] == "test":
        return r["img_a_stem"]
    return r["img_b_stem"]

def get_test_labels(r):
    if r["img_a_split"] == "test":
        return {"roya": r["label_count_a_roya"], "coco": r["label_count_a_coco"], "minador": r["label_count_a_minador"]}
    return {"roya": r["label_count_b_roya"], "coco": r["label_count_b_coco"], "minador": r["label_count_b_minador"]}

for thresh_name, threshold, field, op in [
    ("sift_inliers>=15", 15, "sift_inliers", ">="),
    ("sift_inliers>=30", 30, "sift_inliers", ">="),
    ("cosine_sim>=0.95", 0.95, "cosine_sim", ">="),
    ("cosine_sim>=0.99", 0.99, "cosine_sim", ">="),
]:
    if op == ">=":
        filtered = [r for r in test_train_rows if float(r[field]) >= threshold]
    else:
        filtered = [r for r in test_train_rows if float(r[field]) <= threshold]

    unique_test_stems = set(get_test_stem(r) for r in filtered)
    total_anno = {"roya": 0, "coco": 0, "minador": 0}
    seen_stems = set()
    for r in filtered:
        ts = get_test_stem(r)
        if ts not in seen_stems:
            seen_stems.add(ts)
            lbl = get_test_labels(r)
            for cls in ["roya", "coco", "minador"]:
                total_anno[cls] += int(lbl[cls])

    print(f"  [{thresh_name}] Unique TEST images with dup in TRAIN: {len(unique_test_stems)}, "
          f"annotations: roya={total_anno['roya']}, coco={total_anno['coco']}, minador={total_anno['minador']}")

# Top source breakdown
source_counts = {}
for r in cross_rows:
    if r["sift_inliers"] >= 15:
        for s in [r["img_a_source"], r["img_b_source"]]:
            source_counts[s] = source_counts.get(s, 0) + 1

# Compute unique test images with duplicate in train at each threshold for report
thresh_data = {}
for thresh_name, threshold, field, op in [
    ("sift>=15", 15, "sift_inliers", ">="),
    ("sift>=30", 30, "sift_inliers", ">="),
    ("sift>=60", 60, "sift_inliers", ">="),
    ("cos>=0.90", 0.90, "cosine_sim", ">="),
    ("cos>=0.95", 0.95, "cosine_sim", ">="),
    ("cos>=0.99", 0.99, "cosine_sim", ">="),
]:
    if op == ">=":
        filtered = [r for r in test_train_rows if float(r[field]) >= threshold]
    else:
        filtered = [r for r in test_train_rows if float(r[field]) <= threshold]
    unique_test = set(get_test_stem(r) for r in filtered)
    total_anno = {"roya": 0, "coco": 0, "minador": 0}
    seen = set()
    for r in filtered:
        ts = get_test_stem(r)
        if ts not in seen:
            seen.add(ts)
            lbl = get_test_labels(r)
            for cls in ["roya", "coco", "minador"]:
                total_anno[cls] += int(lbl[cls])
    thresh_data[thresh_name] = {"unique_test": len(unique_test), "anno": total_anno}

# 5. Write REPORT.md
report_path = output_dir / "REPORT.md"
print(f"\n[5] Writing REPORT.md to {report_path}...")

report_lines = []
report_lines.append("# DECAFIA Near-Duplicate Audit Report\n")
report_lines.append(f"**Dataset:** decafia_clean — 2315 images (train=1618, val=348, test=349)\n")
report_lines.append(f"**Provenance manifest:** {provenance_path}\n")
report_lines.append(f"**Output folder:** {output_dir}\n")
report_lines.append(f"**Date run:** 2026-09-14\n\n")

report_lines.append("---\n\n")
report_lines.append("## 1. Flagged Cross-Split Pairs by Method and Threshold\n\n")

report_lines.append("### 1a. Perceptual Hash (pHash, min of direct and flipped)\n\n")
report_lines.append("| Threshold (≤) | Cross-split pairs |\n")
report_lines.append("|---|---|\n")
for t in [0, 4, 8, 12]:
    report_lines.append(f"| phash_dist ≤ {t} | {cross_ph_counts[t]} |\n")
report_lines.append("\n")

report_lines.append("### 1b. ResNet-50 Cosine Similarity (cross-split top-5)\n\n")
report_lines.append("| Threshold (≥) | Unique cross-split pairs |\n")
report_lines.append("|---|---|\n")
for t in [0.90, 0.95, 0.99]:
    report_lines.append(f"| cosine_sim ≥ {t} | {cross_cos_counts[t]} |\n")
report_lines.append("\n")

report_lines.append("### 1c. SIFT Geometric Verification (RANSAC inliers)\n\n")
report_lines.append("| Threshold (≥) | Cross-split pairs |\n")
report_lines.append("|---|---|\n")
for t in [15, 30, 60]:
    report_lines.append(f"| sift_inliers ≥ {t} | {cross_sift_counts[t]} |\n")
report_lines.append("\n")

report_lines.append("---\n\n")
report_lines.append("## 2. Breakdown by Split Pair\n\n")

report_lines.append("### sift_inliers ≥ 15\n\n")
report_lines.append("| Split pair | Count |\n")
report_lines.append("|---|---|\n")
for lbl in ["test↔train", "test↔val", "train↔val"]:
    report_lines.append(f"| {lbl} | {split_pair_counts_sift15.get(lbl, 0)} |\n")
report_lines.append("\n")

report_lines.append("### cosine_sim ≥ 0.95\n\n")
report_lines.append("| Split pair | Count |\n")
report_lines.append("|---|---|\n")
for lbl in ["test↔train", "test↔val", "train↔val"]:
    report_lines.append(f"| {lbl} | {split_pair_counts_cos95.get(lbl, 0)} |\n")
report_lines.append("\n")

report_lines.append("---\n\n")
report_lines.append("## 3. Breakdown by Filename Prefix\n\n")
report_lines.append("(Pairs with sift_inliers ≥ 30, by img_a_prefix)\n\n")
report_lines.append("| Prefix | Count |\n")
report_lines.append("|---|---|\n")
for px, cnt in sorted(prefix_counts_sift30.items(), key=lambda x: -x[1]):
    report_lines.append(f"| {px} | {cnt} |\n")
report_lines.append("\n")

report_lines.append("---\n\n")
report_lines.append("## 4. TEST Images with Likely Duplicate/Parent in TRAIN\n\n")
report_lines.append("| Method & Threshold | Unique TEST images | Annotations roya | Annotations coco | Annotations minador |\n")
report_lines.append("|---|---|---|---|---|\n")
for key, data in thresh_data.items():
    a = data["anno"]
    report_lines.append(f"| {key} | {data['unique_test']} | {a['roya']} | {a['coco']} | {a['minador']} |\n")
report_lines.append("\n")

report_lines.append("---\n\n")
report_lines.append("## 5. Limitations\n\n")
report_lines.append("""- **Hash methods** (pHash, dHash) only detect near-identical images. Cropped, recoloured, or resized images at distance > 12 bits are missed by this pass.
- **ResNet-50 embeddings** were computed with `num_workers=0` (CPU DataLoader) to avoid multiprocessing issues; this does not affect correctness. The top-5 cross-split search is asymmetric: very similar pairs that happen to be ranked 6th or lower are missed. Cosine similarity at the 50th percentile is ~0.92 across this dataset, meaning most images share moderately similar visual features (consistent field conditions); many pairs above 0.90 are NOT true duplicates.
- **SIFT verification** was run on 9589 candidates (union of hash≤12 and cos≥0.85). Pairs with very low texture (background images) may get 0 SIFT keypoints, recorded as 0 inliers in sift_issues.txt (642 issues logged). Homography requires ≥4 matches; pairs with 1-3 matches are logged but not considered verified.
- **Provenance manifest** was used to label sources; if any image is absent from the manifest, source is reported as UNKNOWN.
- **No within-split SIFT** was performed (hash candidates and embedding top-5 were cross-split only by design). Within-split duplicates are flagged in the hash step (66 pairs at pHash=0) but not SIFT-verified here.
- These findings flag *candidates* for human review, not confirmed leakage. Final leakage determination requires domain knowledge of image acquisition.
""")

report_content = "".join(report_lines)
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_content)
print(f"  REPORT.md written.")
print("\n" + "=" * 60)
print("REPORT.md CONTENTS:")
print("=" * 60)
print(report_content)
print("=" * 60)
print("STEP A4 COMPLETE")
print("=" * 60)
