# FINAL_REPORT.md — CoffeeLeaf-CO Paper 1 (SESSION_FINAL_PASS)

## 1. Files to submit (exact paths)

**Anonymous manuscript (double-blind review submission):**
`paper1/manuscript/CoffeeLeafCO_manuscript_v4_anonymous.docx`
`paper1/manuscript/CoffeeLeafCO_manuscript_v4_anonymous.pdf`

**Figures folder (TIFF ≥ 300 dpi):**
`paper1/manuscript/figures_submission/Fig. 3a.tif`  — confusion matrix, raw counts
`paper1/manuscript/figures_submission/Fig. 3b.tif`  — confusion matrix, normalized
`paper1/manuscript/figures_submission/Fig. 5.tif`   — training curves
`paper1/manuscript/figures_submission/Fig. 7.tif`   — bootstrap confidence intervals

**Cover letter:**
`paper1/manuscript/cover_letter_v4.docx`

**Non-anonymous version (Esteban's records only — do NOT submit):**
`paper1/manuscript/CoffeeLeafCO_manuscript_v4.docx`
`paper1/manuscript/CoffeeLeafCO_manuscript_v4.pdf`

**Supporting files (not submitted to journal):**
`paper1/manuscript/NOVELTY_SEARCH.md` — weevil dataset search log
`zenodo_v2.1.0/` — Zenodo v2.1.0 package (ready, not yet uploaded)

---

## 2. Counts

| Item | Value | Limit | Status |
|------|-------|-------|--------|
| Abstract (English) | 167 words | ≤ 250 | PASS |
| Practical application | 169 words | 150–200 | PASS |
| Highlights | 5 items | ≤ 85 chars each | PASS (max 82 chars) |
| Keywords (English) | 5 | 3–5 | PASS |
| Keywords (Spanish) | 5 | 3–5 | PASS |
| Total word count (text only, approx) | ~3,854 | ≤ 6,000 (all content) | PASS (substantial margin) |

**Highlight character counts:**
- 82: DECAFIA: 2,315 field-annotated coffee leaf images from Colombian Andean conditions
- 76: Three concurrent foliar conditions: rust, weevil (Curculionidae), leaf-miner
- 82: Grouped split prevents same-leaf crops and capture series from crossing boundaries
- 74: Post-hoc integrity audit: 49 of 356 test images have training-split copies
- 76: Open-access release: images, YOLO labels, model weights, and evaluation code

**Word count note:** The journal counts "the whole text and its references, figures, and tables"
toward the 6,000-word limit. The 3,854-word estimate above covers text paragraphs only.
Adding figure captions and table content, the total is estimated ~4,200 words — well within
the 6,000-word limit.

---

## 3. Esteban's remaining steps, in order

### 3.1 Reserve Zenodo v2.1.0 version DOI and upload model to Hugging Face

1. Go to Zenodo: https://zenodo.org/records/22756170 → "New version"
2. Upload the files in `zenodo_v2.1.0/` plus the split files from `splits/grouped_v1/`
3. Use the description and keywords in `zenodo_v2.1.0/ZENODO_DESCRIPTION.txt`
4. Reserve the DOI before publishing to get the version DOI.
5. Upload model weights (`best.pt`) to https://huggingface.co/estebanr25/decafia and copy the URL.

### 3.2 Replace two placeholders in BOTH versions

Open both `CoffeeLeafCO_manuscript_v4.docx` and `CoffeeLeafCO_manuscript_v4_anonymous.docx`
and replace:
- `[PEGAR DOI ZENODO v2.1.0]` → the Zenodo v2.1.0 version DOI (e.g., `doi:10.5281/zenodo.XXXXXXX`)
- `[PEGAR URL HUGGING FACE]` → the Hugging Face model URL

After replacing, re-export both PDFs from Word.

**Note:** The anonymous version also has `[dataset DOI withheld for double-blind review]` which
should NOT be changed — it is intentionally anonymized.

### 3.3 Update the claude.ai project

Update files in `paper1/for_claude_project/` from the latest state and follow `README.txt`:
- Delete old files; upload new files; replace project instructions with `PROJECT_INSTRUCTIONS.txt`

### 3.4 Submit through the journal's OJS

Go to https://revistas.unal.edu.co/index.php/ingeinv and submit with:
- Anonymous manuscript (v4_anonymous.docx)
- Figures (figures_submission/ folder)
- Cover letter (cover_letter_v4.docx)

---

## 4. Decisions applied (all 5 from SESSION_FINAL_PASS)

| # | Decision | Status |
|---|----------|--------|
| 1 | Remove κ = 0.91 claim | ✓ Done — no κ anywhere in manuscript |
| 2 | Remove anonymous-supervisor sentence | ✓ Done — annotation described as author's protocol with unnamed second reviewer |
| 3 | Add thesis citation [17] | ✓ Done — cited in Introduction with supersedes sentence; anonymized in blind version |
| 4 | Hedge weevil novelty claim | ✓ Done — "to the best of the author's knowledge" with dataset list |
| 5 | No same-day preprint; request EC authorization | ✓ Done — cover letter requests authorization |

---

## 5. Content restored from earlier draft (~5,400-word version)

**Restored:**
- Note on coco class taxonomy (Curculionidae assignment, morphological basis, Cenicafé reference)
- Practical application section (new, 169 words)
- Explicit F1 scores (Table 4)
- Best checkpoint epoch (epoch 98)
- Background FAR exact value with iou setting clarification

**Not restored (reasons):**
- Section on PR curves: PR curve figures not available in the figures directory (only confusion matrix, training curves, bootstrap CIs exist). Mentioned: Figure 7 serves a similar purpose.
- Qualitative predictions figure: not in figures directory.
- Figure 1 label statistics: not in figures directory.
- Original section 4.3 per-class AP50 as a separate table: merged into Table 4 for conciseness and to stay within word limit.

**Explanation:** The original ~5,400-word draft was produced before the split was corrected and
used superseded numbers (mAP50=92.4%, 2,786 images). v4 uses corrected numbers and structure
throughout. The 1,600-word gap reflects removal of placeholder tables, the wrong split
description, and figures that do not exist for the current corrected evaluation.

---

## 6. Unresolved items

| Item | Status | Action needed |
|------|--------|---------------|
| Zenodo v2.1.0 DOI | Pending | Esteban must reserve/publish via Zenodo |
| Hugging Face model URL | Pending | Esteban must upload best.pt and copy URL |
| Article DOI | Pending | Assigned by journal after acceptance |
| "Received" / "Accepted" dates | Blank | Filled by journal |
| Cover letter false-positive check | Note | "simultaneously" in cover letter check is a false positive from "No simultaneous submission" — the cover letter content is correct |
| GPS coordinates in anonymous version | Fixed | Replaced with [coordinates withheld] |

---

## 7. Hostile review summary

**Two review passes performed (REVIEW_V4.md, REVIEW_V4_PASS2.md).**

Pass 1: 4 critical, 6 major, 8 minor issues found. All 4 critical issues fixed.
Pass 2: 2 critical, 3 major, 5 minor issues found. All fixed.

**All 22 numerical values verified against metrics_final.json.**
**All banned strings absent in final v4.**
**All journal format requirements met.**

v4 SHA-256 (first 16 hex): `907f6ad1dc7b61e2`
v4_anonymous SHA-256 (first 16 hex): `2bc59c67576f97e2`
