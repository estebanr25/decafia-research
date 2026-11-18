# REPORT.md — SESSION_SPLIT_V2

## 1. Path taken and why

**Path B** (keep v1 model, bound the effect). Path A failed because the MINEIRO_99
image group contains 290 images (12.5% > 10% threshold), and all minador test images
belong to this group. Moving it to test would drift train proportion by 13 percentage
points, exceeding the 2pp tolerance. No feasible rebalancing exists that simultaneously
satisfies component-size, class-balance, and proportion constraints.

## 2. Final numbers (from paper1/results/metrics_final.json)

Official model: decafia_grouped_v1 (YOLOv8m, seed 42) on split_grouped_v1.

**Full v1 test set** (356 images):

| | overall | roya | coco | minador |
|-|---------|------|------|---------|
| mAP50 | 0.928148 | 0.839143 | 0.962144 | 0.983157 |
| mAP50-95 | 0.722829 | — | — | — |

95% CI mAP50 (cluster bootstrap, B=2000, seed=42): overall [0.847, 0.943]

**Contamination sensitivity:**
- 49 test images excluded (have merged-tier copy in train=28 or val-only=21)
- Filtered test (307 images): mAP50=0.926117, mAP50-95=0.726920
- Delta: -0.0021 mAP50, -0.0049 mAP50-95
- NOTE: two test sets differ; this is sensitivity, not a corrected metric.

## 3. What changed vs v1 and what the manuscript must say

The official model and numbers are unchanged from v1 (Path B). However the manuscript
must be updated to:
1. Remove "leakage-free" / "sin fuga" wording
2. Remove the sentence "no pair of images with a pHash distance of 4 or less remained across subsets"
3. Replace the residual-copy paragraph with the finding: 49 test images (13.8% of test) have
   dihedral pHash distance <= 4 to an image in train or val; sensitivity delta is -0.0021 mAP50
4. Resolve the per-class annotation percentages (see MANUSCRIPT_CHANGES.md)

See paper1/MANUSCRIPT_CHANGES.md for exact replacement text.

## 4. What Esteban must review

- **Contact sheets** (5 minutes): split_v2/contact_tier_a_cross.png (107 Tier A merged pairs),
  split_v2/contact_tier_b_merged.png (13 Tier B verified pairs),
  split_v2/contact_tier_b_rejected.png (40 rejected pairs sample)
- **Decisions taken without asking:**
  - Path B chosen because structural constraints prevent Path A (MINEIRO_99 group size)
  - 48 SANAS_NUEVAS <-> SANAS_SOCORRO cross-split pairs merged (all Tier A, d<=4)
  - Tier B: 13 merged, 176 rejected after SIFT+leaf-mask verification
  - bootstrap B=2000, seed=42, cluster primary (by group_root)

## 5. Next steps (unblocked)

**Zenodo v2.1.0 contents:**
- split_grouped_v1 stays as official (Path B)
- Add CORRECTIONS.md documenting the 49 contaminated test images
- Files: splits/grouped_v1/{train,val,test}.txt, assignments.csv, split_v2/v1_test_exclusion_list.csv
- Note: v2 split (split_v2/) is on branch split-v2 for reference but not the official split

**Hugging Face:**
- Weights file: decafia_grouped_v1_best.pt
- SHA-256: (see paper1/results/metrics_final.json phase4.model.sha256)

**Website:**
- RESULTS_FILE = paper1/results/metrics_final.json

**Do not merge into main. Esteban reviews the branch.**
