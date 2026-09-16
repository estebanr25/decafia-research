# Near-Duplicates Audit — Exploratory Trail

This folder contains the **exploratory audit trail** produced while investigating
cross-split leakage in the DECAFIA clean dataset. It is preserved for reproducibility
but several conclusions have been superseded.

**Authoritative results are in:**
- [`splits/grouped_v1/SPLIT_README.md`](../../splits/grouped_v1/SPLIT_README.md) — final split method, grouping rules, crop-parent results, orphan handling
- [`results/grouped_v1/RESULTS_grouped_v1.md`](../../results/grouped_v1/RESULTS_grouped_v1.md) — per-class test metrics, background FP analysis, baseline comparison

---

## Known Errors / Superseded Conclusions

### 1. `SESSION_FEASIBILITY.md` and `crop_parent_map.csv` — crop-parent cross-split rate

**Claimed:** "405/405 crop-parent pairs cross-split (100%)"

**Why it is wrong:** This figure is an artifact of the search design: only cross-split
candidates were passed to the SIFT crop-parent pipeline, so 100% cross-split is a
tautology, not a finding. Inspection showed that 345 of those 405 rows were SANAS
images, not crops — they were included by mistake.

**Superseded by:** `splits/grouped_v1/crop_parent_map_full.csv`
— 176 valid crop-parent pairs after full search (inliers ≥ 30, containment ≥ 0.80):
92 same-split, 84 different-split; 222 orphan crops (no parent found).

### 2. `REPORT.md` — "within-split SIFT inliers ≥ 15: 0"

**Claimed / implied:** Zero within-split SIFT-verified pairs.

**Why it is wrong:** Within-split candidates were never evaluated — only cross-split
candidates were submitted to SIFT geometric verification. The value 0 means
NOT EVALUATED, not zero verified pairs.

### 3. Session-based split — abandoned

The session-based split strategy (grouping images by EXIF timestamp windows) was
abandoned because **no image in this dataset has EXIF metadata**. The final grouped
split instead uses filename-number blocks (floor(number / B)) combined with
crop-parent union-find links and pHash ≤ 4 near-duplicate edges.
See `splits/grouped_v1/SPLIT_README.md` for the full method.
