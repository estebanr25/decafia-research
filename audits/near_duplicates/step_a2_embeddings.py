import pathlib
import csv
import sys
import numpy as np
import torch
import torchvision
import torchvision.transforms as T
from torchvision.models import resnet50, ResNet50_Weights
from torch.utils.data import Dataset, DataLoader
from PIL import Image

print("=" * 60)
print("STEP A2 — ResNet-50 Embeddings")
print("=" * 60)

dataset_root = pathlib.Path(r"C:\Users\luise\OneDrive\Documentos\DECAFIA_v2\01_dataset\decafia_clean")
output_dir = pathlib.Path(r"C:\Users\luise\temp\decafia-research\audits\near_duplicates")
splits = ["train", "val", "test"]
image_exts = {".jpg", ".jpeg", ".png"}

# 1. Load ResNet-50 with ImageNet weights
print("\n[1] Loading ResNet-50 (IMAGENET1K_V1)...")
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)

# 2. Remove final FC layer — use as feature extractor (2048-dim)
model.fc = torch.nn.Identity()
model.eval()

# 3. GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"  Device: {device}")

# 4. DataLoader setup
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Collect all images in order
all_records = []
for split in splits:
    img_dir = dataset_root / "images" / split
    files = sorted([f for f in img_dir.iterdir() if f.suffix.lower() in image_exts])
    for f in files:
        all_records.append({"filepath": str(f), "split": split, "stem": f.stem})

print(f"  Total images: {len(all_records)}")

class ImageDataset(Dataset):
    def __init__(self, records, transform):
        self.records = records
        self.transform = transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        img = Image.open(rec["filepath"]).convert("RGB")
        return self.transform(img), idx

# num_workers=0 is MANDATORY per spec
loader = DataLoader(ImageDataset(all_records, transform), batch_size=32, num_workers=0, shuffle=False)

# 6. Extract embeddings
print("\n[6] Extracting embeddings...")
embeddings = np.zeros((len(all_records), 2048), dtype=np.float32)

with torch.no_grad():
    for batch_imgs, batch_idxs in loader:
        batch_imgs = batch_imgs.to(device)
        feats = model(batch_imgs)  # shape: (B, 2048)
        feats_np = feats.cpu().numpy()
        for local_i, global_idx in enumerate(batch_idxs.numpy()):
            embeddings[global_idx] = feats_np[local_i]
        processed = max(batch_idxs.numpy()) + 1
        if processed % 500 < 32:
            print(f"  Processed ~{processed}/{len(all_records)}...")

print(f"  Done. Embeddings shape: {embeddings.shape}")

# Normalize embeddings for cosine similarity
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
if np.any(norms == 0):
    raise RuntimeError("Zero-norm embedding found — cannot normalize.")
emb_norm = embeddings / norms

# 7. For each image, find top-5 most similar in OTHER splits
print("\n[7] Computing cross-split top-5 similarities...")

# Build split masks
split_indices = {s: [] for s in splits}
for i, rec in enumerate(all_records):
    split_indices[rec["split"]].append(i)

# Cosine similarity matrix (chunked to avoid OOM)
# For each query, compute similarity to all others in different splits
top5_rows = []
CHUNK = 200

total_processed = 0
for split in splits:
    q_indices = split_indices[split]
    other_splits = [s for s in splits if s != split]
    other_indices = []
    for s in other_splits:
        other_indices.extend(split_indices[s])
    other_indices = np.array(other_indices)
    other_emb = emb_norm[other_indices]  # shape: (N_other, 2048)

    for start in range(0, len(q_indices), CHUNK):
        chunk_idxs = q_indices[start:start + CHUNK]
        chunk_emb = emb_norm[chunk_idxs]  # (chunk, 2048)
        sims = chunk_emb @ other_emb.T  # (chunk, N_other)

        for local_i, global_q_idx in enumerate(chunk_idxs):
            row_sims = sims[local_i]
            # top-5 indices into other_indices
            top5_pos = np.argpartition(row_sims, -5)[-5:]
            top5_pos = top5_pos[np.argsort(row_sims[top5_pos])[::-1]]
            for rank, pos in enumerate(top5_pos):
                cand_global_idx = other_indices[pos]
                sim_val = float(row_sims[pos])
                top5_rows.append({
                    "query_path": all_records[global_q_idx]["filepath"],
                    "query_split": all_records[global_q_idx]["split"],
                    "query_stem": all_records[global_q_idx]["stem"],
                    "candidate_path": all_records[cand_global_idx]["filepath"],
                    "candidate_split": all_records[cand_global_idx]["split"],
                    "candidate_stem": all_records[cand_global_idx]["stem"],
                    "cosine_sim": sim_val,
                    "rank": rank + 1
                })

        total_processed += len(chunk_idxs)
        if total_processed % 500 < CHUNK:
            print(f"  Processed {total_processed}/{len(all_records)} queries...")

print(f"  Done. Total top-5 rows: {len(top5_rows)}")

# 8. Similarity score distribution
all_top5_sims = np.array([r["cosine_sim"] for r in top5_rows])
print("\n[8] Similarity score distribution (all top-5 cross-split sims):")
for p in [50, 75, 90, 95, 99, 100]:
    val = np.percentile(all_top5_sims, p)
    print(f"  p{p:3d}: {val:.6f}")

# 9. Save embeddings
emb_path = output_dir / "embeddings.npy"
np.save(str(emb_path), embeddings)
print(f"\n[9] Saved embeddings to {emb_path}")

# Save index file
idx_path = output_dir / "embeddings_index.csv"
with open(idx_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["index", "filepath", "split", "stem"])
    writer.writeheader()
    for i, rec in enumerate(all_records):
        writer.writerow({"index": i, "filepath": rec["filepath"], "split": rec["split"], "stem": rec["stem"]})
print(f"  Saved index to {idx_path}")

# 10. Save top5_cross_split.csv
top5_path = output_dir / "top5_cross_split.csv"
with open(top5_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["query_path", "query_split", "candidate_path", "candidate_split", "cosine_sim", "rank"])
    writer.writeheader()
    for r in top5_rows:
        writer.writerow({
            "query_path": r["query_path"],
            "query_split": r["query_split"],
            "candidate_path": r["candidate_path"],
            "candidate_split": r["candidate_split"],
            "cosine_sim": r["cosine_sim"],
            "rank": r["rank"]
        })
print(f"  Saved top5_cross_split.csv with {len(top5_rows)} rows")

# 11. Cross-split pairs above thresholds
print("\n[11] Cross-split pairs by cosine_sim threshold (all top-5 combinations):")
# Only unique pairs (query, candidate) — avoid double counting from query/candidate flip
# Count distinct pairs at each threshold
def count_pairs_above(rows, threshold):
    pairs = set()
    for r in rows:
        if r["cosine_sim"] >= threshold:
            key = tuple(sorted([r["query_path"], r["candidate_path"]]))
            pairs.add(key)
    return len(pairs)

for thresh in [0.90, 0.95, 0.99]:
    count = count_pairs_above(top5_rows, thresh)
    print(f"  cosine_sim >= {thresh}: {count} unique pairs")

print("\n" + "=" * 60)
print("STEP A2 COMPLETE")
print("=" * 60)
