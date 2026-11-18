# NUMBERS_FOR_MANUSCRIPT.md

All claims rendered from paper1/results/metrics_final.json (SHA-256 at time of writing: bc4fbb2b09d6...)

Path B: decafia_grouped_v1 evaluated on split_grouped_v1 test set.
NMS IoU setting: iou=0.7 (September documented setting).

| Claim | JSON path | Value |
|-------|-----------|-------|
| mAP50 (full test, model.val) | phase4.test_set_full.map50_model_val | 0.929377 |
| mAP50-95 (full test, model.val) | phase4.test_set_full.map50_95_model_val | 0.734368 |
| mAP50 roya | phase4.test_set_full.map50_per_class_model_val.roya | 0.841307 |
| mAP50 coco | phase4.test_set_full.map50_per_class_model_val.coco | 0.961786 |
| mAP50 minador | phase4.test_set_full.map50_per_class_model_val.minador | 0.985040 |
| Background FA rate | phase4.test_set_full.background_far_at_conf050.rate | 0.018987 |
| Bootstrap CI coco (cluster) lo | phase4.test_set_full.bootstrap_map50_ci95.per_class_cluster.coco.lo | 0.8012 |
| Bootstrap CI coco (cluster) hi | phase4.test_set_full.bootstrap_map50_ci95.per_class_cluster.coco.hi | 0.9713 |
| Bootstrap CI minador (cluster) lo | phase4.test_set_full.bootstrap_map50_ci95.per_class_cluster.minador.lo | 0.9731 |
| Bootstrap CI minador (cluster) hi | phase4.test_set_full.bootstrap_map50_ci95.per_class_cluster.minador.hi | 0.9998 |
| Overall cluster CI | — | NOT REPORTED (roya single cluster 53.1% > 50%) |
| Filtered test mAP50 | filtered_test.map50_overall | 0.925574 |
| Filtered test mAP50-95 | filtered_test.map50_95_overall | 0.729163 |
| Contaminated test images excluded | exclusion_list.n_excluded | 49 |

## Notes on CIs

The cluster bootstrap cannot estimate the roya interval because one cluster
(ROYA_RECORTES_107) holds 438/825 = 53.1% of test-set roya instances, exceeding the 50%
reportability threshold. The overall mAP50 CI is therefore also not reported.

Per-class cluster CIs are reported for coco and minador only.
Image-level bootstrap CIs are shown as secondary for all classes (ignores within-leaf correlation).

## NMS iou discrepancy (now resolved)

The previous session reported mAP50-95=0.722829 / 0.726920. This was computed with iou=0.6
instead of the documented September setting iou=0.7. With iou=0.7: mAP50-95=0.734368 (full)
/ 0.729163 (filtered). The mAP50 gap is negligible (0.929377 vs 0.929781; within noise).
See section2_resolution in metrics_final.json.
