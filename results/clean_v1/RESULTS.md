# Evaluation Results — decafia_clean_v1

**Date:** 2026-09-11
**Model:** `03_models/decafia_clean_best.pt`
**Split:** TEST (349 images, 1,948 instances)
**Dataset card assertions:** passed (349 images, 1,948 instances)
**Training run:** `02_training/runs/decafia_clean_v1-2/`

## Per-Class Metrics

| Class | Precision | Recall | F1 | mAP50 | mAP50-95 |
|-------|----------:|-------:|---:|------:|---------:|
| roya    | 0.8364 | 0.7931 | 0.8142 | 0.8619 | 0.5700 |
| coco    | 0.9177 | 0.9087 | 0.9132 | 0.9638 | 0.7921 |
| minador | 0.8687 | 0.8987 | 0.8834 | 0.9449 | 0.8258 |
| **all** | | | | **0.9235** | **0.7293** |

## Confusion Matrix Notes

Ultralytics stores the matrix as **cm[predicted, true]**. Column sums equal the
dataset card GT counts (roya 864, coco 699, minador 385), confirming orientation.
`confusion_matrix_normalized.png` is column-normalised by true-class GT count;
diagonal values are therefore recall at the CM confidence threshold (≈ 0.25),
which is higher than the F1-optimal threshold used for the metrics table above.

The raw (counts) 4×4 matrix — rows = predicted class, cols = true class:

| Pred \ True | roya | coco | minador | bkgd (no GT) |
|-------------|-----:|-----:|--------:|-------------:|
| roya        |  753 |    1 |       0 |          248 |
| coco        |    1 |  657 |       0 |          116 |
| minador     |    2 |    0 |     361 |           90 |
| bkgd (FN)  |  108 |   41 |      24 |            0 |

Column sums (GT totals): roya=864, coco=699, minador=385 — match dataset card.

**Background column** (`bkgd (no GT)`, col 4) — left blank in the figure:
These are detections with no matching ground-truth box (FP). The cell value is
the detection count, not an instance count. Raw totals: 248 roya + 116 coco +
90 minador = **454 FP detections** at CM threshold (≈ 0.25). These fire on
background images or on annotated images where no GT box had sufficient IoU.
At the operational threshold (conf ≥ 0.50), only 4 FP detections survive across
all 167 background test images (3 roya, 1 coco): 164/167 (98.2%) produce zero
detections, and 3/167 (1.8%) produce at least one.

**Background row** (`bkgd (FN)`, row 4) — left blank in the figure:
These are GT boxes not matched by any detection (FN / missed detections).
Raw counts: **108 roya + 41 coco + 24 minador = 173 total missed GT boxes**.

**Roya** has the highest FN count (108 missed GT boxes, 12.5% of 864 roya GT).
It also has the most FP detections (248 at CM threshold). Both failure modes
lower roya precision (0.836) and recall (0.793) relative to coco and minador.
The dominant failure mode is spurious roya detections on images without disease,
not inter-class confusion (off-diagonal cross-class entries are near zero).

## Background-Image Detection Statistics (conf ≥ 0.50)

Of the 167 background test images (images with empty label files = healthy leaves):

| Result | Count | Fraction |
|--------|------:|---------:|
| Zero detections (correct) | 164 | 98.2% |
| ≥ 1 detection (FP) | 3 | 1.8% |
| Total FP detections | 4 | — |

FP breakdown at 0.50: roya=3, coco=1, minador=0.
This validates the three-class + background design: the model suppresses nearly
all spurious detections on healthy tissue at the operational threshold.

## Figures

| File | Description |
|------|-------------|
| `confusion_matrix_normalized.png` | Column-normalised CM (recall on diagonal); background row/col blank |
| `pr_curves.png` | PR curves per class from p_curve/r_curve arrays, 300 dpi |
| `training_curves.png` | 4-panel: train box loss, val mAP50, val precision, val recall |
| `test_predictions_grid.png` | 4x4 random test predictions (conf >= 0.25) |

## Interpretation Notes

- **Coco** is the strongest class (mAP50=0.964, F1=0.913): 100% own-field
  images from Socorro with consistent annotation quality.
- **Minador** (mAP50=0.945, F1=0.883): 100% from Silva et al. (Brazil).
  Performance measures cross-country generalisation, not Colombian field performance.
- **Roya** (mAP50=0.862, F1=0.814): 60% own-field / 40% Silva et al.
  Lower recall (0.793): 108 of 864 GT roya boxes not detected (FN = 12.5%).
  Lower precision (0.836): 248 spurious roya detections at CM threshold (FP).
- Background images: 167 of 349 test images (47.9%) have empty label files.
  At conf ≥ 0.50, 164/167 (98.2%) produce zero detections.
