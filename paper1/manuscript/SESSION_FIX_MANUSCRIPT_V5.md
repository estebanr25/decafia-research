# DECAFIA Paper 1: fix the v4 manuscript after external review → v5 (one session)

> **For Esteban:** first fill in Section 0 (2 minutes). Save as `SESSION_FIX_MANUSCRIPT_V5.md` in `C:\Users\luise\temp\decafia-research`. Open **Claude Code on your PC** there, select Fable, and send:
> *"Read SESSION_FIX_MANUSCRIPT_V5.md and execute it end to end on main. Do not stop to ask me questions."*

---

## 0. Esteban's answers (fill in; anything left as `?` means: remove the claim)

```yaml
CAPTURE_YEARS: ?            # manuscript says 2024; earlier records say 2022–2023. Which is true?
FARM_ALTITUDE_M: ?          # manuscript says ~1,500; earlier notes say 1,360
FARM_COORDINATES: ?         # manuscript says 6°28′N, 73°19′W. Correct?
PHONE_MODEL: ?              # earlier notes: Xiaomi Poco X3 Pro
REFLECTION_IMAGES_141: ?    # true / false. Did you deliberately add 141 images of light reflections as background?
SECOND_ANNOTATOR_REVIEW: ?  # what actually happened? e.g. "Andrey annotated part of the images; no independent double review", or "Andrey reviewed all labels and we resolved disagreements"
SAM_MASKS_PUBLISHED: ?      # true / false. Are the SAM polygon masks in the repo or on Zenodo?
NAME_SCHEME: A              # A (recommended): dataset = "CoffeeLeaf-CO", project/brand = "DECAF IA"
                            # B: "DECAF IA" everywhere (dataset, project, title)
```

## 1. Rules

All rules from `SESSION_MANUSCRIPT.md` Section 1 still apply: numbers only from repository JSON/CSV files, 3 decimals, banned strings, verified references only, work on copies, fail loudly, don't stop to ask. Input: `paper1/manuscript/CoffeeLeafCO_manuscript_v4.docx` and its anonymous version. Output: v5 of both, a revised cover letter, and `paper1/manuscript/V5_CHANGES.md` listing every change (old text → new text → reason).

---

## 2. Blocking fixes

1. **RoCoLe is not a source.** All RoCoLe images (SANAS_ROCOLE) were removed, and the split audit confirmed zero remain. Remove RoCoLe as a source from the abstract, the Resumen, Section 3.1 ("Source 2"), Section 3.2 ("Sources 2 and 3"), and anywhere else. RoCoLe stays only in Related Work and Table 1 as a comparison dataset.
2. **Correct provenance.** Silva et al. contributes **all minador images and the rust prefixes ROYA_FONDO and ROYA_RECORTES**, not only leaf-miner images. Rewrite Section 3.1 as two sources:
   - own field images (SANAS_*, all COCO_*, ROYA_P_A, ROYA_MA, ROYA_Muy_A);
   - Silva et al. (ROYA_FONDO, ROYA_RECORTES, all minador).
   Add a table of images and instances per class × source × split, computed from the dataset files (reuse `paper1/tables/dataset_composition.json` if it exists, otherwise recompute). Report the share of roya instances from each source.
3. **Image-flow arithmetic.** "Of 2,803 raw images evaluated, 17 were excluded … yielding 2,315" is false (2,803 − 17 ≠ 2,315), and its intermediate value is the banned old-dataset figure. Reconstruct the real flow from the manifest/provenance files (raw → RoCoLe removal → exclusions → 2,315) with each count traceable to a file. Never print the banned figure. If the flow can't be reconstructed from files, state only the final 2,315 images and their provenance.
4. **Remove contradictions about residual copies.**
   - Section 6.3(1) says rust and weevil test images have no verified copies in training, but Section 5.3 reports 25 roya and 12 coco annotations in affected images. Rewrite 6.3(1) to state the real affected shares (3.0% roya, 1.5% coco, 23.5% minador) and point to the sensitivity analysis.
   - Section 3.2 claims all rotations of a leaf are in the same subset. Rewrite it as "the split was designed to keep … together; a post-hoc audit found residual transformed copies (Section 5.3)".
   - Use one consistent statement everywhere (highlights, abstract, Resumen, 3.2, 5.3, conclusions) for how many of the 49 affected test images have their copy in **train** and how many only in **val**. Compute both counts from the copy-pairs file.
5. **Minador caveat in words, in the abstract and the Resumen.** A dagger in an abstract means nothing. Add one sentence: leaf-miner test images are linked to training images through verified transformed copies, so its score cannot be read as performance on independent leaves.
6. **Name and acronym (apply `NAME_SCHEME`).** The project name is **DECAF IA**, written with a space: a deliberate pun on "decaf" + IA. It stands for *Detección de Enfermedades en el Café con Inteligencia Artificial*. Remove the invented expansion in v4. On first use in English, give the expansion plus a short gloss ("disease detection in coffee with artificial intelligence").
   - **Scheme A (recommended):** the dataset is called **CoffeeLeaf-CO** everywhere in the manuscript: title, abstract, Resumen, highlights, tables, captions, conclusions, data availability. DECAF IA appears as the project within which the dataset was developed, with its expansion, once in the introduction and in the data availability / acknowledgements where relevant. Suggested title: "CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images for detecting rust, weevil damage and leaf miner".
   - **Scheme B:** use "DECAF IA" everywhere the manuscript currently says "DECAFIA" (dataset and project), never "DECAFIA" or "DECAF-IA".
   - Both schemes: keep internal identifiers unchanged (`decafia_grouped_v1`, `split_grouped_v1`, repository and file names, Hugging Face repo id) so traceability isn't broken; mention them only as identifiers. Update `zenodo_v2.1.0/ZENODO_DESCRIPTION.txt` (title and description), the dataset README/card, and the Hugging Face model card text in the repo to use the same naming. Run a final search for any leftover "DECAFIA" in prose and report each hit.
7. **Unverified facts:** apply Section 0. Remove any claim marked `?`: capture years, altitude, coordinates, phone model, the 141 reflection images, the second-annotator review, and the SAM masks being "retained in the repository". The annotation paragraph must describe only what Esteban confirmed. No inter-annotator agreement claim.
8. **Remove the unsupported claim in Practical Application:** "This level of specificity is not achievable with models trained on existing datasets collected under Ecuadorean or Brazilian conditions." No cross-dataset experiment supports it, and part of DECAFIA is itself Brazilian. Also soften "can be linked to economic damage thresholds" to a possibility, with no implied validation.

## 3. References (verify each against Crossref or the publisher page; never from memory)

- **[18] Wrong authors.** The paper is by **J. G. M. Esgario, R. A. Krohling, and J. A. Ventura**, *Comput. Electron. Agric.* 169 (2020) 105162, doi 10.1016/j.compag.2019.105162.
- **[11] Wrong venue/DOI.** Use A. Dutta and A. Zisserman, "The VIA Annotation Software for Images, Audio and Video," *Proc. 27th ACM Int. Conf. Multimedia (MM '19)*, 2019 (arXiv:1904.10699). Verify the ACM DOI before using it.
- **[8] Unsupported details.** The abstract of Zúñiga Cajas et al. (2025) describes thirteen CNN models that classify lesions by severity. Open the full PDF and verify image source/country, number of images, models, and any metric. Rewrite the sentence with only what the paper states; if the PDF can't be read, keep only what the abstract supports.
- **[6] Not found.** Verify "Sajitha et al., Artif. Intell. Rev. 58, 2025, doi 10.1007/s10462-024-11052-2". If it can't be verified, replace it with a verified review (e.g. the 2024 *Artificial Intelligence Review* systematic review, doi 10.1007/s10462-024-10944-7, after verifying its authors) or remove it.
- **[13] Suspicious.** The same DOI is attributed to a different chapter ("Roya del Cafeto") than [3]. Verify the chapter, authors, and DOI. If they can't be verified, cite only [3] and Cenicafé publications you can verify.
- **[17] Author order.** The thesis title page lists **L. E. Rosas Ruiz** first, then A. F. Salom Medina. Verify the year and the handle `20.500.14071/42486`; mark `[VERIFY]` if unresolved.
- **[1], [2], [4], [7]:**
  - [1]: give the exact FNC document/page for the families and municipalities figures, or remove the figures;
  - [2]: check that "production losses exceeding 30% in affected Colombian farms" matches what Avelino et al. actually report (national production decline vs farm level) and fix the wording;
  - [4], [7]: verify, and keep them only if they support the sentence they're attached to.
- **[10] Silva et al.:** use the dataset's exact title from Mendeley. In **Table 1**, the source description reports **285 rust + 257 leaf-miner images** (not 1,251), and the dataset is categorized for object detection (not "classification"). Recheck every Table 1 cell (images, annotation type, year) for Silva, BRACOL (which includes symptom segmentation), and RoCoLe (which includes polygon annotations), against the original sources. Then rewrite the novelty sentence in 2.2: DECAFIA's distinguishing features are Colombian field images, the weevil class, three classes in one detection dataset, and the grouped split with an integrity audit. **Not** "instance-level boxes", which others also have. Hedge the Table 1 caption ("among the datasets reviewed…").

## 4. Major fixes

1. **Title and highlights:** don't call the whole dataset "field-collected … under Colombian Andean conditions". Minador is entirely Brazilian laboratory imagery, and a large share of roya comes from Silva et al. Suggested title: "DECAFIA (CoffeeLeaf-CO): a multi-source coffee leaf dataset with Colombian field images for detecting rust, weevil damage and leaf miner". Keep highlights ≤ 85 characters.
2. **Roya by source.** Report roya mAP50 / mAP50-95 separately for own-field and Silva test images (with instance counts), from the existing analysis or by recomputing from the saved stats. The ROYA_RECORTES group holds 53.1% of roya test instances; say explicitly what that group is.
3. **Leaky baseline.** Add the per-image (leaky) split result (test mAP50 0.9235 / mAP50-95 0.7293, from its results file) next to the grouped result, with the caveat that the test sets differ. Discuss in two sentences what this says about the effect of leakage on this dataset.
4. **Integrity-audit methods must match what was done.** Describe the consolidated pipeline from `split_v2/` (pHash tiers ≤ 4 and 5–8, SIFT + RANSAC verification with foreground masks, the September audit, the union) and take every count from `split_v2/copy_pairs.csv` / `copy_pairs`-derived JSON. Reconcile the "60 cross-split pairs" in 5.3 with the session reports (107 Tier A cross pairs, 13 merged Tier B), and use the final verified numbers. Explain that the large component's connectivity combines verified copies with filename-based capture-series links (an assumption). Replace the internal name "MINEIRO_99" with a description.
5. **Coco interval:** with only 6 clusters, the cluster bootstrap is unreliable. Keep it only with an explicit sentence on this limitation, or report the image-level interval as secondary for coco too. Be consistent across 5.2, Fig. 7, and the conclusions.
6. **Training configuration** copied exactly from the run's `args.yaml`: the optimizer setting (if `auto`, say so and what it resolved to in the training log), lr0, lrf, momentum, warmup, and the augmentation parameters actually used (mosaic, fliplr, HSV, scale, translate…). Remove "Albumentations defaults" unless the log proves Albumentations transforms were applied. Report software versions for **training** from the training log; if those aren't available, label the stated versions as the evaluation environment. Make the best epoch consistent with `results.csv` (97 vs 98: state the indexing).
7. **Remove the unsupported causal claim in 5.4** ("primary error: visual overlap with specular reflections and early-stage chlorosis") unless the error analysis supports it; otherwise use observable descriptors only.
8. **Figures:** renumber sequentially (no gaps). Add (a) a figure with example annotated images for each class and each source, using images from the dataset (not the test set only), and (b) a schematic of the split construction and the integrity audit. Every figure must be cited in order in the text.
9. **AI statement:** include drafting and language editing of the manuscript text among the uses, along with code, figures, formatting, and verification. Follow the journal's sample wording.
10. Single author: "The authors thank" → "The author thanks". Remove the "Received / Accepted [DATE]" lines unless the template requires them.

## 5. Anonymous version and file properties

- **Never paste the Zenodo version DOI or the Hugging Face URL into the anonymous version.** Both placeholders there become `[withheld for double-blind review]`. Only the named version gets the real values later.
- Remove the Acknowledgements and CRediT blocks from the anonymous version entirely, rather than leaving placeholders.
- **Set the Word document properties of every output:** title = the article title; creator and last-modified-by cleared (anonymous) or "Luis Esteban Rosas Ruiz" (named); company cleared. Both v4 files still carry the template's unrelated title "BASES DE LA IMPLEMENTACIÓN DE INTELIGENCIA APLICADAS AL DESARROLLO TECNOLÓGICO DEL SOFTWARE EN COLOMBIA" and a previous editor's name in last-modified-by.
- Re-run the identifier search on the anonymous v5 (text, headers, footers, properties, image metadata).

## 6. Cover letter

- Update the title.
- Remove the unsupported superlative "among the first published for a coffee leaf disease dataset".
- Rewrite the sole-authorship paragraph honestly: the work derives from an undergraduate thesis co-authored with A. F. Salom Medina and directed by Prof. J. G. Barrero Pérez; both were invited to review and approve the manuscript and did not respond; their contributions are acknowledged in the manuscript. Remove "no other person qualifies as an author".
- Keep the preprint-authorization request.

## 7. Verify and report

Re-run the fresh hostile-reviewer subagent on v5 (numbers vs files, banned strings, every reference verified, journal requirements, anonymization, internal consistency between abstract, highlights, body, tables, and conclusions). Fix and re-run once.

Write `paper1/manuscript/FINAL_REPORT_V5.md`, page one:
- files to submit;
- counts (abstract, practical application, highlights, total words by the journal's definition);
- every reference with status VERIFIED / REPLACED / REMOVED / [VERIFY];
- anything still needing Esteban.

Commit and push.
