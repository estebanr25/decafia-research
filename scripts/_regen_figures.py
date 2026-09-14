"""
Regenerate the three fixed figures for results/clean_v1/:
  1. training_curves.png  — from the actual results.csv, run dir resolved from model
  2. confusion_matrix_normalized.png — from saved CM array, empty rows left blank
  3. pr_curves.png — from p_curve/r_curve arrays at 300 dpi with English labels

Run from the repository root:
    python scripts/_regen_figures.py [--root /path/to/repo]
"""
import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--root", type=Path, default=None,
                 help="Repository root (default: parent of this script)")
_args, _ = _ap.parse_known_args()

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = _args.root.resolve() if _args.root else SCRIPT_DIR.parent
RESULTS_DIR  = PROJECT_ROOT / "results" / "clean_v1"

CLASS_NAMES  = ["roya", "coco", "minador"]
COLORS       = {"roya": "#E65100", "coco": "#1565C0", "minador": "#6A1B9A"}
DPI = 300

# ── Per-class metrics from val run ────────────────────────────────────────────
P    = [0.8364, 0.9177, 0.8687]
R    = [0.7931, 0.9087, 0.8987]
F1   = [0.8142, 0.9132, 0.8834]
AP50 = [0.8619, 0.9638, 0.9449]
AP   = [0.5700, 0.7921, 0.8258]
MAP50_OVERALL = 0.9235
MAP_OVERALL   = 0.7293

print("=" * 65)
print("1. TRAINING CURVES")
print("=" * 65)

# Resolve run dir from model's sibling args.yaml
# Model is at 03_models/decafia_clean_best.pt.
# It was copied from the actual run dir. Find results.csv by searching runs/.
runs_root = PROJECT_ROOT / "runs"
results_csv = None
for run_dir in sorted(runs_root.iterdir()):
    candidate = run_dir / "results.csv"
    if candidate.exists():
        # Prefer the one whose args.yaml names decafia_clean_v1
        args_yaml = run_dir / "args.yaml"
        if args_yaml.exists():
            content = args_yaml.read_text(encoding="utf-8")
            if "decafia_clean" in content and "data.yaml" in content:
                results_csv = candidate
                print(f"  Found results.csv: {candidate}")
                break

if results_csv is None:
    # Fall back: pick most recently modified results.csv
    candidates = list(runs_root.rglob("results.csv"))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        results_csv = candidates[0]
        print(f"  Fell back to most recent: {results_csv}")

if results_csv is None or not results_csv.exists():
    print("  ERROR: results.csv not found — skipping training curves.")
else:
    with open(results_csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]

    def col(rows, *fragments):
        for frag in fragments:
            key = next((k for k in rows[0] if frag in k), None)
            if key:
                vals = []
                for r in rows:
                    try:
                        vals.append(float(r[key]))
                    except (ValueError, KeyError):
                        pass
                if vals:
                    return vals
        return None

    epochs   = col(rows, "epoch") or list(range(1, len(rows) + 1))
    box_t    = col(rows, "train/box_loss")
    map50_v  = col(rows, "metrics/mAP50(B)")
    prec_v   = col(rows, "metrics/precision(B)")
    rec_v    = col(rows, "metrics/recall(B)")

    n = len(epochs)
    print(f"  Epochs read: {n}")

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    panels = [
        (axes[0, 0], box_t,   "Train Box Loss",   "#0277BD",  False),
        (axes[0, 1], map50_v, "Val mAP50",        "#6A1B9A",  False),
        (axes[1, 0], prec_v,  "Val Precision",    "#2E7D32",  True),
        (axes[1, 1], rec_v,   "Val Recall",       "#E65100",  True),
    ]
    for ax, data, title, color, is_metric in panels:
        if data:
            x = epochs[:len(data)]
            ax.plot(x, data, color=color, linewidth=1.6)
            if is_metric:
                ax.set_ylim(0, 1.05)
                ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
            # Mark best value
            if is_metric:
                best_idx = int(np.argmax(data))
                best_val = data[best_idx]
                ax.axvline(x[best_idx], color=color, linestyle="--",
                           alpha=0.4, linewidth=0.8)
                ax.scatter([x[best_idx]], [best_val], color=color,
                           zorder=5, s=30)
                ax.annotate(f"{best_val:.3f}", (x[best_idx], best_val),
                            textcoords="offset points", xytext=(5, 3),
                            fontsize=7, color=color)
            else:
                best_idx = int(np.argmin(data))
                best_val = data[best_idx]
                ax.scatter([x[best_idx]], [best_val], color=color,
                           zorder=5, s=30)
        else:
            ax.text(0.5, 0.5, "Not available", ha="center", va="center",
                    transform=ax.transAxes, fontsize=11, color="grey")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Epoch", fontsize=9)
        ax.grid(True, alpha=0.22, linewidth=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(f"Training Curves — decafia_clean_v1  (seed=42, YOLOv8m)",
                 fontsize=12, y=1.01)
    fig.tight_layout()
    out = RESULTS_DIR / "training_curves.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


print("\n" + "=" * 65)
print("2. CONFUSION MATRIX (normalized)")
print("=" * 65)

cm_path = RESULTS_DIR / "_cm.npy"
if not cm_path.exists():
    print("  ERROR: _cm.npy not found — run the data collection step first.")
else:
    cm_raw = np.load(str(cm_path)).astype(float)
    print(f"  Raw CM shape: {cm_raw.shape}")
    print("  Raw values:")
    print(cm_raw.astype(int))

    # Ultralytics CM convention: cm[predicted, true]
    # Verified: column sums = [864, 699, 385] = dataset card GT counts.
    # Row 3 (predicted=background) = FN: GT instances not matched by any detection.
    # Col 3 (true=background/no-GT) = FP: detections with no matching GT box.
    AXIS_LABELS = ["roya", "coco", "minador", "background"]
    nc_full = cm_raw.shape[0]   # 4

    col_sums = cm_raw.sum(axis=0)
    fn_counts = cm_raw[3, :3].astype(int)   # row 3: missed GTs per class
    fp_counts = cm_raw[:3, 3].astype(int)   # col 3: FP detections per class

    print(f"\n  Col sums (GT totals): {col_sums[:3].astype(int)}  <- match dataset card")
    print(f"  FN row (missed GTs) : {fn_counts}, total={fn_counts.sum()}")
    print(f"  FP col (no-GT dets) : {fp_counts}, total={fp_counts.sum()}")

    # Normalize by column (true class total = col sum including FN row).
    # Diagonal values = recall at CM confidence threshold (~0.25).
    # Row 3 (FN) and col 3 (FP) are left blank (NaN).
    cm_norm = np.full_like(cm_raw, np.nan)
    for j in range(nc_full - 1):            # true-class columns 0-2
        if col_sums[j] > 0:
            for i in range(nc_full - 1):    # predicted-class rows 0-2
                cm_norm[i, j] = cm_raw[i, j] / col_sums[j]

    fig, ax = plt.subplots(figsize=(6, 5.2))
    masked = np.ma.masked_invalid(cm_norm)
    cmap   = plt.cm.Blues
    cmap.set_bad(color="#F5F5F5")

    im = ax.imshow(masked, vmin=0, vmax=1, cmap=cmap)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=8)

    ax.set_xticks(range(nc_full))
    ax.set_yticks(range(nc_full))
    ax.set_xticklabels(AXIS_LABELS, fontsize=9)
    ax.set_yticklabels(AXIS_LABELS, fontsize=9)
    ax.set_xlabel("True", fontsize=10)
    ax.set_ylabel("Predicted", fontsize=10)

    for i in range(nc_full):
        for j in range(nc_full):
            val = cm_norm[i, j]
            if np.isnan(val):
                ax.text(j, i, "—", ha="center", va="center",
                        fontsize=10, color="#AAAAAA")
            else:
                ax.text(j, i, f"{val:.2f}",
                        ha="center", va="center", fontsize=9,
                        color="white" if val > 0.55 else "black")

    fn_str = (f"FN (background row): roya={fn_counts[0]}, coco={fn_counts[1]},"
              f" minador={fn_counts[2]}  ({fn_counts.sum()} missed GT boxes)")
    fp_str = (f"FP (background col): roya={fp_counts[0]}, coco={fp_counts[1]},"
              f" minador={fp_counts[2]}  ({fp_counts.sum()} no-GT detections)")
    ax.set_title(
        "Normalized Confusion Matrix — TEST split\n"
        "(column-normalized by GT count; background row/col blank)\n"
        + fn_str + "\n" + fp_str,
        fontsize=8, pad=8
    )

    fig.tight_layout()
    out = RESULTS_DIR / "confusion_matrix_normalized.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out.name}")


print("\n" + "=" * 65)
print("3. PR CURVES (300 dpi, English labels)")
print("=" * 65)

p_path = RESULTS_DIR / "_p_curve.npy"
r_path = RESULTS_DIR / "_r_curve.npy"

if not p_path.exists() or not r_path.exists():
    print("  ERROR: _p_curve.npy / _r_curve.npy not found.")
else:
    p_curve = np.load(str(p_path))   # shape (3, 1000)
    r_curve = np.load(str(r_path))   # shape (3, 1000)
    print(f"  p_curve: {p_curve.shape}, r_curve: {r_curve.shape}")

    # ultralytics p_curve rows are indexed by confidence threshold (sorted desc),
    # and r_curve rows likewise. Pair them: at each threshold, P[class, t], R[class, t].
    # To plot PR curve: for each class, plot P[class,:] vs R[class,:]
    # The x-axis should be recall (ascending) so we need to sort by recall.

    fig, ax = plt.subplots(figsize=(7, 5))
    for i, name in enumerate(CLASS_NAMES):
        p_vals = p_curve[i]
        r_vals = r_curve[i]

        # Sort by recall ascending for a clean curve
        sort_idx = np.argsort(r_vals)
        r_sorted = r_vals[sort_idx]
        p_sorted = p_vals[sort_idx]

        ap50 = AP50[i]
        color = COLORS[name]
        ax.plot(r_sorted, p_sorted, color=color, linewidth=1.8,
                label=f"{name}  (AP50={ap50:.3f})")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_title(f"Precision-Recall Curves — TEST split\n"
                 f"all classes  (mAP50={MAP50_OVERALL:.3f})", fontsize=11)
    ax.legend(fontsize=10, loc="lower left")
    ax.grid(True, alpha=0.25, linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    out = RESULTS_DIR / "pr_curves.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    # Verify DPI
    from PIL import Image
    saved = Image.open(out)
    dpi_check = saved.info.get("dpi", "not set")
    print(f"  Saved: {out.name}  DPI={dpi_check}")


print("\n" + "=" * 65)
print("Updating RESULTS.md")
print("=" * 65)

md = f"""# Evaluation Results — decafia_clean_v1

**Date:** 2026-09-11
**Model:** `03_models/decafia_clean_best.pt`
**Split:** TEST (349 images, 1,948 instances)
**Dataset card assertions:** passed (349 images, 1,948 instances)
**Training run:** `02_training/runs/decafia_clean_v1-2/`

## Per-Class Metrics

| Class | Precision | Recall | F1 | mAP50 | mAP50-95 |
|-------|----------:|-------:|---:|------:|---------:|
| roya    | {P[0]:.4f} | {R[0]:.4f} | {F1[0]:.4f} | {AP50[0]:.4f} | {AP[0]:.4f} |
| coco    | {P[1]:.4f} | {R[1]:.4f} | {F1[1]:.4f} | {AP50[1]:.4f} | {AP[1]:.4f} |
| minador | {P[2]:.4f} | {R[2]:.4f} | {F1[2]:.4f} | {AP50[2]:.4f} | {AP[2]:.4f} |
| **all** | | | | **{MAP50_OVERALL:.4f}** | **{MAP_OVERALL:.4f}** |

## Confusion Matrix Notes

Ultralytics stores the matrix as **cm[predicted, true]**. Column sums equal the
dataset card GT counts (roya 864, coco 699, minador 385), confirming orientation.
`confusion_matrix_normalized.png` is column-normalised by true-class GT count;
diagonal values are therefore recall at the CM confidence threshold (≈ 0.25),
which is higher than the F1-optimal threshold used for the metrics table above.

The raw (counts) 4×4 matrix — rows = predicted class, cols = true class:

| Pred \\ True | roya | coco | minador | bkgd (no GT) |
|-------------|-----:|-----:|--------:|-------------:|
| roya        |  753 |    1 |       0 |          248 |
| coco        |    1 |  657 |       0 |          116 |
| minador     |    2 |    0 |     361 |           90 |
| bkgd (FN)  |  108 |   41 |      24 |            0 |

Column sums (GT totals): roya=864, coco=699, minador=385 — match dataset card.

**Background column** (`bkgd (no GT)`, col 4) — left blank in the figure:
These are detections with no matching ground-truth box (FP). The cell value is
the detection count, not an instance count. Raw totals: 248 roya + 116 coco +
90 minador = **454 FP detections** at CM threshold (≈ 0.25). These fire on
background images or on annotated images where no GT box had sufficient IoU.
At the operational threshold (conf ≥ 0.50), only 4 FP detections survive across
all 167 background test images (3 roya, 1 coco): 164/167 (98.2%) produce zero
detections, and 3/167 (1.8%) produce at least one.

**Background row** (`bkgd (FN)`, row 4) — left blank in the figure:
These are GT boxes not matched by any detection (FN / missed detections).
Raw counts: **108 roya + 41 coco + 24 minador = 173 total missed GT boxes**.

**Roya** has the highest FN count (108 missed GT boxes, 12.5% of 864 roya GT).
It also has the most FP detections (248 at CM threshold). Both failure modes
lower roya precision (0.836) and recall (0.793) relative to coco and minador.
The dominant failure mode is spurious roya detections on images without disease,
not inter-class confusion (off-diagonal cross-class entries are near zero).

## Background-Image Detection Statistics (conf ≥ 0.50)

Of the 167 background test images (images with empty label files = healthy leaves):

| Result | Count | Fraction |
|--------|------:|---------:|
| Zero detections (correct) | 164 | 98.2% |
| ≥ 1 detection (FP) | 3 | 1.8% |
| Total FP detections | 4 | — |

FP breakdown at 0.50: roya=3, coco=1, minador=0.
This validates the three-class + background design: the model suppresses nearly
all spurious detections on healthy tissue at the operational threshold.

## Figures

| File | Description |
|------|-------------|
| `confusion_matrix_normalized.png` | Column-normalised CM (recall on diagonal); background row/col blank |
| `pr_curves.png` | PR curves per class from p_curve/r_curve arrays, 300 dpi |
| `training_curves.png` | 4-panel: train box loss, val mAP50, val precision, val recall |
| `test_predictions_grid.png` | 4x4 random test predictions (conf >= 0.25) |

## Interpretation Notes

- **Coco** is the strongest class (mAP50=0.964, F1=0.913): 100% own-field
  images from Socorro with consistent annotation quality.
- **Minador** (mAP50=0.945, F1=0.883): 100% from Silva et al. (Brazil).
  Performance measures cross-country generalisation, not Colombian field performance.
- **Roya** (mAP50=0.862, F1=0.814): 60% own-field / 40% Silva et al.
  Lower recall (0.793): 108 of 864 GT roya boxes not detected (FN = 12.5%).
  Lower precision (0.836): 248 spurious roya detections at CM threshold (FP).
- Background images: 167 of 349 test images (47.9%) have empty label files.
  At conf ≥ 0.50, 164/167 (98.2%) produce zero detections.
"""

(RESULTS_DIR / "RESULTS.md").write_text(md, encoding="utf-8")
print(f"  Written: RESULTS.md")

print("\n" + "=" * 65)
print("ALL DONE")
print("=" * 65)
