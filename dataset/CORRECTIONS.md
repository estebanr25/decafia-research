# DATASET_CORRECTIONS

## 2026-09-11 — Deleted spurious coco annotation from MINEIRO_111.txt (test split)

**File:** `labels/test/MINEIRO_111.txt`
**Deleted line:** `1 0.65625 0.825 0.071429 0.033333`
**Class deleted:** 1 (coco / Curculionidae)
**Bounding box size:** approx. 33 × 31 px in a 448 × 960 image

**Reason:**
MINEIRO images originate from the Silva et al. "rust and leaf miner" dataset
(DOI 10.17632/vfxf4trtcg.5). That dataset contains only roya (rust) and
minador (leaf miner) damage — Curculionidae (coco) is absent from its class
schema. The 33 × 31 px bounding box at image position (277, 776)–(310, 807)
is consistent with a mislabelled annotation artefact, not a genuine coco
infestation documented in the source dataset.

The image (`images/test/MINEIRO_111.jpg`) and all remaining annotations
(minador / class 2) are retained unchanged.
