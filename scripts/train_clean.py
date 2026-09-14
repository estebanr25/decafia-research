"""
train_clean.py — DECAFIA clean_v1 training script.

Run from the DECAFIA_v2 root directory:
    python 02_training/scripts/train_clean.py

Requirements:
    ultralytics >= 8.3
    PyTorch     >= 2.7  (RTX 5070 / Blackwell sm_120 requires >=2.7 + CUDA 12.8)
    CUDA        >= 12.8

If your 'ia' conda env has PyTorch 2.5.x, install a compatible version:
    conda activate ia
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    pip install ultralytics
"""

import argparse
import os
import random
import shutil
import sys
import time
from pathlib import Path

# ── Resolve project root ──────────────────────────────────────────────────────
# Default: one level above this script (repo root when script is at scripts/).
# Override with --root /path/to/repo if running from elsewhere.
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--root", type=Path, default=None,
                 help="Repository root (default: parent of this script)")
_args, _ = _ap.parse_known_args()

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = _args.root.resolve() if _args.root else SCRIPT_DIR.parent
CONFIG_PATH  = PROJECT_ROOT / "configs" / "clean_v1.yaml"
MODEL_SRC    = PROJECT_ROOT / "models" / "checkpoints" / "yolov8m.pt"
MODELS_DIR   = PROJECT_ROOT / "models"

# ── Dependency checks before any heavy import ─────────────────────────────────

def abort(msg):
    print(f"\n[ABORT] {msg}", file=sys.stderr)
    sys.exit(1)


# torch
try:
    import torch
except ImportError:
    abort(
        "PyTorch is not installed in this Python environment.\n"
        "  conda activate ia\n"
        "  pip install torch torchvision torchaudio "
        "--index-url https://download.pytorch.org/whl/cu128"
    )

# GPU presence
if not torch.cuda.is_available():
    abort(
        "No CUDA GPU detected. Training requires a CUDA-capable GPU.\n"
        "This script will NEVER fall back to CPU."
    )

# Compute-capability compatibility check
gpu_name  = torch.cuda.get_device_name(0)
props     = torch.cuda.get_device_properties(0)
cc_major  = props.major
cc_minor  = props.minor
vram_gb   = round(props.total_memory / 1024**3, 2)

print(f"\n{'='*65}")
print(f"  GPU  : {gpu_name}")
print(f"  VRAM : {vram_gb} GB")
print(f"  CC   : sm_{cc_major}{cc_minor}")
print(f"  PyTorch : {torch.__version__}  (CUDA build: {torch.version.cuda})")
print(f"{'='*65}\n")

# Check that this GPU's compute capability is in PyTorch's supported set.
# PyTorch 2.5 tops out at sm_90; Blackwell (RTX 50xx) needs sm_120 -> PT>=2.7
supported_cc = torch.cuda.get_arch_list()           # e.g. ['sm_50', 'sm_60', ...]
this_cc      = f"sm_{cc_major}{cc_minor}"
if this_cc not in supported_cc:
    abort(
        f"Your GPU ({gpu_name}, {this_cc}) is NOT supported by the installed "
        f"PyTorch {torch.__version__}.\n"
        f"  Supported architectures: {supported_cc}\n\n"
        f"  Fix: install PyTorch >= 2.7 with CUDA 12.8 support:\n"
        f"    conda activate ia\n"
        f"    pip install torch torchvision torchaudio "
        f"--index-url https://download.pytorch.org/whl/cu128\n"
        f"    pip install ultralytics\n"
        f"  Then rerun this script."
    )

# ultralytics
try:
    from ultralytics import YOLO
    import ultralytics
    print(f"  ultralytics : {ultralytics.__version__}")
except ImportError:
    abort(
        "ultralytics is not installed.\n"
        "    pip install ultralytics"
    )

# Config and model files
if not CONFIG_PATH.exists():
    abort(f"Config not found: {CONFIG_PATH}")
if not MODEL_SRC.exists():
    abort(
        f"Base model not found: {MODEL_SRC}\n"
        "  Place yolov8m.pt at 03_models/checkpoints/yolov8m.pt\n"
        "  or run: python -c \"from ultralytics import YOLO; YOLO('yolov8m.pt')\""
    )

# ── Seed everything ───────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
try:
    import numpy as np
    np.random.seed(SEED)
except ImportError:
    pass
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
os.environ["PYTHONHASHSEED"] = str(SEED)
print(f"  Seeds set to {SEED} (random, numpy, torch, cuda)\n")

# ── Load config ───────────────────────────────────────────────────────────────
import yaml
with open(CONFIG_PATH, encoding="utf-8") as fh:
    cfg = yaml.safe_load(fh)

print(f"  Config : {CONFIG_PATH}")
print(f"  Model  : {MODEL_SRC}")
print(f"  Data   : {cfg.get('data')}")
print(f"  Epochs : {cfg.get('epochs')}  Batch: {cfg.get('batch')}  "
      f"imgsz: {cfg.get('imgsz')}\n")

# Resolve data path relative to project root
data_yaml = PROJECT_ROOT / cfg["data"]
if not data_yaml.exists():
    abort(f"data.yaml not found: {data_yaml}")

# ── Train ─────────────────────────────────────────────────────────────────────
model = YOLO(str(MODEL_SRC))

t_start = time.time()

results = model.train(
    data          = str(data_yaml),
    epochs        = int(cfg["epochs"]),
    patience      = int(cfg["patience"]),
    batch         = int(cfg["batch"]),
    imgsz         = int(cfg["imgsz"]),
    optimizer     = cfg["optimizer"],
    amp           = bool(cfg["amp"]),
    workers       = 0,                       # MANDATORY on Windows
    seed          = SEED,
    lr0           = float(cfg["lr0"]),
    lrf           = float(cfg["lrf"]),
    momentum      = float(cfg["momentum"]),
    weight_decay  = float(cfg["weight_decay"]),
    warmup_epochs = float(cfg["warmup_epochs"]),
    warmup_momentum = float(cfg.get("warmup_momentum", 0.8)),
    warmup_bias_lr  = float(cfg.get("warmup_bias_lr", 0.1)),
    hsv_h         = float(cfg["hsv_h"]),
    hsv_s         = float(cfg["hsv_s"]),
    hsv_v         = float(cfg["hsv_v"]),
    degrees       = float(cfg["degrees"]),
    translate     = float(cfg["translate"]),
    scale         = float(cfg["scale"]),
    flipud        = float(cfg["flipud"]),
    fliplr        = float(cfg["fliplr"]),
    mosaic        = float(cfg["mosaic"]),
    mixup         = float(cfg["mixup"]),
    close_mosaic  = int(cfg["close_mosaic"]),
    project       = str(PROJECT_ROOT / "runs"),
    name          = "decafia_clean_v1",
    exist_ok      = False,
    save          = True,
    save_period   = -1,
    plots         = True,
    verbose       = True,
    device        = 0,
)

elapsed = time.time() - t_start
h, rem  = divmod(int(elapsed), 3600)
m, s    = divmod(rem, 60)

# ── Post-training report ──────────────────────────────────────────────────────
run_dir   = Path(results.save_dir)
best_pt   = run_dir / "weights" / "best.pt"

# Read best mAP50 and epoch from results.csv
best_map50  = None
best_epoch  = None
results_csv = run_dir / "results.csv"
if results_csv.exists():
    import csv
    with open(results_csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows   = list(reader)
    # header keys have leading spaces in ultralytics CSV
    map50_key = next((k for k in rows[0] if "mAP50" in k and "95" not in k), None)
    if map50_key:
        best_row   = max(rows, key=lambda r: float(r[map50_key].strip()))
        best_map50 = float(best_row[map50_key].strip())
        epoch_key  = next((k for k in rows[0] if "epoch" in k.lower()), None)
        if epoch_key:
            best_epoch = int(float(best_row[epoch_key].strip()))

print(f"\n{'='*65}")
print(f"  TRAINING COMPLETE")
print(f"{'='*65}")
print(f"  Wall-clock time : {h}h {m}m {s}s")
if best_map50 is not None:
    print(f"  Best mAP50      : {best_map50:.4f}")
if best_epoch is not None:
    print(f"  Best epoch      : {best_epoch}")
print(f"  Run directory   : {run_dir}")
print(f"  best.pt         : {best_pt}")

# ── Copy best.pt to models/ ───────────────────────────────────────────────────
dest_pt = MODELS_DIR / "decafia_clean_best.pt"
if best_pt.exists():
    shutil.copy2(best_pt, dest_pt)
    print(f"  Copied to       : {dest_pt}")
else:
    print(f"  WARNING: best.pt not found at {best_pt} — copy skipped.")

print(f"{'='*65}\n")
