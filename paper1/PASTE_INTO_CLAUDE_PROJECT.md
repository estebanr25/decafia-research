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
(12.5% of dataset) cannot be assigned to the test split while keeping all three classes
represented and proportions within tolerance.

**Official numbers (from paper1/results/metrics_final.json):**

Full v1 test set (356 images, 158 backgrounds):
- mAP50 overall: 0.928148
- mAP50-95 overall: 0.722829
- mAP50 per class: roya=0.839143, coco=0.962144, minador=0.983157
- 95% CI (cluster bootstrap, B=2000): overall [0.847, 0.943]

Contamination sensitivity (Path B):
- 49 test images have transformed-copy matches in train/val
- Filtered test (307 images, excluding 49): mAP50 = 0.926117
- **Caveat: the two test sets differ; this measures sensitivity, not a corrected metric.**

**Rules that apply to all outputs:**
1. Never write "92.4%" or "76.6%" or "2,786".
2. coco = Curculionidae. Do not write Coccinellidae or Pseudococcidae.
3. All mAP values as decimals, not percentages.
4. Any sentence about test-set performance must state the contamination sensitivity finding.

---

## Files to re-upload to the claude.ai project

After running this pipeline, upload the following files:

| File | SHA-256 (first 12 chars) |
|------|--------------------------|
| paper1/results/metrics_final.json | 304ff8ad1e5f |
| paper1/figures/figure3_confusion_counts.png | 2536050bc698 |
| paper1/figures/figure7_bootstrap_intervals.png | e474bd566e1c |
| paper1/figures/figure5_training_curves.png | 41610ae045c9 |

Additionally useful:
- paper1/RESULTS_FINAL.md
- paper1/NUMBERS_FOR_MANUSCRIPT.md
- paper1/VERIFICATION.md
