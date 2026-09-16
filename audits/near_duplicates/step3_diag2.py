"""
Quick diagnostic: what do COCO_RECORTE images match against?
Test with relaxed thresholds to understand the data.
"""
import os, csv, cv2, numpy as np

DATASET_ROOT = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean"
AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
INVENTORY_CSV = os.path.join(AUDIT_DIR, "inventory.csv")

def get_image_path(stem, split):
    for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        p = os.path.join(DATASET_ROOT, "images", split, stem + ext)
        if os.path.exists(p):
            return p
    return None

with open(INVENTORY_CSV, newline='', encoding='utf-8') as f:
    inv = {r['stem']: r for r in csv.DictReader(f)}

# Get all COCO_RECORTE crops
coco_crops = [(s, info['split']) for s, info in inv.items() if info['prefix'] == 'COCO_RECORTE']
# Get all COCO non-crop images
coco_parents = [(s, info['split']) for s, info in inv.items()
                if info['prefix'].upper().startswith('COCO') and 'RECORTE' not in info['prefix'].upper()]

print(f"COCO crops: {len(coco_crops)}")
print(f"COCO parent candidates: {len(coco_parents)}")
print(f"Parent prefixes: {sorted(set(inv[s]['prefix'] for s, _ in coco_parents))[:10]}")

# Test first 5 crops against first 20 parents with relaxed thresholds
sift = cv2.SIFT_create()

def get_features(stem, split):
    path = get_image_path(stem, split)
    if not path:
        return None, None, None
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return None, None, None
    h, w = img.shape[:2]
    scale = 1024 / max(h, w) if max(h, w) > 1024 else 1.0
    if scale < 1.0:
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp, des = sift.detectAndCompute(gray, None)
    return img.shape[:2], kp, des

print("\n=== Testing COCO_RECORTE crops vs COCO parents ===")
for crop_stem, crop_split in coco_crops[:5]:
    crop_shape, crop_kp, crop_des = get_features(crop_stem, crop_split)
    if crop_des is None:
        print(f"  {crop_stem}: no features")
        continue

    best_inliers = 0
    best_parent = None
    best_cont = 0.0
    best_matches = 0

    # Test all COCO parents
    for parent_stem, parent_split in coco_parents:
        parent_shape, parent_kp, parent_des = get_features(parent_stem, parent_split)
        if parent_des is None or len(parent_kp) < 4:
            continue

        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        raw = bf.knnMatch(crop_des, parent_des, k=2)
        good = [m for m_pair in raw if len(m_pair) == 2
                for m, n in [m_pair] if m.distance < 0.75 * n.distance]

        if len(good) < 4:
            continue

        src = np.float32([crop_kp[m.queryIdx].pt for m in good]).reshape(-1,1,2)
        dst = np.float32([parent_kp[m.trainIdx].pt for m in good]).reshape(-1,1,2)
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)

        if H is None or mask is None:
            continue

        inliers = int(mask.sum())
        if inliers > best_inliers:
            ch, cw = crop_shape
            ph, pw = parent_shape
            corners = np.float32([[0,0],[cw,0],[cw,ch],[0,ch]]).reshape(-1,1,2)
            proj = cv2.perspectiveTransform(corners, H).reshape(-1,2)

            px_min = np.clip(proj[:,0].min(), 0, pw)
            px_max = np.clip(proj[:,0].max(), 0, pw)
            py_min = np.clip(proj[:,1].min(), 0, ph)
            py_max = np.clip(proj[:,1].max(), 0, ph)

            isect = max(0, px_max-px_min) * max(0, py_max-py_min)
            cont = isect / (ph*pw) if ph*pw > 0 else 0

            best_inliers = inliers
            best_parent = (parent_stem, parent_split)
            best_cont = cont
            best_matches = len(good)

    if best_parent:
        print(f"  {crop_stem}: best parent={best_parent[0]} inliers={best_inliers} matches={best_matches} containment={best_cont:.4f}")
    else:
        print(f"  {crop_stem}: no valid parent found (all < 4 good matches)")

# Also test: are COCO_RECORTE images actual sub-crops of COCO images?
# Check dimensions
print("\n=== Size comparison ===")
for crop_stem, crop_split in coco_crops[:5]:
    path = get_image_path(crop_stem, crop_split)
    img = cv2.imread(path)
    h, w = img.shape[:2]
    print(f"  Crop {crop_stem}: {w}x{h} = {w*h} px")
for parent_stem, parent_split in coco_parents[:5]:
    path = get_image_path(parent_stem, parent_split)
    img = cv2.imread(path)
    h, w = img.shape[:2]
    print(f"  Parent {parent_stem}: {w}x{h} = {w*h} px")

# Check if crop is significantly smaller than parent
crop_areas = []
for crop_stem, crop_split in coco_crops:
    path = get_image_path(crop_stem, crop_split)
    if path:
        img = cv2.imread(path)
        if img is not None:
            crop_areas.append(img.shape[0] * img.shape[1])
parent_areas = []
for parent_stem, parent_split in coco_parents:
    path = get_image_path(parent_stem, parent_split)
    if path:
        img = cv2.imread(path)
        if img is not None:
            parent_areas.append(img.shape[0] * img.shape[1])

import statistics
if crop_areas:
    print(f"\nCOCO_RECORTE areas: min={min(crop_areas)}, median={statistics.median(crop_areas):.0f}, max={max(crop_areas)}")
if parent_areas:
    print(f"COCO parent areas: min={min(parent_areas)}, median={statistics.median(parent_areas):.0f}, max={max(parent_areas)}")
