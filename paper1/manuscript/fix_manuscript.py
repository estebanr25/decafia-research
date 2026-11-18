"""
Apply fixes from hostile review to manuscript v1.
Produces CoffeeLeafCO_manuscript_v2.docx and _anonymous version.
"""
import json, hashlib
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"
RESULTS_DIR = REPO / "paper1/results"

# Load numbers
d = json.load((RESULTS_DIR / "metrics_final.json").open())
p4 = d['phase4']['test_set_full']
mAP50     = p4['map50_model_val']       # 0.929377
filt_mAP  = 0.925574
delta     = filt_mAP - mAP50           # -0.003803

doc = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v1.docx")

# Build text map of all fixes
fixes = {
    # J1: Reduce keywords to 5
    "Keywords: coffee leaf disease; object detection; YOLOv8; Colombia; Santander; "
    "Hemileia vastatrix; Leucoptera coffeella; benchmark dataset; grouped split; data integrity":
    "Keywords: coffee leaf disease; object detection; YOLOv8; grouped split; data integrity",

    "Palabras clave: enfermedad foliar del café; detección de objetos; YOLOv8; Colombia; "
    "Santander; Hemileia vastatrix; Leucoptera coffeella; conjunto de datos de referencia; "
    "división agrupada; integridad de datos":
    "Palabras clave: enfermedad foliar del café; detección de objetos; YOLOv8; "
    "división agrupada por hoja; integridad de datos",

    # N1: Abstract delta consistency — use "0.004 (rounded to 3 dp)"
    f"reduces mAP@0.50 by {abs(filt_mAP-mAP50):.3f} to":
    f"reduces mAP@0.50 by {abs(filt_mAP-mAP50):.4f} to",

    # C5: Remove "November 2026" date (replace with generic)
    "as of November 2026":
    "as of the submission date",

    # C2 / 3.2: "leakage" → "duplication"
    "minimise cross-split leakage":
    "minimise cross-split duplication",

    # R2: ibid in reference [13]
    '"Otros habitantes naturales del cafetal," ibid. [3].':
    '"Otros habitantes naturales del cafetal," in Manual del Cafetero Colombiano, '
    'vol. 2, Cenicafé, Chinchiná, Colombia, 2013, pp. 261–306, doi: 10.38141/cenbook-0026_25.',

    # R1: RoCoLe DOI — replace dataset DOI with journal article DOI
    "doi: 10.17632/c5yvn32dzg":
    "doi: 10.1016/j.dib.2019.104414",
}

# Also remove the [VERIFY] UIS thesis from references
verify_thesis = "[VERIFY] UIS thesis on DECAFIA / AI for coffee disease risk — verify at https://noesis.uis.edu.co (search: DECAFIA café enfermedad); authors, year, handle unknown."

def apply_fix_to_paragraph(p, fixes):
    """Apply text replacements to a paragraph. Returns True if changed."""
    changed = False
    full_text = "".join(run.text for run in p.runs)
    new_text = full_text
    for old, new in fixes.items():
        if old in new_text:
            new_text = new_text.replace(old, new)
            changed = True
    if changed and new_text != full_text:
        # Clear all runs and put text in first run
        for i, run in enumerate(p.runs):
            if i == 0:
                run.text = new_text
            else:
                run.text = ""
    return changed

n_changed = 0
paras_to_remove = []
for i, p in enumerate(doc.paragraphs):
    full_text = "".join(run.text for run in p.runs)
    # Remove UIS thesis verify entry
    if verify_thesis[:40] in full_text:
        paras_to_remove.append(p)
        continue
    if apply_fix_to_paragraph(p, fixes):
        n_changed += 1

# Remove marked paragraphs
for p in paras_to_remove:
    p._element.getparent().remove(p._element)
    print("Removed [VERIFY] UIS thesis paragraph")

print(f"Fixed {n_changed} paragraphs")

# Verify no banned strings remain
all_text = " ".join("".join(run.text for run in p.runs) for p in doc.paragraphs)
banned = ['92.4%','76.6%','2,786','Coccinellidae','Pseudococcidae','leakage-free','sin fuga','no leakage']
found = [b for b in banned if b in all_text]
if found:
    print(f"WARNING: Banned strings still found: {found}")
else:
    print("Banned string check: PASS")

# Verify keywords count
kw_line = [p for p in doc.paragraphs if 'Keywords:' in "".join(r.text for r in p.runs)]
for kl in kw_line:
    text = "".join(r.text for r in kl.runs)
    count = len(text.split(':')[1].split(';')) if ':' in text else 0
    print(f"Keywords: {count} ({'PASS' if count <= 5 else 'FAIL'}): {text[:80]}")

# Save v2
out_path = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v2.docx"
doc.save(out_path)
print(f"Saved v2: {out_path}")

wc = len(all_text.split())
print(f"Word count: {wc}")

# =====================================================================
# ANONYMOUS VERSION v2
# =====================================================================
doc_anon = Document(out_path)

anon_map = [
    ("Luis Esteban Rosas Ruiz", "[AUTHOR]"),
    ("L. E. Rosas Ruiz", "[AUTHOR]"),
    ("luis.rosas@correo.uis.edu.co", "[EMAIL]"),
    ("0000-0003-0233-6336", "[ORCID]"),
    ("A. F. Salom Medina", "[CO-AUTHOR]"),
    ("J. G. Barrero Pérez", "[DIRECTOR]"),
    ("estebanr25/decafia-research", "[CODE-REPO]"),
    ("estebanr25/decafia", "[MODEL-REPO]"),
    ("Universidad Industrial de Santander", "[INSTITUTION]"),
    ("El Socorro, Santander", "[LOCATION]"),
    ("Bucaramanga, Colombia\n(corresponding", "[INSTITUTION-CITY]\n(corresponding"),
    ("Bucaramanga, Colombia", "[INSTITUTION-CITY]"),
]

for p in doc_anon.paragraphs:
    full_text = "".join(run.text for run in p.runs)
    new_text = full_text
    for orig, repl in anon_map:
        new_text = new_text.replace(orig, repl)
    if new_text != full_text:
        for i, run in enumerate(p.runs):
            if i == 0:
                run.text = new_text
            else:
                run.text = ""

anon_path = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v2_anonymous.docx"
doc_anon.save(anon_path)
print(f"Saved anonymous v2: {anon_path}")

# Verify anon: author name should not appear
anon_text = " ".join("".join(r.text for r in p.runs) for p in doc_anon.paragraphs)
remaining_pii = [x for x in ["Luis Esteban Rosas Ruiz", "luis.rosas@correo.uis.edu.co", "0000-0003-0233-6336"] if x in anon_text]
if remaining_pii:
    print(f"WARNING: PII still in anon version: {remaining_pii}")
else:
    print("Anonymous version PII check: PASS")
