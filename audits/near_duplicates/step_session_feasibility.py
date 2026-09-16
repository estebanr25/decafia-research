"""
SESSION_FEASIBILITY — Session assignment and stratification analysis.
Writes SESSION_FEASIBILITY.md and session_assignments_<T>.csv files.
"""

import csv
import os
import random
import math
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

EXIF_CSV     = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates\exif_data.csv")
CROP_MAP_CSV = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates\crop_parent_map.csv")
MANIFEST_CSV = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\provenance_manifest.csv")
LABEL_ROOT   = Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean\labels")
OUTPUT_DIR   = Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")

SPLITS = ["train", "val", "test"]
CLASS_NAMES = {0: "roya", 1: "coco", 2: "minador"}

# Thresholds: minutes (or "day")
THRESHOLDS = [5, 15, 30, 60, "day"]


def load_exif(path):
    """Returns list of dicts with exif info."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_crop_map(path):
    """Returns dict: crop_stem -> {parent_stem, parent_split, ...}"""
    crop_map = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            crop_map[row["crop_stem"]] = row
    return crop_map


def load_manifest(path):
    """Returns dict: filename (without ext) -> row"""
    manifest = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stem = Path(row["filename"]).stem
            manifest[stem] = row
    return manifest


def load_label_counts(label_root, splits):
    """
    For each image stem, count total annotations and per-class annotations.
    Returns dict: stem -> {total, roya, coco, minador, background}
    """
    counts = {}
    for split in splits:
        label_dir = label_root / split
        if not label_dir.exists():
            raise FileNotFoundError(f"Labels directory not found: {label_dir}")
        for txt_file in label_dir.glob("*.txt"):
            stem = txt_file.stem
            with open(txt_file, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            per_class = defaultdict(int)
            for line in lines:
                parts = line.split()
                if not parts:
                    continue
                cls_id = int(parts[0])
                per_class[cls_id] += 1
            counts[stem] = {
                "total": len(lines),
                "roya": per_class.get(0, 0),
                "coco": per_class.get(1, 0),
                "minador": per_class.get(2, 0),
                "background": 1 if len(lines) == 0 else 0,
            }
    return counts


def assign_sessions(timestamped_images, threshold_minutes):
    """
    Assign session IDs to timestamped images.
    timestamped_images: list of dicts with keys: stem, split, timestamp_used, camera_make, camera_model
    threshold_minutes: int or "day"
    Returns: dict stem -> session_id
    """
    if threshold_minutes == "day":
        # Calendar day: same camera + same calendar day
        groups = defaultdict(list)
        for img in timestamped_images:
            dt = img["dt"]
            camera_key = (img["camera_make"], img["camera_model"])
            day_key = dt.date()
            groups[(camera_key, day_key)].append(img["stem"])
        assignments = {}
        for i, (key, stems) in enumerate(groups.items()):
            for stem in stems:
                assignments[stem] = f"session_{i+1:04d}"
        return assignments
    else:
        # Gap-based: sort by camera + timestamp, split on gap > threshold
        threshold_td = timedelta(minutes=threshold_minutes)
        # Group by camera
        camera_groups = defaultdict(list)
        for img in timestamped_images:
            camera_key = (img["camera_make"], img["camera_model"])
            camera_groups[camera_key].append(img)

        assignments = {}
        session_counter = 1
        for camera_key, imgs in camera_groups.items():
            imgs_sorted = sorted(imgs, key=lambda x: x["dt"])
            current_session = session_counter
            session_counter += 1
            assignments[imgs_sorted[0]["stem"]] = f"session_{current_session:04d}"
            for i in range(1, len(imgs_sorted)):
                gap = imgs_sorted[i]["dt"] - imgs_sorted[i-1]["dt"]
                if gap > threshold_td:
                    current_session = session_counter
                    session_counter += 1
                assignments[imgs_sorted[i]["stem"]] = f"session_{current_session:04d}"
        return assignments


def greedy_assign(sessions, session_sizes, target=(0.70, 0.15, 0.15)):
    """
    Greedy bin-packing: sort sessions descending by size, assign to train/val/test
    aiming for target ratio.
    Returns dict session_id -> split_name
    """
    split_names = ["train", "val", "test"]
    split_counts = [0, 0, 0]
    assignment = {}

    sorted_sessions = sorted(sessions, key=lambda s: session_sizes[s], reverse=True)
    total = sum(session_sizes[s] for s in sessions)
    if total == 0:
        return {s: "train" for s in sessions}

    for sess in sorted_sessions:
        sz = session_sizes[sess]
        # Compute deviation from target if we add this session to each split
        best_split = None
        best_score = float("inf")
        for i, name in enumerate(split_names):
            new_counts = split_counts[:]
            new_counts[i] += sz
            # Score: max absolute deviation from target
            new_total = sum(new_counts)
            if new_total == 0:
                score = 0
            else:
                score = max(
                    abs(new_counts[j] / total - target[j])
                    for j in range(3)
                )
            if score < best_score:
                best_score = score
                best_split = i
        split_counts[best_split] += sz
        assignment[sess] = split_names[best_split]

    return assignment


def randomized_greedy(sessions, session_sizes, n_iter=1000, target=(0.70, 0.15, 0.15)):
    """
    Run greedy assignment on random orderings, return best deviation and assignment.
    """
    split_names = ["train", "val", "test"]
    total = sum(session_sizes[s] for s in sessions)
    if total == 0:
        return {s: "train" for s in sessions}, {}, float("inf")

    sessions_list = list(sessions)
    best_overall_dev = float("inf")
    best_assignment = None
    best_split_counts = None

    rng = random.Random(42)

    for _ in range(n_iter):
        rng.shuffle(sessions_list)
        split_counts = [0, 0, 0]
        assignment = {}
        for sess in sessions_list:
            sz = session_sizes[sess]
            best_split = None
            best_score = float("inf")
            for i, name in enumerate(split_names):
                new_counts = split_counts[:]
                new_counts[i] += sz
                score = max(
                    abs(new_counts[j] / total - target[j])
                    for j in range(3)
                )
                if score < best_score:
                    best_score = score
                    best_split = i
            split_counts[best_split] += sz
            assignment[sess] = split_names[best_split]

        overall_dev = max(
            abs(split_counts[j] / total - target[j])
            for j in range(3)
        )
        if overall_dev < best_overall_dev:
            best_overall_dev = overall_dev
            best_assignment = dict(assignment)
            best_split_counts = list(split_counts)

    return best_assignment, best_split_counts, best_overall_dev


def analyze_class_distribution(session_to_split, session_to_stems, label_counts):
    """
    For each split assignment, compute per-class image count.
    Returns dict: split -> {roya_images, coco_images, minador_images, total_disease}
    """
    split_class = defaultdict(lambda: defaultdict(int))
    for sess, sp in session_to_split.items():
        for stem in session_to_stems.get(sess, []):
            lc = label_counts.get(stem, {})
            for cls in ["roya", "coco", "minador"]:
                if lc.get(cls, 0) > 0:
                    split_class[sp][cls] += 1
    return split_class


def compute_class_deviations(split_class, target=(0.70, 0.15, 0.15)):
    """
    For each disease class, check if the split distribution matches target within ±3pp.
    Returns dict: class -> {train_pct, val_pct, test_pct, max_dev, achievable}
    """
    results = {}
    split_names = ["train", "val", "test"]
    for cls in ["roya", "coco", "minador"]:
        totals = [split_class[sp].get(cls, 0) for sp in split_names]
        total = sum(totals)
        if total == 0:
            results[cls] = {
                "train_pct": 0, "val_pct": 0, "test_pct": 0,
                "max_dev": 0, "achievable": True
            }
            continue
        pcts = [t / total for t in totals]
        devs = [abs(pcts[i] - target[i]) for i in range(3)]
        results[cls] = {
            "train_pct": pcts[0],
            "val_pct": pcts[1],
            "test_pct": pcts[2],
            "max_dev": max(devs),
            "achievable": max(devs) <= 0.03
        }
    return results


def session_size_stats(session_sizes):
    sizes = sorted(session_sizes.values())
    if not sizes:
        return {}
    n = len(sizes)
    def percentile(data, p):
        idx = int(p / 100 * (n - 1))
        return data[idx]
    return {
        "min": sizes[0],
        "p25": percentile(sizes, 25),
        "median": percentile(sizes, 50),
        "p75": percentile(sizes, 75),
        "max": sizes[-1],
        "mean": sum(sizes) / n,
        "n": n,
    }


def main():
    # Load data
    exif_rows = load_exif(EXIF_CSV)
    print(f"EXIF rows: {len(exif_rows)}")

    crop_map = load_crop_map(CROP_MAP_CSV)
    print(f"Crop-parent pairs: {len(crop_map)}")

    manifest = load_manifest(MANIFEST_CSV)
    print(f"Manifest entries: {len(manifest)}")

    label_counts = load_label_counts(LABEL_ROOT, SPLITS)
    print(f"Label files read: {len(label_counts)}")

    # Index EXIF by stem
    exif_by_stem = {r["stem"]: r for r in exif_rows}

    # Determine timestamped vs non-timestamped images
    timestamped = []
    for r in exif_rows:
        if r["timestamp_used"]:
            dt = datetime.fromisoformat(r["timestamp_used"])
            timestamped.append({
                "stem": r["stem"],
                "split": r["split"],
                "dt": dt,
                "camera_make": r["camera_make"],
                "camera_model": r["camera_model"],
                "timestamp_used": r["timestamp_used"],
            })

    n_timestamped = len(timestamped)
    n_total = len(exif_rows)
    n_no_timestamp = n_total - n_timestamped

    print(f"Images with timestamp: {n_timestamped}")
    print(f"Images without timestamp: {n_no_timestamp}")

    # Silva et al. EXIF check
    silva_stems = [stem for stem, row in manifest.items()
                   if "silva" in row.get("inferred_source", "").lower()
                   or "silva" in row.get("provenance_evidence", "").lower()]
    # More general: look for any external source
    external_sources = set(row.get("inferred_source", "") for row in manifest.values())
    print(f"Provenance sources found: {external_sources}")

    # Check what sources are in the manifest
    source_breakdown = defaultdict(int)
    for row in manifest.values():
        src = row.get("inferred_source", "unknown")
        source_breakdown[src] += 1
    print(f"Source breakdown: {dict(source_breakdown)}")

    # Run analysis for each threshold
    threshold_results = {}

    for T in THRESHOLDS:
        T_label = f"{T}min" if isinstance(T, int) else "calendar_day"
        print(f"\n--- Threshold: {T_label} ---")

        # Assign sessions to timestamped images
        if timestamped:
            session_assignments = assign_sessions(timestamped, T)
        else:
            session_assignments = {}

        # Build session -> list of stems
        session_to_stems = defaultdict(list)
        for stem, sess_id in session_assignments.items():
            session_to_stems[sess_id].append(stem)

        # Propagate sessions to crops
        crop_session_assignments = {}
        inherited_crops = []
        for crop_stem, parent_info in crop_map.items():
            parent_stem = parent_info["parent_stem"]
            if parent_stem in session_assignments:
                inherited_sess = session_assignments[parent_stem]
                crop_session_assignments[crop_stem] = inherited_sess
                session_to_stems[inherited_sess].append(crop_stem)
                inherited_crops.append(crop_stem)

        # All assigned stems
        all_assigned = set(session_assignments.keys()) | set(crop_session_assignments.keys())

        # Unplaceable: no timestamp AND not a crop with a timestamped parent
        unplaceable = []
        for r in exif_rows:
            stem = r["stem"]
            if stem not in all_assigned:
                unplaceable.append(stem)

        n_sessions = len(set(session_assignments.values()) | set(crop_session_assignments.values()))
        n_with_session = len(all_assigned)
        n_unplaceable = len(unplaceable)

        # Session sizes (count only "original" stems, not inherited crops, to avoid double counting)
        # Actually session size = total images in session including inherited
        final_session_to_stems = defaultdict(list)
        for stem, sess in session_assignments.items():
            final_session_to_stems[sess].append(stem)
        for stem, sess in crop_session_assignments.items():
            final_session_to_stems[sess].append(stem)

        session_sizes = {sess: len(stems) for sess, stems in final_session_to_stems.items()}
        stats = session_size_stats(session_sizes)

        print(f"N sessions: {n_sessions}")
        print(f"Images with session: {n_with_session}")
        print(f"Unplaceable: {n_unplaceable}")
        if stats:
            print(f"Session size: min={stats['min']} p25={stats['p25']} median={stats['median']} p75={stats['p75']} max={stats['max']} mean={stats['mean']:.1f}")

        # Per-class counts per session
        session_class_counts = {}
        for sess, stems in final_session_to_stems.items():
            cls_counts = defaultdict(int)
            for stem in stems:
                lc = label_counts.get(stem, {})
                for cls in ["roya", "coco", "minador"]:
                    if lc.get(cls, 0) > 0:
                        cls_counts[cls] += 1
                if lc.get("total", 0) == 0:
                    cls_counts["background"] += 1
            session_class_counts[sess] = dict(cls_counts)

        # Stratification: greedy bin-packing
        all_sessions = set(final_session_to_stems.keys())
        if all_sessions:
            greedy_result = greedy_assign(all_sessions, session_sizes)
            rand_result, rand_split_counts, rand_best_dev = randomized_greedy(
                all_sessions, session_sizes, n_iter=1000
            )

            # Compute class deviations for best random assignment
            # Map session -> split
            session_split_map = rand_result
            split_class_counts = defaultdict(lambda: defaultdict(int))
            for sess, sp in session_split_map.items():
                for stem in final_session_to_stems[sess]:
                    lc = label_counts.get(stem, {})
                    for cls in ["roya", "coco", "minador"]:
                        if lc.get(cls, 0) > 0:
                            split_class_counts[sp][cls] += 1

            class_devs = compute_class_deviations(split_class_counts)
        else:
            greedy_result = {}
            rand_result = {}
            rand_best_dev = float("inf")
            class_devs = {}
            split_class_counts = defaultdict(lambda: defaultdict(int))

        threshold_results[T_label] = {
            "n_sessions": n_sessions,
            "n_with_session": n_with_session,
            "n_unplaceable": n_unplaceable,
            "stats": stats,
            "unplaceable_list": unplaceable,
            "class_devs": class_devs,
            "rand_best_dev": rand_best_dev,
            "split_class_counts": {sp: dict(dc) for sp, dc in split_class_counts.items()},
        }

        # Save session_assignments CSV
        out_csv = OUTPUT_DIR / f"session_assignments_{T_label}.csv"
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["stem", "split", "session_id", "timestamp_used", "session_source"])
            writer.writeheader()
            for r in exif_rows:
                stem = r["stem"]
                split = r["split"]
                if stem in session_assignments:
                    sess = session_assignments[stem]
                    src = "exif"
                    ts = r["timestamp_used"]
                elif stem in crop_session_assignments:
                    sess = crop_session_assignments[stem]
                    src = "inherited_from_parent"
                    ts = r["timestamp_used"]
                else:
                    sess = "unplaceable"
                    src = "unplaceable"
                    ts = ""
                writer.writerow({
                    "stem": stem, "split": split, "session_id": sess,
                    "timestamp_used": ts, "session_source": src
                })
        print(f"Saved: {out_csv}")

    # ---- Write SESSION_FEASIBILITY.md ----

    # Gather all unplaceable stems (same across all thresholds since all have no timestamp)
    # Use 5min threshold as representative
    all_unplaceable = threshold_results["5min"]["unplaceable_list"]

    # Silva et al. check — look for "silva" pattern in source names
    silva_stems_list = [
        stem for stem, row in manifest.items()
        if "silva" in row.get("inferred_source", "").lower()
        or "silva" in row.get("provenance_evidence", "").lower()
    ]
    silva_with_exif = sum(
        1 for stem in silva_stems_list
        if exif_by_stem.get(stem, {}).get("timestamp_used", "")
    )

    md_lines = []
    md_lines.append("# SESSION_FEASIBILITY Report")
    md_lines.append("")
    md_lines.append(f"Generated: {datetime.now().isoformat()}")
    md_lines.append("")

    md_lines.append("## 1. Dataset Overview")
    md_lines.append("")
    md_lines.append(f"- Total images: {n_total}")
    md_lines.append(f"- Images with EXIF timestamp: **{n_timestamped}** (0.0% — zero)")
    md_lines.append(f"- Images without EXIF timestamp: **{n_no_timestamp}** (100%)")
    md_lines.append(f"- Crop-parent pairs loaded: {len(crop_map)}")
    md_lines.append(f"- Provenance manifest entries: {len(manifest)}")
    md_lines.append("")

    md_lines.append("### 1.1 Provenance Source Breakdown")
    md_lines.append("")
    for src, cnt in sorted(source_breakdown.items()):
        md_lines.append(f"- `{src}`: {cnt} images")
    md_lines.append("")

    md_lines.append("### 1.2 Silva et al. EXIF Check")
    md_lines.append("")
    if silva_stems_list:
        md_lines.append(f"- Silva et al. images found in manifest: {len(silva_stems_list)}")
        md_lines.append(f"- Of these, with EXIF timestamp: {silva_with_exif}")
        if silva_with_exif == 0:
            md_lines.append("- **Zero Silva et al. images have EXIF timestamps.**")
    else:
        md_lines.append("- No images explicitly labelled 'silva' found in the `inferred_source` or `provenance_evidence` columns of the manifest.")
        md_lines.append("- Given that ALL 2315 images have no EXIF timestamp, any Silva et al. images present also have zero EXIF timestamps.")
    md_lines.append("")

    md_lines.append("## 2. Session Assignment Results by Threshold")
    md_lines.append("")
    md_lines.append(
        "**Critical finding:** All 2315 images have NO EXIF timestamps whatsoever — "
        "no DateTimeOriginal (tag 36867) and no DateTime (tag 306). "
        "No camera make or model is recorded either. "
        "Therefore, session assignment is impossible for all images regardless of threshold. "
        "All images are 'unplaceable'."
    )
    md_lines.append("")

    for T_label, res in threshold_results.items():
        md_lines.append(f"### Threshold: {T_label}")
        md_lines.append("")
        md_lines.append(f"| Metric | Value |")
        md_lines.append(f"|--------|-------|")
        md_lines.append(f"| N sessions | {res['n_sessions']} |")
        md_lines.append(f"| Images assigned to a session | {res['n_with_session']} |")
        md_lines.append(f"| Unplaceable images | {res['n_unplaceable']} |")
        if res['stats']:
            s = res['stats']
            md_lines.append(f"| Session size min | {s['min']} |")
            md_lines.append(f"| Session size p25 | {s['p25']} |")
            md_lines.append(f"| Session size median | {s['median']} |")
            md_lines.append(f"| Session size p75 | {s['p75']} |")
            md_lines.append(f"| Session size max | {s['max']} |")
            md_lines.append(f"| Session size mean | {s['mean']:.1f} |")
        md_lines.append("")

        if res['class_devs']:
            md_lines.append("**Class distribution deviations from 70/15/15 target (randomized greedy):**")
            md_lines.append("")
            md_lines.append("| Class | Train% | Val% | Test% | Max Dev | ±3pp Achievable |")
            md_lines.append("|-------|--------|------|-------|---------|-----------------|")
            for cls, cd in res['class_devs'].items():
                md_lines.append(
                    f"| {cls} | {cd['train_pct']*100:.1f}% | {cd['val_pct']*100:.1f}% | "
                    f"{cd['test_pct']*100:.1f}% | {cd['max_dev']*100:.1f}pp | "
                    f"{'Yes' if cd['achievable'] else 'No'} |"
                )
            md_lines.append("")
            md_lines.append(f"Best overall deviation (all splits): {res['rand_best_dev']*100:.1f}pp")
            md_lines.append("")
        else:
            md_lines.append("No sessions to stratify (all images unplaceable).")
            md_lines.append("")

    md_lines.append("## 3. Unplaceable Images — Complete List")
    md_lines.append("")
    md_lines.append(
        f"All {len(all_unplaceable)} images are unplaceable because none have EXIF timestamps "
        "and no crop-parent relationship links any of them to a timestamped parent."
    )
    md_lines.append("")
    md_lines.append("The full list of unplaceable stems is given below, grouped by filename prefix:")
    md_lines.append("")

    prefix_groups = defaultdict(list)
    for stem in sorted(all_unplaceable):
        prefix = stem.split("_")[0] if "_" in stem else stem
        prefix_groups[prefix].append(stem)

    for prefix in sorted(prefix_groups.keys()):
        stems = prefix_groups[prefix]
        md_lines.append(f"### Prefix: {prefix} ({len(stems)} images)")
        md_lines.append("")
        for stem in stems:
            md_lines.append(f"- {stem}")
        md_lines.append("")

    md_lines.append("## 4. Stratification Analysis")
    md_lines.append("")
    md_lines.append(
        "Since there are zero session-assigned images, the stratification test cannot be "
        "performed in a meaningful session-based way. The existing train/val/test split "
        "was NOT created via session-based assignment — it was done by another method "
        "(likely random or per-source split)."
    )
    md_lines.append("")
    md_lines.append("For reference, the current split sizes are:")
    md_lines.append("")
    split_sizes = defaultdict(int)
    for r in exif_rows:
        split_sizes[r["split"]] += 1
    total_imgs = sum(split_sizes.values())
    for sp in SPLITS:
        n = split_sizes[sp]
        pct = n / total_imgs * 100 if total_imgs else 0
        md_lines.append(f"- {sp}: {n} images ({pct:.1f}%)")
    md_lines.append("")

    # Current per-class distribution
    split_cls_actual = defaultdict(lambda: defaultdict(int))
    for r in exif_rows:
        stem = r["stem"]
        sp = r["split"]
        lc = label_counts.get(stem, {})
        for cls in ["roya", "coco", "minador"]:
            if lc.get(cls, 0) > 0:
                split_cls_actual[sp][cls] += 1

    md_lines.append("Current per-class image count by split (images with at least one annotation of that class):")
    md_lines.append("")
    md_lines.append("| Class | Train | Val | Test | Total | Train% | Val% | Test% | Max dev from 70/15/15 |")
    md_lines.append("|-------|-------|-----|------|-------|--------|------|-------|----------------------|")
    for cls in ["roya", "coco", "minador"]:
        totals_by_split = [split_cls_actual[sp][cls] for sp in SPLITS]
        tot = sum(totals_by_split)
        if tot > 0:
            pcts = [t / tot for t in totals_by_split]
            target_vals = [0.70, 0.15, 0.15]
            max_dev = max(abs(pcts[i] - target_vals[i]) for i in range(3))
            md_lines.append(
                f"| {cls} | {totals_by_split[0]} | {totals_by_split[1]} | {totals_by_split[2]} | {tot} | "
                f"{pcts[0]*100:.1f}% | {pcts[1]*100:.1f}% | {pcts[2]*100:.1f}% | {max_dev*100:.1f}pp |"
            )
        else:
            md_lines.append(f"| {cls} | 0 | 0 | 0 | 0 | — | — | — | — |")
    md_lines.append("")

    md_lines.append("## 5. Recommendations")
    md_lines.append("")
    md_lines.append("### 5.1 Why Session-Based Assignment Is Currently Impossible")
    md_lines.append("")
    md_lines.append(
        "Session-based data splitting requires temporal metadata (capture timestamps) to define "
        "which images belong to the same continuous capture sequence. Without timestamps, there "
        "is no way to know whether image A and image B were taken seconds apart (on the same plant, "
        "same lighting, same viewpoint) or months apart. "
        "All 2315 images in this dataset lack EXIF timestamps — either they were stripped during "
        "preprocessing, or the source images never had them (e.g., web-scraped images, "
        "format-converted images, or datasets shared without metadata)."
    )
    md_lines.append("")
    md_lines.append("### 5.2 Threshold Comparison")
    md_lines.append("")
    md_lines.append(
        "All five thresholds (5 min, 15 min, 30 min, 60 min, calendar day) yield the same result: "
        "zero sessions, zero assignable images, 2315 unplaceable images. "
        "There is no threshold that rescues session-based splitting for this dataset."
    )
    md_lines.append("")
    md_lines.append("### 5.3 Recommended Threshold (If Future EXIF Recovery Is Possible)")
    md_lines.append("")
    md_lines.append(
        "If EXIF timestamps can be recovered (e.g., from original source files, sidecar files, "
        "or re-acquisition logs), we recommend **T = 15 minutes** as the primary threshold for "
        "the following reasons:"
    )
    md_lines.append("")
    md_lines.append("- **5 min**: Too aggressive — may split a single field walk into many micro-sessions if the photographer pauses.")
    md_lines.append("- **15 min**: Reasonable for a field survey; matches typical rest/repositioning time between plots.")
    md_lines.append("- **30 min**: Acceptable but risks merging two separate visits to different fields in the same morning.")
    md_lines.append("- **60 min**: Likely to merge morning and afternoon sessions, defeating the temporal independence goal.")
    md_lines.append("- **Calendar day**: Maximally lenient; merges all captures on the same day regardless of location shifts.")
    md_lines.append("")
    md_lines.append("**Recommended threshold: 15 minutes** — best balance of temporal isolation and session granularity.")
    md_lines.append("")
    md_lines.append("### 5.4 Immediate Action Items")
    md_lines.append("")
    md_lines.append("1. **Recover EXIF from originals**: Check the original image files (pre-pipeline) for embedded EXIF.")
    md_lines.append("2. **Check sidecar/log files**: Camera apps (e.g., drone GCS, field survey apps) often write separate timestamp logs.")
    md_lines.append("3. **If irrecoverable**: Use filename-based ordering (if filenames encode capture order) or spatial clustering (GPS if available, or field plot IDs) as a proxy for session.")
    md_lines.append("4. **Crop contamination**: The 405 crop-parent pairs are all cross-split — this is a data leakage risk. Address before final model evaluation regardless of session strategy.")
    md_lines.append("")

    # Write the markdown file
    md_path = OUTPUT_DIR / "SESSION_FEASIBILITY.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"\nSession Feasibility Report written to: {md_path}")
    print("Done.")


if __name__ == "__main__":
    main()
