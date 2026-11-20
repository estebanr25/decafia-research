"""
verify_v7.py
# -*- coding: utf-8 -*-

Verification script for CoffeeLeafCO_manuscript_v7.docx
Checks all items from SESSION_FINAL_V7.md PART 10.

Run from: C:/Users/luise/temp/decafia-research
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import json
from pathlib import Path
from docx import Document
from lxml import etree

REPO = Path("C:/Users/luise/temp/decafia-research")
MANUSCRIPT_DIR = REPO / "paper1/manuscript"

# Load JSON reference values
with open(REPO / "paper1/results/metrics_final.json") as f:
    METRICS = json.load(f)

FAIL_COUNT = 0
PASS_COUNT = 0
WARN_COUNT = 0

def chk(label, condition, detail=""):
    global FAIL_COUNT, PASS_COUNT
    if condition:
        print(f"  PASS: {label}" + (f" ({detail})" if detail else ""))
        PASS_COUNT += 1
    else:
        print(f"  FAIL: {label}" + (f" — {detail}" if detail else ""))
        FAIL_COUNT += 1

def warn(label, detail=""):
    global WARN_COUNT
    print(f"  WARN: {label}" + (f" — {detail}" if detail else ""))
    WARN_COUNT += 1


def get_all_text(doc):
    """Get all text from doc including tables and headers/footers."""
    parts = []
    for para in doc.paragraphs:
        parts.append("".join(r.text for r in para.runs))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    parts.append("".join(r.text for r in para.runs))
    # Also check headers and footers
    for section in doc.sections:
        for header_para in section.header.paragraphs:
            parts.append("".join(r.text for r in header_para.runs))
        for footer_para in section.footer.paragraphs:
            parts.append("".join(r.text for r in footer_para.runs))
    return " ".join(parts)


def count_words(doc):
    """Count words in document body (paragraphs only, not tables/captions)."""
    total = 0
    for para in doc.paragraphs:
        t = "".join(r.text for r in para.runs)
        total += len(t.split())
    # Add table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    t = "".join(r.text for r in para.runs)
                    total += len(t.split())
    return total


def get_section_text(doc, section_start, section_end=None):
    """Get text of a section between two headings."""
    collecting = False
    parts = []
    for para in doc.paragraphs:
        t = "".join(r.text for r in para.runs)
        if section_start in t:
            collecting = True
            continue
        if collecting:
            if section_end and section_end in t:
                break
            parts.append(t)
    return " ".join(parts)


def get_abstract_text(doc):
    """Get abstract section text."""
    collecting = False
    parts = []
    for para in doc.paragraphs:
        t = "".join(r.text for r in para.runs)
        if t.strip() == "ABSTRACT":
            collecting = True
            continue
        if collecting and t.strip().startswith("Keywords:"):
            break
        if collecting and t.strip():
            parts.append(t)
    return " ".join(parts)


# ============================================================
# CHECK NAMED VERSION
# ============================================================
print("=" * 60)
print("CHECKING NAMED VERSION: CoffeeLeafCO_manuscript_v7.docx")
print("=" * 60)

doc_v7 = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7.docx")
full_text_v7 = get_all_text(doc_v7)
xml_v7 = doc_v7.element.xml

# ---------------------------------------------------------------------------
# Check 1: Drawing count
# ---------------------------------------------------------------------------
print("\n--- 1. Drawing count ---")
n_drawings = xml_v7.count('<w:drawing')

# Count figure captions (paragraphs starting with "Fig. N.")
fig_captions = []
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    if re.match(r'^Fig\. \d+[ab]?\. ', t):
        fig_captions.append(t[:60])

print(f"  Drawings: {n_drawings}")
print(f"  Figure captions: {len(fig_captions)}")
for cap in fig_captions:
    print(f"    - {cap}")
chk("Drawing count equals caption count", n_drawings == len(fig_captions),
    f"{n_drawings} drawings, {len(fig_captions)} captions")

# ---------------------------------------------------------------------------
# Check 2: Identifier search (named version — just check it has them)
# ---------------------------------------------------------------------------
print("\n--- 2. Named version identifier presence (should have) ---")
chk("Has 'Rosas' in named", "Rosas" in full_text_v7)
chk("Has author email in named", "correo.uis" in full_text_v7)
chk("Has ORCID in named", "0000-0003-0233-6336" in full_text_v7)

# ---------------------------------------------------------------------------
# Check 3: Banned strings
# ---------------------------------------------------------------------------
print("\n--- 3. Banned strings ---")
BANNED = [
    "92.4%", "76.6%", "2,786",
    "Pseudococcidae", "Coccinellidae",
    "leakage-free", "sin fuga",
    "DECAF-IA",
    "DECAFIA",
]
# Note: "DECAF IA" (project name) is ALLOWED
for b in BANNED:
    if b in full_text_v7:
        warn(f"Banned string found: '{b}'", full_text_v7[max(0,full_text_v7.find(b)-30):full_text_v7.find(b)+60])
    else:
        chk(f"Banned '{b}' not present", True)

# ---------------------------------------------------------------------------
# Check 4: [VERIFY] markers
# ---------------------------------------------------------------------------
print("\n--- 4. [VERIFY] markers ---")
verify_matches = re.findall(r'\[VERIFY[^\]]*\]', full_text_v7)
chk("No [VERIFY] markers", len(verify_matches) == 0,
    f"Found: {verify_matches}" if verify_matches else "")

# ---------------------------------------------------------------------------
# Check 5: Numbers vs JSON
# ---------------------------------------------------------------------------
print("\n--- 5. Numbers vs JSON ---")

# From JSON
phase4 = METRICS["phase4"]["test_set_full"]
map50_overall = phase4["map50_model_val"]  # 0.929377 → 0.929
map5095_overall = phase4["map50_95_model_val"]  # 0.734368 → 0.734
map50_roya = phase4["map50_per_class_model_val"]["roya"]  # 0.841307 → 0.841
map50_coco = phase4["map50_per_class_model_val"]["coco"]  # 0.961786 → 0.962
map50_min = phase4["map50_per_class_model_val"]["minador"]  # 0.985040 → 0.985

n_test = phase4["gt_counts_per_class"]  # roya:825, coco:820, minador:375
n_images_test = METRICS["full_test"]["n_images"]  # 356

filtered = METRICS["filtered_test"]
map50_filtered = filtered["map50_overall"]  # 0.925574 → 0.926
n_filtered = filtered["n_images"]  # 307

excl = METRICS["exclusion_list"]
n_excluded = excl["n_excluded"]  # 49
by_train = excl["excluded_by_train"]  # 40
by_val = excl["excluded_by_val_only"]  # 9

ci_coco = METRICS["phase4"]["test_set_full"]["bootstrap_map50_ci95"]["per_class_cluster"]["coco"]
ci_coco_lo = round(ci_coco["lo"], 3)  # 0.801
ci_coco_hi = round(ci_coco["hi"], 3)  # 0.971

split = {"train": 1577, "val": 382, "test": 356}

number_checks = [
    ("0.929", map50_overall, "mAP50 overall"),
    ("0.734", map5095_overall, "mAP50-95 overall"),
    ("0.841", map50_roya, "mAP50 roya"),
    ("0.962", map50_coco, "mAP50 coco"),
    ("0.985", map50_min, "mAP50 minador"),
    ("0.926", map50_filtered, "mAP50 filtered"),
    ("1,577", split["train"], "train split"),
    ("382", split["val"], "val split"),
    ("356", split["test"], "test split"),
    ("2,315", 2315, "total images"),
    ("0.801", ci_coco_lo, "CI coco lo"),
    ("0.971", ci_coco_hi, "CI coco hi"),
]

for text_in_doc, json_val, label in number_checks:
    in_doc = text_in_doc in full_text_v7
    # Verify JSON value rounds to text
    if isinstance(json_val, float):
        rounded = f"{json_val:.3f}"
        if rounded.endswith("0") and "." in rounded:
            rounded = rounded.rstrip("0").rstrip(".")
        # Check it matches
        expected_match = abs(json_val - float(text_in_doc)) < 0.0005
    else:
        expected_match = True
    chk(f"Number {text_in_doc} in doc ({label})", in_doc and expected_match)

# Check specific numbers
chk("2,315 in doc", "2,315" in full_text_v7, "total images")
chk("49 excluded in doc", "49" in full_text_v7)
chk("40 by_train in doc", "40" in full_text_v7)
chk("9 by_val in doc", "9 have a copy only in the val" in full_text_v7 or "val only (9)" in full_text_v7)

# ---------------------------------------------------------------------------
# Check 6: Highlights char count
# ---------------------------------------------------------------------------
print("\n--- 6. Highlights (≤85 chars each) ---")
highlights = []
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    if t.strip().startswith("•"):
        highlights.append(t.strip())

for h in highlights:
    n = len(h)
    chk(f"Highlight ≤85 chars: '{h[:60]}...' ({n})", n <= 85, f"{n} chars")

# ---------------------------------------------------------------------------
# Check 7: Abstract word count
# ---------------------------------------------------------------------------
print("\n--- 7. Abstract word count (≤250) ---")
abstract_text = get_abstract_text(doc_v7)
abstract_words = len(abstract_text.split())
chk(f"Abstract ≤250 words", abstract_words <= 250, f"{abstract_words} words")

# ---------------------------------------------------------------------------
# Check 8: Practical Application word count
# ---------------------------------------------------------------------------
print("\n--- 8. Practical Application word count (150–200) ---")
prac_text = get_section_text(doc_v7, "8. Practical Application", "Data Availability")
prac_words = len(prac_text.split())
chk(f"Practical Application 150–200 words", 150 <= prac_words <= 200, f"{prac_words} words")

# ---------------------------------------------------------------------------
# Check 9: Total word count
# ---------------------------------------------------------------------------
print("\n--- 9. Total word count ---")
total_wc = count_words(doc_v7)
print(f"  Total word count (all paragraphs + tables): {total_wc}")

# ---------------------------------------------------------------------------
# Check 10: Figures in citation order
# ---------------------------------------------------------------------------
print("\n--- 10. Figures citation order ---")
fig_first_mention = {}
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    for fig_id in ["Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5a", "Fig. 5b"]:
        if fig_id in t and fig_id not in fig_first_mention:
            fig_first_mention[fig_id] = t[:80]

print("  First mentions in order:")
for fig_id, ctx in fig_first_mention.items():
    print(f"    {fig_id}: {ctx[:70]}")

ordered = list(fig_first_mention.keys())
expected_order = ["Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5a", "Fig. 5b"]
all_present = all(f in fig_first_mention for f in expected_order)
chk("All figures cited", all_present)
if all_present:
    # Check order
    indices = [ordered.index(f) for f in expected_order]
    chk("Figures cited in order", indices == sorted(indices))

# ---------------------------------------------------------------------------
# Check 11: Tables in citation order
# ---------------------------------------------------------------------------
print("\n--- 11. Tables citation order ---")
# Count table caption paragraphs in document order
table_caps = []
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    if re.match(r'^Table \d+\.', t):
        table_caps.append((t[:60]))

print("  Table captions in document order:")
for cap in table_caps:
    print(f"    {cap}")

# Check in-text citations
table_first_mention = {}
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    for tbl_id in ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5"]:
        # Only count in-text refs (not caption lines)
        if tbl_id in t and not t.startswith(tbl_id + ".") and tbl_id not in table_first_mention:
            table_first_mention[tbl_id] = t[:80]

print("  First in-text mentions:")
for tbl_id, ctx in table_first_mention.items():
    print(f"    {tbl_id}: {ctx[:70]}")

# ---------------------------------------------------------------------------
# Check 12: References cited
# ---------------------------------------------------------------------------
print("\n--- 12. Reference checks ---")
# Find all [N] citations in text
in_text_refs = set(re.findall(r'\[(\d+)\]', full_text_v7))
# Find all reference entries [N]
ref_entries = set()
for para in doc_v7.paragraphs:
    t = "".join(r.text for r in para.runs)
    m = re.match(r'^\[(\d+)\]', t.strip())
    if m:
        ref_entries.add(m.group(1))

print(f"  In-text citations: {sorted(in_text_refs, key=int)}")
print(f"  Reference entries: {sorted(ref_entries, key=int)}")

# Check every cited ref has an entry
for r in sorted(in_text_refs, key=int):
    chk(f"Ref [{r}] has entry", r in ref_entries)

# Check every entry is cited
for r in sorted(ref_entries, key=int):
    chk(f"Ref [{r}] is cited", r in in_text_refs)

# Check no [VERIFY] in refs
verify_in_refs = re.findall(r'\[VERIFY[^\]]*\]', full_text_v7)
chk("No [VERIFY] in references", len(verify_in_refs) == 0)

# ============================================================
# CHECK ANONYMOUS VERSION
# ============================================================
print("\n" + "=" * 60)
print("CHECKING ANONYMOUS VERSION: CoffeeLeafCO_manuscript_v7_anonymous.docx")
print("=" * 60)

doc_anon = Document(MANUSCRIPT_DIR / "CoffeeLeafCO_manuscript_v7_anonymous.docx")
full_text_anon = get_all_text(doc_anon)
xml_anon = doc_anon.element.xml

# ---------------------------------------------------------------------------
# Anon Check 1: Drawing count
# ---------------------------------------------------------------------------
print("\n--- Anon 1. Drawing count ---")
n_drawings_anon = xml_anon.count('<w:drawing')
fig_captions_anon = []
for para in doc_anon.paragraphs:
    t = "".join(r.text for r in para.runs)
    if re.match(r'^Fig\. \d+[ab]?\. ', t):
        fig_captions_anon.append(t[:60])

print(f"  Drawings: {n_drawings_anon}")
print(f"  Figure captions: {len(fig_captions_anon)}")
chk("Anon drawing count equals caption count", n_drawings_anon == len(fig_captions_anon),
    f"{n_drawings_anon} drawings, {len(fig_captions_anon)} captions")

# ---------------------------------------------------------------------------
# Anon Check 2: Identifier search
# ---------------------------------------------------------------------------
print("\n--- Anon 2. Identifier search (must NOT contain) ---")

IDENTIFIERS = [
    ("Rosas", "Author surname"),
    ("Salom", "Co-author surname"),
    ("Barrero", "Director surname"),
    ("estebanr25", "GitHub username"),
    ("luise", "Windows username"),
    ("Industrial de Santander", "Institution name"),
    ("Univ. Ind.", "Abbreviated institution"),
    ("correo.uis", "Email domain"),
    ("0000-0003-0233-6336", "ORCID"),
    ("zenodo.19931903", "Zenodo ID"),
    ("huggingface", "HuggingFace"),
    ("decafia-research", "GitHub repo"),
]

# Note: "E. Santander" (RoCoLe author) is ALLOWED
# Note: "El Socorro" should be replaced with "[location withheld]"

id_issues = []
for identifier, description in IDENTIFIERS:
    if identifier in full_text_anon:
        # Find context
        idx = full_text_anon.find(identifier)
        context = full_text_anon[max(0, idx-40):idx+len(identifier)+40]
        id_issues.append((identifier, description, context))
        warn(f"Found '{identifier}' ({description})", f"Context: ...{context}...")
    else:
        chk(f"'{identifier}' not found ({description})", True)

# Check "Socorro" not present (should be "[location withheld]")
if "El Socorro" in full_text_anon:
    idx = full_text_anon.find("El Socorro")
    context = full_text_anon[max(0, idx-30):idx+40]
    warn("Found 'El Socorro' in anon", f"Context: {context}")
else:
    chk("'El Socorro' not in anon", True)

# Check "E. Santander" is still allowed (RoCoLe author)
if "E. Santander" in full_text_anon:
    chk("'E. Santander' (RoCoLe author) present and allowed", True)

# Check thesis title words
THESIS_TITLE_WORDS = ["Detecci", "prevenci", "inteligencia artificial"]
for word in THESIS_TITLE_WORDS:
    if word.lower() in full_text_anon.lower():
        idx = full_text_anon.lower().find(word.lower())
        ctx = full_text_anon[max(0,idx-30):idx+50]
        warn(f"Thesis title word '{word}' found", f"Context: {ctx}")

# Check [16] is properly anonymized
for para in doc_anon.paragraphs:
    t = "".join(r.text for r in para.runs)
    if t.strip().startswith("[16]"):
        chk("[16] entry anonymized", "[Reference withheld for double-blind review]" in t, t[:100])
        break

# Check [location withheld] in source 1
chk("[location withheld] in anon", "[location withheld]" in full_text_anon)

# ---------------------------------------------------------------------------
# Anon Check 3: Banned strings
# ---------------------------------------------------------------------------
print("\n--- Anon 3. Banned strings ---")
for b in BANNED:
    if b in full_text_anon:
        warn(f"Banned string in anon: '{b}'")
    else:
        chk(f"Anon banned '{b}' not present", True)

# Check DECAFIA in prose (not as identifier "decafia_grouped_v1" etc.)
if "DECAFIA" in full_text_anon:
    # Find context
    idx = full_text_anon.find("DECAFIA")
    ctx = full_text_anon[max(0,idx-30):idx+50]
    if "decafia_grouped" in full_text_anon[max(0,idx-5):idx+15].lower():
        chk("DECAFIA only as identifier (not prose)", True)
    else:
        warn(f"DECAFIA in prose", f"Context: {ctx}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"SUMMARY: {PASS_COUNT} passed, {FAIL_COUNT} failed, {WARN_COUNT} warnings")
print("=" * 60)

if FAIL_COUNT > 0:
    print(f"\nFAILED CHECKS: {FAIL_COUNT}")
if WARN_COUNT > 0:
    print(f"WARNINGS: {WARN_COUNT}")
if FAIL_COUNT == 0 and WARN_COUNT == 0:
    print("ALL CHECKS PASSED")

print("\nDone.")
