"""
STEP 1 — Inventory
Scan all images across train/val/test splits, extract metadata, verify totals.
"""
import os
import re
import csv
import sys
import time

DATASET_ROOT = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean"
PROVENANCE_CSV = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/provenance_manifest.csv"
AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
OUTPUT_CSV = os.path.join(AUDIT_DIR, "inventory.csv")

SPLITS = ["train", "val", "test"]
EXPECTED = {"train": 1618, "val": 348, "test": 349, "total": 2315}
EXPECTED_TOTAL_ANNOTS = 12794
EXPECTED_BACKGROUND = {"train": 779, "val": 167, "test": 167, "total": 1113}

def parse_prefix_and_number(stem):
    """Extract prefix (everything before last _<digits>) and trailing number."""
    m = re.search(r'^(.*?)_(\d+)$', stem)
    if m:
        return m.group(1), int(m.group(2))
    return None, None

def load_provenance():
    """Load provenance manifest, keyed by stem (filename without extension)."""
    prov = {}
    with open(PROVENANCE_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row['filename']
            stem = os.path.splitext(fname)[0]
            prov[stem] = row.get('inferred_source', 'unknown')
    return prov

def count_annotations(label_path):
    """Count annotations per class in a YOLO label file.
    Returns (roya, coco, minador, total, is_background).
    Raises on any read error — do NOT silently skip.
    """
    if not os.path.exists(label_path):
        raise FileNotFoundError(f"Label file not found: {label_path}")
    with open(label_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
    lines = [l for l in lines if l]  # remove blank lines
    if not lines:
        return 0, 0, 0, 0, True
    roya = coco = minador = 0
    for line in lines:
        parts = line.split()
        if not parts:
            raise ValueError(f"Empty line in label file: {label_path}")
        cls = int(parts[0])
        if cls == 0:
            roya += 1
        elif cls == 1:
            coco += 1
        elif cls == 2:
            minador += 1
        else:
            raise ValueError(f"Unknown class {cls} in {label_path}")
    total = roya + coco + minador
    return roya, coco, minador, total, False

def main():
    print("=== STEP 1: INVENTORY ===")
    start = time.time()

    prov_map = load_provenance()
    print(f"Loaded provenance for {len(prov_map)} stems")

    records = []
    split_counts = {s: 0 for s in SPLITS}
    split_background = {s: 0 for s in SPLITS}
    total_annots = 0
    parse_failures = []
    read_errors = []

    # For Step 7.6 baseline: count files and bytes in decafia_clean/ excluding split_grouped_v1/
    file_count_baseline = 0
    byte_count_baseline = 0

    for root, dirs, files in os.walk(DATASET_ROOT):
        # Exclude split_grouped_v1 from baseline count
        dirs[:] = [d for d in dirs if d != 'split_grouped_v1']
        for fn in files:
            fpath = os.path.join(root, fn)
            try:
                byte_count_baseline += os.path.getsize(fpath)
                file_count_baseline += 1
            except OSError as e:
                read_errors.append(f"OSError reading size of {fpath}: {e}")

    print(f"Baseline file count (excl. split_grouped_v1): {file_count_baseline}")
    print(f"Baseline total bytes (excl. split_grouped_v1): {byte_count_baseline}")

    # Save baseline for Step 7
    with open(os.path.join(AUDIT_DIR, "baseline_filecount.txt"), 'w') as f:
        f.write(f"file_count={file_count_baseline}\n")
        f.write(f"byte_count={byte_count_baseline}\n")

    for split in SPLITS:
        img_dir = os.path.join(DATASET_ROOT, "images", split)
        lbl_dir = os.path.join(DATASET_ROOT, "labels", split)
        img_files = sorted(os.listdir(img_dir))
        for fn in img_files:
            if not fn.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                continue
            stem = os.path.splitext(fn)[0]
            prefix, number = parse_prefix_and_number(stem)
            if prefix is None or number is None:
                parse_failures.append(stem)
                # Still continue to record but flag
                prefix = stem
                number = -1

            source = prov_map.get(stem, "not_in_manifest")

            label_path = os.path.join(lbl_dir, stem + ".txt")
            try:
                roya, coco, minador, total, is_bg = count_annotations(label_path)
            except Exception as e:
                read_errors.append(f"ERROR reading labels for {stem}: {e}")
                raise  # Per rules: do NOT silently skip

            records.append({
                "stem": stem,
                "split": split,
                "prefix": prefix,
                "trailing_number": number,
                "source": source,
                "roya_count": roya,
                "coco_count": coco,
                "minador_count": minador,
                "total_annots": total,
                "is_background": is_bg
            })

            split_counts[split] += 1
            total_annots += total
            if is_bg:
                split_background[split] += 1

    print(f"\n--- Image counts ---")
    for s in SPLITS:
        exp = EXPECTED[s]
        actual = split_counts[s]
        match = "OK" if actual == exp else f"MISMATCH (expected {exp})"
        print(f"  {s}: {actual} [{match}]")
    total_images = sum(split_counts.values())
    total_match = "OK" if total_images == EXPECTED["total"] else f"MISMATCH (expected {EXPECTED['total']})"
    print(f"  total: {total_images} [{total_match}]")

    print(f"\n--- Total annotations: {total_annots} (expected {EXPECTED_TOTAL_ANNOTS}) ---")
    annot_match = "OK" if total_annots == EXPECTED_TOTAL_ANNOTS else "MISMATCH"
    print(f"  [{annot_match}]")

    print(f"\n--- Background images (empty labels) ---")
    total_bg = sum(split_background.values())
    for s in SPLITS:
        exp = EXPECTED_BACKGROUND[s]
        actual = split_background[s]
        match = "OK" if actual == exp else f"MISMATCH (expected {exp})"
        print(f"  {s}: {actual} [{match}]")
    total_bg_match = "OK" if total_bg == EXPECTED_BACKGROUND["total"] else f"MISMATCH (expected {EXPECTED_BACKGROUND['total']})"
    print(f"  total: {total_bg} [{total_bg_match}]")

    # STOP-IF checks
    stop = False
    if total_images != EXPECTED["total"]:
        print(f"\nSTOP-IF: Total image count {total_images} != {EXPECTED['total']}")
        stop = True
    for s in SPLITS:
        if split_counts[s] != EXPECTED[s]:
            print(f"STOP-IF: {s} count {split_counts[s]} != {EXPECTED[s]}")
            stop = True
    if total_annots != EXPECTED_TOTAL_ANNOTS:
        print(f"STOP-IF: Total annotations {total_annots} != {EXPECTED_TOTAL_ANNOTS}")
        stop = True
    if total_bg != EXPECTED_BACKGROUND["total"]:
        print(f"STOP-IF: Total background {total_bg} != {EXPECTED_BACKGROUND['total']}")
        stop = True
    for s in SPLITS:
        if split_background[s] != EXPECTED_BACKGROUND[s]:
            print(f"STOP-IF: {s} background {split_background[s]} != {EXPECTED_BACKGROUND[s]}")
            stop = True

    if parse_failures:
        print(f"\nSTOP-IF: {len(parse_failures)} stems could not parse trailing number:")
        for stem in parse_failures:
            print(f"  {stem}")
        stop = True

    if read_errors:
        print(f"\nRead errors encountered:")
        for e in read_errors:
            print(f"  {e}")

    if stop:
        print("\n=== STOPPED due to STOP-IF condition ===")
        sys.exit(1)

    # Report SANAS with non-empty labels and non-SANAS with empty labels
    print("\n--- SANAS images with non-empty labels ---")
    sanas_nonempty = [r for r in records if r['prefix'].startswith('SANAS') and not r['is_background']]
    if sanas_nonempty:
        for r in sanas_nonempty:
            print(f"  {r['stem']} (split={r['split']}, annots={r['total_annots']})")
    else:
        print("  None found.")

    print("\n--- Non-SANAS images with empty labels ---")
    nonsanas_bg = [r for r in records if not r['prefix'].startswith('SANAS') and r['is_background']]
    if nonsanas_bg:
        for r in nonsanas_bg:
            print(f"  {r['stem']} (split={r['split']}, prefix={r['prefix']})")
    else:
        print("  None found.")

    # Save inventory.csv
    fieldnames = ["stem", "split", "prefix", "trailing_number", "source",
                  "roya_count", "coco_count", "minador_count", "total_annots", "is_background"]
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"\nSaved inventory.csv: {len(records)} rows -> {OUTPUT_CSV}")

    elapsed = time.time() - start
    print(f"\nStep 1 complete in {elapsed:.1f}s")

if __name__ == "__main__":
    main()
