# NUMBERS_FOR_MANUSCRIPT.md

All claims rendered from paper1/results/metrics_final.json (SHA-256 at time of writing: 304ff8ad1e5f152a179bfe21acece2e422666c435c4107dd6f7418b651ea571f)

Path B: decafia_grouped_v1 evaluated on split_grouped_v1 test set.

| Claim | JSON key | Value |
|-------|----------|-------|
| mAP50 (full test) | phase4.test_set_full.map50_overall | 0.928148 |
| mAP50-95 (full test) | phase4.test_set_full.map50_95_overall | 0.722829 |
| mAP50 roya | phase4.test_set_full.map50_per_class.roya | 0.839143 |
| mAP50 coco | phase4.test_set_full.map50_per_class.coco | 0.962144 |
| mAP50 minador | phase4.test_set_full.map50_per_class.minador | 0.983157 |
| Background FA rate | phase4.test_set_full.background_far_at_conf050.rate | 0.018987 |
| Bootstrap CI overall lo | phase4.test_set_full.bootstrap_map50_ci95.cluster.overall.lo | 0.8469 |
| Bootstrap CI overall hi | phase4.test_set_full.bootstrap_map50_ci95.cluster.overall.hi | 0.9430 |
| Filtered test mAP50 | filtered_test.map50_overall | 0.926117 |
| Filtered test mAP50-95 | filtered_test.map50_95_overall | 0.726920 |
| Contaminated test images excluded | exclusion_list.n_excluded | 49 |
