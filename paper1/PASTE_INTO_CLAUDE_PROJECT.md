# PASTE_INTO_CLAUDE_PROJECT.md

This file contains the exact replacement text for the claude.ai project instructions,
plus the list of files to re-upload.

---

## Replacement text for project instructions

Replace the section that currently says:
> "the only valid figures are those of decafia_grouped_v1 on split_grouped_v1"

With the following:

---

**Official model:** decafia_grouped_v1 (YOLOv8m, seed 42) on split_grouped_v1.

**Path B was chosen** (retrain was not completed). Reason: the MINEIRO_99 image group
(272 images after SIFT+mask geometric verification) cannot be assigned to the test split
while keeping all three classes represented and proportions within tolerance.

**Official numbers (from paper1/results/metrics_final.json, iou=0.7):**

Full v1 test set (356 images, 158 backgrounds):
- mAP50 overall: 0.929377
- mAP50-95 overall: 0.734368
- mAP50 per class: roya=0.841307, coco=0.961786, minador=0.985040

Confidence intervals (95%, cluster bootstrap, B=2000):
- coco: [0.8012, 0.9713]
- minador: [0.9731, 0.9998]
- roya: NOT REPORTABLE via cluster bootstrap (53.1% in one cluster); image-level secondary: [0.8033, 0.8735]
- **Overall CI: NOT REPORTED (roya cluster bootstrap invalid)**

Contamination sensitivity (Path B):
- 49 test images have transformed-copy matches in train/val
- Filtered test (307 images, excluding 49): mAP50 = 0.925574
- **Caveat: the two test sets differ; this measures sensitivity, not a corrected metric.**

**Rules that apply to all outputs:**
1. Never write "92.4%" or "76.6%" or "2,786".
2. coco = Curculionidae. Do not write Coccinellidae or Pseudococcidae.
3. All mAP values as decimals, not percentages.
4. Any sentence about test-set performance must state the contamination sensitivity finding.
5. Do not report an overall cluster CI. Report per-class cluster CIs for coco and minador.
6. Minador test performance caveat: test images share group membership with training images
   through verified transformed copies; mAP50=0.985 cannot be interpreted as performance
   on independent held-out leaves.

---

## Files to re-upload to the claude.ai project

After running this pipeline, upload the following files:

| File | SHA-256 (first 12 chars) |
|------|--------------------------|
| paper1/results/metrics_final.json | bc4fbb2b09d6 |
| paper1/figures/figure3_confusion_counts.png | (unchanged — recheck) |
| paper1/figures/figure7_bootstrap_intervals.png | (regenerated — recheck) |
| paper1/figures/figure5_training_curves.png | (unchanged) |

Additionally useful:
- paper1/RESULTS_FINAL.md
- paper1/NUMBERS_FOR_MANUSCRIPT.md
- paper1/MANUSCRIPT_CHANGES.md
- paper1/VERIFICATION.md
- split_v2/REPORT_FIX.md
