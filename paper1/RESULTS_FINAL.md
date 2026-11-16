# RESULTS_FINAL.md

Path B. Official model: decafia_grouped_v1 on split_grouped_v1.
**NOTE: Two test sets differ (see Phase 3B). Full and filtered results both reported; this is a sensitivity measurement, not a corrected metric.**

## Model

- Name: decafia_grouped_v1
- SHA-256: d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a
- Split: split_grouped_v1 (train 1577 / val 382 / test 356)

## Full v1 Test Set (356 images, 158 backgrounds)

| | overall | roya | coco | minador |
|-|---------|------|------|---------|
| mAP50 | 0.928148 | 0.839143 | 0.962144 | 0.983157 |
| mAP50-95 | 0.722829 | 0.515676 | 0.787722 | 0.865089 |

Comparison with model.val reference: mAP50 ref=0.929781 (delta=0.001633)

### P/R/F1 at conf=0.50

| Class | P | R | F1 |
|-------|---|---|----|
| roya    | 0.8501 | 0.6945 | 0.7645 |
| coco    | 0.9187 | 0.8963 | 0.9074 |
| minador | 0.9471 | 0.9547 | 0.9509 |
| all     | 0.8996 | 0.8248 | 0.8605 |

Background FA at conf=0.50: 3/158 = 0.0190

### 95% Bootstrap CIs (mAP50, B=2000, seed=42, cluster primary)

| Class | lo | hi |
|-------|----|----|
| overall | 0.8469 | 0.9430 |
| roya    | 0.7047 | 0.8796 |
| coco    | 0.8012 | 0.9715 |
| minador | 0.9734 | 0.9998 |

CIs reflect test-set sampling variability only (single training seed).

### Confusion matrix (pred x true, conf=0.50)

Rows = predicted class, columns = true class. Last row/col = background.

```
[[573   0   0 101]
 [  0 735   0  65]
 [  0   0 358  20]
 [252  85  17   0]]
```

Column sums match GT counts: True
GT counts: roya=825, coco=820, minador=375

## Filtered v1 Test Set (307 images)

Path B sensitivity measurement only. See metrics_final.json for full filtered metrics.
mAP50=0.926117, mAP50-95=0.726920
Delta vs full: mAP50=-0.0020

## Source file

All numbers in this file are rendered from paper1/results/metrics_final.json.
