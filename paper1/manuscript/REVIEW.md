# Peer Review — Ingeniería e Investigación (I&I)
## Manuscript: "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions"
## Reviewer: Anonymous | Date: 2026-11-17 | Recommendation: **MAJOR REVISION**

---

## 1. NUMBERS CHECK

**Reference document:** `paper1/NUMBERS_FOR_MANUSCRIPT.md` / `metrics_final.json` (SHA-256 prefix: bc4fbb2b)

### 1.1 Core metrics — all present and correctly rounded

| Metric | JSON value | Manuscript | Assessment |
|--------|-----------|------------|------------|
| mAP@0.50 (full) | 0.929377 | 0.929 | PASS (3 dp) |
| mAP@0.50:0.95 (full) | 0.734368 | 0.734 | PASS (3 dp) |
| mAP@0.50 roya | 0.841307 | 0.841 | PASS |
| mAP@0.50 coco | 0.961786 | 0.962 | PASS (rounds up at 3 dp) |
| mAP@0.50 minador | 0.985040 | 0.985 | PASS |
| mAP@0.50 filtered | 0.925574 | 0.926 | PASS (rounds up at 3 dp) |
| Δ filtered | 0.003803 | −0.0038 | PASS |
| Coco CI lo | 0.8012 | 0.801 | PASS |
| Coco CI hi | 0.9713 | 0.971 | PASS (truncated, not rounded — 0.9713 → 0.971; acceptable) |
| Roya image-level CI lo | 0.8033 | 0.803 | PASS |
| Roya image-level CI hi | 0.8735 | 0.874 | PASS (rounds up: 0.8735 → 0.874; acceptable) |
| BG false-alarm rate | 0.018987 | 0.019 | PASS (2 dp) |
| F1 overall | 2×0.895×0.826/(0.895+0.826) = 0.859 | 0.859 | PASS |
| 49/356 = 13.76% | — | 13.8% | PASS |
| FN roya = 825×(1−0.696) = 250.8 | — | 251 | PASS |

### 1.2 Flags

**FLAG N1 — Abstract says "reduces mAP@0.50 by 0.004 to 0.926":**
The abstract states the reduction is 0.004, while the body correctly reports Δ = −0.0038. The rounding from 0.0038 to 0.004 in the abstract is aggressive; Δ = −0.004 is technically wrong at two significant figures. The body is correct; the abstract must be made consistent. Either state "0.004" everywhere with a note, or use "< 0.004" / "0.004 (rounded)" in the abstract.

**FLAG N2 — VERIFY item κ = 0.91 has no traceable source file:**
Section 3.3 states: "a κ value from an earlier draft of this work has no source file in the repository and is marked [VERIFY: κ = 0.91 — confirm source]." This is an unresolved manuscript flag left in the submitted text. A kappa coefficient without a verifiable source CANNOT appear in a submitted manuscript, with or without a [VERIFY] label. Either verify and document the source or remove the claim entirely.

**FLAG N3 — PyTorch version 2.11 cited in Section 4.1:**
PyTorch 2.11 is cited. As of November 2026, the current stable PyTorch release is well past 2.5. If 2.11 is correct (a future version), no citation exists and the claim is unverifiable. If it is a typo for 2.1.1 or 2.1 (released 2023–2024), it must be corrected and cited properly. This is a reproducibility-critical detail.

**FLAG N4 — 23.5% minador annotation contamination claim:**
Section 5.3 states "88 carry minador annotations (23.5%)." Verification: 88/375 = 23.47%, rounds to 23.5%. This is consistent with the GT count of 375 minador test instances. PASS on arithmetic. However, the manuscript does not state whether these 88 are instances or images. Given that 49 images are affected and minador images can carry multiple instances, this should be clarified.

---

## 2. CLAIMS CHECK

### 2.1 Minador CI caveat — PASS (with reservation)

Section 4.4 explicitly states: "Minador: cluster CI computed but not reported in the manuscript (Section 5.3)." Section 5.2 states: "Minador mAP@0.50 = 0.985†; see Section 5.3." Section 6.3 states: "All minador test images belong to this component; therefore, minador test performance (mAP@0.50 = 0.985) cannot be interpreted as performance on independent held-out leaves." The caveat is stated clearly and correctly. NUMBERS_FOR_MANUSCRIPT.md confirms the reason (contaminated group, CI retained with reported:false). **PASS on correctness.** However, the dagger notation (†) must appear consistently in Table 4, Figure 7, the Conclusions, and everywhere 0.985 appears. A reviewer reading only the abstract sees "leaf-miner: 0.985†" with no footnote text in the abstract itself — the dagger must be explained at first occurrence.

### 2.2 Roya CI — correctly labeled as image-level secondary — PASS

Section 5.2 states: "Image-level CI (secondary; ignores within-leaf correlation): [0.803, 0.874]." The Conclusions repeat this with the label "95% image-level CI." NUMBERS_FOR_MANUSCRIPT.md confirms this is secondary and that the cluster CI is unreportable due to cluster size (not contamination). **PASS.**

### 2.3 Contamination sensitivity — correctly labeled "not a corrected metric" — PASS

Section 5.3 states: "this comparison measures sensitivity to the contamination and is not a corrected metric." The Conclusions repeat: "This sensitivity check is not a corrected metric; the two test sets differ in composition." **PASS.**

### 2.4 Split description — PASS

The manuscript uses "grouped by leaf" / "grouped split" / "split is grouped by leaf" throughout. The phrases "leakage-free," "sin fuga," and "no leakage" do not appear anywhere in the manuscript (confirmed by text search). The split is described as preventing "crop-parent and capture-series pairs from crossing split boundaries" and conservatively uses filename patterns for third-party images. **PASS on wording.** However, the manuscript uses the phrase "minimise cross-split leakage" in Section 3.2 — this is a loose use of "leakage" in a non-banned context; acceptable, but should be changed to "minimise cross-split duplication" to avoid any ambiguity.

### 2.5 Unsupported or unresolved claims — FLAGS

**FLAG C1 — κ = 0.91 without source (see also N2):** This claim is published in Section 3.3 with an explicit in-text flag "[VERIFY: κ = 0.91 — confirm source]." This is not a reviewable scientific manuscript — it is a draft with unresolved placeholders. A claim flagged as unverified by the author must be resolved before submission.

**FLAG C2 — Agronomist annotation supervision described anonymously with an in-text flag:** Section 3.1 and the Acknowledgements both contain "[CONFIRMAR: OK to describe the supervisor anonymously?]". This is an unresolved editorial decision flagged by the author and must not appear in a submitted manuscript.

**FLAG C3 — Dataset novelty claim for weevil (Section 6.1):** The claim "No public dataset with Curculionidae-class bounding-box annotations for coffee was found" is flagged as "[VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists]" and uses a 2026 date stamp. The search covers only Mendeley Data and CrossRef, omitting Google Dataset Search, Roboflow Universe, IEEE DataPort, and Kaggle. This search is insufficient to support a "first publicly available" claim, and the in-text [VERIFY] flag confirms the author knows it is unresolved.

**FLAG C4 — Unresolved UIS thesis reference:** The reference list ends with "[VERIFY] UIS thesis on DECAFIA / AI for coffee disease risk — verify at https://noesis.uis.edu.co (search: DECAFIA café enfermedad); authors, year, handle unknown." This is not a reference — it is an editorial note to the author. It must be resolved or removed before submission. No article can be submitted with an unverified reference carrying unknown authors, year, and handle.

**FLAG C5 — "November 2026" date in body text (Section 6.1):** The dataset novelty claim uses "as of November 2026" — revealing the submission date in the body text. In a double-blind submission this may reveal timing; more importantly, this is the reviewer's current date (2026-11-17) and the literature claim needs to be robust, not tied to a specific month that becomes stale on publication.

**FLAG C6 — Section 2.1 cites Araaf et al. [16] in Section 5.1 as a comparison point:** The claim "Araaf et al. reported mAP@0.50 = 0.732 for single-class rust detection (different dataset — not directly comparable)" is correctly caveated. However, citing a single external result with no further comparison analysis is of marginal scientific value and may invite reviewer questions about the choice of this specific comparator.

---

## 3. BANNED STRINGS CHECK

Searched manuscript text for all eight banned strings. Results:

| String | Found? |
|--------|--------|
| "92.4%" | NOT FOUND — PASS |
| "76.6%" | NOT FOUND — PASS |
| "2,786" | NOT FOUND — PASS |
| "Coccinellidae" | NOT FOUND — PASS |
| "Pseudococcidae" | NOT FOUND — PASS |
| "leakage-free" | NOT FOUND — PASS |
| "sin fuga" | NOT FOUND — PASS |
| "no leakage" | NOT FOUND — PASS |

**All eight banned strings absent.** The manuscript does use "cross-split leakage" once (Section 3.2) as a generic term, which is not on the banned list; see Claim §2.4 for commentary.

---

## 4. REFERENCES CHECK

### 4.1 IEEE format compliance

Overall formatting is close to IEEE style. Specific violations:

**FLAG R1 — Reference [9] RoCoLe: wrong DOI type for a journal citation.**
The manuscript cites reference [9] (Parraga-Alava et al., *Data in Brief*, vol. 25, p. 104414, 2019) with DOI `10.17632/c5yvn32dzg`. This is the **Mendeley Data repository DOI** for the dataset itself, not the journal article DOI. The journal article (*Data in Brief*) DOI is `10.1016/j.dib.2019.104414`. For a reference to the journal publication, the journal DOI must be used. Using the dataset DOI conflates the dataset with the article.

**FLAG R2 — Reference [13] uses "ibid." — non-standard in IEEE.**
IEEE does not use Latin abbreviations such as "ibid." Reference [13] is listed as `L. M. Constantino et al., "Otros habitantes naturales del cafetal," ibid. [3].` This must be replaced with a full repeat citation or omitted if [3] and [13] are genuinely identical sources. If they are the same chapter cited twice, consider whether two separate entries are needed at all.

**FLAG R3 — Reference [7] missing DOI and incomplete bibliographic data.**
Somanna et al., "Proc. AICS, Springer, Cham, 2024" has no DOI, no page range, no volume/issue, and no conference full title. "AICS" is expanded nowhere. IEEE requires sufficient detail for unambiguous retrieval. The conference proceedings DOI (or at minimum the Springer link) must be supplied.

**FLAG R4 — Reference [1] missing DOI or stable URL.**
The FNC Informe de Gestión 2024 is a grey literature report. No URL, no DOI, no access date. IEEE requires a URL with access date for web-only institutional reports.

**FLAG R5 — Reference [14] YOLOv8 cites "GitHub, 2023" with access date "Mar. 2025."**
The citation year (2023) conflicts with the access date (Mar. 2025). The Ultralytics YOLOv8 project has a citable JOSS paper and a Zenodo release with version-specific DOIs. The GitHub URL alone is not a stable reference. The specific version used (Ultralytics 8.4.148) must be cited with a version-pinned DOI from Zenodo (e.g., `https://doi.org/10.5281/zenodo.XXXXXXXX` for version 8.4.148) or the Jocher et al. JOSS/arXiv citation.

**FLAG R6 — Reference [VERIFY] is not a reference.**
An unresolved editorial note ("authors, year, handle unknown") appears in the reference list. This must be removed before submission. See FLAG C4.

### 4.2 Age of references (journal prefers ≤ 5 years, i.e., ≥ 2021)

Eight of sixteen completed references predate 2021:

| Ref | Year | Notes |
|-----|------|-------|
| [3]/[13] | 2013 | Cenicafé manual — foundational, justified |
| [15] | 2014 | MS COCO — foundational, justified |
| [2] | 2015 | Avelino rust epidemic — historical, justified |
| [5] | 2016 | Mohanty PlantVillage — foundational, justified |
| [9] | 2019 | RoCoLe — primary dataset, cannot be replaced |
| [10] | 2020 | Silva et al. — primary dataset, cannot be replaced |
| [11] | 2019 | VIA annotator — tool citation, justified |

Foundational and dataset citations justify pre-2021 dates; the editor should accept these. Nevertheless, **8/16 references (50%) are older than 5 years** — the journal guideline says "preferably not exceeding five years." The author should acknowledge this in the cover letter.

### 4.3 [VERIFY] items

The manuscript contains four unresolved pre-flagged items that have NOT been cleared before submission:

1. `[VERIFY: κ = 0.91 — confirm source]` — Section 3.3
2. `[CONFIRMAR: OK to describe the supervisor anonymously?]` — Section 3.1 and Acknowledgements
3. `[VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists]` — Section 6.1
4. `[PENDIENTE: publish Zenodo v2.1.0 and paste version DOI]` — Data Availability
5. `[PENDIENTE: upload to Hugging Face estebanr25/decafia and paste URL]` — Data Availability
6. `[VERIFY] UIS thesis` — Reference list

**Six unresolved author flags remain in the submitted text.** This is unacceptable for a manuscript submitted for peer review. The manuscript is in draft state.

---

## 5. JOURNAL COMPLIANCE CHECK

### 5.1 Language
- Article in English: **YES**
- Title in English: **YES**
- Title in Spanish: **YES**
- Abstract in English: **YES** (167 words — within 250-word limit)
- Abstract in Spanish (Resumen): **YES** (Spanish abstract present)
- Keywords in English: **YES — but NON-COMPLIANT (10 keywords; limit is 3–5)**
- Keywords in Spanish: **YES — but NON-COMPLIANT (10 keywords; limit is 3–5)**

**FLAG J1 — Keywords severely exceed the 3–5 limit in both languages.**
English: "coffee leaf disease; object detection; YOLOv8; Colombia; Santander; Hemileia vastatrix; Leucoptera coffeella; benchmark dataset; grouped split; data integrity" = **10 keywords**.
Spanish: same 10 items.
Journal requirement: 3–5 keywords. The author must reduce to a maximum of 5. Suggested: retain the most specific and searchable 5 (e.g., coffee leaf disease; object detection; YOLOv8; grouped split; data integrity).

### 5.2 Abstract word count
English abstract: **167 words** — within the 250-word limit. **PASS.**

### 5.3 Total word count
Measured from the extracted paragraph text (all paragraphs, both abstracts, body, declarations, references): **3,378 words.**
Journal limit: 6,000 words including references, figures, and tables.
The word count is well within limit — **PASS**. However, all table and figure content is currently represented as `[INSERT TABLE]` / `[INSERT FIGURE]` placeholders. When the actual tables (Tables 1–4) and figures (Figs. 3, 5, 7) are inserted, the word count will increase. With typical table caption and legend text, the total is unlikely to exceed 6,000 words, but this must be verified after placeholders are replaced.

### 5.4 Required sections
Per journal guidelines: Title, Abstract, Keywords, Introduction, Methodology, Results, Discussion and Conclusions, References.

| Section | Present? |
|---------|---------|
| Title | YES |
| Abstract + Resumen | YES |
| Keywords + Palabras clave | YES (non-compliant count — see J1) |
| 1. Introduction | YES |
| 2. Related Work | YES (supplementary — acceptable) |
| 3. Dataset Description | YES |
| 4. Methodology | YES |
| 5. Results | YES |
| 6. Discussion | YES |
| 7. Conclusions | YES |
| References | YES |

**All required sections present.** PASS.

### 5.5 Required declarations

| Declaration | Present? | Notes |
|-------------|---------|-------|
| CRediT Author Contributions | YES | Complete; single author covers all 14 roles |
| Conflicts of Interest | YES | "No conflicts of interest" stated |
| Funding | YES | "No external funding" stated |
| Data Availability | YES (INCOMPLETE) | Two PENDIENTE placeholders — Zenodo version DOI and HuggingFace URL missing |
| AI Statement | YES | Correctly formatted per template |
| Acknowledgements | YES (INCOMPLETE) | Contains [CONFIRMAR] flag — draft state |

**FLAG J2 — Data Availability section is incomplete.** Two required URLs/DOIs are listed as [PENDIENTE]. A submission with incomplete data availability declarations violates the journal's data policy and open-science commitments. The Zenodo concept DOI (`10.5281/zenodo.19931903`) is provided but the version DOI is missing. Model weights URL is entirely absent.

### 5.6 Figures
The manuscript contains **three figure placeholders**: `[INSERT FIGURE 3]`, `[INSERT FIGURE 5]`, `[INSERT FIGURE 7]`.
No actual figures are embedded in the document.
The journal requires figures in **TIFF or EPS format at ≥ 300 dpi**.
The manuscript makes no mention of figure format or resolution anywhere.

**FLAG J3 — All three figures are missing (placeholder only).** This manuscript cannot be reviewed for figure quality, axis labels, caption completeness, or resolution compliance. Figure submission is a submission requirement; placeholders are not acceptable for a final submission.

**FLAG J4 — No statement of figure format or resolution.** The manuscript does not indicate that figures will be submitted as TIFF/EPS ≥ 300 dpi. The author must prepare figures in the correct format and confirm this in the submission cover letter.

### 5.7 All four tables are missing (placeholder only)
Tables 1–4 are all `[INSERT TABLE]` placeholders. Table 4 contains the key performance metrics in placeholder form. While the data are discussed in the text, reviewers cannot evaluate table formatting, header consistency, footnote placement for the dagger notation, or completeness. This is a draft submitted prematurely.

### 5.8 Double-blind compliance — NON-COMPLIANT
The journal uses **double-blind review**. The submitted manuscript is **not anonymized**:
- Author name appears on page 1: "Luis Esteban Rosas Ruiz¹"
- Institutional affiliation present: "Universidad Industrial de Santander, Bucaramanga, Colombia"
- Email address present: `luis.rosas@correo.uis.edu.co`
- ORCID present: `0000-0003-0233-6336`
- Self-identifying GitHub/Zenodo URLs in Data Availability section identify the author
- Acknowledgements name the author, co-annotator, and thesis director

**FLAG J5 — This is not an anonymized manuscript.** The journal's double-blind policy requires a separate anonymized version. Author names, affiliations, ORCID, email, self-identifying repository URLs, and acknowledgements naming individuals must be removed from the blind copy. A non-anonymized version may be retained as the author's copy.

### 5.9 IEEE references
References generally follow IEEE style with the following exceptions documented in Section 4: wrong DOI in [9], "ibid." in [13], missing DOI in [7], missing URL in [1], non-pinned software citation in [14], and an unresolved entry [VERIFY]. **Partially compliant; six issues.**

---

## 6. TOP 3 REVIEWER ATTACK POINTS

### ATTACK 1: The manuscript is a draft, not a submission

The manuscript contains **six unresolved author flags** (`[VERIFY]`, `[CONFIRMAR]`, `[PENDIENTE]`), **three missing figures**, **four missing tables**, and **two incomplete data availability URLs** — all of which are explicitly marked as pending in the text. Submitting a document with in-text editorial notes (`[VERIFY: κ = 0.91 — confirm source]`, `[CONFIRMAR: OK to describe the supervisor anonymously?]`, `[PENDIENTE: publish Zenodo v2.1.0 and paste version DOI]`) to a Scopus-indexed journal is not a submission — it is sending a draft for external proofreading at the journal's expense. A reviewer encountering "[VERIFY] UIS thesis … authors, year, handle unknown" in the reference list will immediately reject. The editor should desk-reject on this basis alone.

### ATTACK 2: The minador result (mAP@0.50 = 0.985) is scientifically meaningless as an independent benchmark result

The manuscript acknowledges (correctly, in Section 6.3) that all minador test images belong to the MINEIRO_99 contaminated component, meaning every minador test image has a geometrically verified copy in the training split. The 0.985 figure therefore measures the model's ability to recognize near-duplicate images, not its ability to generalize to unseen leaves. Despite the extensive caveats and dagger notation, the headline result — presented in the abstract, conclusions, and all summary tables — includes this number without sufficient prominence. A hostile reviewer will argue: (a) reporting 0.985 at all misleads readers who do not read footnotes; (b) the entire minador class contributes 375/2,020 = 18.6% of test instances, potentially inflating the overall mAP@0.50 = 0.929; (c) no clean minador test performance is available, making the dataset benchmark incomplete for one of its three classes. The author has no rebuttal to (c) except to frame DECAFIA as a two-class benchmark for independent evaluation and a three-class training resource — a substantial repositioning of the paper's claims.

### ATTACK 3: Roya cluster structure undermines the statistical validity of the primary confidence interval

The manuscript's primary class-level CI is for coco [0.801, 0.971], a 17.0 percentage-point interval that is extremely wide and barely informative. For the flagship class — roya (rust), which is the economically critical disease and the class most discussed in the introduction — no cluster CI can be reported because a single leaf group (ROYA_RECORTES) holds 53.1% of all roya test instances. The image-level CI [0.803, 0.874] is provided as "secondary" but ignores within-leaf correlation, which is precisely the correlation that matters for a dataset grouped by leaf. A reviewer will attack: (a) the test set's leaf-group imbalance — 53.1% of roya test instances from a single group is a design flaw, not a footnote; (b) the coco cluster CI [0.801, 0.971] is so wide it is consistent with mAP@0.50 ranging from 80% to 97%, providing essentially no information about expected generalization performance; (c) the combination of a contaminated minador class and an unresolvable roya CI means the paper can claim statistically valid confidence for only one of its three classes, which is insufficient for a dataset paper positioning itself as a benchmark.

---

## 7. OVERALL VERDICT

**MAJOR REVISION** — with strong caveat that the manuscript in its current state should not have been submitted.

### Summary of blocking issues (must be resolved before re-submission)

| # | Issue | Severity |
|---|-------|----------|
| B1 | Six unresolved author flags ([VERIFY]/[CONFIRMAR]/[PENDIENTE]) left in manuscript body and reference list | Blocking |
| B2 | Three figures entirely absent (placeholders only) | Blocking |
| B3 | Four tables entirely absent (placeholders only) | Blocking |
| B4 | Data Availability section incomplete — two missing URLs/DOIs | Blocking |
| B5 | 10 keywords in both languages (limit is 3–5) | Blocking |
| B6 | Manuscript is not anonymized — author name, email, ORCID, affiliation, and self-identifying URLs all present | Blocking |
| B7 | κ = 0.91 inter-annotator agreement reported without verifiable source | Blocking |
| B8 | Reference [VERIFY] UIS thesis — not a reference | Blocking |

### Summary of non-blocking issues (must be addressed in revision)

| # | Issue | Severity |
|---|-------|----------|
| N1 | Abstract states Δ = 0.004 while body states Δ = −0.0038 — inconsistent rounding | Minor |
| N3 | PyTorch version "2.11" — verify or correct | Minor |
| R1 | Reference [9] RoCoLe uses dataset DOI instead of journal article DOI | Moderate |
| R2 | Reference [13] uses non-IEEE "ibid." abbreviation | Minor |
| R3 | Reference [7] missing DOI, page range, conference expansion | Moderate |
| R4 | Reference [1] missing URL/access date | Minor |
| R5 | Reference [14] non-version-pinned software citation | Moderate |
| C3 | Weevil novelty claim search scope insufficient (Roboflow, IEEE DataPort, Kaggle not searched) | Moderate |
| C5 | "November 2026" date embedded in body — should be a relative statement | Minor |
| J2 | TIFF/EPS figures at ≥ 300 dpi not prepared or declared | Moderate |

### Scientific merit

The dataset concept is sound, the integrity audit methodology is commendable and unusually rigorous for a dataset paper, and the statistical transparency (reporting CI non-reportability rather than manufacturing misleading intervals) is praiseworthy. If the blocking issues are resolved and the minador limitation is more forcefully repositioned in the abstract and conclusions, this work has merit for publication as a data/benchmark paper. However, the scientific contribution is weakened by the fact that two of the three classes have methodologically limited test-set evaluations (roya: unresolvable cluster CI due to split imbalance; minador: contaminated, non-independent). The author must either (a) revise the split to fix the roya cluster imbalance or (b) explicitly frame the paper as reporting independent benchmark results for one class only (coco/weevil), with roya and minador as supplementary/indicative results. Presenting all three classes symmetrically in the abstract and conclusions while burying the limitations in §6.3 is not acceptable for a dataset paper claiming to establish benchmark performance.

---

*Review completed: 2026-11-17. All number checks performed against NUMBERS_FOR_MANUSCRIPT.md and cross-verified arithmetically. All string searches performed on extracted document text via python-docx.*
