"""
Category B fixes on CoffeeLeafCO_manuscript_v2.docx:
- N3: PyTorch 2.11 — confirm it's correct (env actually has 2.11.0+cu128)
- R3: Ref [7] Somanna et al. — add correct DOI and venue
- R4: Ref [1] FNC — add URL and access date
- R5: Ref [14] YOLOv8 — improve citation (note: no pinned Zenodo DOI found; keep GitHub + version)
- Duplicate ref [3]/[13]: collapse to single cite
- Also note: 88 annotations vs 49 images clarification in §5.3

Output: CoffeeLeafCO_manuscript_v3.docx + _anonymous.docx
"""
from pathlib import Path
from docx import Document
import hashlib

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"

doc = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v2.docx")

fixes = {
    # R3: Somanna et al. — correct venue and DOI
    '"A deep learning-based plant disease detection and classification for Arabica coffee leaves," '
    'in Proc. AICS, Springer, Cham, 2024.':
    '"A deep learning-based plant disease detection and classification for Arabica coffee leaves," '
    'in Deep Learning Theory and Applications (Commun. Comput. Inf. Sci.), Springer, Cham, 2024, '
    'pp. 19–37, doi: 10.1007/978-3-031-66694-0_2.',

    # R4: FNC Informe — add URL and access date
    'FNC: Bogotá, Colombia, 2024.':
    'FNC, Bogotá, Colombia, 2024. [Online]. Available: https://federaciondecafeteros.org. [Accessed: Nov. 2026].',

    # R5: YOLOv8 — add specific version note
    'Ultralytics, "YOLOv8," GitHub, 2023. [Online]. Available: https://github.com/ultralytics/ultralytics. [Accessed: Mar. 2025].':
    'G. Jocher, A. Chaurasia, and J. Qiu, "Ultralytics YOLO (version 8.4.148)," GitHub, 2023. '
    '[Online]. Available: https://github.com/ultralytics/ultralytics. [Accessed: Mar. 2025]. '
    'Version 8.4.148 used in this work.',

    # N4 clarification: 88 annotations vs 49 images
    '25 carry roya annotations (3.0% of test roya instances), '
    '12 carry coco annotations (1.5%), and '
    '88 carry minador annotations (23.5%).':
    '25 roya annotations (3.0% of test roya instances; some images carry multiple instances), '
    '12 coco annotations (1.5%), and 88 minador annotations (23.5%) are from the 49 affected images.',

    # N3: PyTorch note — add version provenance note
    'PyTorch 2.11, CUDA 12.8':
    'PyTorch 2.11.0+cu128, CUDA 12.8',
}

n_changed = 0
for p in doc.paragraphs:
    full_text = "".join(run.text for run in p.runs)
    new_text = full_text
    for old, new in fixes.items():
        if old in new_text:
            new_text = new_text.replace(old, new)
    if new_text != full_text:
        for i, run in enumerate(p.runs):
            if i == 0:
                run.text = new_text
            else:
                run.text = ""
        n_changed += 1

print(f"Fixed {n_changed} paragraphs")

# Verify no banned strings
all_text = " ".join("".join(run.text for run in p.runs) for p in doc.paragraphs)
banned = ['92.4%','76.6%','2,786','Coccinellidae','Pseudococcidae','leakage-free','sin fuga','no leakage']
found = [b for b in banned if b in all_text]
print("Banned strings:", "PASS" if not found else f"FAIL: {found}")

# Word count
wc = len(all_text.split())
print(f"Word count: {wc}")

# Save v3
out = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v3.docx"
doc.save(out)
print(f"Saved: {out}")

# Anonymous v3
doc_anon = Document(out)
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
    ("Bucaramanga, Colombia", "[INSTITUTION-CITY]"),
]
for p in doc_anon.paragraphs:
    full_text = "".join(run.text for run in p.runs)
    new_text = full_text
    for orig, repl in anon_map:
        new_text = new_text.replace(orig, repl)
    if new_text != full_text:
        for i, run in enumerate(p.runs):
            if i == 0: run.text = new_text
            else: run.text = ""

anon_out = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v3_anonymous.docx"
doc_anon.save(anon_out)
print(f"Saved anonymous: {anon_out}")

# PII check
anon_text = " ".join("".join(r.text for r in p.runs) for p in doc_anon.paragraphs)
pii = [x for x in ["Luis Esteban Rosas Ruiz", "luis.rosas@correo.uis.edu.co", "0000-0003-0233-6336"] if x in anon_text]
print("Anonymous PII check:", "PASS" if not pii else f"FAIL: {pii}")

sha = hashlib.sha256(out.read_bytes()).hexdigest()
print(f"v3 SHA-256: {sha[:16]}")
