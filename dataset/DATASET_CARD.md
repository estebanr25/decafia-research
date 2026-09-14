# DECAFIA Clean Dataset Card

**Generated:** 2026-09-11  
**Source:** `01_dataset/decafia_yolo_original/`  
**Split seed:** 42  
**Split ratio:** 70 / 15 / 15 (stratified by class-presence signature)

---

## 1. Image and Annotation Counts

| Split | Images | Roya ann. | Coco ann. | Minador ann. | Total ann. | Background imgs |
|-------|-------:|----------:|----------:|-------------:|-----------:|----------------:|
| train | 1618 | 3433 | 3883 | 1634 | 8950 | 779 |
| val | 348 | 723 | 807 | 366 | 1896 | 167 |
| test | 349 | 864 | 699 | 385 | 1948 | 167 |
| **TOTAL** | **2315** | **5020** | **5389** | **2385** | **12794** | **1113** |

*Class IDs: 0 = roya, 1 = coco, 2 = minador.*  
*Background images carry empty label files (healthy-leaf examples).*

---

## 2. Source x Class Breakdown

Instance counts after class-ID remapping, summed across all splits.

| Source | Roya | % of roya | Coco | % of coco | Minador | % of minador | Total instances |
|--------|-----:|----------:|-----:|----------:|--------:|-------------:|----------------:|
| own_field | 3013 | 60.0% | 5389 | 100.0% | 0 | 0.0% | 8402 |
| rust_and_leaf_miner | 2007 | 40.0% | 0 | 0.0% | 2385 | 100.0% | 4392 |
| **TOTAL** | **5020** | 100% | **5389** | 100% | **2385** | 100% | **12794** |

**Key observations:**

- **Coco** (5389 annotations): 100% own_field images from Socorro, Santander. No coco annotations exist in any external dataset used here.
- **Minador** (2385 annotations): 100% from Silva et al. (rust and leaf miner). This means minador performance measures *cross-country generalisation* (Brazil training conditions vs. Colombian deployment) rather than in-field Colombian performance.
- **Roya** (5020 annotations): 60.0% own_field, 40.0% Silva et al. The majority of roya annotations come from the external dataset; own-field roya coverage is limited.

---

## 3. Exclusion Rules and Rationale

### Excluded: RoCoLe subset

| Prefix | Images excluded | Reason |
|--------|----------------:|--------|
| SANAS_ROCOLE | 454 | Laboratory white-background images; domain mismatch; source of all 5 SHA256 cross-split duplicates |

RoCoLe (Parraga-Alava et al., DOI 10.17632/c5yvn32dzg.2) provides only healthy-leaf images photographed against a plain white background under controlled conditions. This distribution does not match Socorro field conditions. Own-field healthy images (SANAS_NUEVAS, SANAS_SOCORRO) are retained instead.

### Cross-source outlier removed

One spurious coco annotation was deleted from `labels/test/MINEIRO_111.txt` (33x31 px box in a 448x960 image). Coco is absent from the Silva et al. class schema; this was a labelling artefact. See `CORRECTIONS.md`.

### Class 'sano' is NOT a detection class

Healthy leaves appear as **background images with empty label files**. The model predicts 3 classes only: roya, coco, minador.

At inference time the system reports a leaf as healthy by the **absence of detections above the confidence threshold (0.50)**. No bounding box is predicted for healthy tissue and no fabricated 'sano' confidence score is emitted.

Background images (empty label files): **1113** (48.1% of dataset).

---

## 4. Attribution

### Silva et al. — rust and leaf miner (used in this dataset)

> Brito Silva, Lucas, et al.
> *Dataset of images for training artificial intelligence models to detect
> coffee leaf rust and leaf miner.*
> Mendeley Data, V5.
> DOI: [10.17632/vfxf4trtcg.5](https://doi.org/10.17632/vfxf4trtcg.5)
> License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Contributes images under prefixes: ROYA_FONDO, ROYA_MA, ROYA_Muy_A, ROYA_P_A,
ROYA_RECORTES, MINADOR, MINADO_RECORTES, MINEIRO.

### Own-field images (used in this dataset)

Collected by Andrey Salom and Esteban Rosas in coffee farms in Socorro,
Santander, Colombia. Not publicly released separately. Available here under
CC BY 4.0.

Prefixes: SANAS_NUEVAS, SANAS_SOCORRO, COCO_RECORTE, COCO_M_A, COCO_Muy_A,
COCO_P_A, ROYA_P_A, ROYA_MA, ROYA_Muy_A.

### RoCoLe (excluded)

> Parraga-Alava, Jorge, et al.
> *RoCoLe: A Robusta Coffee Leaf Images Dataset.*
> Mendeley Data, V2.
> DOI: [10.17632/c5yvn32dzg.2](https://doi.org/10.17632/c5yvn32dzg.2)
> License: CC BY 4.0

Excluded from `decafia_clean`. Preserved in `decafia_yolo_original/`.

---

## 5. Class ID Mapping

| Original ID | New ID | Class | Notes |
|:-----------:|:------:|-------|-------|
| 0 | 0 | roya | unchanged |
| 1 | 1 | coco | unchanged |
| 3 | 2 | minador | remapped from 3 |
| 2 | — | sano | background; no label emitted |

---

## 6. File Layout

```
decafia_clean/
  data.yaml           # nc=3, names=[roya, coco, minador]
  DATASET_CARD.md     # this file
  CORRECTIONS.md      # log of post-build annotation deletions
  images/
    train/  val/  test/
  labels/
    train/  val/  test/   # YOLO format; empty = background (healthy leaf)
```