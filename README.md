# DECAFIA — Coffee Leaf Disease Detection (YOLOv8m)

YOLOv8m object detector for three coffee crop threats under Colombian Andean
field conditions. Trained on images collected at *Coffea arabica* plantations
in El Socorro, Santander, Colombia, supplemented with the Silva et al.
rust-and-leaf-miner dataset.

**GitHub:** [estebanr25/decafia-research](https://github.com/estebanr25/decafia-research)
**Live demo:** <https://decaf-ia.netlify.app>
**Dataset DOI:** [10.5281/zenodo.19931903](https://doi.org/10.5281/zenodo.19931903) (concept DOI — always resolves to the latest version)
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## Getting started

```bash
# 1. Clone
git clone https://github.com/estebanr25/decafia-research.git
cd decafia-research

# 2. Install dependencies
pip install -r requirements_training.txt

# 3. Download the dataset from Zenodo and extract it
#    DOI: https://doi.org/10.5281/zenodo.19931903
#    Extract so that the following path exists:
#      dataset/decafia_clean/images/{train,val,test}/
#      dataset/decafia_clean/labels/{train,val,test}/

# 4. Download the YOLOv8m base weights (auto-downloaded by ultralytics,
#    or place manually at models/checkpoints/yolov8m.pt)
mkdir -p models/checkpoints
python -c "from ultralytics import YOLO; YOLO('yolov8m.pt')" && \
  mv yolov8m.pt models/checkpoints/yolov8m.pt

# 5. Train
python scripts/train_clean.py
# Trained weights are saved to runs/decafia_clean_v1/weights/best.pt
# and copied to models/decafia_clean_best.pt

# 6. Evaluate on the test split
python scripts/evaluate_clean.py
# Figures and RESULTS.md are written to results/clean_v1/

# 7. Regenerate paper figures from saved arrays (no GPU needed)
python scripts/_regen_figures.py
```

If you already have trained weights, pass them explicitly to the evaluation script:

```bash
python scripts/evaluate_clean.py --model /path/to/decafia_clean_best.pt
```

---

## Detection classes

The model predicts **three classes only**:

| ID | Class | Pathogen / agent | Common name |
|---:|-------|-----------------|-------------|
| 0 | `roya` | *Hemileia vastatrix* | Coffee leaf rust |
| 1 | `coco` | Curculionidae weevil (*Compsus* sp. / *Epicaerus* sp.) | Weevil defoliation |
| 2 | `minador` | *Leucoptera coffeella* | Coffee leaf miner |

**Healthy leaves are not a detection class.** There is no `sano` class and no
`hojas` class in this release. Healthy (background) leaf images are represented
as images with **empty label files**. At inference time, a healthy verdict is
derived from the **absence of any detection above the confidence threshold
(0.50)**; no bounding box and no fabricated class score is emitted for healthy
tissue.

---

## Dataset

### Summary

| Split | Images | Roya ann. | Coco ann. | Minador ann. | Total ann. | Background imgs |
|-------|-------:|----------:|----------:|-------------:|-----------:|----------------:|
| train | 1,618 | 3,433 | 3,883 | 1,634 | 8,950 | 779 |
| val | 348 | 723 | 807 | 366 | 1,896 | 167 |
| test | 349 | 864 | 699 | 385 | 1,948 | 167 |
| **Total** | **2,315** | **5,020** | **5,389** | **2,385** | **12,794** | **1,113** |

Split ratio: 70/15/15, stratified by class-presence signature, seed = 42.
Background images (empty label files): **1,113 of 2,315 = 48.1%**.

### Provenance

**Own-field collection — El Socorro, Santander, Colombia (1,705 images)**

Collected by Andrey Salom and Luis Esteban Rosas at *Coffea arabica* farms
in El Socorro, Santander. Available under CC BY 4.0.

Image prefixes: `SANAS_NUEVAS`, `SANAS_SOCORRO`, `COCO_RECORTE`, `COCO_M_A`,
`COCO_Muy_A`, `COCO_P_A`, `ROYA_P_A`, `ROYA_MA`, `ROYA_Muy_A`

**Silva et al. — rust and leaf miner dataset (610 images)**

> Brito Silva, Lucas, et al.
> *Dataset of images for training artificial intelligence models to detect
> coffee leaf rust and leaf miner.*
> Mendeley Data, V5. DOI: [10.17632/vfxf4trtcg.5](https://doi.org/10.17632/vfxf4trtcg.5)
> License: CC BY 4.0

Image prefixes: `ROYA_FONDO`, `ROYA_RECORTES`, `MINEIRO`, `MINADO_RECORTES`,
`MINADOR`

**RoCoLe — EXCLUDED (454 images, not part of this release)**

> Parraga-Alava, Jorge, et al.
> *RoCoLe: A Robusta Coffee Leaf Images Dataset.*
> Mendeley Data, V2. DOI: [10.17632/c5yvn32dzg.2](https://doi.org/10.17632/c5yvn32dzg.2)

Image prefix: `SANAS_ROCOLE`

RoCoLe was excluded to preserve it as an independent external validation set.
Exclusion also removed 5 SHA256 duplicate pairs found in the original splits,
including 3 train/test cross-split leaks.

### Per-class source breakdown

| Source | Roya | Coco | Minador | Total instances |
|--------|-----:|-----:|--------:|----------------:|
| Own field | 3,013 (60.0%) | 5,389 (100%) | 0 (0%) | 8,402 |
| Silva et al. | 2,007 (40.0%) | 0 (0%) | 2,385 (100%) | 4,392 |
| **Total** | **5,020** | **5,389** | **2,385** | **12,794** |

By image count, roya images are 52.6% own field / 47.4% Silva et al.
(241 and 217 images respectively, out of 458 roya-containing images;
derived from `01_dataset/provenance_manifest.csv`).

Key implications:
- **Coco** performance reflects Colombian field conditions directly (100%
  own-field images from El Socorro).
- **Minador** performance measures cross-country generalisation — all minador
  annotations come from Brazil (Silva et al.), not from Colombian field images.
- **Roya** performance is a mix: majority own-field by annotation count,
  roughly equal by image count.

---

## Results — TEST split (349 images, 1,948 instances)

### Per-class metrics

| Class | Precision | Recall | F1 | mAP50 | mAP50-95 |
|-------|----------:|-------:|---:|------:|---------:|
| roya | 0.8364 | 0.7931 | 0.8142 | 0.8619 | 0.5700 |
| coco | 0.9177 | 0.9087 | 0.9132 | 0.9638 | 0.7921 |
| minador | 0.8687 | 0.8987 | 0.8834 | 0.9449 | 0.8258 |
| **all** | | | | **0.9235** | **0.7293** |

Metrics are computed at the F1-optimal confidence threshold per class.

### Background-image detection rate (conf >= 0.50)

Of the 167 background test images (healthy-leaf images with empty label files):

| Result | Count | Fraction |
|--------|------:|---------:|
| Zero detections (correct) | 164 | 98.2% |
| One or more detections (FP) | 3 | 1.8% |
| Total FP detections | 4 | — |

At the operational threshold (conf >= 0.50), the model suppresses spurious
detections on healthy tissue in 98.2% of cases. This supports the
three-class + background design: a healthy verdict is reliable under
normal field conditions.

### Figures (in `results/clean_v1/`)

| File | Description |
|------|-------------|
| `training_curves.png` | 4-panel: train box loss, val mAP50, val precision, val recall |
| `confusion_matrix_normalized.png` | Column-normalised confusion matrix; background row/col blank |
| `pr_curves.png` | Precision-recall curves per class, 300 dpi |
| `test_predictions_grid.png` | 4x4 random test predictions (conf >= 0.25) |

Full confusion-matrix notes and interpretation are in
`results/clean_v1/RESULTS.md`.

---

## Reproducibility

| Parameter | Value |
|-----------|-------|
| Model | YOLOv8m |
| Epochs | 100 (early-stop patience 20) |
| Image size | 640 |
| Batch | 16 |
| Optimizer | AdamW |
| LR schedule | lr0=0.01, lrf=0.001, linear decay (cos_lr=false; final lr = 1e-5) |
| Seed | 42 (random, numpy, torch, cuda) |
| `workers` | 0 (mandatory on Windows) |
| Augmentation | mosaic=1.0, mixup=0.15, hsv, flip, degrees=15, scale=0.5 |
| Hardware | NVIDIA RTX 5070 Laptop GPU (Blackwell sm_120, 8 GB VRAM) |
| Wall-clock time | 1 h 21 m 7 s (4867.66 s; from `results.csv` `time` column, epoch 100) |
| Python | 3.14 |
| ultralytics | 8.4.148 |
| PyTorch | 2.11.0+cu128 |
| CUDA | 12.8 |

Full dependency list: [`requirements_training.txt`](requirements_training.txt)

Training script: [`02_training/scripts/train_clean.py`](02_training/scripts/train_clean.py)
Config: [`02_training/configs/clean_v1.yaml`](02_training/configs/clean_v1.yaml)
Evaluation script: [`02_training/scripts/evaluate_clean.py`](02_training/scripts/evaluate_clean.py)

The trained model weights are at `03_models/decafia_clean_best.pt`
(YOLOv8m PyTorch checkpoint). An ONNX export for mobile inference is
available in `03_models/`.

> **Note on `workers=0`:** This is mandatory on Windows. Omitting it causes
> a paging-file crash during DataLoader multiprocessing. The setting has no
> effect on model quality.

---

## Superseded results

Earlier releases of this repository reported **mAP50 = 92.4% / mAP50-95 = 76.6%**
on a 2,786-image four-class dataset. Those figures are superseded and should
not be cited. They came from a dataset with three known problems:

1. **Cross-split SHA256 duplicate leakage** — 3 image pairs appeared in both
   train and test splits (all from the RoCoLe subset).
2. **Declared class with zero annotated instances** — the `sano` class was
   listed in `data.yaml` but carried no bounding-box annotations; healthy
   leaves were background images. Because Ultralytics excludes classes with
   no instances from the mAP mean, the reported mAP was an average over three
   classes (roya, coco, minador), not four.
3. **Domain contamination** — RoCoLe white-background lab photographs were
   mixed with field images, producing training and evaluation distributions
   that do not reflect Colombian farm conditions.

The figures in the Results section above are from the clean dataset
(`decafia_clean`, this release) with all three problems resolved.

---

## Authors

**Luis Esteban Rosas Ruiz** — lead author ([@estebanr25](https://github.com/estebanr25))
**Andrey Fernando Salom Medina** — co-author
**Prof. Jaime Guillermo Barrero Pérez** — director

*Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones*
*Universidad Industrial de Santander (UIS) · Bucaramanga, Colombia*

---

## Citation

<!-- TODO: replace with final citation once dataset descriptor and/or preprint are published -->

```bibtex
@misc{rosas2026decafia,
  author    = {Rosas Ruiz, Luis Esteban and Salom Medina, Andrey Fernando
               and Barrero Pérez, Jaime Guillermo},
  title     = {{DECAFIA}: {YOLOv8m} coffee leaf disease detector
               trained on Colombian field images},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/estebanr25/decafia-research}
}
```

---

## License

This dataset and model are released under the
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
licence. See [`LICENSE`](LICENSE) for the full text.

> **Note:** the `LICENSE` file at the repo root is an MIT licence covering the
> code and scripts in this repository. The dataset (images and annotations) is
> separately covered by CC BY 4.0 as stated above.

The Silva et al. subset is used under its original CC BY 4.0 licence
([DOI 10.17632/vfxf4trtcg.5](https://doi.org/10.17632/vfxf4trtcg.5)).
The RoCoLe subset is **not** redistributed in this release.

---

## Related repositories

| Repository | Contents |
|------------|----------|
| [estebanr25/decafia-research](https://github.com/estebanr25/decafia-research) | **This repo** — dataset pipeline, training scripts, evaluation, paper figures |
| [estebanr25/decafia-model](https://github.com/estebanr25/decafia-model) | WhatsApp chatbot + ONNX inference server (production deployment) |
| [estebanr25/decafia-app](https://github.com/estebanr25/decafia-app) | Flutter Android app for offline on-device inference |
| [estebanr25/decafia-landing](https://github.com/estebanr25/decafia-landing) | Project website — <https://decaf-ia.netlify.app> |
| [estebanr25/decafia-webcam](https://github.com/estebanr25/decafia-webcam) | Browser-based webcam demo |

> **Note:** [estebanr25/decafia](https://github.com/estebanr25/decafia) is the
> archived 2024 Mask R-CNN thesis repository. It is superseded by
> estebanr25/decafia-research and is kept for reference only.
