# RESULTS_FINAL.md

Path B. Official model: decafia_grouped_v1 on split_grouped_v1.
**NOTE: Two test sets differ (see Phase 3B). Full and filtered results both reported; this is a sensitivity measurement, not a corrected metric.**
**NMS IoU setting: iou=0.7 (September documented setting).**

## Model

- Name: decafia_grouped_v1
- SHA-256: d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a
- Split: split_grouped_v1 (train 1577 / val 382 / test 356)

## Full v1 Test Set (356 images, 158 backgrounds) — iou=0.7

| | overall | roya | coco | minador |
|-|---------|------|------|---------|
| mAP50 (model.val) | 0.929377 | 0.841307 | 0.961786 | 0.985040* |
| mAP50-95 (model.val) | 0.734368 | 0.537046 | 0.794734 | 0.871323* |

*minador: test images share group membership with training images through verified transformed
copies. Performance on independent held-out leaves cannot be estimated.

### P/R/F1 at conf=0.50

| Class | P | R | F1 |
|-------|---|---|----|
| roya    | 0.8454 | 0.6958 | 0.7633 |
| coco    | 0.9178 | 0.8988 | 0.9082 |
| minador | 0.9347 | 0.9547 | 0.9446* |
| all     | 0.8949 | 0.8262 | 0.8592 |

*minador caveat applies

Background FA at conf=0.50: 3/158 = 0.0190

### 95% Bootstrap CIs (mAP50, B=2000, seed=42)

Clusters = v1 groups (group_root from assignments.csv)

| Class | Method | lo | hi | Reportable? |
|-------|--------|----|----|-------------|
| coco    | cluster (primary) | 0.8012 | 0.9713 | YES |
| roya    | image-level (secondary; ignores within-leaf correlation) | 0.8033 | 0.8735 | SECONDARY ONLY |
| minador | cluster | (0.9731) | (0.9998) | NOT REPORTED (contaminated) |
| overall | — | — | — | NOT REPORTED |

Roya cluster CI not reportable: ROYA_RECORTES_107 holds 53.1% of roya test instances (>50% threshold).
Minador CI not reported: test images contaminated; not independent-leaf evaluation.
Overall CI not reported: roya and minador conditions both unmet.

**Phase 1.3 check:** ROYA_RECORTES_107 does NOT overlap MINEIRO_99 verified component.
The one candidate edge (MINADOR_50 — ROYA_FONDO_35) fails SIFT verification (4 inliers).
Roya test images are not contaminated; the cluster CI issue is purely statistical.

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

Sensitivity measurement only (two test sets differ in composition).
mAP50=0.925574, mAP50-95=0.729163
Delta vs full: mAP50=-0.0038, mAP50-95=-0.0052

## Source file

All numbers in this file are rendered from paper1/results/metrics_final.json.
