# FIGURES.md

Draft captions rendered from paper1/results/metrics_final.json.

**Figure 3.** Confusion matrix for decafia_grouped_v1 on split_grouped_v1 test set
(n=356 images) at confidence threshold 0.50. Left: raw counts. Right: normalized
by true class. Rows = predicted class; columns = true class; last row/column = background.
GT counts: roya=825, coco=820, minador=375.

**Figure 7.** mAP50 per class with 95% bootstrap confidence intervals (B=2000,
cluster bootstrap over leaf groups, seed=42). CIs reflect test-set sampling
variability only (single training seed).
roya: 0.839 [0.705, 0.880];
coco: 0.962 [0.801, 0.971];
minador: 0.983 [0.973, 1.000].

**Figure 5.** Training curves (val mAP50 vs epoch) for decafia_grouped_v1 on
split_grouped_v1.
