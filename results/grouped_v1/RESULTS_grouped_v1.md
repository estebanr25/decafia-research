# RESULTS — DECAFIA grouped split v1

Model: `decafia_grouped_v1_best.pt` (YOLOv8m, 100 epochs, AdamW)
Split: leakage-safe grouped split (B=20, union-find on number blocks + crop-parent + pHash ≤ 4)
Test set: **356 images, 2,020 instances** (CONFIRMED)
Val set: 382 images

---

## 1. Per-class test results (CONFIRMED)

| Class   |    P |    R |   F1 | mAP50 | mAP50-95 |
|---------|------|------|------|-------|----------|
| all     | 0.876 | 0.870 | 0.873 | 0.929 | 0.734    |
| roya    | 0.803 | 0.740 | 0.770 | 0.841 | 0.537    |
| coco    | 0.908 | 0.909 | 0.908 | 0.962 | 0.795    |
| minador | 0.918 | 0.963 | 0.940 | 0.985 | 0.871    |

F1 = 2·P·R/(P+R), computed from the CONFIRMED P and R above.

---

## 2. Val vs test consistency

| Split | mAP50 | mAP50-95 |
|-------|-------|----------|
| val   | 0.924 | 0.731    |
| test  | 0.929 | 0.734    |
| diff  | +0.005 | +0.003  |

Val and test differ by < 0.5 pp on both aggregate metrics, indicating
that the grouped split produced a consistent difficulty distribution.

---

## 3. Background false positives (CONFIRMED — eval_background_fp.py)

Background images in test split (empty label file): **158**

| Threshold | Images clean | Images w/ FP | Total FP boxes | roya FP | coco FP | minador FP |
|-----------|-------------|--------------|----------------|---------|---------|------------|
| conf ≥ 0.25 | 145/158 (91.8%) | 13 | 13 | 1 | 3 | 9 |
| conf ≥ 0.50 | 155/158 (98.1%) | 3 | 3 | 1 | 1 | 1 |

Images with detections at conf ≥ 0.25 (13):
SANAS_NUEVAS_534
    SANAS_NUEVAS_396
    SANAS_NUEVAS_57
    SANAS_SOCORRO_112
    SANAS_SOCORRO_123
    SANAS_SOCORRO_202
    SANAS_SOCORRO_209
    SANAS_SOCORRO_211
    SANAS_SOCORRO_217
    SANAS_SOCORRO_398
    SANAS_NUEVAS_397
    SANAS_SOCORRO_107
    SANAS_SOCORRO_133

Images with detections at conf ≥ 0.50 (3):
SANAS_NUEVAS_396
    SANAS_NUEVAS_57
    SANAS_SOCORRO_398

All FP images belong to the SANAS prefix (healthy-leaf images from the same acquisition
as annotated leaves), consistent with their visual similarity to annotated leaves.

---

## 4. Baseline vs grouped comparison

> **Caveat:** Test sets differ between splits and a single split seed was used;
> per-class differences (≤ 4.5 pp) were not evaluated against split-to-split variability.

Baseline: `decafia_clean_v1-2` — per-image stratified split, test set 349 images (CONFIRMED).
Grouped:  `decafia_grouped_v1`  — leakage-safe grouped split, test set 356 images (CONFIRMED).

| Class   | Metric     | Baseline | Grouped | Δ (pp)  |
|---------|------------|----------|---------|---------|
| all     | mAP50      | 0.9235   | 0.929   | +0.55  |
| all     | mAP50-95   | 0.7293   | 0.734   | +0.47  |
| roya    | mAP50      | 0.8619   | 0.841   | -2.09  |
| roya    | mAP50-95   | 0.5700   | 0.537   | -3.30  |
| coco    | mAP50      | 0.9638   | 0.962   | -0.18  |
| coco    | mAP50-95   | 0.7921   | 0.795   | +0.29  |
| minador | mAP50      | 0.9449   | 0.985   | +4.01  |
| minador | mAP50-95   | 0.8258   | 0.871   | +4.52  |

---

## 5. Limitations

1. **Non-consecutive file numbers:** The grouped split uses floor(number / B) blocks to
   detect same-session images. A physical leaf photographed at non-consecutive file numbers
   (e.g., session gap between images) is not detectable by this strategy and can only be
   caught by pHash near-duplicate edges (distance ≤ 4). Pairs with 5 ≤ pHash ≤ 12 may
   still represent the same leaf and remain undetected. Residual leakage cannot be fully
   excluded.

2. **Orphan-crop rule:** Orphan crops from the `own_field` source (COCO_RECORTE, 64 images)
   are forced to the training split, under the assumption that their parents exist in the
   dataset but were not detected by the SIFT pipeline. If any such parent is actually in val
   or test, these crops represent a minor train-time advantage that cannot be quantified
   without re-running the SIFT crop-parent search with relaxed thresholds.

3. **Single seed:** Only seed=42 was used for the randomized group assignment. The reported
   per-class differences between baseline and grouped are within the likely range of
   split-to-split variability and should not be interpreted as model-level differences.

4. **Metric transcription:** Metric values in this file were transcribed from the Ultralytics
   test evaluation output (runs/decafia_grouped_v1_test) by
   scripts/one_shot/organize_grouped_v1.py; they were not re-parsed automatically.

---

## 6. Figures

### Test evaluation (`decafia_grouped_v1_test/`)
- `BoxF1_curve.png`
- `BoxPR_curve.png`
- `BoxP_curve.png`
- `BoxR_curve.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`

### Training run (`decafia_grouped_v1/`)
- `BoxF1_curve.png`
- `BoxPR_curve.png`
- `BoxP_curve.png`
- `BoxR_curve.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`
- `results.png`
