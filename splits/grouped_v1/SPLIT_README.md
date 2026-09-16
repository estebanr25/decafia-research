# DECAFIA Grouped Split v1

## Method
Images grouped with union-find under the following rules:

1. **Non-crop images**: within each prefix, stems sharing floor(number / B) are merged.
2. **Crops with a valid parent** (inliers >= 30, containment >= 0.80): merged with their
   parent only. No block grouping (a crop's number carries no session information).
3. **Orphan crops without a valid parent**:
   - own_field (e.g. COCO_RECORTE): forced to the training split.
   - rust_and_leaf_miner: block-grouped floor(number/B) ONLY among orphan crops of the
     same prefix (not mixed with non-orphan images).
4. **pHash <= 4 edges**: any cross-image pair with pHash distance <= 4 is merged.

Split assigned by randomized greedy search (seed=42, 20 000 iterations), minimising
max deviation from 70/15/15 across image share, per-class annotation share, and
background-image share in val and test.

## Chosen B = 20  (max deviation = 2.41 pp)

## Deviations table
| split | images | roya  | coco  | minador | background |
|-------|--------|-------|-------|---------|------------|
| train | 68.1% | 66.2% | 69.5% | 68.0% | 71.7% |
| val   | 16.5% | 17.4% | 15.3% | 16.3% | 14.1% |
| test  | 15.4% | 16.4% | 15.2% | 15.7% | 14.2% |

## Crop results
- Total crops: 398, valid parent pairs (post-filter): 176
  (92 same split, 84 different split), orphans: 222
- Rows dropped for threshold (inliers < 30 or containment < 0.80): 0

## Orphan handling assumption
**Orphan crops from `own_field` (e.g. COCO_RECORTE) are forced to the training split**,
because their parents likely exist in the dataset but were not detected by the SIFT pipeline.

Orphan crops from `rust_and_leaf_miner` (Silva et al.) are NOT forced; they are block-grouped
only among other orphan crops of the same prefix, because their parents are likely not in this
dataset.

Per-prefix orphan counts:
  - ROYA_RECORTES: 89
  - MINADO_RECORTES: 69
  - COCO_RECORTE: 64

## Limitation
The same physical leaf photographed at non-consecutive number intervals is not detectable
by the block-based grouping strategy. Such pairs can only be caught by pHash near-duplicate
edges (distance <= 4). Pairs with 5 <= pHash <= 12 may still represent the same leaf and
remain undetected.
