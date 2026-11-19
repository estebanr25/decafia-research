"""
build_manuscript_v6.py

Applies all changes from SESSION_FINAL_V6.md to v5 -> v6:
  1. Reference corrections (replace [6], rewrite [8], update [11], remove [13])
  2. FNC number updates (557,000 / 600+ municipalities)
  3. Avelino [2] sentence correction
  4. Remove all [VERIFY] markers
  5. Add figures (Fig_examples and Fig_schematic)
  6. Renumber all figures in citation order
  7. Save CoffeeLeafCO_manuscript_v6.docx
  8. Save CoffeeLeafCO_manuscript_v6_anonymous.docx

Run from: C:/Users/luise/temp/decafia-research
"""
import sys
import copy
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import lxml.etree as etree

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"
FIGURES_DIR = REPO / "paper1/figures"
SUBMISSION_DIR = MANUSCRIPT_DIR / "figures_submission"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def merge_runs(para):
    full_text = "".join(run.text for run in para.runs)
    if not para.runs:
        return full_text
    para.runs[0].text = full_text
    for run in para.runs[1:]:
        run.text = ""
    return full_text


def replace_in_para(para, old, new):
    full_text = merge_runs(para)
    if old in full_text:
        para.runs[0].text = full_text.replace(old, new)
        return True
    return False


def replace_all_paras(doc, old, new):
    count = 0
    for para in doc.paragraphs:
        if replace_in_para(para, old, new):
            count += 1
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if replace_in_para(para, old, new):
                        count += 1
    return count


def get_full_text(doc):
    parts = []
    for para in doc.paragraphs:
        parts.append("".join(run.text for run in para.runs))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    parts.append("".join(run.text for run in para.runs))
    return " ".join(parts)


def remove_para(para):
    p = para._element
    p.getparent().remove(p)


def find_para_containing(doc, text):
    """Return first paragraph whose full text contains `text`."""
    for para in doc.paragraphs:
        t = "".join(run.text for run in para.runs)
        if text in t:
            return para
    return None


def insert_image_after_para(doc, para, image_path, width_inches=5.5, caption_text=None,
                             caption_style="Tables and figures Titles"):
    """Insert an image paragraph after `para`, with optional caption."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    # Create image paragraph
    img_para_elem = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    img_para_elem.insert(0, pPr)

    # Insert after para
    para._element.addnext(img_para_elem)

    # Now create a proper paragraph using the Document API (temporary hack)
    # We'll use a run with inline image
    img_para = doc.add_paragraph()
    img_run = img_para.add_run()
    try:
        img_run.add_picture(str(image_path), width=Inches(width_inches))
        img_para.alignment = 1  # center
    except Exception as e:
        img_para.text = f"[Figure: {image_path.name}]"
        print(f"  Warning: could not embed image {image_path}: {e}")

    # Move the new para element after our placeholder
    img_para_elem.addnext(img_para._element)
    img_para_elem.getparent().remove(img_para_elem)

    # Caption paragraph
    if caption_text:
        cap_para = doc.add_paragraph(caption_text)
        try:
            cap_para.style = caption_style
        except Exception:
            pass
        img_para._element.addnext(cap_para._element)
        # Move cap_para element to be right after img_para
        # It's already appended to doc.paragraphs, so just move in XML
        return img_para, cap_para

    return img_para, None


# ---------------------------------------------------------------------------
# Load v5
# ---------------------------------------------------------------------------
print("Loading CoffeeLeafCO_manuscript_v5.docx ...")
doc = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v5.docx")

changes_log = []

# ---------------------------------------------------------------------------
# PART 1: Reference [2] — Avelino sentence correction
# ---------------------------------------------------------------------------
print("Step 1: Avelino [2] sentence correction ...")

# In intro paragraph
count = replace_all_paras(doc,
    "Coffee leaf rust (Hemileia vastatrix) caused production losses exceeding 30% in affected Colombian farms during the 2008\u20132013 epidemic [2].",
    "Coffee leaf rust reduced Colombian coffee production by 31% on average during the 2008\u20132011 epidemic years compared with 2007 [2]."
)
changes_log.append(("[2] Avelino sentence - intro", count))
print(f"  Avelino intro: {count}")

# Fix the full citation [2]
count = replace_all_paras(doc,
    "[2] J. Avelino et al., \"The coffee rust crises in Colombia and Central America (2008\u20132013),\" Food Security, vol. 7, pp. 303\u2013321, 2015, doi: 10.1007/s12571-015-0446-9.",
    "[2] J. Avelino, M. Cristancho, S. Georgiou, P. Imbach, L. Aguilar, G. Bornemann, P. L\u00e4derach, F. Anzueto, A. J. Hruska, C. Morales, \"The coffee rust crises in Colombia and Central America (2008\u20132013),\" Food Security, vol. 7, no. 2, pp. 303\u2013321, 2015, doi: 10.1007/s12571-015-0446-9."
)
changes_log.append(("[2] Full citation update", count))
print(f"  Avelino citation: {count}")

# ---------------------------------------------------------------------------
# PART 1: FNC numbers update [1] — 557,000 families, 600+ municipalities
# ---------------------------------------------------------------------------
print("Step 2: FNC numbers update ...")

# Abstract
count = replace_all_paras(doc,
    "Coffee cultivation supports approximately 550,000 farming families in Colombia,",
    "Coffee cultivation supports approximately 557,000 farming families in Colombia,"
)
changes_log.append(("[1] FNC - abstract", count))
print(f"  FNC abstract: {count}")

# Resumen (Spanish)
count = replace_all_paras(doc,
    "El cultivo del caf\u00e9 sostiene a aproximadamente 550,000 familias en Colombia,",
    "El cultivo del caf\u00e9 sostiene a aproximadamente 557,000 familias en Colombia,"
)
changes_log.append(("[1] FNC - resumen", count))
print(f"  FNC resumen: {count}")

# Introduction paragraph - 550,000 → 557,000
count = replace_all_paras(doc,
    "generating income for approximately 550,000 farming families across more than 590 municipalities in Colombia [1].",
    "generating income for approximately 557,000 farming families across more than 600 municipalities in Colombia [1]."
)
changes_log.append(("[1] FNC - intro", count))
print(f"  FNC intro: {count}")

# ---------------------------------------------------------------------------
# PART 1: Reference [6] REPLACE — Pacal et al. 2024
# ---------------------------------------------------------------------------
print("Step 3: Replace reference [6] (Sajitha → Pacal) ...")

# Replace in-text sentence (keep same citation number)
count = replace_all_paras(doc,
    "Review studies confirm EfficientNet, ResNet, and VGG architectures across a range of crop-disease pairs [6].",
    "Review studies confirm EfficientNet, ResNet, and VGG architectures across a range of crop-disease pairs [6]."
)
# sentence is the same, fine — just update the reference entry

# Replace reference entry
count = replace_all_paras(doc,
    "[6] A. Sajitha et al., \"A comprehensive review of CNN-based plant disease detection,\" Artif. Intell. Rev., vol. 58, pp. 1\u201345, 2025, doi: 10.1007/s10462-024-11052-2. [VERIFY DOI]",
    "[6] I. Pacal, I. Kunduracioglu, M. H. Alma, M. Deveci, S. Kadry, \"A systematic review of deep learning techniques for plant diseases,\" Artificial Intelligence Review, vol. 57, no. 11, art. 304, 2024, doi: 10.1007/s10462-024-10944-7."
)
changes_log.append(("[6] Replace Sajitha → Pacal", count))
print(f"  [6] replace: {count}")

# ---------------------------------------------------------------------------
# PART 1: Reference [8] REWRITE — Zúñiga Cajas
# ---------------------------------------------------------------------------
print("Step 4: Rewrite [8] Zúñiga Cajas ...")

count = replace_all_paras(doc,
    "For coffee leaf rust severity specifically, Z\u00fa\u00f1iga Cajas et al. [8] reported mAP@0.50 = 0.843 with a custom YOLOv8 architecture trained on 1,423 images from Ecuadorean plantations, using a severity scale derived from CABI guidelines.",
    "For coffee leaf rust severity specifically, Z\u00fa\u00f1iga Cajas et al. [8] evaluated thirteen CNN classifiers for coffee leaf rust severity classification using images from Costa Rican plantations, reporting a best F1 of approximately 0.80 for five-class severity classification [8]."
)
changes_log.append(("[8] Rewrite Zúñiga Cajas", count))
print(f"  [8] rewrite: {count}")

# Update the reference entry for [8] (citation data was already correct in v5 — keep it)
# The citation in v5 is correct: Inteligencia Artificial 28(76), 200–222, 2025

# ---------------------------------------------------------------------------
# PART 1: Reference [11] VIA — UPDATE to ACM MM'19
# ---------------------------------------------------------------------------
print("Step 5: Update [11] VIA reference ...")

count = replace_all_paras(doc,
    "[11] A. Dutta and A. Zisserman, \"The VGG image annotator (VIA),\" Image Vis. Comput., vol. 89, pp. 188\u2013196, 2019, doi: 10.1016/j.imavis.2019.06.011. [Also available as arXiv:1904.10699; ACM DOI: VERIFY]",
    "[11] A. Dutta and A. Zisserman, \"The VIA Annotation Software for Images, Audio and Video,\" in Proc. 27th ACM Int. Conf. Multimedia (MM '19), Nice, France, 2019, arXiv:1904.10699."
)
changes_log.append(("[11] VIA update to ACM MM'19", count))
print(f"  [11] update: {count}")

# Remove [VERIFY DOI] marker from text (also catch [VERIFY] in annotation protocol section)
count = replace_all_paras(doc, " [VERIFY DOI]", "")
count += replace_all_paras(doc, "[VERIFY DOI]", "")
changes_log.append(("Remove [VERIFY DOI]", count))
print(f"  [VERIFY DOI] removed: {count}")

count = replace_all_paras(doc, " [VERIFY]", "")
count += replace_all_paras(doc, "[VERIFY]", "")
changes_log.append(("Remove [VERIFY]", count))
print(f"  [VERIFY] removed: {count}")

# Remove [Also available as arXiv...] from [11] entry if any remnant
count = replace_all_paras(doc, " [Also available as arXiv:1904.10699; ACM DOI: VERIFY]", "")
changes_log.append(("Remove arXiv VERIFY note", count))

# ---------------------------------------------------------------------------
# PART 1: Reference [13] REMOVE — Constantino Roya del Cafeto
# ---------------------------------------------------------------------------
print("Step 6: Remove [13] ...")

# Fix [3, 13] → [3] in class definitions paragraph
count = replace_all_paras(doc, "[3, 13]", "[3]")
changes_log.append(("[13] remove from [3,13]", count))
print(f"  [3,13] → [3]: {count}")

# Fix "[13]" standalone anywhere in text
count = replace_all_paras(doc, " [13]", "")
count += replace_all_paras(doc, "[13]", "")
changes_log.append(("[13] remove standalone", count))
print(f"  [13] standalone removed: {count}")

# Remove reference [13] entry
count = replace_all_paras(doc,
    "[13] L. M. Constantino et al., \"Roya del Cafeto,\" in Manual del Cafetero Colombiano, vol. 2, Cenicaf\u00e9, Chinchi\u00f1\u00e1, Colombia, 2013, doi: 10.38141/cenbook-0026_25.",
    ""
)
changes_log.append(("[13] Remove reference entry", count))
print(f"  [13] entry removed: {count}")

# Remove any paragraph that is now just empty (has only whitespace)
# Note: we can't easily find empty paras by text alone, skip for now

# Renumber [14]-[18] → [13]-[17]
# Strategy: use temp placeholders to avoid cascading collisions
print("Step 7: Renumber [14]-[18] → [13]-[17] ...")

# Phase A: replace all [14]-[18] with temp markers (no collisions since temps are unique)
temp_map = [
    ("[14]", "[[TMP14]]"),
    ("[15]", "[[TMP15]]"),
    ("[16]", "[[TMP16]]"),
    ("[17]", "[[TMP17]]"),
    ("[18]", "[[TMP18]]"),
]
for old, temp in temp_map:
    c = replace_all_paras(doc, old, temp)
    print(f"  Phase A {old} → {temp}: {c}")

# Also update reference entry prefixes (which still start with the original numbers
# because merge_runs was called, but the reference entries in the doc are whole paragraphs)
# The reference entries were already changed above but we need to fix duplicates
# Let's also temp-replace reference entry prefixes to avoid any remaining issues
ref_temp_map = [
    # These are now the already-renamed reference entries (Jocher, Lin, etc.)
    # but they still have the old [14]/[15]/etc. prefix
    # Actually by now they still have the old number since we haven't renamed them yet
    # ref entries start with "[14] G. Jocher", "[15] T.-Y. Lin", etc.
    # They were converted to temp above: "[[TMP14]] G. Jocher" etc.
]

# Phase B: replace temps with correct new numbers
final_map = [
    ("[[TMP14]]", "[13]"),
    ("[[TMP15]]", "[14]"),
    ("[[TMP16]]", "[15]"),
    ("[[TMP17]]", "[16]"),
    ("[[TMP18]]", "[17]"),
]
for temp, new in final_map:
    c = replace_all_paras(doc, temp, new)
    print(f"  Phase B {temp} → {new}: {c}")
    changes_log.append((f"Renumber {temp} → {new}", c))

# ---------------------------------------------------------------------------
# PART 3: Figure renumbering
# Current figures in v5:
#   Fig. 3a — confusion matrix raw
#   Fig. 3b — confusion matrix normalized
#   Fig. 5 — training curves
#   Fig. 7 — bootstrap CIs
#
# New figures to add:
#   Fig_examples — Section 3.1 (first)
#   Fig_schematic — Section 4.3 (third, after training curves)
#
# Citation order in text:
#   Section 3.1: Fig_examples → Fig. 1
#   Section 4.1: Fig. 5 (training curves) → Fig. 2
#   Section 4.3: Fig_schematic → Fig. 3
#   Section 5.2: Fig. 7 (bootstrap CIs) → Fig. 4
#   Section 5.4: Fig. 3b (confusion matrix normalized) → Fig. 5b
#   Section 5.4: Fig. 3a (confusion matrix raw) → Fig. 5a
# ---------------------------------------------------------------------------
print("Step 8: Figure renumbering ...")

# Rename existing figure captions and in-text refs
# Step 1: Use temp markers to avoid collision
fig_rename = [
    # In-text references (from text)
    ("Fig. 7 shows mAP@0.50 per class", "Fig. 4 shows mAP@0.50 per class"),
    ("(Fig. 3b)", "(Fig. 5b)"),
    ("(Fig. 3a)", "(Fig. 5a)"),
    ("Fig. 3a.", "Fig. 5a."),
    ("Fig. 3b.", "Fig. 5b."),
    # Caption references for Fig. 5 → Fig. 2
    ("Fig. 5. Training curves", "Fig. 2. Training curves"),
    # Caption references for Fig. 7
    ("Fig. 7. mAP@0.50 per class", "Fig. 4. mAP@0.50 per class"),
    # Same test set reference in Fig 3b caption
    ("Same test set as Fig. 3a.", "Same test set as Fig. 5a."),
    # Fig captions full text
    ("Fig. 3a. Confusion matrix for decafia_grouped_v1", "Fig. 5a. Confusion matrix for decafia_grouped_v1"),
    ("Fig. 3b. Confusion matrix", "Fig. 5b. Confusion matrix"),
]

for old, new in fig_rename:
    c = replace_all_paras(doc, old, new)
    if c:
        print(f"  Fig rename '{old[:40]}' → '{new[:40]}': {c}")
        changes_log.append((f"Fig rename", c))

# ---------------------------------------------------------------------------
# PART 3: Insert new figures into manuscript
# ---------------------------------------------------------------------------
print("Step 9: Insert figures ...")

# Insert Fig. 1 (examples) after Section 3.1 source descriptions
# Find paragraph starting with "Source 2 — Silva et al."
fig1_anchor = find_para_containing(doc, "Source 2 \u2014 Silva et al. (Brazil, re-annotated). Rust and leaf-miner")
if fig1_anchor is None:
    fig1_anchor = find_para_containing(doc, "Source 2")
print(f"  Fig1 anchor: {fig1_anchor.text[:60] if fig1_anchor else 'NOT FOUND'}")

# Insert Fig. 3 (schematic) after integrity audit paragraph
fig3_anchor = find_para_containing(doc,
    "An integrity audit was conducted to identify and quantify transformed-copy overlap")
print(f"  Fig3 anchor: {fig3_anchor.text[:60] if fig3_anchor else 'NOT FOUND'}")

# Caption texts
FIG1_CAPTION = (
    "Fig. 1. Example annotated images. Left column: own-field images (El Socorro, Colombia). "
    "Right column: Silva et al. images (Brazil). Rows: (a\u2013b) rust (roya); (c\u2013d) weevil damage (coco); "
    "(e\u2013f) healthy background; (g\u2013h) rust from Silva et al.; (i\u2013j) leaf-miner (minador). "
    "Bounding boxes are ground-truth annotations (red = roya, blue = coco, green = minador)."
)
FIG3_CAPTION = (
    "Fig. 3. Dataset construction and integrity audit pipeline. "
    "Numbers rendered from repository files (split_v2/assignments_v2.csv, "
    "split_v2/copy_pairs.csv, paper1/results/metrics_final.json)."
)

# Reference to Fig. 1 and Fig. 3 in text
# Add "(Fig. 1)" after the Source 2 paragraph in Section 3.1
# Find a good insertion point: after both source paragraphs in 3.1
# The sentence after sources says "The CoffeeLeaf-CO dataset integrates images from two sources"
# We'll add an in-text reference at the end of the source 2 paragraph description

# Add "(see Fig. 1)" to the end of source2 para
if fig1_anchor:
    replace_in_para(fig1_anchor,
        "This source contributes all leaf-miner (minador) instances and a portion of roya instances (image prefixes: ROYA_FONDO, ROYA_RECORTES, all MINADO_* and MINADOR_*).",
        "This source contributes all leaf-miner (minador) instances and a portion of roya instances (image prefixes: ROYA_FONDO, ROYA_RECORTES, all MINADO_* and MINADOR_*). Example annotated images from both sources are shown in Fig. 1."
    )

# Add "(Fig. 3)" to audit section sentence
audit_para = find_para_containing(doc,
    "The largest verified component (272 images) comprises a cross-source leaf group")
if audit_para:
    replace_in_para(audit_para,
        "This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split while maintaining all three classes in the test set (Section 5.3).",
        "This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split while maintaining all three classes in the test set (Section 5.3). The full audit pipeline is illustrated in Fig. 3."
    )

# Now insert images as paragraphs
def insert_text_figure_ref(doc, anchor_para, image_path, caption_text,
                            caption_style_name="Tables and figures Titles"):
    """
    Insert a figure (image + caption paragraph) into the document body
    immediately after anchor_para.
    """
    # Build a new 'run with picture' paragraph
    img_para = doc.add_paragraph()
    img_para.alignment = 1  # WD_ALIGN_PARAGRAPH.CENTER
    if image_path.exists():
        try:
            run = img_para.add_run()
            run.add_picture(str(image_path), width=Inches(5.0))
        except Exception as e:
            img_para.text = f"[Figure: {image_path.name}]"
            print(f"  Could not embed {image_path.name}: {e}")
    else:
        img_para.text = f"[Figure: {image_path.name} — file not found]"
        print(f"  Warning: {image_path} not found")

    # Build caption paragraph
    cap_para = doc.add_paragraph(caption_text)
    try:
        cap_para.style = caption_style_name
    except Exception:
        pass

    # Move both elements after anchor_para in XML
    # Insert cap_para first, then img_para before it
    anchor_para._element.addnext(cap_para._element)
    anchor_para._element.addnext(img_para._element)

    return img_para, cap_para


if fig1_anchor:
    img1_png = FIGURES_DIR / "figure_annotated_examples.png"
    insert_text_figure_ref(doc, fig1_anchor, img1_png, FIG1_CAPTION)
    print(f"  Inserted Fig. 1 after anchor para")
else:
    print("  WARNING: Fig1 anchor not found")

if fig3_anchor:
    img3_png = FIGURES_DIR / "figure_split_schematic.png"
    # Find the second paragraph in section 4.3 (the MINEIRO component one)
    mineiro_para = find_para_containing(doc,
        "The largest verified component (272 images)")
    if mineiro_para is None:
        mineiro_para = fig3_anchor
    insert_text_figure_ref(doc, mineiro_para, img3_png, FIG3_CAPTION)
    print(f"  Inserted Fig. 3 after anchor para")
else:
    print("  WARNING: Fig3 anchor not found")

# Add in-text references to Fig. 1 and Fig. 3 in running text
# Check Section 3.2 which describes the split — add Fig. 3 reference
# Check if Fig. 1 already cited
full_text_check = get_full_text(doc)
if "Fig. 1" not in full_text_check:
    print("  WARNING: Fig. 1 not cited in text")
if "Fig. 2" not in full_text_check:
    # Training curves reference in Section 4.1
    # The section just references training log; add a reference
    training_para = find_para_containing(doc,
        "The best checkpoint was saved at epoch 97")
    if training_para:
        replace_in_para(training_para,
            "The best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924).",
            "The best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924; training curves in Fig. 2)."
        )
        print("  Added Fig. 2 reference in Section 4.1")
if "Fig. 3" not in get_full_text(doc):
    print("  WARNING: Fig. 3 not cited in text")
if "Fig. 4" not in full_text_check:
    print("  WARNING: Fig. 4 not cited in text (was Fig. 7)")

# ---------------------------------------------------------------------------
# PART 1: Final cleanup — remove orphaned [13] reference entry (Roya del Cafeto)
# ---------------------------------------------------------------------------
print("Step 10: Cleanup orphaned Roya del Cafeto reference ...")
paras_to_remove = []
for para in doc.paragraphs:
    # Merge runs to get full text
    t = merge_runs(para)
    if "Roya del Cafeto" in t and para.style.name == "References":
        paras_to_remove.append(para)
        print(f"  Removing: {t[:80]}")
for para in paras_to_remove:
    p = para._element
    p.getparent().remove(p)
print(f"  Removed {len(paras_to_remove)} orphaned Roya del Cafeto paragraph(s)")

# ---------------------------------------------------------------------------
# PART 1: Verify no VERIFY markers remain
# ---------------------------------------------------------------------------
full_text = get_full_text(doc)
if "[VERIFY" in full_text:
    print("  WARNING: [VERIFY] markers still present!")
    # Find them
    import re
    for m in re.finditer(r'\[VERIFY[^\]]*\]', full_text):
        print(f"    Found: {full_text[max(0,m.start()-30):m.end()+30]}")
else:
    print("  PASS: No [VERIFY] markers in text")

# ---------------------------------------------------------------------------
# Save v6
# ---------------------------------------------------------------------------
out_v6 = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v6.docx"
doc.save(out_v6)
print(f"Saved: {out_v6}")

# ---------------------------------------------------------------------------
# Anonymous version
# ---------------------------------------------------------------------------
print("Building anonymous version ...")
doc_anon = Document(out_v6)

# Remove author info
anon_paras_remove = []
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if any(x in t for x in [
        "Luis Esteban Rosas Ruiz",
        "Escuela de Ingenier\u00edas El\u00e9ctrica",
        "Corresponding author:",
        "ORCID:",
        "luis.rosas@correo.uis.edu.co",
        "0000-0003-0233-6336",
    ]):
        anon_paras_remove.append(para)
for para in anon_paras_remove:
    remove_para(para)

# Replace author line in title area
replace_all_paras(doc_anon,
    "Luis Esteban Rosas Ruiz\u00b9",
    "[Author details withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    "\u00b9 Escuela de Ingenier\u00edas El\u00e9ctrica, Electr\u00f3nica y de Telecomunicaciones (E3T), Universidad Industrial de Santander, Bucaramanga, Colombia",
    ""
)

# Anonymize data availability URLs
replace_all_paras(doc_anon,
    "https://doi.org/10.5281/zenodo.19931903",
    "[withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    "10.5281/zenodo.19931903",
    "[withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    "https://github.com/estebanr25/decafia-research",
    "[withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    "https://noesis.uis.edu.co/handle/20.500.14071/42486",
    "[withheld for double-blind review]"
)

# Replace CRediT
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if t.strip().startswith("CRediT"):
        merge_runs(para)
        if para.runs:
            para.runs[0].text = "[Author contributions withheld for double-blind review]"

# Replace Acknowledgements content
in_ack = False
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if t.strip() == "Acknowledgements":
        in_ack = True
        continue
    if in_ack and t.strip() and any(t.strip().startswith(x) for x in
                                     ["Data", "Author", "Funding", "Conflicts", "Statement", "References"]):
        in_ack = False
    if in_ack and t.strip():
        merge_runs(para)
        if para.runs:
            para.runs[0].text = "[Acknowledgements withheld for double-blind review]"
        in_ack = False  # only replace first content paragraph

# Reference [16] — Rosas Ruiz thesis — anonymize
replace_all_paras(doc_anon,
    "[16] L. E. Rosas Ruiz and A. F. Salom Medina,",
    "[16] [withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    '"Detecci\u00f3n y prevenci\u00f3n de riesgo de enfermedades en plantaciones de caf\u00e9 mediante inteligencia artificial," Trabajo de Grado',
    '"[withheld for double-blind review]"'
)

# Document properties
anon_props = doc_anon.core_properties
anon_props.title = ("CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images "
                    "for detecting rust, weevil damage and leaf miner")
anon_props.creator = ""
anon_props.last_modified_by = ""
anon_props.description = ""

out_anon = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v6_anonymous.docx"
doc_anon.save(out_anon)
print(f"Saved: {out_anon}")

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
print("\n--- Verification ---")
doc_check = Document(out_v6)
full_text_v6 = get_full_text(doc_check)

BANNED = [
    "92.4%", "76.6%", "2,786",
    "Pseudococcidae",
    "leakage-free", "sin fuga",
    "DECAF-IA",
]
banned_found = []
for b in BANNED:
    if b in full_text_v6:
        banned_found.append(b)

if banned_found:
    print(f"FAIL: Banned strings found: {banned_found}")
else:
    print("PASS: No banned strings found")

if "[VERIFY" in full_text_v6:
    print("FAIL: [VERIFY] markers still present in v6")
else:
    print("PASS: No [VERIFY] markers in v6")

# Check figures cited
for fig in ["Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5"]:
    if fig in full_text_v6:
        print(f"PASS: {fig} cited in text")
    else:
        print(f"WARN: {fig} NOT found in text")

# Check reference numbers
for ref in ["[1]", "[2]", "[6]", "[8]", "[11]", "[13]", "[17]"]:
    n = full_text_v6.count(ref)
    print(f"  Ref {ref} count: {n}")

# Check key numbers
checks = [
    ("557,000 farming families", "557,000"),
    ("more than 600 municipalities", "600 municipalities"),
    ("31%", "31%"),
    ("0.929", "mAP50 overall"),
    ("0.734", "mAP50-95 overall"),
    ("120 total", "120 pairs"),
    ("107 Tier A", "107 Tier A"),
]
for text, label in checks:
    if text in full_text_v6:
        print(f"PASS: {label} present")
    else:
        print(f"WARN: {label} ('{text}') NOT found")

# Word count (approximate — paragraphs only)
wc = len(full_text_v6.split())
print(f"\nWord count (v6, approx): {wc}")

print(f"\n=== DONE ===")
print(f"  {out_v6} — {'EXISTS' if out_v6.exists() else 'MISSING'}")
print(f"  {out_anon} — {'EXISTS' if out_anon.exists() else 'MISSING'}")
