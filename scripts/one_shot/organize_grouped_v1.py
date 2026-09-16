# ONE-SHOT, MACHINE-SPECIFIC SETUP SCRIPT — NOT PART OF THE REPRODUCIBLE PIPELINE.
# Already executed on 2026-09-16. Paths point to the author's local machine.
# Kept for provenance: it wrote results/grouped_v1/RESULTS_grouped_v1.md using metric values
# hardcoded from the confirmed test evaluation (runs/decafia_grouped_v1_test), and rewrote the
# split .txt files from absolute to dataset-relative paths.
# Reproducible scripts: splits/grouped_v1/build_split.py, eval_background_fp.py, train_grouped_v1.py.
#!/usr/bin/env python3
"""organize_grouped_v1.py
Steps 3+4: write RESULTS_grouped_v1.md and populate the research repo.
Does NOT run git. Does NOT modify images or label files. Raises on any error.
"""

import csv, pathlib, shutil, textwrap

if __name__ == "__main__":

    # ---- Paths ---------------------------------------------------------------
    DATASET    = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
    SPLIT_DIR  = DATASET / "split_grouped_v1"
    TRAIN_RUN  = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_grouped_v1")
    TEST_EVAL  = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_grouped_v1_test")
    REPO       = pathlib.Path("C:/Users/luise/temp/decafia-research")
    AUDIT_SRC  = REPO / "audits" / "near_duplicates"  # already in repo, just untracked

    RES_DIR    = REPO / "results"  / "grouped_v1"
    SPL_DIR    = REPO / "splits"   / "grouped_v1"
    RES_DIR.mkdir(parents=True, exist_ok=True)
    SPL_DIR.mkdir(parents=True, exist_ok=True)

    MB = 1024 * 1024
    MAX_BYTES = 20 * MB

    def copy_assert(src, dst):
        src = pathlib.Path(src)
        dst = pathlib.Path(dst)
        if not src.exists():
            raise FileNotFoundError("Source missing: " + str(src))
        size = src.stat().st_size
        if size > MAX_BYTES:
            raise AssertionError("File > 20 MB: {} ({:.1f} MB)".format(src.name, size/MB))
        shutil.copy2(src, dst)
        print("  copied {:>8.1f} kB  {}  ->  {}".format(size/1024, src.name, dst))
        return size

    # ---- STEP 3: Write RESULTS_grouped_v1.md --------------------------------
    print("=" * 60)
    print("STEP 3 -- Write RESULTS_grouped_v1.md")
    print("=" * 60)

    # F1 = 2PR/(P+R)
    def f1(p, r): return 2 * p * r / (p + r)

    # CONFIRMED test metrics
    met = {
        "all":     dict(P=0.876, R=0.870, m50=0.929, m5095=0.734),
        "roya":    dict(P=0.803, R=0.740, m50=0.841, m5095=0.537),
        "coco":    dict(P=0.908, R=0.909, m50=0.962, m5095=0.795),
        "minador": dict(P=0.918, R=0.963, m50=0.985, m5095=0.871),
    }
    # Baseline (clean_v1, test split 349 images) — CONFIRMED
    base = {
        "all":     dict(m50=0.9235, m5095=0.7293),
        "roya":    dict(m50=0.8619, m5095=0.5700),
        "coco":    dict(m50=0.9638, m5095=0.7921),
        "minador": dict(m50=0.9449, m5095=0.8258),
    }

    # Read background FP csv
    BG_CSV = SPLIT_DIR / "background_fp.csv"
    if not BG_CSV.exists():
        raise FileNotFoundError("background_fp.csv missing — run eval_background_fp.py first")
    bg_rows = list(csv.DictReader(open(BG_CSV, encoding="utf-8")))
    n_bg = len(bg_rows)

    def bg_stat(thr_pct):
        key  = "n_det_conf{}".format(thr_pct)
        zero = sum(1 for r in bg_rows if int(r[key]) == 0)
        total_fp = sum(int(r[key]) for r in bg_rows)
        cls_fp = {}
        for name in ("roya", "coco", "minador"):
            cls_fp[name] = sum(int(r["{}_conf{}".format(name, thr_pct)]) for r in bg_rows)
        with_det = [r["stem"] for r in bg_rows if int(r[key]) > 0]
        return zero, total_fp, cls_fp, with_det

    z25, fp25, cfp25, wd25 = bg_stat(25)
    z50, fp50, cfp50, wd50 = bg_stat(50)

    # Figures
    test_pngs = sorted(p.name for p in TEST_EVAL.iterdir()
                       if p.suffix.lower() == ".png")
    train_pngs = sorted(p.name for p in TRAIN_RUN.iterdir()
                        if p.suffix.lower() == ".png")

    md = textwrap.dedent("""\
    # RESULTS — DECAFIA grouped split v1

    Model: `decafia_grouped_v1_best.pt` (YOLOv8m, 100 epochs, AdamW)
    Split: leakage-safe grouped split (B=20, union-find on number blocks + crop-parent + pHash ≤ 4)
    Test set: **356 images, 2,020 instances** (CONFIRMED)
    Val set: 382 images

    ---

    ## 1. Per-class test results (CONFIRMED)

    | Class   |    P |    R |   F1 | mAP50 | mAP50-95 |
    |---------|------|------|------|-------|----------|
    """)
    for cls in ("all", "roya", "coco", "minador"):
        m = met[cls]
        f = f1(m["P"], m["R"])
        md += "| {:<7} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f}    |\n".format(
            cls, m["P"], m["R"], f, m["m50"], m["m5095"])

    md += textwrap.dedent("""
    F1 = 2·P·R/(P+R), computed from the CONFIRMED P and R above.

    ---

    ## 2. Val vs test consistency

    | Split | mAP50 | mAP50-95 |
    |-------|-------|----------|
    | val   | 0.924 | 0.731    |
    | test  | 0.929 | 0.734    |
    | diff  | +0.005 | +0.003  |

    Val and test differ by < 0.5 pp on both aggregate metrics, indicating
    that the grouped split produced a consistent difficulty distribution.

    ---

    ## 3. Background false positives (CONFIRMED — eval_background_fp.py)

    Background images in test split (empty label file): **{n_bg}**

    | Threshold | Images clean | Images w/ FP | Total FP boxes | roya FP | coco FP | minador FP |
    |-----------|-------------|--------------|----------------|---------|---------|------------|
    | conf ≥ 0.25 | {z25}/{n_bg} ({pz25:.1f}%) | {wd25_n} | {fp25} | {cfp25_r} | {cfp25_c} | {cfp25_m} |
    | conf ≥ 0.50 | {z50}/{n_bg} ({pz50:.1f}%) | {wd50_n} | {fp50} | {cfp50_r} | {cfp50_c} | {cfp50_m} |

    Images with detections at conf ≥ 0.25 ({wd25_n}):
    {wd25_list}

    Images with detections at conf ≥ 0.50 ({wd50_n}):
    {wd50_list}

    All FP images belong to the SANAS prefix (healthy-leaf images from the same acquisition
    as annotated leaves), consistent with their visual similarity to annotated leaves.

    ---

    ## 4. Baseline vs grouped comparison

    > **Caveat:** Test sets differ between splits and a single split seed was used;
    > per-class differences (≤ 4.5 pp) were not evaluated against split-to-split variability.

    Baseline: `decafia_clean_v1-2` — per-image stratified split, test set 349 images (CONFIRMED).
    Grouped:  `decafia_grouped_v1`  — leakage-safe grouped split, test set 356 images (CONFIRMED).

    | Class   | Metric     | Baseline | Grouped | Δ (pp)  |
    |---------|------------|----------|---------|---------|
    """)
    for cls in ("all", "roya", "coco", "minador"):
        b = base[cls]
        g = met[cls]
        for metric, bval, gval in (
            ("mAP50",    b["m50"],   g["m50"]),
            ("mAP50-95", b["m5095"], g["m5095"]),
        ):
            delta = (gval - bval) * 100
            sign  = "+" if delta >= 0 else ""
            md += "| {:<7} | {:<10} | {:.4f}   | {:.3f}   | {}{:.2f}  |\n".format(
                cls, metric, bval, gval, sign, delta)

    md = md.format(
        n_bg=n_bg,
        z25=z25,   pz25=100*z25/n_bg,  wd25_n=len(wd25),  fp25=fp25,
        cfp25_r=cfp25["roya"], cfp25_c=cfp25["coco"], cfp25_m=cfp25["minador"],
        z50=z50,   pz50=100*z50/n_bg,  wd50_n=len(wd50),  fp50=fp50,
        cfp50_r=cfp50["roya"], cfp50_c=cfp50["coco"], cfp50_m=cfp50["minador"],
        wd25_list="\n    ".join(wd25) if wd25 else "(none)",
        wd50_list="\n    ".join(wd50) if wd50 else "(none)",
    )

    md += textwrap.dedent("""
    ---

    ## 5. Limitations

    1. **Non-consecutive file numbers:** The grouped split uses floor(number / B) blocks to
       detect same-session images. A physical leaf photographed at non-consecutive file numbers
       (e.g., session gap between images) is not detectable by this strategy and can only be
       caught by pHash near-duplicate edges (distance ≤ 4). Pairs with 5 ≤ pHash ≤ 12 may
       still represent the same leaf and remain undetected. Residual leakage cannot be fully
       excluded.

    2. **Orphan-crop rule:** Orphan crops from the `own_field` source (COCO_RECORTE, 64 images)
       are forced to the training split, under the assumption that their parents exist in the
       dataset but were not detected by the SIFT pipeline. If any such parent is actually in val
       or test, these crops represent a minor train-time advantage that cannot be quantified
       without re-running the SIFT crop-parent search with relaxed thresholds.

    3. **Single seed:** Only seed=42 was used for the randomized group assignment. The reported
       per-class differences between baseline and grouped are within the likely range of
       split-to-split variability and should not be interpreted as model-level differences.

    ---

    ## 6. Figures

    ### Test evaluation (`decafia_grouped_v1_test/`)
    """)
    for name in test_pngs:
        md += "- `{}`\n".format(name)

    md += "\n### Training run (`decafia_grouped_v1/`)\n"
    for name in train_pngs:
        md += "- `{}`\n".format(name)

    results_md_path = RES_DIR / "RESULTS_grouped_v1.md"
    results_md_path.write_text(md, encoding="utf-8")
    print("Wrote: " + str(results_md_path))

    # ---- STEP 4a: Copy to results/grouped_v1/ --------------------------------
    print("\n" + "=" * 60)
    print("STEP 4a -- Populate results/grouped_v1/")
    print("=" * 60)

    copy_assert(SPLIT_DIR / "background_fp.csv",                  RES_DIR / "background_fp.csv")
    copy_assert(TRAIN_RUN / "results.csv",                         RES_DIR / "results.csv")
    copy_assert(TRAIN_RUN / "args.yaml",                           RES_DIR / "args.yaml")
    for png in TEST_EVAL.iterdir():
        if png.suffix.lower() == ".png":
            copy_assert(png, RES_DIR / png.name)

    # ---- STEP 4b: Populate splits/grouped_v1/ --------------------------------
    print("\n" + "=" * 60)
    print("STEP 4b -- Populate splits/grouped_v1/")
    print("=" * 60)

    # Rewrite txt files with relative paths (relative to dataset root)
    DATASET_PREFIX = DATASET.as_posix() + "/"
    for split in ("train", "val", "test"):
        src_txt = SPLIT_DIR / (split + ".txt")
        lines   = src_txt.read_text(encoding="utf-8").splitlines()
        rel_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            posix = pathlib.Path(line).as_posix()
            if not posix.startswith(DATASET_PREFIX):
                raise ValueError(
                    "Path not under dataset root: " + line)
            rel_lines.append(posix[len(DATASET_PREFIX):])
        out_txt = SPL_DIR / (split + ".txt")
        out_txt.write_text("\n".join(rel_lines) + "\n", encoding="utf-8")
        size = out_txt.stat().st_size
        if size > MAX_BYTES:
            raise AssertionError(split + ".txt > 20 MB: " + str(size))
        print("  wrote  {:>8.1f} kB  {}  ({} paths, relative)".format(
            size/1024, out_txt.name, len(rel_lines)))

    # Write data_grouped_v1.yaml with placeholder
    data_yaml_content = textwrap.dedent("""\
    # DECAFIA grouped split v1 - data configuration
    # TODO: set `path` to the absolute path of your decafia_clean dataset root on your machine.
    # TODO: update train/val/test to absolute paths of the split txt files (or paths relative to `path`).
    path: /path/to/decafia_clean   # <-- EDIT THIS (absolute path to dataset root)
    train: /path/to/splits/grouped_v1/train.txt  # <-- EDIT THIS
    val:   /path/to/splits/grouped_v1/val.txt    # <-- EDIT THIS
    test:  /path/to/splits/grouped_v1/test.txt   # <-- EDIT THIS

    nc: 3
    names:
      0: roya
      1: coco
      2: minador
    """)
    data_yaml_out = SPL_DIR / "data_grouped_v1.yaml"
    data_yaml_out.write_text(data_yaml_content, encoding="utf-8")
    print("  wrote {:>8.1f} kB  data_grouped_v1.yaml  (placeholder paths)".format(
        data_yaml_out.stat().st_size / 1024))

    # Copy split artifacts
    for fname in (
        "assignments.csv", "SPLIT_README.md",
        "crop_parent_map_full.csv", "orphan_crops.txt",
        "build_split.py", "train_grouped_v1.py", "eval_background_fp.py",
    ):
        copy_assert(SPLIT_DIR / fname, SPL_DIR / fname)

    # ---- STEP 4c: Audit files (already in repo, verify sizes) ---------------
    print("\n" + "=" * 60)
    print("STEP 4c -- Verify audit files (untracked, will be staged)")
    print("=" * 60)
    EXCLUDE_AUDIT = {"embeddings.npy"}
    audit_ok = []
    audit_skip = []
    for p in sorted(AUDIT_SRC.iterdir()):
        if p.name in EXCLUDE_AUDIT:
            audit_skip.append(p.name)
            continue
        size = p.stat().st_size
        if size > MAX_BYTES:
            audit_skip.append(p.name + " (>" + str(size//MB) + " MB)")
            continue
        if size > MAX_BYTES:
            raise AssertionError("Audit file > 20 MB: " + p.name)
        audit_ok.append((p.name, size))
        print("  ok  {:>8.1f} kB  {}".format(size/1024, p.name))
    print("  Skipped: " + ", ".join(audit_skip))

    # ---- Final size assertion on all files we copied -------------------------
    print("\n" + "=" * 60)
    print("Size assertions")
    print("=" * 60)
    all_out = list(RES_DIR.iterdir()) + list(SPL_DIR.iterdir())
    max_size = 0
    for p in all_out:
        s = p.stat().st_size
        if s > max_size:
            max_size = s
        if s > MAX_BYTES:
            raise AssertionError("Output file > 20 MB: {} ({:.1f} MB)".format(
                p.name, s/MB))
    print("  All output files pass 20 MB limit (largest: {:.2f} MB)".format(max_size/MB))
    print("  results/grouped_v1/ : {} files".format(len(list(RES_DIR.iterdir()))))
    print("  splits/grouped_v1/  : {} files".format(len(list(SPL_DIR.iterdir()))))
    print("\nDone. Now run git commands to stage, review, commit and push.")
