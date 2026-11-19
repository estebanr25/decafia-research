# FINAL REPORT V5 — CoffeeLeaf-CO Manuscript

**Date:** 2026-11-19
**Prepared by:** SESSION_FIX_MANUSCRIPT_V5 pipeline

---

## Files to Submit

| File | Purpose |
|------|---------|
| `CoffeeLeafCO_manuscript_v5.docx` | Named manuscript (submit after decision) |
| `CoffeeLeafCO_manuscript_v5_anonymous.docx` | Anonymous version (submit for review) |
| `cover_letter_v5.docx` | Revised cover letter |

---

## Word Count

- **Total word count (all text incl. tables/refs):** ~4,360 words
- **Journal limit:** 6,000 words — PASS (~1,640 words of headroom)

---

## Highlights (all <= 85 characters — PASS)

| Chars | Highlight |
|-------|-----------|
| 79 | CoffeeLeaf-CO: 2,315 annotated coffee leaf images; two sources, three classes |
| 78 | Three concurrent foliar conditions: rust, weevil (Curculionidae), leaf-miner |
| 84 | Grouped split prevents same-leaf crops and capture series from crossing boundaries |
| 76 | Post-hoc integrity audit: 49 of 356 test images have training-split copies |
| 78 | Open-access release: images, YOLO labels, model weights, and evaluation code |

---

## References Status

| # | Authors | Status | Notes |
|---|---------|--------|-------|
| [1] | FNC Informe 2024 | VERIFY | Exact page for 550,000 families / 590 municipalities needed |
| [2] | Avelino et al. 2015 | VERIFY | Confirm 30% at farm level vs national |
| [3] | Constantino et al. (Otros habitantes) | VERIFIED | DOI 10.38141/cenbook-0026_25 |
| [4] | Tian et al. 2023 | VERIFIED | DOI 10.1016/j.compag.2023.108233 |
| [5] | Mohanty et al. 2016 | VERIFIED | DOI 10.3389/fpls.2016.01419 |
| [6] | Sajitha et al. 2025 | [VERIFY] | DOI 10.1007/s10462-024-11052-2 — marked in text |
| [7] | Somanna et al. 2024 | VERIFIED | DOI 10.1007/978-3-031-66694-0_2 |
| [8] | Zuniga Cajas et al. 2025 | VERIFY | 1,423 images / mAP 0.843 — verify from full paper |
| [9] | Parraga-Alava et al. 2019 | VERIFIED | DOI 10.1016/j.dib.2019.104414 |
| [10] | Silva et al. 2020 | REPLACED | Table 1: 542 images (285 rust + 257 miner) |
| [11] | Dutta & Zisserman 2019 | [VERIFY] | arXiv:1904.10699; ACM MM'19 DOI not verified — marked in text |
| [12] | Kirillov et al. 2023 | VERIFIED | DOI 10.1109/ICCV51070.2023.00371 |
| [13] | Constantino et al. (Roya del Cafeto) | VERIFY | Same DOI as [3]; verify chapter-level DOI |
| [14] | Jocher et al. 2023 | VERIFIED | GitHub + version 8.4.148 |
| [15] | Lin et al. 2014 | VERIFIED | DOI 10.1007/978-3-319-10602-1_48 |
| [16] | Araaf et al. 2024 | VERIFIED | DOI 10.3390/s24248018 |
| [17] | Rosas Ruiz & Salom Medina 2024 | REPLACED | Author order fixed; handle 20.500.14071/42486 — VERIFY year |
| [18] | Esgario, Krohling & Ventura 2020 | REPLACED | Authors corrected; DOI 10.1016/j.compag.2019.105162 |

---

## Verification Checks

| Check | Status | Notes |
|-------|--------|-------|
| All mAP numbers match metrics_final.json | PASS | 0.929/0.734/0.841/0.962/0.985/0.926 |
| Split sizes (2315/1577/382/356) | PASS | Consistent throughout |
| Contamination (49/40/9, 107+13=120 pairs) | PASS | Stated in Section 5.3 |
| Roya CI not reportable (53.1%, ROYA_RECORTES_107) | PASS | Explained |
| Coco CI [0.801, 0.971] with 6-cluster caveat | PASS | Limitation noted in Section 5.2 |
| Best epoch 97 (1-indexed) | PASS | Section 4.1 and Fig. 5 consistent |
| Banned strings (92.4%, 76.6%, 2786, etc.) | PASS | None found |
| DECAFIA in prose | PASS | None; identifiers preserved |
| Highlights <= 85 chars | PASS | All 5 pass |
| RoCoLe only in Related Work / Table 1 | PASS | Removed from Abstract, Resumen, Section 3.1 |
| Minador caveat in abstract and Resumen | PASS | Sentences added |
| Two sources in Section 3.1 | PASS | Own field + Silva et al. |
| Source composition table (Table 2b) | PASS | Added |
| Image flow corrected | PASS | States only final 2,315 |
| Augmentation from args.yaml (not Albumentations defaults) | PASS | Fixed in Table 3 |
| lrf=0.001 | PASS | Corrected from 0.01 |
| Single author fixes | PASS | The author thanks; CRediT unchanged |
| Received/Accepted lines removed | PASS | Done |
| Practical Application unsupported claim removed | PASS | Done |
| Ref [18] authors corrected | PASS | Esgario/Krohling/Ventura |
| Ref [17] author order | PASS | Rosas Ruiz first |
| AI statement updated | PASS | Drafting/editing added |
| Doubled sentence in Section 5.2 | PASS | Fixed |
| Anonymous: no name/ORCID/email | PASS | Cleared |
| Anonymous: no Zenodo/HF/GitHub URLs | PASS | All [withheld for double-blind review] |
| Anonymous: Acknowledgements removed | PASS | Cleared |
| Document properties | PASS | Title/creator set for both versions |

---

## Items Still Needing Esteban

### High priority (must resolve before submission)

1. **Data Availability — fill real values into named version:**
   - Replace `[PEGAR DOI ZENODO v2.1.0]` with the Zenodo v2.1.0 version DOI
   - Replace `[PEGAR URL HUGGING FACE]` with the model weights URL

2. **Reference [1] (FNC):** Provide exact document/page for 550,000 families and
   590 municipalities, or remove the specific figures.

3. **Reference [2] (Avelino):** Confirm "30% losses in affected farms" is farm-level,
   not national aggregate. Adjust wording if needed.

### Medium priority

4. **[6] Sajitha:** Verify DOI 10.1007/s10462-024-11052-2 or replace.
5. **[8] Zuniga Cajas:** Verify 1,423 images and mAP 0.843 from full paper.
6. **[11] VIA:** Confirm ACM MM '19 DOI from arXiv:1904.10699, or keep imavis DOI.
7. **[13] vs [3]:** Verify that DOI 10.38141/cenbook-0026_25 covers both chapters, or find separate DOIs.
8. **[17]:** Verify thesis year 2024 at noesis.uis.edu.co handle 20.500.14071/42486.

### Low priority (optional before submission)

9. **New figures not added:** (a) example annotated images per class/source; (b) split-construction schematic. Add before final submission.
10. **Figure renumbering:** Verify Figs 3a, 3b, 5, 7 cited in sequential text order.
11. **Anonymous [17]:** Decide whether to mask self-citation as [WITHHELD].
12. **Roya mAP50 by source:** Only P/R by source was reported. mAP50 by source not computed; add if feasible.
