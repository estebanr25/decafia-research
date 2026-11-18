# NOVELTY_SEARCH.md
## Search log — Curculionidae/weevil/vaquita class in public coffee leaf datasets

**Purpose:** Verify the manuscript claim that no public coffee-leaf dataset includes a class
for weevil (Curculionidae) feeding damage before submitting to Ingeniería e Investigación.
**Date of search:** November 2026
**Author:** Luis Esteban Rosas Ruiz

---

## 1. Known datasets — classes verified

| Dataset | Country | Year | Classes | Weevil/Curculionidae/vaquita? | Reference |
|---------|---------|------|---------|-------------------------------|-----------|
| Silva et al. | Brazil | 2020 | rust (*Hemileia vastatrix*), leaf miner (*Leucoptera coffeella*) | **NO** | doi:10.17632/vfxf4trtcg.5 |
| BRACOL | Brazil | 2019 | leaf miner, rust, brown leaf spot, cercospora (4 classes) | **NO** | doi:10.1016/j.compag.2019.105162 |
| JMuBEN / JMuBEN2 | Kenya | ~2016 | phoma, cercospora, rust, miner, healthy (5 classes in JMuBEN) | **NO** | ICMLA 2016 [citation not fully confirmed — VERIFY] |
| RoCoLe | Ecuador | 2019 | rust, red spider mite, healthy (3 classes) | **NO** | doi:10.1016/j.dib.2019.104414 |

Sources for class information:
- Silva et al. 2020: Mendeley dataset page (HTTP 500 during session; classes confirmed via DECAFIA provenance metadata)
- BRACOL: Esgario et al. 2020 paper abstract and DECAFIA authors' statement in Zenodo v2.0.0 metadata
- JMuBEN/JMuBEN2: Described in Zenodo record doi:10.5281/zenodo.20253119; original paper citation not confirmed
- RoCoLe: Parraga-Alava et al. 2019, Data in Brief, doi:10.1016/j.dib.2019.104414

---

## 2. Platform searches — queries and results

### 2.1 Kaggle
- Query A: `coffee leaf disease weevil`
- Query B: `coffee leaf curculionidae`
- Query C: `coffee leaf disease`
- **Result: INACCESSIBLE** — Kaggle datasets pages are fully JavaScript-rendered; only page initialization code was returned. No dataset listings accessible.
- Known Kaggle presence: BRACOL has been mirrored on Kaggle (URL not confirmed); no weevil/Curculionidae class in BRACOL.

### 2.2 Roboflow Universe
- Query A: `coffee leaf weevil` at universe.roboflow.com/search?q=coffee+leaf+weevil
- Query B: `coffee vaquita` at universe.roboflow.com/search?q=coffee+vaquita
- **Result: INACCESSIBLE** — HTTP 403 Forbidden on all Roboflow Universe search endpoints.

### 2.3 IEEE DataPort
- Query A: `coffee leaf weevil` via ieee-dataport.org/search
- Query B: `coffee leaf` via ieee-dataport.org/search
- Direct URL checks for RoCoLe and other known datasets: all returned HTTP 404
- **Result: NOT FUNCTIONAL** — IEEE DataPort search does not honor query parameters in URL form; returned unrelated datasets. Direct pages for known datasets not accessible.

### 2.4 Zenodo API (accessible)
- Query A: `coffee leaf weevil`
- Query B: `coffee leaf disease`
- Query C: `coffee leaf disease detection dataset`
- Query D: `coffee leaf Colombia Santander`
- Query E: `coffee leaf disease vaquita OR coco OR Curculionidae`
- **Result:** Only dataset with a Curculionidae/weevil/vaquita class found: **DECAFIA v2.0.0**
  (doi:10.5281/zenodo.22756170, the dataset described in this manuscript).
  No other coffee leaf dataset with a weevil/Curculionidae class was found on Zenodo.

### 2.5 Web search engines
- Google Search, Google Scholar, DuckDuckGo, Brave Search — all returned CAPTCHA challenges
  or rate-limiting (HTTP 429) for all queries. No results obtained.
- Semantic Scholar API: HTTP 429 rate-limited before results returned.

---

## 3. Conclusion for manuscript

No public coffee-leaf dataset with a weevil (Curculionidae) feeding damage class was found
in any accessible repository or literature source during this search (November 2026).

The datasets reviewed that do not include this class are: Silva et al. (2020),
BRACOL (2019), RoCoLe (2019), and JMuBEN/JMuBEN2 (~2016).

**Limitations of this search:**
- Kaggle, Roboflow Universe, and IEEE DataPort were not accessible via automated search.
- Google Scholar was CAPTCHA-blocked.
- The absence of evidence from inaccessible platforms should be noted in the manuscript
  with appropriate hedging ("to the best of the author's knowledge").

**Manuscript language (Decision 4 from SESSION_FINAL_PASS):**
"To the best of the author's knowledge, none of the public coffee-leaf datasets reviewed
for this work (November 2026) includes a class for weevil (Curculionidae) feeding damage."
Followed by a list of datasets reviewed and their classes.
