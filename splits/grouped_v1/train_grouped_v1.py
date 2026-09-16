#!/usr/bin/env python3
"""train_grouped_v1.py - Training with grouped split.
Use the PowerShell command at the bottom of build_split.py output.
"""

import json, pathlib, yaml
import torch
from ultralytics import YOLO

if __name__ == "__main__":
    assert "cu" in torch.__version__, "CUDA not in torch build: " + torch.__version__
    assert torch.cuda.is_available(), "torch.cuda.is_available() is False"

    ARGS_YAML = pathlib.Path('C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_clean_v1-2/args.yaml')
    DATA_YAML = pathlib.Path('C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1/data_grouped_v1.yaml')

    with open(ARGS_YAML, encoding="utf-8") as f:
        args = yaml.safe_load(f)

    args["data"]    = str(DATA_YAML)
    args["name"]    = "decafia_grouped_v1"
    args["workers"] = 0
    for k in ("task", "mode", "save_dir", "source", "split", "format"):
        args.pop(k, None)

    model_path = args.pop("model")
    model = YOLO(model_path)

    results = model.train(**args)

    # Validate on test split
    val_results = model.val(split="test", workers=0)
    out = pathlib.Path(results.save_dir) / "results_test.json"
    with open(out, "w") as fh:
        json.dump(val_results.results_dict, fh, indent=2)
    print("Test results ->", out)
