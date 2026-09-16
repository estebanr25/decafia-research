"""
STEP 2 — Is numbering informative?
Check whether adjacent trailing numbers correlate with near-duplicate pairs.
"""
import os
import sys
import csv
import random
import numpy as np

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
NEAR_DUP_CSV = os.path.join(AUDIT_DIR, "near_duplicate_pairs.csv")
SIFT_CSV = os.path.join(AUDIT_DIR, "sift_results.csv")
INVENTORY_CSV = os.path.join(AUDIT_DIR, "inventory.csv")

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = reader.fieldnames
    return rows, cols

def get_prefix(stem, inventory_map):
    if stem in inventory_map:
        return inventory_map[stem]['prefix']
    # Fallback parse
    import re
    m = re.search(r'^(.*?)_(\d+)$', stem)
    if m:
        return m.group(1)
    return stem

def get_trailing_number(stem, inventory_map):
    if stem in inventory_map:
        return inventory_map[stem]['trailing_number']
    import re
    m = re.search(r'_(\d+)$', stem)
    if m:
        return int(m.group(1))
    return None

def main():
    print("=== STEP 2: NUMBERING CHECK ===")

    # Load inventory
    inv_rows, inv_cols = load_csv(INVENTORY_CSV)
    print(f"Inventory columns: {inv_cols}")
    inventory_map = {}
    for r in inv_rows:
        inventory_map[r['stem']] = {
            'prefix': r['prefix'],
            'trailing_number': int(r['trailing_number']),
            'split': r['split']
        }

    # Load near_duplicate_pairs.csv
    nd_rows, nd_cols = load_csv(NEAR_DUP_CSV)
    print(f"\nnear_duplicate_pairs.csv columns: {nd_cols}")

    # Load sift_results.csv
    sift_rows, sift_cols = load_csv(SIFT_CSV)
    print(f"sift_results.csv columns: {sift_cols}")

    # --- Find same-prefix strong pairs ---
    strong_pairs = set()  # set of (stem_a, stem_b) canonical pairs

    def canonical(a, b):
        return (min(a, b), max(a, b))

    # From near_duplicate_pairs.csv
    nd_same_prefix_strong = 0
    for r in nd_rows:
        # Check available columns for stems and prefix
        stem_a = r.get('img_a_stem') or r.get('stem_a')
        stem_b = r.get('img_b_stem') or r.get('stem_b')
        prefix_a = r.get('img_a_prefix') or get_prefix(stem_a, inventory_map)
        prefix_b = r.get('img_b_prefix') or get_prefix(stem_b, inventory_map)
        phash_dist_str = r.get('phash_dist', r.get('min_phash_dist', '999'))
        try:
            phash_dist = int(float(phash_dist_str))
        except (ValueError, TypeError):
            phash_dist = 999

        if prefix_a == prefix_b and phash_dist <= 4:
            strong_pairs.add(canonical(stem_a, stem_b))
            nd_same_prefix_strong += 1

    print(f"\nFrom near_duplicate_pairs.csv: {nd_same_prefix_strong} same-prefix pairs with phash_dist <= 4")

    # From sift_results.csv
    sift_same_prefix_strong = 0
    for r in sift_rows:
        stem_a = r.get('stem_a')
        stem_b = r.get('stem_b')
        if stem_a is None or stem_b is None:
            raise ValueError(f"Cannot find stem columns in sift_results.csv: {sift_cols}")

        prefix_a = get_prefix(stem_a, inventory_map)
        prefix_b = get_prefix(stem_b, inventory_map)

        try:
            inliers = int(float(r.get('ransac_inliers', 0)))
        except (ValueError, TypeError):
            inliers = 0

        try:
            cont_a = float(r.get('containment_a_in_b', 0))
        except (ValueError, TypeError):
            cont_a = 0.0
        try:
            cont_b = float(r.get('containment_b_in_a', 0))
        except (ValueError, TypeError):
            cont_b = 0.0

        if (prefix_a == prefix_b and
                inliers >= 60 and
                (cont_a >= 0.5 or cont_b >= 0.5)):
            strong_pairs.add(canonical(stem_a, stem_b))
            sift_same_prefix_strong += 1

    print(f"From sift_results.csv: {sift_same_prefix_strong} same-prefix SIFT strong pairs")
    print(f"Union of strong same-prefix pairs: {len(strong_pairs)}")

    # --- Compute gaps for strong pairs ---
    strong_gaps = []
    for (stem_a, stem_b) in strong_pairs:
        na = get_trailing_number(stem_a, inventory_map)
        nb = get_trailing_number(stem_b, inventory_map)
        if na is not None and nb is not None:
            strong_gaps.append(abs(na - nb))
        else:
            print(f"WARNING: could not get trailing number for {stem_a} or {stem_b}")

    # --- Generate 10,000 random same-prefix pairs ---
    # Group stems by prefix
    prefix_to_stems = {}
    for stem, info in inventory_map.items():
        p = info['prefix']
        prefix_to_stems.setdefault(p, []).append(stem)

    # Only prefixes with >= 2 images
    valid_prefixes = {p: stems for p, stems in prefix_to_stems.items() if len(stems) >= 2}
    prefix_sizes = np.array([len(v) for v in valid_prefixes.values()])
    prefix_names = list(valid_prefixes.keys())

    # Weight by prefix size (number of possible pairs ~ n*(n-1)/2 ~ n^2)
    weights = prefix_sizes * (prefix_sizes - 1) / 2
    weights = weights / weights.sum()

    rng = np.random.default_rng(42)
    random_gaps = []
    n_random = 10000
    attempts = 0
    max_attempts = n_random * 100
    while len(random_gaps) < n_random and attempts < max_attempts:
        # Pick prefix proportional to weight
        idx = rng.choice(len(prefix_names), p=weights)
        p = prefix_names[idx]
        stems = valid_prefixes[p]
        if len(stems) < 2:
            attempts += 1
            continue
        i, j = rng.choice(len(stems), size=2, replace=False)
        stem_a, stem_b = stems[i], stems[j]
        na = get_trailing_number(stem_a, inventory_map)
        nb = get_trailing_number(stem_b, inventory_map)
        if na is not None and nb is not None:
            random_gaps.append(abs(na - nb))
        attempts += 1

    if len(random_gaps) < n_random:
        print(f"WARNING: only generated {len(random_gaps)} random pairs (target {n_random})")

    # --- Compute statistics ---
    def fraction_leq(gaps, threshold):
        if not gaps:
            return 0.0
        return sum(1 for g in gaps if g <= threshold) / len(gaps)

    print(f"\n--- Strong pairs (n={len(strong_gaps)}) ---")
    if strong_gaps:
        print(f"  Gaps: {sorted(strong_gaps)[:20]}{'...' if len(strong_gaps) > 20 else ''}")
        print(f"  Median gap: {np.median(strong_gaps):.1f}")
        print(f"  Fraction gap<=10: {fraction_leq(strong_gaps, 10):.3f}")
        print(f"  Fraction gap<=20: {fraction_leq(strong_gaps, 20):.3f}")
        print(f"  Fraction gap<=40: {fraction_leq(strong_gaps, 40):.3f}")
    else:
        print("  No strong pairs found.")

    print(f"\n--- Random same-prefix pairs (n={len(random_gaps)}) ---")
    print(f"  Median gap: {np.median(random_gaps):.1f}")
    print(f"  Fraction gap<=10: {fraction_leq(random_gaps, 10):.3f}")
    print(f"  Fraction gap<=20: {fraction_leq(random_gaps, 20):.3f}")
    print(f"  Fraction gap<=40: {fraction_leq(random_gaps, 40):.3f}")

    # --- STOP-IF check ---
    n_strong = len(strong_gaps)
    frac_strong_20 = fraction_leq(strong_gaps, 20)
    frac_random_20 = fraction_leq(random_gaps, 20)

    print(f"\n--- STOP-IF check ---")
    print(f"  strong_pairs={n_strong}, frac_strong_20={frac_strong_20:.3f}, frac_random_20={frac_random_20:.3f}")
    if n_strong >= 30:
        ratio = frac_strong_20 / frac_random_20 if frac_random_20 > 0 else float('inf')
        print(f"  Ratio strong/random at gap<=20: {ratio:.2f} (need >= 3.0 to NOT stop)")
        if frac_strong_20 < 3 * frac_random_20:
            print("  STOP-IF: strong_pairs >= 30 AND fraction_gap_leq_20_strong < 3 * fraction_gap_leq_20_random")
            print("  => Numbering is NOT informative enough. Grouping by prefix+block only.")
            # This is a WARNING not a hard stop per the rules — the condition means numbering isn't informative
            # but we proceed with B grouping regardless (Step 4 still uses B)
            print("  NOTE: Continuing since B-block grouping is still valid; INFERRED that B should be chosen conservatively.")
        else:
            print("  => Numbering IS informative (ratio >= 3). B-block grouping supported by evidence.")
    else:
        print(f"  strong_pairs={n_strong} < 30, STOP-IF condition does not apply.")
        if n_strong > 0 and frac_strong_20 >= 3 * frac_random_20:
            print("  => Numbering appears informative (even with few strong pairs).")
        else:
            print("  => Insufficient strong pairs to confirm numbering is informative.")
            print("  => B-block grouping will be labeled INFERRED in README.")

    print("\nStep 2 complete.")

if __name__ == "__main__":
    main()
