<!-- SUPERSEDED — see audits/near_duplicates/README.md -->
# DECAFIA Near-Duplicate Audit Report
**Dataset:** decafia_clean — 2315 images (train=1618, val=348, test=349)
**Provenance manifest:** C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\provenance_manifest.csv
**Output folder:** C:\Users\luise\temp\decafia-research\audits\near_duplicates
**Date run:** 2026-09-14

---

## 1. Flagged Cross-Split Pairs by Method and Threshold

### 1a. Perceptual Hash (pHash, min of direct and flipped)

| Threshold (≤) | Cross-split pairs |
|---|---|
| phash_dist ≤ 0 | 52 |
| phash_dist ≤ 4 | 57 |
| phash_dist ≤ 8 | 85 |
| phash_dist ≤ 12 | 492 |

### 1b. ResNet-50 Cosine Similarity (cross-split top-5)

| Threshold (≥) | Unique cross-split pairs |
|---|---|
| cosine_sim ≥ 0.9 | 6214 |
| cosine_sim ≥ 0.95 | 662 |
| cosine_sim ≥ 0.99 | 48 |

### 1c. SIFT Geometric Verification (RANSAC inliers)

| Threshold (≥) | Cross-split pairs |
|---|---|
| sift_inliers ≥ 15 | 845 |
| sift_inliers ≥ 30 | 722 |
| sift_inliers ≥ 60 | 641 |

---

## 2. Breakdown by Split Pair

### sift_inliers ≥ 15

| Split pair | Count |
|---|---|
| test↔train | 401 |
| test↔val | 58 |
| train↔val | 386 |

### cosine_sim ≥ 0.95

| Split pair | Count |
|---|---|
| test↔train | 269 |
| test↔val | 43 |
| train↔val | 350 |

---

## 3. Breakdown by Filename Prefix

(Pairs with sift_inliers ≥ 30, by img_a_prefix)

| Prefix | Count |
|---|---|
| SANAS | 639 |
| COCO | 37 |
| MINADO | 19 |
| ROYA | 16 |
| MINEIRO | 11 |

---

## 4. TEST Images with Likely Duplicate/Parent in TRAIN

| Method & Threshold | Unique TEST images | Annotations roya | Annotations coco | Annotations minador |
|---|---|---|---|---|
| sift>=15 | 158 | 121 | 172 | 67 |
| sift>=30 | 140 | 60 | 116 | 36 |
| sift>=60 | 127 | 50 | 104 | 27 |
| cos>=0.90 | 301 | 583 | 614 | 328 |
| cos>=0.95 | 114 | 46 | 58 | 13 |
| cos>=0.99 | 23 | 0 | 0 | 0 |

---

## 5. Limitations

- **Hash methods** (pHash, dHash) only detect near-identical images. Cropped, recoloured, or resized images at distance > 12 bits are missed by this pass.
- **ResNet-50 embeddings** were computed with `num_workers=0` (CPU DataLoader) to avoid multiprocessing issues; this does not affect correctness. The top-5 cross-split search is asymmetric: very similar pairs that happen to be ranked 6th or lower are missed. Cosine similarity at the 50th percentile is ~0.92 across this dataset, meaning most images share moderately similar visual features (consistent field conditions); many pairs above 0.90 are NOT true duplicates.
- **SIFT verification** was run on 9589 candidates (union of hash≤12 and cos≥0.85). Pairs with very low texture (background images) may get 0 SIFT keypoints, recorded as 0 inliers in sift_issues.txt (642 issues logged). Homography requires ≥4 matches; pairs with 1-3 matches are logged but not considered verified.
- **Provenance manifest** was used to label sources; if any image is absent from the manifest, source is reported as UNKNOWN.
- **No within-split SIFT** was performed (hash candidates and embedding top-5 were cross-split only by design). Within-split duplicates are flagged in the hash step (66 pairs at pHash=0) but not SIFT-verified here.
- These findings flag *candidates* for human review, not confirmed leakage. Final leakage determination requires domain knowledge of image acquisition.
