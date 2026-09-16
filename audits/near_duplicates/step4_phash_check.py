"""Check the 57 phash strong pairs and the crop-parent chain."""
import csv
from collections import Counter, defaultdict

AUDIT_DIR = "C:/Users/luise/temp/decafia-research/audits/near_duplicates"
SPLIT_DIR = "C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1"

with open(AUDIT_DIR + "/inventory.csv", newline='', encoding='utf-8') as f:
    inv = {r['stem']: r for r in csv.DictReader(f)}

with open(AUDIT_DIR + "/near_duplicate_pairs.csv", newline='', encoding='utf-8') as f:
    nd_rows = list(csv.DictReader(f))

# Show the 57 valid phash pairs
print("=== Valid phash pairs (0 <= phash <= 4) ===")
valid_phash = []
for r in nd_rows:
    stem_a = r.get('img_a_stem') or r.get('stem_a')
    stem_b = r.get('img_b_stem') or r.get('stem_b')
    try:
        pd = int(float(r.get('phash_dist', '-999')))
    except:
        pd = -999
    if 0 <= pd <= 4:
        pa = inv.get(stem_a, {}).get('prefix', '?')
        pb = inv.get(stem_b, {}).get('prefix', '?')
        valid_phash.append((stem_a, stem_b, pa, pb, pd))
        print(f"  {stem_a}({pa}) <-> {stem_b}({pb}): phash={pd}")

print(f"\nTotal valid phash pairs: {len(valid_phash)}")
print(f"Prefix pairs:")
pp = Counter(f"{p[2]}|{p[3]}" for p in valid_phash)
for k, v in sorted(pp.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Now check what crop-parent edges do
print("\n=== Crop-parent edges ===")
with open(SPLIT_DIR + "/crop_parent_map_full.csv", newline='', encoding='utf-8') as f:
    cp_rows = list(csv.DictReader(f))

found = [(r['crop_stem'], r['parent_stem'], r['crop_prefix'], r['parent_prefix'])
         for r in cp_rows if r['parent_stem']]
print(f"Found: {len(found)}")
pp2 = Counter(f"{r[2]}|{r[3]}" for r in found)
print("Crop prefix -> parent prefix:")
for k, v in sorted(pp2.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Trace the giant component formation
# Use simple union-find to trace which prefix clusters connect
class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}
    def find(self, x):
        while self.p[x] != x: self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py: self.p[py] = px

# Work at prefix level to trace connectivity
all_prefixes = set(r['prefix'] for r in inv.values())
uf_prefix = UF(all_prefixes)

print("\n=== Prefix-level connectivity from crop-parent ===")
cp_prefix_edges = set()
for crop_stem, parent_stem, crop_prefix, parent_prefix in found:
    if crop_prefix != parent_prefix:
        cp_prefix_edges.add((crop_prefix, parent_prefix))

for pa, pb in cp_prefix_edges:
    uf_prefix.union(pa, pb)
    print(f"  MERGED: {pa} <-> {pb}")

# Show prefix components after crop-parent
comp_map = defaultdict(set)
for p in all_prefixes:
    comp_map[uf_prefix.find(p)].add(p)
print(f"\nPrefix components after crop-parent merges:")
for root, prefixes in sorted(comp_map.items(), key=lambda x: -len(x[1])):
    if len(prefixes) > 1:
        print(f"  {sorted(prefixes)}")

# Now add phash prefix edges
print("\n=== After adding phash cross-prefix edges ===")
for stem_a, stem_b, pa, pb, pd in valid_phash:
    if pa != pb:
        uf_prefix.union(pa, pb)
        print(f"  PHASH MERGE: {pa} <-> {pb} (phash={pd})")

comp_map2 = defaultdict(set)
for p in all_prefixes:
    comp_map2[uf_prefix.find(p)].add(p)
print(f"\nPrefix components after phash merges:")
for root, prefixes in sorted(comp_map2.items(), key=lambda x: -len(x[1])):
    if len(prefixes) >= 1:
        sizes = sum(sum(1 for r in inv.values() if r['prefix'] == p) for p in prefixes)
        if sizes > 50:
            print(f"  ({sizes} imgs) {sorted(prefixes)}")
