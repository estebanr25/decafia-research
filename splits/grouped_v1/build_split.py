#!/usr/bin/env python3
"""build_split.py - grouped YOLO train/val/test split from existing CSVs only."""

import re, csv, random, pathlib, collections, yaml

DATASET      = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
PROV_CSV     = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/provenance_manifest.csv")
OUT_DIR      = DATASET / "split_grouped_v1"
CROP_MAP_CSV = OUT_DIR / "crop_parent_map_full.csv"
ORPHAN_TXT   = OUT_DIR / "orphan_crops.txt"
HASH_CSV     = pathlib.Path("C:/Users/luise/temp/decafia-research/audits/near_duplicates/near_dup_candidates_hashes.csv")
ARGS_YAML    = pathlib.Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_clean_v1-2/args.yaml")
DATA_YAML    = DATASET / "data.yaml"

_NUM_RE = re.compile(r'^(.+?)_(\d+)$')

def split_stem(stem):
    m = _NUM_RE.match(stem)
    if not m:
        raise ValueError("Cannot parse stem: " + repr(stem))
    return m.group(1), int(m.group(2))

def chk(label, got, expected):
    if got != expected:
        raise AssertionError("FAILED -- " + label + ": expected " + str(expected) + ", got " + str(got))

SEP = "=" * 65

# ---- STEP 1: Inventory ------------------------------------------------------
print(SEP)
print("STEP 1 -- Inventory")
print(SEP)

prov = {}
with open(PROV_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        prov[pathlib.Path(row['filename']).stem] = row['inferred_source']

images    = {}
total_ann = 0
empty_lbl = 0

for split in ('train', 'val', 'test'):
    img_dir = DATASET / 'images' / split
    lbl_dir = DATASET / 'labels' / split
    for img_path in sorted(img_dir.iterdir()):
        if img_path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
            continue
        stem = img_path.stem
        prefix, number = split_stem(stem)
        lbl_path = lbl_dir / (stem + '.txt')
        if not lbl_path.exists():
            raise FileNotFoundError("Label missing: " + str(lbl_path))
        counts = {0: 0, 1: 0, 2: 0}
        lines = [l for l in lbl_path.read_text().splitlines() if l.strip()]
        if not lines:
            empty_lbl += 1
        for line in lines:
            cls = int(line.split()[0])
            counts[cls] += 1
            total_ann += 1
        if stem not in prov:
            raise KeyError("Stem missing from provenance: " + repr(stem))
        images[stem] = dict(split=split, prefix=prefix, number=number,
                            source=prov[stem], path=img_path, counts=counts)

n_train = sum(1 for v in images.values() if v['split'] == 'train')
n_val   = sum(1 for v in images.values() if v['split'] == 'val')
n_test  = sum(1 for v in images.values() if v['split'] == 'test')
print("  Total images:      " + str(len(images)) + "  (train=" + str(n_train) + " val=" + str(n_val) + " test=" + str(n_test) + ")")
print("  Total annotations: " + str(total_ann))
print("  Empty label files: " + str(empty_lbl))
chk("total images", len(images), 2315)
chk("train",        n_train,     1618)
chk("val",          n_val,       348)
chk("test",         n_test,      349)
chk("annotations",  total_ann,   12794)
chk("empty labels", empty_lbl,   1113)
print("  [OK] All inventory assertions passed")

# ---- STEP 2: Validate crop map ----------------------------------------------
print("\n" + SEP)
print("STEP 2 -- Validate crop map")
print(SEP)

orphan_stems = set()
with open(ORPHAN_TXT, encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if s:
            orphan_stems.add(s)

crop_stems = {s for s, v in images.items() if 'RECORTE' in v['prefix']}
print("  Crops (RECORTE in prefix): " + str(len(crop_stems)))

all_rows = []
with open(CROP_MAP_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        row['inliers'] = int(row['inliers'])
        row['crop_containment_in_parent'] = float(row['crop_containment_in_parent'])
        all_rows.append(row)

found_rows = [r for r in all_rows if r['evidence_type'] != 'no_parent_found']
dropped    = [r for r in found_rows
              if r['inliers'] < 30 or r['crop_containment_in_parent'] < 0.8]
valid_rows = [r for r in found_rows
              if r['inliers'] >= 30 and r['crop_containment_in_parent'] >= 0.8]

same_sp = sum(1 for r in valid_rows if r['crop_split'] == r['parent_split'])
diff_sp = sum(1 for r in valid_rows if r['crop_split'] != r['parent_split'])
print("  Rows with parent found (before filter): " + str(len(found_rows)))
print("  Dropped (threshold fail):               " + str(len(dropped)))
print("  Valid crop-parent pairs:                " + str(len(valid_rows)) +
      "  (same=" + str(same_sp) + ", diff=" + str(diff_sp) + ")")
print("  Orphans in orphan_crops.txt:            " + str(len(orphan_stems)))
chk("total crops", len(crop_stems),   398)
chk("valid pairs", len(valid_rows),   176)
chk("same-split",  same_sp,           92)
chk("diff-split",  diff_sp,           84)
chk("orphans",     len(orphan_stems), 222)
print("  [OK] Crop map assertions passed")

# ---- STEP 3: Orphan analysis ------------------------------------------------
print("\n" + SEP)
print("STEP 3 -- Orphan analysis")
print(SEP)

orphan_by_prefix = collections.Counter()
orphan_by_source = collections.Counter()
for stem in orphan_stems:
    if stem not in images:
        raise KeyError("Orphan stem not in images: " + repr(stem))
    v = images[stem]
    orphan_by_prefix[v['prefix']] += 1
    orphan_by_source[v['source']] += 1

print("  Orphans by prefix:")
for prefix, cnt in sorted(orphan_by_prefix.items(), key=lambda x: -x[1]):
    total = sum(1 for v in images.values() if v['prefix'] == prefix)
    print("    {:<35}  {:3d}/{} ({:.0f}%)".format(prefix, cnt, total, 100*cnt/total))

print("  Orphans by source:")
for src, cnt in sorted(orphan_by_source.items(), key=lambda x: -x[1]):
    total = sum(1 for v in images.values() if v['source'] == src)
    print("    {:<35}  {:3d}/{} ({:.0f}%)".format(src, cnt, total, 100*cnt/total))

forced_to_train = {s for s in orphan_stems if images[s]['source'] == 'own_field'}
print("\n  Forced to train (own_field orphan crops):  " + str(len(forced_to_train)))
print("  Grouped normally (other orphan crops):     " + str(len(orphan_stems) - len(forced_to_train)))

# ---- STEP 4: Load pHash pairs -----------------------------------------------
print("\n" + SEP)
print("STEP 4 -- Build groups (union-find)")
print(SEP)

phash_pairs = []
with open(HASH_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if int(row['min_phash_dist']) <= 4:
            sa, sb = row['stem_a'], row['stem_b']
            if sa in images and sb in images:
                phash_pairs.append((sa, sb))
print("  pHash pairs with dist <= 4 (both in dataset): " + str(len(phash_pairs)))

# Pre-compute sets for grouping rules
crops_with_valid_parent = {r['crop_stem'] for r in valid_rows if r['crop_stem'] in images}
# parent lookup: crop_stem -> parent_stem
crop_to_parent = {r['crop_stem']: r['parent_stem'] for r in valid_rows
                  if r['crop_stem'] in images and r['parent_stem'] in images}
# Orphan crops: crop_stems minus those with valid parent
orphan_crop_set = crop_stems - crops_with_valid_parent   # 222 items (since dropped=0)
# rust_and_leaf_miner orphan crops (grouped by block among themselves)
rl_orphan_crops = {s for s in orphan_crop_set
                   if images[s]['source'] == 'rust_and_leaf_miner'}
# own_field orphan crops (forced to train, no grouping)
of_orphan_crops = {s for s in orphan_crop_set
                   if images[s]['source'] == 'own_field'}
# Non-crop images
non_crop_stems = set(images.keys()) - crop_stems

print("  Non-crop images:            " + str(len(non_crop_stems)))
print("  Crops with valid parent:    " + str(len(crops_with_valid_parent)))
print("  Orphan crops (own_field):   " + str(len(of_orphan_crops)) + "  [forced to train]")
print("  Orphan crops (rust&miner):  " + str(len(rl_orphan_crops)) + "  [block-grouped among themselves]")

class UF:
    def __init__(self, keys):
        self.p = {k: k for k in keys}
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[b] = a

def build_groups(B, include_crop_parent=True, include_phash=True):
    uf = UF(images.keys())

    # Rule 1: non-crop images -- block grouping within prefix
    by_prefix_nc = collections.defaultdict(list)
    for stem in non_crop_stems:
        v = images[stem]
        by_prefix_nc[v['prefix']].append((v['number'], stem))
    for items in by_prefix_nc.values():
        bmap = collections.defaultdict(list)
        for num, stem in items:
            bmap[num // B].append(stem)
        for bstems in bmap.values():
            for i in range(1, len(bstems)):
                uf.union(bstems[0], bstems[i])

    # Rule 2: crops with valid parent -- union with parent only (no block)
    if include_crop_parent:
        for cs, ps in crop_to_parent.items():
            uf.union(cs, ps)

    # Rule 3: rust_and_leaf_miner orphan crops -- block among orphan crops of same prefix
    by_prefix_rl = collections.defaultdict(list)
    for stem in rl_orphan_crops:
        v = images[stem]
        by_prefix_rl[v['prefix']].append((v['number'], stem))
    for items in by_prefix_rl.values():
        bmap = collections.defaultdict(list)
        for num, stem in items:
            bmap[num // B].append(stem)
        for bstems in bmap.values():
            for i in range(1, len(bstems)):
                uf.union(bstems[0], bstems[i])
    # own_field orphan crops: no grouping edges (forced to train at assignment time)

    # Rule 4: pHash <= 4 edges
    if include_phash:
        for sa, sb in phash_pairs:
            uf.union(sa, sb)

    comps = collections.defaultdict(set)
    for stem in images:
        comps[uf.find(stem)].add(stem)
    return uf, dict(comps)

# ---- STEP 4b: Diagnostics (per B) ------------------------------------------
def print_group_diagnostics(B, uf, comps):
    groups_list = sorted(comps.values(), key=len, reverse=True)
    G           = len(groups_list)
    largest_n   = len(groups_list[0])
    N_TOTAL_    = len(images)
    print("  B={} | {} groups | largest={} ({:.1f}%)".format(
        B, G, largest_n, 100*largest_n/N_TOTAL_))

    print("  Top-5 groups:")
    for i, g in enumerate(groups_list[:5]):
        prefix_cnt = collections.Counter(images[s]['prefix'] for s in g)
        top_pfx = sorted(prefix_cnt.items(), key=lambda x: -x[1])[:4]
        pfx_str = ", ".join("{}:{}".format(p, c) for p, c in top_pfx)
        if len(prefix_cnt) > 4:
            pfx_str += " (+{} more)".format(len(prefix_cnt)-4)
        print("    #{}: size={} ({:.1f}%)  prefixes=[{}]".format(
            i+1, len(g), 100*len(g)/N_TOTAL_, pfx_str))

    # Edge ablation
    _, ca  = build_groups(B, include_crop_parent=False, include_phash=False)
    _, cb  = build_groups(B, include_crop_parent=True,  include_phash=False)
    _, cc  = comps, None   # already built
    la = max(len(g) for g in ca.values())
    lb = max(len(g) for g in cb.values())
    lc = largest_n
    print("  Edge ablation: (a) blocks-only largest={} ({:.1f}%)"
          " | (b) +crop-parent={} ({:.1f}%)"
          " | (c) +pHash={} ({:.1f}%)".format(
        la, 100*la/N_TOTAL_, lb, 100*lb/N_TOTAL_, lc, 100*lc/N_TOTAL_))

    # Per-group class totals (flag >15% of any class)
    TR = sum(v['counts'][0] for v in images.values())
    TC = sum(v['counts'][1] for v in images.values())
    TM = sum(v['counts'][2] for v in images.values())
    warnings = []
    for g in groups_list:
        gr  = sum(images[s]['counts'][0] for s in g)
        gc  = sum(images[s]['counts'][1] for s in g)
        gm  = sum(images[s]['counts'][2] for s in g)
        gn  = len(g)
        root_stem = uf.find(next(iter(g)))
        if (TR and gr/TR > 0.15) or (TC and gc/TC > 0.15) or (TM and gm/TM > 0.15):
            warnings.append("    [!] group size={} ({:.1f}%): roya={:.1f}% coco={:.1f}% mina={:.1f}%".format(
                gn, 100*gn/N_TOTAL_,
                100*gr/TR if TR else 0, 100*gc/TC if TC else 0,
                100*gm/TM if TM else 0))
    if warnings:
        print("  Groups holding >15% of a class's annotations:")
        for w in warnings:
            print(w)
    else:
        print("  No group holds >15% of any class's annotations.")

# ---- STEP 5: Randomized search ----------------------------------------------
print("\n" + SEP)
print("STEP 5 -- Randomized search")
print(SEP)

N_TOTAL       = len(images)
TOTAL_ROYA    = sum(v['counts'][0] for v in images.values())
TOTAL_COCO    = sum(v['counts'][1] for v in images.values())
TOTAL_MINADOR = sum(v['counts'][2] for v in images.values())
TOTAL_BG      = sum(1 for v in images.values() if not any(v['counts'].values()))
TARGETS       = [0.70, 0.15, 0.15]
N_ITER        = 20_000
RNG           = random.Random(42)

def compute_dev_table(cnt, ry, co, mi, bg):
    """Return per-split fraction dict and the (max_dev, worst_label) tuple."""
    frac = {}
    max_dev = 0.0
    worst   = ('?', '?')
    for si, sp in enumerate(('train', 'val', 'test')):
        frac[sp] = {
            'img':  cnt[si] / N_TOTAL,
            'roya': ry[si]  / TOTAL_ROYA    if TOTAL_ROYA    else 0,
            'coco': co[si]  / TOTAL_COCO    if TOTAL_COCO    else 0,
            'mina': mi[si]  / TOTAL_MINADOR if TOTAL_MINADOR else 0,
            'bg':   bg[si]  / TOTAL_BG      if TOTAL_BG      else 0,
        }
        if sp in ('val', 'test'):
            for metric, val in frac[sp].items():
                dev = abs(val - 0.15) * 100
                if dev > max_dev:
                    max_dev = dev
                    worst   = (sp, metric)
    return frac, max_dev, worst

def print_dev_table(frac, max_dev, worst):
    print("    {:<8} {:>6} {:>7} {:>7} {:>7} {:>7}".format(
        'split', 'img%', 'roya%', 'coco%', 'mina%', 'bg%'))
    for sp in ('train', 'val', 'test'):
        f = frac[sp]
        print("    {:<8} {:>5.1f}% {:>6.1f}% {:>6.1f}% {:>6.1f}% {:>6.1f}%".format(
            sp, f['img']*100, f['roya']*100, f['coco']*100, f['mina']*100, f['bg']*100))
    print("    max_dev={:.2f} pp  (worst: {}/{})".format(max_dev, worst[0], worst[1]))

best_result  = None
per_B_report = {}

for B in [40, 20, 10]:
    print("\n" + "-" * 55)
    print("  B = " + str(B))
    uf, comps = build_groups(B)
    groups    = list(comps.values())
    G         = len(groups)
    largest_n = max(len(g) for g in groups)
    largest_f = largest_n / N_TOTAL

    # Step 4b diagnostics
    print_group_diagnostics(B, uf, comps)

    # Precompute group stats
    gstat = []
    for g in groups:
        force = any(s in forced_to_train for s in g)
        gstat.append((len(g),
                      sum(images[s]['counts'][0] for s in g),
                      sum(images[s]['counts'][1] for s in g),
                      sum(images[s]['counts'][2] for s in g),
                      sum(1 for s in g if not any(images[s]['counts'].values())),
                      force))

    best_dev  = float('inf')
    best_asgn = None
    best_cnt = best_ry = best_co = best_mi = best_bg = None

    for _ in range(N_ITER):
        order = list(range(G))
        RNG.shuffle(order)
        cnt = [0, 0, 0]; ry = [0, 0, 0]; co = [0, 0, 0]
        mi  = [0, 0, 0]; bg = [0, 0, 0]
        asgn = [0] * G

        for gi in order:
            n, roya, coco, mina, bgv, force = gstat[gi]
            if force:
                sp = 0
            else:
                deficits = [TARGETS[i] * N_TOTAL - cnt[i] for i in range(3)]
                sp = deficits.index(max(deficits))
            asgn[gi] = sp
            cnt[sp] += n;    ry[sp] += roya
            co[sp]  += coco; mi[sp] += mina; bg[sp] += bgv

        _, dev, _ = compute_dev_table(cnt, ry, co, mi, bg)
        if dev < best_dev:
            best_dev  = dev
            best_asgn = asgn[:]
            best_cnt  = cnt[:]; best_ry = ry[:]; best_co = co[:]
            best_mi   = mi[:];  best_bg = bg[:]

    frac, max_dev, worst = compute_dev_table(best_cnt, best_ry, best_co, best_mi, best_bg)
    qualifies = (max_dev <= 3.0) and (largest_f <= 0.10)
    print("  Randomized search result (best of {:,} iterations):".format(N_ITER))
    print_dev_table(frac, max_dev, worst)
    print("  largest_group={:.1f}%  qualifies={}".format(100*largest_f, qualifies))
    per_B_report[B] = dict(dev=max_dev, largest_pct=100*largest_f, qualifies=qualifies)

    if qualifies:
        sp_names   = ['train', 'val', 'test']
        final_asgn = {}
        for gi, g in enumerate(groups):
            for stem in g:
                final_asgn[stem] = sp_names[best_asgn[gi]]
        best_result = dict(
            B=B, uf=uf, comps=comps, groups=groups, asgn=final_asgn,
            dev=max_dev,
            counts={'train': best_cnt[0], 'val': best_cnt[1], 'test': best_cnt[2]},
            roya  ={'train': best_ry[0],  'val': best_ry[1],  'test': best_ry[2]},
            coco  ={'train': best_co[0],  'val': best_co[1],  'test': best_co[2]},
            mina  ={'train': best_mi[0],  'val': best_mi[1],  'test': best_mi[2]},
            bg    ={'train': best_bg[0],  'val': best_bg[1],  'test': best_bg[2]},
        )
        break

if best_result is None:
    print("\n  Summary: no B qualifies.")
    print("  {:<6} {:>10} {:>14}".format('B', 'max_dev(pp)', 'largest(%)'))
    for Bv, rep in per_B_report.items():
        print("  {:<6} {:>10.2f} {:>14.1f}".format(Bv, rep['dev'], rep['largest_pct']))
    raise RuntimeError("No B in [40,20,10] qualifies (dev<=3pp AND largest<=10%). See diagnostics above.")

br     = best_result
B      = br['B']
asgn   = br['asgn']
uf     = br['uf']
comps  = br['comps']
groups = br['groups']
print("\n  CHOSEN B = " + str(B) + "  (max_dev={:.2f} pp)".format(br['dev']))

# ---- STEP 6: Write outputs --------------------------------------------------
print("\n" + SEP)
print("STEP 6 -- Write outputs")
print(SEP)

def pct(key, sp):
    denom = {'counts': N_TOTAL, 'roya': TOTAL_ROYA, 'coco': TOTAL_COCO,
             'mina': TOTAL_MINADOR, 'bg': TOTAL_BG}[key]
    return br[key][sp] / denom * 100

for sp in ('train', 'val', 'test'):
    paths = sorted(v['path'].as_posix() for stem, v in images.items() if asgn[stem] == sp)
    (OUT_DIR / (sp + '.txt')).write_text('\n'.join(paths) + '\n', encoding='utf-8')
    print("  {}.txt: {} images".format(sp, len(paths)))

with open(DATA_YAML, encoding='utf-8') as f:
    orig = yaml.safe_load(f)
grouped_yaml = {
    'train': (OUT_DIR / 'train.txt').as_posix(),
    'val':   (OUT_DIR / 'val.txt').as_posix(),
    'test':  (OUT_DIR / 'test.txt').as_posix(),
    'nc':    orig['nc'],
    'names': orig['names'],
}
with open(OUT_DIR / 'data_grouped_v1.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(grouped_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print("  data_grouped_v1.yaml written")

with open(OUT_DIR / 'assignments.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['stem', 'split_old', 'split_new', 'prefix', 'number', 'source',
                'roya', 'coco', 'minador', 'group_root'])
    for stem in sorted(images):
        v = images[stem]
        w.writerow([stem, v['split'], asgn[stem], v['prefix'], v['number'],
                    v['source'], v['counts'][0], v['counts'][1], v['counts'][2],
                    uf.find(stem)])
print("  assignments.csv written")

orphan_prefix_lines = '\n'.join(
    "  - {}: {}".format(p, c) for p, c in sorted(orphan_by_prefix.items(), key=lambda x: -x[1])
)
readme = (
    "# DECAFIA Grouped Split v1\n\n"
    "## Method\n"
    "Images grouped with union-find under the following rules:\n\n"
    "1. **Non-crop images**: within each prefix, stems sharing floor(number / B) are merged.\n"
    "2. **Crops with a valid parent** (inliers >= 30, containment >= 0.80): merged with their\n"
    "   parent only. No block grouping (a crop's number carries no session information).\n"
    "3. **Orphan crops without a valid parent**:\n"
    "   - own_field (e.g. COCO_RECORTE): forced to the training split.\n"
    "   - rust_and_leaf_miner: block-grouped floor(number/B) ONLY among orphan crops of the\n"
    "     same prefix (not mixed with non-orphan images).\n"
    "4. **pHash <= 4 edges**: any cross-image pair with pHash distance <= 4 is merged.\n\n"
    "Split assigned by randomized greedy search (seed=42, 20 000 iterations), minimising\n"
    "max deviation from 70/15/15 across image share, per-class annotation share, and\n"
    "background-image share in val and test.\n\n"
    "## Chosen B = {}  (max deviation = {:.2f} pp)\n\n".format(B, br['dev']) +
    "## Deviations table\n"
    "| split | images | roya  | coco  | minador | background |\n"
    "|-------|--------|-------|-------|---------|------------|\n" +
    "| train | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% |\n".format(
        pct('counts','train'), pct('roya','train'), pct('coco','train'),
        pct('mina','train'), pct('bg','train')) +
    "| val   | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% |\n".format(
        pct('counts','val'), pct('roya','val'), pct('coco','val'),
        pct('mina','val'), pct('bg','val')) +
    "| test  | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% |\n\n".format(
        pct('counts','test'), pct('roya','test'), pct('coco','test'),
        pct('mina','test'), pct('bg','test')) +
    "## Crop results\n"
    "- Total crops: {}, valid parent pairs (post-filter): {}\n".format(
        len(crop_stems), len(valid_rows)) +
    "  (92 same split, 84 different split), orphans: {}\n".format(len(orphan_stems)) +
    "- Rows dropped for threshold (inliers < 30 or containment < 0.80): {}\n\n".format(
        len(dropped)) +
    "## Orphan handling assumption\n"
    "**Orphan crops from `own_field` (e.g. COCO_RECORTE) are forced to the training split**,\n"
    "because their parents likely exist in the dataset but were not detected by the SIFT pipeline.\n\n"
    "Orphan crops from `rust_and_leaf_miner` (Silva et al.) are NOT forced; they are block-grouped\n"
    "only among other orphan crops of the same prefix, because their parents are likely not in this\n"
    "dataset.\n\n"
    "Per-prefix orphan counts:\n" + orphan_prefix_lines + "\n\n"
    "## Limitation\n"
    "The same physical leaf photographed at non-consecutive number intervals is not detectable\n"
    "by the block-based grouping strategy. Such pairs can only be caught by pHash near-duplicate\n"
    "edges (distance <= 4). Pairs with 5 <= pHash <= 12 may still represent the same leaf and\n"
    "remain undetected.\n"
)
(OUT_DIR / 'SPLIT_README.md').write_text(readme, encoding='utf-8')
print("  SPLIT_README.md written")

# ---- STEP 7: Verify ---------------------------------------------------------
print("\n" + SEP)
print("STEP 7 -- Verify")
print(SEP)

listed_all = set()
for sp in ('train', 'val', 'test'):
    for line in (OUT_DIR / (sp + '.txt')).read_text(encoding='utf-8').splitlines():
        p = line.strip()
        if not p:
            continue
        stem = pathlib.Path(p).stem
        if stem in listed_all:
            raise AssertionError("Duplicate in lists: " + stem)
        listed_all.add(stem)
        if not pathlib.Path(p).exists():
            raise AssertionError("Image missing on disk: " + p)

missing = set(images) - listed_all
extra   = listed_all - set(images)
if missing or extra:
    raise AssertionError("List mismatch: missing=" + str(len(missing)) + ", extra=" + str(len(extra)))
print("  [OK] All " + str(len(listed_all)) + " images in exactly one list and exist on disk")

for stem, v in images.items():
    lbl = DATASET / 'labels' / v['split'] / (stem + '.txt')
    if not lbl.exists():
        raise AssertionError("Label missing: " + str(lbl))
print("  [OK] All images have label files")

group_span = [(root, {asgn[s] for s in comp}, len(comp))
              for root, comp in comps.items()
              if len({asgn[s] for s in comp}) > 1]
if group_span:
    print("  [WARN] " + str(len(group_span)) + " groups span splits:")
    for root, splits, n in group_span[:5]:
        print("    root={}  splits={}  size={}".format(root, splits, n))
else:
    print("  [OK] No groups span splits")

cp_span = [(r['crop_stem'], r['parent_stem'], asgn[r['crop_stem']], asgn[r['parent_stem']])
           for r in valid_rows if asgn[r['crop_stem']] != asgn[r['parent_stem']]]
if cp_span:
    print("  [WARN] " + str(len(cp_span)) + " crop-parent pairs span splits:")
    for cs, ps, sa, sb in cp_span[:5]:
        print("    {}({}) <-> {}({})".format(cs, sa, ps, sb))
else:
    print("  [OK] No crop-parent pairs span splits")

cross_split = [(a, asgn[a], b, asgn[b]) for a, b in phash_pairs if asgn[a] != asgn[b]]
print("  Cross-split pHash <= 4 pairs remaining: " + str(len(cross_split)))
for a, sa, b, sb in cross_split[:10]:
    print("    {}({}) <-> {}({})".format(a, sa, b, sb))

changed = sum(1 for stem, v in images.items() if asgn[stem] != v['split'])
print("  Images that changed split: " + str(changed))

print("\n  Old vs new balance:")
print("  {:<8} {:>6} {:>6}  {:>6} {:>6}".format('split', 'old_n', 'new_n', 'old_%', 'new_%'))
for sp in ('train', 'val', 'test'):
    old_n = sum(1 for v in images.values() if v['split'] == sp)
    new_n = br['counts'][sp]
    print("  {:<8} {:>6} {:>6}  {:>5.1f}% {:>5.1f}%".format(
        sp, old_n, new_n, 100*old_n/N_TOTAL, 100*new_n/N_TOTAL))

# ---- STEP 8: Write train_grouped_v1.py --------------------------------------
print("\n" + SEP)
print("STEP 8 -- Write train_grouped_v1.py")
print(SEP)

with open(ARGS_YAML, encoding='utf-8') as f:
    args_check = yaml.safe_load(f)

args_yaml_posix = str(ARGS_YAML).replace('\\', '/')
data_yaml_posix = (OUT_DIR / 'data_grouped_v1.yaml').as_posix()

train_script = (
    '#!/usr/bin/env python3\n'
    '"""train_grouped_v1.py - Training with grouped split.\n'
    'Use the PowerShell command at the bottom of build_split.py output.\n'
    '"""\n\n'
    'import json, pathlib, yaml\n'
    'import torch\n'
    'from ultralytics import YOLO\n\n'
    'assert "cu" in torch.__version__, "CUDA not in torch build: " + torch.__version__\n'
    'assert torch.cuda.is_available(), "torch.cuda.is_available() is False"\n\n'
    'ARGS_YAML = pathlib.Path(' + repr(args_yaml_posix) + ')\n'
    'DATA_YAML = pathlib.Path(' + repr(data_yaml_posix) + ')\n\n'
    'with open(ARGS_YAML, encoding="utf-8") as f:\n'
    '    args = yaml.safe_load(f)\n\n'
    'args["data"]    = str(DATA_YAML)\n'
    'args["name"]    = "decafia_grouped_v1"\n'
    'args["workers"] = 0\n'
    'for k in ("task", "mode", "save_dir", "source", "split", "format"):\n'
    '    args.pop(k, None)\n\n'
    'model_path = args.pop("model")\n'
    'model = YOLO(model_path)\n\n'
    'results = model.train(**args)\n\n'
    '# Validate on test split\n'
    'val_results = model.val(split="test")\n'
    'out = pathlib.Path(results.save_dir) / "results_test.json"\n'
    'with open(out, "w") as fh:\n'
    '    json.dump(val_results.results_dict, fh, indent=2)\n'
    'print("Test results ->", out)\n'
)

train_py = OUT_DIR / 'train_grouped_v1.py'
train_py.write_text(train_script, encoding='utf-8')
print("  Wrote " + str(train_py))

# ---- FINAL SUMMARY ----------------------------------------------------------
print("\n" + SEP)
print("FINAL SUMMARY")
print(SEP)
print("  Chosen B      = " + str(B))
print("  Max deviation = {:.2f} pp".format(br['dev']))
print()
print("  {:<8} {:>6} {:>6} {:>7} {:>7} {:>7} {:>6}".format(
    'split', 'n', '%img', '%roya', '%coco', '%mina', '%bg'))
for sp in ('train', 'val', 'test'):
    print("  {:<8} {:>6} {:>5.1f}% {:>6.1f}% {:>6.1f}% {:>6.1f}% {:>5.1f}%".format(
        sp, br['counts'][sp],
        pct('counts', sp), pct('roya', sp), pct('coco', sp),
        pct('mina', sp), pct('bg', sp)))

print()
print("  PowerShell command to launch training:")
print('  powershell.exe -NoProfile -Command "python ' + train_py.as_posix() + '"')
