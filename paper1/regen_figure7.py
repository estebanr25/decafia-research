"""
Regenerate figure7_bootstrap_intervals.png with correct CIs:
- roya: image-level CI only (secondary, dashed), cluster CI not shown
- coco: cluster CI (solid)
- minador: point estimate only, no CI (dagger footnote)
"""
import json, hashlib
from pathlib import Path
import numpy as np

REPO = Path("C:/Users/luise/temp/decafia-research")
RESULTS_DIR = REPO / "paper1/results"
FIGURES_DIR = REPO / "paper1/figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load data from JSON
d = json.load((RESULTS_DIR / "metrics_final.json").open())
p4 = d['phase4']['test_set_full']
bs = p4['bootstrap_map50_ci95']
mp = p4['map50_per_class_model_val']

# Values
classes = ['roya', 'coco', 'minador']
map50s = [mp['roya'], mp['coco'], mp['minador']]

coco_ci_lo = bs['per_class_cluster']['coco']['lo']
coco_ci_hi = bs['per_class_cluster']['coco']['hi']
roya_img_lo = bs['per_class_image_level']['roya']['lo']
roya_img_hi = bs['per_class_image_level']['roya']['hi']

# Class labels for display
class_labels = ['roya\n(rust)', 'coco\n(weevil)', 'minador†\n(leaf-miner)']

fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.array([0, 1, 2])
colors = ['#d62728', '#2ca02c', '#ff7f0e']

# Plot bars
bars = ax.bar(x, map50s, color=colors, alpha=0.75, width=0.5, zorder=3)

# coco: cluster CI (solid error bar)
coco_lo_err = mp['coco'] - coco_ci_lo
coco_hi_err = coco_ci_hi - mp['coco']
ax.errorbar(1, mp['coco'], yerr=[[coco_lo_err], [coco_hi_err]],
            fmt='none', color='black', linewidth=2, capsize=8, capthick=2,
            zorder=5, label='Cluster CI (95%)')

# roya: image-level CI (dashed error bar, different color to signal secondary)
roya_lo_err = mp['roya'] - roya_img_lo
roya_hi_err = roya_img_hi - mp['roya']
ax.errorbar(0, mp['roya'], yerr=[[roya_lo_err], [roya_hi_err]],
            fmt='none', color='#555555', linewidth=2, capsize=8, capthick=2,
            linestyle='dashed', zorder=5, label='Image-level CI (95%, secondary)')

# No CI for minador
ax.text(2, mp['minador'] + 0.012, 'No CI†', ha='center', va='bottom', fontsize=9, color='#555555')

ax.set_xticks(x)
ax.set_xticklabels(class_labels, fontsize=11)
ax.set_ylabel('mAP@50', fontsize=12)
ax.set_ylim(0.70, 1.05)
ax.set_title('Per-class mAP@50 with 95% confidence intervals\n(decafia_grouped_v1 on split_grouped_v1 test, n=356)', fontsize=11)
ax.yaxis.grid(True, alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Value labels above each bar
for i, (xi, v) in enumerate(zip(x, map50s)):
    offset = -0.03 if i == 2 else 0.005
    ax.text(xi, v + offset, f'{v:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Footnote
footnote = (
    '† minador: test images share group membership with training images through verified\n'
    '  transformed copies; independent-leaf evaluation not possible (CI not shown).\n'
    'Roya CI: cluster CI unreportable (one group holds 53% of instances); image-level shown as secondary.'
)
fig.text(0.02, -0.08, footnote, fontsize=8, color='#444444',
         verticalalignment='top', wrap=True)

ax.legend(fontsize=9, loc='lower right')

plt.tight_layout(rect=[0, 0.08, 1, 1])
out_path = FIGURES_DIR / "figure7_bootstrap_intervals.png"
plt.savefig(out_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: {out_path}")

# Update sidecar JSON
metrics_hash = hashlib.sha256((RESULTS_DIR / "metrics_final.json").read_bytes()).hexdigest()
sidecar = {
    "figure": "figure7_bootstrap_intervals",
    "plotted_values": {
        "map50_per_class": {
            "roya": round(mp['roya'], 4),
            "coco": round(mp['coco'], 4),
            "minador": round(mp['minador'], 4)
        },
        "ci95_coco_cluster": {"lo": coco_ci_lo, "hi": coco_ci_hi},
        "ci95_roya_image_level_secondary": {"lo": roya_img_lo, "hi": roya_img_hi},
        "ci95_minador": "NOT REPORTED (contaminated)"
    },
    "notes": {
        "roya": "Cluster CI unreportable (53.1% in one cluster). Image-level CI shown as secondary.",
        "coco": "Cluster CI reported (37.2% max cluster).",
        "minador": "No CI shown. Test images contaminated; independent evaluation not possible."
    },
    "input_hashes": {"metrics_final.json": metrics_hash},
    "generated": "2026-11-18"
}
sidecar_path = FIGURES_DIR / "figure7_bootstrap_intervals_sidecar.json"
sidecar_path.write_text(json.dumps(sidecar, indent=2))
print(f"Sidecar updated: {sidecar_path}")
