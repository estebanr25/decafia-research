"""
A5.9 — EXIF Capture Time and Camera Model
Reads all images from train/val/test splits and extracts EXIF metadata.
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags

DATASET_ROOT = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean")
OUTPUT_DIR = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")
SPLITS = ["train", "val", "test"]

TAG_DATETIME_ORIGINAL = 36867
TAG_DATETIME = 306
TAG_MAKE = 271
TAG_MODEL = 272
TAG_GPS = 34853

DATETIME_FMT = "%Y:%m:%d %H:%M:%S"

errors = []

def parse_timestamp_strict(raw_str, filepath, errors_list):
    """Attempt strict parse. Return (dt_obj or None, raw_str, parse_ok)."""
    if not raw_str or not raw_str.strip():
        return None, raw_str, False
    raw_str = raw_str.strip()
    try:
        dt = datetime.strptime(raw_str, DATETIME_FMT)
        return dt, raw_str, True
    except ValueError as e:
        errors_list.append(
            f"TIMESTAMP_PARSE_ERROR | {filepath} | raw='{raw_str}' | {e}"
        )
        return None, raw_str, False

def extract_exif(filepath, errors_list):
    """Extract EXIF from a single image. Returns dict of fields."""
    record = {
        "filepath": str(filepath),
        "datetime_original": "",
        "datetime_fallback": "",
        "timestamp_used": "",
        "timestamp_source": "no_timestamp",
        "timestamp_raw": "",
        "camera_make": "",
        "camera_model": "",
        "has_gps": False,
    }

    img = Image.open(filepath)  # Let exception propagate — no bare except

    exif_data = img._getexif()
    if exif_data is None:
        return record

    # DateTimeOriginal
    raw_dto = exif_data.get(TAG_DATETIME_ORIGINAL)
    dt_original, raw_original, ok_original = parse_timestamp_strict(
        raw_dto, filepath, errors_list
    )
    if raw_original:
        record["datetime_original"] = (
            dt_original.isoformat() if ok_original else ""
        )
        if not ok_original:
            record["timestamp_raw"] = raw_original

    # DateTime fallback
    raw_dt = exif_data.get(TAG_DATETIME)
    dt_fallback, raw_fb, ok_fallback = parse_timestamp_strict(
        raw_dt, filepath, errors_list
    )
    if raw_fb:
        record["datetime_fallback"] = (
            dt_fallback.isoformat() if ok_fallback else ""
        )

    # Determine which timestamp to use
    if ok_original:
        record["timestamp_used"] = dt_original.isoformat()
        record["timestamp_source"] = "DateTimeOriginal"
    elif ok_fallback:
        record["timestamp_used"] = dt_fallback.isoformat()
        record["timestamp_source"] = "DateTime"
        if not ok_original and raw_original:
            record["timestamp_raw"] = raw_original
    else:
        record["timestamp_source"] = "no_timestamp"
        # timestamp_raw already set if unparseable DTO existed

    # Camera info
    make_val = exif_data.get(TAG_MAKE)
    if make_val:
        record["camera_make"] = str(make_val).strip()

    model_val = exif_data.get(TAG_MODEL)
    if model_val:
        record["camera_model"] = str(model_val).strip()

    # GPS
    record["has_gps"] = TAG_GPS in exif_data

    return record


def main():
    all_records = []
    error_log = OUTPUT_DIR / "exif_errors.txt"

    for split in SPLITS:
        img_dir = DATASET_ROOT / "images" / split
        if not img_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {img_dir}")
        image_files = sorted(img_dir.glob("*.jpg")) + sorted(img_dir.glob("*.JPG")) + \
                      sorted(img_dir.glob("*.jpeg")) + sorted(img_dir.glob("*.png")) + \
                      sorted(img_dir.glob("*.PNG"))
        # Deduplicate (case sensitivity on Windows)
        seen = set()
        unique_files = []
        for f in image_files:
            if f.name.lower() not in seen:
                seen.add(f.name.lower())
                unique_files.append(f)
        image_files = unique_files

        print(f"Split '{split}': found {len(image_files)} images")

        for img_path in image_files:
            stem = img_path.stem
            try:
                rec = extract_exif(img_path, errors)
                rec["split"] = split
                rec["stem"] = stem
                all_records.append(rec)
            except Exception as exc:
                msg = f"PIL_ERROR | {img_path} | {type(exc).__name__}: {exc}"
                errors.append(msg)
                # Still record the image with empty EXIF so we know it existed
                all_records.append({
                    "filepath": str(img_path),
                    "split": split,
                    "stem": stem,
                    "datetime_original": "",
                    "datetime_fallback": "",
                    "timestamp_used": "",
                    "timestamp_source": "no_timestamp",
                    "timestamp_raw": "",
                    "camera_make": "",
                    "camera_model": "",
                    "has_gps": False,
                })
                raise  # Re-raise per "no silent failures" rule

    # Write error log
    with open(error_log, "w", encoding="utf-8") as f:
        if errors:
            f.write("\n".join(errors) + "\n")
        else:
            f.write("No errors.\n")

    # Write CSV
    csv_path = OUTPUT_DIR / "exif_data.csv"
    fieldnames = [
        "filepath", "split", "stem",
        "datetime_original", "datetime_fallback",
        "timestamp_used", "timestamp_source", "timestamp_raw",
        "camera_make", "camera_model", "has_gps"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in all_records:
            writer.writerow(rec)

    # ---- SUMMARY ----
    total = len(all_records)
    n_dto = sum(1 for r in all_records if r["timestamp_source"] == "DateTimeOriginal")
    n_dt  = sum(1 for r in all_records if r["timestamp_source"] == "DateTime")
    n_none= sum(1 for r in all_records if r["timestamp_source"] == "no_timestamp")

    print(f"\n=== SUMMARY ===")
    print(f"Total images processed: {total}")
    print(f"  DateTimeOriginal:      {n_dto}")
    print(f"  DateTime fallback:     {n_dt}")
    print(f"  No timestamp:          {n_none}")

    # Unique camera models
    models = set(r["camera_model"] for r in all_records if r["camera_model"])
    print(f"\nUnique camera models ({len(models)}):")
    for m in sorted(models):
        count = sum(1 for r in all_records if r["camera_model"] == m)
        print(f"  '{m}': {count} images")

    # Date range
    timestamps = [
        datetime.fromisoformat(r["timestamp_used"])
        for r in all_records if r["timestamp_used"]
    ]
    if timestamps:
        print(f"\nDate range:")
        print(f"  Earliest: {min(timestamps).isoformat()}")
        print(f"  Latest:   {max(timestamps).isoformat()}")
    else:
        print("\nDate range: N/A (no timestamps found)")

    # By split
    print("\nTimestamp presence by split:")
    for split in SPLITS:
        split_recs = [r for r in all_records if r["split"] == split]
        s_dto  = sum(1 for r in split_recs if r["timestamp_source"] == "DateTimeOriginal")
        s_dt   = sum(1 for r in split_recs if r["timestamp_source"] == "DateTime")
        s_none = sum(1 for r in split_recs if r["timestamp_source"] == "no_timestamp")
        print(f"  {split}: total={len(split_recs)} | DTO={s_dto} | DT={s_dt} | none={s_none}")

    # By prefix (chars before first underscore)
    from collections import defaultdict
    prefix_counts = defaultdict(lambda: {"DTO": 0, "DT": 0, "none": 0, "total": 0})
    for r in all_records:
        stem = r["stem"]
        prefix = stem.split("_")[0] if "_" in stem else stem
        prefix_counts[prefix]["total"] += 1
        src = r["timestamp_source"]
        if src == "DateTimeOriginal":
            prefix_counts[prefix]["DTO"] += 1
        elif src == "DateTime":
            prefix_counts[prefix]["DT"] += 1
        else:
            prefix_counts[prefix]["none"] += 1

    print("\nTimestamp presence by filename prefix (before first '_'):")
    for prefix in sorted(prefix_counts.keys()):
        pc = prefix_counts[prefix]
        print(f"  {prefix}: total={pc['total']} | DTO={pc['DTO']} | DT={pc['DT']} | none={pc['none']}")

    print(f"\nExif errors logged: {len(errors)}")
    print(f"Output CSV: {csv_path}")
    print(f"Error log:  {error_log}")


if __name__ == "__main__":
    main()
