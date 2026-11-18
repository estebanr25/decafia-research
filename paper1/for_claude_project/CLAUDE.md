# CLAUDE.md — DECAFIA Research Repository

This file tells Claude Code agents what the authoritative state of this project is.
Do not change the "Source of truth" section without running the full SESSION_FIX_V2
pipeline and passing Section 5 verification.

---

## Source of truth

**Last updated:** 2026-11-16 by SESSION_FIX_V2 pipeline (branch split-v2)

### Official model and split

| Item | Value |
|------|-------|
| Official model | `decafia_grouped_v1` (YOLOv8m, seed 42) |
| Official split | `split_grouped_v1` (1577 / 382 / 356) |
| Path chosen | **B** (keep v1, bound the effect) |
| NMS IoU setting | `iou=0.7` (documented September setting) |

Path A failed because:
- Component `MINEIRO_99` contains 272 images after SIFT+mask edge re-verification (still > 10% threshold).
- All minador test images belong to this component.
- Result: 0 minador instances in any feasible v2 test set.

### Official numbers (from paper1/results/metrics_final.json)

All numbers below are rendered from `paper1/results/metrics_final.json`.
Do NOT type numbers by hand; always read from JSON.

**Full v1 test set** (356 images, iou=0.7):

| Metric | Overall | roya | coco | minador |
|--------|---------|------|------|---------|
| mAP50 (model.val)  | 0.929377 | 0.841307 | 0.961786 | 0.985040 |
| mAP50-95 (model.val) | 0.734368 | 0.537046 | 0.794734 | 0.871323 |

**Bootstrap CIs (95%, B=2000, seed=42):**
- coco (cluster, primary): [0.8012, 0.9713]
- minador (cluster, primary): [0.9731, 0.9998]
- roya cluster CI: NOT REPORTABLE (53.1% in one cluster > 50% threshold)
- Overall cluster CI: NOT REPORTED (roya invalid)
- Image-level CIs (secondary only): roya [0.803, 0.874], coco [0.951, 0.974], minador [0.972, 0.991]

**Contamination sensitivity (Path B):**
- 49 v1 test images have a merged-tier copy in train or val
- Filtered test (307 images, excluding 49, iou=0.7): mAP50 = 0.925574 (delta = -0.0038)
- **These two test sets differ; this is a sensitivity measurement, not a corrected metric.**

### Superseded entries

- Previous session mAP50-95 = 0.722829 (full) / 0.726920 (filtered): **SUPERSEDED** — computed
  with iou=0.6 instead of documented iou=0.7. Use 0.734368 / 0.729163.
- Previous overall cluster CI [0.847, 0.943]: **SUPERSEDED** — was not validity-checked per class.
  Overall CI is not reportable (roya bootstrap invalid). Use per-class cluster CIs above.

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
7. The overall cluster CI is NOT reported. Use per-class cluster CIs for coco and minador.
8. Minador test performance caveat: minador test images share group membership with training images
   through verified transformed copies; mAP50=0.985 cannot be interpreted as performance on
   independent held-out leaves.
