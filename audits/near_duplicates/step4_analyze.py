"""
Analyze the near-dup network to understand why giant components form.
"""
import csv
from collections import Counter, defaultdict

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
SIFT_CSV = AUDIT_DIR + "/sift_results.csv"
NEAR_DUP_CSV = AUDIT_DIR + "/near_duplicate_pairs.csv"
INVENTORY_CSV = AUDIT_DIR + "/inventory.csv"

with open(INVENTORY_CSV, newline='', encoding='utf-8') as f:
    inv = {r['stem']: r for r in csv.DictReader(f)}

# Are the near_dup pairs cross-split?
with open(NEAR_DUP_CSV, newline='', encoding='utf-8') as f:
    nd_rows = list(csv.DictReader(f))

cross_split = sum(1 for r in nd_rows if r.get('img_a_split') != r.get('img_b_split'))
same_split = sum(1 for r in nd_rows if r.get('img_a_split') == r.get('img_b_split'))
print(f"near_dup pairs: cross-split={cross_split}, same-split={same_split}")

# Splits breakdown
for r in nd_rows[:5]:
    print(f"  splits: {r.get('img_a_split')} <-> {r.get('img_b_split')}")

# SIFT results
with open(SIFT_CSV, newline='', encoding='utf-8') as f:
    sift_rows = list(csv.DictReader(f))

cross_split_sift = sum(1 for r in sift_rows if r.get('split_a') != r.get('split_b'))
same_split_sift = sum(1 for r in sift_rows if r.get('split_a') == r.get('split_b'))
print(f"\nsift_results pairs: cross-split={cross_split_sift}, same-split={same_split_sift}")

# SIFT strong (>=60 inliers, >=0.5 containment)
sift_strong = []
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
        sift_strong.append(r)

print(f"\nSIFT strong pairs (>=60 inliers, >=0.5 cont): {len(sift_strong)}")
cross_sift_strong = sum(1 for r in sift_strong if r.get('split_a') != r.get('split_b'))
same_sift_strong = sum(1 for r in sift_strong if r.get('split_a') == r.get('split_b'))
print(f"  cross-split: {cross_sift_strong}, same-split: {same_sift_strong}")

# What prefixes connect cross-split via SIFT?
from collections import Counter
cross_prefixes = Counter()
for r in sift_strong:
    if r.get('split_a') != r.get('split_b'):
        sa, sb = r.get('stem_a'), r.get('stem_b')
        pa = inv.get(sa, {}).get('prefix', '?')
        pb = inv.get(sb, {}).get('prefix', '?')
        cross_prefixes[(pa, pb)] += 1

print("\nCross-split SIFT strong pairs by prefix:")
for (pa, pb), cnt in sorted(cross_prefixes.items(), key=lambda x: -x[1])[:15]:
    print(f"  {pa} <-> {pb}: {cnt}")

# What prefixes connect cross-split via SIFT with cross-BLOCK B=40?
B = 40
print(f"\nCross-split AND cross-block (B={B}) SIFT strong pairs:")
cross_cross_prefixes = Counter()
cross_cross_pairs = []
for r in sift_strong:
    if r.get('split_a') != r.get('split_b'):
        sa, sb = r.get('stem_a'), r.get('stem_b')
        if sa not in inv or sb not in inv:
            continue
        pa = inv[sa]['prefix']
        pb = inv[sb]['prefix']
        tna = int(inv[sa]['trailing_number'])
        tnb = int(inv[sb]['trailing_number'])
        ba, bb = tna // B, tnb // B
        if (pa, ba) != (pb, bb):
            cross_cross_prefixes[(pa, pb)] += 1
            cross_cross_pairs.append((sa, sb, pa, pb, r.get('ransac_inliers'), r.get('split_a'), r.get('split_b')))

print(f"Total: {len(cross_cross_pairs)}")
for (pa, pb), cnt in sorted(cross_cross_prefixes.items(), key=lambda x: -x[1])[:15]:
    print(f"  {pa} <-> {pb}: {cnt}")

# Show a few cross-cross pairs
print("\nFirst 5 cross-split cross-block strong pairs:")
for t in cross_cross_pairs[:5]:
    print(f"  {t}")

# Check: is the giant component mainly from WITHIN-prefix block merges?
# i.e., even without cross-block merges, does block merging create giant component?
print("\n\n=== What happens with ONLY block merges (no cross-block) for B=40? ===")
class UF:
    def __init__(self, n): self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x: self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py: self.p[py] = px

stems = [r['stem'] for r in csv.DictReader(open(INVENTORY_CSV))]
stem_to_idx = {s: i for i, s in enumerate(stems)}
inv_list = list(csv.DictReader(open(INVENTORY_CSV)))
inv_map = {r['stem']: r for r in inv_list}

uf = UF(len(stems))
prefix_block_to_stems = defaultdict(list)
for r in inv_list:
    tn = int(r['trailing_number'])
    prefix_block_to_stems[(r['prefix'], tn // 40)].append(r['stem'])

for key, block_stems in prefix_block_to_stems.items():
    for i in range(1, len(block_stems)):
        uf.union(stem_to_idx[block_stems[0]], stem_to_idx[block_stems[i]])

from collections import defaultdict as dd
comp = dd(list)
for i, s in enumerate(stems):
    comp[uf.find(i)].append(s)
sizes = sorted([len(v) for v in comp.values()], reverse=True)
print(f"Groups: {len(sizes)}, largest: {sizes[0]} ({sizes[0]/len(stems)*100:.1f}%)")
print(f"Top 10 sizes: {sizes[:10]}")
largest_group = sorted(comp.values(), key=len, reverse=True)[0]
prefixes = Counter(inv_map[s]['prefix'] for s in largest_group)
print(f"Largest group prefixes: {dict(prefixes.most_common(10))}")

# Check: what is the largest group if SANAS is treated as separate sub-groups (SANAS_NUEVAS, SANAS_SOCORRO)?
# i.e., use finer prefix parsing (as inventory.csv has it)?
print("\n\nTop 5 block groups:")
top_blocks = sorted(comp.values(), key=len, reverse=True)[:5]
for i, g in enumerate(top_blocks):
    prefixes = Counter(inv_map[s]['prefix'] for s in g)
    print(f"  Group {i+1}: size={len(g)}, prefixes={dict(prefixes.most_common(5))}")
