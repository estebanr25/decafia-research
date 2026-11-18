# DECAFIA Paper 1: final pass to a submittable package (one session)

> **For Esteban:** save as `SESSION_FINAL_PASS.md` in `C:\Users\luise\temp\decafia-research`. Open **Claude Code on your PC** in that folder, select Fable, and send:
> *"Read SESSION_FINAL_PASS.md and execute it end to end on main. Do not stop to ask me questions."*

---

## 0. Context

`SESSION_MANUSCRIPT.md` produced `paper1/manuscript/CoffeeLeafCO_manuscript_v3.docx`, an anonymous version, and a cover letter, but left 7 open items and placeholder tables/figures. Esteban has decided the open items below. All rules from `SESSION_MANUSCRIPT.md` Section 1 still apply: numbers only from `metrics_final.json` via `NUMBERS_FOR_MANUSCRIPT.md`, 3 decimals, banned strings, verified references only, work on copies, fail loudly, don't stop to ask. The output is `v4`.

## 1. Decisions to apply (Esteban, 2026-11-18)

1. **Remove the κ = 0.91 claim** and any sentence that depends on it. No source file exists.
2. **Remove the anonymous-supervisor sentence entirely.** The two annotation supervisors don't want to appear, even anonymously. Describe annotation only as what the author did (tools, guidelines, Cenicafé reference for symptoms).
3. **Cite the author's own undergraduate thesis.** The thesis in the UIS Noesis repository is Esteban's own:
   - Title: *Detección y Prevención de Riesgo de Enfermedades en Plantaciones de Café mediante Inteligencia Artificial*
   - Authors: L. E. Rosas Ruiz and A. F. Salom Medina
   - Director: J. G. Barrero Pérez
   - Degree: Trabajo de grado, Ingeniería Electrónica, UIS
   - PDF: https://noesis.uis.edu.co/bitstreams/545a6d5d-0748-4cc1-a739-6e5aa3b99ed2/download
   Find the year and the item's handle/landing page; mark `[VERIFY]` if not found. Then:
   - add it to the references and cite it where the work's origin is described;
   - add one sentence stating that this article **supersedes** the results reported in the thesis, which used an earlier version of the dataset later corrected for source attribution, coco taxonomy, and same-leaf leakage. Don't print the old numbers;
   - in the anonymous version, replace this citation with `[Author, year]` and remove it from the reference list, following standard double-blind practice.
4. **Novelty claim about Curculionidae.** Replace any "first publicly available" wording with a hedged, checkable statement. For example: to the best of the author's knowledge, none of the public coffee-leaf datasets reviewed includes a class for weevil (Curculionidae) feeding damage. List the datasets reviewed and their classes, with verified references: Silva et al. (rust, leaf miner), BRACOL (leaf miner, rust, brown leaf spot, cercospora), JMuBEN/JMuBEN2 (phoma, cercospora, rust, miner, healthy), RoCoLe (rust, red spider mite, healthy). Add the month and year of the search. Also search Kaggle, IEEE DataPort, and Roboflow Universe for coffee datasets with a weevil/Curculionidae/"vaquita" class, and record queries and results in `paper1/manuscript/NOVELTY_SEARCH.md`. If one exists, rewrite the claim accordingly.
5. **Preprint:** the journal allows preprints in non-commercial repositories only after prior evaluation by its Editorial Committee, and may regard internet distribution as prior publication. So: **no same-day preprint.** Rewrite the cover letter to request the Editorial Committee's authorization to post a preprint on Zenodo, and remove every statement that a preprint has been or will be posted on submission day.

## 2. Complete the manuscript to the journal's format

Check every item against `paper1/manuscript/JOURNAL_REQUIREMENTS.md` and the editorial policy:

- **Tables:** build every table in Word from `metrics_final.json` and the dataset-composition JSON. No placeholders, numbers rendered from JSON.
- **Figures:** embed the final figures in the manuscript for review. Also export each figure as **TIFF at ≥ 300 dpi** (LZW compression), named `Fig. 1.tif`, `Fig. 2.tif`, … in `paper1/manuscript/figures_submission/`.
- **Abstract ≤ 250 words; a "practical application" section of 150–200 words; highlights of ≤ 85 characters each.** Add any that are missing and report the counts.
- **AI-use statement** at the end of the manuscript, **before the References**, following the journal's sample wording. Name the tools used and their purpose, and state that the author takes full responsibility for the content.
- **Word count ≤ 6,000 including text, references, figures, and tables** (the journal counts all of them). Report the count with that definition.
- **Content check:** compare v4 section by section with the longest earlier draft (earlier drafts ran to about 5,400 words; v3 is about 3,400). List any methods/results content that disappeared, and restore anything needed for reproducibility.
- **Data availability:** Zenodo concept DOI 10.5281/zenodo.19931903; version DOI as `[PEGAR DOI ZENODO v2.1.0]`; code at github.com/estebanr25/decafia-research; model as `[PEGAR URL HUGGING FACE]`. Use exactly these two placeholders so Esteban can find them.

## 3. Anonymous version, done properly

From the final v4:
- remove name, ORCID, e-mail, affiliation, acknowledgments, and the CRediT statement;
- anonymize self-citations (thesis; Zenodo, GitHub, and Hugging Face links → `[link removed for double-blind review]`);
- **clear the Word document properties** (author, last modified by, company, comments, template path) in both versions' metadata, and check for tracked changes or comments left in the file;
- search the anonymous file (text, headers, footers, properties, image metadata) for "Rosas", "Salom", "Barrero", "estebanr25", "luise", "UIS", "Santander", "Socorro", and the ORCID. Report every hit and remove the identifying ones. Field location may stay as "northeastern Colombia" if needed for science.

## 4. Zenodo v2.1.0 package

Prepare `zenodo_v2.1.0/`:
- the `split_grouped_v1` list files and `assignments.csv`;
- a `CORRECTIONS.md` explaining what changed since v2.0.0 (grouped split, residual transformed copies and the minador caveat, iou = 0.7 evaluation setting);
- the CC BY 4.0 attribution note for crops derived from Silva et al.;
- an updated dataset card / README, and checksums;
- `ZENODO_DESCRIPTION.txt`: ready-to-paste description, keywords, related identifiers, and version notes.

Don't upload anything.

## 5. Final checks

- Re-run the hostile reviewer subagent (fresh) on v4: numbers vs JSON, banned strings, journal-requirement compliance, anonymization. Fix and re-run once.
- Export PDF copies if Word or LibreOffice is installed.

## 6. Report: `paper1/manuscript/FINAL_REPORT.md` (one page)

1. Files to submit (exact paths): anonymous manuscript, figures folder, cover letter, and the non-anonymous version for Esteban's records.
2. Counts: abstract, practical application, highlights, total words (journal definition).
3. Esteban's remaining steps, in order:
   1. reserve or publish the Zenodo v2.1.0 version DOI and upload the model to Hugging Face;
   2. replace the two placeholders in both versions;
   3. update the claude.ai project from `paper1/for_claude_project/`;
   4. submit through the journal's OJS with the anonymous version.
4. Anything still unresolved.

Commit and push to `main`.
