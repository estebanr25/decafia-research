# SECOND-PASS PEER REVIEW — Ingeniería e Investigación
**Manuscript:** DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions
**Files reviewed:** `CoffeeLeafCO_manuscript_v4.docx`, `CoffeeLeafCO_manuscript_v4_anonymous.docx`, `cover_letter_v4.docx`
**Metrics source:** `paper1/results/metrics_final.json` (`phase4.test_set_full`, official iou=0.7 setting)
**Review date:** 2026-11-18
**Reviewer note:** This is a hostile but fair second-pass review. Issues from round 1 are re-checked; a full fresh review is also conducted.

---

## CRITICAL ISSUES (Blockers — must be resolved before acceptance)

### CRITICAL-1: Anonymous version contains GPS coordinates that de-anonymize the field site

**Location:** Anonymous version, Section 3.1, Source 1 paragraph.
**Exact quote:**
> "Source 1 — Original field collection ([LOCATION], Colombia). The primary corpus was captured at a Coffea arabica plantation in [LOCATION], Colombia (6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024..."

**What is wrong:** The town name "El Socorro" has been replaced with the placeholder `[LOCATION]`, but the GPS coordinates (6°28′N, 73°19′W) remain verbatim. These coordinates resolve unambiguously to the El Socorro municipality, Santander, Colombia — a 10-second reverse geocoding search returns the exact town. A reviewer who follows the double-blind protocol but is familiar with Colombian geography, or who uses any map service, will immediately identify the author's field site. Because El Socorro is stated in the main version as the collection site, and the main version names the author's institution as UIS Bucaramanga (which is in Santander), the GPS coordinates cross-identify the author.

**Fix required:** In the anonymous version only, replace the GPS coordinates with a geographic range description, e.g.:
> "...at a Coffea arabica plantation in [LOCATION], Colombia (approximately 6°N, 73°W; approximately 1,500 m a.s.l.)..."
or omit the coordinates entirely in the anonymous version and add a footnote: "[Coordinates withheld for double-blind review; available in author version]". The main version should retain the full coordinates.

---

### CRITICAL-2: Anonymous version reference list skips from [16] to [18] — the gap reveals [17] was removed

**Location:** Anonymous version, References section.
**Exact quote (reference list):** `[16] R. T. Araaf...` followed immediately by `[18] J. G. M. Esgario...`

**What is wrong:** The reference [17] (the author's undergraduate thesis) was correctly removed from the anonymous body text and reference list. However, the reference numbering was NOT renumbered: the list jumps from [16] to [18], and the body text still uses `[18]` for BRACOL. Any reviewer will notice the gap and deduce that a self-citation (reference [17]) was removed, narrowing the search to papers that cite this specific numbered slot. Furthermore, the body text continues to cite `[18]` (two body citations), making the numbering inconsistent in the anonymous version: there is no [17] entry, so the reader cannot verify what [17] was. This is a structural integrity defect in the anonymous submission, and it signals to a reviewer that the manuscript has a thesis predecessor.

**Fix required:** One of two approaches:
(a) **Preferred:** Renumber all references in the anonymous version: shift [18] → [17] and update all in-text citations of [18] to [17]. This produces a contiguous list [1]–[17].
(b) **Alternative:** Insert a stub entry in position [17]: `[17] [Reference withheld for double-blind review]` and retain [18] as BRACOL. This is less clean but avoids renumbering.

---

## MAJOR ISSUES (Must be resolved before acceptance, but not outright blockers)

### MAJOR-1: Anonymous version — Zenodo concept DOI identifies the author's dataset

**Location:** Anonymous version, Data Availability section.
**Exact quote:**
> "Dataset (images, YOLO labels, dataset.yaml, split assignments): https://doi.org/10.5281/zenodo.19931903 (concept DOI; v2.1.0 version DOI [PEGAR DOI ZENODO v2.1.0])..."

**What is wrong:** The Zenodo concept DOI `10.5281/zenodo.19931903` is a live, publicly resolvable URL. Visiting it immediately reveals the dataset name "DECAFIA", the uploader's account name, and all version records. This is equivalent to a direct author link in the anonymous version. The fact that the GitHub source code link was correctly removed (`[link removed for double-blind review]`) makes the oversight in the Data Availability section more conspicuous: the Zenodo link accomplishes the same de-anonymization.

**Fix required:** In the anonymous version, replace the Zenodo concept DOI with a placeholder:
> "Dataset (images, YOLO labels, dataset.yaml, split assignments): [Dataset DOI withheld for double-blind review]. Model weights: [link withheld for double-blind review]. Source code: [link removed for double-blind review]."

The main version must retain the full links.

---

### MAJOR-2: Anonymous version — reference list numbering gap (structural consequence of CRITICAL-2)

This is documented above under CRITICAL-2. The numbering gap creates a structurally incomplete document independently of the de-anonymization concern. It is listed here as a MAJOR issue because it also constitutes a formatting error: the BRACOL reference cited as [18] in the body of the anonymous version has no corresponding [18] definition (since [17] was removed but [18] was not renumbered). Wait — the reference list does include `[18]` for BRACOL, and the body cites `[18]`. The gap is therefore [1]–[16], then [18], with [17] absent. The list is present but non-contiguous. See CRITICAL-2 for the fix.

---

### MAJOR-3: Main version — background false alarm rate figure is inconsistent with the stated exact value

**Location:** Section 5.1, main version.
**Exact quote:**
> "Background false alarm rate = 0.019 (3 of 158 background images triggered at least one detection at conf = 0.50; exact value 0.018987)."

**What is wrong:** 3 ÷ 158 = 0.018987... which rounds to 0.019. The stated exact value and the rounded figure are consistent. However, `metrics_final.json` contains two conflicting background FAR entries:
- `full_test.background_far_at_conf050`: n_with_detection = **4**, rate = **0.025316** (evaluated at iou=0.6)
- `phase4.test_set_full.background_far_at_conf050`: n_with_detection = **3**, rate = **0.018987** (evaluated at iou=0.7)

The manuscript correctly uses the `phase4` (official iou=0.7) value. However, the manuscript does not explicitly state that this FAR figure was computed at NMS IoU = 0.7. A reader comparing to the `full_test` stanza in the JSON would see a discrepancy (4 images, not 3). The evaluation procedure section (4.2) specifies iou=0.7 for mAP evaluation but does not explicitly state the NMS threshold used for the background FAR count.

**Fix required:** Add a parenthetical to the FAR statement: "...at conf = 0.50 and NMS IoU = 0.7;" or add a footnote confirming that all conf=0.50 metrics in Section 5.1 use the same NMS IoU = 0.7 setting as the mAP evaluation.

---

## MINOR ISSUES

### MINOR-1: Anonymous version — "thesis phase" language in Section 3.3 is a soft de-anonymization signal

**Location:** Anonymous version, Section 3.3.
**Exact quote:**
> "...a second annotator independently reviewed labels during the thesis phase, and disagreements were resolved by consulting the Cenicafé phytosanitary identification guide [13]."

**What is wrong:** The phrase "during the thesis phase" discloses that the work originated as a university thesis. Combined with the acknowledgement section (which states "This work derives from the undergraduate thesis of [AUTHOR] and [CO-AUTHOR]..."), this language is consistent and does not by itself reveal the author. However, it does narrow the manuscript's origin type. This is borderline; an aggressive reviewer could object. The more neutral phrasing "during the annotation phase" or "during dataset development" would remove the signal without loss of meaning.

**Fix required (recommended):** In the anonymous version, replace "during the thesis phase" with "during the annotation phase."

---

### MINOR-2: Main version — Section 4.2 GitHub URL (`estebanr25`) is present, correctly expected, but verify it is removed in anonymous version

**Location:** Main version, Section 4.2.
**Exact quote:**
> "All numbers are sourced from metrics_final.json, archived in the public code repository (https://github.com/estebanr25/decafia-research)."

**Status:** This is CORRECT in the main version. The anonymous version correctly replaces this with "[link removed for double-blind review]". No action required on the anonymous version. Logging here as PASS for transparency.

---

### MINOR-3: Reference [17] in main version — handle URL format

**Location:** Main version, References, entry [17].
**Exact quote:**
> "[17] A. F. Salom Medina and L. E. Rosas Ruiz, "Detección y prevención de riesgo de enfermedades en plantaciones de café mediante inteligencia artificial," Trabajo de Grado, Programa de Ingeniería Electrónica, Univ. Ind. Santander, Bucaramanga, Colombia, 2024. [Online]. Available: https://noesis.uis.edu.co/handle/20.500.14071/42486"

**What is right:** Year 2024 is present. The handle `20.500.14071/42486` is correctly cited. The supersedes sentence does not claim same-day preprint posting ("this article supersedes those earlier results, which used an earlier version of the dataset later corrected..."). All round-1 requirements for this reference appear satisfied.

**Remaining minor issue:** The handle is cited only as a URL (`https://noesis.uis.edu.co/handle/...`) rather than as a formal handle DOI (`hdl:20.500.14071/42486`). This is a citation style preference. For IEEE-style references, using the handle as a URL is standard. No fix strictly required; author may wish to add the hdl: prefix for completeness.

---

### MINOR-4: Practical application section — word count is at lower boundary

**Measurement:** Practical application section (Section 8) contains 169 words against the 150–200 word requirement.

**Status:** 169 words is within the 150–200 word range. PASS. Flagging that it is 19 words above the minimum; any editing that removes sentences could push it below 150. Monitor if revisions are made.

---

### MINOR-5: NOVELTY_SEARCH.md cited as a supplementary file but it is a repository file, not a formal supplementary document

**Location:** Table 1 caption and Section 6.1.
**Exact quotes:**
> "Full search log: NOVELTY_SEARCH.md."
> "Full query documentation is provided in the supplementary file NOVELTY_SEARCH.md, archived with the code repository."

**What is wrong:** NOVELTY_SEARCH.md is not submitted as a formal supplementary file to the journal — it is archived in the code repository. The term "supplementary file" implies a journal-submitted supplementary document. This is a terminology error. The correct phrasing would be "supplementary file NOVELTY_SEARCH.md, available in the code repository at [URL]."

**Fix required:** Change "supplementary file NOVELTY_SEARCH.md" → "supplementary file NOVELTY_SEARCH.md, archived in the code repository" (or just "repository file NOVELTY_SEARCH.md"). Ensure the Table 1 caption is consistent.

---

## PASS ITEMS (Confirmed satisfactory)

**PASS-1 — Banned strings:** None of the following banned strings appear anywhere in the main manuscript: "92.4%", "76.6%", "2,786", "Coccinellidae" (as standalone wrong-family reference), "Pseudococcidae", "leakage-free", "sin fuga", "no leakage", "κ = 0.91", "k = 0.91". All clear.

**PASS-2 — All numerical values verified against `metrics_final.json` (phase4.test_set_full, iou=0.7):**
- mAP@0.50 = 0.929 (source: 0.929377) ✓
- mAP@0.50:0.95 = 0.734 (source: 0.734368) ✓
- Roya mAP@0.50 = 0.841 (source: 0.841307) ✓
- Coco mAP@0.50 = 0.962 (source: 0.961786) ✓
- Minador mAP@0.50 = 0.985 (source: 0.985040) ✓
- Filtered mAP@0.50 = 0.926 (source: 0.925574) ✓
- Delta = -0.0038 (computed: 0.925574 − 0.929377 = −0.003803) ✓
- GT instances: roya=825, coco=820, minador=375 ✓
- Coco 95% cluster CI: [0.801, 0.971] (source JSON: lo=0.8012, hi=0.9713) ✓
- Roya image-level 95% CI: [0.803, 0.874] (source JSON: lo=0.8033, hi=0.8735) ✓

**PASS-3 — kappa (κ) symbol:** κ does not appear anywhere in the main manuscript. No inter-rater agreement kappa is reported. ✓

**PASS-4 — Anonymous supervisor sentence:** No sentence claiming a supervisor wishes to remain anonymous appears in the main version. The acknowledgements correctly name the director (Prof. J. G. Barrero Pérez) by name. ✓

**PASS-5 — Thesis reference [17] — year and handle:** Reference [17] in the main version correctly cites year 2024 and includes the handle URL `https://noesis.uis.edu.co/handle/20.500.14071/42486`. ✓

**PASS-6 — Supersedes sentence:** The supersedes sentence reads: "this article supersedes those earlier results, which used an earlier version of the dataset later corrected for source attribution, coco-class taxonomy, and same-leaf duplication between train and test subsets." No claim of same-day preprint posting. ✓

**PASS-7 — Anonymous version — same-day preprint claim:** Not present. ✓

**PASS-8 — Weevil novelty claim properly hedged:** Section 6.1 reads: "To the best of the author's knowledge, none of the public coffee-leaf datasets reviewed for this work includes a class for weevil (Curculionidae) feeding damage (Table 1)." The hedge phrase "To the best of the author's knowledge" is correctly present. ✓

**PASS-9 — Cover letter — no same-day preprint promise:** The cover letter correctly states: "I will not post any preprint prior to receiving such authorization." No promise to post simultaneously or on the same day as submission. ✓

**PASS-10 — Anonymous version — personal identifiers removed:** The following do not appear in the anonymous version: "Luis Esteban Rosas Ruiz", "luis.rosas", "0000-0003-0233-6336", "estebanr25", "El Socorro", "Bucaramanga", "Universidad Industrial de Santander", "Escuela de Ingeniería" (school name). ✓

**PASS-11 — Anonymous version — [17] removed from body and reference list:** Reference [17] (the undergraduate thesis) does not appear anywhere in the anonymous version body text or reference list. The introduction paragraph in the anonymous version correctly reads: "This article supersedes an earlier dataset version that was corrected for source attribution, coco-class taxonomy, and same-leaf duplication between train and test subsets" — no dangling [Author, 2024] pointer. ✓

**PASS-12 — Data Availability — exact placeholder strings present (main version):** Both `[PEGAR DOI ZENODO v2.1.0]` and `[PEGAR URL HUGGING FACE]` appear verbatim in the main version Data Availability section. ✓

**PASS-13 — Data Availability — exact placeholder strings present (anonymous version):** Both `[PEGAR DOI ZENODO v2.1.0]` and `[PEGAR URL HUGGING FACE]` appear verbatim in the anonymous version Data Availability section. ✓

**PASS-14 — AI statement placement:** The "Statement on Artificial Intelligence" section appears before the References section in the main manuscript. ✓

**PASS-15 — Abstract length:** English abstract word count = 178 words, within the ≤250 word limit. ✓

**PASS-16 — Keywords count:** 5 keywords ("coffee leaf disease; object detection; YOLOv8; grouped split; data integrity"), within the 3–5 keyword requirement. ✓

**PASS-17 — Highlights character lengths:** All five highlights are ≤85 characters:
- 84 chars: "• DECAFIA: 2,315 field-annotated coffee leaf images from Colombian Andean conditions"
- 78 chars: "• Three concurrent foliar conditions: rust, weevil (Curculionidae), leaf-miner"
- 84 chars: "• Grouped split prevents same-leaf crops and capture series from crossing boundaries"
- 76 chars: "• Post-hoc integrity audit: 49 of 356 test images have training-split copies"
- 78 chars: "• Open-access release: images, YOLO labels, model weights, and evaluation code"
All pass. ✓

**PASS-18 — Practical application word count:** 169 words, within the 150–200 word range. ✓

**PASS-19 — Roya recall value:** Manuscript reports "Roya recall at conf = 0.50: 0.696"; JSON `phase4.test_set_full.prf1_at_conf050.roya.R = 0.6958`, which rounds to 0.696. ✓

**PASS-20 — Coco CI reportability correctly handled:** Coco cluster CI reported (6 clusters, max 37.2% < 50%). Roya cluster CI correctly suppressed with explanation (single cluster holds 53.1%). Minador cluster CI correctly suppressed with explanation (MINEIRO_99 contamination). Image-level CI reported for roya as secondary only, with caveat. ✓

**PASS-21 — No anonymous institution school name:** The anonymous version uses `[INSTITUTION-SCHOOL]` placeholder. The school name "Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)" does not appear in the anonymous version body. ✓

**PASS-22 — Cover letter preprint request language:** The preprint authorization request is correctly framed as a request contingent on editorial committee decision: "once a decision on this submission has been reached." No unconditional preprint posting is promised. ✓

---

## SUMMARY DISPOSITION

| Category | Count |
|----------|-------|
| CRITICAL (blockers) | 2 |
| MAJOR | 3 |
| MINOR | 5 |
| PASS | 22 |

**Recommendation:** Major revision required before acceptance. The two critical issues (GPS coordinates de-anonymizing the field site in the anonymous version; reference list numbering gap revealing the removed self-citation) must be resolved in the anonymous version. The Zenodo DOI issue (MAJOR-1) in the anonymous version must also be addressed. The two remaining MAJOR issues (background FAR NMS clarification; reference list structural defect already covered by CRITICAL-2) require author response. The five MINOR items do not block acceptance but should be addressed in revision.

The main version (non-anonymous) is in strong shape: all numerical values verified against `metrics_final.json`, all banned strings absent, structural requirements met, weevil claim properly hedged, supersedes sentence correctly worded, and cover letter correctly structured.

---
*Review conducted by extracting all document text via python-docx and cross-checking against `metrics_final.json` (phase4.test_set_full, NMS iou=0.7). All checks run on 2026-11-18.*
