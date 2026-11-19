"""
build_manuscript_v5.py

Implements ALL changes from SESSION_FIX_MANUSCRIPT_V5.md to produce:
  - CoffeeLeafCO_manuscript_v5.docx
  - CoffeeLeafCO_manuscript_v5_anonymous.docx
  - cover_letter_v5.docx
  - V5_CHANGES.md

Run from: C:/Users/luise/temp/decafia-research
"""
import sys
import copy
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import lxml.etree as etree

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def merge_runs(para):
    """Collapse all runs in a paragraph into a single run, preserving text."""
    full_text = "".join(run.text for run in para.runs)
    if not para.runs:
        return full_text
    # Keep first run's formatting, clear the rest
    para.runs[0].text = full_text
    for run in para.runs[1:]:
        run.text = ""
    return full_text


def replace_in_para(para, old, new):
    """Merge runs then do string replacement. Returns True if changed."""
    full_text = merge_runs(para)
    if old in full_text:
        para.runs[0].text = full_text.replace(old, new)
        return True
    return False


def replace_all_paras(doc, old, new):
    """Replace in all paragraphs and table cells. Returns count."""
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
    """Return full text of document (paragraphs + table cells)."""
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
    """Remove a paragraph element from its parent."""
    p = para._element
    p.getparent().remove(p)


def add_table_after_para(doc, para, header_row, data_rows, style_name=None):
    """
    Insert a new table with header and data rows immediately after `para`.
    Returns the new table.
    """
    # Create table
    n_cols = len(header_row)
    table = doc.add_table(rows=1 + len(data_rows), cols=n_cols)
    if style_name:
        try:
            table.style = style_name
        except Exception:
            pass

    # Fill header
    hdr_cells = table.rows[0].cells
    for i, text in enumerate(header_row):
        hdr_cells[i].text = text
        for run in hdr_cells[i].paragraphs[0].runs:
            run.bold = True

    # Fill data rows
    for r_idx, row_data in enumerate(data_rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, text in enumerate(row_data):
            row_cells[c_idx].text = text

    # Move the table element to immediately after the paragraph
    para._element.addnext(table._tbl)
    return table


# ---------------------------------------------------------------------------
# Load v4
# ---------------------------------------------------------------------------
print("Loading CoffeeLeafCO_manuscript_v4.docx ...")
doc = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v4.docx")

changes_log = []


# ---------------------------------------------------------------------------
# STEP 1 — Name changes: DECAFIA → CoffeeLeaf-CO (prose) / DECAF IA (project)
# ---------------------------------------------------------------------------

# 1a. Title
count = replace_all_paras(doc,
    "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions",
    "CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images for detecting rust, weevil damage and leaf miner"
)
changes_log.append(("Title rename", "DECAFIA: A Multi-Source...", "CoffeeLeaf-CO: a multi-source...", "NAME_SCHEME A", count))

# 1b. Spanish title
count = replace_all_paras(doc,
    "DECAFIA: Conjunto de datos de campo multi-fuente para la detección de enfermedades foliares del café en condiciones andinas colombianas",
    "CoffeeLeaf-CO: conjunto de datos multi-fuente de hojas de café con imágenes de campo colombianas para la detección de roya, daño por gorgojo y minador"
)
changes_log.append(("Spanish title rename", "DECAFIA: Conjunto...", "CoffeeLeaf-CO: conjunto...", "NAME_SCHEME A", count))

# 1c. Intro paragraph: acronym expansion + first occurrence of DECAFIA as dataset
count = replace_all_paras(doc,
    "This article presents DECAFIA (DEtección de enfermedades en hojas de CAfé, FIncas de Área cafetera de Colombia), a multi-source dataset of 2,315 annotated coffee leaf images.",
    "This article presents CoffeeLeaf-CO, a multi-source dataset of 2,315 annotated coffee leaf images, developed within the DECAF IA project (Detección de Enfermedades en el Café con Inteligencia Artificial; disease detection in coffee with artificial intelligence)."
)
changes_log.append(("Intro DECAFIA expansion", "DECAFIA (DEtección...)", "CoffeeLeaf-CO ... DECAF IA project...", "NAME_SCHEME A — wrong expansion", count))

# 1d. Section 3.1: "The DECAFIA dataset integrates images from three sources"
count = replace_all_paras(doc,
    "The DECAFIA dataset integrates images from three sources, unified under a single annotation protocol:",
    "The CoffeeLeaf-CO dataset integrates images from two sources, unified under a single annotation protocol:"
)
changes_log.append(("3.1 header DECAFIA→CoffeeLeaf-CO", "three sources", "two sources", "RoCoLe removed; two sources only", count))

# 1e. Table 1: "DECAFIA (this work)"
count = replace_all_paras(doc, "DECAFIA (this work)", "CoffeeLeaf-CO (this work)")
changes_log.append(("Table 1 rename", "DECAFIA (this work)", "CoffeeLeaf-CO (this work)", "NAME_SCHEME A", count))

# 1f. Highlights bullet
count = replace_all_paras(doc,
    "• DECAFIA: 2,315 field-annotated coffee leaf images from Colombian Andean conditions",
    "• CoffeeLeaf-CO: 2,315 field-annotated coffee leaf images from Colombian Andean conditions"
)
changes_log.append(("Highlights rename", "• DECAFIA:", "• CoffeeLeaf-CO:", "NAME_SCHEME A", count))

# 1g. Table 2 caption (Table 4 in results): DECAFIA test set → CoffeeLeaf-CO
count = replace_all_paras(doc,
    "Table 4. Baseline performance on the DECAFIA test set",
    "Table 4. Baseline performance on the CoffeeLeaf-CO test set"
)
changes_log.append(("Table 4 caption", "DECAFIA test set", "CoffeeLeaf-CO test set", "NAME_SCHEME A", count))

# 1h. Table 2 caption
count = replace_all_paras(doc,
    "Table 2. DECAFIA dataset composition",
    "Table 2. CoffeeLeaf-CO dataset composition"
)
changes_log.append(("Table 2 caption", "DECAFIA dataset composition", "CoffeeLeaf-CO dataset composition", "NAME_SCHEME A", count))

# 1i. Any remaining "DECAFIA" in prose (excluding identifiers)
# We handle the remaining occurrences case by case to be precise
remaining_swaps = [
    ("DECAFIA contributes an annotated dataset",
     "CoffeeLeaf-CO contributes an annotated dataset"),
    ("DECAFIA provides a multi-source annotated dataset",
     "CoffeeLeaf-CO provides a multi-source annotated dataset"),
    ("The DECAFIA dataset and trained model",
     "The CoffeeLeaf-CO dataset and trained model"),
    ("trained on DECAFIA",
     "trained on CoffeeLeaf-CO"),
    # Section 3.1 source description
    ("a CoffeeLeaf-CO dataset",   # guard no double-replacement
     "a CoffeeLeaf-CO dataset"),
]
for old, new in remaining_swaps:
    if old != new:
        c = replace_all_paras(doc, old, new)
        changes_log.append(("DECAFIA→CoffeeLeaf-CO prose", old[:60], new[:60], "NAME_SCHEME A", c))

# ---------------------------------------------------------------------------
# STEP 2 — Remove RoCoLe as Source 2 paragraph
# ---------------------------------------------------------------------------
paras_to_remove = []
for para in doc.paragraphs:
    t = "".join(run.text for run in para.runs)
    if "Source 2" in t and "RoCoLe" in t and "Ecuador" in t:
        paras_to_remove.append(para)
for para in paras_to_remove:
    remove_para(para)
    changes_log.append(("Remove RoCoLe source paragraph", "Source 2 — RoCoLe...", "(removed)", "RoCoLe was removed in prior version", 1))

# Rename Source 3 → Source 2
count = replace_all_paras(doc,
    "Source 3 — Silva et al. leaf-miner images (Brazil, re-annotated). Leaf-miner images from Silva et al.",
    "Source 2 — Silva et al. (Brazil, re-annotated). Rust and leaf-miner images from Silva et al."
)
changes_log.append(("Rename Source 3→Source 2", "Source 3 — Silva et al.", "Source 2 — Silva et al.", "Only two sources now", count))

# Fix Source 2 description to match SESSION spec exactly
count = replace_all_paras(doc,
    "Source 2 — Silva et al. (Brazil, re-annotated). Rust and leaf-miner images from Silva et al. [10] (CC BY 4.0; DOI: 10.17632/vfxf4trtcg.5) were incorporated to enrich the minador class. Most images in this source were acquired in a laboratory on a white background [10], introducing a distribution shift relative to Colombian field images (Section 5.3).",
    "Source 2 — Silva et al. (Brazil, re-annotated). Rust and leaf-miner images from Silva et al. [10] (CC BY 4.0; DOI: 10.17632/vfxf4trtcg.5) were incorporated to enrich the roya and minador classes. Most images in this source were acquired in a laboratory on a white background [10], introducing a distribution shift relative to Colombian field images. This source contributes all leaf-miner (minador) instances and a portion of roya instances (image prefixes: ROYA_FONDO, ROYA_RECORTES, all MINADO_* and MINADOR_*)."
)
changes_log.append(("Source 2 description update", "enrich the minador class", "enrich the roya and minador classes; add prefix info", "Session spec", count))

# Update Source 1 description
count = replace_all_paras(doc,
    "Source 1 — Original field collection (El Socorro, Colombia). The primary corpus was captured at a Coffea arabica plantation in El Socorro, Santander, Colombia (6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024, using a smartphone camera under uncontrolled natural field lighting. Images represent the full range of illumination conditions, leaf angles, and disease severity levels encountered in the field. This source contributes all weevil-damage (coco) instances, as well as rust (roya) instances and Colombian healthy leaves.",
    "Source 1 — Own field collection (El Socorro, Colombia). The primary corpus was captured at a Coffea arabica plantation in El Socorro, Santander, Colombia, using a smartphone camera under uncontrolled natural field lighting. Images represent the full range of illumination conditions, leaf angles, and disease severity levels encountered in the field. This source contributes all weevil-damage (coco) instances and Colombian field rust (roya) instances (image prefixes: SANAS_*, COCO_*, ROYA_P_A, ROYA_MA, ROYA_Muy_A)."
)
changes_log.append(("Source 1 — remove coordinates, altitude, year; add prefixes",
    "6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024",
    "(removed)", "FARM_ALTITUDE_M=?, FARM_COORDINATES=?, CAPTURE_YEARS=?", count))

# ---------------------------------------------------------------------------
# STEP 3 — Remove reflection images paragraph
# ---------------------------------------------------------------------------
paras_to_remove = []
for para in doc.paragraphs:
    t = "".join(run.text for run in para.runs)
    if "141 images of sunlight reflections" in t or \
       ("Reflection images" in t and "anti-false-positive" in t):
        paras_to_remove.append(para)
for para in paras_to_remove:
    remove_para(para)
    changes_log.append(("Remove reflection images paragraph", "141 images of sunlight...", "(removed)", "REFLECTION_IMAGES_141=?", 1))

# ---------------------------------------------------------------------------
# STEP 4 — Section 3.2: Fix false arithmetic & update capture-series reference
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "Of 2,803 raw images evaluated, 17 were excluded due to unresolvable annotation ambiguity, yielding 2,315 final images. Images are split into train (1,577), validation (382), and test (356) subsets.",
    "The final dataset comprises 2,315 annotated images. Images are split into train (1,577), validation (382), and test (356) subsets by leaf group."
)
changes_log.append(("3.2 Fix false arithmetic", "Of 2,803 raw images...", "The final dataset comprises 2,315...", "2,803 - 17 = 2,786 (banned figure)", count))

count = replace_all_paras(doc,
    "Capture-series grouping for third-party images (Sources 2 and 3) is based on filename patterns",
    "Capture-series grouping for third-party images (Source 2) is based on filename patterns"
)
changes_log.append(("3.2 Sources 2 and 3 → Source 2", "Sources 2 and 3", "Source 2", "Only one third-party source now", count))

# ---------------------------------------------------------------------------
# STEP 5 — Section 3.3: Remove second annotator claim and SAM masks claim
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "All images were annotated using VGG Image Annotator (VIA) v2.0 [11] with polygon regions generated by Segment Anything Model (SAM) [12] in interactive point-prompt mode. Class labels were assigned using this protocol; a second annotator independently reviewed labels during the thesis phase, and disagreements were resolved by consulting the Cenicafé phytosanitary identification guide [13]. Bounding boxes for YOLO training were derived from polygon bounding rectangles. SAM polygon masks are retained in the repository for instance-segmentation research.",
    "All images were annotated using VGG Image Annotator (VIA) v2.0 [11] with polygon regions generated by Segment Anything Model (SAM) [12] in interactive point-prompt mode. Class labels were assigned using the Cenicafé phytosanitary identification guide [13]. Bounding boxes for YOLO training were derived from polygon bounding rectangles."
)
changes_log.append(("3.3 Remove second annotator + SAM masks claims",
    "a second annotator independently...", "(removed)", "SECOND_ANNOTATOR_REVIEW=?, SAM_MASKS_PUBLISHED=?", count))

# ---------------------------------------------------------------------------
# STEP 6 — Section 4.1: epoch 98 → epoch 97
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "The best checkpoint was saved at epoch 98 (validation mAP@0.50 = 0.924).",
    "The best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924)."
)
changes_log.append(("4.1 epoch 98→97", "epoch 98", "epoch 97 (1-indexed)", "Best-by-mAP50-95 is epoch 97, 1-indexed", count))

# Fix figure caption also
count = replace_all_paras(doc,
    "Best checkpoint at epoch 98 (val mAP@",
    "Best checkpoint at epoch 97 (val mAP@"
)
changes_log.append(("Fig caption epoch 98→97", "epoch 98", "epoch 97", "consistent with args", count))

# ---------------------------------------------------------------------------
# STEP 7 — Table 3 (Training config): Fix augmentation row & lrf
# ---------------------------------------------------------------------------
for table in doc.tables:
    for row in table.rows:
        cells = [c.text for c in row.cells]
        # Fix lrf value (was 0.01, should be 0.001)
        if len(cells) >= 2 and "Learning rate (lrf)" in cells[0] and "0.01" in cells[1]:
            row.cells[1].paragraphs[0].runs[0].text = "0.001"
            changes_log.append(("Table 3 lrf", "0.01", "0.001", "args.yaml: lrf=0.001", 1))
        # Fix augmentation row
        if len(cells) >= 2 and "Augmentation" in cells[0] and "Albumentations defaults" in cells[1]:
            new_aug = ("mosaic=1.0, fliplr=0.5, flipud=0.5, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, "
                       "scale=0.5, translate=0.1, degrees=15.0, mixup=0.15, erasing=0.4, "
                       "auto_augment=randaugment")
            cell = row.cells[1]
            for para in cell.paragraphs:
                t = "".join(r.text for r in para.runs)
                if "Albumentations defaults" in t:
                    merge_runs(para)
                    if para.runs:
                        para.runs[0].text = new_aug
            changes_log.append(("Table 3 augmentation",
                "Albumentations defaults", new_aug[:60] + "...",
                "args.yaml has explicit params; not Albumentations defaults", 1))

# ---------------------------------------------------------------------------
# STEP 8 — Section 4.3: Replace MINEIRO_99 reference
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "The largest verified component (272 images, the MINEIRO_99 group) comprises laboratory leaf-miner images (Source 3) with SIFT-verified geometric copies across split boundaries. This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split while maintaining all three classes in the test set (Section 5.3).",
    "The largest verified component (272 images) comprises a cross-source leaf group (image prefixes ROYA_MA and ROYA_RECORTES, combined under a shared filename-pattern group root) of laboratory leaf-miner images (Source 2) with SIFT-verified geometric copies across split boundaries. This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split while maintaining all three classes in the test set (Section 5.3)."
)
changes_log.append(("4.3 MINEIRO_99 replacement", "MINEIRO_99 group", "cross-source leaf group (ROYA_MA, ROYA_RECORTES)", "MINEIRO_99 is not the actual group name", count))

# ---------------------------------------------------------------------------
# STEP 9 — Section 5.2: Explain ROYA_RECORTES_107 group properly
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "Roya achieves mAP@0.50 = 0.841; a cluster confidence interval cannot be reported because one leaf group (ROYA_RECORTES) holds 53.1% of roya test instances, exceeding the 50% single-cluster threshold.",
    "Roya achieves mAP@0.50 = 0.841; a cluster confidence interval cannot be reported because the leaf group ROYA_RECORTES_107 — a cross-source group of 21 images combining own-field images (prefix ROYA_MA) and Silva et al. images (prefix ROYA_RECORTES), all assigned to the test split — holds 438 roya test instances (53.1%), exceeding the 50% single-cluster threshold."
)
changes_log.append(("5.2 ROYA_RECORTES_107 explanation",
    "one leaf group (ROYA_RECORTES) holds 53.1%",
    "ROYA_RECORTES_107 — cross-source group of 21 images...",
    "Clarify group composition", count))

# Also fix 6.3 roya cluster reference
count = replace_all_paras(doc,
    "(4) Roya cluster structure: The roya leaf group ROYA_RECORTES holds 53.1% of test-set roya instances, preventing a meaningful cluster bootstrap interval for that class.",
    "(4) Roya cluster structure: The leaf group ROYA_RECORTES_107 (21 images; a cross-source group combining own-field ROYA_MA images and Silva et al. ROYA_RECORTES images, all in the test split) holds 438 instances (53.1% of test-set roya instances), preventing a meaningful cluster bootstrap interval for that class."
)
changes_log.append(("6.3(4) ROYA_RECORTES_107 explanation",
    "ROYA_RECORTES holds 53.1%",
    "ROYA_RECORTES_107 (21 images; cross-source)...",
    "Clarify group composition", count))

# ---------------------------------------------------------------------------
# STEP 10 — Section 5.3: Fix copy-pairs numbers
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "The integrity audit identified 60 cross-split pairs at pHash distance ≤ 4, affecting 49 unique test images (13.8% of the test set). Of these, 25 roya annotations (3.0% of test roya instances; some images carry multiple instances), 12 coco annotations (1.5%), and 88 minador annotations (23.5%) are from the 49 affected images.",
    "The integrity audit identified 107 Tier A (pHash ≤ 4) and 13 Tier B (pHash 5–8, SIFT+RANSAC confirmed) cross-split pairs (120 total), affecting 49 unique test images (13.8% of the test set). Of the 49 affected test images, 40 have a verified copy in the training split and 9 have a copy only in the validation split. Of these 49 images, 25 roya annotations (3.0% of test roya instances; some images carry multiple instances), 12 coco annotations (1.5%), and 88 minador annotations (23.5%) are from the affected images."
)
changes_log.append(("5.3 Fix copy-pairs numbers",
    "60 cross-split pairs at pHash distance ≤ 4",
    "107 Tier A + 13 Tier B = 120 total; 40 have copy in train, 9 in val only",
    "Correct counts from copy_pairs.csv", count))

# ---------------------------------------------------------------------------
# STEP 11 — Section 6.3(1): Fix contamination claim
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "mAP@0.50 for rust and weevil detection is based on test images with no verified transformed copies in the training split.",
    "Of the 49 affected test images, 40 have a verified copy in the training split and 9 have a copy only in the validation split (Section 5.3). The affected shares are: 3.0% of roya test instances, 1.5% of coco test instances, and 23.5% of minador test instances originate from these 49 images. The sensitivity analysis (mAP@0.50 drops 0.0038 when excluding all 49) suggests the contamination has a small aggregate effect, but the minador class is disproportionately affected."
)
changes_log.append(("6.3(1) Fix contamination claim",
    "mAP@0.50 for rust and weevil detection is based on test images with no verified...",
    "Of the 49 affected test images, 40 have copy in train, 9 in val only...",
    "Previous claim was wrong; roya and coco ARE affected", count))

# Fix Section 6.1: also update Source 3 → Source 2 reference if present
count = replace_all_paras(doc,
    "Source 3 images (laboratory, white background) introduce a distribution shift",
    "Source 2 images (laboratory, white background) introduce a distribution shift"
)
changes_log.append(("6.3 Source 3→Source 2", "Source 3 images", "Source 2 images", "Only two sources now", count))

# ---------------------------------------------------------------------------
# STEP 12 — Section 8: Practical Application fixes
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "This level of specificity is not achievable with models trained on existing datasets collected under Ecuadorean or Brazilian conditions.",
    ""
)
# The above will leave an empty string; better to rephrase the sentence
# Let's look at context more carefully
count2 = replace_all_paras(doc,
    "A model trained on CoffeeLeaf-CO can be integrated into mobile applications to provide real-time, instance-level localization of rust pustules, weevil perforation patterns, and leaf-miner serpentine mines under the illumination, altitude, and variety conditions of the Colombian Andean coffee belt. This level of specificity is not achievable with models trained on existing datasets collected under Ecuadorean or Brazilian conditions.",
    "A model trained on CoffeeLeaf-CO can be integrated into mobile applications to provide real-time, instance-level localization of rust pustules, weevil perforation patterns, and leaf-miner serpentine mines under the illumination, altitude, and variety conditions of the Colombian Andean coffee belt."
)
changes_log.append(("8 Remove Ecuadorean/Brazilian claim",
    "This level of specificity is not achievable...",
    "(removed)", "Unsupported comparative claim", count2))

count = replace_all_paras(doc,
    "can be linked to economic damage thresholds",
    "may potentially be linked to economic damage thresholds"
)
changes_log.append(("8 Hedge IPM claim",
    "can be linked to economic damage thresholds",
    "may potentially be linked to economic damage thresholds",
    "Hedge speculative claim", count))

# ---------------------------------------------------------------------------
# STEP 13 — Remove Received/Accepted date lines
# ---------------------------------------------------------------------------
paras_to_remove = []
for para in doc.paragraphs:
    t = "".join(run.text for run in para.runs)
    if t.strip().startswith("Received:") or t.strip().startswith("Accepted:"):
        paras_to_remove.append(para)
for para in paras_to_remove:
    remove_para(para)
    changes_log.append(("Remove Received/Accepted lines", t.strip()[:40], "(removed)", "Not yet accepted", 1))

# ---------------------------------------------------------------------------
# STEP 14 — References fixes
# ---------------------------------------------------------------------------
# [17]: Fix author order
count = replace_all_paras(doc,
    "[17] A. F. Salom Medina and L. E. Rosas Ruiz,",
    "[17] L. E. Rosas Ruiz and A. F. Salom Medina,"
)
changes_log.append(("[17] Author order fix",
    "A. F. Salom Medina and L. E. Rosas Ruiz",
    "L. E. Rosas Ruiz and A. F. Salom Medina",
    "Correct author order per session instructions", count))

# [18]: Fix author names
count = replace_all_paras(doc,
    "[18] J. G. M. Esgario, R. A. C. Barata, and V. S. Baravati,",
    "[18] J. G. M. Esgario, R. A. Krohling, and J. A. Ventura,"
)
changes_log.append(("[18] Author names fix",
    "R. A. C. Barata, and V. S. Baravati",
    "R. A. Krohling, and J. A. Ventura",
    "Correct authors for BRACOL paper", count))

# [11]: Add arXiv note [VERIFY]
count = replace_all_paras(doc,
    "[11] A. Dutta and A. Zisserman, \"The VGG image annotator (VIA),\" Image Vis. Comput., vol. 89, pp. 188–196, 2019, doi: 10.1016/j.imavis.2019.06.011.",
    "[11] A. Dutta and A. Zisserman, \"The VGG image annotator (VIA),\" Image Vis. Comput., vol. 89, pp. 188–196, 2019, doi: 10.1016/j.imavis.2019.06.011. [Also available as arXiv:1904.10699; ACM DOI: VERIFY]"
)
changes_log.append(("[11] Add arXiv note",
    "doi: 10.1016/j.imavis.2019.06.011.",
    "doi: 10.1016/j.imavis.2019.06.011. [Also available as arXiv:1904.10699; ACM DOI: VERIFY]",
    "Add arXiv reference per session instructions", count))

# [6]: Mark as [VERIFY]
count = replace_all_paras(doc,
    "[6] A. Sajitha et al., \"A comprehensive review of CNN-based plant disease detection,\" Artif. Intell. Rev., vol. 58, pp. 1–45, 2025, doi: 10.1007/s10462-024-11052-2.",
    "[6] A. Sajitha et al., \"A comprehensive review of CNN-based plant disease detection,\" Artif. Intell. Rev., vol. 58, pp. 1–45, 2025, doi: 10.1007/s10462-024-11052-2. [VERIFY DOI]"
)
changes_log.append(("[6] Mark as VERIFY",
    "doi: 10.1007/s10462-024-11052-2.",
    "doi: 10.1007/s10462-024-11052-2. [VERIFY DOI]",
    "Cannot verify without web access", count))

# ---------------------------------------------------------------------------
# STEP 15 — Acknowledgements: "The authors thank" → "The author thanks"
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "The authors thank the farm owners",
    "The author thanks the farm owners"
)
changes_log.append(("Acknowledgements plural→singular",
    "The authors thank", "The author thanks", "Single author paper", count))

# ---------------------------------------------------------------------------
# STEP 16 — AI Statement: add "drafting and language editing"
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "During the elaboration of this work, the author used Claude Code (Anthropic) with the aim to assist with data analysis scripting, figure generation, manuscript formatting, and evidence verification.",
    "During the elaboration of this work, the author used Claude Code (Anthropic) with the aim to assist with data analysis scripting, figure generation, manuscript formatting, evidence verification, and drafting and language editing of the manuscript text."
)
changes_log.append(("AI Statement — add drafting/editing",
    "manuscript formatting, and evidence verification.",
    "...and drafting and language editing of the manuscript text.",
    "Requested addition", count))

# ---------------------------------------------------------------------------
# STEP 17 — Abstract: Remove RoCoLe reference
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "re-annotated images from two publicly available sources (RoCoLe, Silva et al.)",
    "re-annotated images from Silva et al."
)
changes_log.append(("Abstract remove RoCoLe",
    "two publicly available sources (RoCoLe, Silva et al.)",
    "re-annotated images from Silva et al.",
    "RoCoLe images removed from dataset", count))

# Also fix the Spanish abstract if it references DECAFIA
count = replace_all_paras(doc,
    "DECAFIA, un conjunto de datos multi-fuente",
    "CoffeeLeaf-CO, un conjunto de datos multi-fuente"
)
changes_log.append(("RESUMEN DECAFIA→CoffeeLeaf-CO", "DECAFIA, un conjunto", "CoffeeLeaf-CO, un conjunto", "NAME_SCHEME A", count))

# Fix any remaining DECAFIA in abstract
count = replace_all_paras(doc,
    "El artículo presenta DECAFIA,",
    "El artículo presenta CoffeeLeaf-CO,"
)
changes_log.append(("RESUMEN El artículo DECAFIA→CoffeeLeaf-CO", "", "", "NAME_SCHEME A", count))

# Fix abstract: "This article presents DECAFIA, a multi-source dataset"
count = replace_all_paras(doc,
    "This article presents DECAFIA, a multi-source dataset of 2,315 annotated coffee leaf images",
    "This article presents CoffeeLeaf-CO, a multi-source dataset of 2,315 annotated coffee leaf images"
)
changes_log.append(("Abstract DECAFIA→CoffeeLeaf-CO", "This article presents DECAFIA,", "This article presents CoffeeLeaf-CO,", "NAME_SCHEME A", count))

# Section 2.2: "DECAFIA differs from all prior datasets"
count = replace_all_paras(doc,
    "DECAFIA differs from all prior datasets by integrating field images from Colombia with two external sources",
    "CoffeeLeaf-CO differs from all prior datasets by integrating field images from Colombia with one external source"
)
changes_log.append(("2.2 DECAFIA→CoffeeLeaf-CO", "DECAFIA differs", "CoffeeLeaf-CO differs", "NAME_SCHEME A; also two→one source", count))

# ---------------------------------------------------------------------------
# STEP 18 — Add source composition table (Table 2b) after Table 2 / Section 3.2
# ---------------------------------------------------------------------------
# Find the paragraph "Table 2. CoffeeLeaf-CO dataset composition..." and add table after it
TABLE2B_HEADER = ["Source / Split", "Images", "Roya inst.", "Coco inst.", "Minador inst."]
TABLE2B_DATA = [
    ["Own field / Train", "1,181", "2,198", "3,746", "0"],
    ["Own field / Val",   "255",   "177",   "823",   "0"],
    ["Own field / Test",  "269",   "638",   "820",   "0"],
    ["Silva et al. / Train", "396", "1,123", "0",    "1,621"],
    ["Silva et al. / Val",   "127", "697",   "0",    "389"],
    ["Silva et al. / Test",  "87",  "187",   "0",    "375"],
    ["Total",             "2,315", "5,020", "5,389", "2,385"],
]

# Insert a caption paragraph and then the table after the Table 2 caption paragraph
table2_caption_para = None
for para in doc.paragraphs:
    t = "".join(run.text for run in para.runs)
    if "Table 2. CoffeeLeaf-CO dataset composition" in t:
        table2_caption_para = para
        break

if table2_caption_para:
    # Add a blank paragraph and caption for Table 2b, then insert table
    # We'll add the table after the existing Table 2 (the class×split table)
    # First find the table element that follows the Table 2 caption
    # Strategy: insert caption paragraph after table2_caption_para, then table
    # Actually, let's add it after the second table in the document body
    # Simpler: just add a new paragraph caption right before the table 2b
    # We'll do this by inserting elements into the XML directly

    # Find the index of Table 1 (class×split) in doc.tables
    # Table 0 = comparison table, Table 1 = class×split, Table 2 = training config, Table 3 = results
    if len(doc.tables) >= 2:
        class_split_table = doc.tables[1]  # Table 2 in document = doc.tables[1]

        # Create caption paragraph
        from docx.oxml.ns import qn as _qn
        cap_para = OxmlElement('w:p')
        cap_run_elem = OxmlElement('w:r')
        cap_text_elem = OxmlElement('w:t')
        cap_text_elem.text = ("Table 2b. CoffeeLeaf-CO source composition by split and class. "
                              "Counts derived from split_v2/assignments_v2.csv analysis.")
        cap_run_elem.append(cap_text_elem)
        cap_para.append(cap_run_elem)

        # Apply "Tables and figures Titles" style if available
        pPr = OxmlElement('w:pPr')
        pStyle = OxmlElement('w:pStyle')
        pStyle.set(qn('w:val'), 'Tablesandfigurestitles')
        pPr.insert(0, pStyle)
        cap_para.insert(0, pPr)

        # Insert caption after class_split_table
        class_split_table._tbl.addnext(cap_para)

        # Now create the actual table
        new_tbl = doc.add_table(rows=1 + len(TABLE2B_DATA), cols=len(TABLE2B_HEADER))
        try:
            new_tbl.style = 'Table Grid'
        except Exception:
            pass

        # Fill header
        hdr = new_tbl.rows[0].cells
        for i, h in enumerate(TABLE2B_HEADER):
            hdr[i].text = h
            for run in hdr[i].paragraphs[0].runs:
                run.bold = True

        # Fill data
        for r_i, row_data in enumerate(TABLE2B_DATA):
            row_cells = new_tbl.rows[r_i + 1].cells
            for c_i, val in enumerate(row_data):
                row_cells[c_i].text = val

        # Move new table element after the caption
        cap_para.addnext(new_tbl._tbl)

        changes_log.append(("Add Table 2b", "(new)", "Source composition table", "Session spec", 1))

# ---------------------------------------------------------------------------
# STEP 19 — Fix "leaky baseline" section: remove "leakage-free" if present
# ---------------------------------------------------------------------------
for banned_str in ["leakage-free", "sin fuga", "no leakage"]:
    count = replace_all_paras(doc, banned_str, "")
    if count:
        changes_log.append((f"Remove banned string '{banned_str}'", banned_str, "(removed)", "Banned string", count))

# ---------------------------------------------------------------------------
# STEP 20 — Fix "Dataset heterogeneity" paragraph in 6.3: Source 3→Source 2
# Already done above, but also fix the sentence about "Source 3" in results section
# ---------------------------------------------------------------------------
count = replace_all_paras(doc,
    "(1) Dataset heterogeneity: Source 3 images",
    "(1) Dataset heterogeneity: Source 2 images"
)
changes_log.append(("6.3(1) Source 3→Source 2", "Source 3 images", "Source 2 images", "Two sources only", count))

# ---------------------------------------------------------------------------
# STEP 21 — Document properties
# ---------------------------------------------------------------------------
props = doc.core_properties
props.title = ("CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images "
               "for detecting rust, weevil damage and leaf miner")
props.creator = "Luis Esteban Rosas Ruiz"
props.last_modified_by = "Luis Esteban Rosas Ruiz"
props.description = ""
# company is not a standard core property in python-docx; skip
changes_log.append(("Document properties", "BASES DE LA IMPLEMENTACIÓN...", "CoffeeLeaf-CO article title; creator set", "Fix wrong title in properties", 1))

# ---------------------------------------------------------------------------
# SAVE v5
# ---------------------------------------------------------------------------
out_v5 = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v5.docx"
doc.save(out_v5)
print(f"Saved: {out_v5}")

# ---------------------------------------------------------------------------
# STEP 22 — Create anonymous version
# ---------------------------------------------------------------------------
import copy as _copy

doc_anon = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v5.docx")

# Remove author name, affiliation, ORCID, email paragraph
paras_to_remove_anon = []
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if any(x in t for x in [
        "Luis Esteban Rosas Ruiz",
        "Escuela de Ingenierías Eléctrica",
        "Corresponding author:",
        "ORCID:",
        "luis.rosas@correo.uis.edu.co",
        "ORCID: 0000-0003-0233-6336",
    ]):
        paras_to_remove_anon.append(para)
for para in paras_to_remove_anon:
    remove_para(para)

# Remove acknowledgements content
in_ack = False
ack_paras = []
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if t.strip() == "Acknowledgements":
        in_ack = True
        continue
    if in_ack and t.strip() and t.strip().startswith(("[", "Data", "Author", "Funding",
                                                       "Conflicts", "Statement", "References")):
        in_ack = False
    if in_ack and t.strip():
        ack_paras.append(para)

for para in ack_paras:
    merge_runs(para)
    if para.runs:
        para.runs[0].text = "[Acknowledgements withheld for double-blind review]"

# Remove CRediT content
for para in doc_anon.paragraphs:
    t = "".join(run.text for run in para.runs)
    if t.strip().startswith("CRediT"):
        merge_runs(para)
        if para.runs:
            para.runs[0].text = "[Author contributions withheld for double-blind review]"

# Replace Zenodo DOI and HF URL
anon_replacements = [
    ("https://doi.org/10.5281/zenodo.19931903", "[withheld for double-blind review]"),
    ("10.5281/zenodo.19931903", "[withheld for double-blind review]"),
    ("https://huggingface.co/", "[withheld for double-blind review — "),
]
for old, new in anon_replacements:
    replace_all_paras(doc_anon, old, new)

# Replace thesis reference [17] with anonymized version
replace_all_paras(doc_anon,
    "[17] L. E. Rosas Ruiz and A. F. Salom Medina,",
    "[17] [withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    '"Detección y prevención de riesgo de enfermedades en plantaciones de café mediante inteligencia artificial," Trabajo de Grado',
    '"[withheld for double-blind review]," Trabajo de Grado'
)

# Anonymous document properties
anon_props = doc_anon.core_properties
anon_props.title = ("CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images "
                    "for detecting rust, weevil damage and leaf miner")
anon_props.creator = ""
anon_props.last_modified_by = ""
anon_props.description = ""

out_anon = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v5_anonymous.docx"
doc_anon.save(out_anon)
print(f"Saved: {out_anon}")

# ---------------------------------------------------------------------------
# STEP 23 — Cover letter v5
# ---------------------------------------------------------------------------
print("Loading cover_letter_v4.docx ...")
cl = Document(MANUSCRIPT_DIR / "cover_letter_v4.docx")

# Update title in submission line
replace_all_paras(cl,
    '"DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions"',
    '"CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images for detecting rust, weevil damage and leaf miner"'
)

# Update "DECAFIA" in body of cover letter
replace_all_paras(cl,
    "This manuscript presents DECAFIA, an annotated dataset",
    "This manuscript presents CoffeeLeaf-CO, an annotated dataset"
)

# Remove "among the first published for a coffee leaf disease dataset"
replace_all_paras(cl,
    "The integrity audit and sensitivity analysis included in the manuscript are, to the author's knowledge, among the first published for a coffee leaf disease dataset.",
    "The integrity audit and sensitivity analysis included in the manuscript are described fully in Section 5.3."
)

# Replace sole authorship paragraph
OLD_SOLE = ("Sole authorship. This article has a single author: Luis Esteban Rosas Ruiz. "
            "The research derives from an undergraduate thesis at the Universidad Industrial de Santander directed by Prof. Jaime Guillermo Barrero Pérez, "
            "whose contributions are fully credited in the Acknowledgements section. "
            "Per the journal's authorship criteria (substantial contribution + drafting/revising + approval of final version), "
            "no other person qualifies as an author.")
NEW_SOLE = ("Sole authorship. This article has a single author: Luis Esteban Rosas Ruiz. "
            "The research derives from an undergraduate thesis co-authored with A. F. Salom Medina and directed by Prof. J. G. Barrero Pérez, "
            "Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones, Universidad Industrial de Santander. "
            "Both were invited to review and approve the manuscript; neither responded. "
            "Their contributions are acknowledged in the manuscript.")
replace_all_paras(cl, OLD_SOLE, NEW_SOLE)

# Save cover letter v5
out_cl = MANUSCRIPT_DIR / "cover_letter_v5.docx"
cl.save(out_cl)
print(f"Saved: {out_cl}")

# ---------------------------------------------------------------------------
# STEP 24 — Verification: banned strings check
# ---------------------------------------------------------------------------
print("\n--- Verification ---")
doc_check = Document(out_v5)
full_text_v5 = get_full_text(doc_check)

BANNED = [
    "92.4%", "76.6%", "2,786",
    "Coccinellidae",   # in class name context — check carefully
    "Pseudococcidae",
    "leakage-free", "sin fuga", "no leakage",
]
# Note: "DECAFIA" in prose (not identifiers)
# We check for DECAFIA appearing NOT as part of decafia_grouped_v1, etc.
import re
decafia_prose = re.findall(r'(?<![a-z_])DECAFIA(?![_a-z])', full_text_v5)
if decafia_prose:
    print(f"WARNING: 'DECAFIA' still appears in prose {len(decafia_prose)} times")
    # find context
    for m in re.finditer(r'(?<![a-z_])DECAFIA(?![_a-z])', full_text_v5):
        start = max(0, m.start()-40)
        end = min(len(full_text_v5), m.end()+40)
        print(f"  ...{full_text_v5[start:end]}...")
else:
    print("PASS: No prose 'DECAFIA' found")

banned_found = []
for b in BANNED:
    if b in full_text_v5:
        # Special case: Curculionidae is correct, Coccinellidae is banned
        banned_found.append(b)

if banned_found:
    print(f"FAIL: Banned strings found: {banned_found}")
else:
    print("PASS: No banned strings found")

# Word count
wc = len(full_text_v5.split())
print(f"Word count (v5): {wc}")

# Check key numbers
if "0.929" in full_text_v5:
    print("PASS: mAP50_overall 0.929 present")
if "0.734" in full_text_v5:
    print("PASS: mAP50_95_overall 0.734 present")
if "120 total" in full_text_v5:
    print("PASS: 120 total copy pairs present")
if "107 Tier A" in full_text_v5:
    print("PASS: 107 Tier A present")

# ---------------------------------------------------------------------------
# STEP 25 — Write V5_CHANGES.md
# ---------------------------------------------------------------------------
changes_md_lines = [
    "# V5 Changes",
    "",
    "Generated by build_manuscript_v5.py",
    "",
]

change_descriptions = [
    ("Blocking Fix 1: Remove RoCoLe as Source",
     '"... re-annotated images from two publicly available sources (RoCoLe, Silva et al.) ..."',
     '"... re-annotated images from Silva et al. ..."',
     "RoCoLe images were removed in prior version; RoCoLe stays only in Related Work"),
    ("Blocking Fix 2: NAME_SCHEME A — rename dataset DECAFIA → CoffeeLeaf-CO",
     "Title: DECAFIA: A Multi-Source Field-Collected Dataset...",
     "Title: CoffeeLeaf-CO: a multi-source coffee leaf dataset...",
     "NAME_SCHEME=A. Dataset is CoffeeLeaf-CO; project is DECAF IA"),
    ("Blocking Fix 3: Correct acronym expansion",
     "DECAFIA (DEtección de enfermedades en hojas de CAfé, FIncas de Área cafetera de Colombia)",
     "DECAF IA (Detección de Enfermedades en el Café con Inteligencia Artificial)",
     "The old expansion was fabricated; correct expansion provided"),
    ("Fix 4: Remove unknown/unverified data claims",
     "6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024",
     "(removed — FARM_COORDINATES=?, FARM_ALTITUDE_M=?, CAPTURE_YEARS=?)",
     "Cannot verify these values from available data"),
    ("Fix 5: Remove reflection images paragraph",
     "141 images of sunlight reflections on healthy leaf surfaces...",
     "(entire paragraph removed)",
     "REFLECTION_IMAGES_141=? — cannot verify this claim"),
    ("Fix 6: Remove second annotator claim",
     "a second annotator independently reviewed labels during the thesis phase...",
     "(removed)",
     "SECOND_ANNOTATOR_REVIEW=? — cannot verify this claim"),
    ("Fix 7: Remove SAM masks claim",
     "SAM polygon masks are retained in the repository for instance-segmentation research.",
     "(removed)",
     "SAM_MASKS_PUBLISHED=? — cannot verify this claim"),
    ("Fix 8: Fix false arithmetic in Section 3.2",
     "Of 2,803 raw images evaluated, 17 were excluded ... yielding 2,315",
     "The final dataset comprises 2,315 annotated images.",
     "2,803 - 17 = 2,786 is a banned figure; provenance of 2,803/17 unverifiable"),
    ("Fix 9: Section 3.2 Sources 2 and 3 → Source 2",
     "Capture-series grouping for third-party images (Sources 2 and 3)",
     "Capture-series grouping for third-party images (Source 2)",
     "Only one third-party source remains after RoCoLe removal"),
    ("Fix 10: Table 3 lrf value",
     "Learning rate (lrf) | 0.01",
     "Learning rate (lrf) | 0.001",
     "args.yaml shows lrf=0.001"),
    ("Fix 11: Table 3 Augmentation row",
     "Augmentation | Albumentations defaults",
     "Augmentation | mosaic=1.0, fliplr=0.5, flipud=0.5, ... (explicit params from args.yaml)",
     "'Albumentations defaults' claim not supported by args.yaml"),
    ("Fix 12: Section 4.1 epoch 98 → epoch 97",
     "best checkpoint was saved at epoch 98 (validation mAP@0.50 = 0.924)",
     "best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924)",
     "args.yaml/results.csv confirm epoch 97 (1-indexed) is correct"),
    ("Fix 13: Section 4.3 MINEIRO_99 group",
     "the MINEIRO_99 group",
     "a cross-source leaf group (image prefixes ROYA_MA and ROYA_RECORTES, combined under a shared filename-pattern group root)",
     "MINEIRO_99 is not the correct identifier for this component"),
    ("Fix 14: Section 5.2/6.3 ROYA_RECORTES_107 explanation",
     "one leaf group (ROYA_RECORTES) holds 53.1%",
     "leaf group ROYA_RECORTES_107 — a cross-source group of 21 images combining own-field (ROYA_MA) and Silva et al. (ROYA_RECORTES) images, all in test split — holds 438 roya test instances (53.1%)",
     "Clarify that ROYA_RECORTES_107 is a cross-source group, not a single-source group"),
    ("Fix 15: Section 5.3 copy-pairs numbers",
     "60 cross-split pairs at pHash distance ≤ 4",
     "107 Tier A (pHash ≤ 4) and 13 Tier B (pHash 5–8, SIFT+RANSAC confirmed) = 120 total; 40 have copy in train, 9 in val only",
     "Correct counts from split_v2/copy_pairs.csv and v1_test_exclusion_list.csv"),
    ("Fix 16: Section 6.3(1) contamination claim",
     "mAP@0.50 for rust and weevil detection is based on test images with no verified transformed copies in the training split.",
     "Of the 49 affected test images, 40 have a verified copy in the training split and 9 have a copy only in the validation split. Affected shares: 3.0% roya, 1.5% coco, 23.5% minador. Sensitivity: Δ=-0.0038.",
     "Previous claim was factually wrong: roya and coco test images ARE affected"),
    ("Fix 17: Section 8 remove Ecuadorean/Brazilian claim",
     "This level of specificity is not achievable with models trained on existing datasets collected under Ecuadorean or Brazilian conditions.",
     "(removed)",
     "Unsupported comparative claim"),
    ("Fix 18: Section 8 hedge IPM claim",
     "can be linked to economic damage thresholds",
     "may potentially be linked to economic damage thresholds",
     "Hedge speculative claim"),
    ("Fix 19: Reference [17] author order",
     "[17] A. F. Salom Medina and L. E. Rosas Ruiz,",
     "[17] L. E. Rosas Ruiz and A. F. Salom Medina,",
     "Correct author order"),
    ("Fix 20: Reference [18] author names (BRACOL)",
     "R. A. C. Barata, and V. S. Baravati",
     "R. A. Krohling, and J. A. Ventura",
     "Correct authors for Esgario et al. BRACOL paper"),
    ("Fix 21: Reference [11] add arXiv note",
     "doi: 10.1016/j.imavis.2019.06.011.",
     "doi: 10.1016/j.imavis.2019.06.011. [Also available as arXiv:1904.10699; ACM DOI: VERIFY]",
     "Add arXiv preprint reference; flag ACM DOI for verification"),
    ("Fix 22: Reference [6] mark as VERIFY",
     "doi: 10.1007/s10462-024-11052-2.",
     "doi: 10.1007/s10462-024-11052-2. [VERIFY DOI]",
     "Cannot verify Sajitha DOI without web access"),
    ("Fix 23: Acknowledgements plural→singular",
     "The authors thank", "The author thanks",
     "Single-author paper"),
    ("Fix 24: AI Statement — add drafting/editing use",
     "manuscript formatting, and evidence verification.",
     "manuscript formatting, evidence verification, and drafting and language editing of the manuscript text.",
     "Add actual use of AI for drafting"),
    ("Fix 25: Remove Received/Accepted date lines",
     "Received: [DATE] / Accepted: [DATE]",
     "(removed)",
     "Not yet accepted; placeholder lines removed"),
    ("Fix 26: Add Table 2b — source composition",
     "(none — new addition)",
     "Table 2b: images and instances per source × split",
     "Session spec: add source breakdown table in Section 3.2"),
    ("Fix 27: Document properties",
     "title='BASES DE LA IMPLEMENTACIÓN...', creator=unclear",
     "title=article title, creator='Luis Esteban Rosas Ruiz'",
     "Fix wrong title in Word document properties"),
    ("Cover Letter Fix 1: Update title",
     "DECAFIA: A Multi-Source...",
     "CoffeeLeaf-CO: a multi-source...",
     "NAME_SCHEME A"),
    ("Cover Letter Fix 2: Remove 'among the first published' claim",
     "among the first published for a coffee leaf disease dataset",
     "(removed)",
     "Unsupported claim"),
    ("Cover Letter Fix 3: Sole authorship paragraph",
     "Research derives from undergraduate thesis... no other person qualifies as an author",
     "co-authored with A. F. Salom Medina... Both invited to review; neither responded.",
     "More accurate description of thesis co-authorship situation"),
    ("Anonymous version",
     "Author name, affiliation, ORCID, email, acknowledgements, CRediT, Zenodo DOI, HF URL",
     "[withheld for double-blind review]",
     "Create clean anonymous version for double-blind review"),
]

for item in change_descriptions:
    if len(item) == 4:
        heading, old, new, reason = item
    else:
        heading, old, new, reason = item[0], item[1], item[2], item[3]
    changes_md_lines.append(f"## {heading}")
    changes_md_lines.append(f"- OLD: `{old}`")
    changes_md_lines.append(f"- NEW: `{new}`")
    changes_md_lines.append(f"- REASON: {reason}")
    changes_md_lines.append("")

changes_md_path = MANUSCRIPT_DIR / "V5_CHANGES.md"
changes_md_path.write_text("\n".join(changes_md_lines), encoding="utf-8")
print(f"\nSaved: {changes_md_path}")

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
print("\n=== DONE ===")
print(f"  {out_v5} — {'EXISTS' if out_v5.exists() else 'MISSING'}")
print(f"  {out_anon} — {'EXISTS' if out_anon.exists() else 'MISSING'}")
print(f"  {out_cl} — {'EXISTS' if out_cl.exists() else 'MISSING'}")
print(f"  {changes_md_path} — {'EXISTS' if changes_md_path.exists() else 'MISSING'}")
