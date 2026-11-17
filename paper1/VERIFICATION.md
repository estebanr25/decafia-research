# VERIFICATION.md

Verified by: independent verifier (SESSION_SPLIT_V2)
Date: 2026-11-17
Python: C:/Python314/python

---

## Check 1: Recompute mAP50 from per_image_stats_full.npy

**PASS**

Loaded `paper1/results/per_image_stats_full.npy` (356 entries, allow_pickle=True).
Each entry contains `pred_cls`, `pred_conf`, `tp_matrix` (shape n_pred x 10, column 0 = IoU@0.50), and `gt_cls`.

Method: for each class, collected all detections (tp_at_iou50, conf), sorted by conf descending,
computed precision-recall curve, applied max-precision envelope (monotone decreasing), then computed
area under the step function (equivalent to VOC trapezoid). This matches the method used in the original
evidence package.

| Class   | Recomputed AP50 | JSON (phase4.test_set_full.map50_per_class) | Match |
|---------|-----------------|---------------------------------------------|-------|
| roya    | 0.839143        | 0.839143                                    | exact |
| coco    | 0.962144        | 0.962144                                    | exact |
| minador | 0.983157        | 0.983157                                    | exact |
| **mAP50** | **0.928148**  | **0.928148137682382**                       | exact |

GT counts confirmed: roya=825, coco=820, minador=375 (match JSON).

Recomputed mAP50 = 0.928148, matches JSON reference 0.928148137682382 exactly (within floating-point
precision of the displayed value). The model.val reference of 0.929781 differs by 0.001633 as noted
in the JSON — this is a known discrepancy between YOLO's internal metric computation and the
recomputed value from saved stats, documented in `recomputed_reference` field.

---

## Check 2: Cross-split copy check on the final split

**PASS**

Loaded `split_v2/copy_pairs.csv` (6289 rows) and
`split_grouped_v1/assignments.csv` (2315 entries, column `split_new`).

Decision value distribution in copy_pairs.csv:
- `reject`: 5775 pairs
- `merge_within`: 394 pairs (same-split duplicates — no cross-split contamination)
- `merge`: 120 pairs

For the 120 rows with `decision == "merge"`:
- All 120 are cross-split (`cross_split == True` confirmed by both the CSV column and independent
  lookup in assignments.csv).
- The `merge` decision marks cross-split near-duplicate pairs whose test/val images were added to
  the exclusion list (v1_test_exclusion_list.csv).
- No `merge` row has stem_a and stem_b in the same logical split — they are all cross-split, which
  is the correct and expected behavior for this decision type.

Cross-split `merge` pairs broken down by split pair type:
- train-test pairs: 49 unique test-side images affected
- train-val pairs: 43 unique val-side images affected
- val-test pairs: a small number of val/test pairs also present

The 49 unique test images affected matches exactly the `exclusion_list.n_excluded = 49` in
`metrics_final.json`. The exclusion list is consistent with the copy_pairs.csv merge decisions.

**Count of merged cross-split pairs: 120**

---

## Check 3: Numbers in .md files vs JSON

**PASS**

Checked all numeric claims in `paper1/RESULTS_FINAL.md`, `paper1/NUMBERS_FOR_MANUSCRIPT.md`,
and `paper1/FIGURES.md` against `paper1/results/metrics_final.json`.

### NUMBERS_FOR_MANUSCRIPT.md (11 claims)

| Claim | JSON key | MD value | JSON value | Match |
|-------|----------|----------|------------|-------|
| mAP50 (full test) | phase4.test_set_full.map50_overall | 0.928148 | 0.928148137... | OK |
| mAP50-95 (full test) | phase4.test_set_full.map50_95_overall | 0.722829 | 0.722828926... | OK |
| mAP50 roya | phase4.test_set_full.map50_per_class.roya | 0.839143 | 0.839143 | OK |
| mAP50 coco | phase4.test_set_full.map50_per_class.coco | 0.962144 | 0.962144 | OK |
| mAP50 minador | phase4.test_set_full.map50_per_class.minador | 0.983157 | 0.983157 | OK |
| Background FA rate | phase4.test_set_full.background_far_at_conf050.rate | 0.018987 | 0.018987 | OK |
| Bootstrap CI overall lo | ...cluster.overall.lo | 0.8469 | 0.846852... | OK (rounded) |
| Bootstrap CI overall hi | ...cluster.overall.hi | 0.9430 | 0.943047... | OK (rounded) |
| Filtered test mAP50 | filtered_test.map50_overall | 0.926117 | 0.926117 | OK |
| Filtered test mAP50-95 | filtered_test.map50_95_overall | 0.726920 | 0.72692 | OK |
| Contaminated excluded | exclusion_list.n_excluded | 49 | 49 | OK |

### RESULTS_FINAL.md (34 claims checked)

All mAP50/mAP50-95 per class, P/R/F1 at conf=0.50 for all classes, background FA rate,
bootstrap CIs (all 8 lo/hi values), GT counts per class, filtered test mAP50 and mAP50-95:
all match JSON exactly or within display rounding. No mismatches found.

### FIGURES.md (12 claims checked)

Figure 7 caption values (roya/coco/minador mAP50 rounded to 3dp, all 6 CI endpoints rounded to 3dp)
and Figure 3 caption GT counts (roya=825, coco=820, minador=375): all match JSON. No mismatches.

**No mismatches found in any .md file.**

---

## Check 4: Banned-strings check

**PASS**

Searched all files under `paper1/` for the following exact strings:

| String | Occurrences |
|--------|-------------|
| "92.4%" | 0 |
| "76.6%" | 0 |
| "2,786" | 0 |
| "Coccinellidae" | 0 |
| "Pseudococcidae" | 0 |

None of the banned strings appear in any file under `paper1/`.

---

## Check 5: Plotted values vs sidecar JSON

**PASS**

### Figure 7 (`figure7_bootstrap_intervals_sidecar.json`)

3 spot-checks of `plotted_values` against `metrics_final.json`:

| Value | Sidecar | JSON | Match |
|-------|---------|------|-------|
| map50_per_class.roya | 0.8391 | 0.839143 (rounds to 0.8391) | OK |
| ci95_cluster.coco.lo | 0.8011976064938466 | 0.8011976064938466 | exact |
| ci95_cluster.minador.hi | 0.9997577519379846 | 0.9997577519379846 | exact |

All `ci95_cluster` values in the sidecar are identical (full precision) to `metrics_final.json`.
`map50_per_class` values are stored rounded to 4 decimal places, consistent with the JSON source.

### Figure 3 counts (`figure3_confusion_counts_sidecar.json`)

3 spot-checks of confusion matrix `cm[pred,true]`:

| Cell | Sidecar | JSON | Match |
|------|---------|------|-------|
| cm[0][0] (roya TP) | 573 | 573 | exact |
| cm[3][0] (roya FN) | 252 | 252 | exact |
| cm[1][1] (coco TP) | 735 | 735 | exact |

Additional check: column sums of JSON confusion matrix = [825, 820, 375] for roya/coco/minador,
matching GT counts exactly. `cm_column_sums_match_gt = true` confirmed.

### Figure 3 normalized (`figure3_confusion_normalized_sidecar.json`)

Sidecar stores only orientation text (no numeric values to spot-check). Orientation `cm[pred,true]`
is consistent with both `figure3_confusion_counts_sidecar.json` and `metrics_final.json`.

### Figure 5 (`figure5_training_curves_sidecar.json`)

3 spot-checks of training curve values (source: results.csv, not metrics_final.json):

| Check | Value |
|-------|-------|
| Epoch list length | 100 entries (epochs 1–100) |
| Epoch 1 val_map50 | 0.00713 |
| Epoch 55 val_map50 | 0.90793 |
| Epoch 100 val_map50 | 0.92335 |

Sidecar is internally consistent (100 epochs, monotone overall trend, final value 0.92335 consistent
with published mAP50 of ~0.928). Note: figure5 is sourced from results.csv (not metrics_final.json);
the sidecar records a hash of results.csv.

---

## Overall Result

**PASS**

All 5 checks pass:

| Check | Result |
|-------|--------|
| 1. Recompute mAP50 | PASS — recomputed 0.928148, matches JSON exactly |
| 2. Cross-split copy check | PASS — all 120 merge-decision pairs are cross-split (expected); 49 test images excluded, matching JSON |
| 3. Numbers in .md vs JSON | PASS — no mismatches found in any of the 3 .md files |
| 4. Banned-strings check | PASS — none of the 5 banned strings appear anywhere in paper1/ |
| 5. Sidecar spot-checks | PASS — all spot-checked values match metrics_final.json |
