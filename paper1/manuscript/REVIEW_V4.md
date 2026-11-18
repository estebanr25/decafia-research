# Peer Review — CoffeeLeafCO_manuscript_v4.docx

**Reviewer:** Automated hostile peer review against checklist
**Date:** 2026-11-18
**Files reviewed:**
- `paper1/manuscript/CoffeeLeafCO_manuscript_v4.docx` (main manuscript)
- `paper1/manuscript/CoffeeLeafCO_manuscript_v4_anonymous.docx` (anonymous version)
- `paper1/manuscript/cover_letter_v4.docx` (cover letter)
- `paper1/results/metrics_final.json` (official numbers)

---

## CRITICAL ISSUES (Blockers — must fix before any submission)

---

### CRITICAL-1: Anonymous version — full department name reveals institution identity

**Location:** Anonymous version, Acknowledgements (P98 equivalent)

**Quote:**
> "directed by Prof. [DIRECTOR], Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones, [INSTITUTION]."

**Problem:** The department name "Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones" (E3T) is left unredacted. This uniquely identifies Universidad Industrial de Santander (UIS), Bucaramanga, Colombia. Any reviewer who searches this department name will find the institution in one click, completely defeating double-blind anonymization. Rule 10 requires that the anonymous version must NOT contain institution-identifying information.

**Fix:** Replace with `[DEPARTMENT], [INSTITUTION]` or omit the full department name entirely from the anonymous Acknowledgements.

---

### CRITICAL-2: Anonymous version — reference [17] is entirely absent from references list

**Location:** Anonymous version, References section

**Quote (anon intro):**
> "first introduced in the author's undergraduate thesis [Author, 2024]"

**Problem:** The in-text citation `[Author, 2024]` has no corresponding entry in the references list of the anonymous version. The reference list jumps from `[16]` to `[18]`, with no `[17]`. A reviewer who attempts to verify or locate the thesis cannot do so. Depending on the journal's handling, this dangling citation may be treated as an editorial error or may expose authorship through the missing entry. The citation should be either (a) replaced with a properly anonymized numbered reference entry such as `[17] [Author], "Detección y prevención…," Trabajo de Grado, [INSTITUTION], 2024. [Online]. Available: [URL REMOVED]`, or (b) the in-text `[Author, 2024]` must be changed to `[17]` and an anonymized ref entry added.

**Fix:** Add a properly anonymized `[17]` reference entry to the anonymous version's reference list, keeping the year (2024) and removing authors, institution, and URL.

---

### CRITICAL-3: Internal filesystem path exposed in manuscript body (both versions)

**Location:** Section 4.2, Evaluation Procedure (P49 in main; P49 in anonymous)

**Quote:**
> "All numbers are sourced from paper1/results/metrics_final.json (SHA-256: d8bf05c31ec37923…)."

**Problem:** `paper1/results/metrics_final.json` is a local repository path relative to the author's working directory. It is meaningless to a journal reader, it appears in both the main and anonymous versions, and in the anonymous version it may also identify the repository structure. A submitted manuscript should reference the publicly released evaluation code and data archive, not a local path. The SHA-256 is truncated (shown as `d8bf05c31ec37923…`) and cannot be verified as written — the full hash from the JSON is `d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a`.

**Fix:** Replace with something like: "All numbers are sourced from the evaluation script included in the code repository (DOI/URL) and are reproduced in Table 4." Or provide the full SHA-256 if the hash is to be cited. Remove the local path in both versions.

---

### CRITICAL-4: Annotation protocol contradicts Acknowledgements regarding co-annotator

**Location:** Section 3.3 (P42) vs. Acknowledgements (P98)

**Quote Section 3.3:**
> "Class labels were assigned by the author; disagreements resolved by consulting the Cenicafé phytosanitary identification guide [13]."

**Quote Acknowledgements:**
> "A. F. Salom Medina contributed to image annotation during the thesis."

**Problem:** Section 3.3 implies sole authorial annotation, referring only to "the author" and describing disagreement resolution by reference to a guide (not a second annotator). The Acknowledgements confirm that a second person (A. F. Salom Medina) contributed to annotation. This is a material inconsistency about annotation provenance. If two people annotated, the methods section must say so, explain how disagreements between annotators were resolved, and must NOT claim that only the author assigned labels. Rule 4 states that inter-annotator agreement (κ = 0.91) must not appear, and Rule 5 states the anonymous supervisor must not appear in the annotation section — but the inverse problem also exists: a co-annotator who performed work on the dataset cannot be silently omitted from the methods description. The methods section misrepresents the annotation process.

**Fix:** Either (a) clarify in Section 3.3 that A. F. Salom Medina co-annotated images in the thesis-era dataset and describe how conflicts were resolved (without introducing a κ claim), or (b) if that annotation work is not reflected in the final v2.1.0 dataset, state explicitly that all annotations for the released version were reviewed and finalized by the author alone, citing the thesis for the prior version.

---

## MAJOR ISSUES (Must fix before submission, not strictly blocking)

---

### MAJOR-1: `paper1/results/metrics_final.json` path also present in anonymous version

**Location:** Anonymous version, Section 4.2

**Quote:**
> "All numbers are sourced from paper1/results/metrics_final.json (SHA-256: d8bf05c31ec37923…)."

**Problem:** Identical to CRITICAL-3 above. The local path appears verbatim in the anonymous version, compounding the anonymization failure (a unique repo directory structure could identify the author). This is listed separately because it must be fixed independently for the anonymous file even after the main manuscript is corrected.

**Fix:** Same as CRITICAL-3. Must be corrected in both files.

---

### MAJOR-2: Background false-alarm rate — numeric mismatch between manuscript and JSON

**Location:** Section 5.1, Overall Detection Performance (P57)

**Quote:**
> "Background false alarm rate = 0.0190 (3 of 158 background images triggered at least one detection at conf = 0.50)."

**Problem:** The official value from `metrics_final.json → phase4 → test_set_full → background_far_at_conf050 → rate` is **0.018987**. The manuscript reports **0.0190**. While `0.018987` rounds to `0.0190` at four decimal places, the rounding is non-standard (0.018987 → 0.019 at 3 significant figures, not 0.0190). Rule 2 specifies the official value as 0.018987. Presenting 0.0190 without noting the rounding rule (and given that the manuscript presents other values to 3 decimal places) could cause a reader to believe the rate is exactly 2.0%, not 1.90%. The value must match the JSON or the rounding convention must be explicit.

Additionally, the JSON contains a second `background_far_at_conf050` entry under `full_test` (not `phase4`) with `n_with_detection=4` and `rate=0.025316`. The manuscript uses the phase4 entry (n=3, rate=0.018987), which is correct per the official setting. The existence of a conflicting value in the same JSON file should be documented or the JSON note clarified to prevent future confusion.

**Fix:** Either report as `0.019` (3 dp, standard rounding), or report as `0.0190` and add a footnote that this is rounded from 0.018987. The count "3 of 158" is verified correct.

---

### MAJOR-3: NOVELTY_SEARCH.md cited as a file path in Table 1 caption and Section 6.1

**Location:** Table 1 caption (P29), Section 6.1 (P77)

**Quote (Table 1):**
> "Full search log: NOVELTY_SEARCH.md."

**Quote (Section 6.1):**
> "see NOVELTY_SEARCH.md for the full search log"

**Problem:** `NOVELTY_SEARCH.md` is a local repository file. Submitting a manuscript that cites a local filename (rather than a URL in the released repository, or a supplementary file reference) is unprofessional and unverifiable by reviewers. If the journal requires this evidence, the file must be submitted as a named supplementary file and cited accordingly (e.g., "Supplementary File S1: Novelty Search Log"), or a URL to the released repository file must be provided.

**Fix:** Either (a) reference a supplementary file formally submitted with the manuscript, or (b) provide a URL to the file in the public code repository.

---

### MAJOR-4: Anonymous version — Acknowledgements still exposes institutional school name (see CRITICAL-1) and geography

**Location:** Anonymous version, Acknowledgements

**Quote:**
> "The authors thank the farm owners in [LOCATION], for plantation access"

**Minor positive:** "[LOCATION]" is correctly used here.

**Remaining problem:** As noted in CRITICAL-1, the full department name "Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones" is unredacted. This is repeated as MAJOR because if CRITICAL-1 is considered "blocking," this is a redundant flag; if not treated as a blocker, it remains the most severe de-anonymization risk in the file.

---

### MAJOR-5: Table 1 — DECAFIA dataset year listed as 2026

**Location:** Table 1, DECAFIA row (table cell)

**Quote:**
> `Colombia | 2026 | 2,315 | ...`

**Problem:** The dataset was collected in 2024 (stated in Section 3.1: "during 2024"). Using 2026 (the submission year) as the dataset year is non-standard; the convention for dataset comparison tables is the year the dataset was collected or first released, not the year of the article's submission. All other datasets in the table use their original publication/collection year (2019, 2019, 2020). Using 2026 may confuse readers and is inconsistent with the article text.

**Fix:** Change to 2024 (collection year) or 2025 (if that is the first public release year of the dataset). Do not use the submission year 2026.

---

### MAJOR-6: Section 4.2 cites `model.val()` SHA-256 truncated — cannot be verified

**Location:** Section 4.2 (P49)

**Quote:**
> "SHA-256: d8bf05c31ec37923…"

**Problem:** The SHA-256 hash is truncated with an ellipsis. The purpose of citing a SHA-256 is reproducibility and integrity verification. A truncated hash is useless for that purpose. The full hash from the JSON is `d8bf05c31ec37923ceb9a3224441301ba9d8442e42783841cfe4cfa120549d1a`.

**Fix:** Either include the full 64-character hash or remove the hash claim entirely. If space is a concern, place the full hash in the Data Availability section or repository.

---

## MINOR ISSUES (Should fix)

---

### MINOR-1: Practical Application section — word count borderline

**Location:** Section 8, Practical Application (P90–P92)

**Measurement:** 169 words (counted from manuscript text P90–P92).

**Rule:** Journal requirement specifies 150–200 words. 169 words is within range, but only just. No action required unless the journal counts differently (e.g., excludes headings).

**Status:** Technically compliant. Flag for awareness.

---

### MINOR-2: Abstract footnote dagger (†) for minador CI caveat — word count impact

**Location:** Abstract (P12)

**Quote:**
> "leaf-miner: 0.985†"

**Problem:** The abstract includes a dagger symbol referencing a caveat about minador CI. If the journal's abstract word count excludes footnote text (the footnote itself appears at P88, not in the abstract), this is fine. However, the footnote `†` appears in the abstract without an inline explanation. Some journal style guides require the caveat to be stated in the abstract itself or omit footnote markers from the abstract.

**Fix:** Consider whether the journal allows footnote markers in the abstract. If not, either expand the abstract to include the caveat inline (e.g., "leaf-miner: 0.985 (independent-leaf evaluation not possible; see limitations)") or remove the dagger if the abstract is self-contained.

**Word count:** Abstract = 167 words, well within the 250-word limit.

---

### MINOR-3: Table 1 missing DECAFIA from comparison context

**Location:** Table 1 caption (P29)

**Quote:**
> "No prior dataset includes a weevil (Curculionidae) class. JMuBEN/JMuBEN2 (Kenya, phoma/cercospora/rust/miner/healthy) also reviewed — no weevil class."

**Problem:** JMuBEN/JMuBEN2 are mentioned only in the caption, not in the body of the table. If they were reviewed, they should appear as rows in the comparison table, or the caption should explicitly note "not shown in table but reviewed." As written, it appears the caption acknowledges datasets that are discussed nowhere in the table body, which is inconsistent.

**Fix:** Either add JMuBEN and JMuBEN2 as rows to Table 1, or reword the caption to "Additional datasets reviewed but not tabulated: JMuBEN/JMuBEN2 (Kenya…) — no weevil class."

---

### MINOR-4: Annotation section uses "the author" for a dataset partially annotated by a thesis co-author

**Location:** Section 3.3 (P42)

**Quote:**
> "Class labels were assigned by the author; disagreements resolved by consulting the Cenicafé phytosanitary identification guide [13]."

**Problem:** This is partly repeated from CRITICAL-4. Even if the CRITICAL-4 issue is resolved by clarifying that the released dataset was finalized by one person, the description "disagreements resolved by consulting a guide" implies a solo annotator process. For a solo annotator, "disagreements" is an odd word choice — there is nobody to disagree with. The sentence likely means "uncertain cases were resolved by consulting the guide," which is the appropriate phrasing for a single annotator.

**Fix:** Change to "Ambiguous cases were resolved by consulting the Cenicafé phytosanitary identification guide [13]."

---

### MINOR-5: Data Availability — both Zenodo version DOI and Hugging Face URL placeholders unfilled

**Location:** Data Availability section (P94)

**Quote:**
> "v2.1.0 version DOI [PEGAR DOI ZENODO v2.1.0]). Model weights (best.pt, SHA-256: d8bf05c31ec37923…): [PEGAR URL HUGGING FACE]."

**Problem:** Both placeholders are present and must be filled before submission. This is an editorial completeness issue. Rule 9 requires both placeholders to be present (confirmed) but they must be replaced with actual DOIs/URLs before final submission.

**Status:** Placeholders correctly present per Rule 9. PASS for format compliance. However, flagged here because the manuscript cannot be submitted in final form with unfilled placeholders.

**Fix:** Fill `[PEGAR DOI ZENODO v2.1.0]` with the actual Zenodo version DOI and `[PEGAR URL HUGGING FACE]` with the actual Hugging Face model URL before submission.

---

### MINOR-6: Cover letter discloses supervisor name and institution — anonymization inconsistency

**Location:** Cover letter (P12)

**Quote:**
> "The research derives from an undergraduate thesis at the Universidad Industrial de Santander directed by Prof. Jaime Guillermo Barrero Pérez, whose contributions are fully credited in the Acknowledgements section."

**Problem:** The cover letter is not anonymous (it is a separate document from the anonymous manuscript), so this is not a Rule 10 violation per se. However, the cover letter is typically submitted to the editor only and should not accompany the manuscript sent to reviewers. If the journal uses a combined submission portal where the cover letter may be visible to reviewers, this could break double-blind review. Additionally, the cover letter uses "Prof. Jaime Guillermo Barrero Pérez" (full name), while the manuscript Acknowledgements use "Prof. J. G. Barrero Pérez" (abbreviated). These should be consistent for a formal submission.

**Fix:** Confirm with the journal's submission system whether the cover letter is forwarded to reviewers. If so, anonymize the supervisor name in the cover letter as well. Standardize the supervisor name format between the cover letter and the manuscript.

---

### MINOR-7: Section 4.2 — eval procedure references local path in both versions

This is duplicated from CRITICAL-3/MAJOR-1. No new text needed — the fix is the same.

---

### MINOR-8: Annotation section — no mention of polygon annotation tool version inconsistency

**Location:** Section 3.3 (P42)

**Quote:**
> "All images were annotated using VGG Image Annotator (VIA) v2.0 [11] with polygon regions generated by Segment Anything Model (SAM) [12]"

**Problem:** SAM is used for polygon generation in "interactive point-prompt mode." The SAM version is not specified (ViT-H, ViT-L, ViT-B, or SAM2?). For reproducibility, the SAM model variant and checkpoint should be stated. This is a minor reproducibility gap.

**Fix:** Add SAM model variant (e.g., "SAM ViT-H checkpoint, sam_vit_h_4b8939.pth") to the annotation protocol.

---

## PASS ITEMS (Explicitly verified)

The following items were checked and confirmed compliant:

**PASS-1: Banned strings — all clear.**
Searched for all ten banned strings ("92.4%", "76.6%", "2,786", "Coccinellidae", "Pseudococcidae", "leakage-free", "sin fuga", "no leakage", "κ = 0.91", "k = 0.91") in both the main manuscript and anonymous version. None found.

**PASS-2: Weevil novelty claim properly hedged.**
Section 6.1: "To the best of the author's knowledge, none of the public coffee-leaf datasets reviewed for this work includes a class for weevil (Curculionidae) feeding damage." The required hedge phrase is present. The claim is not stated as absolute.

**PASS-3: Reference [17] — year and handle correct (main manuscript).**
Reference [17]: year = 2024 (confirmed), handle = `20.500.14071/42486` (confirmed). Both correct per Rule 6.

**PASS-4: No inter-annotator agreement claim (κ or kappa).**
No occurrence of "inter-annotator," "kappa," "Cohen," or the κ symbol found in either version. Rule 4 complied with.

**PASS-5: No banned κ = 0.91 or k = 0.91.**
Explicitly confirmed absent (see PASS-1).

**PASS-6: Core numerical values verified against JSON.**
All values in Table 4 and the abstract verified against `metrics_final.json`:
- mAP@0.50 = 0.929 ✓ (JSON: 0.929377)
- mAP@0.50:0.95 = 0.734 ✓ (JSON: 0.734368)
- roya mAP@0.50 = 0.841 ✓ (JSON: 0.841307)
- coco mAP@0.50 = 0.962 ✓ (JSON: 0.961786, rounds to 0.962)
- minador mAP@0.50 = 0.985 ✓ (JSON: 0.985040)
- coco cluster CI [0.801, 0.971] ✓ (JSON: lo=0.8012, hi=0.9713)
- roya image-level CI [0.803, 0.874] ✓ (JSON: lo=0.8033, hi=0.8735)
- filtered test mAP@0.50 = 0.926 ✓ (JSON: 0.925574)
- delta = -0.0038 ✓ (JSON: -0.0038030)
- GT instances: roya=825, coco=820, minador=375 ✓
- Per-class precision/recall/F1 at conf=0.50: all verified ✓

**PASS-7: No supervisor (Barrero) in annotation section.**
Section 3.3 makes no reference to the supervisor. Barrero is mentioned only in the Acknowledgements. Rule 5 complied with. (Note: CRITICAL-4 flags a different issue — the co-annotator is inconsistently described.)

**PASS-8: Cover letter — no same-day preprint promise.**
The cover letter requests authorization before posting, explicitly stating "I will not post any preprint prior to receiving such authorization." Rule 8 complied with.

**PASS-9: Abstract word count.**
167 words. Well within the ≤250 word limit.

**PASS-10: Keywords count.**
5 keywords ("coffee leaf disease; object detection; YOLOv8; grouped split; data integrity"). Within the required 3–5 keyword range.

**PASS-11: Highlights — all within 85 characters.**
- Highlight 1: 82 characters ✓
- Highlight 2: 76 characters ✓
- Highlight 3: 82 characters ✓
- Highlight 4: 74 characters ✓
- Highlight 5: 76 characters ✓

**PASS-12: Data Availability — both required placeholders present.**
`[PEGAR DOI ZENODO v2.1.0]` and `[PEGAR URL HUGGING FACE]` both present in Data Availability section. Rule 9 format requirement met. (Content must still be filled — see MINOR-5.)

**PASS-13: AI-use statement present before References.**
Section "Statement on Artificial Intelligence" (P103–P104) appears before the References section. Rule 9 complied with.

**PASS-14: Anonymous version — primary PII removed.**
Confirmed absent from anonymous version: author name ("Luis Esteban Rosas Ruiz"), ORCID (0000-0003-0233-6336), email, "Bucaramanga", "El Socorro", "estebanr25", "Universidad Industrial de Santander", thesis URL (noesis.uis.edu.co), thesis handle (20.500.14071). Author line uses `[AUTHOR]`, institution uses `[INSTITUTION]`.

**PASS-15: Anonymous version — GitHub estebanr25 URL removed.**
Data Availability in the anonymous version replaces the GitHub source code URL with `[link removed for double-blind review]`. Rule 10 complied with for this item.

**PASS-16: Practical Application word count.**
169 words. Within the required 150–200 word range.

**PASS-17: minador CI — not reported in manuscript.**
Section 4.4 and Fig. 7 caption explicitly state minador CI is not shown. This is consistent with the JSON flag `reported: False` for minador cluster CI due to the MINEIRO_99 contamination. Compliant with the JSON's own reporting instruction.

---

## SUMMARY TABLE

| ID | Severity | Description |
|----|----------|-------------|
| CRITICAL-1 | CRITICAL | Anon version: unredacted department name identifies UIS |
| CRITICAL-2 | CRITICAL | Anon version: reference [17] entry missing from references list |
| CRITICAL-3 | CRITICAL | Local path `paper1/results/metrics_final.json` in both manuscript versions |
| CRITICAL-4 | CRITICAL | Annotation protocol contradicts Acknowledgements re: co-annotator |
| MAJOR-1 | MAJOR | Same as CRITICAL-3 specifically for anonymous version (must fix independently) |
| MAJOR-2 | MAJOR | Background FA rate: 0.018987 (JSON) vs. 0.0190 (ms) — rounding not explicit |
| MAJOR-3 | MAJOR | NOVELTY_SEARCH.md cited as local filename; must be supplementary file or URL |
| MAJOR-4 | MAJOR | Anon Acknowledgements: unredacted department name (see CRITICAL-1) |
| MAJOR-5 | MAJOR | Table 1: DECAFIA year listed as 2026 (submission year), should be 2024 |
| MAJOR-6 | MAJOR | SHA-256 hash truncated (d8bf05c31ec37923…) — useless for verification |
| MINOR-1 | MINOR | Practical Application: 169 words — within range, flagged for awareness |
| MINOR-2 | MINOR | Abstract: dagger footnote marker without inline explanation |
| MINOR-3 | MINOR | JMuBEN/JMuBEN2 referenced in caption but not tabulated in Table 1 body |
| MINOR-4 | MINOR | "disagreements resolved" implies multi-annotator; should be "ambiguous cases" |
| MINOR-5 | MINOR | Data Availability: two DOI/URL placeholders unfilled (not yet submittable) |
| MINOR-6 | MINOR | Cover letter: supervisor full name vs. abbreviated name inconsistency |
| MINOR-7 | MINOR | (Duplicate of CRITICAL-3/MAJOR-1 for anonymous version) |
| MINOR-8 | MINOR | SAM model variant and checkpoint not specified in annotation protocol |

---

*End of review.*
