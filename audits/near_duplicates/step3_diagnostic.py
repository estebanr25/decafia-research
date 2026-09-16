"""
Diagnostic: Check SIFT matching quality for a few crop-parent pairs.
Test with the existing sift_results.csv which has known crop-parent pairs.
"""
import os
import csv
import cv2
import numpy as np

DATASET_ROOT = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean"
AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
INVENTORY_CSV = os.path.join(AUDIT_DIR, "inventory.csv")
OLD_CROP_PARENT = os.path.join(AUDIT_DIR, "crop_parent_map.csv")

def get_image_path(stem, split):
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        p = os.path.join(DATASET_ROOT, "images", split, stem + ext)
        if os.path.exists(p):
            return p
    return None

def load_inventory():
    with open(INVENTORY_CSV, newline='', encoding='utf-8') as f:
        return {r['stem']: r for r in csv.DictReader(f)}

def resize_max_side(img, max_side=1024):
    h, w = img.shape[:2]
    if max(h, w) <= max_side:
        return img
    scale = max_side / max(h, w)
    return cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)

def test_pair(crop_stem, crop_split, parent_stem, parent_split):
    crop_path = get_image_path(crop_stem, crop_split)
    parent_path = get_image_path(parent_stem, parent_split)
    if not crop_path or not parent_path:
        print(f"  Image not found: crop={crop_path}, parent={parent_path}")
        return

    crop_img = cv2.imread(crop_path, cv2.IMREAD_COLOR)
    parent_img = cv2.imread(parent_path, cv2.IMREAD_COLOR)
    if crop_img is None or parent_img is None:
        print(f"  Failed to load images")
        return

    crop_r = resize_max_side(crop_img, 1024)
    parent_r = resize_max_side(parent_img, 1024)

    ch, cw = crop_r.shape[:2]
    ph, pw = parent_r.shape[:2]
    print(f"  Crop size (resized): {cw}x{ch}, Parent size: {pw}x{ph}")
    print(f"  Crop orig: {crop_img.shape[1]}x{crop_img.shape[0]}, Parent orig: {parent_img.shape[1]}x{parent_img.shape[0]}")

    sift = cv2.SIFT_create()
    crop_gray = cv2.cvtColor(crop_r, cv2.COLOR_BGR2GRAY)
    parent_gray = cv2.cvtColor(parent_r, cv2.COLOR_BGR2GRAY)

    kp_c, des_c = sift.detectAndCompute(crop_gray, None)
    kp_p, des_p = sift.detectAndCompute(parent_gray, None)
    print(f"  SIFT keypoints: crop={len(kp_c)}, parent={len(kp_p)}")

    if des_c is None or des_p is None or len(kp_c) < 4 or len(kp_p) < 4:
        print(f"  Too few keypoints, skipping matching")
        return

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    raw_matches = bf.knnMatch(des_c, des_p, k=2)
    good = []
    for m_pair in raw_matches:
        if len(m_pair) == 2:
            m, n = m_pair
            if m.distance < 0.75 * n.distance:
                good.append(m)
    print(f"  Good matches (Lowe 0.75): {len(good)}")

    if len(good) < 4:
        print(f"  Too few good matches for homography")
        return

    src_pts = np.float32([kp_c[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_p[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if H is None:
        print(f"  Homography failed")
        return

    inliers = int(mask.sum())
    print(f"  RANSAC inliers: {inliers}")

    # Project crop corners
    crop_corners = np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]]).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(crop_corners, H).reshape(-1, 2)
    print(f"  Projected crop corners in parent: {projected.tolist()}")

    # Bounding box clipped to parent
    px_min = np.clip(projected[:, 0].min(), 0, pw)
    px_max = np.clip(projected[:, 0].max(), 0, pw)
    py_min = np.clip(projected[:, 1].min(), 0, ph)
    py_max = np.clip(projected[:, 1].max(), 0, ph)

    intersection_area = max(0, px_max - px_min) * max(0, py_max - py_min)
    parent_area = ph * pw
    crop_area = ch * cw

    projected_area = (projected[:, 0].max() - projected[:, 0].min()) * (projected[:, 1].max() - projected[:, 1].min())
    containment_in_parent = intersection_area / parent_area if parent_area > 0 else 0
    containment_proj_vs_parent = projected_area / parent_area if parent_area > 0 else 0

    print(f"  intersection_area={intersection_area:.0f}, parent_area={parent_area:.0f}")
    print(f"  crop_containment_in_parent (intersection/parent): {containment_in_parent:.4f}")
    print(f"  projected_area/parent_area: {containment_proj_vs_parent:.4f}")
    print(f"  => VALID parent? inliers>={30}: {inliers>=30}, containment>=0.8: {containment_in_parent>=0.8}")

# Load inventory
inv = load_inventory()

# Check the old crop_parent_map.csv for known cross-split pairs
print("=== Loading old crop_parent_map.csv ===")
with open(OLD_CROP_PARENT, newline='', encoding='utf-8') as f:
    old_rows = list(csv.DictReader(f))
print(f"Old crop_parent_map.csv columns: {csv.DictReader(open(OLD_CROP_PARENT)).fieldnames}")
print(f"Rows: {len(old_rows)}")
print("First 3:")
for r in old_rows[:3]:
    print(f"  {r}")

# Find crops with identified parents
found_rows = [r for r in old_rows if r.get('parent_stem', r.get('parent', '')) != '']
print(f"\nRows with parent found: {len(found_rows)}")

print("\n=== Testing a few known crop-parent pairs ===")

# Test the first few crops vs COCO parent images directly
# First find all COCO_RECORTE crops
crops_by_prefix = {}
for stem, info in inv.items():
    if 'RECORTE' in info['prefix'].upper():
        crops_by_prefix.setdefault(info['prefix'], []).append(stem)

print(f"\nCrop prefixes: {list(crops_by_prefix.keys())}")
for prefix, stems in list(crops_by_prefix.items())[:1]:
    print(f"\nTesting crop: {stems[0]} (prefix={prefix})")
    crop_info = inv[stems[0]]
    crop_stem = stems[0]
    crop_split = crop_info['split']

    # Find potential COCO parents (non-crop with prefix starting with COCO)
    coco_parents = [(s, info['split']) for s, info in inv.items()
                    if info['prefix'].upper().startswith('COCO') and 'RECORTE' not in info['prefix'].upper()]
    print(f"  Testing against {len(coco_parents)} COCO parent candidates")
    # Test just first 3
    for parent_stem, parent_split in coco_parents[:3]:
        print(f"\n  Testing {crop_stem} vs {parent_stem}")
        test_pair(crop_stem, crop_split, parent_stem, parent_split)

# Also test some crops that the old script found as matches
print("\n=== Testing pairs from old crop_parent_map ===")
for r in found_rows[:5]:
    crop_col = 'crop_stem' if 'crop_stem' in r else list(r.keys())[0]
    parent_col = 'parent_stem' if 'parent_stem' in r else 'parent'
    crop_split_col = 'crop_split' if 'crop_split' in r else None
    parent_split_col = 'parent_split' if 'parent_split' in r else None
    crop_stem = r[crop_col]
    parent_stem = r[parent_col]
    crop_split_v = r.get(crop_split_col, inv.get(crop_stem, {}).get('split', 'train')) if crop_split_col else 'train'
    parent_split_v = r.get(parent_split_col, inv.get(parent_stem, {}).get('split', 'train')) if parent_split_col else 'train'
    print(f"\n  Testing: crop={crop_stem} (split={crop_split_v}) vs parent={parent_stem} (split={parent_split_v})")
    test_pair(crop_stem, crop_split_v, parent_stem, parent_split_v)
