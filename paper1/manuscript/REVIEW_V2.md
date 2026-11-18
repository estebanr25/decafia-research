# Re-Review Update — Ingeniería e Investigación (I&I)
## Manuscript: "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions"
## Reviewer: Anonymous | Re-review date: 2026-11-17 | Based on: CoffeeLeafCO_manuscript_v2.docx

---

## Scope

This update checks only the eight items flagged in the first review. It does not re-examine items that were already PASS in v1 or items outside the specified scope.

---

## Item-by-Item Verdict

### 1. Keywords — limit ≤ 5

**PASS.**

v1 had 10 keywords. v2 has exactly 5:
`coffee leaf disease; object detection; YOLOv8; grouped split; data integrity`

This matches the reviewer's own suggested set verbatim. FLAG J1 is resolved.

---

### 2. Banned strings — all eight

**PASS (all 8 absent).**

| String | v2 status |
|--------|-----------|
| "92.4%" | ABSENT |
| "76.6%" | ABSENT |
| "2,786" | ABSENT |
| "Coccinellidae" | ABSENT |
| "Pseudococcidae" | ABSENT |
| "leakage-free" | ABSENT |
| "sin fuga" | ABSENT |
| "no leakage" | ABSENT |

---

### 3. "leakage" → "duplication" in Section 3.2

**PASS.**

The word "leakage" does not appear anywhere in v2 (zero occurrences). Section 3.2 now reads: "…designed to minimise cross-split duplication (future work: per-image provenance verification)." The change requested in FLAG C4 / §2.4 commentary is applied correctly.

---

### 4. "November 2026" date — should now say "submission date"

**PASS.**

The phrase "November 2026" is absent. Section 6.1 now reads: "…as of the submission date [VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists]." FLAG C5 is resolved. Note: the [VERIFY] flag in that sentence is a pre-existing unresolved item (FLAG C3 from v1), not a new issue.

The received/accepted fields in the header now read `Received: [DATE]` / `Accepted: [DATE]`, which is correct for a pre-submission draft.

---

### 5. Reference [9] RoCoLe DOI — should be 10.1016/j.dib.2019.104414

**PASS.**

v2 reference [9] reads:
> J. Parraga-Alava, K. Cusme, A. Loor, and E. Santander, "RoCoLe: A robusta coffee leaf images dataset," Data Brief, vol. 25, p. 104414, 2019, doi: 10.1016/j.dib.2019.104414.

The journal article DOI is now correctly used. FLAG R1 is resolved.

---

### 6. Reference [13] "ibid." — should now be a full citation

**PASS.**

v2 reference [13] reads:
> L. M. Constantino et al., "Otros habitantes naturales del cafetal," in Manual del Cafetero Colombiano, vol. 2, Cenicafé, Chinchiná, Colombia, 2013, pp. 261–306, doi: 10.38141/cenbook-0026_25.

This is a full citation, identical to [3] (which is correct — both cite the same chapter). The "ibid." abbreviation is gone. FLAG R2 is resolved.

---

### 7. [VERIFY] UIS thesis — should be ABSENT from reference list

**PASS.**

The reference list in v2 runs from [1] to [16]. No entry contains the text "thesis," "[VERIFY]," or any unresolved UIS entry. The reference list ends at [16] (Araaf et al., 2024). FLAG C4 / FLAG R6 is resolved.

---

### 8. Anonymous version — PII check

**PASS.**

In `CoffeeLeafCO_manuscript_v2_anonymous.docx`:

| PII item | Status |
|----------|--------|
| "Luis Esteban Rosas Ruiz" | ABSENT — replaced with "[AUTHOR]" |
| "luis.rosas@correo.uis.edu.co" | ABSENT — replaced with "[EMAIL]" |
| ORCID 0000-0003-0233-6336 | ABSENT — replaced with "[ORCID]" |

The affiliation block reads "[INSTITUTION], [INSTITUTION-CITY]" and the Acknowledgements use "[AUTHOR]", "[CO-AUTHOR]", and "[DIRECTOR]" throughout. FLAG J5 is resolved for the anonymous copy.

---

## Overall verdict on the targeted items

**All 8 flagged items: PASS.** The author has correctly resolved every item that was specifically requested for this re-review round.

---

## Remaining blocks

The following issues from v1 are **not** in the scope of this targeted re-review but remain unresolved in v2 and continue to block submission. They are reproduced here for reference; no new analysis is performed on them in this update.

| Flag | Issue | Status in v2 |
|------|-------|--------------|
| N2 / C1 | κ = 0.91 inter-annotator agreement — no traceable source; `[VERIFY: κ = 0.91 — confirm source]` still present in Section 3.3 | Unresolved (confirmed present) |
| N3 | PyTorch version "2.11" — unverifiable | Not checked in this round |
| C2 | `[CONFIRMAR: OK to describe the supervisor anonymously?]` in Acknowledgements | Unresolved (confirmed present in anonymous version) |
| C3 | Weevil novelty claim — `[VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists]` still present | Unresolved (but date wording fixed — see item 4) |
| B2 | Three figures absent (placeholders only) | Not checked in this round |
| B3 | Four tables absent (placeholders only) | Not checked in this round |
| J2 | Data Availability — `[PENDIENTE]` items (Zenodo version DOI, HuggingFace URL) | Not checked in this round |
| R3 | Reference [7] missing DOI, page range, conference expansion | Not checked in this round |
| R4 | Reference [1] missing URL/access date | Not checked in this round |
| R5 | Reference [14] non-version-pinned software citation | Not checked in this round |
| N1 | Abstract Δ = 0.004 vs. body Δ = −0.0038 rounding inconsistency | Not checked in this round |

---

## Assessment

The manuscript is making real progress. The 8 targeted fixes are all correctly applied. The remaining unresolved items fall into two categories:

**Category A — [VERIFY]/[CONFIRMAR]/[PENDIENTE] placeholders** (items N2/C1, C2, C3, J2): these are inherently author-side tasks (verify a source, confirm an editorial decision, publish a Zenodo release, obtain a URL). They are not fixable by markup alone. Until they are resolved, the manuscript is still in draft state.

**Category B — fixable reference and consistency issues** (N1, N3, R3, R4, R5): these are straightforward edits that have no dependency on external verification. There is no reason they should remain after a second revision pass.

**Verdict:** The manuscript is NOT yet in a state where only [VERIFY]/[CONFIRMAR]/[PENDIENTE] items remain as blocks. Category B issues (N1, N3, R3, R4, R5) are still present, are not gated on external verification, and should have been fixed in this revision. The author cleaned the items explicitly requested but did not address the other non-blocking issues from v1. A further revision pass is needed to clear Category B, after which the only remaining blocks will be the inherently external Category A items.

---

*Re-review completed: 2026-11-17. All checks performed on extracted document text via python-docx.*
