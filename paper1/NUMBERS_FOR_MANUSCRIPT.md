# NUMBERS_FOR_MANUSCRIPT.md

All claims rendered from paper1/results/metrics_final.json (SHA-256 prefix: bc4fbb2b09d6)

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
| Bootstrap CI roya (image-level, secondary) lo | phase4.test_set_full.bootstrap_map50_ci95.per_class_image_level.roya.lo | 0.8033 |
| Bootstrap CI roya (image-level, secondary) hi | phase4.test_set_full.bootstrap_map50_ci95.per_class_image_level.roya.hi | 0.8735 |
| Overall cluster CI | — | NOT REPORTED (roya: 53.1% single cluster; minador: contaminated) |
| Filtered test mAP50 | filtered_test.map50_overall (or phase_fix_log) | 0.925574 |
| Filtered test mAP50-95 | (phase_fix_log) | 0.729163 |
| Contaminated test images excluded | exclusion_list.n_excluded | 49 |

## Notes on CIs

The cluster bootstrap uses v1 groups (group_root from assignments.csv) as clusters.

**roya:** 10 clusters, largest (ROYA_RECORTES_107) holds 438/825 = 53.1% of roya test instances.
Cluster CI cannot be estimated. Report image-level CI as secondary only, labeled "ignores within-leaf correlation".

**coco:** 6 clusters, largest holds 37.2%. Cluster CI: [0.801, 0.971] — REPORTABLE.

**minador:** 4 clusters, largest holds 43.7%. Cluster CI: NOT REPORTED IN MANUSCRIPT.
Reason: minador test images share group membership with training images through verified
transformed copies. CI is not meaningful as performance on independent held-out leaves.
(Retained in JSON with reported:false.)

**Overall CI:** NOT REPORTED (both roya cluster bootstrap invalid AND minador contaminated).

## Roya source analysis (Phase 1.3 check)

The ROYA_RECORTES_107 cluster (the large roya cluster causing the CI issue) does NOT
overlap the MINEIRO_99 verified component. The only edge between a MINEIRO_99 node and a
ROYA_* image (MINADOR_50 — ROYA_FONDO_35) fails SIFT verification (4 inliers, 0.23 hull
coverage — both below threshold). Therefore, roya test images in ROYA_RECORTES_107 are
NOT linked to training images through verified copies. The roya cluster CI is unreportable
solely because of cluster size, not data contamination.

## NMS iou note

Previous session used iou=0.6 → mAP50-95=0.722829. Official setting iou=0.7 → 0.734368.
See section2_resolution in metrics_final.json.

## Component size note (Phase 1.4)

The MINEIRO_99 component:
- 290 images: original v1 group size (MINEIRO_99 group before SESSION_SPLIT_V2)
- 339 images: after SESSION_SPLIT_V2 pHash merges (incorporated adjacent groups)
- 272 images: after SESSION_FIX_V2 SIFT+mask edge re-verification (4 false pHash edges removed)

The manuscript uses **272** as the verified component size.
Brief explanation for methods: "The largest verified component (272 images) comprises
laboratory leaf images from the external dataset with pHash-verified geometric copies
in the training split."
