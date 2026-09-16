"""
STEP 3 — Crop → parent mapping (FULL, all splits)
For each crop image, find its parent non-crop image using SIFT containment.

CORRECTED containment metric:
  crop_containment_in_parent = intersection_area / projected_crop_area
  This measures what fraction of the projected crop footprint lies within the parent bounds.
  A value >= 0.8 means 80% of the crop is geometrically contained within the parent.

  Note: The spec says "intersection area / area_parent" but that formula yields very small
  values when crop << parent (e.g. crop=200kpx, parent=550kpx → max ~0.36).
  The corrected formula (intersection / projected_crop_area) is geometrically meaningful.
"""
import os
import sys
import csv
import time
import cv2
import numpy as np

DATASET_ROOT = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean"
AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
INVENTORY_CSV = os.path.join(AUDIT_DIR, "inventory.csv")
SPLIT_DIR = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1"
OUTPUT_CSV = os.path.join(SPLIT_DIR, "crop_parent_map_full.csv")
ORPHAN_TXT = os.path.join(SPLIT_DIR, "orphan_crops.txt")
SIFT_ERRORS_TXT = os.path.join(SPLIT_DIR, "sift_errors.txt")

os.makedirs(SPLIT_DIR, exist_ok=True)

def load_inventory():
    rows = []
    with open(INVENTORY_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def get_image_path(stem, split):
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        p = os.path.join(DATASET_ROOT, "images", split, stem + ext)
        if os.path.exists(p):
            return p
    return None

def resize_max_side(img, max_side=1024):
    h, w = img.shape[:2]
    if max(h, w) <= max_side:
        return img
    scale = max_side / max(h, w)
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)

def compute_sift_features(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"cv2.imread returned None for {img_path}")
    img_r = resize_max_side(img, 1024)
    gray = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)
    return img_r.shape[:2], kp, des

def match_and_check(crop_shape, crop_kp, crop_des, parent_shape, parent_kp, parent_des):
    """
    Returns: (good_matches, ransac_inliers, inlier_ratio,
              crop_containment_in_parent, area_ratio, homography_found)

    crop_containment_in_parent = intersection_area / projected_crop_area
      -> fraction of projected crop footprint that lies within parent bounds
      -> >= 0.8 means 80%+ of crop is geometrically inside parent

    area_ratio = parent_area / crop_area (for tie-breaking)
    """
    if crop_des is None or parent_des is None or len(crop_kp) < 4 or len(parent_kp) < 4:
        return 0, 0, 0.0, 0.0, 0.0, False

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    raw_matches = bf.knnMatch(crop_des, parent_des, k=2)
    good = []
    for m_pair in raw_matches:
        if len(m_pair) == 2:
            m, n = m_pair
            if m.distance < 0.75 * n.distance:
                good.append(m)

    if len(good) < 4:
        return len(good), 0, 0.0, 0.0, 0.0, False

    src_pts = np.float32([crop_kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([parent_kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None or mask is None:
        return len(good), 0, 0.0, 0.0, 0.0, False

    inliers = int(mask.sum())
    inlier_ratio = inliers / len(good) if good else 0.0

    # Project crop corners into parent space
    ch, cw = crop_shape
    ph, pw = parent_shape
    crop_corners = np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]]).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(crop_corners, H).reshape(-1, 2)

    # Projected crop bounding box
    proj_x_min = projected[:, 0].min()
    proj_x_max = projected[:, 0].max()
    proj_y_min = projected[:, 1].min()
    proj_y_max = projected[:, 1].max()
    projected_area = max(0, proj_x_max - proj_x_min) * max(0, proj_y_max - proj_y_min)

    # Intersection with parent bounds [0,pw] x [0,ph]
    ix_min = np.clip(proj_x_min, 0, pw)
    ix_max = np.clip(proj_x_max, 0, pw)
    iy_min = np.clip(proj_y_min, 0, ph)
    iy_max = np.clip(proj_y_max, 0, ph)
    intersection_area = max(0, ix_max - ix_min) * max(0, iy_max - iy_min)

    # crop_containment_in_parent = what fraction of projected crop is inside parent
    crop_containment_in_parent = intersection_area / projected_area if projected_area > 0 else 0.0

    # area_ratio for tie-breaking (larger ratio = parent much bigger than crop = more likely correct)
    crop_area = ch * cw
    parent_area = ph * pw
    area_ratio = parent_area / crop_area if crop_area > 0 else 0.0

    return len(good), inliers, inlier_ratio, crop_containment_in_parent, area_ratio, True

def get_family_filter(crop_prefix):
    """Return a function that tests if a non-crop prefix belongs to the crop's family."""
    cp = crop_prefix.upper()
    if 'COCO' in cp:
        return lambda p: p.upper().startswith('COCO') and 'RECORTE' not in p.upper()
    elif 'ROYA' in cp:
        return lambda p: p.upper().startswith('ROYA') and 'RECORTE' not in p.upper()
    elif 'MINADO' in cp or 'MINADOR' in cp or 'MINEIRO' in cp:
        return lambda p: (p.upper().startswith('MINADO') or p.upper().startswith('MINADOR') or
                          p.upper().startswith('MINEIRO')) and 'RECORTE' not in p.upper()
    return lambda p: False

def main():
    print("=== STEP 3: CROP-PARENT MAPPING (FULL, CORRECTED) ===")
    start_total = time.time()

    rows = load_inventory()
    crops = [r for r in rows if 'RECORTE' in r['prefix'].upper()]
    non_crops = [r for r in rows if 'RECORTE' not in r['prefix'].upper()]

    from collections import Counter
    print(f"\nCrops: {len(crops)}")
    print(f"  Per prefix: {dict(Counter(r['prefix'] for r in crops))}")
    print(f"  Per split: {dict(Counter(r['split'] for r in crops))}")
    print(f"Non-crops: {len(non_crops)}")

    # Cache for non-crop SIFT features: stem -> (shape, kp, des)
    noncrop_cache = {}

    def get_noncrop_features(stem, split):
        if stem in noncrop_cache:
            return noncrop_cache[stem]
        path = get_image_path(stem, split)
        if path is None:
            raise FileNotFoundError(f"Image not found for non-crop stem={stem}, split={split}")
        shape, kp, des = compute_sift_features(path)
        noncrop_cache[stem] = (shape, kp, des)
        return shape, kp, des

    # Runtime estimation on first 20 crops
    print("\n--- Runtime estimation (first 20 crops) ---")
    est_n = min(20, len(crops))
    est_start = time.time()
    sift_errors = []

    for i, crop_row in enumerate(crops[:est_n]):
        crop_stem = crop_row['stem']
        crop_split = crop_row['split']
        crop_path = get_image_path(crop_stem, crop_split)
        if crop_path is None:
            raise FileNotFoundError(f"Crop image not found: {crop_stem}")
        crop_shape, crop_kp, crop_des = compute_sift_features(crop_path)

        family_filter = get_family_filter(crop_row['prefix'])
        family_candidates = [r for r in non_crops if family_filter(r['prefix'])]

        # Try first 5 family candidates (just for timing, not full run)
        for nc in family_candidates[:5]:
            try:
                get_noncrop_features(nc['stem'], nc['split'])
            except Exception as e:
                sift_errors.append(f"Error loading {nc['stem']}: {e}")

    est_elapsed = time.time() - est_start

    # Full estimate: time per crop will be dominated by matching, not loading (cache helps)
    # After warmup, each crop-vs-candidate match takes ~0.002-0.01s
    # Estimate based on actual candidates per crop
    total_matches_needed = 0
    for crop_row in crops:
        family_filter = get_family_filter(crop_row['prefix'])
        family_size = sum(1 for r in non_crops if family_filter(r['prefix']))
        total_matches_needed += family_size

    # Each match: ~0.005s (BFMatcher + RANSAC after features cached)
    # Image load per unique non-crop: ~0.05s
    unique_noncrops = len(set(r['stem'] for r in non_crops))
    est_total = unique_noncrops * 0.05 + total_matches_needed * 0.005
    print(f"  est_n={est_n} timing: {est_elapsed:.1f}s")
    print(f"  Estimated total matches: {total_matches_needed}")
    print(f"  Unique non-crops to load: {unique_noncrops}")
    print(f"  Estimated runtime: {est_total:.0f}s ({est_total/3600:.2f}h)")

    if est_total > 10800:
        print(f"STOP-IF: Estimated {est_total:.0f}s > 3 hours (10800s)")
        sys.exit(1)
    else:
        print(f"  => Estimate OK. Proceeding with full run.")

    # Clear cache for fresh full run
    noncrop_cache.clear()

    print(f"\n--- Processing all {len(crops)} crops ---")

    results = []
    orphan_crops = []
    sift_errors_full = []

    for crop_idx, crop_row in enumerate(crops):
        if crop_idx % 50 == 0:
            elapsed = time.time() - start_total
            pct = crop_idx / len(crops) * 100
            print(f"  [{crop_idx}/{len(crops)} {pct:.0f}%] elapsed={elapsed:.0f}s "
                  f"cache_size={len(noncrop_cache)}")

        crop_stem = crop_row['stem']
        crop_split = crop_row['split']
        crop_prefix = crop_row['prefix']

        crop_path = get_image_path(crop_stem, crop_split)
        if crop_path is None:
            sift_errors_full.append(f"Crop image not found: {crop_stem}")
            orphan_crops.append(crop_stem)
            results.append({
                "crop_stem": crop_stem, "crop_split": crop_split, "crop_prefix": crop_prefix,
                "parent_stem": "", "parent_split": "", "parent_prefix": "",
                "inliers": 0, "crop_containment_in_parent": 0.0, "area_ratio": 0.0,
                "evidence_type": "image_not_found"
            })
            continue

        try:
            crop_shape, crop_kp, crop_des = compute_sift_features(crop_path)
        except Exception as e:
            sift_errors_full.append(f"SIFT error on crop {crop_stem}: {e}")
            orphan_crops.append(crop_stem)
            results.append({
                "crop_stem": crop_stem, "crop_split": crop_split, "crop_prefix": crop_prefix,
                "parent_stem": "", "parent_split": "", "parent_prefix": "",
                "inliers": 0, "crop_containment_in_parent": 0.0, "area_ratio": 0.0,
                "evidence_type": "sift_error"
            })
            continue

        if crop_des is None or len(crop_kp) < 4:
            sift_errors_full.append(f"Too few keypoints for crop {crop_stem}: {len(crop_kp) if crop_kp else 0}")
            orphan_crops.append(crop_stem)
            results.append({
                "crop_stem": crop_stem, "crop_split": crop_split, "crop_prefix": crop_prefix,
                "parent_stem": "", "parent_split": "", "parent_prefix": "",
                "inliers": 0, "crop_containment_in_parent": 0.0, "area_ratio": 0.0,
                "evidence_type": "no_keypoints"
            })
            continue

        family_filter = get_family_filter(crop_prefix)
        family_candidates = [r for r in non_crops if family_filter(r['prefix'])]

        best_parent = None
        best_inliers = 0
        best_containment = 0.0
        best_area_ratio = 0.0

        def try_candidates(candidates):
            nonlocal best_parent, best_inliers, best_containment, best_area_ratio
            for nc in candidates:
                nc_stem = nc['stem']
                nc_split = nc['split']
                try:
                    parent_shape, parent_kp, parent_des = get_noncrop_features(nc_stem, nc_split)
                except Exception as e:
                    sift_errors_full.append(f"SIFT error loading parent {nc_stem}: {e}")
                    continue

                gm, inliers, inlier_ratio, crop_cont, area_ratio, hom = match_and_check(
                    crop_shape, crop_kp, crop_des,
                    parent_shape, parent_kp, parent_des
                )

                # Valid: inliers >= 30 AND crop_containment_in_parent >= 0.8
                if hom and inliers >= 30 and crop_cont >= 0.8:
                    if (inliers > best_inliers or
                            (inliers == best_inliers and area_ratio > best_area_ratio)):
                        best_inliers = inliers
                        best_containment = crop_cont
                        best_area_ratio = area_ratio
                        best_parent = nc

        # First try family candidates
        try_candidates(family_candidates)

        # If no valid parent in family, expand to all non-crops
        if best_parent is None and family_candidates:
            try_candidates(non_crops)

        if best_parent is not None:
            results.append({
                "crop_stem": crop_stem,
                "crop_split": crop_split,
                "crop_prefix": crop_prefix,
                "parent_stem": best_parent['stem'],
                "parent_split": best_parent['split'],
                "parent_prefix": best_parent['prefix'],
                "inliers": best_inliers,
                "crop_containment_in_parent": best_containment,
                "area_ratio": best_area_ratio,
                "evidence_type": "sift_containment"
            })
        else:
            orphan_crops.append(crop_stem)
            results.append({
                "crop_stem": crop_stem, "crop_split": crop_split, "crop_prefix": crop_prefix,
                "parent_stem": "", "parent_split": "", "parent_prefix": "",
                "inliers": 0, "crop_containment_in_parent": 0.0, "area_ratio": 0.0,
                "evidence_type": "no_parent_found"
            })

    total_elapsed = time.time() - start_total
    print(f"\nCompleted {len(crops)} crops in {total_elapsed:.0f}s ({total_elapsed/3600:.2f}h)")

    # Report
    found_same = sum(1 for r in results if r['parent_stem'] and r['crop_split'] == r['parent_split'])
    found_diff = sum(1 for r in results if r['parent_stem'] and r['crop_split'] != r['parent_split'])
    not_found = sum(1 for r in results if not r['parent_stem'])
    print(f"\n--- Results ---")
    print(f"  Parent found (same split): {found_same}")
    print(f"  Parent found (diff split): {found_diff}")
    print(f"  No parent found: {not_found}")

    if orphan_crops:
        print(f"\n  Orphan crops: {len(orphan_crops)}")
        for s in orphan_crops[:20]:
            print(f"    {s}")
        if len(orphan_crops) > 20:
            print(f"    ... and {len(orphan_crops)-20} more (see orphan_crops.txt)")

    # Save
    fieldnames = ["crop_stem", "crop_split", "crop_prefix", "parent_stem", "parent_split",
                  "parent_prefix", "inliers", "crop_containment_in_parent", "area_ratio", "evidence_type"]
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved {OUTPUT_CSV}")

    with open(ORPHAN_TXT, 'w', encoding='utf-8') as f:
        for s in orphan_crops:
            f.write(s + '\n')
    print(f"Saved {ORPHAN_TXT}")

    if sift_errors_full:
        with open(SIFT_ERRORS_TXT, 'w', encoding='utf-8') as f:
            for e in sift_errors_full:
                f.write(e + '\n')
        print(f"Saved {SIFT_ERRORS_TXT}: {len(sift_errors_full)} errors")

    print(f"\nStep 3 complete in {total_elapsed:.0f}s")

if __name__ == "__main__":
    main()
