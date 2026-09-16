import pathlib
import csv
import sys
import cv2
import numpy as np

print("=" * 60)
print("STEP A3 — SIFT Geometric Verification")
print("=" * 60)

output_dir = pathlib.Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")
hash_cands_path = output_dir / "near_dup_candidates_hashes.csv"
top5_path = output_dir / "top5_cross_split.csv"
sift_issues_path = output_dir / "sift_issues.txt"

# 1. Load candidates from hash step
print("\n[1] Loading hash candidates (min_phash_dist<=12 OR dhash_dist<=12)...")
hash_pairs = set()
hash_data = {}
with open(hash_cands_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = tuple(sorted([row["path_a"], row["path_b"]]))
        if key not in hash_pairs:
            hash_pairs.add(key)
            hash_data[key] = {
                "path_a": row["path_a"], "split_a": row["split_a"], "stem_a": row["stem_a"],
                "path_b": row["path_b"], "split_b": row["split_b"], "stem_b": row["stem_b"],
                "min_phash_dist": int(row["min_phash_dist"]),
                "dhash_dist": int(row["dhash_dist"])
            }

print(f"  Hash candidates: {len(hash_pairs)} unique pairs")

# Load top-5 from embedding step (cosine_sim >= 0.85)
print("\n[1b] Loading top5 embedding candidates (cosine_sim>=0.85)...")
emb_pairs = set()
emb_data = {}
with open(top5_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sim = float(row["cosine_sim"])
        if sim >= 0.85:
            key = tuple(sorted([row["query_path"], row["candidate_path"]]))
            if key not in emb_pairs:
                emb_pairs.add(key)
                emb_data[key] = {
                    "path_a": min(row["query_path"], row["candidate_path"]),
                    "path_b": max(row["query_path"], row["candidate_path"]),
                    "cosine_sim": sim
                }

print(f"  Embedding candidates (>=0.85): {len(emb_pairs)} unique pairs")

# Union of unique pairs
all_pair_keys = hash_pairs | emb_pairs
print(f"  Union of unique pairs: {len(all_pair_keys)}")

# Build combined pair info
pairs_to_check = []
for key in all_pair_keys:
    # Get paths — key is always sorted
    pa, pb = key
    # Determine splits from hash_data or emb_data
    if key in hash_data:
        info = hash_data[key]
        split_a = info["split_a"]
        split_b = info["split_b"]
        stem_a = info["stem_a"]
        stem_b = info["stem_b"]
        min_phash_dist = info["min_phash_dist"]
        dhash_dist = info["dhash_dist"]
    else:
        # Must infer split from path
        def split_from_path(p):
            for s in ["train", "val", "test"]:
                if f"images\\{s}\\" in p or f"images/{s}/" in p:
                    return s
            return "unknown"
        split_a = split_from_path(pa)
        split_b = split_from_path(pb)
        stem_a = pathlib.Path(pa).stem
        stem_b = pathlib.Path(pb).stem
        min_phash_dist = -1
        dhash_dist = -1

    cosine_sim = emb_data[key]["cosine_sim"] if key in emb_data else -1.0

    pairs_to_check.append({
        "path_a": pa, "split_a": split_a, "stem_a": stem_a,
        "path_b": pb, "split_b": split_b, "stem_b": stem_b,
        "min_phash_dist": min_phash_dist,
        "dhash_dist": dhash_dist,
        "cosine_sim": cosine_sim
    })

print(f"\n[2] Running SIFT on {len(pairs_to_check)} pairs...")

sift = cv2.SIFT_create()
issues = []

def load_and_resize(path, max_side=1024):
    img = cv2.imread(path)
    if img is None:
        raise RuntimeError(f"cv2.imread returned None for: {path}")
    h, w = img.shape[:2]
    scale = min(max_side / max(h, w), 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img

def poly_intersection_area(corners_a, corners_b):
    """Compute intersection area of two convex quadrilaterals using Sutherland-Hodgman."""
    def clip_polygon_by_edge(polygon, edge_start, edge_end):
        """Clip polygon by half-plane defined by directed edge."""
        if len(polygon) == 0:
            return []
        output = []
        def inside(p):
            # Point is inside (left of) directed edge
            return (edge_end[0] - edge_start[0]) * (p[1] - edge_start[1]) - \
                   (edge_end[1] - edge_start[1]) * (p[0] - edge_start[0]) >= 0
        def intersect(p1, p2):
            # Intersection of line segment p1-p2 with edge
            d1 = (edge_end[0] - edge_start[0]) * (p1[1] - edge_start[1]) - \
                 (edge_end[1] - edge_start[1]) * (p1[0] - edge_start[0])
            d2 = (edge_end[0] - edge_start[0]) * (p2[1] - edge_start[1]) - \
                 (edge_end[1] - edge_start[1]) * (p2[0] - edge_start[0])
            if abs(d1 - d2) < 1e-10:
                return p1
            t = d1 / (d1 - d2)
            return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
        n = len(polygon)
        for i in range(n):
            curr = polygon[i]
            prev = polygon[(i - 1) % n]
            if inside(curr):
                if not inside(prev):
                    output.append(intersect(prev, curr))
                output.append(curr)
            elif inside(prev):
                output.append(intersect(prev, curr))
        return output

    # Convert to list of tuples
    poly_a = [tuple(c) for c in corners_a]
    poly_b = [tuple(c) for c in corners_b]

    # Clip poly_a against each edge of poly_b (Sutherland-Hodgman)
    output = poly_a
    n_b = len(poly_b)
    for i in range(n_b):
        if not output:
            return 0.0
        output = clip_polygon_by_edge(output, poly_b[i], poly_b[(i + 1) % n_b])

    if len(output) < 3:
        return 0.0

    # Shoelace formula for area
    n = len(output)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += output[i][0] * output[j][1]
        area -= output[j][0] * output[i][1]
    return abs(area) / 2.0

results = []
for i, pair in enumerate(pairs_to_check):
    if (i + 1) % 200 == 0:
        print(f"  Processed {i + 1}/{len(pairs_to_check)}...")

    try:
        img_a = load_and_resize(pair["path_a"])
        img_b = load_and_resize(pair["path_b"])
    except RuntimeError as e:
        msg = f"LOAD_FAIL|{pair['path_a']}|{pair['path_b']}|{str(e)}"
        issues.append(msg)
        results.append({**pair, "good_matches": 0, "ransac_inliers": 0,
                        "inlier_ratio": 0.0, "containment_a_in_b": 0.0, "containment_b_in_a": 0.0,
                        "homography_found": False})
        continue

    gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)

    kp_a, desc_a = sift.detectAndCompute(gray_a, None)
    kp_b, desc_b = sift.detectAndCompute(gray_b, None)

    if desc_a is None or desc_b is None or len(kp_a) == 0 or len(kp_b) == 0:
        msg = f"NO_DESC|{pair['path_a']}|{pair['path_b']}|kp_a={len(kp_a) if kp_a else 0},kp_b={len(kp_b) if kp_b else 0}"
        issues.append(msg)
        results.append({**pair, "good_matches": 0, "ransac_inliers": 0,
                        "inlier_ratio": 0.0, "containment_a_in_b": 0.0, "containment_b_in_a": 0.0,
                        "homography_found": False})
        continue

    # BFMatcher with crossCheck=False, ratio test (Lowe's ratio = 0.75)
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    raw_matches = bf.knnMatch(desc_a, desc_b, k=2)

    good = []
    for m_pair in raw_matches:
        if len(m_pair) == 2:
            m, n = m_pair
            if m.distance < 0.75 * n.distance:
                good.append(m)

    good_matches = len(good)

    # RANSAC homography — need at least 4 matches
    ransac_inliers = 0
    inlier_ratio = 0.0
    containment_a_in_b = 0.0
    containment_b_in_a = 0.0
    homography_found = False

    if good_matches >= 4:
        src_pts = np.float32([kp_a[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_b[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if H is not None and mask is not None:
            homography_found = True
            ransac_inliers = int(mask.sum())
            inlier_ratio = ransac_inliers / good_matches if good_matches > 0 else 0.0

            # Project corners of A into B's space
            h_a, w_a = img_a.shape[:2]
            h_b, w_b = img_b.shape[:2]
            corners_a = np.float32([[0, 0], [w_a, 0], [w_a, h_a], [0, h_a]])
            corners_b_img = np.float32([[0, 0], [w_b, 0], [w_b, h_b], [0, h_b]])
            # Project A corners into B space
            corners_a_in_b = cv2.perspectiveTransform(corners_a.reshape(-1, 1, 2), H).reshape(-1, 2)

            area_a = float(w_a * h_a)
            area_b = float(w_b * h_b)

            inter_area = poly_intersection_area(corners_a_in_b, corners_b_img)
            containment_a_in_b = inter_area / area_b if area_b > 0 else 0.0
            containment_b_in_a = inter_area / area_a if area_a > 0 else 0.0
        else:
            msg = f"HOMOGRAPHY_FAIL|{pair['path_a']}|{pair['path_b']}|good_matches={good_matches}"
            issues.append(msg)
    else:
        if good_matches > 0:
            msg = f"TOO_FEW_MATCHES|{pair['path_a']}|{pair['path_b']}|good_matches={good_matches}"
            issues.append(msg)

    results.append({**pair,
                    "good_matches": good_matches,
                    "ransac_inliers": ransac_inliers,
                    "inlier_ratio": inlier_ratio,
                    "containment_a_in_b": containment_a_in_b,
                    "containment_b_in_a": containment_b_in_a,
                    "homography_found": homography_found})

print(f"  Done. Processed {len(results)} pairs.")

# Write sift_issues.txt
print(f"\n[2g] Writing sift_issues.txt ({len(issues)} issues)...")
with open(sift_issues_path, "w", encoding="utf-8") as f:
    if issues:
        for msg in issues:
            f.write(msg + "\n")
    else:
        f.write("No SIFT issues.\n")

# 3. Report counts
cross_results = [r for r in results if r["split_a"] != r["split_b"]]
within_results = [r for r in results if r["split_a"] == r["split_b"]]

print(f"\n[3] SIFT inlier counts:")
print(f"  Cross-split pairs: {len(cross_results)}")
for thresh in [15, 30, 60]:
    count = sum(1 for r in cross_results if r["ransac_inliers"] >= thresh)
    print(f"    inliers >= {thresh}: {count}")

print(f"  Within-split pairs: {len(within_results)}")
for thresh in [15, 30, 60]:
    count = sum(1 for r in within_results if r["ransac_inliers"] >= thresh)
    print(f"    inliers >= {thresh}: {count}")

# 4. Save sift_results.csv
sift_csv = output_dir / "sift_results.csv"
fieldnames = ["path_a", "split_a", "stem_a", "path_b", "split_b", "stem_b",
              "min_phash_dist", "dhash_dist", "cosine_sim",
              "good_matches", "ransac_inliers", "inlier_ratio",
              "containment_a_in_b", "containment_b_in_a", "homography_found"]
print(f"\n[4] Saving sift_results.csv...")
with open(sift_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow({k: r.get(k, "") for k in fieldnames})
print(f"  Saved {len(results)} rows to {sift_csv}")

print("\n" + "=" * 60)
print("STEP A3 COMPLETE")
print("=" * 60)
