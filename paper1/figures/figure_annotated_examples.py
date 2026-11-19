"""
figure_annotated_examples.py
Generates annotated image grid for the manuscript.
Selects train-only images, avoids test set.
"""
import csv
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
import numpy as np

# ---- Paths ----------------------------------------------------------------
BASE = 'C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean'
ASSIGNMENTS = 'C:/Users/luise/temp/decafia-research/split_v2/assignments_v2.csv'
OUT_DIR = 'C:/Users/luise/temp/decafia-research/paper1/figures'
SUBMISSION_DIR = 'C:/Users/luise/temp/decafia-research/paper1/manuscript/figures_submission'

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# ---- Class colours (RGB float) -------------------------------------------
CLASS_COLORS = {
    0: (1.0, 0.196, 0.196),   # roya: red
    1: (0.196, 0.392, 1.0),   # coco: blue
    2: (0.196, 0.784, 0.196),  # minador: green
}
CLASS_NAMES = {0: 'roya', 1: 'coco', 2: 'minador'}

# ---- Load assignments -------------------------------------------------------
rows = []
with open(ASSIGNMENTS) as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

def find_image(stem):
    """Return (path, actual_split) for a stem."""
    for split in ['train', 'val', 'test']:
        for ext in ['.jpg', '.jpeg', '.JPG', '.png']:
            path = os.path.join(BASE, 'images', split, stem + ext)
            if os.path.exists(path):
                return path, split
    return None, None

def find_label(stem, img_split):
    """Return label path."""
    path = os.path.join(BASE, 'labels', img_split, stem + '.txt')
    if os.path.exists(path):
        return path
    return None

def pick_train_only(candidates, n=2):
    """From sorted candidate list, pick first n that are actually on disk in train."""
    result = []
    for r in candidates:
        path, sp = find_image(r['stem'])
        if path and sp == 'train':
            result.append(r['stem'])
        if len(result) >= n:
            break
    return result

# ---- Select images ----------------------------------------------------------
# 1. Own field roya: highest roya count first
own_roya_all = [r for r in rows
                if r['source'] == 'own_field'
                and int(r['roya']) > 0
                and int(r['coco']) == 0
                and int(r['minador']) == 0
                and r['split_v2'] == 'train']
own_roya_all.sort(key=lambda r: (-int(r['roya']), r['stem']))
own_roya_sel = pick_train_only(own_roya_all[1:], 2)  # skip rank 0, pick 2nd+3rd
if len(own_roya_sel) < 2:
    own_roya_sel = pick_train_only(own_roya_all, 2)

# 2. Own field coco
own_coco_all = [r for r in rows
                if r['source'] == 'own_field'
                and int(r['coco']) > 0
                and int(r['roya']) == 0
                and int(r['minador']) == 0
                and r['split_v2'] == 'train']
own_coco_all.sort(key=lambda r: (-int(r['coco']), r['stem']))
own_coco_sel = pick_train_only(own_coco_all[1:], 2)
if len(own_coco_sel) < 2:
    own_coco_sel = pick_train_only(own_coco_all, 2)

# 3. Own field background
own_bg_all = [r for r in rows
              if r['source'] == 'own_field'
              and int(r['roya']) == 0
              and int(r['coco']) == 0
              and int(r['minador']) == 0
              and r['split_v2'] == 'train']
own_bg_all.sort(key=lambda r: r['stem'])
own_bg_sel = pick_train_only(own_bg_all[1:], 2)
if len(own_bg_sel) < 2:
    own_bg_sel = pick_train_only(own_bg_all, 2)

# 4. Silva roya
silva_roya_all = [r for r in rows
                  if r['source'] == 'rust_and_leaf_miner'
                  and int(r['roya']) > 0
                  and int(r['minador']) == 0
                  and r['split_v2'] == 'train']
silva_roya_all.sort(key=lambda r: r['stem'])
silva_roya_sel = pick_train_only(silva_roya_all[1:], 2)
if len(silva_roya_sel) < 2:
    silva_roya_sel = pick_train_only(silva_roya_all, 2)

# 5. Silva minador
silva_min_all = [r for r in rows
                 if r['source'] == 'rust_and_leaf_miner'
                 and int(r['minador']) > 0
                 and r['split_v2'] == 'train']
silva_min_all.sort(key=lambda r: r['stem'])
silva_min_sel = pick_train_only(silva_min_all[1:], 2)
if len(silva_min_sel) < 2:
    silva_min_sel = pick_train_only(silva_min_all, 2)

print('Selected images:')
print('  Own field roya:', own_roya_sel)
print('  Own field coco:', own_coco_sel)
print('  Own field bg:  ', own_bg_sel)
print('  Silva roya:    ', silva_roya_sel)
print('  Silva minador: ', silva_min_sel)

# ---- Panel definitions ------------------------------------------------------
# (stem, row_label, panel_letter)
panels = [
    (own_roya_sel[0], 'Own field\nroya', '(a)'),
    (own_roya_sel[1], 'Own field\nroya', '(b)'),
    (own_coco_sel[0], 'Own field\ncoco', '(c)'),
    (own_coco_sel[1], 'Own field\ncoco', '(d)'),
    (own_bg_sel[0],   'Own field\nhealthy', '(e)'),
    (own_bg_sel[1],   'Own field\nhealthy', '(f)'),
    (silva_roya_sel[0], 'Silva et al.\nroya', '(g)'),
    (silva_roya_sel[1], 'Silva et al.\nroya', '(h)'),
    (silva_min_sel[0], 'Silva et al.\nminador', '(i)'),
    (silva_min_sel[1], 'Silva et al.\nminador', '(j)'),
]

def load_labels(stem):
    """Load YOLO label file. Returns list of (class_id, cx, cy, w, h)."""
    path, sp = find_image(stem)
    if path is None:
        return []
    lbl = find_label(stem, sp)
    if lbl is None or not os.path.exists(lbl):
        return []
    boxes = []
    with open(lbl) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                cls, cx, cy, w, h = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                boxes.append((cls, cx, cy, w, h))
    return boxes

def draw_boxes(ax, img, boxes):
    """Draw YOLO bounding boxes on axes."""
    W, H = img.size
    for cls, cx, cy, bw, bh in boxes:
        color = CLASS_COLORS.get(cls, (1, 1, 0))
        x1 = (cx - bw / 2) * W
        y1 = (cy - bh / 2) * H
        rw = bw * W
        rh = bh * H
        rect = mpatches.Rectangle(
            (x1, y1), rw, rh,
            linewidth=1.5, edgecolor=color, facecolor='none'
        )
        ax.add_patch(rect)

# ---- Build figure -----------------------------------------------------------
N_ROWS, N_COLS = 5, 2
fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(5.0, 12.5))
fig.subplots_adjust(hspace=0.08, wspace=0.04, left=0.14, right=0.98, top=0.98, bottom=0.01)

sidecar = []

for idx, (stem, row_label, letter) in enumerate(panels):
    row = idx // N_COLS
    col = idx % N_COLS
    ax = axes[row][col]

    path, sp = find_image(stem)
    if path is None:
        ax.set_visible(False)
        continue

    img = Image.open(path).convert('RGB')
    boxes = load_labels(stem)

    # Row label on left column only
    if col == 0:
        ax.set_ylabel(row_label, fontsize=7, rotation=90, labelpad=4,
                      va='center', ha='right')

    ax.imshow(img)
    draw_boxes(ax, img, boxes)

    # Panel letter bottom-left
    ax.text(0.03, 0.04, letter, transform=ax.transAxes,
            fontsize=8, fontweight='bold', color='white',
            bbox=dict(facecolor='black', alpha=0.5, pad=1, linewidth=0))

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Collect sidecar info
    sidecar.append({
        'panel': letter,
        'stem': stem,
        'path': path,
        'split_on_disk': sp,
        'row_label': row_label,
        'n_boxes': len(boxes),
        'classes': [CLASS_NAMES.get(b[0], str(b[0])) for b in boxes],
    })

# ---- Save PNG ---------------------------------------------------------------
out_png = os.path.join(OUT_DIR, 'figure_annotated_examples.png')
fig.savefig(out_png, dpi=150, bbox_inches='tight')
print(f'Saved PNG: {out_png}')

# ---- Save TIFF LZW 300dpi ---------------------------------------------------
out_tif = os.path.join(SUBMISSION_DIR, 'Fig_examples.tif')
fig.savefig(out_tif, dpi=300, format='tiff',
            pil_kwargs={'compression': 'tiff_lzw'})
print(f'Saved TIFF: {out_tif}')

plt.close(fig)

# ---- Sidecar JSON -----------------------------------------------------------
out_json = os.path.join(OUT_DIR, 'figure_annotated_examples_sidecar.json')
with open(out_json, 'w') as f:
    json.dump(sidecar, f, indent=2)
print(f'Saved sidecar: {out_json}')
print('Done.')
