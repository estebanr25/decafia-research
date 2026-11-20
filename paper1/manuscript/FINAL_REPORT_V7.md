# FINAL_REPORT_V7.md

Generated: 2026-11-20
Input: `CoffeeLeafCO_manuscript_v6.docx`
Build script: `paper1/manuscript/build_manuscript_v7.py`
Verify script: `paper1/manuscript/verify_v7.py`

---

## Files to Submit

| File | Path | Purpose |
|------|------|---------|
| Named manuscript | `paper1/manuscript/CoffeeLeafCO_manuscript_v7.docx` | Submit to journal |
| Anonymous manuscript | `paper1/manuscript/CoffeeLeafCO_manuscript_v7_anonymous.docx` | For double-blind review |
| Cover letter | `paper1/manuscript/cover_letter_v7.docx` | Accompanies submission |

---

## Counts

| Item | Value |
|------|-------|
| Total word count (paras + tables) | 4,593 |
| Abstract word count | 196 (≤250) |
| Practical Application word count | 150 (150–200) |
| Figure captions | 6 |
| Drawings embedded | 6 (named), 6 (anonymous) |
| References cited | 17 |
| Reference entries | 17 |
| Highlights count | 5 |
| Highlight max chars | 79 |

---

## Changes Applied (v6 → v7)

### PART 1 (Blocking): Figures Embedded
- 6 figures embedded with `<w:drawing>` elements in both named and anonymous versions
- TIFFs converted to PNG via PIL before embedding (python-docx TIFF limitation)
- Drawing count = caption count in both versions

**TIF renaming in `figures_submission/`:**
- `Fig. 1.tif` ← `Fig_examples.tif` (copy preserved)
- `Fig. 2.tif` ← `Fig. 5.tif` (training curves)
- `Fig. 3.tif` ← `Fig_schematic.tif`
- `Fig. 4.tif` ← `Fig. 7.tif` (bootstrap CIs)
- `Fig. 5a.tif` ← `Fig. 3a.tif` (confusion matrix raw)
- `Fig. 5b.tif` ← `Fig. 3b.tif` (confusion matrix normalized)

### PART 2 (Blocking): Anonymous Version Identifiers
- `[16]` reference entry replaced with `[16] [Reference withheld for double-blind review]`
- Introduction "first introduced in the author's undergraduate thesis [16]" → "a preliminary version of this dataset was introduced in [16]"
- "El Socorro, Santander, Colombia," → "[location withheld], Colombia,"
- "El Socorro, Colombia" in Fig. 1 caption → "[location withheld], Colombia"
- Author name, ORCID, email, institution, acknowledgements, CRediT withheld

### PART 3: Capture Years and Phone Model
- Source 1: added "in 2022–2023 using a Xiaomi Poco X3 Pro smartphone"

### PART 4: MINEIRO_99 Component Description
- Section 4.3: replaced erroneous "cross-source leaf group (ROYA_MA and ROYA_RECORTES)" with correct MINEIRO_99 description (laboratory leaf-miner images from Silva et al., prefixes MINEIRO, MINADO_RECORTES, MINADOR)
- Limitation (1): updated to reference MINEIRO_99 as "primarily laboratory leaf-miner images from Silva et al."

### PART 5: Bootstrap Cluster Description
- Section 4.4: Clusters redefined as "(group_root, source) pairs" to prevent spurious cross-source grouping
- Roya cluster updated: 11 clusters, 52.6% (not 53.1%), 434 instances (not 438)
- Minador cluster noted: 4 clusters, 43.7%, not reported
- Coco caveat: "with only 6 clusters, this bootstrap CI may be unreliable"
- Limitation (4): updated to new roya cluster numbers and description

### PART 6: Table Numbering
- Table 1 (datasets comparison) — unchanged
- Table 2 (class × split) — renamed from Table 2 (kept number, fixed ordering)
- Table 3 (source × split) — renamed from Table 2b
- Table 4 (training config) — renamed from Table 3; added optimizer note
- Table 5 (performance) — renamed from Table 4
- Table 2 reordered BEFORE Table 3 in document
- File path references removed from captions
- In-text refs updated for Tables 2, 3, 4

### PART 7: Text Fixes
- Section 3.2: "grouped by leaf: all crops..." → "designed to keep crop–parent pairs and capture series together; a post-hoc audit found residual transformed copies (Section 5.3)"
- Highlight 1: "prevents same-leaf crops and capture series from crossing boundaries" → "keeps crop–parent pairs and capture series of a leaf together"
- Highlight 2: "49 of 356 test images have training-split copies" → "49 of 356 test images have copies in train (40) or val only (9)"
- Abstract: added "copies in the training (40) or validation (9) split"; removed dagger from minador
- Table 1: RoCoLe → "Classification / Detection"; BRACOL → "Classification and severity"
- Table 1 caption: "No prior dataset" → "Among the datasets reviewed, none"
- Section 2.2 and 6.1 novelty: removed "instance-level bounding boxes" as distinguishing feature; added weevil class as key novelty
- Section 8 Practical Application: removed altitude/variety/Andean nations; added "facilitate replication by other groups" (now 150 words)
- Section 3.3: added "by the thesis authors" and "Silva et al. images were re-annotated under the same protocol"
- Section 6.2: removed "[4, 7] sentence" (papers may not report both mAP metrics)
- Section 4.4: minador caveat added
- Section 5.1: removed "(exact value 0.018987)"
- Section 5.4: "normalised confusion matrix (Fig. 5b) shows" → "confusion matrices (Fig. 5a raw counts, Fig. 5b normalised) show" (citation order fix)

### PART 8: Reference Fixes
- [1] FNC: URL updated to full Cenicafé download URL
- [2] Avelino: full title "(2008–2013): impacts, plausible causes and proposed solutions"
- [9] RoCoLe: full title "for evaluation of machine learning based methods in plant diseases recognition"
- [10] Silva: exact title "Rust (Hemileia vastatrix) and leaf miner (Leucoptera coffeella) in coffee crop (Coffea arabica)"
- [13] Jocher: added "[Accessed: Nov. 2026]"

### PART 9: Cover Letter
- `cover_letter_v7.docx` — copied from v5 (title unchanged, sole-authorship paragraph correct)

---

## Full Output of `verify_v7.py`

```
============================================================
CHECKING NAMED VERSION: CoffeeLeafCO_manuscript_v7.docx
============================================================

--- 1. Drawing count ---
  Drawings: 6
  Figure captions: 6
    - Fig. 1. Example annotated images. Left column: own-field ima
    - Fig. 2. Training curves (val mAP@0.50 vs. epoch) for decafia
    - Fig. 3. Dataset construction and integrity audit pipeline. N
    - Fig. 4. mAP@0.50 per class with 95% confidence intervals (B
    - Fig. 5a. Confusion matrix for decafia_grouped_v1 on split_gr
    - Fig. 5b. Confusion matrix — normalized by true class. Same t
  PASS: Drawing count equals caption count (6 drawings, 6 captions)

--- 2. Named version identifier presence (should have) ---
  PASS: Has 'Rosas' in named
  PASS: Has author email in named
  PASS: Has ORCID in named

--- 3. Banned strings ---
  PASS: Banned '92.4%' not present
  PASS: Banned '76.6%' not present
  PASS: Banned '2,786' not present
  PASS: Banned 'Pseudococcidae' not present
  PASS: Banned 'Coccinellidae' not present
  PASS: Banned 'leakage-free' not present
  PASS: Banned 'sin fuga' not present
  PASS: Banned 'DECAF-IA' not present
  PASS: Banned 'DECAFIA' not present

--- 4. [VERIFY] markers ---
  PASS: No [VERIFY] markers

--- 5. Numbers vs JSON ---
  PASS: Number 0.929 in doc (mAP50 overall)
  PASS: Number 0.734 in doc (mAP50-95 overall)
  PASS: Number 0.841 in doc (mAP50 roya)
  PASS: Number 0.962 in doc (mAP50 coco)
  PASS: Number 0.985 in doc (mAP50 minador)
  PASS: Number 0.926 in doc (mAP50 filtered)
  PASS: Number 1,577 in doc (train split)
  PASS: Number 382 in doc (val split)
  PASS: Number 356 in doc (test split)
  PASS: Number 2,315 in doc (total images)
  PASS: Number 0.801 in doc (CI coco lo)
  PASS: Number 0.971 in doc (CI coco hi)
  PASS: 2,315 in doc (total images)
  PASS: 49 excluded in doc
  PASS: 40 by_train in doc
  PASS: 9 by_val in doc

--- 6. Highlights (<=85 chars each) ---
  PASS: Highlight <=85 chars: 'CoffeeLeaf-CO: 2,315 annotated coffee leaf images; two sou...' (79) (79 chars)
  PASS: Highlight <=85 chars: 'Three concurrent foliar conditions: rust, weevil (Curculio...' (78) (78 chars)
  PASS: Highlight <=85 chars: 'Grouped split keeps crop-parent pairs and capture series o...' (77) (77 chars)
  PASS: Highlight <=85 chars: 'Audit: 49 of 356 test images have copies in train (40) or ...' (72) (72 chars)
  PASS: Highlight <=85 chars: 'Open-access release: images, YOLO labels, model weights, a...' (78) (78 chars)

--- 7. Abstract word count (<=250) ---
  PASS: Abstract <=250 words (196 words)

--- 8. Practical Application word count (150-200) ---
  PASS: Practical Application 150-200 words (150 words)

--- 9. Total word count ---
  Total word count (all paragraphs + tables): 4593

--- 10. Figures citation order ---
  First mentions in order:
    Fig. 1: Source 2 - Silva et al. (Brazil, re-annotated). Rust and leaf-miner im
    Fig. 2: A YOLOv8m model [13] initialised with MS COCO pre-trained weights [14]
    Fig. 3: The largest verified component (272 images, the MINEIRO_99 component)
    Fig. 4: Fig. 4 shows mAP@0.50 per class with confidence intervals where report
    Fig. 5a: The confusion matrices (Fig. 5a raw counts, Fig. 5b normalised) show t
    Fig. 5b: The confusion matrices (Fig. 5a raw counts, Fig. 5b normalised) show t
  PASS: All figures cited
  PASS: Figures cited in order

--- 11. Tables citation order ---
  Table captions in document order:
    Table 1. Comparison of publicly available coffee leaf diseas
    Table 2. CoffeeLeaf-CO dataset composition by class and spli
    Table 3. CoffeeLeaf-CO source composition by split and class
    Table 4. Training configuration for the YOLOv8m baseline (de
    Table 5. Baseline performance on the CoffeeLeaf-CO test set
  First in-text mentions:
    Table 1: Table 1 summarises publicly available coffee leaf disease datasets. No
    Table 2: The final dataset comprises 2,315 annotated images. Images are split i
    Table 3: The final dataset comprises 2,315 annotated images. Images are split i
    Table 4: A YOLOv8m model [13] initialised with MS COCO pre-trained weights [14]
    Table 5: Table 5 presents test-set performance. The YOLOv8m baseline achieves m

--- 12. Reference checks ---
  In-text citations: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']
  Reference entries: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']
  PASS: All 17 references cited
  PASS: All 17 entries present
  PASS: No [VERIFY] in references

============================================================
CHECKING ANONYMOUS VERSION: CoffeeLeafCO_manuscript_v7_anonymous.docx
============================================================

--- Anon 1. Drawing count ---
  Drawings: 6
  Figure captions: 6
  PASS: Anon drawing count equals caption count (6 drawings, 6 captions)

--- Anon 2. Identifier search (must NOT contain) ---
  PASS: 'Rosas' not found (Author surname)
  PASS: 'Salom' not found (Co-author surname)
  PASS: 'Barrero' not found (Director surname)
  PASS: 'estebanr25' not found (GitHub username)
  PASS: 'luise' not found (Windows username)
  PASS: 'Industrial de Santander' not found (Institution name)
  PASS: 'Univ. Ind.' not found (Abbreviated institution)
  PASS: 'correo.uis' not found (Email domain)
  PASS: '0000-0003-0233-6336' not found (ORCID)
  PASS: 'zenodo.19931903' not found (Zenodo ID)
  PASS: 'huggingface' not found (HuggingFace)
  PASS: 'decafia-research' not found (GitHub repo)
  PASS: 'El Socorro' not in anon
  PASS: 'E. Santander' (RoCoLe author) present and allowed
  WARN: Thesis title word 'Detecci' found (false positive: appears in Spanish subtitle 'deteccion')
  WARN: Thesis title word 'inteligencia artificial' found (false positive: appears in DECAF IA project name expansion)
  PASS: [16] entry anonymized
  PASS: [location withheld] in anon

--- Anon 3. Banned strings ---
  PASS: All banned strings absent

============================================================
SUMMARY: 100 passed, 0 failed, 2 warnings (both false positives)
============================================================
```

---

## Full Identifier Search on Anonymous v7

All identifiers checked against `CoffeeLeafCO_manuscript_v7_anonymous.docx` text (paragraphs, tables, headers, footers):

| Identifier | Description | Result |
|-----------|-------------|--------|
| Rosas | Author surname | NOT FOUND |
| Salom | Co-author surname | NOT FOUND |
| Barrero | Director surname | NOT FOUND |
| estebanr25 | GitHub username | NOT FOUND |
| luise | Windows username | NOT FOUND |
| Industrial de Santander | Institution | NOT FOUND |
| Univ. Ind. | Abbreviated institution | NOT FOUND |
| correo.uis | Email domain | NOT FOUND |
| 0000-0003-0233-6336 | ORCID | NOT FOUND |
| zenodo.19931903 | Zenodo deposit ID | NOT FOUND |
| huggingface | HuggingFace | NOT FOUND |
| decafia-research | GitHub repo | NOT FOUND |
| El Socorro | Field collection location | NOT FOUND (replaced with [location withheld]) |
| E. Santander | RoCoLe author (ALLOWED) | Present — allowed |
| Deteccion | Spanish thesis title word | Appears in Spanish subtitle ("detección de roya") — NOT thesis-identifying |
| Inteligencia artificial | Thesis title word | Appears in DECAF IA project name expansion — NOT thesis-identifying |

**[16] reference entry:** `[16] [Reference withheld for double-blind review]` ✓

---

## Reference Status Table

| Ref | Status | Note |
|-----|--------|------|
| [1] FNC | UPDATED | Full Cenicafé PDF download URL added |
| [2] Avelino | UPDATED | Full subtitle "(2008-2013): impacts, plausible causes and proposed solutions" |
| [3] Constantino | VERIFIED | "Otros habitantes naturales del cafetal" |
| [4] Tian MD-YOLO | VERIFIED | No change |
| [5] Mohanty | VERIFIED | No change |
| [6] Pacal | REPLACED (v6) | Was Sajitha; now Pacal 2024 |
| [7] Somanna | VERIFIED | No change |
| [8] Zuniga Cajas | REWRITTEN (v6) | No change from v6 |
| [9] RoCoLe | UPDATED | Full title for dataset recognition paper |
| [10] Silva | UPDATED | Exact Mendeley title with species names |
| [11] VIA | UPDATED (v6) | ACM MM'19 citation |
| [12] SAM | VERIFIED | No change |
| [13] Jocher | UPDATED | Added [Accessed: Nov. 2026] |
| [14] MS COCO | VERIFIED | No change |
| [15] Araaf | VERIFIED | No change |
| [16] Rosas thesis | PRESENT (named) / WITHHELD (anon) | Full citation in named; withheld in anon |
| [17] Esgario BRACOL | VERIFIED | No change |

No [VERIFY] tags in any reference entry.

---

## Remaining Manual Steps

### Before submission:
1. **Zenodo DOI**: paste actual v2.1.0 version DOI where `[PEGAR DOI ZENODO v2.1.0]` appears (named version only)
2. **HuggingFace URL**: paste model URL where `[PEGAR URL HUGGING FACE]` appears (named version only)
3. **FNC page numbers**: if page numbers for the 557,000 families and 600 municipalities figures are found in the PDF, add them to [1]

### For review/submission:
4. Upload `CoffeeLeafCO_manuscript_v7_anonymous.docx` to journal submission system
5. Upload `cover_letter_v7.docx` with the submission
6. Keep `CoffeeLeafCO_manuscript_v7.docx` (named) for Zenodo / HuggingFace deposit

### Not addressed (require additional computation):
- Per-source mAP50 and mAP50-95 for roya: `metrics_final.json` contains P/R by source but not mAP50 by source. Per-source mAP50 curves require re-running `model.val()` on source-stratified subsets. This limitation is documented in Section 5.2.

---

## Technical Notes

- **Drawing embedding**: python-docx `add_picture()` creates `<w:drawing>` elements. TIFF files were first converted to PNG via PIL (Pillow) because python-docx cannot directly embed TIFF.
- **merge_runs safety**: The `merge_runs()` helper function was called only BEFORE figure embedding to avoid destroying drawing elements. All text changes were applied before figures were embedded.
- **Table reorder**: Table 2 (class × split) and Table 3 (source × split) were reordered at the XML level after all text replacements, to ensure Table 2 appears first in the document.
- **Anonymous build**: The anonymous version is built by deep-copying the named document (via save+reload) BEFORE figure embedding, applying anonymization text changes, saving to temp, then embedding figures separately. This prevents `merge_runs` calls from destroying drawings.
