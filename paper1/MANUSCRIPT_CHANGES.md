# MANUSCRIPT_CHANGES.md

Claims the manuscript must change, with replacement text rendered from
paper1/results/metrics_final.json.

---

## 1. Remove all "leakage-free" / "sin fuga" wording

**Find and remove:** any sentence containing "leakage-free", "sin fuga", or similar.

**Replacement:** "The split construction uses group-based assignment to prevent
crop-parent and capture-series pairs from crossing split boundaries.
An independent audit found 49 test images (13.8% of the test set) with
dihedral pHash distance <= 4 to an image in the training or validation split
(contamination analysis in Section [X])."

---

## 2. Remove the pHash distance claim

**Remove:** the sentence "no pair of images with a pHash distance of 4 or less
remained across subsets" (or any equivalent claim).

**Replacement:** "A post-hoc audit using dihedral pHash (minimum over 8 flip/rotation
transforms, 64-bit DCT) found 60 cross-split pairs at distance <= 4 in split_grouped_v1,
of which 49 unique test images are affected."

---

## 3. Replace the residual-copy and sensitivity-check paragraphs

**Remove:** the existing residual-copy paragraph and the sensitivity-check paragraph.

**Replace with:**

"An independent integrity audit identified 49 test images with a geometrically
transformed copy in the training or validation split (dihedral pHash distance <= 4,
verified visually for a subset). Of these, 25 carry roya annotations (3.0% of test
roya instances), 12 carry coco annotations (1.5%), and 88 carry minador annotations
(23.5%). To measure the effect, the model was evaluated on both the full test set
(n=356) and a filtered test set that excludes the 49 affected images (n=307). The
results are mAP50=0.928148 [95% CI 0.847-0.943] on the full test set and mAP50=0.926117
on the filtered set (delta=-0.0021). These two test sets have different compositions;
this comparison measures sensitivity to the contamination and is not a corrected metric."

---

## 4. Per-class annotation percentages (resolved from data)

**Previous manuscript had:** "2 / 2 / 13 annotations" or "3.0 / 1.5 / 21.6%"
(the September audit left this unresolved).

**Resolution from data (see metrics_final.json, exclusion_list):**

| Class | Affected annotations | Total test annotations | Percentage |
|-------|---------------------|----------------------|------------|
| roya | 25 | 825 | 3.0% |
| coco | 12 | 820 | 1.5% |
| minador | 88 | 375 | 23.5% |

Note: minador is disproportionately affected (23.5%) because the MINEIRO_99 group
(the largest group, 290 images) contains most minador images, and 49 of its test
images happen to have copies in train.

---

All numbers above are from paper1/results/metrics_final.json
(phase4.test_set_full and exclusion_list sections).
