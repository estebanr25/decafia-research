"""
Verification script for decafia_clean.
Tasks 1-4. Task 1 partially writes (manifest correction).
Task 4 writes crops to provenance_check/outliers/.
"""
import csv, re, struct, shutil
from pathlib import Path
from collections import defaultdict

BASE     = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset")
ORIG     = BASE / "decafia_yolo_original"
CLEAN    = BASE / "decafia_clean"
MANIFEST = BASE / "provenance_manifest.csv"
OUTDIR   = BASE / "provenance_check" / "outliers"

SPLITS = ("train", "val", "test")


def get_prefix(stem):
    m = re.match(r"^([A-Za-z_]+)", stem)
    return m.group(1).rstrip("_") if m else "(none)"


# =============================================================================
# TASK 1 — provenance_evidence integrity
# =============================================================================
print("=" * 70)
print("TASK 1 — provenance_evidence integrity")
print("=" * 70)

with open(MANIFEST, newline="", encoding="utf-8") as fh:
    manifest_rows = list(csv.DictReader(fh))

# Count by (inferred_source, provenance_evidence)
pair_counts = defaultdict(int)
for r in manifest_rows:
    pair_counts[(r["inferred_source"], r["provenance_evidence"])] += 1

print("\n  Rows per (inferred_source, provenance_evidence):")
for (src, evd), cnt in sorted(pair_counts.items()):
    print(f"    ({src!r}, {evd!r}): {cnt}")

# Which prefixes carry declared_by_author?
pfx_evd = defaultdict(set)
for r in manifest_rows:
    pfx = get_prefix(Path(r["filename"]).stem)
    pfx_evd[pfx].add(r["provenance_evidence"])

print("\n  Prefixes with declared_by_author:")
for pfx in sorted(pfx_evd):
    if "declared_by_author" in pfx_evd[pfx]:
        print(f"    {pfx}")

# Correct ROYA_RECORTES -> inferred_weak
roya_recortes_rows = [r for r in manifest_rows
                      if get_prefix(Path(r["filename"]).stem) == "ROYA_RECORTES"]
print(f"\n  ROYA_RECORTES rows: {len(roya_recortes_rows)}")
print(f"  Current evidence for ROYA_RECORTES: "
      f"{set(r['provenance_evidence'] for r in roya_recortes_rows)}")
print(f"  Current source for ROYA_RECORTES: "
      f"{set(r['inferred_source'] for r in roya_recortes_rows)}")

# Update manifest
changed = 0
updated_rows = []
for r in manifest_rows:
    pfx = get_prefix(Path(r["filename"]).stem)
    row = dict(r)
    if pfx == "ROYA_RECORTES" and row["provenance_evidence"] == "declared_by_author":
        row["provenance_evidence"] = "inferred_weak"
        changed += 1
    updated_rows.append(row)

fieldnames = list(manifest_rows[0].keys())
with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(updated_rows)

print(f"\n  Rows changed to inferred_weak: {changed}")
print(f"  Manifest rewritten. ({len(updated_rows)} rows total)")


# =============================================================================
# TASK 2 — Reconcile annotation counts
# =============================================================================
print("\n" + "=" * 70)
print("TASK 2 — Annotation count reconciliation")
print("=" * 70)

def count_annotations(dataset_root, split):
    """Count total annotation lines across all label files for a split."""
    lbl_dir = dataset_root / "labels" / split
    total = 0
    files = 0
    for lbl in lbl_dir.iterdir():
        files += 1
        for line in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                total += 1
    return files, total

print("\n  decafia_yolo_original (original class IDs, includes sano class 2):")
orig_totals = {}
for split in SPLITS:
    files, ann = count_annotations(ORIG, split)
    orig_totals[split] = ann
    print(f"    {split}: {files} label files, {ann} annotation lines")
print(f"    TOTAL: {sum(orig_totals.values())}")

print("\n  decafia_clean (remapped, rocole excluded, sano lines dropped):")
clean_totals = {}
for split in SPLITS:
    files, ann = count_annotations(CLEAN, split)
    clean_totals[split] = ann
    print(f"    {split}: {files} label files, {ann} annotation lines")
print(f"    TOTAL: {sum(clean_totals.values())}")

# Count how many sano (class 2) lines exist in original
print("\n  Class-2 (sano) annotation lines in decafia_yolo_original per split:")
sano_total = 0
for split in SPLITS:
    lbl_dir = ORIG / "labels" / split
    cnt = 0
    for lbl in lbl_dir.iterdir():
        for line in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and line.split()[0] == "2":
                cnt += 1
    sano_total += cnt
    print(f"    {split}: {cnt} sano lines")
print(f"    TOTAL sano lines: {sano_total}")

# What is the "~8100" figure referring to? Check splits/ directory
splits_dir = BASE / "splits"
if splits_dir.exists():
    print("\n  Checking 01_dataset/splits/ annotation count (possible source of ~8100 figure):")
    for split in SPLITS:
        lbl_dir = splits_dir / split / "labels" if (splits_dir / split / "labels").exists() else None
        if lbl_dir and lbl_dir.exists():
            files2, ann2 = count_annotations(splits_dir / split, "")
            # adapt — labels are directly in split/labels
            cnt2 = 0
            f2 = 0
            for lbl in (splits_dir / split / "labels").iterdir():
                f2 += 1
                for line in lbl.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.strip():
                        cnt2 += 1
            print(f"    {split}: {f2} label files, {cnt2} annotation lines")


# =============================================================================
# TASK 3 — Reconcile background images
# =============================================================================
print("\n" + "=" * 70)
print("TASK 3 — Background image reconciliation")
print("=" * 70)

# Count SANAS_* images in decafia_clean
sanas_all = []
sanas_nonempty = []

for split in SPLITS:
    img_dir = CLEAN / "images" / split
    lbl_dir = CLEAN / "labels" / split
    for img in img_dir.iterdir():
        pfx = get_prefix(img.stem)
        if pfx in ("SANAS_NUEVAS", "SANAS_SOCORRO"):
            lbl = lbl_dir / (img.stem + ".txt")
            ann_lines = []
            if lbl.exists():
                ann_lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines()
                             if l.strip()]
            sanas_all.append((split, img.name, ann_lines))
            if ann_lines:
                sanas_nonempty.append((split, img.name, ann_lines))

print(f"\n  Total SANAS_NUEVAS + SANAS_SOCORRO in decafia_clean: {len(sanas_all)}")
print(f"  Of those, with non-empty label files: {len(sanas_nonempty)}")
print(f"  Background (empty labels): {len(sanas_all) - len(sanas_nonempty)}")

# Also count all background images
all_bg = 0
for split in SPLITS:
    lbl_dir = CLEAN / "labels" / split
    for lbl in lbl_dir.iterdir():
        lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            all_bg += 1
print(f"  Total background images in decafia_clean (all prefixes, empty labels): {all_bg}")

if sanas_nonempty:
    print(f"\n  SANAS_* images with non-empty label files ({len(sanas_nonempty)}):")
    for split, fname, ann_lines in sorted(sanas_nonempty):
        class_ids = sorted(set(int(l.split()[0]) for l in ann_lines))
        print(f"    {split}/{fname}  classes={class_ids}  lines={len(ann_lines)}")
else:
    print("\n  No SANAS_* images with non-empty label files found.")

# Check non-SANAS background images
print("\n  Background images by prefix (top prefixes not SANAS_*):")
bg_by_pfx = defaultdict(int)
for split in SPLITS:
    img_dir = CLEAN / "images" / split
    lbl_dir = CLEAN / "labels" / split
    for lbl in lbl_dir.iterdir():
        lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            pfx = get_prefix(lbl.stem)
            bg_by_pfx[pfx] += 1
for pfx, cnt in sorted(bg_by_pfx.items(), key=lambda x: -x[1]):
    print(f"    {pfx}: {cnt}")


# =============================================================================
# TASK 4 — Locate cross-source outliers and crop
# =============================================================================
print("\n" + "=" * 70)
print("TASK 4 — Cross-source outliers")
print("=" * 70)

# Find: single minador (class 2) in own_field image
# Find: single coco (class 1) in rust_and_leaf_miner image

# Build lookup: filename -> source
fname_to_src = {}
for r in updated_rows:
    fname_to_src[r["filename"]] = r["inferred_source"]

outliers = []
for split in SPLITS:
    img_dir = CLEAN / "images" / split
    lbl_dir = CLEAN / "labels" / split
    for lbl in lbl_dir.iterdir():
        fname = lbl.stem + ".jpg"
        src = fname_to_src.get(fname, "unknown")
        lines = [l.strip() for l in lbl.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            cid = int(line.split()[0])
            # minador (2) in own_field
            if cid == 2 and src == "own_field":
                outliers.append({
                    "type": "minador_in_own_field",
                    "split": split,
                    "filename": fname,
                    "source": src,
                    "label_line": line,
                    "img_path": img_dir / fname,
                    "class_id": cid,
                })
            # coco (1) in rust_and_leaf_miner
            elif cid == 1 and src == "rust_and_leaf_miner":
                outliers.append({
                    "type": "coco_in_rust_leaf",
                    "split": split,
                    "filename": fname,
                    "source": src,
                    "label_line": line,
                    "img_path": img_dir / fname,
                    "class_id": cid,
                })

print(f"\n  Outliers found: {len(outliers)}")
for o in outliers:
    print(f"\n  [{o['type']}]")
    print(f"    filename  : {o['filename']}")
    print(f"    split     : {o['split']}")
    print(f"    source    : {o['source']}")
    print(f"    label line: {o['label_line']}")

# Crop bounding boxes
def read_jpeg_dims(path):
    with open(path, "rb") as f:
        f.read(2)
        while True:
            marker = f.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                break
            length = struct.unpack(">H", f.read(2))[0]
            if marker[1] in (0xC0, 0xC2):
                f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            f.seek(length - 2, 1)
    return None, None

def read_png_dims(path):
    with open(path, "rb") as f:
        hdr = f.read(24)
    if hdr[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", hdr[16:24])
        return w, h
    return None, None

def get_dims(path):
    path = Path(path)
    suf = path.suffix.lower()
    if suf in (".jpg", ".jpeg"):
        return read_jpeg_dims(path)
    elif suf == ".png":
        return read_png_dims(path)
    return None, None

# Try to import PIL/Pillow for cropping; fall back to manual JPEG extraction
try:
    from PIL import Image as PILImage
    HAS_PIL = True
    print("\n  Pillow available — will use for cropping.")
except ImportError:
    HAS_PIL = False
    print("\n  Pillow not available — attempting to import from conda env.")
    try:
        import sys
        sys.path.insert(0, r"C:\Users\luise\miniforge3\envs\ia\Lib\site-packages")
        from PIL import Image as PILImage
        HAS_PIL = True
        print("  Loaded Pillow from conda env path.")
    except ImportError:
        print("  Pillow still not found — crops cannot be saved.")

OUTDIR.mkdir(parents=True, exist_ok=True)

for i, o in enumerate(outliers):
    img_path = o["img_path"]
    parts    = o["label_line"].split()
    cid_str, cx, cy, bw, bh = parts[0], float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

    if not img_path.exists():
        # Try .jpg / .JPG / .png variations
        for ext in (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"):
            candidate = img_path.with_suffix(ext)
            if candidate.exists():
                img_path = candidate
                break

    if not img_path.exists():
        print(f"\n  WARNING: image not found for {o['filename']}")
        continue

    W, H = get_dims(img_path)
    if W is None:
        print(f"\n  WARNING: could not read dims for {img_path}")
        continue

    # YOLO bbox -> pixel coords
    px_cx = cx * W
    px_cy = cy * H
    px_bw = bw * W
    px_bh = bh * H
    x1 = max(0, int(px_cx - px_bw / 2))
    y1 = max(0, int(px_cy - px_bh / 2))
    x2 = min(W, int(px_cx + px_bw / 2))
    y2 = min(H, int(px_cy + px_bh / 2))

    class_name = {0: "roya", 1: "coco", 2: "minador"}.get(int(cid_str), "unknown")
    out_name   = f"{o['type']}_{o['split']}_{Path(o['filename']).stem}_cls{cid_str}_{class_name}.jpg"
    out_path   = OUTDIR / out_name

    print(f"\n  [{o['type']}] image dims: {W}x{H}")
    print(f"    BBox pixels: ({x1},{y1}) -> ({x2},{y2})")
    print(f"    Crop output: {out_path.name}")

    if HAS_PIL:
        try:
            img = PILImage.open(img_path).convert("RGB")
            crop = img.crop((x1, y1, x2, y2))
            crop.save(out_path, "JPEG", quality=95)
            print(f"    Saved crop: {out_path}")
        except Exception as ex:
            print(f"    ERROR saving crop: {ex}")
    else:
        print("    Skipping crop (no Pillow).")

print("\n" + "=" * 70)
print("ALL TASKS COMPLETE")
print("=" * 70)
