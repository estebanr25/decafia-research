# DECAFIA Paper 1: close the evidence package and produce the submission-ready manuscript (one session)

> **For Esteban:** save as `SESSION_MANUSCRIPT.md` in `C:\Users\luise\temp\decafia-research`. Open **Claude Code on your PC** in that folder, select Fable, and send:
> *"Read SESSION_MANUSCRIPT.md and execute it end to end. Do not stop to ask me questions; mark anything only I can decide as [CONFIRMAR] and list it in the final report."*

---

## 0. Context

- Repo: `C:\Users\luise\temp\decafia-research`, branch `split-v2` (sessions SESSION_SPLIT_V2 and SESSION_FIX_V2 are done). Read `CLAUDE.md`, `split_v2/REPORT.md`, `split_v2/REPORT_FIX.md`, `paper1/RESULTS_FINAL.md`, `paper1/NUMBERS_FOR_MANUSCRIPT.md`, `paper1/MANUSCRIPT_CHANGES.md`, and `paper1/FIGURES.md` first.
- **Final state:** Path B. Official model `decafia_grouped_v1` on `split_grouped_v1`; test mAP50 0.929 / mAP50-95 0.734 (NMS iou = 0.7). Minador test images share group membership with training images through geometrically verified transformed copies, so minador performance cannot be read as performance on independent held-out leaves.
- **Target:** *Ingeniería e Investigación* (Universidad Nacional de Colombia), submission before 2026-11-30, same-day preprint on Zenodo (no arXiv endorsement available).
- **Esteban is the sole author.** Andrey Fernando Salom Medina (thesis co-author, image annotation) and Prof. Jaime Guillermo Barrero Pérez (thesis director) did not respond to requests to review or approve the manuscript. Under the journal's authorship criteria (substantial contribution + drafting/revising + approval of the final version), they can't be listed as authors without approval. Their contributions **must** be acknowledged explicitly so there is no ghost authorship.

## 1. Hard rules

1. Never modify, move, or delete dataset folders, model files, split lists, or the original manuscript draft. Work on copies in `paper1/manuscript/`.
2. **Every number in the manuscript comes from `paper1/results/metrics_final.json` through `NUMBERS_FOR_MANUSCRIPT.md`.** No hand-typed numbers. Report metrics with 3 decimals.
3. **Banned strings** in every output: 92.4 / 76.6 and the 2,786-image dataset; Coccinellidae / Pseudococcidae for coco (coco = Curculionidae, *Compsus* sp. / *Epicaerus* sp.); "leakage-free", "sin fuga", "no leakage". Write val mAP values as decimals, never as percentages.
4. **Numbers not produced by this pipeline need a file behind them.** Any statistic in the draft that is not in `metrics_final.json`, e.g. an inter-annotator agreement value (Cohen's κ), polygon counts, capture dates, altitude, or the phone model, must be backed by a file in the repo or an explicit statement from Esteban in this brief. Otherwise remove it or mark it `[VERIFY]`, and list it. A κ value that appeared in an older draft has no known source file: treat it as unverified.
5. **References:** verify every reference against Crossref or doi.org (title, authors, year, venue, DOI). Never invent a DOI, author, page range, or year. Anything that can't be verified is marked `[VERIFY]` and listed.
6. **No installs** in the research Python environment. For document work you may create an isolated venv inside the repo (`.venv-manuscript`, gitignored) and install only document tools there (e.g. `python-docx`). Use pandoc / LibreOffice / Word only if they're already installed.
7. Don't submit anything, send emails, or upload anywhere. Git: commit atomically, push. Fail loudly; don't stop to ask; log decisions.

---

## 2. Phases

### Phase 1: Close the evidence package (branch `split-v2`)
1. Confirm `paper1/VERIFICATION.md` reports a full pass. If not, fix and re-run the independent verification first.
2. **Remove the minador confidence interval** from everything the manuscript uses (`NUMBERS_FOR_MANUSCRIPT.md`, `RESULTS_FINAL.md`, figure captions). Reporting an interval contradicts the statement that minador wasn't evaluated on independent leaves. In the JSON, keep the value but add `"reported": false` with the reason. State which clusters the bootstrap used (v1 groups or verified components), and report that in the methods text.
3. **Roya check:** find out whether the cluster holding 53.1% of roya test instances overlaps the verified MINEIRO component, i.e. whether any roya test images (e.g. Silva et al. roya images) share a verified component with training images.
   - If yes: report roya metrics with and without those images, and extend the caveat to that portion of roya.
   - If no: say so in the report.
4. Make the component sizes consistent (290 / 339 before verification, 272 after). The manuscript uses only the verified number, with a one-line explanation of how it was obtained.
5. Re-run the independent verification subagent. When it passes, **merge `split-v2` into `main`** with a merge commit and push.

### Phase 2: Package for the claude.ai project
Create `paper1/for_claude_project/` with:
- the updated `CLAUDE.md`;
- `RESULTS_FINAL.md` (to replace the old project `RESULTS.md`, which comes from the leaky baseline);
- the new figure PNGs that replace `confusion_matrix_normalized.png`, `training_curves.png`, `pr_curves.png`, and `test_predictions_grid.png`;
- `PROJECT_INSTRUCTIONS.txt`: the full replacement text for both the project **description** and the project **instructions**. Both currently say "split agrupado sin fuga"; change to "split agrupado por hoja", update the official-numbers sentence, and add the minador caveat in one line.
- `README.txt`: exactly what Esteban uploads, deletes, and pastes, in three steps.

### Phase 3: Journal requirements
1. Fetch and read the *Ingeniería e Investigación* author guidelines, editorial policy, ethics policy (https://revistas.unal.edu.co/index.php/ingeinv/etica), data policy, and the submission template from https://revistas.unal.edu.co/index.php/ingeinv. Download the template.
2. Write `paper1/manuscript/JOURNAL_REQUIREMENTS.md`: article type and structure, length limits, abstract and keyword rules, reference style, figure and table formats, blind-review/anonymization requirements, data and preprint policy, AI-use disclosure rule, required declarations (CRediT, conflicts, funding, data availability), and cover-letter requirements. Quote the source URL for each item.
3. If the template or a guideline can't be downloaded, report it and follow the editorial policy text.

### Phase 4: Manuscript
1. **Locate the latest draft:** search under `C:\Users\luise` for `Manuscrito_IngInv*` and other DECAFIA/CoffeeLeaf-CO manuscript `.docx` files. List all candidates with path, date, and size. Use the most recent CoffeeLeaf-CO draft for Ingeniería e Investigación and record the choice. Work on a copy.
2. **Apply `MANUSCRIPT_CHANGES.md` in full**, plus the Phase 1 outcomes. Update every number from `NUMBERS_FOR_MANUSCRIPT.md`. Specifically:
   - the split is "grouped by leaf", never "leakage-free";
   - correct the pHash sentence;
   - the residual-copy paragraph and the sensitivity check (full test vs filtered test, labeled as sensitivity, not a corrected metric);
   - the minador caveat, wherever minador results appear (abstract, results, discussion, conclusions);
   - the roya caveat if Phase 1 requires it;
   - intervals only where they're valid;
   - the grouping rule described as conservative by design, with the limitation that capture-series blocks for third-party images are an assumption, not verified identity (future work).
3. **Authorship and declarations:**
   - sole author Luis Esteban Rosas Ruiz, Electronic Engineer, ORCID 0000-0003-0233-6336;
   - **affiliation (decided):** Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T), Universidad Industrial de Santander, Bucaramanga, Colombia (the institution where the research was carried out, as an undergraduate thesis). If the journal's guidelines require a *current* affiliation distinct from where the work was done, follow them and flag it in the report;
   - **corresponding e-mail:** luis.rosas@correo.uis.edu.co;
   - CRediT roles for the single author;
   - **Acknowledgments:** a statement that the work derives from the undergraduate thesis of L. E. Rosas Ruiz and A. F. Salom Medina, directed by Prof. J. G. Barrero Pérez (UIS); A. F. Salom Medina credited for image annotation during the thesis; Prof. Barrero credited for thesis direction. **The agronomist and the agroindustrial engineer who supervised annotation do not want to be named:** never write their names anywhere. In Methods, the supervision may be described anonymously only (e.g. "reviewed by an agronomist with coffee experience"); add a `[CONFIRMAR: OK to describe anonymously?]` marker on that sentence;
   - **funding:** "This research received no external funding.";
   - conflicts of interest (none declared unless the draft states otherwise), AI-use disclosure written to the journal's rule, and data availability (Zenodo concept DOI 10.5281/zenodo.19931903; mark `[PENDIENTE: version DOI of v2.1.0 with split_grouped_v1]`; code at github.com/estebanr25/decafia-research; model on Hugging Face `[PENDIENTE: upload of decafia_grouped_v1_best.pt]`).
4. **Related work:** add and verify at least:
   - Zuñiga Cajas et al. (2025), coffee leaf rust severity with deep learning, *Inteligencia Artificial* 28(76), DOI 10.4114/intartif.vol28iss76pp200-222;
   - the Silva et al. dataset (DOI 10.17632/vfxf4trtcg.5), stating that its description reports most photos taken in a laboratory on a white background;
   - the UIS undergraduate thesis on AI for coffee disease risk in the Noesis repository (verify title, authors, year);
   - a search for public datasets with Curculionidae damage on coffee.
   State clearly how CoffeeLeaf-CO differs from each.
5. **Figures and tables:** insert the new figures with captions from `FIGURES.md` (numbers rendered from JSON), in the template's required format and resolution.
6. **Format:** move everything into the journal template, check the word count against the limit, and apply the reference style. Produce an anonymized version too if the journal uses blind review.
7. **Cover letter to the editor** (`paper1/manuscript/cover_letter.docx`): sole authorship; originality and no simultaneous submission; same-day preprint on Zenodo (only if the journal's policy allows it; quote the policy); the dataset's contribution in 3 sentences.

### Phase 5: Hostile review
Spawn a **fresh subagent** that receives only the journal requirements, `NUMBERS_FOR_MANUSCRIPT.md`, and the final manuscript. It acts as the toughest reviewer for this journal and writes `paper1/manuscript/REVIEW.md`. It must check:
- every number against the JSON;
- every claim for support;
- every reference for verification status;
- banned strings;
- compliance with each item in `JOURNAL_REQUIREMENTS.md`;
- what a reviewer would attack first.

Fix everything fixable and re-run the review once.

---

## 3. Final report: `paper1/manuscript/SUBMISSION_REPORT.md`

Page one:
1. **Status:** ready to submit, or what blocks it.
2. **Files:** final `.docx` (and PDF if a converter is installed), anonymized version if required, cover letter, figure files.
3. **[CONFIRMAR] list for Esteban,** ordered by urgency.
4. **Remaining steps outside Claude Code,** in order:
   1. update the claude.ai project with `paper1/for_claude_project/`;
   2. publish Zenodo v2.1.0 and paste its version DOI into the manuscript;
   3. upload the model to Hugging Face;
   4. post the Zenodo preprint;
   5. submit to the journal the same day.
5. The top 3 reviewer risks still standing, and how the manuscript addresses each.

Then details. Push.
