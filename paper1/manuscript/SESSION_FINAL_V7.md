# CoffeeLeaf-CO Paper 1: last fixes after external review of v6 → v7

> **For Esteban:** fill in Section 0 if you know the answers (1 minute). Save as `SESSION_FINAL_V7.md` in `C:\Users\luise\temp\decafia-research`, open **Claude Code on your PC** there, select Fable, and send:
> *"Read SESSION_FINAL_V7.md and execute it end to end on main. Do not stop to ask me questions."*

## 0. Esteban's answers (a dataset paper should state capture date and device; leave `?` if unsure and they stay out)

```yaml
CAPTURE_YEARS: 2022–2023        # confirmed by Esteban on 2026-11-19
PHONE_MODEL: Xiaomi Poco X3 Pro # confirmed by Esteban on 2026-11-19
```

## 1. Rules

All earlier rules still apply: numbers only from repository files, 3 decimals, banned strings, Scheme A naming, work on copies, fail loudly, don't stop to ask. Input: `CoffeeLeafCO_manuscript_v6.docx` and its anonymous version. Output: v7 of both, plus `FINAL_REPORT_V7.md`. **The v6 report claimed checks passed that did not.** Every check in Section 7 must be done by a script that inspects the actual `.docx` XML, and its output pasted into the report.

## 2. Blocking: figures are not in the documents

Both v6 `.docx` files contain **zero `<w:drawing>` elements**. The figure images sit in `word/media` but nothing references them, so no figure is visible.
- Re-embed every figure in both versions, in order of first mention, each followed by its caption, at a review resolution that stays readable (≥ 150 dpi at printed size).
- Rename the TIFF files in `figures_submission/` to match the final numbering exactly: `Fig. 1.tif`, `Fig. 2.tif`, `Fig. 3.tif`, `Fig. 4.tif`, `Fig. 5a.tif`, `Fig. 5b.tif`. Today `Fig. 5.tif` is Fig. 2, `Fig. 7.tif` is Fig. 4, and so on.
- Scripted check: the number of `<w:drawing>` elements equals the number of figure captions, in each version.

## 3. Blocking: the anonymous version still identifies the author

- **Reference [16]** in the anonymous version still shows the thesis title, "Univ. Ind. Santander", and the year. Searching that title finds the author. Replace the **entire** entry with `[16] [Reference withheld for double-blind review]`.
- In the anonymous introduction, change "first introduced in the author's undergraduate thesis [16]" to neutral wording, e.g. "a preliminary version of this dataset [16]".
- In the anonymous version only, replace "El Socorro, Santander" (Source 1 and the Fig. 1 caption) with `[location withheld for double-blind review]`. Keep "Colombia".
- Scripted identifier search on the anonymous v7 (text, headers, footers, captions, properties, image metadata): Rosas, Salom, Barrero, estebanr25, luise, Socorro, "Industrial de Santander", "Univ. Ind.", correo.uis, the ORCID, zenodo.19931903, huggingface, decafia-research, and any distinctive words of the thesis title. "E. Santander" as a RoCoLe author is allowed. Paste the full result into the report.

## 4. Blocking: provenance and the large groups (check the data, then fix the text)

1. **ROYA_RECORTES vs ROYA_MA.** v6 says group `ROYA_RECORTES_107` is a "leaf group" mixing own-field `ROYA_MA` images and Silva et al. `ROYA_RECORTES` images. Images from two countries cannot be the same physical leaf.
   - Using the crop–parent links from the September audit and the provenance manifest, determine for every `ROYA_RECORTES` image which parent it was cropped from (a Silva `ROYA_FONDO` image, an own-field `ROYA_MA` image, or unknown).
   - **If the `ROYA_RECORTES` crops come from own-field `ROYA_MA` photos,** their provenance is own field, not Silva. Correct Table 3 (source composition), Section 3.1, the roya-by-source numbers, and `CLAUDE.md`. Write the finding prominently in the report, because it also affects the Zenodo CC BY attribution note.
   - **If they come from Silva images,** the group is an artifact of filename-number grouping. Describe it that way, not as a leaf.
2. **The 272-image component.** Report its composition by filename prefix and source from the data. Rewrite Section 4.3 and Limitation (1) so they agree with each other and with the data. v6 currently describes it as both "laboratory leaf-miner images" and a "cross-source leaf group (ROYA_MA and ROYA_RECORTES)".
3. **Bootstrap clusters.** Clusters must never merge sources. Define clusters as (group_root, source) and recompute the per-class cluster bootstrap with the same validity rule (> 50% in one cluster → not reportable) and the same seed and B. Update 4.4, 5.2, Fig. 4, and the conclusions with whatever results. If roya becomes reportable, report it.
4. **Roya by source:** add mAP50 and mAP50-95 for own-field vs Silva roya test images, recomputed from the saved matching stats. P/R alone is not enough; keep P/R too.

## 5. Text fixes

1. **Section 3.2:** remove "all crops, rotations, and capture-series frames from the same physical leaf are assigned to the same subset". Replace with: the split was designed to keep crop–parent pairs and capture series together; a post-hoc audit found residual transformed copies (Section 5.3).
2. **Highlights:**
   - "Grouped split prevents same-leaf crops…" → "Grouped split keeps crops and capture series of a leaf together" (or similar, ≤ 85 chars).
   - "49 of 356 test images have training-split copies" → "Audit: 49 of 356 test images have copies in train (40) or val only (9)".
3. **Abstract and Resumen:** say "copies in the training (40) or validation (9) split" instead of "in the training split". Remove the dagger from the abstract; the sentence already explains the caveat.
4. **Table 1 and novelty:**
   - RoCoLe's annotation column: its data paper describes ground-truth annotations for objects (leaves, red spider mite presence, rust presence) and infection severity, so not "Classification" only.
   - BRACOL: classification and severity, plus a symptom-image set.
   - Hedge the caption: "Among the datasets reviewed, none includes a weevil (Curculionidae) class".
   - In 2.2 and 6.1, remove "instance-level bounding boxes" as a distinguishing feature (Silva et al. also has boxes) and remove "differs from all prior datasets". Distinguishing features: Colombian field images, the weevil class, three conditions in one detection dataset, and the grouped split with an integrity audit.
5. **Tables:**
   - Caption below each table, consistently.
   - Renumber: Table 1 datasets, Table 2 class × split, Table 3 source × split, Table 4 training configuration, Table 5 performance.
   - v6 has "Table 2b" before "Table 2", with swapped captions. Fix that, and remove file paths from captions.
6. **Practical Application:** remove "under the illumination, altitude, and variety conditions of the Colombian Andean coffee belt" and "and other Andean nations". The data come from one Colombian farm plus Brazilian laboratory images. Keep it to what the data support. Stay within 150–200 words.
7. **Section 3.3:** cite the Cenicafé source ([3]) for the class definitions. Say who annotated: "by the thesis authors", consistent with the Acknowledgements. Section 3.1 states that Silva et al. images were re-annotated under the same protocol.
8. **Section 6.2:** remove "This gap is consistent with other agricultural detection benchmarks [4, 7]" unless those papers report both mAP@0.50 and mAP@0.50:0.95.
9. **Section 4.4:** minador interval "not reported because minador test images are not independent of training (Section 6.3)". **Section 5.2:** add the same 6-cluster caveat for coco that the conclusions have.
10. **Section 5.1:** remove "exact value 0.018987".
11. **Section 0 answers:** if `CAPTURE_YEARS` and `PHONE_MODEL` are filled, add them to Source 1.
12. **Table 4:** confirm against `args.yaml` that the optimizer was set explicitly to AdamW with lr0 = 0.01 (not `auto`). If `auto`, report what the training log says it resolved to.

## 6. References

- **[1]:** use the full FNC *Informe de Gestión 2024* PDF URL (https://publicaciones.cenicafe.org/index.php/inf-fnc/article/download/4214/4360/3497) and give the page numbers for the families and municipalities figures. If the report doesn't say "more than 600 municipalities", use the exact figure it gives or drop the municipalities.
- **[2]:** full title "…(2008–2013): impacts, plausible causes and proposed solutions".
- **[9]:** full title "RoCoLe: A robusta coffee leaf images dataset for evaluation of machine learning based methods in plant diseases recognition".
- **[10]:** the exact Mendeley title "Rust (Hemileia vastatrix) and leaf miner (Leucoptera coffeella) in coffee crop (Coffea arabica)".
- **[13]:** access date Nov. 2026.
- **[3]:** resolve https://doi.org/10.38141/cenbook-0026_25 and confirm the chapter title and authors. Correct them if needed.

## 7. Cover letter and checks

- **Cover letter:** the title must match v7 exactly. The sole-authorship paragraph must say the thesis co-author and director were invited to review and approve and did not respond, and that their contributions are acknowledged. No superlatives. Produce `cover_letter_v7.docx`.
- **Scripted checks**, with output pasted into `FINAL_REPORT_V7.md`:
  - drawing count = caption count (both versions);
  - anonymous identifier search;
  - banned strings;
  - every number vs JSON;
  - highlights ≤ 85 characters;
  - abstract ≤ 250 words;
  - practical application 150–200 words;
  - total words by the journal's definition;
  - figures and tables cited in order;
  - every reference cited, and no [VERIFY].
- Then a fresh hostile-reviewer subagent reads both v7 files and the cover letter, and lists anything still wrong. Fix it and re-run once.

Commit and push.
