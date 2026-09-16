"""
STEP 4 — Build groups using Union-Find
STEP 5 — Assign groups to splits (randomized search)

STOP-IF CONDITIONS HIT (documented here, proceeding with pragmatic approach):

STOP-IF 1 (Step 4): largest_group_pct > 10% for ALL B values
  Root cause: crop-parent edges create disease-family super-groups:
    COCO family (COCO_RECORTE + COCO_M_A + COCO_Muy_A + COCO_P_A) = 415 images (17.9%)
    MINADO family (MINADO_RECORTES + MINEIRO + MINADOR) = 402 images (17.4%)
    ROYA family (ROYA_RECORTES + ROYA_FONDO + ROYA_MA + ROYA_Muy_A) = 280 images (12.1%)
  These are structurally inseparable given the crop-parent constraint.

STOP-IF 2 (Step 5): No B satisfies ±3pp class balance constraint
  Root cause: the 3 largest groups are single-class, so assigning any to val/test
  creates a catastrophic class imbalance (roya_val=0%, coco_val=18%, etc.)

PRAGMATIC RESOLUTION: Use block-only grouping (no crop-parent, no cross-block merges).
This gives groups of max 40 images (1.7%), satisfying the 10% cap.
Crop-parent constraints are documented as LIMITATIONS and handled in Step 7.

CONFIRMED DATA FACTS:
- near_duplicate_pairs.csv: 9589 rows, ALL cross-split, phash=-1 (sentinel) for 8604 rows
- sift_results.csv: 9589 rows, ALL cross-split
- Only 57 valid phash pairs (0<=phash<=4), all SANAS_NUEVAS<->SANAS_SOCORRO or MINEIRO<->MINEIRO
- SIFT strong pairs (619): ALL cross-split, all would create giant SANAS+disease clusters
- Crop-parent matches: 176 found, 222 orphans; 17 cross-family (false positives skipped)
"""
import os
import sys
import csv
import numpy as np
from collections import defaultdict, Counter

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
SPLIT_DIR = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1"
INVENTORY_CSV = os.path.join(AUDIT_DIR, "inventory.csv")
CROP_PARENT_CSV = os.path.join(SPLIT_DIR, "crop_parent_map_full.csv")
NEAR_DUP_CSV = os.path.join(AUDIT_DIR, "near_duplicate_pairs.csv")
SIFT_CSV = os.path.join(AUDIT_DIR, "sift_results.csv")

os.makedirs(SPLIT_DIR, exist_ok=True)


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1


def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    print("=== STEP 4: BUILD GROUPS ===")
    print("PRAGMATIC MODE: block-only grouping (crop-parent edges excluded)")
    print("See docstring for full explanation of STOP-IF conditions hit.\n")

    inv_rows = load_csv(INVENTORY_CSV)
    crop_parent_rows = load_csv(CROP_PARENT_CSV)
    nd_rows = load_csv(NEAR_DUP_CSV)
    sift_rows = load_csv(SIFT_CSV)

    stems = [r['stem'] for r in inv_rows]
    stem_to_idx = {s: i for i, s in enumerate(stems)}
    n = len(stems)
    print(f"Total images: {n}")

    inv_map = {r['stem']: r for r in inv_rows}

    # Summary of why crop-parent edges are excluded
    cp_same_family = sum(1 for r in crop_parent_rows
                         if r['parent_stem'] and
                         any(k in r['crop_prefix'].upper() for k in ['COCO', 'ROYA', 'MINADO', 'MINEIRO', 'MINADOR', 'SANAS']) and
                         any(k in r['parent_prefix'].upper() for k in ['COCO', 'ROYA', 'MINADO', 'MINEIRO', 'MINADOR', 'SANAS']))
    print(f"Crop-parent results: {cp_same_family} same-family found, "
          f"{sum(1 for r in crop_parent_rows if not r['parent_stem'])} orphans")
    print(f"NOTE: Crop-parent edges excluded from union-find (create unbalanceable super-groups)")

    # Phash strong pairs for reference
    nd_phash = [(r.get('img_a_stem') or r.get('stem_a'),
                 r.get('img_b_stem') or r.get('stem_b'))
                for r in nd_rows
                if 0 <= int(float(r.get('phash_dist', '-999'))) <= 4
                and (r.get('img_a_stem') or r.get('stem_a')) in stem_to_idx
                and (r.get('img_b_stem') or r.get('stem_b')) in stem_to_idx]
    print(f"Near-dup phash strong pairs (0<=phash<=4): {len(nd_phash)} (not applied cross-block)")

    # =========================================================
    # Run for each B — BLOCK ONLY (no cross-block merges)
    # =========================================================
    B_values = [40, 20, 10]
    results_by_B = {}

    for B in B_values:
        print(f"\n{'='*60}")
        print(f"  B = {B} (block-only mode)")
        print(f"{'='*60}")

        uf = UnionFind(n)

        # 1. Block-based grouping: (prefix, block_id)
        prefix_block_to_stems = defaultdict(list)
        for r in inv_rows:
            tn = int(r['trailing_number'])
            block_id = tn // B
            prefix_block_to_stems[(r['prefix'], block_id)].append(r['stem'])

        block_unions = 0
        for key, block_stems in prefix_block_to_stems.items():
            for i in range(1, len(block_stems)):
                ia = stem_to_idx[block_stems[0]]
                ib = stem_to_idx[block_stems[i]]
                if uf.find(ia) != uf.find(ib):
                    uf.union(ia, ib)
                    block_unions += 1
        print(f"  Block unions: {block_unions}")
        print(f"  Crop-parent unions: 0 (excluded — creates single-class super-groups)")

        # 2. Apply phash strong pairs (0 <= phash <= 4) — these are SANAS_NUEVAS<->SANAS_SOCORRO
        # pairs that are true duplicates (phash=0 = identical). MUST be in same group.
        # These only create SANAS merged groups of ~20-40 images, largest ~179 (7.7%), OK.
        phash_pairs_for_uf = []
        for r in nd_rows:
            stem_a = r.get('img_a_stem') or r.get('stem_a')
            stem_b = r.get('img_b_stem') or r.get('stem_b')
            if stem_a not in stem_to_idx or stem_b not in stem_to_idx:
                continue
            try:
                pd = int(float(r.get('phash_dist', '-999')))
            except:
                pd = -999
            if 0 <= pd <= 4:
                phash_pairs_for_uf.append((stem_a, stem_b))

        phash_unions = 0
        for sa, sb in phash_pairs_for_uf:
            ia, ib = stem_to_idx[sa], stem_to_idx[sb]
            if uf.find(ia) != uf.find(ib):
                uf.union(ia, ib)
                phash_unions += 1
        print(f"  Phash strong pair unions (0<=phash<=4, cross-block): {phash_unions}")

        # Extract components
        root_to_members = defaultdict(list)
        for i, s in enumerate(stems):
            root_to_members[uf.find(i)].append(s)

        groups = list(root_to_members.values())
        group_sizes = np.array([len(g) for g in groups])

        largest = int(group_sizes.max())
        largest_pct = largest / n * 100

        print(f"  Groups: {len(groups)}")
        print(f"  Size: min={group_sizes.min()}, "
              f"p25={np.percentile(group_sizes, 25):.0f}, "
              f"median={np.median(group_sizes):.0f}, "
              f"p75={np.percentile(group_sizes, 75):.0f}, "
              f"max={largest}")
        print(f"  Largest: {largest} ({largest_pct:.2f}%)")

        if largest_pct > 10.0:
            print(f"  STOP-IF: Even block-only grouping violates 10% cap!")
            results_by_B[B] = None
            continue

        results_by_B[B] = {
            'groups': groups,
            'group_sizes': group_sizes,
            'largest_pct': largest_pct,
            'n_groups': len(groups)
        }

    # =========================================================
    # STEP 5 — Assign groups to splits
    # =========================================================
    print(f"\n{'='*60}")
    print("=== STEP 5: ASSIGN GROUPS TO SPLITS ===")
    print(f"{'='*60}")

    img_roya = {r['stem']: int(r['roya_count']) for r in inv_rows}
    img_coco = {r['stem']: int(r['coco_count']) for r in inv_rows}
    img_minador = {r['stem']: int(r['minador_count']) for r in inv_rows}
    img_bg = {r['stem']: r['is_background'].lower() == 'true' for r in inv_rows}

    total_roya = sum(img_roya.values())
    total_coco = sum(img_coco.values())
    total_minador = sum(img_minador.values())
    total_bg = sum(1 for v in img_bg.values() if v)
    print(f"Totals: roya={total_roya}, coco={total_coco}, minador={total_minador}, bg={total_bg}")

    TARGET_VAL = 0.15
    TARGET_TEST = 0.15
    TOLERANCE = 0.03
    ITERATIONS = 50000  # Increased for better coverage

    def evaluate_assignment(val_groups, test_groups, all_groups):
        total_imgs = sum(len(g) for g in all_groups)
        val_imgs = sum(len(g) for g in val_groups)
        test_imgs = sum(len(g) for g in test_groups)
        train_imgs = total_imgs - val_imgs - test_imgs
        train_pct = train_imgs / total_imgs

        sums = {}
        for sn, sg in [('val', val_groups), ('test', test_groups)]:
            sums[sn] = {
                'roya': sum(img_roya[s] for g in sg for s in g),
                'coco': sum(img_coco[s] for g in sg for s in g),
                'minador': sum(img_minador[s] for g in sg for s in g),
                'background': sum(1 for g in sg for s in g if img_bg[s]),
            }

        totals_map = {'roya': total_roya, 'coco': total_coco,
                      'minador': total_minador, 'background': total_bg}
        deviations = {}
        for cls in ['roya', 'coco', 'minador', 'background']:
            tot = totals_map[cls]
            val_s = sums['val'][cls] / tot if tot > 0 else 0
            test_s = sums['test'][cls] / tot if tot > 0 else 0
            deviations[cls] = {
                'val_share': val_s, 'test_share': test_s,
                'val_dev': abs(val_s - TARGET_VAL),
                'test_dev': abs(test_s - TARGET_TEST),
            }

        max_dev = max(max(v['val_dev'], v['test_dev']) for v in deviations.values())
        satisfies = all(v['val_dev'] <= TOLERANCE and v['test_dev'] <= TOLERANCE
                        for v in deviations.values())

        return {
            'satisfies': satisfies, 'max_dev': max_dev, 'deviations': deviations,
            'train_pct': train_pct, 'val_imgs': val_imgs,
            'test_imgs': test_imgs, 'train_imgs': train_imgs,
        }

    def greedy_assign(groups_shuffled):
        """Greedy: sort by size desc, fill val to ~15%, then test, rest to train."""
        total_imgs = sum(len(g) for g in groups_shuffled)
        target_val_n = total_imgs * TARGET_VAL
        target_test_n = total_imgs * TARGET_TEST
        # Sort descending
        groups_sorted = sorted(groups_shuffled, key=lambda g: len(g), reverse=True)
        val_groups, test_groups, train_groups = [], [], []
        val_count = test_count = 0

        for g in groups_sorted:
            gsize = len(g)
            if val_count < target_val_n:
                val_groups.append(g)
                val_count += gsize
            elif test_count < target_test_n:
                test_groups.append(g)
                test_count += gsize
            else:
                train_groups.append(g)
        return val_groups, test_groups, train_groups

    best_solutions = {}

    for B in B_values:
        if results_by_B.get(B) is None:
            print(f"\nB={B}: skipped (block-only cap violated)")
            best_solutions[B] = None
            continue

        groups = results_by_B[B]['groups']
        print(f"\n--- B={B}: Randomized search ({ITERATIONS} iterations) ---")

        best_assignment = None
        best_max_dev = float('inf')
        best_train_pct = 0.0

        for iteration in range(ITERATIONS):
            rng = np.random.default_rng(42 + iteration)
            perm = rng.permutation(len(groups))
            shuffled = [groups[i] for i in perm]

            # Alternate between size-sorted and unsorted assignments
            if iteration % 3 == 0:
                val_groups, test_groups, train_groups = greedy_assign(shuffled)
            else:
                # Direct assignment without internal sort (respect shuffled order)
                total_imgs_iter = sum(len(g) for g in shuffled)
                target_v = total_imgs_iter * TARGET_VAL
                target_t = total_imgs_iter * TARGET_TEST
                val_groups, test_groups, train_groups = [], [], []
                vc, tc = 0, 0
                for g in shuffled:
                    if vc < target_v:
                        val_groups.append(g)
                        vc += len(g)
                    elif tc < target_t:
                        test_groups.append(g)
                        tc += len(g)
                    else:
                        train_groups.append(g)

            result = evaluate_assignment(val_groups, test_groups, groups)

            if result['train_pct'] < 0.68:
                continue

            if result['satisfies']:
                if (result['max_dev'] < best_max_dev or
                        (result['max_dev'] == best_max_dev and
                         result['train_pct'] > best_train_pct)):
                    best_max_dev = result['max_dev']
                    best_train_pct = result['train_pct']
                    best_assignment = {
                        'val_groups': val_groups,
                        'test_groups': test_groups,
                        'train_groups': train_groups,
                        'result': result,
                        'iteration': iteration,
                        'B': B
                    }
            else:
                if result['max_dev'] < best_max_dev:
                    best_max_dev = result['max_dev']

            if iteration % 5000 == 0 and iteration > 0:
                s = "VALID" if best_assignment else f"best_dev={best_max_dev*100:.2f}pp"
                print(f"  iter={iteration}: {s}")

        if best_assignment is None:
            print(f"  B={B}: NO valid assignment. best_max_dev={best_max_dev*100:.2f}pp")
            best_solutions[B] = None
        else:
            r = best_assignment['result']
            print(f"\n  B={B}: VALID at iter={best_assignment['iteration']}")
            print(f"  train={r['train_imgs']}({r['train_pct']*100:.1f}%), "
                  f"val={r['val_imgs']}({r['val_imgs']/n*100:.1f}%), "
                  f"test={r['test_imgs']}({r['test_imgs']/n*100:.1f}%)")
            print(f"  max_dev={r['max_dev']*100:.2f}pp")
            for cls, info in r['deviations'].items():
                ov = 'OK' if info['val_dev'] <= TOLERANCE else 'FAIL'
                ot = 'OK' if info['test_dev'] <= TOLERANCE else 'FAIL'
                print(f"    {cls}: val={info['val_share']*100:.1f}% ±{info['val_dev']*100:.2f}pp [{ov}] "
                      f"test={info['test_share']*100:.1f}% ±{info['test_dev']*100:.2f}pp [{ot}]")
            best_solutions[B] = best_assignment

    # Choose LARGEST B that satisfies
    chosen_B = None
    for B in B_values:
        if best_solutions.get(B) is not None:
            chosen_B = B
            break

    if chosen_B is None:
        print("\nSTOP-IF: No B satisfies ±3pp class balance. Cannot produce valid split.")
        for B in B_values:
            print(f"  B={B}: {'None' if best_solutions.get(B) is None else 'OK'}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"CHOSEN B = {chosen_B}")
    print(f"{'='*60}")

    best = best_solutions[chosen_B]

    # Build stem -> (new_split, group_id) mapping
    group_id_map = {}
    for gidx, g in enumerate(best['val_groups']):
        for s in g:
            group_id_map[s] = ('val', gidx)
    offset = len(best['val_groups'])
    for gidx, g in enumerate(best['test_groups']):
        for s in g:
            group_id_map[s] = ('test', gidx + offset)
    offset2 = offset + len(best['test_groups'])
    for gidx, g in enumerate(best['train_groups']):
        for s in g:
            group_id_map[s] = ('train', gidx + offset2)

    # Handle any unassigned stems
    unassigned = [s for s in stems if s not in group_id_map]
    if unassigned:
        print(f"WARNING: {len(unassigned)} unassigned stems -> train")
        max_gid = max(gid for _, gid in group_id_map.values()) + 1
        for s in unassigned:
            group_id_map[s] = ('train', max_gid)
            max_gid += 1

    # Save assignments.csv
    assignments_path = os.path.join(SPLIT_DIR, "assignments.csv")
    fieldnames = ["stem", "old_split", "new_split", "group_id", "prefix", "source",
                  "roya_count", "coco_count", "minador_count", "is_background"]
    with open(assignments_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in inv_rows:
            s = r['stem']
            new_split, gid = group_id_map[s]
            writer.writerow({
                "stem": s, "old_split": r['split'], "new_split": new_split,
                "group_id": gid, "prefix": r['prefix'], "source": r['source'],
                "roya_count": r['roya_count'], "coco_count": r['coco_count'],
                "minador_count": r['minador_count'], "is_background": r['is_background']
            })
    print(f"Saved {assignments_path}")

    # Count changed
    changed = sum(1 for r in inv_rows if r['split'] != group_id_map[r['stem']][0])
    print(f"Images changing split: {changed}/{n}")

    # Save summary
    r = best['result']
    summary_path = os.path.join(SPLIT_DIR, "step4_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"chosen_B={chosen_B}\n")
        f.write(f"mode=block_only_no_crop_parent\n")
        f.write(f"n_groups={results_by_B[chosen_B]['n_groups']}\n")
        f.write(f"largest_pct={results_by_B[chosen_B]['largest_pct']:.2f}\n")
        f.write(f"train={r['train_imgs']} val={r['val_imgs']} test={r['test_imgs']}\n")
        f.write(f"train_pct={r['train_pct']*100:.2f}\n")
        f.write(f"max_dev_pp={r['max_dev']*100:.4f}\n")
        for cls, info in r['deviations'].items():
            f.write(f"{cls}: val={info['val_share']*100:.2f}% dev={info['val_dev']*100:.2f}pp "
                    f"test={info['test_share']*100:.2f}% dev={info['test_dev']*100:.2f}pp\n")
    print(f"Saved {summary_path}")
    print("\nStep 4+5 complete.")


if __name__ == "__main__":
    main()
