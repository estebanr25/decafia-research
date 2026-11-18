# VERIFICATION_FIX.md

**Date:** 2026-11-17
**Verifier:** Independent (no prior pipeline participation)
**Source files checked:**
- `split_v2/phase_fix_log.txt`
- `paper1/results/metrics_final.json`
- `paper1/NUMBERS_FOR_MANUSCRIPT.md`
- `paper1/RESULTS_FINAL.md`
- `split_v2/REPORT_FIX.md`
- `CLAUDE.md`

---

## Check 1: mAP50 / mAP50-95 from evaluation log

**Result: PASS**

Log lines (second full run, lines 95–100):
```
model.val results (iou=0.7):
  mAP50=0.929377  mAP50-95=0.734368
  P=0.8762  R=0.8703
  roya: mAP50=0.841307 mAP50-95=0.537046
  coco: mAP50=0.961786 mAP50-95=0.794734
  minador: mAP50=0.985040 mAP50-95=0.871323
```

Tolerance checks:
- mAP50 = 0.929377; target 0.929 ± 0.0005 → |0.929377 - 0.929| = 0.000377 < 0.0005 **PASS**
- mAP50-95 = 0.734368; target 0.734 ± 0.001 → |0.734368 - 0.734| = 0.000368 < 0.001 **PASS**

Val cross-check (from JSON `section2_resolution`):
- `val_check_map50` = 0.924985 (~0.9250) **PASS**
- `val_check_map50_95` = 0.732988 (~0.7330) **PASS**
- `val_training_log_map50` = 0.924, `val_training_log_map50_95` = 0.731 — consistent with training log reference **PASS**

JSON `section2_resolution` match:
- `iou07_map50` = 0.929377 **PASS**
- `iou07_map50_95` = 0.734368 **PASS**

---

## Check 2: NMS iou setting documented

**Result: PASS (with note on data type)**

Log confirms `iou=0.7` used (lines 4 and 82: `Running model.val (iou=0.7, conf=0.001)`).

JSON `phase4.nms_iou_setting` = `0.7` as a **float**, not the string `"0.7"` as specified. The numeric value is correct (equals 0.7); the data type differs from the check specification. No semantic mismatch.

- `section2_resolution.gap_explained_by` = "NMS IoU threshold: September used iou=0.7, previous session used iou=0.6" — contains "iou" **PASS**
- `section2_resolution.iou07_map50_95` = 0.734368; target ~0.734 **PASS**
- `section2_resolution.iou06_map50_95` = 0.731766; target ~0.731 **PASS**

Note: The check specification states `nms_iou_setting == "0.7"` (string). The JSON stores this as numeric `0.7`. All downstream values are correct.

---

## Check 3: Bootstrap CI validity check

**Result: PASS**

From `phase4.test_set_full.bootstrap_map50_ci95.cluster_validity`:

| Class | can_report_cluster_ci | max_cluster_pct | Expected |
|-------|----------------------|-----------------|---------|
| roya | false | 53.09 | false, >50 |
| coco | true | 37.2 | true, <=50 |
| minador | true | 43.73 | true, <=50 |

- `overall_cluster_ci_reportable` = false **PASS**
- `per_class_cluster` keys present: `coco`, `minador` only (roya absent) **PASS**

Sanity checks (lo < mAP50 < hi):
- coco: lo=0.8012 < mAP50=0.961786 < hi=0.9713 **PASS**
- minador: lo=0.9731 < mAP50=0.985040 < hi=0.9998 **PASS**

---

## Check 4: Numbers in .md files vs JSON

**Result: PASS**

All numbers verified against `phase4.test_set_full` and `filtered_test` in `metrics_final.json`.

| Claim | .md value | JSON value | Match |
|-------|-----------|------------|-------|
| mAP50 overall (model.val) | 0.929377 | 0.929377 | PASS |
| mAP50-95 overall (model.val) | 0.734368 | 0.734368 | PASS |
| mAP50 roya | 0.841307 | 0.841307 | PASS |
| mAP50 coco | 0.961786 | 0.961786 | PASS |
| mAP50 minador | 0.985040 | 0.985040 | PASS |
| Filtered test mAP50 | 0.925574 | 0.925574 | PASS |
| Bootstrap CI coco lo | 0.8012 | 0.8012 | PASS |
| Bootstrap CI coco hi | 0.9713 | 0.9713 | PASS |
| Bootstrap CI minador lo | 0.9731 | 0.9731 | PASS |
| Bootstrap CI minador hi | 0.9998 | 0.9998 | PASS |
| Overall cluster CI | NOT REPORTED | NOT REPORTED (overall_cluster_ci_reportable=false) | PASS |

Both `NUMBERS_FOR_MANUSCRIPT.md` and `RESULTS_FINAL.md` state overall cluster CI is NOT REPORTED.
Both files correctly note roya CI is not reportable due to 53.1% single-cluster concentration.

---

## Check 5: Banned strings

**Result: PASS**

Searched `paper1/` (all .md and .json), `split_v2/REPORT_FIX.md`, and `CLAUDE.md`.

| String | Occurrences as content claims | Notes |
|--------|------------------------------|-------|
| "92.4%" | 0 | Found only as a prohibition rule in CLAUDE.md and PASTE_INTO_CLAUDE_PROJECT.md, and as a table entry "0 occurrences" in VERIFICATION.md |
| "76.6%" | 0 | Same — rule-statement only |
| "2,786" | 0 | Same — rule-statement only |
| "Coccinellidae" | 0 | Same — rule-statement only |
| "Pseudococcidae" | 0 | Same — rule-statement only |

No banned strings appear as factual claims in any manuscript-facing file.

---

## Overall Summary

| Check | Result | Key values confirmed |
|-------|--------|---------------------|
| 1: mAP50/mAP50-95 from log | **PASS** | 0.929377 / 0.734368; val cross-check 0.924985 / 0.732988 |
| 2: NMS iou=0.7 documented | **PASS** | iou=0.7 in log; JSON stores as float 0.7 (correct value) |
| 3: Bootstrap CI validity | **PASS** | roya not reportable (53.09%); coco/minador reportable; CIs bracket mAP50 |
| 4: .md numbers match JSON | **PASS** | All 11 checked values match exactly |
| 5: Banned strings absent | **PASS** | 0 occurrences as content claims |

**OVERALL: PASS**

No discrepancies found between the evaluation log, metrics_final.json, and the manuscript-facing .md files.
The one noted item (nms_iou_setting stored as float rather than string) has no effect on any reported number.
