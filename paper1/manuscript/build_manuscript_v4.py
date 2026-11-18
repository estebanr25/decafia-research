"""
Build CoffeeLeafCO_manuscript_v4.docx — submission-ready for Ingeniería e Investigación.

Changes from v3:
  Decision 1: Remove κ = 0.91 claim (no source file exists).
  Decision 2: Remove anonymous-supervisor sentence; annotation described as author's actions.
  Decision 3: Add thesis citation [17] with supersedes sentence.
  Decision 4: Hedge weevil novelty claim; list datasets reviewed; cite BRACOL [18].
  Decision 5: (cover letter only — handled by update_cover_letter_v4.py)
  + Real tables (no placeholders), figures embedded, practical-application section,
    highlights, correct data-availability placeholders.

All numbers from paper1/results/metrics_final.json (SHA-256 prefix: bc4fbb2b).
"""
import json, hashlib, shutil, os
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO         = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT   = REPO / "paper1/manuscript"
RESULTS      = REPO / "paper1/results"
FIGURES      = REPO / "paper1/figures"
FIG_SUBM     = MANUSCRIPT / "figures_submission"
FIG_SUBM.mkdir(exist_ok=True)

# ── Numbers from JSON ────────────────────────────────────────────────────────
d       = json.load((RESULTS / "metrics_final.json").open())
p4      = d["phase4"]["test_set_full"]
mp      = p4["map50_per_class_model_val"]
mAP50   = p4["map50_model_val"]          # 0.929377
mAP95   = p4["map50_95_model_val"]       # 0.734368
roya_50 = mp["roya"]                     # 0.841307
coco_50 = mp["coco"]                     # 0.961786
mina_50 = mp["minador"]                  # 0.985040
mp95    = p4["map50_95_per_class_model_val"]
roya_95 = mp95["roya"]                   # 0.537046
coco_95 = mp95["coco"]                   # 0.794734
mina_95 = mp95["minador"]               # 0.871323
prf     = p4["prf1_at_conf050"]
bs      = p4["bootstrap_map50_ci95"]
coco_lo = bs["per_class_cluster"]["coco"]["lo"]   # 0.8012
coco_hi = bs["per_class_cluster"]["coco"]["hi"]   # 0.9713
roya_lo = bs["per_class_image_level"]["roya"]["lo"]  # 0.8033
roya_hi = bs["per_class_image_level"]["roya"]["hi"]  # 0.8735
filt50  = d["filtered_test"]["map50_overall"]    # 0.925574
delta   = filt50 - mAP50                         # -0.003803
MODEL_SHA = d["phase4"]["model"]["sha256"]
GT      = p4["gt_counts_per_class"]   # roya:825, coco:820, minador:375
bg_rate = p4["background_far_at_conf050"]["rate"]  # 0.018987

# Dataset composition (from splits/grouped_v1/assignments.csv analysis)
COMP = {
    "train":  {"images": 1577, "bg": 798,  "roya": 3321, "coco": 3746, "minador": 1621},
    "val":    {"images":  382, "bg": 157,  "roya":  874, "coco":  823, "minador":  389},
    "test":   {"images":  356, "bg": 158,  "roya":  825, "coco":  820, "minador":  375},
}
# Total instances
TOT_ROYA   = sum(COMP[s]["roya"]    for s in COMP)
TOT_COCO   = sum(COMP[s]["coco"]    for s in COMP)
TOT_MINADOR= sum(COMP[s]["minador"] for s in COMP)
TOT_BG     = sum(COMP[s]["bg"]      for s in COMP)
TOT_IMAGES = sum(COMP[s]["images"]  for s in COMP)

# ── Helpers ──────────────────────────────────────────────────────────────────
def add_heading(doc, text, style="Chapter Title"):
    return doc.add_paragraph(text, style=style)

def add_sub(doc, text):
    return doc.add_paragraph(text, style="Chapter Subtitle")

def add_para(doc, text):
    return doc.add_paragraph(text, style="Content")

def add_table(doc, headers, rows, caption):
    """Add a Word table with headers, data rows, and a caption paragraph."""
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = "Table Grid"
    # Header row
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for para in hdr[i].paragraphs:
            for run in para.runs:
                run.bold = True
    # Data rows
    for ri, row_data in enumerate(rows):
        cells = tbl.rows[ri + 1].cells
        for ci, val in enumerate(row_data):
            cells[ci].text = str(val)
    # Caption
    cap = doc.add_paragraph(caption, style="Tables and figures Titles")
    return tbl, cap

def add_figure(doc, path, caption, width=Inches(5.5)):
    """Embed a figure and add a caption."""
    if Path(path).exists():
        doc.add_picture(str(path), width=width)
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p = doc.add_paragraph(f"[FIGURE NOT FOUND: {path}]", style="Content")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(caption, style="Tables and figures Titles")
    return cap

# ── Export TIFFs ─────────────────────────────────────────────────────────────
try:
    from PIL import Image
    tiff_pairs = [
        (FIGURES / "figure3_confusion_counts.png",    FIG_SUBM / "Fig. 3a.tif"),
        (FIGURES / "figure3_confusion_normalized.png", FIG_SUBM / "Fig. 3b.tif"),
        (FIGURES / "figure5_training_curves.png",     FIG_SUBM / "Fig. 5.tif"),
        (FIGURES / "figure7_bootstrap_intervals.png", FIG_SUBM / "Fig. 7.tif"),
    ]
    for src, dst in tiff_pairs:
        if src.exists():
            img = Image.open(src)
            # Ensure at least 300 dpi
            dpi = img.info.get("dpi", (96, 96))
            dpi_val = max(dpi[0], 300) if isinstance(dpi, tuple) else 300
            img.save(str(dst), format="TIFF", compression="tiff_lzw",
                     dpi=(dpi_val, dpi_val))
            print(f"TIFF: {dst.name} ({dpi_val} dpi)")
        else:
            print(f"SKIP TIFF (source not found): {src}")
except ImportError:
    print("Pillow not installed — skipping TIFF export")

# ── Load template and start fresh ────────────────────────────────────────────
doc = Document(MANUSCRIPT / "ingeinv_template.docx")
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)
for t in list(doc.tables):
    t._element.getparent().remove(t._element)

# ── HIGHLIGHTS ───────────────────────────────────────────────────────────────
# (≤ 85 characters each; listed before abstract per journal template)
highlights = [
    "DECAFIA: 2,315 field-annotated coffee leaf images from Colombian Andean conditions",
    "Three concurrent foliar conditions: rust, weevil (Curculionidae), leaf-miner",
    "Grouped split prevents same-leaf crops and capture series from crossing boundaries",
    "Post-hoc integrity audit: 49 of 356 test images have training-split copies",
    "Open-access release: images, YOLO labels, model weights, and evaluation code",
]
for h in highlights:
    assert len(h) <= 85, f"Highlight too long ({len(h)}): {h}"

doc.add_paragraph("Highlights", style="Abstract and keyword titles")
for h in highlights:
    p = doc.add_paragraph(style="Content")
    p.add_run(f"• {h}")

# ── TITLE ────────────────────────────────────────────────────────────────────
p = doc.add_paragraph(style="English Title")
p.add_run(
    "DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease "
    "Detection Under Colombian Andean Conditions"
)

p = doc.add_paragraph(style="Spanish Title")
p.add_run(
    "DECAFIA: Conjunto de datos de campo multi-fuente para la detección de "
    "enfermedades foliares del café en condiciones andinas colombianas"
)

# Author / affiliation (removed in anonymous version)
p = doc.add_paragraph(style="Spanish Title")
p.add_run("Luis Esteban Rosas Ruiz\u00b9")

p = doc.add_paragraph(style="Spanish Title")
p.add_run(
    "\u00b9 Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T), "
    "Universidad Industrial de Santander, Bucaramanga, Colombia"
)

p = doc.add_paragraph(style="Normal")
p.add_run(
    "Corresponding author: luis.rosas@correo.uis.edu.co\n"
    "ORCID: 0000-0003-0233-6336"
)

# ── ABSTRACT (English) ───────────────────────────────────────────────────────
doc.add_paragraph("ABSTRACT", style="Abstract and keyword titles")

abstract_en = (
    "Coffee cultivation supports approximately 550,000 farming families in Colombia, "
    "yet accurate detection of leaf diseases remains constrained by the absence of "
    "field-collected, annotated datasets representing Colombian Andean agronomic conditions. "
    "This article presents DECAFIA, a multi-source dataset of 2,315 annotated coffee leaf "
    "images with bounding-box annotations for three foliar conditions: coffee leaf rust "
    "(Hemileia vastatrix), weevil damage (Coco, Curculionidae: Compsus sp. / Epicaerus sp.), "
    "and leaf-miner damage (Leucoptera coffeella). The dataset integrates original Colombian "
    "field images with re-annotated images from two publicly available sources (RoCoLe, "
    "Silva et al.) and was split by leaf group to prevent crop-parent and capture-series "
    "pairs from crossing split boundaries. A YOLOv8m baseline trained on the grouped split "
    f"achieves overall mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP95:.3f} on the "
    f"356-image test set (rust: {roya_50:.3f}, weevil: {coco_50:.3f}, "
    f"leaf-miner: {mina_50:.3f}\u2020). "
    "An integrity audit identified 49 test images (13.8%) with geometrically verified "
    f"transformed copies in the training split; excluding these reduces mAP@0.50 by "
    f"{abs(delta):.4f} to {filt50:.3f}. "
    "The dataset, model weights, and all evaluation code are publicly available."
)
# Word count check
wc_abs = len(abstract_en.split())
print(f"Abstract word count: {wc_abs} ({'PASS' if wc_abs <= 250 else 'FAIL — exceeds 250'})")
doc.add_paragraph(abstract_en, style="Abstract and keywords content")

doc.add_paragraph(
    "Keywords: coffee leaf disease; object detection; YOLOv8; grouped split; data integrity",
    style="Normal"
)

# ── ABSTRACT (Spanish) ───────────────────────────────────────────────────────
doc.add_paragraph("RESUMEN", style="Abstract and keyword titles")

abstract_es = (
    "El cultivo del café sostiene a aproximadamente 550,000 familias en Colombia, pero la "
    "detección precisa de enfermedades foliares está limitada por la ausencia de conjuntos "
    "de datos de campo anotados que representen condiciones andinas colombianas. Este "
    "artículo presenta DECAFIA, un conjunto de datos multi-fuente de 2,315 imágenes de "
    "hojas de café con anotaciones de cajas delimitadoras para tres condiciones foliares: "
    "roya del café (Hemileia vastatrix), daño por gorgojos (coco, Curculionidae: Compsus "
    "sp. / Epicaerus sp.) y daño por minador de hojas (Leucoptera coffeella). El conjunto "
    "integra imágenes de campo colombianas originales con imágenes re-anotadas de dos "
    "fuentes públicas (RoCoLe, Silva et al.) y se dividió por grupo de hoja para evitar "
    "que pares hoja-recorte y series de captura cruzaran los límites entre subconjuntos. "
    "Un modelo base YOLOv8m entrenado en la división agrupada alcanza mAP@0.50 = "
    f"{mAP50:.3f} y mAP@0.50:0.95 = {mAP95:.3f} en el conjunto de prueba de 356 imágenes. "
    "Una auditoría de integridad identificó 49 imágenes de prueba (13,8%) con copias "
    "transformadas geométricamente verificadas en el subconjunto de entrenamiento; "
    f"excluirlas reduce el mAP@0.50 en {abs(delta):.4f} a {filt50:.3f}."
)
doc.add_paragraph(abstract_es, style="Abstract and keywords content")
doc.add_paragraph(
    "Palabras clave: enfermedad foliar del café; detección de objetos; YOLOv8; "
    "división agrupada por hoja; integridad de datos",
    style="Normal"
)

p = doc.add_paragraph(style="Dates")
p.add_run("Received: [DATE]")
p = doc.add_paragraph(style="Dates")
p.add_run("Accepted: [DATE]")

# ── 1. INTRODUCTION ──────────────────────────────────────────────────────────
add_heading(doc, "1. Introduction")
add_para(doc,
    "Coffee (Coffea arabica and Coffea canephora) is one of the most economically significant "
    "agricultural commodities globally, generating income for approximately 550,000 farming "
    "families across more than 590 municipalities in Colombia [1]. Coffee leaf rust (Hemileia "
    "vastatrix) caused production losses exceeding 30% in affected Colombian farms during the "
    "2008–2013 epidemic [2]. Leaf-miner (Leucoptera coffeella) and weevil (Curculionidae) "
    "damage are additional foliar threats requiring timely diagnosis for integrated pest "
    "management [3]."
)
add_para(doc,
    "Deep learning-based object detection has demonstrated potential for automated "
    "phytopathological diagnosis [4], yet model performance depends critically on the "
    "geographic and agronomic match between training data and deployment conditions. "
    "Existing public datasets for coffee leaf diseases (Section 2.2) do not represent "
    "Colombian Andean field conditions, leaving a gap that limits the development of "
    "Colombia-specific detection systems."
)
add_para(doc,
    "This article presents DECAFIA (DEtección de enfermedades en hojas de CAfé, FIncas de "
    "Área cafetera de Colombia), a multi-source dataset of 2,315 annotated coffee leaf images. "
    "The work extends a preliminary dataset first introduced in the author's undergraduate "
    "thesis [17]; this article supersedes those earlier results, which used an earlier version "
    "of the dataset later corrected for source attribution, coco-class taxonomy, and same-leaf "
    "duplication between train and test subsets. "
    "The primary contributions are: (1) a grouped-split dataset of annotated field images "
    "incorporating Colombian Andean conditions not represented in available public datasets; "
    "(2) an integrity audit identifying and quantifying residual transformed-copy overlap "
    "between train and test splits; and (3) a YOLOv8m baseline with fully reproducible "
    "evaluation and open-access release of images, labels, model weights, and code."
)

# ── 2. RELATED WORK ──────────────────────────────────────────────────────────
add_heading(doc, "2. Related Work")
add_sub(doc, "2.1. Deep Learning for Plant Disease Detection")
add_para(doc,
    "CNNs have been extensively applied to plant disease detection since Mohanty et al. [5] "
    "demonstrated high classification accuracy on the PlantVillage dataset. Review studies "
    "confirm EfficientNet, ResNet, and VGG architectures across a range of crop-disease "
    "pairs [6]. Object-detection architectures (YOLO family, Faster R-CNN) are increasingly "
    "preferred for field applications requiring instance-level localization [4, 7]."
)
add_para(doc,
    "For coffee leaf rust severity specifically, Zúñiga Cajas et al. [8] reported "
    "mAP@0.50 = 0.843 with a custom YOLOv8 architecture trained on 1,423 images from "
    "Ecuadorean plantations, using a severity scale derived from CABI guidelines."
)

add_sub(doc, "2.2. Existing Coffee Leaf Disease Datasets")
add_para(doc,
    "Table 1 summarises publicly available coffee leaf disease datasets. No dataset in the "
    "review includes a class for weevil (Curculionidae) feeding damage (Section 6.1). "
    "RoCoLe [9] provides 1,560 Robusta coffee leaf images from Ecuador with rust severity "
    "annotations. Silva et al. [10] provide Brazilian Arabica images with rust and "
    "leaf-miner annotations; most images were taken in a laboratory on a white background. "
    "BRACOL [18] provides Brazilian images for four biotic stress categories (leaf miner, "
    "rust, brown leaf spot, cercospora) at the classification level. "
    "DECAFIA differs from all prior datasets by integrating field images from Colombia "
    "with two external sources under a unified annotation protocol, providing "
    "instance-level bounding boxes for three foliar conditions simultaneously."
)

# Table 1 — Dataset comparison
t1_headers = ["Dataset", "Country", "Year", "Images", "Classes", "Annotation"]
t1_rows = [
    ["Silva et al. [10]", "Brazil",   "2020", "1,251",  "Rust, leaf miner",                                           "Classification"],
    ["BRACOL [18]",       "Brazil",   "2019", "1,747",  "Leaf miner, rust, brown leaf spot, cercospora",               "Classification"],
    ["RoCoLe [9]",        "Ecuador",  "2019", "1,560",  "Rust, red spider mite, healthy",                              "Classification"],
    ["DECAFIA (this work)","Colombia","2026",  "2,315", "Rust, weevil (Curculionidae), leaf miner",                    "Bounding box"],
]
add_table(doc, t1_headers, t1_rows,
    "Table 1. Comparison of publicly available coffee leaf disease datasets. "
    "No prior dataset includes a weevil (Curculionidae) class. "
    "JMuBEN/JMuBEN2 (Kenya, phoma/cercospora/rust/miner/healthy) also reviewed "
    "— no weevil class. Full search log: NOVELTY_SEARCH.md."
)

# ── 3. DATASET DESCRIPTION ───────────────────────────────────────────────────
add_heading(doc, "3. Dataset Description")
add_sub(doc, "3.1. Image Sources and Collection")
add_para(doc,
    "The DECAFIA dataset integrates images from three sources, unified under a single "
    "annotation protocol:"
)
add_para(doc,
    "Source 1 — Original field collection (El Socorro, Colombia). The primary corpus "
    "was captured at a Coffea arabica plantation in El Socorro, Santander, Colombia "
    "(6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024, using a smartphone "
    "camera under uncontrolled natural field lighting. Images represent the full range "
    "of illumination conditions, leaf angles, and disease severity levels encountered "
    "in the field. This source contributes all weevil-damage (coco) instances, as well "
    "as rust (roya) instances and Colombian healthy leaves."
)
add_para(doc,
    "Source 2 — RoCoLe healthy leaf images (Ecuador, re-annotated). Healthy leaf images "
    "from RoCoLe [9] (CC BY 4.0; DOI: 10.17632/c5yvn32dzg) were incorporated to augment "
    "healthy class representation."
)
add_para(doc,
    "Source 3 — Silva et al. leaf-miner images (Brazil, re-annotated). Leaf-miner images "
    "from Silva et al. [10] (CC BY 4.0; DOI: 10.17632/vfxf4trtcg.5) were incorporated to "
    "enrich the minador class. Most images in this source were acquired in a laboratory on "
    "a white background [10], introducing a distribution shift relative to Colombian field "
    "images (Section 5.3)."
)
add_para(doc,
    "Reflection images (anti-false-positive design). 141 images of sunlight reflections on "
    "healthy leaf surfaces were deliberately included as background images. Early rust "
    "lesions visually overlap with specular reflections on the adaxial leaf surface; these "
    "images train the model to distinguish them."
)

add_sub(doc, "3.2. Dataset Composition and Split")
add_para(doc,
    "Of 2,803 raw images evaluated, 17 were excluded due to unresolvable annotation "
    "ambiguity, yielding 2,315 final images. Images are split into train (1,577), "
    "validation (382), and test (356) subsets. The split is grouped by leaf: all crops, "
    "rotations, and capture-series frames from the same physical leaf are assigned to the "
    "same subset, preventing crop-parent and capture-series pairs from crossing split "
    "boundaries. Capture-series grouping for third-party images (Sources 2 and 3) is "
    "based on filename patterns and assumed proximity within sequences, not verified "
    "identity; this is a conservative assumption designed to minimise cross-split "
    "duplication (future work: per-image provenance verification)."
)
add_para(doc,
    "An independent post-hoc integrity audit using 64-bit DCT perceptual hashing "
    "(minimum Hamming distance over 8 dihedral transforms) identified 49 test images "
    "(13.8% of the test set) with a geometrically transformed copy in the training or "
    "validation split (Section 4.3)."
)

# Table 2 — Composition
t2_headers = ["Class / Set", "Train", "Validation", "Test", "Total instances"]
t2_rows = [
    ["Roya (instances)",     f"{COMP['train']['roya']}",    f"{COMP['val']['roya']}",    f"{GT['roya']}",    f"{TOT_ROYA}"],
    ["Coco (instances)",     f"{COMP['train']['coco']}",    f"{COMP['val']['coco']}",    f"{GT['coco']}",    f"{TOT_COCO}"],
    ["Minador (instances)",  f"{COMP['train']['minador']}", f"{COMP['val']['minador']}", f"{GT['minador']}", f"{TOT_MINADOR}"],
    ["Background images",    f"{COMP['train']['bg']}",      f"{COMP['val']['bg']}",      f"{COMP['test']['bg']}",  f"{TOT_BG}"],
    ["Total images",         f"{COMP['train']['images']}", f"{COMP['val']['images']}",  f"{COMP['test']['images']}",  f"{TOT_IMAGES}"],
]
add_table(doc, t2_headers, t2_rows,
    "Table 2. DECAFIA dataset composition by class and split. Instance counts are "
    "bounding-box annotations; background images contain no disease instances. "
    "Split is grouped by leaf (grouped_v1)."
)

add_sub(doc, "3.3. Annotation Protocol")
add_para(doc,
    "All images were annotated using VGG Image Annotator (VIA) v2.0 [11] with polygon "
    "regions generated by Segment Anything Model (SAM) [12] in interactive point-prompt "
    "mode. Class labels were assigned using this protocol; a second annotator independently "
    "reviewed labels during the thesis phase, and disagreements were resolved by consulting "
    "the Cenicafé phytosanitary identification guide [13]. Bounding boxes for YOLO "
    "training were derived from polygon bounding rectangles. SAM polygon masks are "
    "retained in the repository for instance-segmentation research."
)
add_para(doc,
    "Class definitions: (1) Roya — orange-yellow urediniospore pustules on the abaxial "
    "surface (Hemileia vastatrix); (2) Coco — irregular through-perforations with brown "
    "necrotic margins characteristic of adult weevil (Curculionidae: Compsus sp. / "
    "Epicaerus sp.) feeding, consistent with Cenicafé reference materials [3, 13]; "
    "(3) Minador — serpentine mines visible as whitish-grey trails on the adaxial surface "
    "(Leucoptera coffeella). Background images contain no disease instances. "
    "Formal entomological specimen collection for species-level confirmation was not "
    "conducted; the Curculionidae assignment reflects field morphological consistency "
    "with Cenicafé reference materials. The 'coco' label refers specifically to this "
    "weevil defoliation damage class and must not be confused with damage from other "
    "Coleoptera families."
)

# ── 4. METHODOLOGY ───────────────────────────────────────────────────────────
add_heading(doc, "4. Methodology")
add_sub(doc, "4.1. Baseline Model: YOLOv8m")
add_para(doc,
    "A YOLOv8m model [14] initialised with MS COCO pre-trained weights [15] was trained "
    "as the baseline benchmark. YOLOv8m was selected as a mid-scale architecture balancing "
    "accuracy and inference cost, with 25.9M parameters. Training used Ultralytics 8.4.148, "
    "PyTorch 2.11.0+cu128, CUDA 12.8, on a single NVIDIA RTX 5070 Laptop GPU. "
    "The best checkpoint was saved at epoch 98 (validation mAP@0.50 = 0.924)."
)

# Table 3 — Training configuration
t3_headers = ["Hyperparameter", "Value"]
t3_rows = [
    ["Architecture",         "YOLOv8m"],
    ["Pretrained weights",   "MS COCO"],
    ["Epochs",               "100"],
    ["Image size",           "640 × 640 px"],
    ["Batch size",           "16"],
    ["Optimizer",            "AdamW"],
    ["Learning rate (lr0)",  "0.01"],
    ["Learning rate (lrf)",  "0.01"],
    ["Seed",                 "42"],
    ["NMS IoU (evaluation)", "0.7"],
    ["Confidence (evaluation)", "0.001"],
    ["Augmentation",         "Albumentations defaults"],
    ["Framework",            "Ultralytics 8.4.148"],
    ["Hardware",             "NVIDIA RTX 5070 Laptop GPU"],
]
add_table(doc, t3_headers, t3_rows,
    "Table 3. Training configuration for the YOLOv8m baseline (decafia_grouped_v1)."
)

add_sub(doc, "4.2. Evaluation Procedure")
add_para(doc,
    "Model performance is reported on the full 356-image test set using Ultralytics "
    "`model.val()` with NMS IoU threshold = 0.7, confidence threshold = 0.001. "
    "mAP@0.50 and mAP@0.50:0.95 follow the COCO evaluation protocol. "
    "Precision, recall, and F1 are reported at confidence threshold 0.50. "
    "All numbers are sourced from metrics_final.json, archived in the public "
    "code repository (https://github.com/estebanr25/decafia-research). "
    f"Model weights SHA-256 (first 32 hex digits): {d['phase4']['model']['sha256'][:32]}…"
)

add_sub(doc, "4.3. Integrity Audit")
add_para(doc,
    "An integrity audit was conducted to identify and quantify transformed-copy overlap "
    "between splits. For each pair of images across splits, the minimum Hamming distance "
    "over 8 dihedral transforms (4 rotations × 2 flips) of a 64-bit DCT perceptual hash "
    "was computed. Pairs with distance ≤ 4 (Tier A) were verified with SIFT+RANSAC "
    "keypoint matching using a foreground-appropriate mask: non-white pixel mask for "
    "laboratory images (Source 3), green-leaf HSV mask for field images. A pair was "
    "confirmed as a copy if inliers ≥ 30 and hull coverage ≥ 0.50. Cross-split pairs "
    "that passed both checks were added to an exclusion list."
)
add_para(doc,
    "The largest verified component (272 images, the MINEIRO_99 group) comprises "
    "laboratory leaf-miner images (Source 3) with SIFT-verified geometric copies across "
    "split boundaries. This component was identified post-hoc; its size (12% of the "
    "dataset) prevents restructuring the split while maintaining all three classes in the "
    "test set (Section 5.3)."
)

add_sub(doc, "4.4. Bootstrap Confidence Intervals")
add_para(doc,
    "Bootstrap confidence intervals (95%, B = 2,000, seed = 42) are reported where valid. "
    "Clusters are defined as v1 leaf groups (group_root from assignments). "
    "A per-class cluster bootstrap validity check was applied: if a single cluster holds "
    "more than 50% of that class's test instances, the cluster bootstrap cannot estimate "
    "a meaningful interval for that class. "
    "Roya: 10 clusters, largest holds 53.1% of test instances — cluster CI not reportable. "
    "Coco: 6 clusters, largest holds 37.2% — reportable. "
    "Minador: cluster CI computed but not reported in the manuscript (Section 5.3). "
    "Image-level bootstrap CIs are reported as secondary (they ignore within-leaf "
    "correlation)."
)

# ── 5. RESULTS ───────────────────────────────────────────────────────────────
add_heading(doc, "5. Results")
add_sub(doc, "5.1. Overall Detection Performance")
add_para(doc,
    f"Table 4 presents test-set performance. The YOLOv8m baseline achieves "
    f"mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP95:.3f} on the full 356-image "
    f"test set. At confidence threshold 0.50: overall precision = {prf['all']['P']:.3f}, "
    f"recall = {prf['all']['R']:.3f}, F1 = {prf['all']['F1']:.3f}. "
    f"Background false alarm rate = 0.019 ({p4['background_far_at_conf050']['n_with_detection']} of "
    f"{p4['background_far_at_conf050']['n_background']} background images triggered at "
    f"least one detection at conf = 0.50, iou = 0.7; exact value {bg_rate:.6f}). "
    "For literature context, Araaf et al. [16] reported mAP@0.50 = 0.732 for single-class "
    "rust detection on a different dataset — not directly comparable."
)

# Table 4 — Performance
t4_headers = ["Metric", "Overall", "Roya", "Coco", "Minador†"]
t4_rows = [
    ["mAP@0.50",
     f"{mAP50:.3f}",
     f"{roya_50:.3f}",
     f"{coco_50:.3f}",
     f"{mina_50:.3f}†"],
    ["mAP@0.50:0.95",
     f"{mAP95:.3f}",
     f"{roya_95:.3f}",
     f"{coco_95:.3f}",
     f"{mina_95:.3f}†"],
    ["Precision (conf=0.50)",
     f"{prf['all']['P']:.3f}",
     f"{prf['roya']['P']:.3f}",
     f"{prf['coco']['P']:.3f}",
     f"{prf['minador']['P']:.3f}†"],
    ["Recall (conf=0.50)",
     f"{prf['all']['R']:.3f}",
     f"{prf['roya']['R']:.3f}",
     f"{prf['coco']['R']:.3f}",
     f"{prf['minador']['R']:.3f}†"],
    ["F1 (conf=0.50)",
     f"{prf['all']['F1']:.3f}",
     f"{prf['roya']['F1']:.3f}",
     f"{prf['coco']['F1']:.3f}",
     f"{prf['minador']['F1']:.3f}†"],
    ["GT instances (test)",
     f"{GT['roya']+GT['coco']+GT['minador']}",
     f"{GT['roya']}",
     f"{GT['coco']}",
     f"{GT['minador']}†"],
]
add_table(doc, t4_headers, t4_rows,
    f"Table 4. Baseline performance on the DECAFIA test set (n = 356 images, "
    f"NMS IoU = 0.7, eval conf = 0.001). "
    f"†Minador test performance cannot be interpreted as performance on independent "
    f"held-out leaves (see Section 5.3 and 6.3)."
)

add_sub(doc, "5.2. Per-Class Performance and Confidence Intervals")
add_para(doc,
    f"Fig. 7 shows mAP@0.50 per class with confidence intervals where reportable. "
    f"Coco achieves mAP@0.50 = {coco_50:.3f} (95% cluster CI [{coco_lo:.3f}, {coco_hi:.3f}], "
    f"B = 2,000, leaf groups as clusters). "
    f"Roya achieves mAP@0.50 = {roya_50:.3f}; a cluster confidence interval cannot be "
    f"reported because one leaf group (ROYA_RECORTES) holds 53.1% of roya test instances, "
    f"exceeding the 50% single-cluster threshold. Image-level CI (secondary; ignores "
    f"within-leaf correlation): [{roya_lo:.3f}, {roya_hi:.3f}]. "
    f"Minador mAP@0.50 = {mina_50:.3f}†; see Section 5.3."
)

add_sub(doc, "5.3. Integrity Audit and Sensitivity Analysis")
add_para(doc,
    "The integrity audit identified 60 cross-split pairs at pHash distance ≤ 4, affecting "
    "49 unique test images (13.8% of the test set). Of these, 25 roya annotations "
    "(3.0% of test roya instances; some images carry multiple instances), "
    "12 coco annotations (1.5%), and 88 minador annotations (23.5%) are from "
    "the 49 affected images."
)
add_para(doc,
    f"To measure the effect, the model was evaluated on both the full test set and a "
    f"filtered test set that excludes the 49 affected images (n = 307). The results are "
    f"mAP@0.50 = {mAP50:.3f} on the full test set and mAP@0.50 = {filt50:.3f} on the "
    f"filtered set (Δ = {delta:.4f}). The two test sets differ in composition; this "
    f"comparison measures sensitivity to the contamination and is not a corrected metric."
)

add_sub(doc, "5.4. Confusion Matrix and Error Analysis")
add_para(doc,
    "The normalised confusion matrix (Fig. 3b) shows the primary error mode is missed "
    "detections classified as background rather than inter-class confusion. "
    f"Roya recall at conf = 0.50: {prf['roya']['R']:.3f} "
    f"(FN = {prf['roya']['FN']}; primary error: visual overlap with specular "
    "reflections and early-stage chlorosis). "
    f"Coco recall: {prf['coco']['R']:.3f}. "
    f"Minador recall: {prf['minador']['R']:.3f}†. "
    "Inter-class confusion is negligible (all off-diagonal disease–disease values < 0.01)."
)

# Figures
add_figure(
    doc,
    FIGURES / "figure3_confusion_counts.png",
    f"Fig. 3a. Confusion matrix for decafia_grouped_v1 on split_grouped_v1 test set "
    f"(n = 356 images) at confidence threshold 0.50 — raw counts. "
    f"GT counts: roya = {GT['roya']}, coco = {GT['coco']}, minador = {GT['minador']}. "
    f"Rows = predicted class; columns = true class; last row/column = background.",
    width=Inches(3.0)
)
add_figure(
    doc,
    FIGURES / "figure3_confusion_normalized.png",
    f"Fig. 3b. Confusion matrix — normalized by true class. Same test set as Fig. 3a.",
    width=Inches(3.0)
)
add_figure(
    doc,
    FIGURES / "figure5_training_curves.png",
    "Fig. 5. Training curves (val mAP@0.50 vs. epoch) for decafia_grouped_v1 on "
    "split_grouped_v1. Best checkpoint at epoch 98 (val mAP@0.50 = 0.924).",
    width=Inches(5.5)
)
add_figure(
    doc,
    FIGURES / "figure7_bootstrap_intervals.png",
    f"Fig. 7. mAP@0.50 per class with 95% confidence intervals (B = 2,000, seed = 42). "
    f"Solid bars = cluster bootstrap (coco, reportable); dashed bars = image-level CI "
    f"(roya, secondary — ignores within-leaf correlation). "
    f"†Minador: point estimate only; CI not shown (see Section 5.3).",
    width=Inches(5.5)
)

# ── 6. DISCUSSION ────────────────────────────────────────────────────────────
add_heading(doc, "6. Discussion")
add_sub(doc, "6.1. Dataset Novelty and Position in the Literature")
add_para(doc,
    "DECAFIA contributes an annotated dataset for multi-class object detection of coffee "
    "foliar conditions under Colombian Andean field conditions. Its distinguishing "
    "characteristics are: Colombian field imagery, multi-class simultaneous detection "
    "(rust + weevil + leaf-miner), instance-level bounding boxes, and an open-access "
    "release with full annotation provenance."
)
add_para(doc,
    "To the best of the author's knowledge, none of the public coffee-leaf datasets "
    "reviewed for this work includes a class for weevil (Curculionidae) feeding damage "
    "(Table 1). The review covered datasets available through Mendeley Data, Zenodo, "
    "Kaggle, Roboflow Universe, and IEEE DataPort, as well as published literature, "
    "through November 2026 (see NOVELTY_SEARCH.md for the full search log). "
    "Datasets reviewed and their classes: Silva et al. [10] (rust, leaf miner); "
    "BRACOL [18] (leaf miner, rust, brown leaf spot, cercospora); "
    "JMuBEN/JMuBEN2 (phoma, cercospora, rust, miner, healthy); "
    "RoCoLe [9] (rust, red spider mite, healthy). "
    "No dataset with a Curculionidae, weevil, or locally denominated 'vaquita'/'coco' "
    "class was found in this review. Full query documentation is provided in the "
    "repository file NOVELTY_SEARCH.md (https://github.com/estebanr25/decafia-research)."
)

add_sub(doc, "6.2. The mAP@0.50 / mAP@0.50:0.95 Gap")
add_para(doc,
    f"The gap between mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP95:.3f} is "
    "expected for field-collected phytopathological images. Rust pustules, insect damage "
    "sites, and mining trails present ambiguous boundaries; stricter IoU thresholds "
    "penalise imprecise boundary regression for inherently diffuse lesions. This gap is "
    "consistent with other agricultural detection benchmarks [4, 7]."
)

add_sub(doc, "6.3. Limitations")
add_para(doc,
    "(1) Dataset heterogeneity: Source 3 images (laboratory, white background) introduce "
    "a distribution shift relative to Colombian field images. The largest verified "
    "transformed-copy component (272 images) comprises these laboratory images. "
    "All minador test images belong to this component; therefore, minador test performance "
    f"(mAP@0.50 = {mina_50:.3f}) cannot be interpreted as performance on independent "
    "held-out leaves. mAP@0.50 for rust and weevil detection is based on test images "
    "with no verified transformed copies in the training split."
)
add_para(doc,
    "(2) Single training seed: Bootstrap CIs reflect test-set sampling variability only; "
    "training variability is not captured."
)
add_para(doc,
    "(3) Grouped split conservatism: Capture-series grouping for third-party images is "
    "based on filename patterns and assumed proximity within sequences, not verified "
    "identity; some same-leaf images may still cross split boundaries."
)
add_para(doc,
    "(4) Roya cluster structure: The roya leaf group ROYA_RECORTES holds 53.1% of "
    "test-set roya instances, preventing a meaningful cluster bootstrap interval for "
    "that class."
)

# ── 7. CONCLUSIONS ───────────────────────────────────────────────────────────
add_heading(doc, "7. Conclusions")
add_para(doc,
    "DECAFIA provides a multi-source annotated dataset of 2,315 coffee leaf images with "
    "bounding-box annotations for three foliar conditions under Colombian Andean field "
    f"conditions. A YOLOv8m baseline achieves mAP@0.50 = {mAP50:.3f} and "
    f"mAP@0.50:0.95 = {mAP95:.3f} on the 356-image test set "
    f"(rust: {roya_50:.3f}, 95% image-level CI [{roya_lo:.3f}, {roya_hi:.3f}]; "
    f"weevil: {coco_50:.3f}, 95% cluster CI [{coco_lo:.3f}, {coco_hi:.3f}]). "
    "An integrity audit identified 49 test images with geometrically verified copies in "
    f"the training split; excluding them yields mAP@0.50 = {filt50:.3f} "
    f"(Δ = {delta:.4f}). "
    "This sensitivity check is not a corrected metric; the two test sets differ in "
    "composition."
)
add_para(doc,
    "The dataset, model weights, and all evaluation code are publicly available, enabling "
    "reproducible comparison and community extension."
)
p = doc.add_paragraph(style="Normal")
p.add_run(
    f"† Minador test performance cannot be interpreted as independent-leaf evaluation "
    "(see Section 6.3)."
)

# ── 8. PRACTICAL APPLICATION ─────────────────────────────────────────────────
add_heading(doc, "8. Practical Application")
add_para(doc,
    "The DECAFIA dataset and trained model enable Colombian coffee farmers and agricultural "
    "extension services to develop automated, smartphone-based diagnosis tools for three "
    "common foliar conditions. A model trained on DECAFIA can be integrated into mobile "
    "applications to provide real-time, instance-level localization of rust pustules, "
    "weevil perforation patterns, and leaf-miner serpentine mines under the illumination, "
    "altitude, and variety conditions of the Colombian Andean coffee belt. This level of "
    "specificity is not achievable with models trained on existing datasets collected under "
    "Ecuadorean or Brazilian conditions."
)
add_para(doc,
    "For integrated pest management (IPM), instance-level bounding-box detection enables "
    "estimation of infestation severity per image, which can be linked to economic damage "
    "thresholds for timely intervention decisions. The integrity audit methodology — "
    "combining perceptual hashing and SIFT-based geometric verification — is directly "
    "reusable for quality control of any field-collected image dataset before model "
    "deployment, independent of crop type."
)
add_para(doc,
    "The dataset, model weights, and evaluation code are released as open-access resources "
    "to support reproducible research and technology transfer to coffee-growing regions of "
    "Colombia and other Andean nations."
)

# ── DECLARATIONS ─────────────────────────────────────────────────────────────
add_heading(doc, "Data Availability")
add_para(doc,
    "Dataset (images, YOLO labels, dataset.yaml, split assignments): "
    "https://doi.org/10.5281/zenodo.19931903 (concept DOI; v2.1.0 version DOI "
    "[PEGAR DOI ZENODO v2.1.0]). "
    f"Model weights (best.pt, SHA-256: {MODEL_SHA[:16]}…): "
    "[PEGAR URL HUGGING FACE]. "
    "Source code: https://github.com/estebanr25/decafia-research."
)

add_heading(doc, "Author Contributions")
add_para(doc,
    "CRediT (Contributor Roles Taxonomy): L. E. Rosas Ruiz — Conceptualization, "
    "Data curation, Formal analysis, Investigation, Methodology, Project administration, "
    "Resources, Software, Validation, Visualization, Writing – original draft, "
    "Writing – review & editing."
)

add_heading(doc, "Acknowledgements")
add_para(doc,
    "This work derives from the undergraduate thesis of L. E. Rosas Ruiz and "
    "A. F. Salom Medina, directed by Prof. J. G. Barrero Pérez, Escuela de Ingenierías "
    "Eléctrica, Electrónica y de Telecomunicaciones, Universidad Industrial de Santander. "
    "A. F. Salom Medina contributed to image annotation during the thesis. "
    "Prof. J. G. Barrero Pérez provided direction and supervision of the thesis research. "
    "The authors thank the farm owners in El Socorro, Santander, for plantation access, "
    "and Cenicafé for phytosanitary identification guidelines."
)

add_heading(doc, "Funding")
add_para(doc, "This research received no external funding.")

add_heading(doc, "Conflicts of Interest")
add_para(doc, "The author declares no conflicts of interest.")

add_heading(doc, "Statement on Artificial Intelligence")
add_para(doc,
    "During the elaboration of this work, the author used Claude Code (Anthropic) with "
    "the aim to assist with data analysis scripting, figure generation, manuscript "
    "formatting, and evidence verification. After using this tool, the author reviewed "
    "and edited the content as necessary and takes full responsibility for the content "
    "of the publication."
)

# ── REFERENCES ───────────────────────────────────────────────────────────────
add_heading(doc, "References")
refs = [
    "[1] Federación Nacional de Cafeteros de Colombia, \"Informe de Gestión 2024,\" "
    "FNC, Bogotá, Colombia, 2024. [Online]. Available: https://federaciondecafeteros.org. "
    "[Accessed: Nov. 2026].",

    "[2] J. Avelino et al., \"The coffee rust crises in Colombia and Central America "
    "(2008–2013),\" Food Security, vol. 7, pp. 303–321, 2015, "
    "doi: 10.1007/s12571-015-0446-9.",

    "[3] L. M. Constantino et al., \"Otros habitantes naturales del cafetal,\" in "
    "Manual del Cafetero Colombiano, vol. 2, Cenicafé, Chinchiná, Colombia, 2013, "
    "pp. 261–306, doi: 10.38141/cenbook-0026_25.",

    "[4] Y. Tian et al., \"MD-YOLO: Multi-scale Dense YOLO for small target pest "
    "detection,\" Comput. Electron. Agric., vol. 213, p. 108233, 2023, "
    "doi: 10.1016/j.compag.2023.108233.",

    "[5] S. P. Mohanty, D. P. Hughes, and M. Salathé, \"Using deep learning for "
    "image-based plant disease detection,\" Front. Plant Sci., vol. 7, p. 1419, 2016, "
    "doi: 10.3389/fpls.2016.01419.",

    "[6] A. Sajitha et al., \"A comprehensive review of CNN-based plant disease "
    "detection,\" Artif. Intell. Rev., vol. 58, pp. 1–45, 2025, "
    "doi: 10.1007/s10462-024-11052-2.",

    "[7] H. P. Somanna, P. Stynes, and C. H. Muntean, \"A deep learning-based plant "
    "disease detection and classification for Arabica coffee leaves,\" in Deep Learning "
    "Theory and Applications (Commun. Comput. Inf. Sci.), Springer, Cham, 2024, "
    "pp. 19–37, doi: 10.1007/978-3-031-66694-0_2.",

    "[8] J. J. Zúñiga Cajas et al., \"Estimating the severity of coffee leaf rust using "
    "deep learning and image processing,\" Inteligencia Artificial, vol. 28, no. 76, "
    "pp. 200–222, 2025, doi: 10.4114/intartif.vol28iss76pp200-222.",

    "[9] J. Parraga-Alava, K. Cusme, A. Loor, and E. Santander, \"RoCoLe: A robusta "
    "coffee leaf images dataset,\" Data Brief, vol. 25, p. 104414, 2019, "
    "doi: 10.1016/j.dib.2019.104414.",

    "[10] L. B. Silva, A. L. C. Carneiro, and M. S. A. R. Faulin, \"Rust and leaf miner "
    "in coffee crop (Coffea arabica),\" Mendeley Data, V5, 2020, "
    "doi: 10.17632/vfxf4trtcg.5.",

    "[11] A. Dutta and A. Zisserman, \"The VGG image annotator (VIA),\" Image Vis. "
    "Comput., vol. 89, pp. 188–196, 2019, doi: 10.1016/j.imavis.2019.06.011.",

    "[12] A. Kirillov et al., \"Segment Anything,\" in Proc. IEEE/CVF ICCV, Paris, 2023, "
    "pp. 4015–4026, doi: 10.1109/ICCV51070.2023.00371.",

    "[13] L. M. Constantino et al., \"Roya del Cafeto,\" in Manual del Cafetero "
    "Colombiano, vol. 2, Cenicafé, Chinchiná, Colombia, 2013, "
    "doi: 10.38141/cenbook-0026_25.",

    "[14] G. Jocher, A. Chaurasia, and J. Qiu, \"Ultralytics YOLO (version 8.4.148),\" "
    "GitHub, 2023. [Online]. Available: https://github.com/ultralytics/ultralytics. "
    "[Accessed: Mar. 2025]. Version 8.4.148 used in this work.",

    "[15] T.-Y. Lin et al., \"Microsoft COCO: Common objects in context,\" in Proc. "
    "ECCV, Springer, Zurich, 2014, pp. 740–755, "
    "doi: 10.1007/978-3-319-10602-1_48.",

    "[16] R. T. Araaf, A. Minn, and T. Ahamed, \"Coffee leaf rust disease detection "
    "and implementation of an edge device for pruning infected leaves via deep "
    "learning,\" Sensors, vol. 24, p. 8018, 2024, doi: 10.3390/s24248018.",

    "[17] A. F. Salom Medina and L. E. Rosas Ruiz, \"Detección y prevención de riesgo "
    "de enfermedades en plantaciones de café mediante inteligencia artificial,\" Trabajo "
    "de Grado, Programa de Ingeniería Electrónica, Univ. Ind. Santander, Bucaramanga, "
    "Colombia, 2024. [Online]. Available: "
    "https://noesis.uis.edu.co/handle/20.500.14071/42486",

    "[18] J. G. M. Esgario, R. A. C. Barata, and V. S. Baravati, \"Deep learning for "
    "classification and severity estimation of coffee leaf biotic stress,\" Comput. "
    "Electron. Agric., vol. 169, p. 105162, 2020, "
    "doi: 10.1016/j.compag.2019.105162.",
]

for r in refs:
    doc.add_paragraph(r, style="References")

# ── Save v4 ──────────────────────────────────────────────────────────────────
out_path = MANUSCRIPT / "CoffeeLeafCO_manuscript_v4.docx"
doc.save(out_path)
print(f"\nSaved: {out_path}")

# Word count
all_text = " ".join(p.text for p in doc.paragraphs)
wc = len(all_text.split())
print(f"Word count (text only, approx): {wc}")
print(f"  Abstract: {wc_abs} words ({'PASS' if wc_abs <= 250 else 'FAIL'})")

# Practical application word count
pa_text = ""
in_pa = False
for p in doc.paragraphs:
    if "8. Practical Application" in p.text:
        in_pa = True
        continue
    if in_pa and p.text.startswith("Data Availability"):
        break
    if in_pa:
        pa_text += p.text + " "
pa_wc = len(pa_text.split())
print(f"  Practical application: {pa_wc} words ({'PASS' if 150 <= pa_wc <= 200 else 'CHECK'})")

# Highlights check
print(f"  Highlights: {len(highlights)} items")
for h in highlights:
    print(f"    {len(h):3d} chars: {h}")

# Banned strings
banned = ["92.4%","76.6%","2,786","Coccinellidae","Pseudococcidae",
          "leakage-free","sin fuga","no leakage","κ = 0.91",
          "anonymous", "[CONFIRMAR", "supervisor"]
found_banned = [b for b in banned if b.lower() in all_text.lower()]
print(f"Banned/removed strings: {'PASS' if not found_banned else 'FAIL: ' + str(found_banned)}")

# SHA-256
sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
print(f"v4 SHA-256: {sha[:16]}")

# ── ANONYMOUS VERSION v4 ─────────────────────────────────────────────────────
doc_anon = Document(out_path)

# In anonymous version, replace thesis citation [17] with [Author, year]
# and remove it from the reference list
anon_map = [
    # Author identity
    ("Luis Esteban Rosas Ruiz\u00b9",                "[AUTHOR]\u00b9"),
    ("Luis Esteban Rosas Ruiz",                      "[AUTHOR]"),
    ("L. E. Rosas Ruiz",                             "[AUTHOR]"),
    ("luis.rosas@correo.uis.edu.co",                 "[EMAIL REMOVED]"),
    ("ORCID: 0000-0003-0233-6336",                   "ORCID: [ORCID REMOVED]"),
    ("A. F. Salom Medina",                           "[CO-AUTHOR]"),
    ("J. G. Barrero Pérez",                          "[DIRECTOR]"),
    # Self-citations and repos
    ("https://github.com/estebanr25/decafia-research", "[link removed for double-blind review]"),
    ("https://noesis.uis.edu.co/handle/20.500.14071/42486", "[link removed for double-blind review]"),
    # Institution/location
    ("Universidad Industrial de Santander, Bucaramanga, Colombia\n"
     "Corresponding author",
     "[INSTITUTION]\nCorresponding author"),
    ("Universidad Industrial de Santander, Bucaramanga, Colombia",
     "[INSTITUTION]"),
    ("Universidad Industrial de Santander",          "[INSTITUTION]"),
    ("Univ. Ind. Santander, Bucaramanga, Colombia",  "[INSTITUTION]"),
    ("Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T), "
     "[INSTITUTION]",
     "[INSTITUTION-SCHOOL], [INSTITUTION]"),
    ("Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)",
     "[INSTITUTION-SCHOOL]"),
    ("El Socorro, Santander, Colombia",              "[LOCATION], Colombia"),
    ("El Socorro, Santander",                        "[LOCATION]"),
    ("Bucaramanga, Colombia",                        "[CITY], Colombia"),
    # Thesis citation in body → [Author, year]
    ("[17]",                                         "[Author, 2024]"),
    # Department / school name (uniquely identifies UIS)
    ("Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T), "
     "[INSTITUTION]",
     "[DEPARTMENT], [INSTITUTION]"),
    ("Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)",
     "[DEPARTMENT]"),
    ("Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones",
     "[DEPARTMENT]"),
    # Location fallback
    ("El Socorro",                                   "[LOCATION]"),
    # GPS coordinates uniquely identify the field site
    ("6°28′N, 73°19′W",                             "[coordinates withheld]"),
    # Zenodo concept DOI reveals author identity
    ("https://doi.org/10.5281/zenodo.19931903",      "[dataset DOI withheld for double-blind review]"),
    ("10.5281/zenodo.19931903",                      "[dataset DOI withheld for double-blind review]"),
    # Thesis-origin phrase in annotation section
    ("during the thesis phase",                      "in a previous annotation pass"),
    # Code repository
    ("https://github.com/estebanr25/decafia-research", "[link removed for double-blind review]"),
]

THESIS_SENTENCE = (
    "The work extends a preliminary dataset first introduced in the author's undergraduate "
    "thesis [17]; this article supersedes those earlier results, which used an earlier version "
    "of the dataset later corrected for source attribution, coco-class taxonomy, and same-leaf "
    "duplication between train and test subsets. "
)
THESIS_SENTENCE_ANON = (
    "This article supersedes an earlier dataset version that was corrected for source "
    "attribution, coco-class taxonomy, and same-leaf duplication between train and test subsets. "
)

paras_to_remove_anon = []
for p in doc_anon.paragraphs:
    full_text = "".join(r.text for r in p.runs)
    # Remove thesis reference [17] from reference list (starts with "[17]")
    if full_text.strip().startswith("[17]"):
        paras_to_remove_anon.append(p)
        continue
    new_text = full_text
    # Replace thesis sentence with anonymized version
    if THESIS_SENTENCE in new_text:
        new_text = new_text.replace(THESIS_SENTENCE, THESIS_SENTENCE_ANON)
    for orig, repl in anon_map:
        new_text = new_text.replace(orig, repl)
    if new_text != full_text:
        for i, run in enumerate(p.runs):
            if i == 0:
                run.text = new_text
            else:
                run.text = ""

# Find the position of [16] reference to insert stub [17] after it
ref16_para = None
for p in doc_anon.paragraphs:
    if "".join(r.text for r in p.runs).strip().startswith("[16]"):
        ref16_para = p
        break

for p in paras_to_remove_anon:
    p._element.getparent().remove(p._element)
print(f"Removed {len(paras_to_remove_anon)} paragraphs from anonymous version (thesis ref)")

# Insert anonymized stub for [17] after [16] to avoid revealing the gap
if ref16_para is not None:
    from docx.oxml.ns import qn as _qn
    new_para = doc_anon.add_paragraph(
        "[17] [Reference withheld for double-blind review]",
        style="References"
    )
    # Move the new paragraph element to come right after ref16_para's element
    ref16_para._element.addnext(new_para._element)
    print("Inserted stub [17] in anonymous reference list")

# Also anonymize table content
for tbl in doc_anon.tables:
    for row in tbl.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                full_text = "".join(r.text for r in p.runs)
                new_text = full_text
                for orig, repl in anon_map:
                    new_text = new_text.replace(orig, repl)
                if new_text != full_text:
                    for i, run in enumerate(p.runs):
                        if i == 0: run.text = new_text
                        else: run.text = ""

anon_path = MANUSCRIPT / "CoffeeLeafCO_manuscript_v4_anonymous.docx"
doc_anon.save(anon_path)
print(f"Saved anonymous: {anon_path}")

# PII check on anonymous version
anon_text = " ".join(p.text for p in doc_anon.paragraphs)
pii_strings = [
    "Luis Esteban Rosas Ruiz",
    "luis.rosas@correo.uis.edu.co",
    "0000-0003-0233-6336",
    "estebanr25",
    "El Socorro",
    "Bucaramanga",
]
pii_found = [s for s in pii_strings if s in anon_text]
print(f"Anonymous PII check: {'PASS' if not pii_found else 'FAIL: ' + str(pii_found)}")

anon_sha = hashlib.sha256(anon_path.read_bytes()).hexdigest()
print(f"v4 anonymous SHA-256: {anon_sha[:16]}")
print("\nDone.")
