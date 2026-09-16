import sys
import os
import pathlib
import glob

print("=" * 60)
print("STEP 0 — Environment and Dataset Sanity")
print("=" * 60)

# 1. Python version
print(f"\n[1] Python version: {sys.version}")

# 2. Package versions
import torch
import torchvision
import cv2
import numpy as np
from PIL import Image

print(f"\n[2] Package versions:")
print(f"  torch:        {torch.__version__}")
print(f"  torchvision:  {torchvision.__version__}")
print(f"  cv2:          {cv2.__version__}")
print(f"  numpy:        {np.__version__}")
print(f"  PIL:          {Image.__version__}")
print(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")

# 3. SIFT check — actually call it, no try/except
sift = cv2.SIFT_create()
print(f"\n[3] SIFT_OK (cv2.SIFT_create() returned: {type(sift).__name__})")

# 4. Read data.yaml
data_yaml_path = r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean\data.yaml"
with open(data_yaml_path, "r", encoding="utf-8") as f:
    data_yaml_content = f.read()
print(f"\n[4] data.yaml contents:")
print(data_yaml_content)

# 5. Count images and label files per split
dataset_root = pathlib.Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean")
splits = ["train", "val", "test"]
image_exts = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]

print(f"\n[5] File counts per split:")
total_images = 0
total_labels = 0
split_image_counts = {}
split_label_counts = {}

for split in splits:
    img_dir = dataset_root / "images" / split
    lbl_dir = dataset_root / "labels" / split

    img_files = []
    for ext in image_exts:
        img_files.extend(img_dir.glob(ext))
    # deduplicate by case (on Windows glob might be case-insensitive)
    img_files = list({f.name.lower(): f for f in img_files}.values())

    lbl_files = list(lbl_dir.glob("*.txt"))

    n_img = len(img_files)
    n_lbl = len(lbl_files)
    split_image_counts[split] = img_files
    split_label_counts[split] = lbl_files
    total_images += n_img
    total_labels += n_lbl
    print(f"  {split}: images={n_img}, label_files={n_lbl}")

print(f"  TOTAL: images={total_images}, label_files={total_labels}")

# Expected
expected_images = {"train": 1618, "val": 348, "test": 349}
expected_total_images = 2315

# 6. Count annotations per split
print(f"\n[6] Annotation counts per split:")
total_anno = 0
total_empty = 0
expected_annotations = {"train": 8950, "val": 1896, "test": 1948}
expected_empty = {"train": 779, "val": 167, "test": 167}

split_anno_ok = True
for split in splits:
    lbl_dir = dataset_root / "labels" / split
    lbl_files = list(lbl_dir.glob("*.txt"))
    anno_count = 0
    empty_count = 0
    for lbl_file in lbl_files:
        with open(lbl_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        non_empty = [l for l in lines if l]
        anno_count += len(non_empty)
        if len(non_empty) == 0:
            empty_count += 1
    total_anno += anno_count
    total_empty += empty_count
    match_anno = "OK" if anno_count == expected_annotations[split] else f"MISMATCH (expected {expected_annotations[split]})"
    match_empty = "OK" if empty_count == expected_empty[split] else f"MISMATCH (expected {expected_empty[split]})"
    print(f"  {split}: annotations={anno_count} [{match_anno}], empty_txt={empty_count} [{match_empty}]")

print(f"  TOTAL: annotations={total_anno}, empty_txt={total_empty}")

# 7. Check for filenames starting with SANAS_ROCOLE
print(f"\n[7] Filenames starting with SANAS_ROCOLE:")
sanas_found = []
for split in splits:
    img_dir = dataset_root / "images" / split
    for ext in image_exts:
        for f in img_dir.glob(ext):
            if f.name.startswith("SANAS_ROCOLE"):
                sanas_found.append(str(f))
if sanas_found:
    for s in sanas_found:
        print(f"  FOUND: {s}")
else:
    print("  None found.")

# 8. Check for zero-byte files (cloud-only placeholders)
print(f"\n[8] Checking for zero-byte image files (cloud-only placeholders):")
zero_byte_files = []
for split in splits:
    img_files = split_image_counts[split]
    for f in img_files:
        size = f.stat().st_size
        if size == 0:
            zero_byte_files.append((str(f), split, size))

if zero_byte_files:
    print(f"  ZERO-BYTE FILES FOUND ({len(zero_byte_files)}):")
    for path, split, size in zero_byte_files:
        print(f"    [{split}] {path} ({size} bytes)")
else:
    print("  No zero-byte files found. All images appear locally available.")

# STOP-IF checks
print(f"\n{'=' * 60}")
print("STOP-IF CHECKS:")
stop = False

for split in splits:
    n = len(split_image_counts[split])
    if n != expected_images[split]:
        print(f"  STOP: {split} image count {n} != expected {expected_images[split]}")
        stop = True

if total_images != expected_total_images:
    print(f"  STOP: total images {total_images} != expected {expected_total_images}")
    stop = True

ann_total_expected = 12794
if total_anno != ann_total_expected:
    print(f"  STOP: total annotations {total_anno} != expected {ann_total_expected}")
    stop = True

for split in splits:
    # re-check per split
    lbl_dir = dataset_root / "labels" / split
    lbl_files = list(lbl_dir.glob("*.txt"))
    anno_count = sum(
        len([l for l in open(lf, "r", encoding="utf-8").read().splitlines() if l.strip()])
        for lf in lbl_files
    )
    empty_count = sum(
        1 for lf in lbl_files
        if not any(l.strip() for l in open(lf, "r", encoding="utf-8").read().splitlines())
    )
    if anno_count != expected_annotations[split]:
        print(f"  STOP: {split} annotations {anno_count} != expected {expected_annotations[split]}")
        stop = True
    if empty_count != expected_empty[split]:
        print(f"  STOP: {split} empty_txt {empty_count} != expected {expected_empty[split]}")
        stop = True

if zero_byte_files:
    print(f"  STOP: {len(zero_byte_files)} zero-byte (cloud-only) files found")
    stop = True

if not stop:
    print("  All STOP-IF checks PASSED. Safe to proceed.")
else:
    print("  STOP-IF TRIGGERED — halting here.")

print("=" * 60)
