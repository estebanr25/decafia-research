"""Check what happens if we only apply phash pairs in union-find (no SIFT, no crop-parent)."""
import csv
from collections import defaultdict
import numpy as np

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
with open(AUDIT_DIR + "/inventory.csv", newline='', encoding='utf-8') as f:
    inv_list = list(csv.DictReader(f))
with open(AUDIT_DIR + "/near_duplicate_pairs.csv", newline='', encoding='utf-8') as f:
    nd_rows = list(csv.DictReader(f))

stems = [r['stem'] for r in inv_list]
stem_to_idx = {s: i for i, s in enumerate(stems)}
inv_map = {r['stem']: r for r in inv_list}
n = len(stems)
B = 20

class UF:
    def __init__(self, n): self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x: self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py: self.p[py] = px

# Block-only with phash pairs (but ONLY phash, no SIFT, no crop-parent)
uf = UF(n)

# Block unions
blocks = defaultdict(list)
for r in inv_list:
    tn = int(r['trailing_number'])
    blocks[(r['prefix'], tn // B)].append(r['stem'])

for key, block_stems in blocks.items():
    for i in range(1, len(block_stems)):
        uf.union(stem_to_idx[block_stems[0]], stem_to_idx[block_stems[i]])

# Now add phash pairs (all of them, including cross-block)
phash_added = 0
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
        ia, ib = stem_to_idx[stem_a], stem_to_idx[stem_b]
        if uf.find(ia) != uf.find(ib):
            uf.union(ia, ib)
            phash_added += 1

print(f"Phash unions added: {phash_added}")

# Extract components
comp = defaultdict(list)
for i, s in enumerate(stems):
    comp[uf.find(i)].append(s)

sizes = sorted([len(v) for v in comp.values()], reverse=True)
print(f"Groups: {len(sizes)}")
print(f"Top 10 sizes: {sizes[:10]}")
print(f"Largest: {sizes[0]} ({sizes[0]/n*100:.2f}%)")

from collections import Counter
for i, (root, members) in enumerate(sorted(comp.items(), key=lambda x: -len(x[1]))[:5]):
    prefixes = Counter(inv_map[s]['prefix'] for s in members)
    print(f"Group {i+1}: size={len(members)}, prefixes={dict(prefixes.most_common(5))}")
