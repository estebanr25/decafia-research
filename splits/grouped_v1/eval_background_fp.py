#!/usr/bin/env python3
"""eval_background_fp.py
Run inference on background (empty-label) test images at conf=0.25 and conf=0.50.
Reports false-positive counts per class and saves background_fp.csv.
"""

import csv, pathlib, collections

if __name__ == "__main__":
    import torch
    from ultralytics import YOLO

    MODEL_PT   = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/03_models/decafia_grouped_v1_best.pt")
    SPLIT_DIR  = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1")
    TEST_TXT   = SPLIT_DIR / "test.txt"
    ASSIGN_CSV = SPLIT_DIR / "assignments.csv"
    DATASET    = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
    CLASS_NAMES = {0: "roya", 1: "coco", 2: "minador"}
    THRESHOLDS  = [0.25, 0.50]
    OUT_CSV     = SPLIT_DIR / "background_fp.csv"

    # ---- Load test image paths from test.txt
    test_paths = []
    for line in TEST_TXT.read_text(encoding="utf-8").splitlines():
        p = line.strip()
        if p:
            test_paths.append(pathlib.Path(p))

    # ---- Build stem -> split_old from assignments.csv
    stem_to_split_old = {}
    stem_to_split_new = {}
    with open(ASSIGN_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stem_to_split_old[row["stem"]] = row["split_old"]
            stem_to_split_new[row["stem"]] = row["split_new"]

    # ---- Identify background test images (empty label in original split location)
    bg_paths = []
    for img_path in test_paths:
        stem = img_path.stem
        if stem not in stem_to_split_old:
            raise KeyError("Stem not in assignments.csv: " + repr(stem))
        split_old = stem_to_split_old[stem]
        lbl_path  = DATASET / "labels" / split_old / (stem + ".txt")
        if not lbl_path.exists():
            raise FileNotFoundError("Label missing: " + str(lbl_path))
        lines = [l for l in lbl_path.read_text().splitlines() if l.strip()]
        if not lines:
            bg_paths.append(img_path)

    # ---- Assert bg count matches assignments.csv
    bg_from_assign = sum(
        1 for stem, sn in stem_to_split_new.items()
        if sn == "test" and not any(
            (DATASET / "labels" / stem_to_split_old[stem] / (stem + ".txt"))
            .read_text().strip().splitlines()
        )
    )
    if len(bg_paths) != bg_from_assign:
        raise AssertionError(
            "Background count mismatch: test.txt gives {} but assignments.csv gives {}".format(
                len(bg_paths), bg_from_assign))

    print("Background (empty-label) test images: {}".format(len(bg_paths)))

    # ---- Run inference at each threshold
    # Use stream=True so each Result is discarded immediately (low GPU memory).
    # Reload model and clear CUDA cache between thresholds.
    import gc
    results_by_thresh = {}
    for conf_thr in THRESHOLDS:
        print("\nRunning inference at conf={} ...".format(conf_thr))
        model = YOLO(str(MODEL_PT))
        detections = {}
        gen = model.predict(
            source=[str(p) for p in bg_paths],
            imgsz=640, device=0, iou=0.7,
            conf=conf_thr, verbose=False, workers=0,
            stream=True,
        )
        for pred, img_path in zip(gen, bg_paths):
            boxes = pred.boxes
            dets  = []
            if boxes is not None and len(boxes) > 0:
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    conf_v = float(boxes.conf[i].item())
                    xyxy   = boxes.xyxy[i].tolist()
                    dets.append((cls_id, conf_v, *xyxy))
            detections[img_path.stem] = dets
        results_by_thresh[conf_thr] = detections
        del model, gen
        gc.collect()
        torch.cuda.empty_cache()

    # ---- Summarise
    rows = []
    for stem, img_path in [(p.stem, p) for p in bg_paths]:
        row = {"stem": stem, "image_path": str(img_path)}
        for thr in THRESHOLDS:
            dets = results_by_thresh[thr][stem]
            row["n_det_conf{}".format(int(thr*100))] = len(dets)
            for cls_id, name in CLASS_NAMES.items():
                row["{}_conf{}".format(name, int(thr*100))] = sum(
                    1 for d in dets if d[0] == cls_id)
        rows.append(row)

    # ---- Write CSV
    fieldnames = ["stem", "image_path"]
    for thr in THRESHOLDS:
        t = int(thr*100)
        fieldnames += ["n_det_conf{}".format(t)]
        for name in CLASS_NAMES.values():
            fieldnames += ["{}_conf{}".format(name, t)]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("\nSaved: {}".format(OUT_CSV))

    # ---- Print summary
    print("\n" + "=" * 60)
    print("BACKGROUND FALSE-POSITIVE SUMMARY")
    print("=" * 60)
    print("Background test images: {}".format(len(bg_paths)))
    for conf_thr in THRESHOLDS:
        t = int(conf_thr * 100)
        key = "n_det_conf{}".format(t)
        zero = sum(1 for r in rows if r[key] == 0)
        total_fp = sum(r[key] for r in rows)
        print("\n  conf >= {:.2f}:".format(conf_thr))
        print("    Images with ZERO detections: {} / {} ({:.1f}%)".format(
            zero, len(bg_paths), 100 * zero / len(bg_paths)))
        print("    Total FP boxes:              {}".format(total_fp))
        for cls_id, name in CLASS_NAMES.items():
            cls_key = "{}_conf{}".format(name, t)
            cls_fp  = sum(r[cls_key] for r in rows)
            print("      {:<10}: {} FP boxes".format(name, cls_fp))
        with_dets = [r["stem"] for r in rows if r[key] > 0]
        if with_dets:
            print("    Images WITH detections ({})".format(len(with_dets)) + ":")
            for s in with_dets:
                print("      " + s)
        else:
            print("    Images WITH detections: none")
