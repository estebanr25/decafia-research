# SUBMISSION_REPORT.md — SESSION_MANUSCRIPT

---

## Page 1: Five Answers

### 1. Status

**BLOCKED — not yet ready to submit.**

The manuscript is structurally complete and passes two rounds of hostile review. All fixable issues have been resolved. What blocks submission are items only Esteban can resolve (see Section 3 below).

### 2. Files produced

| File | Description |
|------|-------------|
| `paper1/manuscript/CoffeeLeafCO_manuscript_v3.docx` | Final manuscript (English; submit this) |
| `paper1/manuscript/CoffeeLeafCO_manuscript_v3_anonymous.docx` | Anonymized version (double-blind; author names, email, ORCID, institution, location, repos replaced) |
| `paper1/manuscript/cover_letter.docx` | Cover letter for the editor |
| `paper1/manuscript/JOURNAL_REQUIREMENTS.md` | Full journal requirements (fetched 2026-11-18) |
| `paper1/manuscript/ingeinv_template.docx` | Downloaded journal template |
| `paper1/manuscript/REVIEW.md` | First hostile review |
| `paper1/manuscript/REVIEW_V2.md` | Second review (confirms all 8 fixable issues resolved) |
| `paper1/for_claude_project/` | Package to update the claude.ai project |
| `paper1/figures/figure7_bootstrap_intervals.png` | Regenerated figure (minador CI removed) |

### 3. [CONFIRMAR] list for Esteban (ordered by urgency)

1. **[CONFIRMAR — BLOCKS SUBMISSION] κ = 0.91 inter-annotator agreement.** Section 3.3 currently reads: "a κ value from an earlier draft of this work has no source file in the repository and is marked [VERIFY: κ = 0.91 — confirm source]." Either (a) find the source calculation and add it to the repo, or (b) remove the kappa claim and replace with a qualitative statement about the resolution protocol. A submitted manuscript cannot contain an unverified κ.

2. **[CONFIRMAR — BLOCKS SUBMISSION] Anonymous supervisor.** Section 3.1 and Acknowledgements both contain "[CONFIRMAR: OK to describe the supervisor anonymously?]". If yes, remove the brackets and keep "reviewed by an agronomist with coffee experience." If no, the supervisor should be named (requires their approval) or the sentence removed.

3. **[CONFIRMAR — BLOCKS SUBMISSION] Zenodo v2.1.0 version DOI.** The Data Availability section contains "[PENDIENTE: publish Zenodo v2.1.0 and paste version DOI]". You must publish the new Zenodo version and paste the version DOI before submitting.

4. **[CONFIRMAR — BLOCKS SUBMISSION] Hugging Face model upload.** Data Availability contains "[PENDIENTE: upload to Hugging Face estebanr25/decafia and paste URL]". The model must be uploaded before submitting.

5. **[CONFIRMAR] Preprint policy.** The cover letter asks: "does same-day Zenodo preprint require prior Editorial Committee approval, or is disclosure at submission sufficient?" The ethics page says "subject to a prior evaluation by the Editorial Committee." Check with the editorial team by email before posting the preprint.

6. **[CONFIRMAR] No Curculionidae coffee dataset.** Section 6.1 notes "[VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists in public repositories]." Search Google Dataset Search, Roboflow Universe, IEEE DataPort, and Kaggle for "Compsus coffee" / "Epicaerus coffee" / "weevil coffee dataset" before submitting the novelty claim.

7. **[CONFIRMAR] UIS thesis reference.** The [VERIFY] UIS thesis entry was removed from the reference list (it had no title/authors/year/handle). If you want to cite your own thesis, find its Noesis handle and add it as a proper reference.

### 4. Remaining steps outside Claude Code (in order)

1. **Resolve all 7 [CONFIRMAR] items above**, in order.
2. **Insert actual figures** into the manuscript: replace the three `[INSERT FIGURE X]` placeholders with the PNG files from `paper1/figures/`. Note: journal requires TIFF or EPS ≥ 300 dpi — convert PNGs or regenerate at higher resolution.
3. **Insert actual tables** (Tables 1–4): compose them in Word using the template's table styles.
4. **Update the claude.ai project** using `paper1/for_claude_project/README.txt` instructions.
5. **Publish Zenodo v2.1.0**: add `CORRECTIONS.md` documenting the 49 contaminated test images, include `splits/grouped_v1/` files and `split_v2/v1_test_exclusion_list.csv`. Paste the version DOI into the manuscript.
6. **Upload model to Hugging Face**: `decafia_grouped_v1_best.pt` (SHA-256: d8bf05c3...). Paste URL into manuscript.
7. **Post Zenodo preprint** (only after confirming preprint policy with editorial team).
8. **Submit to Ingeniería e Investigación** via OJS at https://revistas.unal.edu.co/index.php/ingeinv. Use the anonymous version for the submission. Upload cover letter separately.
9. **Submit on the same day** as the preprint (or as soon as the editorial committee confirms preprint timing).

### 5. Top 3 reviewer risks still standing

**Risk 1: Minador result is scientifically meaningless as an independent benchmark.**
The reviewer will note that mAP@0.50 = 0.985 for leaf-miner detection is from a contaminated test set and cannot be interpreted as performance on independent held-out leaves. The manuscript addresses this with a prominent caveat (†) and Section 6.3, but a hostile reviewer may argue the entire minador evaluation should be excluded or that the split should be restructured. Response: Section 4.3 explains why restructuring is impossible (272-image component exceeds 10% threshold); mAP@0.50 for rust and weevil (the more practically significant classes) is based on clean test images.

**Risk 2: Roya CI is not from the cluster bootstrap.**
The 95% CI for roya [0.803, 0.874] is image-level, labeled "secondary (ignores within-leaf correlation)." A reviewer may consider this uninformative. The manuscript explains why the cluster CI is unreportable (53.1% single group), and the coco cluster CI [0.801, 0.971] shows the CI is quite wide, consistent with limited test coverage per cluster. Response: Section 4.4 explains the cluster validity check explicitly; no CI can be more precise than the data support.

**Risk 3: Tables and figures are placeholder text.**
The current .docx has `[INSERT TABLE X]` and `[INSERT FIGURE X]` placeholders — reviewers receive a visually incomplete manuscript. This must be resolved before submission. All figure files exist in `paper1/figures/`; tables must be built manually in Word.

---

## Details

### Phase 1 outcome: Evidence package closed
- VERIFICATION_FIX.md: all 5 checks PASS (iou=0.7, model identity, CI validity, numbers vs JSON, banned strings)
- VERIFICATION_MANUSCRIPT.md: all 5 checks PASS (minador CI suppressed, roya cluster documented, numbers match)
- split-v2 merged into main; both branches pushed
- CLAUDE.md restored and updated

### Phase 2 outcome: claude.ai project package complete
- `paper1/for_claude_project/` contains: CLAUDE.md, RESULTS_FINAL.md, 4 figure PNGs, PROJECT_INSTRUCTIONS.txt, README.txt

### Phase 3 outcome: Journal requirements documented
- Language: English only (abstracts also in Spanish)
- Limit: 6,000 words (current: 3,386)
- Reference style: IEEE
- Figures: TIFF or EPS, ≥ 300 dpi
- Double-blind review → anonymous version required
- Preprint: allowed in non-commercial repositories after editorial committee evaluation

### Phase 4 outcome: Manuscript built
- Manuscript structured following journal template
- All numbers from metrics_final.json via NUMBERS_FOR_MANUSCRIPT.md
- MANUSCRIPT_CHANGES.md fully applied
- CRediT, Conflicts, Funding, Data Availability, AI Statement included
- Authorship: sole author Luis Esteban Rosas Ruiz, E3T, UIS
- Acknowledgements: thesis origin, A. F. Salom Medina (annotation), Prof. J. G. Barrero Pérez (direction)
- Two [CONFIRM] items remain in body (supervisor anonymity, κ source)

### Phase 5 outcome: Two rounds of hostile review
- Round 1: 6 blocking failures, 15 flags
- Round 2 fixes: keywords 10→5, banned strings absent, delta consistent, RoCoLe DOI fixed, ibid removed, anonymous PII removed, [VERIFY] UIS thesis removed
- Round 3 fixes (Category B): Somanna et al. DOI added, FNC URL added, YOLOv8 version-pinned citation, annotation ambiguity clarified
- Remaining (external only): [VERIFY] κ, [CONFIRMAR] supervisor, [PENDIENTE] Zenodo/HF, [VERIFY] weevil novelty, [CONFIRMAR] preprint policy

### Numbers used throughout (source: metrics_final.json SHA-256 prefix bc4fbb2b)

| Metric | Value |
|--------|-------|
| mAP@0.50 (full, 356 images) | 0.929 |
| mAP@0.50:0.95 (full) | 0.734 |
| mAP@0.50 roya | 0.841 |
| mAP@0.50 coco | 0.962 |
| mAP@0.50 minador† | 0.985 |
| mAP@0.50 filtered (307 images) | 0.926 |
| Δ filtered vs full | −0.0038 |
| Coco CI (cluster, 95%) | [0.801, 0.971] |
| Roya CI (image-level, secondary) | [0.803, 0.874] |
| Background FA rate | 0.019 |
| Contaminated test images | 49 (13.8%) |

†Cannot be interpreted as performance on independent held-out leaves.
