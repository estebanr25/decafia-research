"""
Debug: understand the near-dup network structure.
"""
import csv
from collections import defaultdict, Counter

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
NEAR_DUP_CSV = AUDIT_DIR + "/near_duplicate_pairs.csv"
SIFT_CSV = AUDIT_DIR + "/sift_results.csv"
INVENTORY_CSV = AUDIT_DIR + "/inventory.csv"

with open(INVENTORY_CSV, newline='', encoding='utf-8') as f:
    inv = {r['stem']: r for r in csv.DictReader(f)}

with open(NEAR_DUP_CSV, newline='', encoding='utf-8') as f:
    nd_rows = list(csv.DictReader(f))

with open(SIFT_CSV, newline='', encoding='utf-8') as f:
    sift_rows = list(csv.DictReader(f))

print(f"Total near-dup pairs: {len(nd_rows)}")
print(f"Total SIFT rows: {len(sift_rows)}")

# Distribution of phash_dist in near_dup_pairs
phash_dists = []
for r in nd_rows:
    try:
        d = int(float(r.get('phash_dist', r.get('min_phash_dist', '999'))))
        phash_dists.append(d)
    except:
        pass

from collections import Counter
dist_counter = Counter(phash_dists)
print("\nphash_dist distribution:")
for d in sorted(dist_counter.keys())[:20]:
    print(f"  {d}: {dist_counter[d]}")

# Count pairs with phash <= 4 by prefix
strong_pairs_by_prefix = defaultdict(int)
cross_prefix_strong = 0
for r in nd_rows:
    stem_a = r.get('img_a_stem') or r.get('stem_a')
    stem_b = r.get('img_b_stem') or r.get('stem_b')
    prefix_a = r.get('img_a_prefix') or (inv.get(stem_a, {}).get('prefix', ''))
    prefix_b = r.get('img_b_prefix') or (inv.get(stem_b, {}).get('prefix', ''))
    try:
        d = int(float(r.get('phash_dist', r.get('min_phash_dist', '999'))))
    except:
        d = 999
    if d <= 4:
        key = f"{min(prefix_a, prefix_b)}|{max(prefix_a, prefix_b)}"
        strong_pairs_by_prefix[key] += 1
        if prefix_a != prefix_b:
            cross_prefix_strong += 1

print(f"\nStrong pairs (phash<=4): {sum(strong_pairs_by_prefix.values())}")
print(f"Cross-prefix strong pairs: {cross_prefix_strong}")
print("Top 20 prefix pair counts:")
for key, cnt in sorted(strong_pairs_by_prefix.items(), key=lambda x: -x[1])[:20]:
    print(f"  {key}: {cnt}")

# Check if SANAS prefix links to other prefixes
print("\nSANAS-to-other prefix strong pairs:")
for r in nd_rows:
    stem_a = r.get('img_a_stem') or r.get('stem_a')
    stem_b = r.get('img_b_stem') or r.get('stem_b')
    prefix_a = r.get('img_a_prefix') or (inv.get(stem_a, {}).get('prefix', ''))
    prefix_b = r.get('img_b_prefix') or (inv.get(stem_b, {}).get('prefix', ''))
    try:
        d = int(float(r.get('phash_dist', r.get('min_phash_dist', '999'))))
    except:
        d = 999
    if d <= 4 and prefix_a != prefix_b:
        pa = inv.get(stem_a, {}).get('prefix', prefix_a)
        pb = inv.get(stem_b, {}).get('prefix', prefix_b)
        if 'SANAS' in pa or 'SANAS' in pb:
            print(f"  {pa} <-> {pb}")
        break  # Just show first

# Check near-dup pairs that cross blocks (B=40) - what prefixes?
print("\n\n=== Near-dup cross-block pairs by prefix (B=40) ===")
cross_block_by_prefix = defaultdict(int)
cross_block_pairs = []
B = 40
for r in nd_rows:
    stem_a = r.get('img_a_stem') or r.get('stem_a')
    stem_b = r.get('img_b_stem') or r.get('stem_b')
    if stem_a not in inv or stem_b not in inv:
        continue
    try:
        d = int(float(r.get('phash_dist', r.get('min_phash_dist', '999'))))
    except:
        d = 999
    if d > 4:
        continue
    pa = inv[stem_a]['prefix']
    pb = inv[stem_b]['prefix']
    tna = int(inv[stem_a]['trailing_number'])
    tnb = int(inv[stem_b]['trailing_number'])
    ba = tna // B
    bb = tnb // B
    if (pa, ba) != (pb, bb):
        cross_block_by_prefix[f"{pa}|{pb}"] += 1
        cross_block_pairs.append((stem_a, stem_b, pa, pb, d))

print(f"Cross-block pairs (B=40): {len(cross_block_pairs)}")
print("By prefix:")
for key, cnt in sorted(cross_block_by_prefix.items(), key=lambda x: -x[1])[:20]:
    print(f"  {key}: {cnt}")

# Check: how many unique stems in the near-dup graph?
all_stems_in_nd = set()
for r in nd_rows:
    stem_a = r.get('img_a_stem') or r.get('stem_a')
    stem_b = r.get('img_b_stem') or r.get('stem_b')
    try:
        d = int(float(r.get('phash_dist', r.get('min_phash_dist', '999'))))
    except:
        d = 999
    if d <= 4:
        all_stems_in_nd.add(stem_a)
        all_stems_in_nd.add(stem_b)
print(f"\nUnique stems in near-dup graph (phash<=4): {len(all_stems_in_nd)}")

# Count by prefix
stems_by_prefix = Counter(inv.get(s, {}).get('prefix', 'unknown') for s in all_stems_in_nd)
print("By prefix:")
for p, cnt in sorted(stems_by_prefix.items(), key=lambda x: -x[1])[:20]:
    print(f"  {p}: {cnt}")

# SIFT cross-block analysis
print("\n\n=== SIFT cross-block pairs (B=40) ===")
sift_cross = []
for r in sift_rows:
    stem_a = r.get('stem_a')
    stem_b = r.get('stem_b')
    if stem_a not in inv or stem_b not in inv:
        continue
    try:
        inliers = int(float(r.get('ransac_inliers', 0)))
        ca = float(r.get('containment_a_in_b', 0))
        cb = float(r.get('containment_b_in_a', 0))
    except:
        continue
    if inliers >= 60 and (ca >= 0.5 or cb >= 0.5):
        pa = inv[stem_a]['prefix']
        pb = inv[stem_b]['prefix']
        tna = int(inv[stem_a]['trailing_number'])
        tnb = int(inv[stem_b]['trailing_number'])
        ba = tna // B
        bb = tnb // B
        if (pa, ba) != (pb, bb):
            sift_cross.append((stem_a, stem_b, pa, pb, inliers))
print(f"SIFT cross-block pairs (B=40): {len(sift_cross)}")
for t in sift_cross[:10]:
    print(f"  {t}")
