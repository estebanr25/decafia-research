"""
figure_split_schematic.py
Dataset construction and integrity audit pipeline diagram.
All numbers rendered from repository files.
"""
import csv
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ---- Paths ----------------------------------------------------------------
ASSIGNMENTS = 'C:/Users/luise/temp/decafia-research/split_v2/assignments_v2.csv'
COPY_PAIRS = 'C:/Users/luise/temp/decafia-research/split_v2/copy_pairs.csv'
METRICS = 'C:/Users/luise/temp/decafia-research/paper1/results/metrics_final.json'
OUT_DIR = 'C:/Users/luise/temp/decafia-research/paper1/figures'
SUBMISSION_DIR = 'C:/Users/luise/temp/decafia-research/paper1/manuscript/figures_submission'

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# ---- Load numbers from files -----------------------------------------------
rows = []
with open(ASSIGNMENTS) as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

total_images = len(rows)
n_own = sum(1 for r in rows if r['source'] == 'own_field')
n_silva = sum(1 for r in rows if r['source'] == 'rust_and_leaf_miner')
n_train = sum(1 for r in rows if r['split_v1'] == 'train')
n_val = sum(1 for r in rows if r['split_v1'] == 'val')
n_test = sum(1 for r in rows if r['split_v1'] == 'test')

pairs = []
with open(COPY_PAIRS) as f:
    reader = csv.DictReader(f)
    for row in reader:
        pairs.append(row)

merged_cross = [r for r in pairs if r['decision'] == 'merge' and r['cross_split'] == 'True']
tier_a_cross = sum(1 for r in merged_cross if r['tier'] == 'A')
tier_b_cross = sum(1 for r in merged_cross if r['tier'] == 'B')
total_pairs = len(merged_cross)

test_images = set()
for r in merged_cross:
    if r['split_a'] == 'test':
        test_images.add(r['stem_a'])
    if r['split_b'] == 'test':
        test_images.add(r['stem_b'])
n_unique_test = len(test_images)

test_with_train = set()
for r in merged_cross:
    if r['split_a'] == 'test' and r['split_b'] == 'train':
        test_with_train.add(r['stem_a'])
    if r['split_b'] == 'test' and r['split_a'] == 'train':
        test_with_train.add(r['stem_b'])
n_train_copy = len(test_with_train)
n_val_only = n_unique_test - n_train_copy

with open(METRICS) as f:
    metrics = json.load(f)

n_excluded = metrics['exclusion_list']['n_excluded']
n_filtered = metrics['filtered_test']['n_images']

print(f'Total: {total_images}, Own: {n_own}, Silva: {n_silva}')
print(f'Train: {n_train}, Val: {n_val}, Test: {n_test}')
print(f'Tier A: {tier_a_cross}, Tier B: {tier_b_cross}, Total: {total_pairs}')
print(f'Unique test affected: {n_unique_test} (train copy: {n_train_copy}, val-only: {n_val_only})')
print(f'Filtered test: {n_filtered}')

# ---- Build diagram ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.4, 8.5))  # ~86mm wide at 25.4mm/in
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

BOX_FACECOLOR = '#E8F0FE'
BOX_EDGECOLOR = '#3B6DBF'
STEP_FACECOLOR = '#FFF3E0'
STEP_EDGECOLOR = '#E65100'
ARROW_COLOR = '#444444'

def draw_box(ax, x, y, w, h, text, facecolor=BOX_FACECOLOR, edgecolor=BOX_EDGECOLOR,
             fontsize=7, bold=False):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle='round,pad=0.01',
        facecolor=facecolor, edgecolor=edgecolor, linewidth=0.8
    )
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text,
            ha='center', va='center', fontsize=fontsize,
            fontweight=weight, wrap=True,
            multialignment='center')

def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=ARROW_COLOR, lw=0.8))

# Layout positions (y from top)
Y = [0.91, 0.78, 0.63, 0.50, 0.38, 0.26, 0.14]
H = 0.09
W_BOX = 0.92
X0 = 0.04

# Row 0: source boxes side by side
row0_y = Y[0]
draw_box(ax, X0, row0_y, 0.42, H,
         f'Own-field images\nn = {n_own:,}\n(El Socorro, Colombia)',
         fontsize=6.5)
draw_box(ax, X0 + 0.46, row0_y, 0.42, H,
         f'Silva et al. images\nn = {n_silva:,}\n(Brazil)',
         fontsize=6.5)

# Merge arrow
cx = X0 + W_BOX / 2
arrow(ax, 0.25, row0_y, cx, Y[1] + H)
arrow(ax, 0.71, row0_y, cx, Y[1] + H)

# Row 1: Grouping
draw_box(ax, X0, Y[1], W_BOX, H,
         f'Total dataset: {total_images:,} images\n'
         f'Grouped split: crop-parent links + filename capture-series blocks',
         fontsize=6.5)

# Arrow
arrow(ax, cx, Y[1], cx, Y[2] + H)

# Row 2: Split
draw_box(ax, X0, Y[2], W_BOX, H,
         f'split_grouped_v1\nTrain: {n_train:,}  |  Val: {n_val:,}  |  Test: {n_test:,}',
         fontsize=6.5, bold=False)

# Arrow
arrow(ax, cx, Y[2], cx, Y[3] + H)

# Row 3: Audit
draw_box(ax, X0, Y[3], W_BOX, H,
         f'Post-hoc integrity audit\n'
         f'pHash \u2264 4: {tier_a_cross} pairs (Tier A)  |  pHash 5\u20138: {tier_b_cross} pairs (Tier B)\n'
         f'SIFT + RANSAC verification with foreground masks',
         fontsize=6, facecolor=STEP_FACECOLOR, edgecolor=STEP_EDGECOLOR)

# Arrow
arrow(ax, cx, Y[3], cx, Y[4] + H)

# Row 4: Verified copies
draw_box(ax, X0, Y[4], W_BOX, H,
         f'Verified cross-split copies: {total_pairs} pairs\n'
         f'\u2192 {n_unique_test} unique test images affected\n'
         f'({n_train_copy} have copy in train; {n_val_only} have copy only in val)',
         fontsize=6.5, facecolor=STEP_FACECOLOR, edgecolor=STEP_EDGECOLOR)

# Arrow
arrow(ax, cx, Y[4], cx, Y[5] + H)

# Row 5: Sensitivity
draw_box(ax, X0, Y[5], W_BOX, H,
         f'Sensitivity analysis\n'
         f'Full test: {n_test} images \u2192 Filtered test: {n_filtered} images\n'
         f'(excluding {n_excluded} affected images)',
         fontsize=6.5)

# Source label at bottom
ax.text(cx, 0.03,
        'Numbers from: split_v2/assignments_v2.csv\n'
        'split_v2/copy_pairs.csv · paper1/results/metrics_final.json',
        ha='center', va='bottom', fontsize=5, color='#666666',
        style='italic')

plt.tight_layout(pad=0.2)

# ---- Save PNG ---------------------------------------------------------------
out_png = os.path.join(OUT_DIR, 'figure_split_schematic.png')
fig.savefig(out_png, dpi=150, bbox_inches='tight')
print(f'Saved PNG: {out_png}')

# ---- Save TIFF LZW 300dpi ---------------------------------------------------
out_tif = os.path.join(SUBMISSION_DIR, 'Fig_schematic.tif')
fig.savefig(out_tif, dpi=300, format='tiff',
            pil_kwargs={'compression': 'tiff_lzw'})
print(f'Saved TIFF: {out_tif}')

plt.close(fig)

# ---- Sidecar JSON -----------------------------------------------------------
sidecar = {
    'source_files': [ASSIGNMENTS, COPY_PAIRS, METRICS],
    'numbers': {
        'total_images': total_images,
        'own_field': n_own,
        'silva_et_al': n_silva,
        'train': n_train,
        'val': n_val,
        'test': n_test,
        'tier_a_cross_pairs': tier_a_cross,
        'tier_b_cross_pairs': tier_b_cross,
        'total_cross_pairs': total_pairs,
        'unique_test_affected': n_unique_test,
        'test_with_train_copy': n_train_copy,
        'test_with_val_only_copy': n_val_only,
        'n_excluded': n_excluded,
        'filtered_test': n_filtered,
    }
}
out_json = os.path.join(OUT_DIR, 'figure_split_schematic_sidecar.json')
with open(out_json, 'w') as f:
    json.dump(sidecar, f, indent=2)
print(f'Saved sidecar: {out_json}')
print('Done.')
