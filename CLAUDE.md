# CLAUDE.md — DECAFIA Research Repository

This file tells Claude Code agents what the authoritative state of this project is.
Do not change the "Source of truth" section without running the full SESSION_SPLIT_V2
pipeline and passing Phase 5 verification.

---

## Source of truth

**Last updated:** 2026-11-16 by SESSION_SPLIT_V2 pipeline (branch split-v2)

### Official model and split

| Item | Value |
|------|-------|
| Official model | `decafia_grouped_v1` (YOLOv8m, seed 42) |
| Official split | `split_grouped_v1` (1577 / 382 / 356) |
| Path chosen | **B** (keep v1, bound the effect) |

Path A failed because:
- Component `MINEIRO_99` contains 290 images (12.5% > 10% threshold) — pre-existing v1 group size.
- Moving it to test would drift train proportion by 13pp (> 2pp tolerance).
- Result: 0 minador instances in any feasible v2 test set.

### Official numbers (from paper1/results/metrics_final.json)

All numbers below are rendered from `paper1/results/metrics_final.json`.
Do NOT type numbers by hand; always read from JSON.

**Full v1 test set** (356 images):

| Metric | Overall | roya | coco | minador |
|--------|---------|------|------|---------|
| mAP50  | 0.928148 | 0.839143 | 0.962144 | 0.983157 |
| mAP50-95 | 0.722829 | — | — | — |

mAP50 95% CI (cluster bootstrap, B=2000, seed=42): [0.847, 0.943]

**Contamination sensitivity (Path B):**
- 49 v1 test images have a merged-tier copy in train or val
- Filtered test (307 images, excluding 49): mAP50 = 0.926117 (delta = -0.0021)
- **These two test sets differ; this is a sensitivity measurement, not a corrected metric.**

### Superseded entries

- `decafia_grouped_v1 on split_grouped_v1`: **ACTIVE, with caveat** — 49 test images
  have transformed-copy matches in the training or validation splits (see
  `split_v2/v1_test_exclusion_list.csv`). The sensitivity delta is -0.0021 mAP50.
  Numbers in the manuscript must reflect this finding.

### Files that must NOT be modified

- `splits/grouped_v1/` — v1 split lists and assignments
- `C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_grouped_v1/` — v1 model
- Any raw dataset folder in decafia_clean

---

## Rules for agents

1. Never modify, move, or delete anything in the v1 split lists, the v1 model, or any raw dataset folder.
2. All reported numbers must be rendered from `paper1/results/metrics_final.json`.
3. Do not write "92.4%" or "76.6%" or "2,786" in any output.
4. Do not write "Coccinellidae" or "Pseudococcidae" for coco (coco = Curculionidae).
5. Write val mAP values as decimals (0.924), never as percentages.
6. The contamination sensitivity result must be stated in every output that discusses test-set performance.
