"""
evaluate_clean.py — DECAFIA clean_v1 evaluation on the TEST split.

Run from the repository root:
    python scripts/evaluate_clean.py [--root /path/to/repo] [--model /path/to/best.pt]

Outputs to results/clean_v1/:
    - per-class metrics table (P, R, mAP50, mAP50-95, F1)
    - normalized confusion matrix (300 dpi)
    - PR curves per class (300 dpi)
    - 4-panel training curves (300 dpi)
    - 4x4 grid of test predictions (300 dpi)
    - RESULTS.md

Dataset card assertions:
    - test images  : 349
    - test instances: 1,948
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
# Default: repo root = parent of this script's directory.
# Override with --root or --model if running from elsewhere.
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--root", type=Path, default=None,
                 help="Repository root (default: parent of this script)")
_ap.add_argument("--model", type=Path, default=None,
                 help="Path to decafia_clean_best.pt (default: <root>/models/decafia_clean_best.pt)")
_args, _ = _ap.parse_known_args()

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = _args.root.resolve() if _args.root else SCRIPT_DIR.parent
MODEL_PATH   = _args.model.resolve() if _args.model else PROJECT_ROOT / "models" / "decafia_clean_best.pt"
DATA_YAML    = PROJECT_ROOT / "dataset" / "decafia_clean" / "data.yaml"
RESULTS_DIR  = PROJECT_ROOT / "results" / "clean_v1"
RUNS_DIR     = PROJECT_ROOT / "runs" / "decafia_clean_v1"

CLASS_NAMES  = ["roya", "coco", "minador"]
EXPECTED_IMGS    = 349
EXPECTED_INSTS   = 1948
DPI = 300


def abort(msg):
    print(f"\n[ABORT] {msg}", file=sys.stderr)
    sys.exit(1)


# ── Dependency checks ─────────────────────────────────────────────────────────
try:
    import torch
except ImportError:
    abort("PyTorch not installed. See train_clean.py for install instructions.")

if not torch.cuda.is_available():
    abort("No CUDA GPU detected. Evaluation requires a CUDA GPU.")

gpu_name = torch.cuda.get_device_name(0)
props    = torch.cuda.get_device_properties(0)
cc_major, cc_minor = props.major, props.minor
this_cc  = f"sm_{cc_major}{cc_minor}"
vram_gb  = round(props.total_memory / 1024**3, 2)

supported_cc = torch.cuda.get_arch_list()
if this_cc not in supported_cc:
    abort(
        f"GPU {gpu_name} ({this_cc}) not supported by PyTorch {torch.__version__}.\n"
        "  pip install torch torchvision torchaudio "
        "--index-url https://download.pytorch.org/whl/cu128\n"
        "  pip install ultralytics"
    )

try:
    from ultralytics import YOLO
    import ultralytics
except ImportError:
    abort("ultralytics not installed. pip install ultralytics")

try:
    from PIL import Image as PILImage
except ImportError:
    abort("Pillow not installed. pip install pillow")

if not MODEL_PATH.exists():
    abort(
        f"Model not found: {MODEL_PATH}\n"
        "  Run train_clean.py first, or place decafia_clean_best.pt at the path above."
    )
if not DATA_YAML.exists():
    abort(f"data.yaml not found: {DATA_YAML}")

# ── Assert test split dimensions ──────────────────────────────────────────────
print("\nVerifying test split against dataset card...")
import yaml
with open(DATA_YAML, encoding="utf-8") as fh:
    data_cfg = yaml.safe_load(fh)

clean_root  = DATA_YAML.parent
test_img_dir = clean_root / "images" / "test"
test_lbl_dir = clean_root / "labels" / "test"

if not test_img_dir.exists():
    abort(f"Test image directory not found: {test_img_dir}")

actual_imgs = len(list(test_img_dir.iterdir()))
actual_insts = 0
for lbl in test_lbl_dir.iterdir():
    for line in lbl.read_text(encoding="utf-8").splitlines():
        if line.strip():
            actual_insts += 1

print(f"  Split used    : TEST")
print(f"  Image count   : {actual_imgs}  (expected {EXPECTED_IMGS})")
print(f"  Instance count: {actual_insts}  (expected {EXPECTED_INSTS})")

if actual_imgs != EXPECTED_IMGS:
    abort(
        f"Image count mismatch: found {actual_imgs}, expected {EXPECTED_IMGS}.\n"
        "  Dataset may have changed since the dataset card was written."
    )
if actual_insts != EXPECTED_INSTS:
    abort(
        f"Instance count mismatch: found {actual_insts}, expected {EXPECTED_INSTS}.\n"
        "  Dataset may have changed since the dataset card was written."
    )
print("  Both assertions passed. OK\n")

# ── Run evaluation ────────────────────────────────────────────────────────────
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print(f"Loading model: {MODEL_PATH}")
model = YOLO(str(MODEL_PATH))

print("Running validation on TEST split...")
t0 = time.time()
metrics = model.val(
    data    = str(DATA_YAML),
    split   = "test",
    imgsz   = 640,
    batch   = 16,
    workers = 0,
    device  = 0,
    verbose = True,
    plots   = False,   # we generate our own
)
eval_time = time.time() - t0

# ── Extract per-class metrics ─────────────────────────────────────────────────
#  metrics.box.p/r/f1/ap50/ap are arrays of shape [num_classes]
p_per_class    = metrics.box.p        # precision per class
r_per_class    = metrics.box.r        # recall per class
f1_per_class   = metrics.box.f1       # F1 per class
ap50_per_class = metrics.box.ap50     # AP@50 per class
ap_per_class   = metrics.box.ap       # AP@50-95 per class
map50_overall  = metrics.box.map50
map50_95       = metrics.box.map

print(f"\n{'='*65}")
print(f"  EVALUATION COMPLETE  ({eval_time:.1f}s)")
print(f"{'='*65}")
print(f"  Split          : TEST ({actual_imgs} images, {actual_insts} instances)")
print(f"  Overall mAP50  : {map50_overall:.4f}")
print(f"  Overall mAP50-95: {map50_95:.4f}")
print(f"\n  Per-class metrics:")
print(f"  {'Class':<12} {'P':>7} {'R':>7} {'F1':>7} {'mAP50':>8} {'mAP50-95':>10}")
print(f"  {'-'*54}")
for i, name in enumerate(CLASS_NAMES):
    print(f"  {name:<12} "
          f"{p_per_class[i]:>7.4f} "
          f"{r_per_class[i]:>7.4f} "
          f"{f1_per_class[i]:>7.4f} "
          f"{ap50_per_class[i]:>8.4f} "
          f"{ap_per_class[i]:>10.4f}")
print(f"  {'all':<12} "
      f"{'':>7} {'':>7} {'':>7} "
      f"{map50_overall:>8.4f} "
      f"{map50_95:>10.4f}")
print(f"{'='*65}\n")


# ── Figure helpers ────────────────────────────────────────────────────────────
COLORS = {"roya": "#E65100", "coco": "#1565C0", "minador": "#6A1B9A"}

def save_fig(fig, name):
    path = RESULTS_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")
    return path


# ── 1. Normalized confusion matrix ───────────────────────────────────────────
print("Generating confusion matrix...")
# ultralytics stores confusion matrix in metrics.confusion_matrix
cm_obj  = metrics.confusion_matrix
cm_raw  = np.array(cm_obj.matrix, dtype=float)   # shape [nc+1, nc+1] with background

# Slice to [nc, nc] (drop background row/col)
nc = len(CLASS_NAMES)
cm = cm_raw[:nc, :nc]
# Normalize by row (true class)
row_sums = cm.sum(axis=1, keepdims=True)
cm_norm  = np.where(row_sums > 0, cm / row_sums, 0.0)

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm_norm, vmin=0, vmax=1, cmap="Blues")
fig.colorbar(im, ax=ax, fraction=0.046)
ax.set_xticks(range(nc))
ax.set_yticks(range(nc))
ax.set_xticklabels(CLASS_NAMES, fontsize=10)
ax.set_yticklabels(CLASS_NAMES, fontsize=10)
ax.set_xlabel("Predicted", fontsize=11)
ax.set_ylabel("True", fontsize=11)
ax.set_title("Normalized Confusion Matrix — TEST split", fontsize=12)
for i in range(nc):
    for j in range(nc):
        val = cm_norm[i, j]
        ax.text(j, i, f"{val:.2f}",
                ha="center", va="center", fontsize=10,
                color="white" if val > 0.5 else "black")
fig.tight_layout()
save_fig(fig, "confusion_matrix_normalized.png")


# ── 2. PR curves per class ────────────────────────────────────────────────────
print("Generating PR curves...")
# Extract from metrics.curves (tuple of arrays) if available
# ultralytics >= 8.1 exposes metrics.box.curves_results
# Fall back to re-running val with plots=True into a temp dir and copying

# Try native curve data first
curves_ok = False
try:
    # px, py, names, ap = metrics.box.curves_results  (newer ultralytics)
    px, py_all, names_curves, ap_curves = metrics.box.curves_results
    # py_all shape: [nc, n_thresh]; px: [n_thresh]
    fig, ax = plt.subplots(figsize=(7, 5))
    for i, name in enumerate(CLASS_NAMES):
        ap50_val = ap50_per_class[i]
        ax.plot(px, py_all[i], color=COLORS[name], linewidth=1.8,
                label=f"{name} (AP50={ap50_val:.3f})")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_title("Precision-Recall Curves — TEST split", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "pr_curves.png")
    curves_ok = True
except Exception as e:
    print(f"  Note: native curve data not available ({e}). "
          "Re-running val with plots=True to extract curves.")

if not curves_ok:
    import tempfile, shutil
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        model.val(
            data=str(DATA_YAML), split="test", imgsz=640,
            batch=16, workers=0, device=0, plots=True,
            project=str(tmp_path), name="pr_tmp", verbose=False,
        )
        pr_src = tmp_path / "pr_tmp" / "BoxPR_curve.png"
        if pr_src.exists():
            dst = RESULTS_DIR / "pr_curves.png"
            shutil.copy2(pr_src, dst)
            print(f"  Saved: pr_curves.png  (copied from ultralytics output)")
        else:
            print("  WARNING: PR curve not available.")


# ── 3. 4-panel training curves ────────────────────────────────────────────────
print("Generating training curves...")
results_csv = RUNS_DIR / "results.csv"
if not results_csv.exists():
    # Search for it
    candidates = list((PROJECT_ROOT / "runs").rglob("decafia_clean_v1/results.csv"))
    if candidates:
        results_csv = candidates[0]

if results_csv.exists():
    with open(results_csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        r_rows = list(reader)

    # Strip whitespace from keys
    r_rows = [{k.strip(): v.strip() for k, v in row.items()} for row in r_rows]

    def get_col(rows, fragments):
        for frag in fragments:
            key = next((k for k in rows[0] if frag in k), None)
            if key:
                return [float(r[key]) for r in rows if r[key]]
        return None

    epochs_col    = get_col(r_rows, ["epoch", "Epoch"])
    epochs_x      = epochs_col if epochs_col else list(range(1, len(r_rows) + 1))

    box_loss_t    = get_col(r_rows, ["train/box_loss"])
    cls_loss_t    = get_col(r_rows, ["train/cls_loss"])
    box_loss_v    = get_col(r_rows, ["val/box_loss"])
    map50_v       = get_col(r_rows, ["metrics/mAP50(B)"])

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    panels = [
        (axes[0, 0], box_loss_t, "Train Box Loss",  "#0277BD"),
        (axes[0, 1], cls_loss_t, "Train Cls Loss",  "#2E7D32"),
        (axes[1, 0], box_loss_v, "Val Box Loss",    "#E65100"),
        (axes[1, 1], map50_v,    "Val mAP50",       "#6A1B9A"),
    ]
    for ax, data, title, color in panels:
        if data:
            ax.plot(epochs_x[:len(data)], data, color=color, linewidth=1.5)
        else:
            ax.text(0.5, 0.5, "N/A", ha="center", va="center",
                    transform=ax.transAxes, fontsize=12, color="grey")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Epoch", fontsize=9)
        ax.grid(True, alpha=0.25)
    fig.suptitle("Training Curves — decafia_clean_v1", fontsize=13, y=1.01)
    fig.tight_layout()
    save_fig(fig, "training_curves.png")
else:
    print(f"  WARNING: results.csv not found at {results_csv} — training curves skipped.")


# ── 4. 4x4 grid of test predictions ─────────────────────────────────────────
print("Generating 4x4 prediction grid...")
import random as _random
_random.seed(42)

test_images = sorted(test_img_dir.iterdir())
sample_imgs = _random.sample(test_images, min(16, len(test_images)))

CMAP = [COLORS["roya"], COLORS["coco"], COLORS["minador"]]

fig, axes = plt.subplots(4, 4, figsize=(14, 14))
axes_flat  = axes.flatten()

for idx, img_path in enumerate(sample_imgs):
    ax = axes_flat[idx]

    # Run inference on single image
    preds = model.predict(
        source  = str(img_path),
        imgsz   = 640,
        conf    = 0.25,
        workers = 0,
        device  = 0,
        verbose = False,
    )
    result = preds[0]
    img_np = np.array(PILImage.open(img_path).convert("RGB"))
    ax.imshow(img_np)

    if result.boxes is not None and len(result.boxes):
        boxes  = result.boxes.xyxy.cpu().numpy()
        confs  = result.boxes.conf.cpu().numpy()
        labels = result.boxes.cls.cpu().numpy().astype(int)
        ih, iw = img_np.shape[:2]
        # Scale boxes if model resized the image
        orig_h, orig_w = result.orig_shape
        sx = iw / orig_w
        sy = ih / orig_h
        for box, conf, cid in zip(boxes, confs, labels):
            x1, y1, x2, y2 = box
            x1 *= sx; x2 *= sx; y1 *= sy; y2 *= sy
            color = CMAP[cid] if cid < len(CMAP) else "#607D8B"
            rect  = patches.Rectangle(
                (x1, y1), x2 - x1, y2 - y1,
                linewidth=1.5, edgecolor=color, facecolor="none"
            )
            ax.add_patch(rect)
            name = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else str(cid)
            ax.text(x1, y1 - 3, f"{name} {conf:.2f}",
                    color="white", fontsize=5,
                    bbox=dict(facecolor=color, alpha=0.8, pad=1, linewidth=0))

    ax.axis("off")
    ax.set_title(img_path.stem[:22], fontsize=6, pad=2)

# Hide unused panels if < 16 images
for idx in range(len(sample_imgs), 16):
    axes_flat[idx].axis("off")

fig.suptitle("Test Split Predictions — decafia_clean_v1 (conf>=0.25)",
             fontsize=13, y=1.005)
fig.tight_layout()
save_fig(fig, "test_predictions_grid.png")


# ── 5. RESULTS.md ─────────────────────────────────────────────────────────────
print("Writing RESULTS.md...")
md_lines = []
M = md_lines.append

M("# Evaluation Results — decafia_clean_v1")
M("")
M(f"**Date:** 2026-09-11  ")
M(f"**Model:** `03_models/decafia_clean_best.pt`  ")
M(f"**Split:** TEST ({actual_imgs} images, {actual_insts} instances)  ")
M(f"**Dataset card assertions:** passed (349 images, 1,948 instances)")
M("")
M("## Per-Class Metrics")
M("")
M("| Class | Precision | Recall | F1 | mAP50 | mAP50-95 |")
M("|-------|----------:|-------:|---:|------:|---------:|")
for i, name in enumerate(CLASS_NAMES):
    M(f"| {name} "
      f"| {p_per_class[i]:.4f} "
      f"| {r_per_class[i]:.4f} "
      f"| {f1_per_class[i]:.4f} "
      f"| {ap50_per_class[i]:.4f} "
      f"| {ap_per_class[i]:.4f} |")
M(f"| **all** | | | | **{map50_overall:.4f}** | **{map50_95:.4f}** |")
M("")
M("## Outputs")
M("")
M("| File | Description |")
M("|------|-------------|")
M("| `confusion_matrix_normalized.png` | Row-normalized confusion matrix, TEST split |")
M("| `pr_curves.png` | Precision-Recall curves per class |")
M("| `training_curves.png` | 4-panel training history (box loss, cls loss, val loss, mAP50) |")
M("| `test_predictions_grid.png` | 4x4 grid of random test predictions (conf>=0.25) |")
M("")
M("## Notes")
M("")
M("- Minador annotations are 100% from Silva et al. (Brazil). "
  "Minador mAP measures cross-country generalisation, not Colombian field performance.")
M("- Coco annotations are 100% own-field (Socorro, Santander). "
  "Coco mAP is the most reliable field-performance indicator.")
M("- Roya is 60% own-field / 40% Silva et al.")
M("- Background images (empty labels) account for 1,113 of 2,315 images. "
  "Healthy leaves are detected as absence of predictions above threshold, not a separate class.")

(RESULTS_DIR / "RESULTS.md").write_text("\n".join(md_lines), encoding="utf-8")
print(f"  Saved: RESULTS.md")

print(f"\n{'='*65}")
print(f"  All outputs written to: {RESULTS_DIR}")
print(f"{'='*65}\n")
