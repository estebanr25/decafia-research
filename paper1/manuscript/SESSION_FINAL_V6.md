# CoffeeLeaf-CO Paper 1: final pass → v6 (references verified by external review + 2 missing figures)

> **For Esteban:** save as `SESSION_FINAL_V6.md` in `C:\Users\luise\temp\decafia-research`. Open **Claude Code on your PC** there, select Fable, and send:
> *"Read SESSION_FINAL_V6.md and execute it end to end on main. Do not stop to ask me questions."*

## 0. Rules

All rules from `SESSION_MANUSCRIPT.md` Section 1 and `SESSION_FIX_MANUSCRIPT_V5.md` still apply (numbers only from repository files, 3 decimals, banned strings, Scheme A naming, work on copies, fail loudly). Input: `CoffeeLeafCO_manuscript_v5.docx` and its anonymous version. Output: v6 of both, and `FINAL_REPORT_V6.md`.

## 1. References: apply these verified corrections

Each item below was checked against the original source during an external review on 2026-11-19. Apply exactly; you may re-verify, but don't override with memory.

- **[1] FNC.** The figures "approximately 550,000 farming families" and "more than 590 municipalities" don't match what public FNC-based sources report (e.g. 557,000 families for 2024; 611 municipalities in an FNC annual balance). Cite the **FNC *Informe de Gestión 2024*** (PDF: https://publicaciones.cenicafe.org/index.php/inf-fnc/article/download/4214/4360/3497). Extract the exact number of coffee-growing families and municipalities from that PDF, with the page number. If a figure isn't in the report, drop that figure. Use the same numbers in the abstract, the Resumen, and the introduction.
- **[2] Avelino et al. 2015.** Replace the sentence with the paper's actual finding: *"Coffee leaf rust reduced Colombian coffee production by 31% on average during the 2008–2011 epidemic years compared with 2007 [2]."* Authors: J. Avelino, M. Cristancho, S. Georgiou, P. Imbach, L. Aguilar, G. Bornemann, P. Läderach, F. Anzueto, A. J. Hruska, C. Morales; *Food Security* 7(2), 303–321, 2015, doi 10.1007/s12571-015-0446-9.
- **[6] Replace** with: I. Pacal, I. Kunduracioglu, M. H. Alma, M. Deveci, S. Kadry, "A systematic review of deep learning techniques for plant diseases," *Artificial Intelligence Review*, vol. 57, no. 11, art. 304, 2024, doi 10.1007/s10462-024-10944-7. Adjust the citing sentence so it claims only what a systematic review of DL techniques for plant diseases supports.
- **[8] Zúñiga Cajas et al. 2025: the v4/v5 description is wrong** (it said Ecuador, 1,423 images, a custom YOLOv8 with mAP@0.50 = 0.843, CABI scale). The full paper (https://agritrop.cirad.fr/614550/1/1833-200-222.pdf) reports:
  - photographs of rust-infected Caturra leaves (underside) from **Costa Rica** (Aserrí, Turrialba, Heredia);
  - **thirteen CNN classifiers** plus few-shot prototypical networks that classify lesions into five severity classes based on affected leaf area;
  - best F1 of about **0.80**;
  - YOLOv8 used **only for leaf segmentation**;
  - **no mAP**.

  Rewrite the sentence accordingly. The paper's text and tables are partly inconsistent, so cite only the table values (e.g. "a best F1 of about 0.80"). Don't quote the image count unless you verify it in the PDF (the text and the per-class counts disagree). Full authors: J. J. Zuñiga Cajas, O. D. Peña Ramos, E. Lasso, J. Avelino, J. C. Corrales, C. N. Figueroa Martínez; *Inteligencia Artificial* 28(76), 200–222, 2025, doi 10.4114/intartif.vol28iss76pp200-222.
- **[11] VIA:** A. Dutta and A. Zisserman, "The VIA Annotation Software for Images, Audio and Video," in *Proc. 27th ACM International Conference on Multimedia (MM '19)*, Nice, France, 2019; arXiv:1904.10699. Add the ACM DOI only if Crossref confirms it.
- **[13] Remove.** Its DOI belongs to a different chapter, and the chapter attribution couldn't be verified. Cite [3] for the coco description. For the roya symptom description, cite [2] or another source you verify; otherwise leave that sentence uncited, as standard symptom description.
- **[18] BRACOL:** authors are J. G. M. Esgario, R. A. Krohling, J. A. Ventura (*Comput. Electron. Agric.* 169, 105162, 2020). Confirm v5 has this.
- **Table 1 (check v5 against these facts):**
  - **Silva et al.:** 285 rust + 257 leaf-miner images; categorized for object detection.
  - **RoCoLe:** 1,560 images with ground-truth annotations for objects (leaves, red spider mite presence, rust presence) and infection severity.
  - **BRACOL:** a whole-leaf dataset labeled by predominant stress and severity, plus a symptom-image dataset.
- After all edits, renumber references in order of first citation, check that every reference is cited and every citation has a reference, and list each reference's status (VERIFIED / REPLACED / REMOVED / [VERIFY]) in the report. **No [VERIFY] marker may remain in the manuscript text.** Anything still unverifiable is removed together with the claim it supports.

## 2. The two missing figures (required)

Generate both with scripts in `paper1/figures/`, each with a sidecar JSON. Export TIFF ≥ 300 dpi (LZW) to `figures_submission/` and embed in both manuscript versions.

1. **Example annotated images.** A grid with 2 images for each combination that exists:
   - own field images: roya, coco, healthy (background);
   - Silva et al.: roya, minador.

   Draw the ground-truth boxes from the YOLO labels with the fixed class colors, label each panel with class and source, and pick images deterministically (seed 42), preferring train-split images. No personal or location information in the images.
2. **Split construction and integrity audit schematic.** A flow diagram:
   - sources → removal of RoCoLe images → grouping (crop–parent links, capture-series blocks) → `split_grouped_v1` (1,577 / 382 / 356);
   - then the post-hoc audit: dihedral pHash candidates → SIFT + RANSAC verification with foreground masks → verified cross-split copies → exclusion list (49 test images) → sensitivity evaluation (356 vs 307 images).

   Every count is rendered from the repository JSON/CSV files. Plain vector style, legible at single-column width.

Then **renumber all figures sequentially in order of first mention**, update every in-text reference and caption, and check that no figure is uncited or cited out of order.

## 3. Final consistency checks (both versions)

- Abstract, Resumen, highlights, body, tables, figure captions, and conclusions state the same numbers and the same caveats: minador not independent; residual copies (train vs val-only counts); roya by source.
- The Data Availability placeholders stay exactly `[PEGAR DOI ZENODO v2.1.0]` and `[PEGAR URL HUGGING FACE]` in the named version, and `[withheld for double-blind review]` in the anonymous version.
- Re-run the identifier search on the anonymous v6 and set the document properties as in v5.
- Banned-strings check, word count by the journal's definition, highlights ≤ 85 characters, abstract ≤ 250 words, practical application 150–200 words.
- Update the cover letter only if the title changed.
- Re-run the fresh hostile-reviewer subagent once on v6 and fix what it finds.

## 4. Report

`paper1/manuscript/FINAL_REPORT_V6.md`, one page:
- the files to submit;
- the counts;
- the reference status table;
- confirmation that no [VERIFY] remains;
- the remaining manual steps:
  1. Zenodo v2.1.0;
  2. Hugging Face;
  3. paste the two values in the named version only;
  4. update the claude.ai project;
  5. submit via OJS with the anonymous version, the TIFF figures, and the cover letter.

Commit and push.
