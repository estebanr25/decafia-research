# RESULTS_FINAL.md

Path B. Official model: decafia_grouped_v1 on split_grouped_v1.
**NOTE: Two test sets differ (see Phase 3B). Full and filtered results both reported; this is a sensitivity measurement, not a corrected metric.**

**NMS IoU setting: iou=0.7 (documented September setting; previous session used iou=0.6 — see section2_resolution in metrics_final.json).**

## Model

- Name: decafia_grouped_v1
- SHA-256: d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a
- Split: split_grouped_v1 (train 1577 / val 382 / test 356)

## Full v1 Test Set (356 images, 158 backgrounds) — iou=0.7

| | overall | roya | coco | minador |
|-|---------|------|------|---------|
| mAP50 (model.val) | 0.929377 | 0.841307 | 0.961786 | 0.985040 |
| mAP50-95 (model.val) | 0.734368 | 0.537046 | 0.794734 | 0.871323 |
| mAP50 (recomputed) | 0.928432 | 0.840425 | 0.962468 | 0.982403 |

model.val is the authoritative value (matches September documentation).

### P/R/F1 at conf=0.50

| Class | P | R | F1 |
|-------|---|---|----|
| roya    | 0.8454 | 0.6958 | 0.7633 |
| coco    | 0.9178 | 0.8988 | 0.9082 |
| minador | 0.9347 | 0.9547 | 0.9446 |
| all     | 0.8949 | 0.8262 | 0.8592 |

Background FA at conf=0.50: 3/158 = 0.0190

### 95% Bootstrap CIs (mAP50, B=2000, seed=42)

Cluster bootstrap validity check:
- roya: 10 clusters, largest holds 53.1% of test instances — CANNOT REPORT cluster CI
- coco: 6 clusters, largest holds 37.2% — REPORTABLE
- minador: 4 clusters, largest holds 43.7% — REPORTABLE
- Overall cluster CI: NOT REPORTED (roya invalid)

| Class | Method | lo | hi |
|-------|--------|----|----|
| coco    | cluster (primary) | 0.8012 | 0.9713 |
| minador | cluster (primary) | 0.9731 | 0.9998 |
| roya    | image-level only (secondary) | 0.8033 | 0.8735 |
| coco    | image-level (secondary) | 0.9505 | 0.9741 |
| minador | image-level (secondary) | 0.9720 | 0.9912 |

Image-level bootstrap ignores within-leaf correlation; shown as secondary only.
CIs reflect test-set sampling variability only (single training seed).

### Confusion matrix (pred x true, conf=0.50)

Rows = predicted class, columns = true class. Last row/col = background.

```
[[574   0   0 105]
 [  0 737   0  66]
 [  0   0 358  25]
 [251  83  17   0]]
```

Column sums match GT counts: True
GT counts: roya=825, coco=820, minador=375

## Filtered v1 Test Set (307 images) — iou=0.7

Path B sensitivity measurement only.
mAP50=0.925574, mAP50-95=0.729163
Delta vs full: mAP50=-0.0038, mAP50-95=-0.0052

## Source file

All numbers in this file are rendered from paper1/results/metrics_final.json.
