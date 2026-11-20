"""
build_manuscript_v7.py

Applies all changes from SESSION_FINAL_V7.md to v6 -> v7:
  PART 1: Embed figures with actual <w:drawing> elements
  PART 2: Fix anonymous version author identification
  PART 3: Add capture years and phone model to Source 1
  PART 4: Fix MINEIRO_99 / 272-image component description
  PART 5: Fix bootstrap cluster description
  PART 6: Table numbering and caption fixes
  PART 7: Text fixes (Section 3.2, Highlights, Abstract, Table 1, 2.2, 6.1, Practical App, etc.)
  PART 8: Reference fixes
  PART 9: Cover letter v7

Run from: C:/Users/luise/temp/decafia-research
"""
import sys
import copy
import re
import shutil
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import lxml.etree as etree

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"
SUBMISSION_DIR = MANUSCRIPT_DIR / "figures_submission"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def merge_runs(para):
    """Merge all runs of a paragraph. NEVER call on image paragraphs."""
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


def find_para_containing(doc, text):
    """Return first paragraph whose full text contains `text`."""
    for para in doc.paragraphs:
        t = "".join(run.text for run in para.runs)
        if text in t:
            return para
    return None


def remove_para(para):
    p = para._element
    p.getparent().remove(p)


def insert_image_before_caption(doc, caption_para, image_path, width_inches=5.5):
    """
    Insert an image paragraph immediately before `caption_para`.
    Uses python-docx add_picture with PIL conversion for TIFF files.
    Returns the image paragraph.
    """
    # Build image paragraph
    img_para = doc.add_paragraph()
    img_para.alignment = 1  # WD_ALIGN_PARAGRAPH.CENTER

    if not image_path.exists():
        img_para.text = f"[Figure: {image_path.name} — file not found]"
        print(f"  WARNING: {image_path} not found")
        # Still insert in correct position
        caption_para._element.addprevious(img_para._element)
        return img_para

    # For TIFF files, convert to PNG via PIL
    actual_path = image_path
    if image_path.suffix.lower() in ('.tif', '.tiff'):
        try:
            from PIL import Image
            png_path = image_path.with_suffix('.png')
            img = Image.open(image_path)
            img.save(png_path, 'PNG')
            actual_path = png_path
            print(f"  Converted {image_path.name} -> {png_path.name}")
        except Exception as e:
            print(f"  PIL conversion failed for {image_path.name}: {e}")
            # Try direct TIFF anyway
            actual_path = image_path

    try:
        run = img_para.add_run()
        run.add_picture(str(actual_path), width=Inches(width_inches))
        print(f"  Embedded {actual_path.name} (width={width_inches}\")")
    except Exception as e:
        img_para.text = f"[Figure: {image_path.name}]"
        print(f"  WARNING: Could not embed {actual_path.name}: {e}")

    # Insert before caption in XML
    caption_para._element.addprevious(img_para._element)
    return img_para


# ---------------------------------------------------------------------------
# STEP 0: Rename TIFFs in figures_submission to final numbering
# ---------------------------------------------------------------------------
print("=" * 60)
print("STEP 0: Rename TIFFs in figures_submission/")
print("=" * 60)

rename_map = {
    "Fig_examples.tif": "Fig. 1.tif",
    "Fig. 5.tif": "Fig. 2.tif",
    "Fig_schematic.tif": "Fig. 3.tif",
    "Fig. 7.tif": "Fig. 4.tif",
    "Fig. 3a.tif": "Fig. 5a.tif",
    "Fig. 3b.tif": "Fig. 5b.tif",
}

for src_name, dst_name in rename_map.items():
    src = SUBMISSION_DIR / src_name
    dst = SUBMISSION_DIR / dst_name
    if src.exists():
        if not dst.exists():
            shutil.copy2(src, dst)
            print(f"  Copied: {src_name} -> {dst_name}")
        else:
            print(f"  Already exists: {dst_name}")
    else:
        print(f"  WARNING: Source not found: {src_name}")

# ---------------------------------------------------------------------------
# Load v6
# ---------------------------------------------------------------------------
print("\nLoading CoffeeLeafCO_manuscript_v6.docx ...")
doc = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v6.docx")

changes_log = []

# ---------------------------------------------------------------------------
# PART 3: Add capture years and phone model to Source 1
# ---------------------------------------------------------------------------
print("\n--- PART 3: Add capture years and phone model ---")

count = replace_all_paras(doc,
    "captured at a Coffea arabica plantation in El Socorro, Santander, Colombia, "
    "using a smartphone camera under uncontrolled natural field lighting.",
    "captured at a Coffea arabica plantation in El Socorro, Santander, Colombia, "
    "in 2022\u20132023 using a Xiaomi Poco X3 Pro smartphone under uncontrolled natural field lighting."
)
changes_log.append(("Source 1 - add capture years and phone model", count))
print(f"  Source 1 phone/year: {count}")

# ---------------------------------------------------------------------------
# PART 4: Fix MINEIRO_99 / 272-image component description
# ---------------------------------------------------------------------------
print("\n--- PART 4: Fix MINEIRO_99 component description ---")

# Section 4.3 — fix the 272-image component description
old_4_3 = (
    "The largest verified component (272 images) comprises a cross-source leaf group "
    "(image prefixes ROYA_MA and ROYA_RECORTES, combined under a shared filename-pattern group root) "
    "of laboratory leaf-miner images (Source 2) with SIFT-verified geometric copies across split boundaries. "
    "This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split "
    "while maintaining all three classes in the test set (Section 5.3). "
    "The full audit pipeline is illustrated in Fig. 3."
)
new_4_3 = (
    "The largest verified component (272 images, the MINEIRO_99 component) comprises laboratory "
    "leaf-miner images from Silva et al. (prefixes MINEIRO, MINADO_RECORTES, and MINADOR), along with "
    "associated ROYA_FONDO images, connected by SIFT-verified geometric copies across split boundaries. "
    "This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split "
    "while maintaining all three classes in the test set (Section 5.3). "
    "The full audit pipeline is illustrated in Fig. 3."
)
count = replace_all_paras(doc, old_4_3, new_4_3)
if count == 0:
    # Try partial match
    old_partial = (
        "The largest verified component (272 images) comprises a cross-source leaf group "
        "(image prefixes ROYA_MA and ROYA_RECORTES"
    )
    new_partial = (
        "The largest verified component (272 images, the MINEIRO_99 component) comprises laboratory "
        "leaf-miner images from Silva et al. (prefixes MINEIRO, MINADO_RECORTES, and MINADOR), along with "
        "associated ROYA_FONDO images, connected by SIFT-verified geometric copies across split boundaries. "
        "This component was identified post-hoc; its size (12% of the dataset) prevents restructuring the split "
        "while maintaining all three classes in the test set (Section 5.3). "
        "The full audit pipeline is illustrated in Fig. 3."
    )
    # Find the para and replace entirely
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "largest verified component (272 images)" in t:
            para.runs[0].text = new_4_3
            count = 1
            break
changes_log.append(("PART 4 - MINEIRO_99 Section 4.3", count))
print(f"  Section 4.3 MINEIRO_99: {count}")

# Limitation (1) in Section 6.3 — update MINEIRO_99 reference
old_lim1 = (
    "(1) Dataset heterogeneity: Source 2 images (laboratory, white background) introduce a distribution "
    "shift relative to Colombian field images. The largest verified transformed-copy component (272 images) "
    "comprises these laboratory images. All minador test images belong to this component; therefore, "
    "minador test performance (mAP@0.50 = 0.985) cannot be interpreted as performance on independent held-out leaves. "
    "Of the 49 affected test images, 40 have a verified copy in the training split and 9 have a copy only "
    "in the validation split (Section 5.3). The affected shares are: 3.0% of roya test instances, "
    "1.5% of coco test instances, and 23.5% of minador test instances originate from these 49 images. "
    "The sensitivity analysis (mAP@0.50 drops 0.0038 when excluding all 49) suggests the contamination "
    "has a small aggregate effect, but the minador class is disproportionately affected."
)
new_lim1 = (
    "(1) Dataset heterogeneity: Source 2 images (laboratory, white background) introduce a distribution "
    "shift relative to Colombian field images. The largest verified transformed-copy component (272 images, "
    "MINEIRO_99) is primarily laboratory leaf-miner images from Silva et al. (prefixes MINEIRO, "
    "MINADO_RECORTES, MINADOR). All minador test images belong to this component; therefore, "
    "minador test performance (mAP@0.50 = 0.985) cannot be interpreted as performance on independent held-out leaves. "
    "Of the 49 affected test images, 40 have a verified copy in the training split and 9 have a copy only "
    "in the validation split (Section 5.3). The affected shares are: 3.0% of roya test instances, "
    "1.5% of coco test instances, and 23.5% of minador test instances originate from these 49 images. "
    "The sensitivity analysis (mAP@0.50 drops 0.0038 when excluding all 49) suggests the contamination "
    "has a small aggregate effect, but the minador class is disproportionately affected."
)
count = replace_all_paras(doc, old_lim1, new_lim1)
if count == 0:
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "(1) Dataset heterogeneity" in t and "ROYA_MA and ROYA_RECORTES" in t:
            para.runs[0].text = new_lim1
            count = 1
            break
        elif "(1) Dataset heterogeneity" in t and "largest verified transformed-copy component" in t:
            # Replace the description part
            new_t = t.replace(
                "The largest verified transformed-copy component (272 images) comprises these laboratory images.",
                "The largest verified transformed-copy component (272 images, MINEIRO_99) is primarily laboratory leaf-miner images from Silva et al. (prefixes MINEIRO, MINADO_RECORTES, MINADOR)."
            )
            if new_t != t:
                para.runs[0].text = new_t
                count = 1
                break
changes_log.append(("PART 4 - Limitation 1 MINEIRO_99", count))
print(f"  Limitation 1 MINEIRO_99: {count}")

# ---------------------------------------------------------------------------
# PART 5: Fix bootstrap cluster description
# ---------------------------------------------------------------------------
print("\n--- PART 5: Fix bootstrap cluster description ---")

# Section 4.4: Replace cluster definition
old_44 = (
    "Bootstrap confidence intervals (95%, B = 2,000, seed = 42) are reported where valid. "
    "Clusters are defined as v1 leaf groups (group_root from assignments). "
    "A per-class cluster bootstrap validity check was applied: if a single cluster holds more than 50% "
    "of that class's test instances, the cluster bootstrap cannot estimate a meaningful interval for that class. "
    "Roya: 10 clusters, largest holds 53.1% of test instances \u2014 cluster CI not reportable. "
    "Coco: 6 clusters, largest holds 37.2% \u2014 reportable. "
    "Minador: cluster CI computed but not reported in the manuscript (Section 5.3). "
    "Image-level bootstrap CIs are reported as secondary (they ignore within-leaf correlation)."
)
new_44 = (
    "Bootstrap confidence intervals (95%, B = 2,000, seed = 42) are reported where valid. "
    "Clusters are defined as (group_root, source) pairs \u2014 groups of filename-related images within "
    "the same source dataset \u2014 to prevent spurious connections from filename-number grouping across sources. "
    "A per-class cluster bootstrap validity check was applied: if a single cluster holds more than 50% "
    "of that class's test instances, the cluster bootstrap cannot estimate a meaningful interval for that class. "
    "Roya: 11 clusters, largest holds 52.6% of test instances \u2014 cluster CI not reportable. "
    "Coco: 6 clusters, largest holds 37.2% \u2014 reportable. "
    "Minador: 4 clusters, largest holds 43.7% of test instances \u2014 CI computed but not reported, "
    "as minador test images are not independent of training (Section 6.3). "
    "Image-level bootstrap CIs are reported as secondary (they ignore within-leaf correlation)."
)
count = replace_all_paras(doc, old_44, new_44)
if count == 0:
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "Bootstrap confidence intervals" in t and "Clusters are defined as v1 leaf groups" in t:
            para.runs[0].text = new_44
            count = 1
            break
changes_log.append(("PART 5 - Section 4.4 cluster def", count))
print(f"  Section 4.4 cluster definition: {count}")

# Section 5.2: Update roya cluster explanation
old_52_roya = (
    "A cluster confidence interval cannot be reported because the leaf group ROYA_RECORTES_107 "
    "\u2014 a cross-source group of 21 images combining own-field images (prefix ROYA_MA) and "
    "Silva et al. images (prefix ROYA_RECORTES), all assigned to the test split \u2014 holds 438 "
    "roya test instances (53.1%), exceeding the 50% single-cluster threshold. "
    "Image-level CI (secondary; ignores within-leaf correlation): [0.803, 0.874]."
)
new_52_roya = (
    "A cluster CI cannot be reported because the cluster (ROYA_RECORTES_107, own_field) "
    "\u2014 20 own-field images (prefix ROYA_MA) grouped with one Silva et al. image by "
    "filename-number proximity \u2014 holds 434 roya test instances (52.6%), exceeding the 50% "
    "single-cluster threshold. These groups are filename-number artifacts, not verified crop-parent links. "
    "Image-level CI (secondary; ignores within-leaf correlation): [0.803, 0.874]."
)
count = replace_all_paras(doc, old_52_roya, new_52_roya)
if count == 0:
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "ROYA_RECORTES_107" in t and "cross-source group" in t and "438" in t:
            new_t = t.replace(
                "A cluster confidence interval cannot be reported because the leaf group ROYA_RECORTES_107 "
                "\u2014 a cross-source group of 21 images combining own-field images (prefix ROYA_MA) and "
                "Silva et al. images (prefix ROYA_RECORTES), all assigned to the test split \u2014 holds 438 "
                "roya test instances (53.1%), exceeding the 50% single-cluster threshold. "
                "Image-level CI (secondary; ignores within-leaf correlation): [0.803, 0.874].",
                new_52_roya
            )
            if new_t != t:
                para.runs[0].text = new_t
                count = 1
                break
changes_log.append(("PART 5 - Section 5.2 roya cluster", count))
print(f"  Section 5.2 roya cluster: {count}")

# Check/add coco caveat in 5.2
coco_caveat = "Note: with only 6 clusters, this bootstrap CI may be unreliable; the image-level CI [0.951, 0.974] is provided as secondary."
full_text_check = get_full_text(doc)
if coco_caveat not in full_text_check:
    # Find the coco CI sentence and append the caveat
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "Coco achieves mAP@0.50 = 0.962" in t and "95% cluster CI [0.801, 0.971]" in t:
            if coco_caveat not in t:
                # Append caveat after the existing sentence about coco
                # Find where to insert it
                idx = t.find("95% cluster CI [0.801, 0.971], B = 2,000, leaf groups as clusters).")
                if idx >= 0:
                    end = idx + len("95% cluster CI [0.801, 0.971], B = 2,000, leaf groups as clusters).")
                    para.runs[0].text = t[:end] + " " + coco_caveat + t[end:]
                    count = 1
                else:
                    # Append at a good place
                    idx2 = t.find("Roya achieves mAP@0.50 = 0.841.")
                    if idx2 >= 0:
                        para.runs[0].text = t[:idx2] + coco_caveat + " " + t[idx2:]
                        count = 1
                break
    changes_log.append(("PART 5 - coco caveat", count if count else 0))
    print(f"  Coco caveat added: {count if count else 0}")
else:
    print("  Coco caveat already present")

# Fix Limitation (4) - roya cluster structure to match new numbers
old_lim4 = (
    "(4) Roya cluster structure: The leaf group ROYA_RECORTES_107 (21 images; a cross-source group "
    "combining own-field ROYA_MA images and Silva et al. ROYA_RECORTES images, all in the test split) "
    "holds 438 instances (53.1% of test-set roya instances), preventing a meaningful cluster bootstrap "
    "interval for that class."
)
new_lim4 = (
    "(4) Roya cluster structure: The cluster (ROYA_RECORTES_107, own_field) holds 434 instances "
    "(52.6% of test-set roya instances), preventing a cluster bootstrap interval for that class. "
    "This group links 20 own-field images (prefix ROYA_MA) with one Silva et al. image (prefix ROYA_RECORTES) "
    "by filename-number proximity, not by verified crop-parent links."
)
count = replace_all_paras(doc, old_lim4, new_lim4)
if count == 0:
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "(4) Roya cluster structure" in t and "438" in t:
            para.runs[0].text = new_lim4
            count = 1
            break
changes_log.append(("PART 5 - Limitation 4", count))
print(f"  Limitation 4: {count}")

# ---------------------------------------------------------------------------
# PART 6: Table numbering and caption fixes
# ---------------------------------------------------------------------------
print("\n--- PART 6: Table numbering ---")

# Fix Table 2b (source x split) which appears BEFORE Table 2 (class x split)
# In v6: para 38 is "Table 2b..." then para 39 is "Table 2..."
# We need to: (1) rename Table 2b -> Table 3, (2) rename Table 2 -> Table 2 (keep)
# (3) rename Table 3 -> Table 4, (4) rename Table 4 -> Table 5

# Step A: Temp rename to avoid collisions
count = replace_all_paras(doc,
    "Table 2b. CoffeeLeaf-CO source composition by split and class. Counts derived from split_v2/assignments_v2.csv analysis.",
    "[[TABLE2B_TEMP]]"
)
print(f"  Temp Table2b: {count}")

count = replace_all_paras(doc,
    "Table 2. CoffeeLeaf-CO dataset composition by class and split. Instance counts are bounding-box annotations; background images contain no disease instances. Split is grouped by leaf (grouped_v1).",
    "[[TABLE2_TEMP]]"
)
print(f"  Temp Table2: {count}")

count = replace_all_paras(doc,
    "Table 3. Training configuration for the YOLOv8m baseline (decafia_grouped_v1).",
    "[[TABLE3_TEMP]]"
)
print(f"  Temp Table3: {count}")

for para in doc.paragraphs:
    t = merge_runs(para)
    if t.startswith("Table 4. Baseline") or "Table 4. Baseline" in t:
        para.runs[0].text = "[[TABLE4_TEMP]]"
        count = 1
        break
print(f"  Temp Table4: {count}")

# Check in-text Table references and update them
# "Table 2b" in text -> "Table 3"
count = replace_all_paras(doc, "Table 2b", "[[T2B_INTEXT]]")
print(f"  Temp Table2b in-text: {count}")

# "Table 3" (training config) -> "Table 4" in text
# But first, find in-text references to Table 3 (training config) in running text
# They appear as "Table 3" in content paras
count_t3_text = 0
for para in doc.paragraphs:
    t = "".join(r.text for r in para.runs)
    if para.style.name not in ["Tables and figures Titles", "Normal"] or "Table" not in t:
        if "Table 3" in t:
            replace_in_para(para, "Table 3", "[[T3_INTEXT]]")
            count_t3_text += 1
print(f"  Temp Table3 in-text: {count_t3_text}")

# "Table 4" -> "Table 5" in text
count_t4_text = 0
for para in doc.paragraphs:
    t = "".join(r.text for r in para.runs)
    if "Table 4" in t:
        replace_in_para(para, "Table 4", "[[T4_INTEXT]]")
        count_t4_text += 1
print(f"  Temp Table4 in-text: {count_t4_text}")

# Step B: Replace temps with new captions
count = replace_all_paras(doc, "[[TABLE2_TEMP]]",
    "Table 2. CoffeeLeaf-CO dataset composition by class and split. "
    "Instance counts are bounding-box annotations; background images contain no disease instances. "
    "Split is grouped by leaf (grouped_v1).")
print(f"  Restore Table 2: {count}")

count = replace_all_paras(doc, "[[TABLE2B_TEMP]]",
    "Table 3. CoffeeLeaf-CO source composition by split and class.")
print(f"  Rename Table 2b -> Table 3: {count}")

count = replace_all_paras(doc, "[[TABLE3_TEMP]]",
    "Table 4. Training configuration for the YOLOv8m baseline (decafia_grouped_v1). "
    "Optimizer set explicitly to AdamW in args.yaml (not auto-resolved).")
print(f"  Rename Table 3 -> Table 4: {count}")

# For Table 4 (performance), restore full caption
for para in doc.paragraphs:
    t = merge_runs(para)
    if "[[TABLE4_TEMP]]" in t:
        para.runs[0].text = (
            "Table 5. Baseline performance on the CoffeeLeaf-CO test set "
            "(n = 356 images, NMS IoU = 0.7, eval conf = 0.001). "
            "\u2020Minador test performance cannot be interpreted as performance on "
            "independent held-out leaves (see Section 5.3 and 6.3)."
        )
        count = 1
        break
print(f"  Rename Table 4 -> Table 5: {count}")

# Fix in-text refs
count = replace_all_paras(doc, "[[T2B_INTEXT]]", "Table 3")
print(f"  Restore Table2b in-text -> Table 3: {count}")

count = replace_all_paras(doc, "[[T3_INTEXT]]", "Table 4")
print(f"  Restore Table3 in-text -> Table 4: {count}")

count = replace_all_paras(doc, "[[T4_INTEXT]]", "Table 5")
print(f"  Restore Table4 in-text -> Table 5: {count}")

changes_log.append(("PART 6 - Table renumbering", "done"))

# ---------------------------------------------------------------------------
# PART 7: Text fixes
# ---------------------------------------------------------------------------
print("\n--- PART 7: Text fixes ---")

# 7.1 Section 3.2 - split description
count = replace_all_paras(doc,
    "The split is grouped by leaf: all crops, rotations, and capture-series frames from the same physical leaf "
    "are assigned to the same subset, preventing crop-parent and capture-series pairs from crossing split boundaries.",
    "The split was designed to keep crop\u2013parent pairs and capture series together; a post-hoc audit found "
    "residual transformed copies (Section 5.3)."
)
changes_log.append(("PART 7.1 - Section 3.2 split desc", count))
print(f"  Section 3.2 split desc: {count}")

# 7.2 Highlights
count = replace_all_paras(doc,
    "\u2022 Grouped split prevents same-leaf crops and capture series from crossing boundaries",
    "\u2022 Grouped split keeps crop\u2013parent pairs and capture series of a leaf together"
)
changes_log.append(("PART 7.2 - Highlight 1", count))
print(f"  Highlight 1: {count}")

count = replace_all_paras(doc,
    "\u2022 Post-hoc integrity audit: 49 of 356 test images have training-split copies",
    "\u2022 Audit: 49 of 356 test images have copies in train (40) or val only (9)"
)
changes_log.append(("PART 7.2 - Highlight 2", count))
print(f"  Highlight 2: {count}")

# 7.3 Abstract - fix "in the training split" -> "in the training (40) or validation (9) split"
count = replace_all_paras(doc,
    "excluding these reduces mAP@0.50 by 0.0038 to 0.926",
    "excluding images with copies in the training (40) or validation (9) split reduces mAP@0.50 by 0.0038 to 0.926"
)
changes_log.append(("PART 7.3 - Abstract contamination", count))
print(f"  Abstract contamination: {count}")

# Remove dagger from abstract minador mention
count = replace_all_paras(doc,
    "(rust: 0.841, weevil: 0.962, leaf-miner: 0.985\u2020).",
    "(rust: 0.841, weevil: 0.962, leaf-miner: 0.985)."
)
changes_log.append(("PART 7.3 - Remove dagger from abstract", count))
print(f"  Abstract dagger removal: {count}")

# 7.4 Table 1 - RoCoLe annotation column
# Replace "Classification" with "Classification / Detection" for RoCoLe
for table in doc.tables:
    for row in table.rows:
        cells_text = [c.text for c in row.cells]
        if any("RoCoLe" in ct for ct in cells_text):
            for cell in row.cells:
                for para in cell.paragraphs:
                    if replace_in_para(para, "Classification", "Classification / Detection"):
                        print("  Fixed RoCoLe annotation column")

# Fix BRACOL annotation
for table in doc.tables:
    for row in table.rows:
        cells_text = [c.text for c in row.cells]
        if any("BRACOL" in ct for ct in cells_text):
            for cell in row.cells:
                for para in cell.paragraphs:
                    t = merge_runs(para)
                    if "Classification" in t and "severity" not in t:
                        replace_in_para(para, "Classification", "Classification and severity")
                        print("  Fixed BRACOL annotation column")

# Fix Table 1 caption - add weevil note
count = replace_all_paras(doc,
    "Table 1. Comparison of publicly available coffee leaf disease datasets. No prior dataset includes a weevil (Curculionidae) class.",
    "Table 1. Comparison of publicly available coffee leaf disease datasets. Among the datasets reviewed, none includes a weevil (Curculionidae) class."
)
changes_log.append(("PART 7.4 - Table 1 caption", count))
print(f"  Table 1 caption: {count}")

# 7.4 Section 2.2 and 6.1 novelty
old_22 = (
    "CoffeeLeaf-CO differs from all prior datasets by integrating field images from Colombia with one "
    "external source under a unified annotation protocol, providing instance-level bounding boxes for "
    "three foliar conditions simultaneously."
)
new_22 = (
    "CoffeeLeaf-CO's distinguishing features are: Colombian field images, a weevil (Curculionidae) class "
    "not present in any reviewed dataset, three conditions in one detection dataset, and the grouped split "
    "with an integrity audit."
)
count = replace_all_paras(doc, old_22, new_22)
changes_log.append(("PART 7.4 - Section 2.2 novelty", count))
print(f"  Section 2.2 novelty: {count}")

old_61 = (
    "Its distinguishing characteristics are: Colombian field imagery, multi-class simultaneous detection "
    "(rust + weevil + leaf-miner), instance-level bounding boxes, and an open-access release with full "
    "annotation provenance."
)
new_61 = (
    "Its distinguishing characteristics are: Colombian field imagery, a weevil (Curculionidae) class "
    "(not present in any reviewed dataset), three foliar conditions in one detection dataset, a grouped "
    "split, and an integrity audit with open-access release."
)
count = replace_all_paras(doc, old_61, new_61)
changes_log.append(("PART 7.4 - Section 6.1 novelty", count))
print(f"  Section 6.1 novelty: {count}")

# 7.5 Practical Application (Section 8)
count = replace_all_paras(doc,
    "under the illumination, altitude, and variety conditions of the Colombian Andean coffee belt.",
    "under conditions similar to those encountered in Colombian coffee-growing regions."
)
changes_log.append(("PART 7.5 - Practical App illumination", count))
print(f"  Practical App illumination: {count}")

count = replace_all_paras(doc,
    "to support reproducible research and technology transfer to coffee-growing regions of Colombia and other Andean nations.",
    "to support reproducible research and technology transfer to coffee-growing regions of Colombia."
)
changes_log.append(("PART 7.5 - Practical App Andean nations", count))
print(f"  Practical App Andean nations: {count}")

# 7.6 Section 3.3 annotation
count = replace_all_paras(doc,
    "Class labels were assigned using the Cenicaf\u00e9 phytosanitary identification guide.",
    "Class labels were assigned by the thesis authors using the Cenicaf\u00e9 phytosanitary identification guide [3]."
)
if count == 0:
    count = replace_all_paras(doc,
        "Class labels were assigned using the Cenicaf\u00e9 phytosanitary identification guide",
        "Class labels were assigned by the thesis authors using the Cenicaf\u00e9 phytosanitary identification guide [3]"
    )
changes_log.append(("PART 7.6 - Section 3.3 annotators", count))
print(f"  Section 3.3 annotators: {count}")

# Add "Silva et al. images were re-annotated under the same protocol." after the annotation protocol sentence
for para in doc.paragraphs:
    t = merge_runs(para)
    if "Class labels were assigned by the thesis authors using the Cenicaf\u00e9 phytosanitary identification guide [3]." in t:
        if "Silva et al. images were re-annotated" not in t:
            end_sent = t.find("Class labels were assigned by the thesis authors using the Cenicaf\u00e9 phytosanitary identification guide [3].")
            end_sent += len("Class labels were assigned by the thesis authors using the Cenicaf\u00e9 phytosanitary identification guide [3].")
            para.runs[0].text = t[:end_sent] + " Silva et al. images were re-annotated under the same protocol." + t[end_sent:]
            print("  Added Silva re-annotation note")
        break

# 7.7 Section 6.2 - remove sentence
count = replace_all_paras(doc,
    " This gap is consistent with other agricultural detection benchmarks [4, 7].",
    ""
)
if count == 0:
    count = replace_all_paras(doc,
        "This gap is consistent with other agricultural detection benchmarks [4, 7].",
        ""
    )
changes_log.append(("PART 7.7 - Remove [4,7] sentence", count))
print(f"  Remove [4,7] sentence: {count}")

# 7.9 Section 5.1 - remove exact value parenthetical
count = replace_all_paras(doc,
    "Background false alarm rate = 0.019 (3 of 158 background images triggered at least one detection "
    "at conf = 0.50, iou = 0.7; exact value 0.018987).",
    "Background false alarm rate = 0.019 (3 of 158 background images triggered at least one detection "
    "at conf = 0.50, iou = 0.7)."
)
if count == 0:
    count = replace_all_paras(doc, "(exact value 0.018987)", "")
    count += replace_all_paras(doc, "; exact value 0.018987", "")
changes_log.append(("PART 7.9 - Remove exact value", count))
print(f"  Remove exact value: {count}")

# 7.10 Add in-text Table citations for Tables 2, 3, 4
count = replace_all_paras(doc,
    "Images are split into train (1,577), validation (382), and test (356) subsets by leaf group.",
    "Images are split into train (1,577), validation (382), and test (356) subsets by leaf group (Table 2)."
)
changes_log.append(("PART 7.10 - Table 2 in-text", count))
print(f"  Table 2 in-text ref: {count}")

count = replace_all_paras(doc,
    "Example annotated images from both sources are shown in Fig. 1.",
    "Example annotated images from both sources are shown in Fig. 1. Source composition by split is given in Table 3."
)
changes_log.append(("PART 7.10 - Table 3 in-text", count))
print(f"  Table 3 in-text ref: {count}")

count = replace_all_paras(doc,
    "The best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924; training curves in Fig. 2).",
    "The best checkpoint was saved at epoch 97 (1-indexed; validation mAP@0.50 = 0.924; training curves in Fig. 2). Training hyperparameters are listed in Table 4."
)
changes_log.append(("PART 7.10 - Table 4 in-text", count))
print(f"  Table 4 in-text ref: {count}")

# 7.11 Practical Application - expand to 150+ words
count = replace_all_paras(doc,
    "to support reproducible research and technology transfer to coffee-growing regions of Colombia.",
    "to support reproducible research, facilitate replication by other groups, and enable technology transfer to coffee-growing regions of Colombia."
)
changes_log.append(("PART 7.11 - Practical App expand", count))
print(f"  Practical App expand: {count}")

# ---------------------------------------------------------------------------
# PART 8: Reference fixes
# ---------------------------------------------------------------------------
print("\n--- PART 8: Reference fixes ---")

# [2] Avelino - add full title
count = replace_all_paras(doc,
    '"The coffee rust crises in Colombia and Central America (2008\u20132013),"',
    '"The coffee rust crises in Colombia and Central America (2008\u20132013): impacts, plausible causes and proposed solutions,"'
)
changes_log.append(("PART 8 - [2] Avelino full title", count))
print(f"  [2] full title: {count}")

# [9] RoCoLe - full title
count = replace_all_paras(doc,
    '"RoCoLe: A robusta coffee leaf images dataset,"',
    '"RoCoLe: A robusta coffee leaf images dataset for evaluation of machine learning based methods in plant diseases recognition,"'
)
changes_log.append(("PART 8 - [9] RoCoLe full title", count))
print(f"  [9] full title: {count}")

# [10] Silva - exact Mendeley title
count = replace_all_paras(doc,
    '"Rust and leaf miner in coffee crop (Coffea arabica),"',
    '"Rust (Hemileia vastatrix) and leaf miner (Leucoptera coffeella) in coffee crop (Coffea arabica),"'
)
changes_log.append(("PART 8 - [10] Silva full title", count))
print(f"  [10] full title: {count}")

# [13] Jocher - add access date Nov. 2026
count = replace_all_paras(doc,
    '"Ultralytics YOLO (version 8.4.148)," GitHub, 2023.',
    '"Ultralytics YOLO (version 8.4.148)," GitHub, 2023. [Accessed: Nov. 2026].'
)
if count == 0:
    # Try partial
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "[13]" in t and "Jocher" in t and "Ultralytics" in t:
            if "[Accessed" not in t:
                new_t = t.replace(
                    "GitHub, 2023. [Online].",
                    "GitHub, 2023. [Online]. [Accessed: Nov. 2026]."
                )
                if new_t == t:
                    # Try another format
                    new_t = t.rstrip()
                    if not new_t.endswith("[Accessed: Nov. 2026]."):
                        new_t = new_t + " [Accessed: Nov. 2026]."
                        para.runs[0].text = new_t
                        count = 1
                        break
                else:
                    para.runs[0].text = new_t
                    count = 1
                    break
changes_log.append(("PART 8 - [13] access date", count))
print(f"  [13] access date: {count}")

# [1] FNC - update URL with full download URL
count = replace_all_paras(doc,
    "[1] Federaci\u00f3n Nacional de Cafeteros de Colombia, \"Informe de Gesti\u00f3n 2024,\" FNC, Bogot\u00e1, Colombia, 2024. [Online]. Available: https://federaciondecafeteros.org. [Accessed: Nov. 2026].",
    "[1] Federaci\u00f3n Nacional de Cafeteros de Colombia, \"Informe de Gesti\u00f3n 2024,\" FNC, Bogot\u00e1, Colombia, 2024. [Online]. Available: https://publicaciones.cenicafe.org/index.php/inf-fnc/article/download/4214/4360/3497. [Accessed: Nov. 2026]."
)
if count == 0:
    for para in doc.paragraphs:
        t = merge_runs(para)
        if "[1]" in t and "Informe de Gesti\u00f3n 2024" in t and "federaciondecafeteros.org" in t:
            para.runs[0].text = t.replace(
                "https://federaciondecafeteros.org",
                "https://publicaciones.cenicafe.org/index.php/inf-fnc/article/download/4214/4360/3497"
            )
            count = 1
            break
changes_log.append(("PART 8 - [1] FNC URL", count))
print(f"  [1] FNC URL: {count}")

# ---------------------------------------------------------------------------
# PART 6b: Reorder Table 2 (class x split) BEFORE Table 3 (source x split)
# This is an XML-level operation done BEFORE figure embedding
# ---------------------------------------------------------------------------
print("\n--- PART 6b: Reorder Table 2 before Table 3 ---")

body = doc.element.body
elements = list(body)

t2_cap_idx = t2_tbl_idx = t3_cap_idx = t3_tbl_idx = None
for i, elem in enumerate(elements):
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    if tag == 'p':
        text = ''.join(n.text or '' for n in elem.iter() if n.tag.endswith('}t'))
        if text.startswith('Table 3. CoffeeLeaf-CO source composition'):
            t3_cap_idx = i
        elif text.startswith('Table 2. CoffeeLeaf-CO dataset composition'):
            t2_cap_idx = i
    elif tag == 'tbl':
        # Check NEXT element to identify table (caption comes after table in this doc)
        if i + 1 < len(elements):
            next_text = ''.join(n.text or '' for n in elements[i+1].iter() if n.tag.endswith('}t'))
            if next_text.startswith('Table 3.'):
                t3_tbl_idx = i
            elif next_text.startswith('Table 2.'):
                t2_tbl_idx = i

print(f"  T3: cap={t3_cap_idx}, tbl={t3_tbl_idx}")
print(f"  T2: cap={t2_cap_idx}, tbl={t2_tbl_idx}")

if all(x is not None for x in [t2_cap_idx, t2_tbl_idx, t3_cap_idx, t3_tbl_idx]):
    t3_cap = elements[t3_cap_idx]
    t3_tbl = elements[t3_tbl_idx]
    t2_cap = elements[t2_cap_idx]
    t2_tbl = elements[t2_tbl_idx]
    # Current: T3_TBL T3_CAP T2_TBL T2_CAP (Table 3 before Table 2)
    # Want: T2_TBL T2_CAP T3_TBL T3_CAP (Table 2 before Table 3)
    # Move T2_TBL and T2_CAP before T3_TBL
    t3_tbl.addprevious(t2_tbl)
    t2_tbl.addnext(t2_cap)
    print("  Reordered: Table 2 (class x split) now before Table 3 (source x split)")
else:
    print(f"  WARNING: T2_tbl={t2_tbl_idx}, T2_cap={t2_cap_idx}, T3_tbl={t3_tbl_idx}, T3_cap={t3_cap_idx}")

# ---------------------------------------------------------------------------
# PART 2: Anonymous version (text changes only, NO figure embedding yet)
# ---------------------------------------------------------------------------
print("\n--- PART 2: Build anonymous v7 (text changes) ---")

# Save named doc to temp (without figures), then load for anon
out_v7_temp = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7_named_nofig.docx"
doc.save(out_v7_temp)
doc_anon = Document(out_v7_temp)

# Fix [16] reference - replace entire entry
for para in doc_anon.paragraphs:
    t = merge_runs(para)
    if t.startswith("[16]") and ("Rosas Ruiz" in t or "Detecci\u00f3n" in t or "Trabajo de Grado" in t):
        para.runs[0].text = "[16] [Reference withheld for double-blind review]"
        print("  [16] reference entry replaced")

# Fix Introduction reference to [16]
count = replace_all_paras(doc_anon,
    "first introduced in the author's undergraduate thesis [16]",
    "a preliminary version of this dataset was introduced in [16]"
)
print(f"  Intro [16] reference: {count}")

# Fix Source 1 location
count = replace_all_paras(doc_anon,
    "El Socorro, Santander, Colombia,",
    "[location withheld], Colombia,"
)
print(f"  Source 1 location: {count}")

# Fix Fig. 1 caption location
count = replace_all_paras(doc_anon,
    "El Socorro, Colombia",
    "[location withheld], Colombia"
)
print(f"  Fig. 1 caption location: {count}")

# Remove author identification paragraphs
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
print(f"  Removed {len(anon_paras_remove)} identifying paragraphs")

# Replace author line
replace_all_paras(doc_anon,
    "Luis Esteban Rosas Ruiz\u00b9",
    "[Author details withheld for double-blind review]"
)
replace_all_paras(doc_anon,
    "\u00b9 Escuela de Ingenier\u00edas El\u00e9ctrica, Electr\u00f3nica y de Telecomunicaciones (E3T), Universidad Industrial de Santander, Bucaramanga, Colombia",
    ""
)

# Anonymize data availability URLs
replace_all_paras(doc_anon, "https://doi.org/10.5281/zenodo.19931903", "[withheld for double-blind review]")
replace_all_paras(doc_anon, "10.5281/zenodo.19931903", "[withheld for double-blind review]")
replace_all_paras(doc_anon, "https://github.com/estebanr25/decafia-research", "[withheld for double-blind review]")
replace_all_paras(doc_anon, "https://noesis.uis.edu.co/handle/20.500.14071/42486", "[withheld for double-blind review]")
replace_all_paras(doc_anon, "[PEGAR DOI ZENODO v2.1.0]", "[withheld for double-blind review]")
replace_all_paras(doc_anon, "[PEGAR URL HUGGING FACE]", "[withheld for double-blind review]")

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
        in_ack = False

# Document properties
anon_props = doc_anon.core_properties
anon_props.title = ("CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images "
                    "for detecting rust, weevil damage and leaf miner")
anon_props.creator = ""
anon_props.last_modified_by = ""
anon_props.description = ""

# Save anon BEFORE figure embedding (figures embedded below)
out_anon_temp = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7_anonymous_nofig.docx"
doc_anon.save(out_anon_temp)
print(f"  Saved anon (pre-figures): {out_anon_temp}")

# ---------------------------------------------------------------------------
# PART 1: Embed figures (named version — MUST be done AFTER all replace_all_paras calls)
# ---------------------------------------------------------------------------
print("\n--- PART 1: Embed figures in named v7 ---")

def embed_figures(target_doc, label=""):
    """Embed all 6 figures in target_doc. Call AFTER all replace_all_paras."""
    fig_files_map = {
        "Fig. 1": SUBMISSION_DIR / "Fig. 1.tif",
        "Fig. 2": SUBMISSION_DIR / "Fig. 2.tif",
        "Fig. 3": SUBMISSION_DIR / "Fig. 3.tif",
        "Fig. 4": SUBMISSION_DIR / "Fig. 4.tif",
        "Fig. 5a": SUBMISSION_DIR / "Fig. 5a.tif",
        "Fig. 5b": SUBMISSION_DIR / "Fig. 5b.tif",
    }
    # Find caption paragraphs
    caps = {}
    for para in target_doc.paragraphs:
        t = "".join(r.text for r in para.runs)
        for fig_id in ["Fig. 1.", "Fig. 2.", "Fig. 3.", "Fig. 4.", "Fig. 5a.", "Fig. 5b."]:
            if t.startswith(fig_id):
                key = fig_id.rstrip(".")
                caps[key] = para
                break
    print(f"  {label}: Found {len(caps)} caption paragraphs: {list(caps.keys())}")

    before = target_doc.element.xml.count('<w:drawing')
    for fig_id, caption_para in caps.items():
        img_path = fig_files_map.get(fig_id)
        if img_path is None:
            print(f"    WARNING: No path for {fig_id}")
            continue
        print(f"    Embedding {fig_id} ...")
        insert_image_before_caption(target_doc, caption_para, img_path, width_inches=5.5)
    after = target_doc.element.xml.count('<w:drawing')
    print(f"  {label}: Drawings: {before} -> {after}")
    return after

n_draw_named = embed_figures(doc, "named")
changes_log.append(("PART 1 - Figures embedded (named)", n_draw_named))

# ---------------------------------------------------------------------------
# Save v7 (named) — AFTER figure embedding
# ---------------------------------------------------------------------------
out_v7 = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7.docx"
doc.save(out_v7)
print(f"\nSaved named v7: {out_v7}")

# ---------------------------------------------------------------------------
# Embed figures in anonymous version
# ---------------------------------------------------------------------------
print("\n--- PART 1b: Embed figures in anon v7 ---")
doc_anon2 = Document(out_anon_temp)
n_draw_anon = embed_figures(doc_anon2, "anon")
changes_log.append(("PART 1 - Figures embedded (anon)", n_draw_anon))

out_anon = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7_anonymous.docx"
doc_anon2.save(out_anon)
print(f"Saved anon v7: {out_anon}")

# Clean up temp files
out_anon_temp.unlink(missing_ok=True)
out_v7_temp.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# PART 9: Cover letter v7
# ---------------------------------------------------------------------------
print("\n--- PART 9: Cover letter v7 ---")

# Cover letter v5 is already correct - check and copy
doc_cl = Document(MANUSCRIPT_DIR / "cover_letter_v5.docx")
cl_full_text = get_full_text(doc_cl)

# Title must match v7
# Title in v5: "CoffeeLeaf-CO: a multi-source coffee leaf dataset with Colombian field images for detecting rust, weevil damage and leaf miner"
# This matches v7 - no change needed

# Check sole authorship paragraph
if "invited to review and approve" in cl_full_text and "did not respond" in cl_full_text:
    print("  Sole authorship paragraph OK")
else:
    print("  WARNING: Sole authorship paragraph may need updating")

# Check for superlatives
superlatives = ["novel", "first", "unique", "pioneering", "groundbreaking", "unprecedented"]
found_sup = [s for s in superlatives if s in cl_full_text.lower()]
if found_sup:
    print(f"  WARNING: Possible superlatives found: {found_sup}")
else:
    print("  No superlatives found in cover letter")

out_cl = MANUSCRIPT_DIR / "cover_letter_v7.docx"
# Save copy
doc_cl.save(out_cl)
print(f"Saved: {out_cl}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== SUMMARY ===")
print(f"Named v7:    {out_v7} ({'EXISTS' if out_v7.exists() else 'MISSING'})")
print(f"Anon v7:     {out_anon} ({'EXISTS' if out_anon.exists() else 'MISSING'})")
print(f"Cover v7:    {out_cl} ({'EXISTS' if out_cl.exists() else 'MISSING'})")
print(f"\nChanges applied:")
for change, count in changes_log:
    print(f"  {change}: {count}")

print("\n=== DONE ===")
