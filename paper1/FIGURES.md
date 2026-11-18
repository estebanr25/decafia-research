# FIGURES.md

Draft captions rendered from paper1/results/metrics_final.json.
Updated for Phase 1 (SESSION_MANUSCRIPT): minador CI removed; roya CI secondary only.

---

**Figure 3.** Confusion matrix for decafia_grouped_v1 on split_grouped_v1 test set
(n=356 images) at confidence threshold 0.50. Left: raw counts. Right: normalized
by true class. Rows = predicted class; columns = true class; last row/column = background.
GT counts: roya=825, coco=820, minador=375.

---

**Figure 5.** Training curves (val mAP50 vs epoch) for decafia_grouped_v1 on
split_grouped_v1.

---

**Figure 7.** mAP50 per class with 95% confidence intervals (B=2000, seed=42).
CIs reflect test-set sampling variability only (single training seed).
Cluster bootstrap (v1 leaf groups as clusters) is used where reportable:
- roya: 0.841 — cluster CI not reportable (one group holds 53% of test instances);
  image-level CI [0.803, 0.874] shown as secondary (ignores within-leaf correlation).
- coco: 0.962 — cluster CI [0.801, 0.971].
- minador: 0.985 — CI not shown (test images share group membership with training
  images through verified transformed copies; independent-leaf evaluation not possible).

Note: minador bar shown as a point estimate only, with a dagger (†) referring to the
minador caveat in the methods section.
