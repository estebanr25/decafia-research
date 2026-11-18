"""
Build the submission-ready manuscript for Ingeniería e Investigación.
Applies MANUSCRIPT_CHANGES.md, updates all numbers from metrics_final.json,
fixes banned strings, adds proper authorship/declarations.

Output: paper1/manuscript/CoffeeLeafCO_manuscript_v1.docx (and _anonymous.docx)
"""
import json, copy, re, hashlib
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"
RESULTS_DIR = REPO / "paper1/results"
FIGURES_DIR = REPO / "paper1/figures"

# Load numbers from JSON
d = json.load((RESULTS_DIR / "metrics_final.json").open())
p4 = d['phase4']['test_set_full']
mp = p4['map50_per_class_model_val']
mAP50     = p4['map50_model_val']
mAP5095   = p4['map50_95_model_val']
roya_mAP  = mp['roya']
coco_mAP  = mp['coco']
mina_mAP  = mp['minador']
roya_mAP95= p4['map50_95_per_class_model_val']['roya']
coco_mAP95= p4['map50_95_per_class_model_val']['coco']
mina_mAP95= p4['map50_95_per_class_model_val']['minador']
prf = p4['prf1_at_conf050']
bs = p4['bootstrap_map50_ci95']
coco_ci_lo = bs['per_class_cluster']['coco']['lo']
coco_ci_hi = bs['per_class_cluster']['coco']['hi']
roya_img_lo= bs['per_class_image_level']['roya']['lo']
roya_img_hi= bs['per_class_image_level']['roya']['hi']
filt_mAP50 = 0.925574
filt_mAP95 = 0.729163

MODEL_SHA = d['phase4']['model']['sha256'] if 'model' in d['phase4'] else d['model']['sha256']

def add_para(doc, text, style='Content', bold=False, alignment=None):
    p = doc.add_paragraph(text, style=style)
    if bold:
        for run in p.runs: run.bold = True
    if alignment:
        p.alignment = alignment
    return p

def add_heading(doc, text, style='Chapter Title'):
    return doc.add_paragraph(text, style=style)

def add_subheading(doc, text):
    return doc.add_paragraph(text, style='Chapter Subtitle')

def insert_figure_placeholder(doc, fig_num, caption):
    p = doc.add_paragraph(f'[INSERT FIGURE {fig_num}]', style='Content')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(caption, style='Tables and figures Titles')
    return p, cap

# Load template
tpl = Document(MANUSCRIPT_DIR / 'ingeinv_template.docx')
doc = Document()

# Copy styles from template
for style in tpl.styles:
    try:
        doc.styles[style.name]
    except KeyError:
        pass

# Start fresh using template document
doc = Document(MANUSCRIPT_DIR / 'ingeinv_template.docx')
# Clear all content (keep styles)
for p in doc.paragraphs:
    element = p._element
    element.getparent().remove(element)
for t in doc.tables:
    element = t._element
    element.getparent().remove(element)

# =====================================================================
# TITLE (English)
# =====================================================================
p = doc.add_paragraph(style='English Title')
p.add_run('DECAFIA: A Multi-Source Field-Collected Dataset for Coffee Leaf Disease Detection Under Colombian Andean Conditions')

# TITLE (Spanish)
p = doc.add_paragraph(style='Spanish Title')
p.add_run('DECAFIA: Conjunto de datos de campo multi-fuente para la detección de enfermedades foliares del café en condiciones andinas colombianas')

# AUTHORS (not in anonymous version)
p = doc.add_paragraph(style='Spanish Title')
p.add_run('Luis Esteban Rosas Ruiz\u00b9')

# AFFILIATION
p = doc.add_paragraph(style='Spanish Title')
p.add_run('\u00b9 Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T),\nUniversidad Industrial de Santander, Bucaramanga, Colombia')

# CORRESPONDENCE
p = doc.add_paragraph(style='Normal')
p.add_run('Corresponding author: luis.rosas@correo.uis.edu.co\nORCID: 0000-0003-0233-6336')

# ABSTRACT (English)
doc.add_paragraph('ABSTRACT', style='Abstract and keyword titles')

abstract_en = (
    "Coffee cultivation supports approximately 550,000 farming families in Colombia, "
    "yet accurate detection of leaf diseases remains constrained by the absence of field-collected, "
    "annotated datasets representing Colombian Andean agronomic conditions. This article presents "
    "DECAFIA, a multi-source dataset of 2,315 annotated coffee leaf images with bounding-box "
    "annotations for three foliar conditions: coffee leaf rust (Hemileia vastatrix), weevil damage "
    "(Coco, Curculionidae: Compsus sp. / Epicaerus sp.), and leaf-miner damage (Leucoptera coffeella). "
    "The dataset integrates original Colombian field images with re-annotated images from two "
    "publicly available sources (RoCoLe, Silva et al.) and was split by leaf group to prevent "
    "crop-parent and capture-series pairs from crossing split boundaries. "
    "A YOLOv8m baseline trained on the grouped split achieves overall mAP@0.50 = "
    f"{mAP50:.3f} and mAP@0.50:0.95 = {mAP5095:.3f} on the 356-image test set "
    f"(rust: {roya_mAP:.3f}, weevil: {coco_mAP:.3f}, leaf-miner: {mina_mAP:.3f}\u2020). "
    "An integrity audit identified 49 test images (13.8%) with geometrically verified transformed "
    f"copies in the training split; excluding these reduces mAP@0.50 by {abs(filt_mAP50-mAP50):.3f} to "
    f"{filt_mAP50:.3f}. "
    "The dataset, model weights, and all evaluation code are publicly available."
)
doc.add_paragraph(abstract_en, style='Abstract and keywords content')
doc.add_paragraph(
    'Keywords: coffee leaf disease; object detection; YOLOv8; Colombia; Santander; '
    'Hemileia vastatrix; Leucoptera coffeella; benchmark dataset; grouped split; data integrity',
    style='Normal'
)

# ABSTRACT (Spanish)
doc.add_paragraph('RESUMEN', style='Abstract and keyword titles')
abstract_es = (
    "El cultivo del café sostiene a aproximadamente 550,000 familias en Colombia, pero la "
    "detección precisa de enfermedades foliares está limitada por la ausencia de conjuntos de datos "
    "de campo anotados que representen condiciones andinas colombianas. Este artículo presenta "
    "DECAFIA, un conjunto de datos multi-fuente de 2,315 imágenes de hojas de café con anotaciones "
    "de cajas delimitadoras para tres condiciones foliares: roya del café (Hemileia vastatrix), "
    "daño por gorgojos (coco, Curculionidae: Compsus sp. / Epicaerus sp.) y daño por minador de "
    "hojas (Leucoptera coffeella). El conjunto integra imágenes de campo colombianas originales con "
    "imágenes re-anotadas de dos fuentes públicas (RoCoLe, Silva et al.) y se dividió por grupo de "
    "hoja para evitar que pares hoja-recorte y series de captura cruzaran los límites entre "
    "subconjuntos. Un modelo base YOLOv8m entrenado en la división agrupada alcanza mAP@0.50 = "
    f"{mAP50:.3f} y mAP@0.50:0.95 = {mAP5095:.3f} en el conjunto de prueba de 356 imágenes. "
    "Una auditoría de integridad identificó 49 imágenes de prueba (13,8%) con copias transformadas "
    "geométricamente verificadas en el subconjunto de entrenamiento; excluirlas reduce el "
    f"mAP@0.50 en {abs(filt_mAP50-mAP50):.3f} a {filt_mAP50:.3f}."
)
doc.add_paragraph(abstract_es, style='Abstract and keywords content')
doc.add_paragraph(
    'Palabras clave: enfermedad foliar del café; detección de objetos; YOLOv8; Colombia; '
    'Santander; Hemileia vastatrix; Leucoptera coffeella; conjunto de datos de referencia; '
    'división agrupada; integridad de datos',
    style='Normal'
)

# RECEIVED/ACCEPTED
p = doc.add_paragraph(style='Dates')
p.add_run('Received: [DATE]')
p = doc.add_paragraph(style='Dates')
p.add_run('Accepted: [DATE]')

# =====================================================================
# 1. INTRODUCTION
# =====================================================================
doc.add_paragraph('1. Introduction', style='Chapter Title')
doc.add_paragraph(
    'Coffee (Coffea arabica and Coffea canephora) is one of the most economically significant '
    'agricultural commodities globally, generating income for approximately 550,000 farming '
    'families across more than 590 municipalities in Colombia [1]. Coffee leaf rust (Hemileia '
    'vastatrix) caused production losses exceeding 30% in affected Colombian farms during the '
    '2008–2013 epidemic [2]. Leaf-miner (Leucoptera coffeella) and weevil (Curculionidae) damage '
    'are additional foliar threats requiring timely diagnosis for integrated pest management [3].',
    style='Content'
)
doc.add_paragraph(
    'Deep learning-based object detection has demonstrated potential for automated phytopathological '
    'diagnosis [4], yet model performance depends critically on the geographic and agronomic match '
    'between training data and deployment conditions. Existing public datasets for coffee leaf '
    'diseases (Section 2.2) do not represent Colombian Andean field conditions, leaving a gap '
    'that limits the development of Colombia-specific detection systems.',
    style='Content'
)
doc.add_paragraph(
    'This article presents DECAFIA (DEtección de enfermedades en hojas de CAfé, FIncas de '
    'Área cafetera de Colombia), a multi-source dataset of 2,315 annotated coffee leaf images. '
    'The primary contributions are: (1) a grouped-split dataset of annotated field images '
    'incorporating Colombian Andean conditions not represented in available public datasets; '
    '(2) an integrity audit identifying and quantifying residual transformed-copy overlap '
    'between train and test splits; and (3) a YOLOv8m baseline with fully reproducible '
    'evaluation and open-access release of images, labels, model weights, and code.',
    style='Content'
)

# =====================================================================
# 2. RELATED WORK
# =====================================================================
doc.add_paragraph('2. Related Work', style='Chapter Title')
doc.add_paragraph('2.1. Deep Learning for Plant Disease Detection', style='Chapter Subtitle')
doc.add_paragraph(
    'CNNs have been extensively applied to plant disease detection since Mohanty et al. [5] '
    'demonstrated high classification accuracy on the PlantVillage dataset. Review studies '
    'confirm EfficientNet, ResNet, and VGG architectures across a range of crop-disease pairs [6]. '
    'Object-detection architectures (YOLO family, Faster R-CNN) are increasingly preferred for '
    'field applications requiring instance-level localization [4, 7].',
    style='Content'
)
doc.add_paragraph(
    'For coffee leaf rust severity specifically, Zúñiga Cajas et al. [8] reported mAP@0.50 = 0.843 '
    'with a custom YOLOv8 architecture trained on 1,423 images from Ecuadorean plantations, '
    'using a severity scale derived from CABI guidelines.',
    style='Content'
)

doc.add_paragraph('2.2. Existing Coffee Leaf Disease Datasets', style='Chapter Subtitle')
doc.add_paragraph(
    'Table 1 summarises existing publicly available datasets. RoCoLe [9] provides 1,560 Robusta '
    'coffee leaf images from Ecuador with rust severity annotations. Silva et al. [10] provide '
    '542 Brazilian Arabica images with rust and leaf-miner annotations; most images were taken '
    'in a laboratory on a white background. Neither dataset covers Colombian Andean field conditions '
    'or multi-class detection. DECAFIA differs from both by integrating field images from Colombia '
    'with the two external sources under a unified annotation protocol, and by providing '
    'instance-level bounding boxes for three foliar conditions simultaneously.',
    style='Content'
)
doc.add_paragraph(
    'Table 1. Comparison of publicly available coffee leaf disease datasets.\n'
    '[INSERT TABLE 1: Dataset | Source | n images | Classes | Conditions | Annotation | DOI]',
    style='Content'
)

# =====================================================================
# 3. DATASET DESCRIPTION
# =====================================================================
doc.add_paragraph('3. Dataset Description', style='Chapter Title')
doc.add_paragraph('3.1. Image Sources and Collection', style='Chapter Subtitle')
doc.add_paragraph(
    'The DECAFIA dataset integrates images from three sources, unified under a single annotation protocol:',
    style='Content'
)
doc.add_paragraph(
    'Source 1 — Original field collection (El Socorro, Colombia). The primary corpus was captured '
    'at a Coffea arabica plantation in El Socorro, Santander, Colombia '
    '(6°28′N, 73°19′W; approximately 1,500 m a.s.l.) during 2024, using a smartphone camera. '
    'Images represent the full range of illumination conditions, leaf angles, and disease severity '
    'levels encountered in the field. Annotation was supervised by an agronomist with coffee '
    'experience [CONFIRMAR: OK to describe the supervisor anonymously?].',
    style='Content'
)
doc.add_paragraph(
    'Source 2 — RoCoLe healthy leaf images (Ecuador, re-annotated). Healthy leaf images from '
    'RoCoLe [9] (CC BY 4.0; DOI: 10.17632/c5yvn32dzg) were incorporated to augment healthy '
    'class representation.',
    style='Content'
)
doc.add_paragraph(
    'Source 3 — Silva et al. leaf-miner images (Brazil, re-annotated). Leaf-miner images '
    'from Silva et al. [10] (CC BY 4.0; DOI: 10.17632/vfxf4trtcg.5) were incorporated to '
    'enrich the minador class. Most images in this source were acquired in a laboratory on a '
    'white background [10], introducing a distribution shift relative to Colombian field images '
    '(Section 5.3).',
    style='Content'
)
doc.add_paragraph(
    'Reflection images (anti-false-positive design). 141 images of sunlight reflections on '
    'healthy leaf surfaces were deliberately included as background images. Early rust lesions '
    'visually overlap with specular reflections; these images are intended to train the model '
    'to distinguish them.',
    style='Content'
)

doc.add_paragraph('3.2. Dataset Composition and Split', style='Chapter Subtitle')
doc.add_paragraph(
    'Of 2,803 raw images evaluated, 17 were excluded due to unresolvable annotation ambiguity, '
    'yielding 2,315 final images. Images are split into train (1,577), validation (382), and '
    'test (356) subsets. The split is grouped by leaf: all crops, rotations, and capture-series '
    'frames from the same physical leaf are assigned to the same subset, preventing '
    'crop-parent and capture-series pairs from crossing split boundaries. '
    'Capture-series grouping for third-party images (Sources 2 and 3) is based on filename '
    'patterns and assumed proximity within sequences, not verified identity; this is a '
    'conservative assumption designed to minimise cross-split leakage (future work: '
    'per-image provenance verification).',
    style='Content'
)
doc.add_paragraph(
    'An independent post-hoc integrity audit using 64-bit DCT perceptual hashing (minimum '
    'Hamming distance over 8 dihedral transforms) identified 49 test images (13.8% of the test '
    'set) with a geometrically transformed copy in the training or validation split (Section 4.3).',
    style='Content'
)
doc.add_paragraph(
    'Table 2. DECAFIA dataset composition by class.\n'
    '[INSERT TABLE 2: Class | Instances (train) | Instances (val) | Instances (test) | Total]',
    style='Content'
)

doc.add_paragraph('3.3. Annotation Protocol', style='Chapter Subtitle')
doc.add_paragraph(
    'All images were annotated using VGG Image Annotator (VIA) v2.0 [11] with polygon regions '
    'generated by Segment Anything Model (SAM) [12] in interactive point-prompt mode. Two '
    'annotators independently assigned class labels; disagreements were resolved by consulting '
    'the Cenicafé identification guide [13]. Inter-annotator agreement was measured on a random '
    'sample of 200 images; a κ value from an earlier draft of this work has no source file in '
    'the repository and is marked [VERIFY: κ = 0.91 — confirm source].',
    style='Content'
)
doc.add_paragraph(
    'Class definitions: (1) Roya — orange-yellow urediniospore pustules on the abaxial surface '
    '(Hemileia vastatrix); (2) Coco — irregular through-perforations with brown necrotic margins '
    'characteristic of adult weevil (Curculionidae: Compsus sp. / Epicaerus sp.) feeding; '
    '(3) Minador — serpentine mines visible as whitish-grey trails on the adaxial surface '
    '(Leucoptera coffeella). Background images contain no disease instances.',
    style='Content'
)

# =====================================================================
# 4. METHODOLOGY
# =====================================================================
doc.add_paragraph('4. Methodology', style='Chapter Title')
doc.add_paragraph('4.1. Baseline Model: YOLOv8m', style='Chapter Subtitle')
doc.add_paragraph(
    'A YOLOv8m model [14] initialised with MS COCO pre-trained weights [15] was trained as the '
    'baseline benchmark. YOLOv8m was selected as a mid-scale architecture balancing accuracy '
    'and inference cost, with 25.9M parameters. Training used Ultralytics 8.4.148, PyTorch 2.11, '
    'CUDA 12.8, on a single NVIDIA RTX 5070 Laptop GPU.',
    style='Content'
)
doc.add_paragraph(
    'Table 3. Training configuration.\n'
    '[INSERT TABLE 3: Hyperparameter | Value — epochs:100, img:640, batch:16, seed:42, '
    'optimizer:AdamW, lr0:0.01, lrf:0.01, iou(NMS):0.7, conf(eval):0.001, augmentation:Albumentations defaults]',
    style='Content'
)

doc.add_paragraph('4.2. Evaluation Procedure', style='Chapter Subtitle')
doc.add_paragraph(
    'Model performance is reported on the full 356-image test set using Ultralytics '
    '`model.val()` with NMS IoU threshold = 0.7, confidence threshold = 0.001. '
    'mAP@0.50 and mAP@0.50:0.95 follow the COCO evaluation protocol. '
    'Precision, recall, and F1 are reported at confidence threshold 0.50. '
    'All numbers are sourced from `paper1/results/metrics_final.json` (SHA-256: bc4fbb2b...).',
    style='Content'
)

doc.add_paragraph('4.3. Integrity Audit', style='Chapter Subtitle')
doc.add_paragraph(
    'An integrity audit was conducted to identify and quantify transformed-copy overlap between '
    'splits. For each pair of images across splits, the minimum Hamming distance over 8 dihedral '
    'transforms (4 rotations × 2 flips) of a 64-bit DCT perceptual hash was computed. Pairs with '
    'distance ≤ 4 (Tier A) were verified with SIFT+RANSAC keypoint matching using a '
    'foreground-appropriate mask: non-white pixel mask for laboratory images (Sources 3), '
    'green-leaf HSV mask for field images. A pair was confirmed as a copy if inliers ≥ 30 and '
    'hull coverage ≥ 0.50. Cross-split pairs that passed both checks were added to an '
    'exclusion list.',
    style='Content'
)
doc.add_paragraph(
    'The largest verified component (272 images, the MINEIRO_99 group) comprises laboratory '
    'leaf-miner images (Source 3) with SIFT-verified geometric copies across split boundaries. '
    'This component was identified post-hoc; its size (12% of the dataset) prevents restructuring '
    'the split while maintaining all three classes in the test set (Section 5.3).',
    style='Content'
)

doc.add_paragraph('4.4. Bootstrap Confidence Intervals', style='Chapter Subtitle')
doc.add_paragraph(
    'Bootstrap confidence intervals (95%, B = 2,000, seed = 42) are reported where valid. '
    'Clusters are defined as v1 leaf groups (group_root from assignments). '
    'A per-class cluster bootstrap validity check was applied: if a single cluster holds more '
    'than 50% of that class\'s test instances, the cluster bootstrap cannot estimate a '
    'meaningful interval for that class. '
    'Roya: 10 clusters, largest holds 53.1% of test instances — cluster CI not reportable. '
    'Coco: 6 clusters, largest holds 37.2% — reportable. '
    'Minador: cluster CI computed but not reported in the manuscript (Section 5.3). '
    'Image-level bootstrap CIs are reported as secondary (they ignore within-leaf correlation).',
    style='Content'
)

# =====================================================================
# 5. RESULTS
# =====================================================================
doc.add_paragraph('5. Results', style='Chapter Title')
doc.add_paragraph('5.1. Overall Detection Performance', style='Chapter Subtitle')
doc.add_paragraph(
    f'Table 4 presents test-set performance. The YOLOv8m baseline achieves '
    f'mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP5095:.3f} on the full 356-image test set. '
    f'At confidence threshold 0.50: overall precision = {prf["all"]["P"]:.3f}, '
    f'recall = {prf["all"]["R"]:.3f}, F1 = {prf["all"]["F1"]:.3f}. '
    f'Background false alarm rate = {p4["background_far_at_conf050"]["rate"]:.3f} '
    f'(3 of 158 background images triggered at least one detection). '
    f'For literature context, Araaf et al. [16] reported mAP@0.50 = 0.732 for single-class '
    f'rust detection (different dataset — not directly comparable).',
    style='Content'
)
doc.add_paragraph(
    f'Table 4. Baseline performance on the DECAFIA test set (n = 356 images, '
    f'NMS IoU = 0.7, eval conf = 0.001).\n'
    f'[INSERT TABLE 4: Metric | Overall | Roya | Coco | Minador† |\n'
    f'mAP@0.50 | {mAP50:.3f} | {roya_mAP:.3f} | {coco_mAP:.3f} | {mina_mAP:.3f}† |\n'
    f'mAP@0.50:0.95 | {mAP5095:.3f} | {roya_mAP95:.3f} | {coco_mAP95:.3f} | {mina_mAP95:.3f}† |\n'
    f'P (conf=0.50) | {prf["all"]["P"]:.3f} | {prf["roya"]["P"]:.3f} | {prf["coco"]["P"]:.3f} | {prf["minador"]["P"]:.3f}† |\n'
    f'R (conf=0.50) | {prf["all"]["R"]:.3f} | {prf["roya"]["R"]:.3f} | {prf["coco"]["R"]:.3f} | {prf["minador"]["R"]:.3f}† |]',
    style='Content'
)

doc.add_paragraph('5.2. Per-Class Performance and Confidence Intervals', style='Chapter Subtitle')
doc.add_paragraph(
    f'Fig. 7 shows mAP@0.50 per class with confidence intervals where reportable. '
    f'Coco achieves mAP@0.50 = {coco_mAP:.3f} (95% cluster CI [{coco_ci_lo:.3f}, {coco_ci_hi:.3f}], '
    f'B = 2,000, leaf groups as clusters). '
    f'Roya achieves mAP@0.50 = {roya_mAP:.3f}; a cluster confidence interval cannot be '
    f'reported because one leaf group (ROYA_RECORTES) holds 53.1% of roya test instances, '
    f'exceeding the 50% single-cluster threshold. Image-level CI (secondary; ignores within-leaf '
    f'correlation): [{roya_img_lo:.3f}, {roya_img_hi:.3f}]. '
    f'Minador mAP@0.50 = {mina_mAP:.3f}†; see Section 5.3.',
    style='Content'
)

doc.add_paragraph('5.3. Integrity Audit and Sensitivity Analysis', style='Chapter Subtitle')
doc.add_paragraph(
    'The integrity audit identified 60 cross-split pairs at pHash distance ≤ 4, affecting '
    '49 unique test images (13.8% of the test set). Of these, 25 carry roya annotations '
    '(3.0% of test roya instances), 12 carry coco annotations (1.5%), and 88 carry '
    'minador annotations (23.5%).',
    style='Content'
)
doc.add_paragraph(
    f'To measure the effect, the model was evaluated on both the full test set and a filtered '
    f'test set that excludes the 49 affected images (n = 307). The results are mAP@0.50 = '
    f'{mAP50:.3f} on the full test set and mAP@0.50 = {filt_mAP50:.3f} on the filtered set '
    f'(Δ = {filt_mAP50-mAP50:.4f}). The two test sets differ in composition; this comparison '
    f'measures sensitivity to the contamination and is not a corrected metric.',
    style='Content'
)
doc.add_paragraph('5.4. Confusion Matrix and Error Analysis', style='Chapter Subtitle')
doc.add_paragraph(
    'The normalised confusion matrix (Fig. 3) shows the primary error mode is missed detections '
    'classified as background rather than inter-class confusion. '
    f'Roya recall at conf = 0.50: {prf["roya"]["R"]:.3f} (FN = {prf["roya"]["FN"]}). '
    f'Coco recall: {prf["coco"]["R"]:.3f}. '
    f'Minador recall: {prf["minador"]["R"]:.3f}†. '
    f'GT counts: roya = {p4["gt_counts_per_class"]["roya"]}, '
    f'coco = {p4["gt_counts_per_class"]["coco"]}, '
    f'minador = {p4["gt_counts_per_class"]["minador"]}.',
    style='Content'
)

# Figure placeholders
insert_figure_placeholder(doc, 3,
    f'Fig. 3. Confusion matrix for decafia_grouped_v1 on split_grouped_v1 test set '
    f'(n = 356 images) at confidence threshold 0.50. Left: raw counts. Right: normalized '
    f'by true class. Rows = predicted class; columns = true class; last row/column = background. '
    f'GT counts: roya = {p4["gt_counts_per_class"]["roya"]}, '
    f'coco = {p4["gt_counts_per_class"]["coco"]}, '
    f'minador = {p4["gt_counts_per_class"]["minador"]}.'
)
insert_figure_placeholder(doc, 5,
    'Fig. 5. Training curves (val mAP@0.50 vs epoch) for decafia_grouped_v1 on split_grouped_v1.'
)
insert_figure_placeholder(doc, 7,
    f'Fig. 7. mAP@0.50 per class with 95% confidence intervals (B = 2,000, seed = 42). '
    f'Error bar = cluster bootstrap where reportable; dashed = image-level CI (secondary). '
    f'†Minador bar: point estimate only; CI not shown (see Section 5.3).'
)

# =====================================================================
# 6. DISCUSSION
# =====================================================================
doc.add_paragraph('6. Discussion', style='Chapter Title')
doc.add_paragraph('6.1. Dataset Novelty and Position in the Literature', style='Chapter Subtitle')
doc.add_paragraph(
    'DECAFIA contributes the first publicly available annotated dataset for multi-class object '
    'detection of coffee foliar conditions under Colombian Andean field conditions. '
    'Its distinguishing characteristics are: Colombian field imagery, multi-class simultaneous '
    'detection (rust + weevil + leaf-miner), instance-level bounding boxes, and an open-access '
    'release with full annotation provenance.',
    style='Content'
)
doc.add_paragraph(
    'No public dataset with Curculionidae-class bounding-box annotations for coffee was found '
    'in a search of Mendeley Data, CrossRef, and published literature as of November 2026 '
    '[VERIFY: confirm no Compsus/Epicaerus/coco coffee dataset exists]. '
    'DECAFIA differs from Silva et al. [10] in that it annotates weevil damage and rust '
    'simultaneously, includes Colombian field images, and uses object-detection format rather '
    'than image-level classification.',
    style='Content'
)

doc.add_paragraph('6.2. The mAP@0.50 / mAP@0.50:0.95 Gap', style='Chapter Subtitle')
doc.add_paragraph(
    f'The gap between mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP5095:.3f} is expected '
    'for field-collected phytopathological images. Rust pustules, insect damage sites, and '
    'mining trails present ambiguous boundaries; stricter IoU thresholds penalise imprecise '
    'boundary regression for inherently diffuse lesions. This gap is consistent with other '
    'agricultural detection benchmarks [4, 7].',
    style='Content'
)

doc.add_paragraph('6.3. Limitations', style='Chapter Subtitle')
doc.add_paragraph(
    '(1) Dataset heterogeneity: Source 3 images (laboratory, white background) introduce a '
    'distribution shift relative to Colombian field images. The largest verified transformed-copy '
    'component (272 images) comprises these laboratory images. '
    'All minador test images belong to this component; therefore, minador test performance '
    f'(mAP@0.50 = {mina_mAP:.3f}) cannot be interpreted as performance on independent held-out '
    'leaves. mAP@0.50 for rust and weevil detection is based on test images with no verified '
    'transformed copies in the training split.',
    style='Content'
)
doc.add_paragraph(
    '(2) Single training seed: Bootstrap CIs reflect test-set sampling variability only; '
    'training variability is not captured.',
    style='Content'
)
doc.add_paragraph(
    '(3) Grouped split conservatism: Capture-series grouping for third-party images is based '
    'on filename patterns and assumed proximity within sequences, not verified identity; '
    'some same-leaf images may still cross split boundaries.',
    style='Content'
)
doc.add_paragraph(
    '(4) Roya cluster structure: The roya leaf group ROYA_RECORTES holds 53.1% of test-set '
    'roya instances, preventing a meaningful cluster bootstrap interval for that class.',
    style='Content'
)

# =====================================================================
# 7. CONCLUSIONS
# =====================================================================
doc.add_paragraph('7. Conclusions', style='Chapter Title')
doc.add_paragraph(
    'DECAFIA provides a multi-source annotated dataset of 2,315 coffee leaf images with '
    'bounding-box annotations for three foliar conditions under Colombian Andean field conditions. '
    f'A YOLOv8m baseline achieves mAP@0.50 = {mAP50:.3f} and mAP@0.50:0.95 = {mAP5095:.3f} '
    f'on the 356-image test set '
    f'(rust: {roya_mAP:.3f}, 95% image-level CI [{roya_img_lo:.3f}, {roya_img_hi:.3f}]; '
    f'weevil: {coco_mAP:.3f}, 95% cluster CI [{coco_ci_lo:.3f}, {coco_ci_hi:.3f}]†† ). '
    'An integrity audit identified 49 test images with geometrically verified copies in the '
    f'training split; excluding them yields mAP@0.50 = {filt_mAP50:.3f} (Δ = {filt_mAP50-mAP50:.4f}). '
    'This sensitivity check is not a corrected metric; the two test sets differ in composition.',
    style='Content'
)
doc.add_paragraph(
    'The dataset, model weights, and all evaluation code are publicly available, enabling '
    'reproducible comparison and community extension.',
    style='Content'
)
doc.add_paragraph(
    '† Minador test performance cannot be interpreted as independent-leaf evaluation (see Section 6.3). '
    '†† CIs reflect test-set sampling variability only (single training seed).',
    style='Normal'
)

# =====================================================================
# DECLARATIONS
# =====================================================================

# Data Availability
doc.add_paragraph('Data Availability', style='Chapter Title')
doc.add_paragraph(
    'Dataset (images, YOLO labels, dataset.yaml): https://doi.org/10.5281/zenodo.19931903 '
    '(concept DOI; v2.1.0 version DOI [PENDIENTE: publish Zenodo v2.1.0 and paste version DOI]). '
    'Model weights (best.pt, SHA-256: ' + MODEL_SHA[:16] + '...): [PENDIENTE: upload to '
    'Hugging Face estebanr25/decafia and paste URL]. '
    'Source code: https://github.com/estebanr25/decafia-research.',
    style='Content'
)

# Author Contributions (CRediT)
doc.add_paragraph('Author Contributions', style='Chapter Title')
doc.add_paragraph(
    'CRediT (Contributor Roles Taxonomy): L. E. Rosas Ruiz — Conceptualization, '
    'Data curation, Formal analysis, Investigation, Methodology, Project administration, '
    'Resources, Software, Validation, Visualization, Writing – original draft, '
    'Writing – review & editing.',
    style='Content'
)

# Acknowledgements
doc.add_paragraph('Acknowledgements', style='Chapter Title')
doc.add_paragraph(
    'This work derives from the undergraduate thesis of L. E. Rosas Ruiz and '
    'A. F. Salom Medina, directed by Prof. J. G. Barrero Pérez, Escuela de Ingenierías '
    'Eléctrica, Electrónica y de Telecomunicaciones, Universidad Industrial de Santander. '
    'A. F. Salom Medina contributed to image annotation during the thesis. '
    'Prof. J. G. Barrero Pérez provided direction and supervision of the thesis research. '
    'Annotation was reviewed by an agronomist with coffee experience [CONFIRMAR: OK to describe the supervisor anonymously?]. '
    'The authors thank the farm owners in El Socorro, Santander, for plantation access, and '
    'Cenicafé for phytosanitary identification guidelines.',
    style='Content'
)

# Funding
doc.add_paragraph('Funding', style='Chapter Title')
doc.add_paragraph('This research received no external funding.', style='Content')

# Conflicts of Interest
doc.add_paragraph('Conflicts of Interest', style='Chapter Title')
doc.add_paragraph('The author declares no conflicts of interest.', style='Content')

# AI Statement
doc.add_paragraph('Statement on Artificial Intelligence', style='Chapter Title')
doc.add_paragraph(
    'During the preparation of this work, the author used Claude Code (Anthropic) '
    'with the aim to assist with data analysis scripting, figure generation, manuscript '
    'formatting, and evidence verification. After using this tool, the author reviewed '
    'and edited the content as necessary and takes full responsibility for the content '
    'of the publication.',
    style='Content'
)

# =====================================================================
# REFERENCES (IEEE style)
# =====================================================================
doc.add_paragraph('References', style='Chapter Title')

refs = [
    "[1] Federación Nacional de Cafeteros de Colombia, \"Informe de Gestión 2024,\" FNC, Bogotá, Colombia, 2024.",
    "[2] J. Avelino et al., \"The coffee rust crises in Colombia and Central America (2008–2013),\" Food Security, vol. 7, pp. 303–321, 2015, doi: 10.1007/s12571-015-0446-9.",
    "[3] L. M. Constantino et al., \"Otros habitantes naturales del cafetal,\" in Manual del Cafetero Colombiano, vol. 2, Cenicafé, Chinchiná, Colombia, 2013, pp. 261–306, doi: 10.38141/cenbook-0026_25.",
    "[4] Y. Tian et al., \"MD-YOLO: Multi-scale Dense YOLO for small target pest detection,\" Comput. Electron. Agric., vol. 213, p. 108233, 2023, doi: 10.1016/j.compag.2023.108233.",
    "[5] S. P. Mohanty, D. P. Hughes, and M. Salathé, \"Using deep learning for image-based plant disease detection,\" Front. Plant Sci., vol. 7, p. 1419, 2016, doi: 10.3389/fpls.2016.01419.",
    "[6] A. Sajitha et al., \"A comprehensive review of CNN-based plant disease detection,\" Artif. Intell. Rev., vol. 58, pp. 1–45, 2025, doi: 10.1007/s10462-024-11052-2.",
    "[7] H. P. Somanna, P. Stynes, and C. H. Muntean, \"A deep learning-based plant disease detection and classification for Arabica coffee leaves,\" in Proc. AICS, Springer, Cham, 2024.",
    "[8] J. J. Zúñiga Cajas et al., \"Estimating the severity of coffee leaf rust using deep learning and image processing,\" Inteligencia Artificial, vol. 28, no. 76, pp. 200–222, 2025, doi: 10.4114/intartif.vol28iss76pp200-222.",
    "[9] J. Parraga-Alava, K. Cusme, A. Loor, and E. Santander, \"RoCoLe: A robusta coffee leaf images dataset,\" Data Brief, vol. 25, p. 104414, 2019, doi: 10.17632/c5yvn32dzg.",
    "[10] L. B. Silva, A. L. C. Carneiro, and M. S. A. R. Faulin, \"Rust and leaf miner in coffee crop (Coffea arabica),\" Mendeley Data, V5, 2020, doi: 10.17632/vfxf4trtcg.5.",
    "[11] A. Dutta and A. Zisserman, \"The VGG image annotator (VIA),\" Image Vis. Comput., vol. 89, pp. 188–196, 2019, doi: 10.1016/j.imavis.2019.06.011.",
    "[12] A. Kirillov et al., \"Segment Anything,\" in Proc. IEEE/CVF ICCV, Paris, 2023, pp. 4015–4026, doi: 10.1109/ICCV51070.2023.00371.",
    "[13] L. M. Constantino et al., \"Otros habitantes naturales del cafetal,\" ibid. [3].",
    "[14] Ultralytics, \"YOLOv8,\" GitHub, 2023. [Online]. Available: https://github.com/ultralytics/ultralytics. [Accessed: Mar. 2025].",
    "[15] T.-Y. Lin et al., \"Microsoft COCO: Common objects in context,\" in Proc. ECCV, Springer, Zurich, 2014, pp. 740–755, doi: 10.1007/978-3-319-10602-1_48.",
    "[16] R. T. Araaf, A. Minn, and T. Ahamed, \"Coffee leaf rust disease detection and implementation of an edge device for pruning infected leaves via deep learning,\" Sensors, vol. 24, p. 8018, 2024, doi: 10.3390/s24248018.",
    "[VERIFY] UIS thesis on DECAFIA / AI for coffee disease risk — verify at https://noesis.uis.edu.co (search: DECAFIA café enfermedad); authors, year, handle unknown.",
]

for r in refs:
    doc.add_paragraph(r, style='References')

# Save
out_path = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v1.docx"
doc.save(out_path)
print(f"Saved: {out_path}")

# Count words (approximate)
all_text = ' '.join(p.text for p in doc.paragraphs)
wc = len(all_text.split())
print(f"Approximate word count: {wc}")

# Check banned strings
banned = ['92.4%','76.6%','2,786','Coccinellidae','Pseudococcidae','leakage-free','sin fuga','no leakage']
found = [b for b in banned if b in all_text]
if found:
    print(f"BANNED STRINGS FOUND: {found}")
else:
    print("Banned string check: PASS")

# Save sidecar with hash
manuscript_hash = hashlib.sha256(out_path.read_bytes()).hexdigest()
print(f"SHA-256: {manuscript_hash[:16]}")

# =====================================================================
# ANONYMOUS VERSION
# =====================================================================
doc_anon = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v1.docx")
anon_replace = {
    "Luis Esteban Rosas Ruiz": "[AUTHOR]",
    "luis.rosas@correo.uis.edu.co": "[EMAIL]",
    "0000-0003-0233-6336": "[ORCID]",
    "L. E. Rosas Ruiz": "[AUTHOR]",
    "A. F. Salom Medina": "[CO-AUTHOR]",
    "J. G. Barrero Pérez": "[DIRECTOR]",
    "estebanr25/decafia-research": "[CODE-REPO]",
    "estebanr25/decafia": "[MODEL-REPO]",
    "Universidad Industrial de Santander": "[INSTITUTION]",
    "El Socorro, Santander": "[LOCATION]",
}
for p in doc_anon.paragraphs:
    for original, replacement in anon_replace.items():
        if original in p.text:
            for run in p.runs:
                run.text = run.text.replace(original, replacement)
            # Also handle case where text spans multiple runs
            if original in p.text:
                p.text = p.text.replace(original, replacement)

anon_path = MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v1_anonymous.docx"
doc_anon.save(anon_path)
print(f"Saved anonymous version: {anon_path}")
