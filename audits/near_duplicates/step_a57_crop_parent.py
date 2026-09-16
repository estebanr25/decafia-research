"""
A5.7 — Crop → Parent Mapping
Identifies images that are crops of other images using SIFT containment and resolution ratio.
"""

import csv
import os
import sys
from pathlib import Path
from collections import defaultdict

import cv2

SIFT_CSV   = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates\sift_results.csv")
HASHES_CSV = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates\image_hashes.csv")
OUTPUT_DIR = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")

SIFT_INLIER_THRESHOLD     = 30    # for containment signal
CONTAINMENT_THRESHOLD     = 0.7   # containment_a_in_b or containment_b_in_a
RESOLUTION_INLIER_MIN     = 15    # for resolution-ratio signal
AREA_RATIO_MIN            = 2.0   # parent area >= 2x crop area


def load_sift_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        print(f"sift_results.csv columns: {cols}")
        for row in reader:
            rows.append(row)
    return rows, cols


def load_hashes_csv(path):
    """Returns dict stem -> {filepath, split}"""
    info = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            info[row["stem"]] = {
                "filepath": row["filepath"],
                "split": row["split"],
            }
    return info


def get_image_dimensions(filepath):
    """Read actual pixel dimensions using cv2. Raises on failure."""
    img = cv2.imread(str(filepath), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"cv2.imread returned None for: {filepath}")
    h, w = img.shape[:2]
    return w, h


def compute_area_ratio(w_a, h_a, w_b, h_b):
    """Returns (larger_area / smaller_area, which_is_larger: 'a' or 'b')"""
    area_a = w_a * h_a
    area_b = w_b * h_b
    if area_a == 0 or area_b == 0:
        return 1.0, "equal"
    if area_a >= area_b:
        return area_a / area_b, "a"
    else:
        return area_b / area_a, "b"


def main():
    # Load SIFT results
    sift_rows, sift_cols = load_sift_csv(SIFT_CSV)
    print(f"SIFT rows loaded: {len(sift_rows)}")

    # Check for containment columns
    has_containment = (
        "containment_a_in_b" in sift_cols
        and "containment_b_in_a" in sift_cols
    )
    if has_containment:
        # Check if they're all zero
        vals = [
            float(r.get("containment_a_in_b", 0) or 0) +
            float(r.get("containment_b_in_a", 0) or 0)
            for r in sift_rows
        ]
        all_zero = all(v == 0 for v in vals)
        if all_zero:
            has_containment = False
            print("NOTE: containment columns present but all-zero — using resolution_ratio + inliers only")
        else:
            print("Containment columns present and non-zero — will use SIFT containment signal")
    else:
        print("NOTE: containment columns MISSING — using resolution_ratio + inliers only")

    # Load hashes (for split info)
    hash_info = load_hashes_csv(HASHES_CSV)
    print(f"Hash info loaded: {len(hash_info)} stems")

    # We'll cache dimensions to avoid re-reading the same image twice
    dim_cache = {}

    def cached_dims(filepath):
        key = str(filepath)
        if key not in dim_cache:
            dim_cache[key] = get_image_dimensions(filepath)
        return dim_cache[key]

    # Collect candidate pairs
    # Each entry: (crop_stem, parent_stem, evidence, inliers, cont_a_in_b, cont_b_in_a, area_ratio)
    candidate_pairs = []

    for row in sift_rows:
        path_a  = row["path_a"]
        path_b  = row["path_b"]
        split_a = row["split_a"]
        split_b = row["split_b"]
        stem_a  = row["stem_a"]
        stem_b  = row["stem_b"]

        # Parse inliers
        try:
            inliers = int(row.get("ransac_inliers", 0) or 0)
        except (ValueError, TypeError):
            inliers = 0

        # Parse containment
        try:
            cont_a_in_b = float(row.get("containment_a_in_b", 0) or 0)
        except (ValueError, TypeError):
            cont_a_in_b = 0.0
        try:
            cont_b_in_a = float(row.get("containment_b_in_a", 0) or 0)
        except (ValueError, TypeError):
            cont_b_in_a = 0.0

        evidence_signals = []

        # Signal A: SIFT containment
        if has_containment and inliers >= SIFT_INLIER_THRESHOLD:
            if cont_a_in_b >= CONTAINMENT_THRESHOLD or cont_b_in_a >= CONTAINMENT_THRESHOLD:
                evidence_signals.append("sift_containment")

        # Signal B: Resolution ratio
        if inliers >= RESOLUTION_INLIER_MIN:
            try:
                w_a, h_a = cached_dims(path_a)
                w_b, h_b = cached_dims(path_b)
                area_ratio, larger = compute_area_ratio(w_a, h_a, w_b, h_b)
                if area_ratio >= AREA_RATIO_MIN:
                    evidence_signals.append("resolution_ratio")
                else:
                    area_ratio = None
                    larger = None
            except Exception as e:
                print(f"ERROR reading dimensions for pair ({stem_a}, {stem_b}): {e}")
                raise
        else:
            try:
                w_a, h_a = cached_dims(path_a)
                w_b, h_b = cached_dims(path_b)
                area_ratio, larger = compute_area_ratio(w_a, h_a, w_b, h_b)
            except Exception as e:
                print(f"ERROR reading dimensions for pair ({stem_a}, {stem_b}): {e}")
                raise
            area_ratio = None
            larger = None

        if not evidence_signals:
            continue

        # Determine crop / parent from SIFT containment or area
        # If sift_containment: cont_a_in_b high -> a is crop of b; cont_b_in_a high -> b is crop of a
        # If resolution_ratio: smaller image is crop

        if "sift_containment" in evidence_signals and has_containment:
            if cont_a_in_b >= cont_b_in_a:
                crop_stem, crop_split, crop_path = stem_a, split_a, path_a
                parent_stem, parent_split, parent_path = stem_b, split_b, path_b
            else:
                crop_stem, crop_split, crop_path = stem_b, split_b, path_b
                parent_stem, parent_split, parent_path = stem_a, split_a, path_a
        elif larger is not None:
            # Use resolution
            if larger == "a":
                # a is larger => a is parent, b is crop
                crop_stem, crop_split = stem_b, split_b
                parent_stem, parent_split = stem_a, split_a
            elif larger == "b":
                crop_stem, crop_split = stem_a, split_a
                parent_stem, parent_split = stem_b, split_b
            else:
                # equal area — skip
                continue
        else:
            continue

        # Determine evidence label
        if "sift_containment" in evidence_signals and "resolution_ratio" in evidence_signals:
            evidence = "both"
        elif "sift_containment" in evidence_signals:
            evidence = "sift_containment"
        else:
            evidence = "resolution_ratio"

        candidate_pairs.append({
            "crop_stem": crop_stem,
            "crop_split": crop_split,
            "crop_path": path_a if crop_stem == stem_a else path_b,
            "parent_stem": parent_stem,
            "parent_split": parent_split,
            "parent_path": path_b if parent_stem == stem_b else path_a,
            "evidence": evidence,
            "sift_inliers": inliers,
            "containment_a_in_b": cont_a_in_b,
            "containment_b_in_a": cont_b_in_a,
            "area_ratio": area_ratio if area_ratio is not None else "",
        })

    print(f"\nRaw candidate crop-parent pairs: {len(candidate_pairs)}")

    # Build crop_to_parent: keep best parent per crop (highest inliers, break ties by area_ratio)
    crop_to_best = {}
    for pair in candidate_pairs:
        cs = pair["crop_stem"]
        inliers = pair["sift_inliers"]
        ar = float(pair["area_ratio"]) if pair["area_ratio"] != "" else 0.0
        if cs not in crop_to_best:
            crop_to_best[cs] = pair
        else:
            existing = crop_to_best[cs]
            existing_inliers = existing["sift_inliers"]
            existing_ar = float(existing["area_ratio"]) if existing["area_ratio"] != "" else 0.0
            if inliers > existing_inliers or (inliers == existing_inliers and ar > existing_ar):
                crop_to_best[cs] = pair

    final_pairs = list(crop_to_best.values())

    # Save crop_parent_map.csv
    out_csv = OUTPUT_DIR / "crop_parent_map.csv"
    fieldnames = [
        "crop_path", "crop_split", "crop_stem",
        "parent_path", "parent_split", "parent_stem",
        "evidence", "sift_inliers", "containment_a_in_b", "containment_b_in_a", "area_ratio"
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for pair in final_pairs:
            writer.writerow({k: pair[k] for k in fieldnames})

    # ---- SUMMARY ----
    print(f"\n=== SUMMARY ===")
    print(f"Total crop-parent pairs (after dedup): {len(final_pairs)}")
    unique_crops   = set(p["crop_stem"] for p in final_pairs)
    unique_parents = set(p["parent_stem"] for p in final_pairs)
    print(f"Unique crops identified:   {len(unique_crops)}")
    print(f"Unique parents identified: {len(unique_parents)}")

    # Evidence breakdown
    ev_counts = defaultdict(int)
    for p in final_pairs:
        ev_counts[p["evidence"]] += 1
    print(f"\nEvidence type breakdown:")
    for ev, cnt in sorted(ev_counts.items()):
        print(f"  {ev}: {cnt}")

    # Prefix breakdown
    prefix_counts = defaultdict(int)
    for p in final_pairs:
        stem = p["crop_stem"]
        prefix = stem.split("_")[0] if "_" in stem else stem
        prefix_counts[prefix] += 1
    print(f"\nCrop prefix breakdown:")
    for prefix in sorted(prefix_counts.keys()):
        print(f"  {prefix}: {prefix_counts[prefix]}")

    # Cross-split pairs
    cross_split = sum(1 for p in final_pairs if p["crop_split"] != p["parent_split"])
    print(f"\nCross-split pairs (crop in different split from parent): {cross_split}")

    if not has_containment:
        print("\nNOTE: containment columns were missing or all-zero; only resolution_ratio + inlier signal was used.")

    print(f"\nOutput: {out_csv}")


if __name__ == "__main__":
    main()
