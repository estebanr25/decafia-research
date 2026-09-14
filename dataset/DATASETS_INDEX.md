# 01_dataset — Dataset Directory Index

Last updated: 2026-09-11

Three image datasets coexist in this directory. Use the table below to
identify which to use for which purpose.

---

## Dataset Summary

| Directory | Status | Images | Annotations | Classes | Use |
|-----------|--------|-------:|------------:|---------|-----|
| `decafia_clean/` | **CANONICAL** | 2315 | 12794 | 3 (roya, coco, minador) | All training and evaluation |
| `decafia_yolo_original/` | **SOURCE** | 2769 | 12810 | 4 (roya, coco, sano, minador) | Reference / provenance audit only |
| `splits/` | **ARCHIVED** | 2769 | 15181 | 4 (roya, coco, sano, minador) | Do not use — see splits/DO_NOT_USE.md |

---

## Detailed Records

### `decafia_clean/` — CANONICAL

**Full path:** `C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean`  
**Images:** 2315 (train=1618, val=348, test=349)  
**Annotations:** 12794 instance lines (roya=5020, coco=5389, minador=2385)  
**Background images:** 1113 (empty label files = healthy leaves)  
**Class scheme:** nc=3, IDs 0=roya 1=coco 2=minador (minador remapped from original ID 3)  
**Split:** 70/15/15 stratified by class presence, seed=42  
**Sources:** own_field (Socorro, Colombia) + Silva et al. rust-and-leaf-miner  
**Excluded:** RoCoLe (454 images, domain mismatch + cross-split leakage)  
**Status:** CANONICAL — use this for all training, fine-tuning, and evaluation.

### `decafia_yolo_original/` — SOURCE

**Full path:** `C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_yolo_original`  
**Images:** 2769 (train=1934, val=549, test=286)  
**Annotations:** 12810 instance lines  
**Class scheme:** nc=4, IDs 0=roya 1=coco 2=sano 3=minador  
**Status:** SOURCE — untouched copy of the production dataset as received.
Read-only reference. Do not train from this directly: it contains 454 RoCoLe
images with cross-split SHA256 duplicates and the 4-class scheme including sano boxes.

### `splits/` — ARCHIVED

**Full path:** `C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\splits`  
**Images:** 2769  
**Annotations:** 15181 instance lines  
**Class scheme:** nc=4, IDs 0=roya 1=coco 2=sano 3=minador (same as original, unverified)  
**Status:** ARCHIVED — do not use for training or evaluation.
See `splits/DO_NOT_USE.md` for full explanation.

---

## Other Files and Directories

| Path | Contents |
|------|----------|
| `provenance_manifest.csv` | One row per image in decafia_yolo_original: sha256, source, evidence |
| `DUPLICATES.csv` | 5 SHA256 duplicate pairs found in decafia_yolo_original |
| `DATASET_AUDIT.md` | Pre-build audit report |
| `DATASET SUBCLASES/` | Raw images before partitioning, with subcategory folders |
| `DATASET Y JSON SEGMENTACION/` | Segmentation-format version of the dataset |
| `splits_clean/` | Earlier cleaned split attempt (superseded by decafia_clean) |
| `raw_images/` | Miscellaneous raw images, 51 files |
| `provenance_check/` | Cropped outlier images from provenance audit |