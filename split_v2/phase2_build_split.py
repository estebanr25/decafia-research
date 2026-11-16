"""
Phase 2: Build split_grouped_v2
SESSION_SPLIT_V2 - DECAFIA Paper 1

Uses union-find to merge v1 groups with Phase 1 copy pairs.
Minimal movement: each component stays with its majority split.
Checks Path A conditions.
"""

import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import random

REPO         = Path("C:/Users/luise/temp/decafia-research")
SPLIT_V2_DIR = REPO / "split_v2"
CACHE_DIR    = REPO / "_cache"

PROGRESS_FILE = SPLIT_V2_DIR / "PROGRESS.md"

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

update_progress(**{"Phase 2 - build split_v2": "in_progress"})

# ── 1. Load data ──────────────────────────────────────────────────────────────
log("=== Phase 2: Build split_grouped_v2 ===")

assign_df = pd.read_csv(REPO / "splits/grouped_v1/assignments.csv")
assign_df = assign_df.rename(columns={"split_new": "split_v1", "split_old": "split_disk"})

copy_pairs = pd.read_csv(SPLIT_V2_DIR / "copy_pairs.csv")

stems  = assign_df["stem"].tolist()
N      = len(stems)
stem_to_idx = {s: i for i, s in enumerate(stems)}

# V1 split and group
stem_to_split_v1 = dict(zip(assign_df["stem"], assign_df["split_v1"]))
stem_to_group    = dict(zip(assign_df["stem"], assign_df["group_root"]))
stem_to_prefix   = dict(zip(assign_df["stem"], assign_df["prefix"]))
stem_to_source   = dict(zip(assign_df["stem"], assign_df["source"]))
stem_to_roya     = dict(zip(assign_df["stem"], assign_df["roya"]))
stem_to_coco     = dict(zip(assign_df["stem"], assign_df["coco"]))
stem_to_minador  = dict(zip(assign_df["stem"], assign_df["minador"]))

log(f"Loaded {N} images, {assign_df['group_root'].nunique()} v1 groups")

# ── 2. Union-Find ─────────────────────────────────────────────────────────────
parent = list(range(N))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(x, y):
    px, py = find(x), find(y)
    if px != py:
        parent[px] = py

# Step A: union all images in the same v1 group
groups = defaultdict(list)
for stem, grp in stem_to_group.items():
    if stem in stem_to_idx:
        groups[grp].append(stem_to_idx[stem])

for grp, idxs in groups.items():
    for idx in idxs[1:]:
        union(idxs[0], idx)

v1_components_before = len(set(find(i) for i in range(N)))
log(f"After v1 group merging: {v1_components_before} components")

# Step B: union merged cross-split pairs
merged_pairs = copy_pairs[copy_pairs["decision"] == "merge"].copy()
n_merged_cross = 0
for _, row in merged_pairs.iterrows():
    a, b = row["stem_a"], row["stem_b"]
    if a in stem_to_idx and b in stem_to_idx:
        ia, ib = stem_to_idx[a], stem_to_idx[b]
        if find(ia) != find(ib):
            union(ia, ib)
            if str(row.get("cross_split", False)).lower() == "true":
                n_merged_cross += 1

v2_components = len(set(find(i) for i in range(N)))
log(f"After merging copies: {v2_components} components (from {v1_components_before})")
log(f"Cross-split merged pair edges applied: {n_merged_cross}")

# ── 3. Build component info ───────────────────────────────────────────────────
comp_members = defaultdict(list)  # root -> [stem_indices]
for i in range(N):
    comp_members[find(i)].append(i)

# Component sizes
comp_sizes = {root: len(members) for root, members in comp_members.items()}
size_array  = np.array(sorted(comp_sizes.values(), reverse=True))
log(f"\nComponent size stats:")
log(f"  min={size_array.min()}, median={np.median(size_array):.1f}, max={size_array.max()}")
log(f"  components > 10% of dataset (>={int(0.1*N)}): {(size_array >= int(0.1*N)).sum()}")

# Check Path A condition 2: no component exceeds 10% of dataset
max_component = int(size_array.max())
pa_cond2 = max_component < int(0.1 * N)
log(f"Path A cond 2 (max component < {int(0.1*N)}): {'PASS' if pa_cond2 else 'FAIL'} (max={max_component})")

# ── 4. Assign components to splits (minimal movement) ────────────────────────
log("\nAssigning components to splits (minimal movement)...")

TARGET_FRACS = {"train": 0.681, "val": 0.165, "test": 0.154}
TOLERANCE    = 0.02  # 2 percentage points

def assign_components_min_movement(comp_members, stems, stem_to_split_v1, N):
    """Assign each component to its majority v1 split."""
    comp_split = {}
    for root, idxs in comp_members.items():
        split_counts = Counter(stem_to_split_v1[stems[i]] for i in idxs)
        # Majority wins; ties go to train
        majority = max(split_counts, key=lambda s: (split_counts[s], s == "train"))
        comp_split[root] = majority
    return comp_split

comp_split = assign_components_min_movement(comp_members, stems, stem_to_split_v1, N)

# Count images per split
split_counts = Counter()
for root, idxs in comp_members.items():
    for i in idxs:
        split_counts[comp_split[root]] += 1

log(f"Initial assignment counts: {dict(split_counts)}")
for s, n in split_counts.items():
    log(f"  {s}: {n}/{N} = {100*n/N:.1f}% (target {100*TARGET_FRACS[s]:.1f}%)")

# Check tolerance
rebalance_needed = False
rebalance_reasons = []
for s, target_frac in TARGET_FRACS.items():
    actual_frac = split_counts[s] / N
    drift = abs(actual_frac - target_frac)
    if drift > TOLERANCE:
        rebalance_needed = True
        rebalance_reasons.append(f"{s}: actual={actual_frac:.3f}, target={target_frac:.3f}, drift={drift:.3f}")

if rebalance_needed:
    log(f"\nRebalance needed: {rebalance_reasons}")
    # Rebalance by moving whole unmerged groups
    # (groups that have no copy-pair merges across their members are "unmerged")
    # Find components that only have v1-intra-group members (no cross-group merging from copies)
    # Simple approach: find smallest components first

    # Get components that are "single-group" (can be moved)
    # A component is movable if all its stems share the same v1 group_root
    def component_is_movable(idxs, stems, stem_to_group):
        groups_in_comp = set(stem_to_group[stems[i]] for i in idxs)
        return len(groups_in_comp) == 1

    movable = {root: idxs for root, idxs in comp_members.items()
               if component_is_movable(idxs, stems, stem_to_group)}
    log(f"Movable components (single v1 group): {len(movable)}")

    # Try to rebalance: target train ~68.1%, val ~16.5%, test ~15.4%
    target_counts = {s: int(TARGET_FRACS[s] * N) for s in TARGET_FRACS}
    rng = random.Random(42)

    for attempt in range(2):
        # Sort movable by size (smallest first for fine-grained rebalance)
        movable_sorted = sorted(movable.items(), key=lambda x: len(x[1]))

        for root, idxs in movable_sorted:
            current_split = comp_split[root]
            n_comp = len(idxs)
            current_actual = {s: 0 for s in TARGET_FRACS}
            for r, ilist in comp_members.items():
                current_actual[comp_split[r]] += len(ilist)

            # Find if moving this component to another split helps
            best_move = None
            best_score = sum(abs(current_actual[s] - target_counts[s]) for s in TARGET_FRACS)

            for new_split in TARGET_FRACS:
                if new_split == current_split:
                    continue
                # Hypothetical counts
                hyp = current_actual.copy()
                hyp[current_split] -= n_comp
                hyp[new_split]     += n_comp
                score = sum(abs(hyp[s] - target_counts[s]) for s in TARGET_FRACS)
                if score < best_score:
                    best_score = score
                    best_move  = new_split

            if best_move is not None:
                comp_split[root] = best_move

        # Recount
        split_counts = Counter()
        for root, idxs in comp_members.items():
            for i in idxs:
                split_counts[comp_split[root]] += 1

        # Check tolerance again
        rebalance_needed = False
        rebalance_reasons = []
        for s, target_frac in TARGET_FRACS.items():
            actual_frac = split_counts[s] / N
            drift = abs(actual_frac - target_frac)
            if drift > TOLERANCE:
                rebalance_needed = True
                rebalance_reasons.append(f"{s}: {actual_frac:.3f} vs {target_frac:.3f} (drift {drift:.3f})")

        log(f"After rebalance attempt {attempt+1}: {dict(split_counts)}")
        if not rebalance_needed:
            log("Tolerance satisfied after rebalancing.")
            break

    if rebalance_needed:
        log(f"[WARN] Still out of tolerance after 2 attempts: {rebalance_reasons}")
else:
    log("Within tolerance, no rebalancing needed.")

# ── 5. Build stem -> split_v2 mapping ─────────────────────────────────────────
stem_to_split_v2 = {}
for root, idxs in comp_members.items():
    s = comp_split[root]
    for i in idxs:
        stem_to_split_v2[stems[i]] = s

# ── 6. Check per-class test instances ─────────────────────────────────────────
log("\nChecking per-class test instances in v2...")
test_stems_v2 = [s for s, sp in stem_to_split_v2.items() if sp == "test"]
test_roya     = sum(stem_to_roya.get(s, 0) for s in test_stems_v2)
test_coco     = sum(stem_to_coco.get(s, 0) for s in test_stems_v2)
test_minador  = sum(stem_to_minador.get(s, 0) for s in test_stems_v2)

log(f"Test set v2: {len(test_stems_v2)} images")
log(f"  roya instances:    {test_roya}")
log(f"  coco instances:    {test_coco}")
log(f"  minador instances: {test_minador}")

pa_cond3 = all(x >= 100 for x in [test_roya, test_coco, test_minador])
log(f"Path A cond 3 (all classes >=100 test instances): {'PASS' if pa_cond3 else 'FAIL'}")

# ── 7. Final split counts and proportions ─────────────────────────────────────
final_split_counts = Counter(stem_to_split_v2.values())
log(f"\nFinal v2 split counts: {dict(final_split_counts)}")
pa_cond4 = True
for s, target_frac in TARGET_FRACS.items():
    actual_frac = final_split_counts[s] / N
    drift = abs(actual_frac - target_frac)
    if drift > TOLERANCE:
        pa_cond4 = False
    log(f"  {s}: {final_split_counts[s]} ({100*actual_frac:.1f}% vs target {100*target_frac:.1f}%, drift {100*drift:.2f}pp)")
log(f"Path A cond 4 (proportions within 2pp): {'PASS' if pa_cond4 else 'FAIL'}")

# ── 8. Write split files ───────────────────────────────────────────────────────
log("\nWriting v2 split files...")
SPLITS_V2_DIR = REPO / "splits/split_grouped_v2"
SPLITS_V2_DIR.mkdir(parents=True, exist_ok=True)

stem_to_disk = dict(zip(assign_df["stem"], assign_df["split_disk"]))

for split_name in ["train", "val", "test"]:
    split_stems = sorted([s for s, sp in stem_to_split_v2.items() if sp == split_name])
    with open(SPLITS_V2_DIR / f"{split_name}.txt", "w") as f:
        for stem in split_stems:
            disk = stem_to_disk[stem]
            f.write(f"images/{disk}/{stem}.jpg\n")
    log(f"  {split_name}.txt: {len(split_stems)} images")

# Write assignments_v2.csv
assign_df["split_v2"] = assign_df["stem"].map(stem_to_split_v2)
assign_df["comp_root"] = assign_df["stem"].apply(lambda s: stems[find(stem_to_idx[s])])
assign_df.to_csv(SPLIT_V2_DIR / "assignments_v2.csv", index=False)
log(f"assignments_v2.csv written")

# ── 9. Write data YAML ────────────────────────────────────────────────────────
# Resolve the absolute path to the split_v2 directory
abs_splits = SPLITS_V2_DIR.resolve()
dataset_root = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
yaml_content = f"""# DECAFIA grouped split v2 - data configuration (auto-generated by phase2_build_split.py)
path: {dataset_root}
train: {abs_splits}/train.txt
val:   {abs_splits}/val.txt
test:  {abs_splits}/test.txt
nc: 3
names:
  0: roya
  1: coco
  2: minador
"""
(SPLIT_V2_DIR / "data_grouped_v2.yaml").write_text(yaml_content)
log("data_grouped_v2.yaml written")

# ── 10. Verify v2: zero merged-tier cross-split pairs ─────────────────────────
log("\nVerifying v2: checking for zero merged-tier cross-split pairs...")
# Load Phase 1 merged pairs
merged_cross = copy_pairs[(copy_pairs["decision"] == "merge") &
                          (copy_pairs["stem_a"].isin(stem_to_split_v2)) &
                          (copy_pairs["stem_b"].isin(stem_to_split_v2))].copy()
merged_cross["new_split_a"] = merged_cross["stem_a"].map(stem_to_split_v2)
merged_cross["new_split_b"] = merged_cross["stem_b"].map(stem_to_split_v2)
remaining_cross = merged_cross[merged_cross["new_split_a"] != merged_cross["new_split_b"]]

pa_cond1 = len(remaining_cross) == 0
log(f"Remaining cross-split merged pairs in v2: {len(remaining_cross)}")
log(f"Path A cond 1 (zero cross-split copies): {'PASS' if pa_cond1 else 'FAIL'}")
if not remaining_cross.empty:
    log("FAILING PAIRS:")
    print(remaining_cross[["stem_a", "new_split_a", "stem_b", "new_split_b"]].to_string())

# ── 11. Path A / Path B decision ──────────────────────────────────────────────
path_a_conditions = {
    "cond1_zero_cross_split_copies": pa_cond1,
    "cond2_max_component_lt_10pct":  pa_cond2,
    "cond3_all_classes_ge_100_test": pa_cond3,
    "cond4_proportions_within_2pp":  pa_cond4,
}
path_a = all(path_a_conditions.values())
path_chosen = "A" if path_a else "B"
failing = [k for k, v in path_a_conditions.items() if not v]

log(f"\nPath A conditions: {path_a_conditions}")
log(f"PATH CHOSEN: {path_chosen}")
if failing:
    log(f"Failing conditions: {failing}")

# ── 12. Component size distribution ───────────────────────────────────────────
size_hist = Counter(len(idxs) for idxs in comp_members.values())
size_hist_sorted = dict(sorted(size_hist.items()))

# Count images moved from v1 to v2 per split
moved = sum(1 for s in stems if stem_to_split_v1[s] != stem_to_split_v2[s])
log(f"\nImages moved from v1 split: {moved}/{N}")

# Per-class instance counts in v2 splits
class_split_counts = defaultdict(lambda: defaultdict(int))
for stem in stems:
    sp = stem_to_split_v2[stem]
    class_split_counts["roya"][sp]  += stem_to_roya.get(stem, 0)
    class_split_counts["coco"][sp]  += stem_to_coco.get(stem, 0)
    class_split_counts["minador"][sp] += stem_to_minador.get(stem, 0)
    class_split_counts["images"][sp] += 1

log("\nPer-class split counts v2:")
for cls in ["roya", "coco", "minador", "images"]:
    log(f"  {cls}: {dict(class_split_counts[cls])}")

# ── 13. Write SPLIT_V2.md ─────────────────────────────────────────────────────
log("\nWriting SPLIT_V2.md...")

split_v1_counts = Counter(assign_df["split_v1"])

split_v2_md = f"""# SPLIT_V2.md

Auto-generated by phase2_build_split.py

## Split counts

| Split | v1 images | v2 images | Change |
|-------|-----------|-----------|--------|
| train | {split_v1_counts['train']} | {final_split_counts['train']} | {final_split_counts['train'] - split_v1_counts['train']:+d} |
| val   | {split_v1_counts['val']}   | {final_split_counts['val']}   | {final_split_counts['val']   - split_v1_counts['val']:+d}   |
| test  | {split_v1_counts['test']}  | {final_split_counts['test']}  | {final_split_counts['test']  - split_v1_counts['test']:+d}  |
| total | {N}  | {N}  | 0 |

## Images moved: {moved}/{N}

## Per-class instance counts in v2

| Class   | train | val | test |
|---------|-------|-----|------|
| roya    | {class_split_counts['roya']['train']} | {class_split_counts['roya']['val']} | {class_split_counts['roya']['test']} |
| coco    | {class_split_counts['coco']['train']} | {class_split_counts['coco']['val']} | {class_split_counts['coco']['test']} |
| minador | {class_split_counts['minador']['train']} | {class_split_counts['minador']['val']} | {class_split_counts['minador']['test']} |

## Component size distribution (top 20 by size)

{chr(10).join(f"  size {s}: {c} components" for s, c in sorted(size_hist.items(), key=lambda x: -x[0])[:20])}

## Path A conditions

| Condition | Result |
|-----------|--------|
| 1. Zero cross-split copies in v2 | {'PASS' if pa_cond1 else 'FAIL'} |
| 2. Max component < 10% ({int(0.1*N)} images) | {'PASS (max='+str(max_component)+')' if pa_cond2 else 'FAIL (max='+str(max_component)+')'} |
| 3. All classes >= 100 test instances | {'PASS' if pa_cond3 else 'FAIL'} (roya={test_roya}, coco={test_coco}, minador={test_minador}) |
| 4. Proportions within 2pp | {'PASS' if pa_cond4 else 'FAIL'} |

## **PATH CHOSEN: {path_chosen}**
{'All conditions pass.' if path_a else f'Failing: {failing}'}
"""

(SPLIT_V2_DIR / "SPLIT_V2.md").write_text(split_v2_md)
log("SPLIT_V2.md written")

# ── 14. Save path decision to JSON ────────────────────────────────────────────
path_decision = {
    "path_chosen": path_chosen,
    "conditions":  path_a_conditions,
    "failing":     failing,
    "split_counts_v2": dict(final_split_counts),
    "images_moved": moved,
    "max_component": max_component,
    "test_instances": {"roya": int(test_roya), "coco": int(test_coco), "minador": int(test_minador)},
}
(SPLIT_V2_DIR / "path_decision.json").write_text(json.dumps(path_decision, indent=2))
log(f"path_decision.json written")

update_progress(**{"Phase 2 - build split_v2": "COMPLETE", "Path chosen": path_chosen})
log("\n=== Phase 2 complete ===")
log(f"PATH: {path_chosen} | splits: {dict(final_split_counts)} | moved: {moved}")
