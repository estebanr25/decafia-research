# CORRECTIONS.md — DECAFIA v2.1.0

Changes since v2.0.0 (doi:10.5281/zenodo.22756170).

---

## 1. Grouped split (split_grouped_v1)

The train/val/test split now uses a grouped assignment strategy (split_grouped_v1).
All crops, rotations, and capture-series frames from the same physical leaf are assigned
to the same subset. This prevents crop-parent and capture-series pairs from crossing split
boundaries (also called "same-leaf duplication between splits").

The split is NOT described as "leakage-free" or "sin fuga"; same-leaf duplication was
investigated by an independent post-hoc integrity audit (see Section 2 below).

Split files included:
- `split_grouped_v1/assignments.csv` — image → split → group_root mapping
- `split_grouped_v1/train.txt`, `val.txt`, `test.txt` — image lists

Sizes: train 1,577 | val 382 | test 356 | total 2,315 images.

---

## 2. Integrity audit — residual transformed copies (MINEIRO_99 caveat)

A post-hoc integrity audit using 64-bit DCT perceptual hashing over 8 dihedral
transforms, followed by SIFT+RANSAC geometric verification (inliers ≥ 30,
hull coverage ≥ 0.50), identified:

- 60 cross-split image pairs at pHash Hamming distance ≤ 4
- 49 unique test images (13.8%) with a geometrically verified transformed copy
  in the training or validation split
- Largest verified component: 272 images (the MINEIRO_99 group) —
  all leaf-miner images from the Silva et al. Brazilian laboratory source

The 49 affected test images are listed in `split_grouped_v1/v1_test_exclusion_list.csv`.

**Minador test performance caveat:** All minador test images belong to the MINEIRO_99
component and therefore share group membership with training images through
SIFT-verified copies. mAP@0.50 = 0.985 for minador cannot be interpreted as
performance on independent held-out leaves.

---

## 3. NMS IoU evaluation setting — iou = 0.7

All official evaluation results for v2.1.0 use Ultralytics `model.val()` with
NMS IoU threshold = 0.7, confidence threshold = 0.001.

This matches the September 2026 documented evaluation setting.
An earlier session used iou = 0.6 (mAP50-95 = 0.722 vs. 0.734 at iou = 0.7);
iou = 0.7 is the correct official setting.

---

## 4. Attribution note for crops derived from Silva et al.

Images derived from Silva et al. 2020 (DOI: 10.17632/vfxf4trtcg.5) are
redistributed under CC BY 4.0. Attribution:

  L. B. Silva, A. L. C. Carneiro, and M. S. A. R. Faulin,
  "Rust and leaf miner in coffee crop (Coffea arabica),"
  Mendeley Data, V5, 2020, doi: 10.17632/vfxf4trtcg.5.

These images have MINEIRO_* file prefixes in DECAFIA. They were originally
acquired in a laboratory on a white background. All bounding-box annotations
are new DECAFIA annotations; original Silva et al. image-level labels are
not used or reproduced.
