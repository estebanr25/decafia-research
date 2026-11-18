"""
Build cover_letter_v4.docx — Decision 5 from SESSION_FINAL_PASS:
  Remove all same-day preprint language.
  Request Editorial Committee authorization for Zenodo preprint.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt

MANUSCRIPT_DIR = Path("C:/Users/luise/temp/decafia-research/paper1/manuscript")

doc = Document()
doc.add_heading("Cover Letter", 0)

body = """To the Editor-in-Chief,
Ingeniería e Investigación

Dear Editor,

I am submitting the original research article titled "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions" for consideration for publication in Ingeniería e Investigación.

Originality and contribution. This manuscript presents DECAFIA, an annotated dataset for multi-class object detection of coffee foliar conditions under Colombian Andean field conditions. The dataset addresses a recognized gap in publicly available agricultural image datasets for Colombia and provides instance-level bounding-box annotations for three foliar conditions simultaneously (coffee leaf rust, weevil damage, leaf-miner damage). The integrity audit and sensitivity analysis included in the manuscript are, to the author's knowledge, among the first published for a coffee leaf disease dataset.

No simultaneous submission. This manuscript has not been submitted to any other journal and is not under consideration elsewhere.

Sole authorship. This article has a single author: Luis Esteban Rosas Ruiz. The research derives from an undergraduate thesis at the Universidad Industrial de Santander directed by Prof. Jaime Guillermo Barrero Pérez, whose contributions are fully credited in the Acknowledgements section. Per the journal's authorship criteria (substantial contribution + drafting/revising + approval of final version), no other person qualifies as an author.

Request for preprint authorization. The journal's ethics policy states that posting articles in non-commercial preprint repositories requires prior evaluation by the Editorial Committee. I therefore respectfully request the Editorial Committee's authorization to post this manuscript as a preprint on Zenodo (non-commercial repository) once a decision on this submission has been reached. I will not post any preprint prior to receiving such authorization. I will disclose the preprint link in the manuscript upon authorization.

Data and code availability. The dataset, model weights, and all evaluation code are publicly available at the links provided in the manuscript.

I look forward to the reviewers' feedback.

Sincerely,

Luis Esteban Rosas Ruiz
Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)
Universidad Industrial de Santander, Bucaramanga, Colombia
luis.rosas@correo.uis.edu.co
ORCID: 0000-0003-0233-6336
"""

for para in body.split("\n"):
    p = doc.add_paragraph(para)
    p.style.font.size = Pt(11)

out = MANUSCRIPT_DIR / "cover_letter_v4.docx"
doc.save(out)
print(f"Saved: {out}")

# Check: no same-day preprint language
text = body.lower()
bad = ["same day", "same-day", "on the day of submission", "simultaneously"]
found = [b for b in bad if b in text]
print(f"Preprint language check: {'PASS' if not found else 'FAIL: ' + str(found)}")
