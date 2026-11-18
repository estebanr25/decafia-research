# DECAFIA — CoffeeLeaf-CO
## Dataset Card / README — v2.1.0

**Full title:** DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease
Detection Under Colombian Andean Conditions (CoffeeLeaf-CO)

**Version:** 2.1.0
**Concept DOI:** https://doi.org/10.5281/zenodo.19931903
**v2.1.0 DOI:** [PEGAR DOI ZENODO v2.1.0]
**License:** CC BY 4.0
**Date:** November 2026

---

## Overview

DECAFIA is a multi-source, field-collected, annotated dataset for coffee leaf disease
detection. It provides instance-level bounding-box annotations for three foliar conditions
simultaneously under Colombian Andean field conditions.

| Property | Value |
|----------|-------|
| Total images | 2,315 (annotated) + 1,113 (background, no annotations) |
| Total instances | 12,794 bounding-box annotations |
| Classes | 3 (roya, coco, minador) |
| Annotation format | YOLO normalized bounding boxes |
| Split strategy | Grouped by leaf (split_grouped_v1) |

---

## Classes

| ID | Label | Scientific name | Local name | Description |
|----|-------|----------------|-----------|-------------|
| 0 | roya | *Hemileia vastatrix* | roya | Coffee leaf rust — orange-yellow urediniospore pustules on abaxial leaf surface |
| 1 | coco | Curculionidae (*Compsus* sp. / *Epicaerus* sp.) | coco / vaquita | Weevil defoliation damage — irregular through-perforations with brown necrotic margins |
| 2 | minador | *Leucoptera coffeella* | minador | Leaf-miner damage — serpentine mines on adaxial leaf surface |

**Note on coco class:** The 'coco' label refers specifically to weevil (Curculionidae)
defoliation damage, not to other Coleoptera families. The Curculionidae assignment is
based on field morphological consistency with Cenicafé reference materials; formal
entomological specimen collection was not conducted.

---

## Dataset Composition

| Split | Images | Background | Roya instances | Coco instances | Minador instances |
|-------|--------|-----------|---------------|----------------|------------------|
| Train | 1,577  | 798       | 3,321         | 3,746          | 1,621            |
| Val   | 382    | 157       | 874           | 823            | 389              |
| Test  | 356    | 158       | 825           | 820            | 375              |
| **Total** | **2,315** | **1,113** | **5,020** | **5,389** | **2,385** |

---

## Image Sources

| Source | Prefix(es) | Country | Conditions | License | Attribution |
|--------|-----------|---------|-----------|---------|-------------|
| Original field collection | COCO_*, ROYA_*, SANAS_SOCORRO_*, SANAS_NUEVAS_*, REFLEJO_* | Colombia (El Socorro, Santander) | Field (uncontrolled) | CC BY 4.0 (new) | Rosas Ruiz & Salom Medina, UIS, 2024 |
| Silva et al. 2020 (re-annotated) | MINEIRO_* | Brazil | Laboratory (white background) | CC BY 4.0 (redistributed) | doi:10.17632/vfxf4trtcg.5 |

---

## Split Strategy

The split uses `split_grouped_v1`: images are grouped by leaf identifier (group_root),
and all images in the same group are assigned to the same split. This prevents
crop-parent pairs and capture-series frames from crossing split boundaries.

**Important — Integrity Audit Results (see CORRECTIONS.md):**

A post-hoc integrity audit identified 49 test images (13.8%) with geometrically verified
transformed copies in the training split. These are listed in
`split_grouped_v1/v1_test_exclusion_list.csv`.

The largest affected component (272 images, MINEIRO_99) comprises laboratory leaf-miner
images from Silva et al. All minador test images belong to this component.
**mAP@0.50 = 0.985 for minador cannot be interpreted as performance on independent held-out leaves.**

---

## Baseline Model — decafia_grouped_v1

| Metric | Value | Notes |
|--------|-------|-------|
| Architecture | YOLOv8m | Ultralytics 8.4.148 |
| mAP@0.50 | 0.929 | Full 356-image test set, NMS IoU = 0.7 |
| mAP@0.50:0.95 | 0.734 | Full 356-image test set |
| Roya mAP@0.50 | 0.841 | 95% image-level CI: [0.803, 0.874] (secondary) |
| Coco mAP@0.50 | 0.962 | 95% cluster CI: [0.801, 0.971] |
| Minador mAP@0.50 | 0.985† | No CI reported (see caveat above) |
| mAP@0.50 (filtered) | 0.926 | 307-image filtered test (49 affected excluded); sensitivity check only |

Model weights: [PEGAR URL HUGGING FACE]
SHA-256: d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a

---

## Attribution

If you use DECAFIA, please cite:

> L. E. Rosas Ruiz, "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf
> Disease Detection Under Colombian Andean Conditions," *Ingeniería e Investigación*,
> [year], doi: [ARTICLE DOI WHEN PUBLISHED].

For the Silva et al. derived images (MINEIRO_* prefix), also cite:

> L. B. Silva, A. L. C. Carneiro, and M. S. A. R. Faulin, "Rust and leaf miner in
> coffee crop (Coffea arabica)," Mendeley Data, V5, 2020,
> doi: 10.17632/vfxf4trtcg.5.

---

## Code

Training, evaluation, and audit scripts: https://github.com/estebanr25/decafia-research

---

## Contact

Luis Esteban Rosas Ruiz
Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)
Universidad Industrial de Santander, Bucaramanga, Colombia
luis.rosas@correo.uis.edu.co | ORCID: 0000-0003-0233-6336
