# FINAL REPORT V6 — CoffeeLeaf-CO Manuscript

**Date:** 2026-11-19
**Prepared by:** SESSION_FINAL_V6 pipeline

---

## Files to Submit

| File | Purpose |
|------|---------|
| `CoffeeLeafCO_manuscript_v6.docx` | Named manuscript (submit after decision) |
| `CoffeeLeafCO_manuscript_v6_anonymous.docx` | Anonymous version for reviewer submission |
| `cover_letter_v5.docx` | Cover letter (unchanged — title did not change) |
| `figures_submission/Fig_examples.tif` | Fig. 1 — annotated examples (300 dpi LZW TIFF) |
| `figures_submission/Fig_schematic.tif` | Fig. 3 — split/audit schematic (300 dpi LZW TIFF) |
| `figures_submission/Fig. 3a.tif` | Fig. 5a — confusion matrix raw counts |
| `figures_submission/Fig. 3b.tif` | Fig. 5b — confusion matrix normalized |
| `figures_submission/Fig. 5.tif` | Fig. 2 — training curves |
| `figures_submission/Fig. 7.tif` | Fig. 4 — bootstrap CIs |

---

## Counts

| Metric | Value | Limit | Status |
|--------|-------|-------|--------|
| Total words | ~4,458 | 6,000 | PASS |
| Abstract words | 186 | 250 | PASS |
| Practical Application words | 151 | 150–200 | PASS |
| Highlights | 5, all ≤ 85 chars | ≤ 85 chars each | PASS |
| Figures | 5 (Fig. 1–5b) | — | Sequential, in-order |
| References | 17 ([1]–[17]) | — | No gaps, no [VERIFY] |

---

## Highlights (all ≤ 85 chars — PASS)

| Chars | Highlight |
|-------|-----------|
| 79 | CoffeeLeaf-CO: 2,315 annotated coffee leaf images; two sources, three classes |
| 78 | Three concurrent foliar conditions: rust, weevil (Curculionidae), leaf-miner |
| 84 | Grouped split prevents same-leaf crops and capture series from crossing boundaries |
| 76 | Post-hoc integrity audit: 49 of 356 test images have training-split copies |
| 78 | Open-access release: images, YOLO labels, model weights, and evaluation code |

---

## References Status (all [VERIFY] removed — PASS)

| # | Authors | Status | Notes |
|---|---------|--------|-------|
| [1] | FNC Informe de Gestión 2024 | VERIFIED | Numbers updated: ~557,000 families, >600 municipalities |
| [2] | Avelino et al. 2015, Food Security | VERIFIED | Sentence rewritten: 31% production reduction 2008–2011 vs 2007; full author list added |
| [3] | Constantino et al. (Otros habitantes), Cenicafé 2013 | VERIFIED | DOI 10.38141/cenbook-0026_25 |
| [4] | Tian et al., Comput. Electron. Agric. 2023 | VERIFIED | DOI 10.1016/j.compag.2023.108233 |
| [5] | Mohanty et al., Front. Plant Sci. 2016 | VERIFIED | DOI 10.3389/fpls.2016.01419 |
| [6] | Pacal et al., Artif. Intell. Rev. 2024 | REPLACED | Was Sajitha 2025; replaced with verified doi 10.1007/s10462-024-10944-7 |
| [7] | Somanna et al., Springer 2024 | VERIFIED | DOI 10.1007/978-3-031-66694-0_2 |
| [8] | Zuñiga Cajas et al., Inteligencia Artificial 2025 | REPLACED | Was wrong (Ecuador/mAP); now: Costa Rica, 13 CNNs, F1~0.80; doi 10.4114/intartif.vol28iss76pp200-222 |
| [9] | Parraga-Alava et al., Data Brief 2019 | VERIFIED | DOI 10.1016/j.dib.2019.104414 |
| [10] | Silva et al., Mendeley Data V5 2020 | VERIFIED | doi 10.17632/vfxf4trtcg.5; Table 1 updated: 542 images |
| [11] | Dutta & Zisserman, ACM MM 2019 | REPLACED | Updated to ACM MM'19 (arXiv:1904.10699); imavis DOI removed |
| [12] | Kirillov et al., ICCV 2023 | VERIFIED | DOI 10.1109/ICCV51070.2023.00371 |
| [13] | Jocher et al., Ultralytics YOLO 8.4.148 | VERIFIED | Was [14] in v5; renumbered |
| [14] | Lin et al., ECCV 2014 | VERIFIED | Was [15] in v5; renumbered |
| [15] | Araaf et al., Sensors 2024 | VERIFIED | Was [16] in v5; renumbered |
| [16] | Rosas Ruiz & Salom Medina, thesis 2024 | VERIFIED | Was [17] in v5; renumbered; author order fixed |
| [17] | Esgario, Krohling & Ventura, Comput. Electron. Agric. 2020 | VERIFIED | Was [18] in v5; renumbered; authors corrected |
| — | Constantino et al. (Roya del Cafeto) | REMOVED | Was [13] in v5; unverifiable DOI; cites merged to [3] |

**No [VERIFY] markers remain in manuscript text — PASS**

---

## Verification Checks

| Check | Status |
|-------|--------|
| Banned strings (92.4%, 76.6%, 2,786, Pseudococcidae, leakage-free, DECAF-IA) | PASS |
| DECAFIA in prose | PASS |
| [VERIFY] markers in manuscript | PASS — none |
| Highlights <= 85 chars | PASS |
| Abstract <= 250 words | PASS (186) |
| Practical Application 150–200 words | PASS (151) |
| Figures in sequential citation order | PASS (1, 2, 3, 4, 5a/5b) |
| All figures cited in text | PASS |
| Numbers match metrics_final.json | PASS |
| RoCoLe only in Related Work / Table 1 | PASS |
| Minador caveat in abstract and Resumen | PASS |
| Anonymous: no identifying info | PASS |
| Anonymous: placeholders correct | PASS |
| Document properties set | PASS |

---

## Remaining Manual Steps (Esteban)

1. **Zenodo v2.1.0:** Publish the dataset version on Zenodo and obtain the version DOI.

2. **Hugging Face:** Upload model weights (best.pt, SHA-256: d8bf05c31ec37923…) and obtain the URL.

3. **Paste both values into named version only:**
   - Open `CoffeeLeafCO_manuscript_v6.docx`
   - In Data Availability, replace `[PEGAR DOI ZENODO v2.1.0]` with the actual version DOI
   - Replace `[PEGAR URL HUGGING FACE]` with the actual HF URL
   - Save (do not change anonymous version — it already has [withheld for double-blind review])

4. **Update the claude.ai project** with the v6 manuscript text.

5. **Submit via OJS** (Ingeniería e Investigación portal):
   - Upload: `CoffeeLeafCO_manuscript_v6_anonymous.docx` as the main manuscript
   - Upload TIFFs: `Fig_examples.tif`, `Fig_schematic.tif`, `Fig. 3a.tif`, `Fig. 3b.tif`, `Fig. 5.tif`, `Fig. 7.tif`
   - Upload: `cover_letter_v5.docx` as the cover letter
   - Confirm author details match your OJS profile
