"""
Phase 3B: Bound the effect (Path B)
SESSION_SPLIT_V2 - DECAFIA Paper 1

Builds union exclusion list from v1 test images with merged-tier copies in train/val.
Evaluates decafia_grouped_v1 on:
  1. Full v1 test set
  2. Filtered test set (excluding contaminated images)
Reports metrics and background false-alarm rate at conf 0.50.
NEVER evaluates v1 model on v2 test set (Hard Rule 4).
"""

import json, sys, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict

REPO         = Path("C:/Users/luise/temp/decafia-research")
SPLIT_V2_DIR = REPO / "split_v2"
DATASET_ROOT = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
V1_MODEL     = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_grouped_v1/weights/best.pt")
V1_DATA_YAML = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1/data_grouped_v1.yaml")
V1_TEST_TXT  = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1/test.txt")

PROGRESS_FILE = SPLIT_V2_DIR / "PROGRESS.md"
PAPER1_DIR    = REPO / "paper1"
PAPER1_DIR.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)

def update_progress(**kwargs):
    existing = {}
    if PROGRESS_FILE.exists():
        for line in PROGRESS_FILE.read_text().splitlines():
            if line.startswith("- "):
                k, _, v = line[2:].partition(": ")
                existing[k] = v
    existing.update(kwargs)
    lines = ["# PROGRESS.md\n", f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
    for k, v in existing.items():
        lines.append(f"- {k}: {v}\n")
    PROGRESS_FILE.write_text("".join(lines))

update_progress(**{"Phase 3B - bound effect": "in_progress"})
log("=== Phase 3B: Bound the effect (Path B) ===")

# ── 1. Load copy pairs and v1 test set ────────────────────────────────────────
copy_pairs = pd.read_csv(SPLIT_V2_DIR / "copy_pairs.csv")
merged = copy_pairs[copy_pairs["decision"] == "merge"].copy()

# v1 test stems (from split_grouped_v1/test.txt - these contain image paths)
v1_test_stems = set()
with open(V1_TEST_TXT) as f:
    for line in f:
        line = line.strip()
        if line:
            # e.g. "/path/to/images/test/STEM.jpg" or "images/test/STEM.jpg"
            stem = Path(line).stem
            v1_test_stems.add(stem)
log(f"v1 test stems: {len(v1_test_stems)}")

# ── 2. Build exclusion list ───────────────────────────────────────────────────
log("\nBuilding exclusion list...")

# Every v1 test image that has a merged-tier pair with an image in train
# and separately in val
excluded_by_train = set()
excluded_by_val   = set()
excluded_all      = set()

for _, row in merged.iterrows():
    a, b   = row["stem_a"], row["stem_b"]
    sa, sb = row["split_a"], row["split_b"]

    # Is one side in test and the other in train/val?
    if a in v1_test_stems:
        test_stem = a
        other_split = sb
    elif b in v1_test_stems:
        test_stem = b
        other_split = sa
    else:
        continue

    excluded_all.add(test_stem)
    if other_split == "train":
        excluded_by_train.add(test_stem)
    elif other_split == "val":
        excluded_by_val.add(test_stem)

excluded_only_val = excluded_by_val - excluded_by_train  # in val but not train

log(f"Excluded test images (any copy): {len(excluded_all)}")
log(f"  with copy in train: {len(excluded_by_train)}")
log(f"  with copy only in val: {len(excluded_only_val)}")

# Write exclusion list
excl_df = pd.DataFrame({
    "stem": sorted(excluded_all),
    "has_train_copy": [s in excluded_by_train for s in sorted(excluded_all)],
    "has_val_copy":   [s in excluded_by_val   for s in sorted(excluded_all)],
})
excl_df.to_csv(SPLIT_V2_DIR / "v1_test_exclusion_list.csv", index=False)
log(f"Exclusion list saved: {len(excl_df)} images")

# ── 3. Build filtered test split file ────────────────────────────────────────
log("\nBuilding filtered test split file...")
filtered_lines = []
with open(V1_TEST_TXT) as f:
    for line in f:
        stem = Path(line.strip()).stem
        if stem not in excluded_all:
            filtered_lines.append(line.rstrip())

FILTERED_TEST_TXT = SPLIT_V2_DIR / "v1_test_filtered.txt"
FILTERED_TEST_TXT.write_text("\n".join(filtered_lines) + "\n")
log(f"Filtered test: {len(filtered_lines)} images (from {len(v1_test_stems)}, excluded {len(excluded_all)})")

# SHA-256 of model
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

model_sha256 = sha256_file(V1_MODEL)
log(f"v1 model SHA-256: {model_sha256}")

# ── 4. Build data YAMLs for evaluation ───────────────────────────────────────
# Full v1 test - use existing yaml but we'll eval with split='test'
# Filtered test - new yaml pointing to filtered test txt

# We'll create a data yaml for filtered evaluation
abs_filtered = FILTERED_TEST_TXT.resolve()
abs_v1_test  = V1_TEST_TXT.resolve()

filtered_yaml = f"""# DECAFIA v1 filtered test evaluation yaml (Path B)
# WARNING: This is for sensitivity measurement only. The two test sets differ.
# Full test: {len(v1_test_stems)} images; Filtered: {len(filtered_lines)} images
# Excluded: {len(excluded_all)} images with merged-tier copies in train ({len(excluded_by_train)}) or val-only ({len(excluded_only_val)})
path: {DATASET_ROOT}
train: {abs_v1_test}
val:   {abs_v1_test}
test:  {abs_filtered}
nc: 3
names:
  0: roya
  1: coco
  2: minador
"""
filtered_yaml_path = SPLIT_V2_DIR / "data_v1_filtered_test.yaml"
filtered_yaml_path.write_text(filtered_yaml)
log(f"Filtered test YAML written: {filtered_yaml_path}")

# ── 5. Run evaluation on FULL v1 test set ────────────────────────────────────
log("\n=== Evaluating v1 model on FULL v1 test set ===")
update_progress(**{"Phase 3B - eval full v1 test": "in_progress"})

from ultralytics import YOLO
import torch

device = "0" if torch.cuda.is_available() else "cpu"
log(f"Device: {device}")

model = YOLO(str(V1_MODEL))

# Evaluate on full v1 test
results_full = model.val(
    data=str(V1_DATA_YAML),
    split="test",
    conf=0.001,     # low conf to get full PR curve data
    iou=0.6,
    device=device,
    workers=0,
    verbose=True,
    save_json=False,
    plots=False,
    name="v1_full_test",
    project=str(SPLIT_V2_DIR / "runs"),
    exist_ok=True,
)

log("Full test evaluation complete.")
update_progress(**{"Phase 3B - eval full v1 test": "done"})

# Extract metrics
def extract_metrics(results, label):
    """Extract key metrics from YOLO val results."""
    maps  = results.maps   # per-class mAP50-95
    map50 = float(results.results_dict.get("metrics/mAP50(B)", results.box.map50))
    map95 = float(results.results_dict.get("metrics/mAP50-95(B)", results.box.map))
    # Per-class mAP50
    map50_per_class = results.box.ap50.tolist() if hasattr(results.box, "ap50") else []
    map95_per_class = results.box.ap.tolist()   if hasattr(results.box, "ap")   else []
    names = results.names if hasattr(results, "names") else {0: "roya", 1: "coco", 2: "minador"}
    metrics = {
        "label": label,
        "map50_overall": round(map50, 6),
        "map50_95_overall": round(map95, 6),
        "map50_per_class": {str(names[i]): round(v, 6) for i, v in enumerate(map50_per_class)},
        "map50_95_per_class": {str(names[i]): round(v, 6) for i, v in enumerate(map95_per_class)},
    }
    # Precision, Recall, F1 at conf 0.50 from results_dict if available
    for k in results.results_dict:
        log(f"  results_dict key: {k} = {results.results_dict[k]}")
    return metrics

metrics_full = extract_metrics(results_full, "v1_full_test")
log(f"\nFull test metrics: {metrics_full}")

# ── 6. Run evaluation on FILTERED v1 test set ────────────────────────────────
log("\n=== Evaluating v1 model on FILTERED v1 test set ===")
update_progress(**{"Phase 3B - eval filtered v1 test": "in_progress"})

results_filtered = model.val(
    data=str(filtered_yaml_path),
    split="test",
    conf=0.001,
    iou=0.6,
    device=device,
    workers=0,
    verbose=True,
    save_json=False,
    plots=False,
    name="v1_filtered_test",
    project=str(SPLIT_V2_DIR / "runs"),
    exist_ok=True,
)

log("Filtered test evaluation complete.")
update_progress(**{"Phase 3B - eval filtered v1 test": "done"})

metrics_filtered = extract_metrics(results_filtered, "v1_filtered_test")
log(f"\nFiltered test metrics: {metrics_filtered}")

# ── 7. Background false-alarm rate at conf 0.50 ───────────────────────────────
log("\n=== Background false-alarm rate at conf 0.50 ===")
update_progress(**{"Phase 3B - background FAR": "in_progress"})

def compute_background_far(test_txt_path, model, conf=0.50):
    """Count background images with >=1 detection at conf threshold."""
    # Load test image paths
    img_paths = []
    with open(test_txt_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Path may be relative to dataset root or absolute
            p = Path(line)
            if not p.is_absolute():
                p = DATASET_ROOT / line
            img_paths.append(p)

    # Find background images: those with empty label files
    def get_label_path(img_path):
        """Convert image path to label path."""
        # e.g. .../images/train/STEM.jpg -> .../labels/train/STEM.txt
        parts = list(img_path.parts)
        for i, part in enumerate(parts):
            if part == "images":
                parts[i] = "labels"
                break
        label_path = Path(*parts).with_suffix(".txt")
        return label_path

    background_imgs = []
    for p in img_paths:
        lbl = get_label_path(p)
        if not lbl.exists() or lbl.stat().st_size == 0:
            background_imgs.append(p)

    log(f"Background images in {test_txt_path.name}: {len(background_imgs)}/{len(img_paths)}")

    if not background_imgs:
        return {"n_background": 0, "n_with_detection": 0, "rate": 0.0}

    # Run inference on background images
    n_with_detection = 0
    fa_examples = []
    for p in background_imgs:
        preds = model.predict(str(p), conf=conf, verbose=False, device=device, workers=0)
        if preds and len(preds[0].boxes) > 0:
            n_with_detection += 1
            if len(fa_examples) < 3:
                fa_examples.append({"path": str(p), "n_dets": len(preds[0].boxes)})

    rate = n_with_detection / len(background_imgs) if background_imgs else 0.0
    log(f"  Background FA rate: {n_with_detection}/{len(background_imgs)} = {rate:.4f}")
    return {
        "n_background": len(background_imgs),
        "n_with_detection": n_with_detection,
        "rate": round(rate, 6),
        "examples": fa_examples,
    }

far_full     = compute_background_far(V1_TEST_TXT, model, conf=0.50)
far_filtered = compute_background_far(FILTERED_TEST_TXT, model, conf=0.50)
log(f"FA rate full: {far_full['rate']}, filtered: {far_filtered['rate']}")
update_progress(**{"Phase 3B - background FAR": "done"})

# ── 8. Save all results to JSON ───────────────────────────────────────────────
log("\nSaving results...")

results_json = {
    "note": "Path B: sensitivity measurement only. The two test sets differ; this is not a corrected metric.",
    "path_b_reason": ["cond2_max_component_lt_10pct", "cond3_all_classes_ge_100_test"],
    "model": {
        "name": "decafia_grouped_v1",
        "weights": str(V1_MODEL),
        "sha256": model_sha256,
    },
    "exclusion_list": {
        "n_excluded": len(excluded_all),
        "excluded_by_train": len(excluded_by_train),
        "excluded_by_val_only": len(excluded_only_val),
        "file": "split_v2/v1_test_exclusion_list.csv",
    },
    "full_test": {
        "n_images": len(v1_test_stems),
        **metrics_full,
        "background_far_at_conf050": far_full,
    },
    "filtered_test": {
        "n_images": len(filtered_lines),
        **metrics_filtered,
        "background_far_at_conf050": far_filtered,
    },
}

results_path = PAPER1_DIR / "results"
results_path.mkdir(exist_ok=True)
json_out = results_path / "metrics_final.json"
json_out.write_text(json.dumps(results_json, indent=2))
log(f"Results saved to {json_out}")

update_progress(**{"Phase 3B - bound effect": "COMPLETE"})
log("\n=== Phase 3B complete ===")
log(f"Full test mAP50={metrics_full['map50_overall']}, mAP50-95={metrics_full['map50_95_overall']}")
log(f"Filtered test mAP50={metrics_filtered['map50_overall']}, mAP50-95={metrics_filtered['map50_95_overall']}")
