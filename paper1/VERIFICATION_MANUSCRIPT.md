# VERIFICATION_MANUSCRIPT.md

Independent verification report.
Verifier has not participated in the pipeline that produced these results.
Verification date: 2026-11-17.

---

## Check 1: Minador CI marked as not reported

**Result: PASS**

Findings:

- `paper1/results/metrics_final.json` — `phase4.test_set_full.bootstrap_map50_ci95.per_class_cluster.minador.reported` is `false`. A `reported_reason` field is present with the full explanation: minador test images share group membership with training images through SIFT+geometric-verified transformed copies (MINEIRO_99 component, 272 images); mAP50=0.985 cannot be interpreted as performance on independent held-out leaves.
- `NUMBERS_FOR_MANUSCRIPT.md` — Under "Notes on CIs", minador cluster CI is explicitly marked "NOT REPORTED IN MANUSCRIPT" with the same contamination rationale. The numbers table row for overall CI reads "NOT REPORTED (roya: 53.1% single cluster; minador: contaminated)".
- `RESULTS_FINAL.md` — Bootstrap CI table row for minador reads: lo=(0.9731), hi=(0.9998), Reportable? = "NOT REPORTED (contaminated)".
- `FIGURES.md` — Figure 7 caption states: "minador: 0.985 — CI not shown (test images share group membership with training images through verified transformed copies; independent-leaf evaluation not possible)." Minador bar is described as a point estimate only with a dagger symbol.

All four sub-conditions satisfied.

---

## Check 2: Roya cluster check documented

**Result: PASS**

Findings:

Both `NUMBERS_FOR_MANUSCRIPT.md` (section "Roya source analysis (Phase 1.3 check)") and `RESULTS_FINAL.md` (section "95% Bootstrap CIs", Phase 1.3 check paragraph) contain the following statements:

1. ROYA_RECORTES_107 does NOT overlap the MINEIRO_99 verified component.
2. The specific edge MINADOR_50 — ROYA_FONDO_35 fails SIFT verification (4 inliers, 0.23 hull coverage — both below threshold), as stated in NUMBERS_FOR_MANUSCRIPT.md; RESULTS_FINAL.md states "4 inliers".
3. The conclusion that roya test images are not contaminated — the roya cluster CI is unreportable solely because of cluster size, not data contamination.

All three sub-conditions satisfied.

---

## Check 3: Numbers in NUMBERS_FOR_MANUSCRIPT.md match metrics_final.json

**Result: PASS**

Each value was compared against `phase4.test_set_full` (and `filtered_test`) in `metrics_final.json`.

| Claim | Expected | NUMBERS_FOR_MANUSCRIPT.md | Match? |
|-------|----------|---------------------------|--------|
| mAP50 overall | 0.929377 | 0.929377 | YES |
| mAP50-95 overall | 0.734368 | 0.734368 | YES |
| mAP50 roya | 0.841307 | 0.841307 | YES |
| mAP50 coco | 0.961786 | 0.961786 | YES |
| mAP50 minador | 0.985040 | 0.985040 | YES |
| coco cluster CI lo | 0.8012 | 0.8012 | YES |
| coco cluster CI hi | 0.9713 | 0.9713 | YES |
| roya image-level CI lo | 0.8033 | 0.8033 | YES |
| roya image-level CI hi | 0.8735 | 0.8735 | YES |
| filtered test mAP50 | 0.925574 | 0.925574 | YES |

All 10 values match exactly.

---

## Check 4: Figure 7 sidecar updated

**Result: PASS**

File: `paper1/figures/figure7_bootstrap_intervals_sidecar.json`

| Field | Expected | Actual | Match? |
|-------|----------|--------|--------|
| ci95_minador | "NOT REPORTED" (not numeric) | "NOT REPORTED (contaminated)" | YES |
| ci95_coco_cluster.lo | 0.8012 | 0.8012 | YES |
| ci95_coco_cluster.hi | 0.9713 | 0.9713 | YES |
| ci95_roya_image_level_secondary.lo | 0.8033 | 0.8033 | YES |
| ci95_roya_image_level_secondary.hi | 0.8735 | 0.8735 | YES |
| generated | 2026-11-18 | 2026-11-18 | YES |

All six sub-conditions satisfied. The ci95_minador value is a non-numeric string ("NOT REPORTED (contaminated)"), confirming it is not a numeric interval.

---

## Check 5: Banned strings

**Result: PASS**

Searched `paper1/` for the strings: "92.4%", "76.6%", "2,786", "Coccinellidae", "Pseudococcidae".

Grep results:

| String | Files with match | Content-claim occurrences |
|--------|-----------------|--------------------------|
| 92.4% | 3 | 0 |
| 76.6% | 3 | 0 |
| 2,786 | 3 | 0 |
| Coccinellidae | 3 | 0 |
| Pseudococcidae | 3 | 0 |

All matches are in prohibition-rule sentences (`PASTE_INTO_CLAUDE_PROJECT.md`) or in table rows from prior verification files (`VERIFICATION.md`, `VERIFICATION_FIX.md`) that themselves record "0 occurrences." No banned string appears as a content claim in any manuscript-facing document.

---

## Overall Verdict: PASS

All 5 checks passed. The manuscript-facing documents are internally consistent with `metrics_final.json`. The minador CI is correctly suppressed with documented rationale. The roya cluster contamination check is fully documented in two independent files. All numerical values match their JSON source exactly. The figure sidecar reflects the correct non-numeric minador CI and correct numeric CI values for coco and roya. No banned strings appear as content claims.
