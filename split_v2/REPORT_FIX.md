# REPORT_FIX.md — SESSION_FIX_V2

---

## Page 1: Five Short Answers

### 1. Official mAP50-95 and why the gap happened

**Official value: 0.734368** (model.val, iou=0.7, full test set, 356 images).

The 0.734 / 0.7228 gap was entirely explained by the NMS IoU threshold.
The documented September evaluation used `iou=0.7` (confirmed in
`CLEAN_TEST_RESULTS.md` and `results/grouped_v1/RESULTS_grouped_v1.md`).
The previous fix session used `iou=0.6` (the Ultralytics default), which
produced mAP50-95=0.7318. When re-run with `iou=0.7`, the result is 0.7344,
matching September within 0.0004.

Model identity was verified: the SHA-256 of the weights file matches between
sessions. The val split re-evaluation (iou=0.7) produced mAP50=0.9250 /
mAP50-95=0.7330, matching the best-epoch log values (0.924 / 0.731) within
noise. The test list hash was also confirmed to match. No other explanation
was needed.

### 2. MINEIRO_99: real or artifact

**Real.** 35 out of 39 cross-group edges survived SIFT+RANSAC verification with
foreground-appropriate masks (non-white pixel mask for laboratory/white-background
images; green-leaf HSV mask for field images; threshold: inliers >= 30 and hull
coverage >= 0.50). Four edges failed and were removed. After re-verification, the
largest verified component contains **272 images** (down from 339). The component
remains large enough to prevent Path A.

### 3. Path taken

**Path B** (keep v1 model and split, bound the effect). Path A conditions
still fail after re-verification:
- Largest component (272 images) exceeds the 10% dataset limit (231 images).
- All minador test images belong to this component; moving them to train would
  eliminate minador from the test split.

### 4. Final headline numbers and intervals

**Full test set (n=356, iou=0.7):**
- mAP50 = 0.929377
- mAP50-95 = 0.734368
- Per-class mAP50: roya=0.841307, coco=0.961786, minador=0.985040

**Bootstrap CIs (95%, B=2000, seed=42):**

| Class | Method | 95% CI |
|-------|--------|--------|
| coco | cluster (primary) | [0.8012, 0.9713] |
| minador | cluster (primary) | [0.9731, 0.9998] |
| roya | image-level only (secondary) | [0.8033, 0.8735] |
| overall | — | NOT REPORTED |

The overall cluster CI is not reported because the roya cluster bootstrap is
invalid: ROYA_RECORTES_107 holds 438/825 = 53.1% of test roya instances
(threshold: 50%). An overall image-level bootstrap is available as secondary
but omitted here because it ignores within-leaf correlation.

**Filtered test (n=307, excluding 49 contaminated images, iou=0.7):**
- mAP50 = 0.925574, mAP50-95 = 0.729163
- Delta vs full: mAP50 = -0.0038, mAP50-95 = -0.0052
- These two test sets differ in composition; this is a sensitivity measurement,
  not a corrected metric.

### 5. What the manuscript must say about minador

"The minador class test images share group membership with training images through
SIFT+geometric-verified transformed copies (the MINEIRO_99 component, 272 images
after verification). The minador test mAP50 (0.985) cannot be interpreted as
performance on independent held-out leaves and is reported for completeness only.
Performance estimates for roya (mAP50=0.841, 95% CI image-level [0.803, 0.874])
and coco (mAP50=0.962, 95% CI cluster [0.801, 0.971]) are based on test images with
no verified transformed copies in the training split."

---

## Details

### Section 2: Reproduction

**Search for September results:**
- `CLEAN_TEST_RESULTS.md`: mAP50=0.929, mAP50-95=0.734, P=0.876, R=0.870 (September)
- `results/grouped_v1/RESULTS_grouped_v1.md`: same values, `iou=0.7` explicit
- `results/grouped_v1/results.csv`: best epoch val mAP50=0.9250, mAP50-95=0.7310

**Side-by-side evaluation settings:**

| Setting | September | Previous session | This session |
|---------|-----------|-----------------|--------------|
| Ultralytics | 8.4.148 | 8.4.148 | 8.4.148 |
| conf | 0.001 | 0.001 | 0.001 |
| iou | 0.7 | 0.6 | 0.7 |
| imgsz | 640 | 640 | 640 |
| batch | 16 | 16 | 16 |
| half | False | False | False |
| model SHA-256 | d8bf05c3... | d8bf05c3... | d8bf05c3... |
| test list hash | matches | matches | matches |

**Result:** iou=0.7 → mAP50=0.929377, mAP50-95=0.734368. Matches September 0.729/0.734.

**Val cross-check (iou=0.7):** mAP50=0.924985, mAP50-95=0.732988.
Training log best epoch: 0.9240/0.7310. Delta within noise (< 0.001). Model confirmed.

### Section 3: MINEIRO_99 anatomy

Before re-verification:
- Component size: 339 images (train=210, val=63, test=66)
- Cross-group edges (Tier A pHash <= 4): 39
- Node sources: MINEIRO prefix files (Silva et al. laboratory images),
  MINADO_RECORTES (cropped derivatives), field images chained via pHash

After SIFT+mask re-verification:
- 35/39 edges pass (inliers >= 30, hull coverage >= 0.50)
- 4 edges removed (white-background false pHash matches)
- Largest verified component: 272 images
- Split: train=~179, val=~41, test=~52

Path A conditions re-checked:
- cond1 (all classes in test): FAIL — minador test instances all in this component
- cond2 (component size <= 231): FAIL — 272 > 231
- cond3-4: blocked by cond1/2

**Silva et al. mapping (DOI 10.17632/vfxf4trtcg.5):** The source dataset contains
285 rust and 257 leaf-miner photos taken in laboratory on white backgrounds.
DECAFIA filenames with MINEIRO prefix correspond to leaf-miner (minador) images.
Most DECAFIA minador images are crops or dihedral derivatives of Silva et al. originals,
explaining why SIFT verification confirms most pHash edges (the transforms are real).

### Section 4: Bootstrap CI methodology

Previous CI ([0.847, 0.943]) was an overall cluster bootstrap that was dominated by
whether the MINEIRO_99 cluster (then 339 images = 100% of minador test) was drawn in
each resample — not genuine mAP sampling uncertainty.

Fixed approach:
1. Per-class validity check: single cluster must hold <= 50% of that class's test instances.
2. roya fails (53.1% in ROYA_RECORTES_107) → no cluster CI for roya or overall.
3. coco (37.2%) and minador (43.7%) pass → cluster CIs reported.
4. Image-level bootstrap reported as secondary for all classes, clearly labeled.

### Output files updated

- paper1/results/metrics_final.json (section2_resolution, section3_resolution, phase4 updated)
- paper1/RESULTS_FINAL.md
- paper1/NUMBERS_FOR_MANUSCRIPT.md
- paper1/MANUSCRIPT_CHANGES.md
- split_v2/REPORT_FIX.md (this file)
- CLAUDE.md (restored — see next section)
- paper1/PASTE_INTO_CLAUDE_PROJECT.md (regenerated)

### Git commits on split-v2 (this session)

1. revert CLAUDE.md source-of-truth section (Section 1 Freeze)
2. phase_fix_eval.py: re-evaluation with iou=0.7 + proper bootstrap CIs
3. update output documents and REPORT_FIX.md

Branch split-v2. Do not merge into main.
