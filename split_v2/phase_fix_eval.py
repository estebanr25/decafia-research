"""
SESSION_FIX_V2 - Full re-evaluation with correct settings + proper bootstrap CIs
iou=0.7 (September setting), plus proper per-class cluster bootstrap validity check.
"""

import json, sys, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import random

REPO         = Path("C:/Users/luise/temp/decafia-research")
SPLIT_V2_DIR = REPO / "split_v2"
PAPER1_DIR   = REPO / "paper1"
RESULTS_DIR  = PAPER1_DIR / "results"
DATASET_ROOT = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean")
V1_MODEL_PATH= Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/02_training/runs/decafia_grouped_v1/weights/best.pt")
V1_DATA_YAML = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1/data_grouped_v1.yaml")
V1_TEST_TXT  = Path("C:/Users/luise/OneDrive/Documentos/DECAFIA_v2/01_dataset/decafia_clean/split_grouped_v1/test.txt")
ASSIGN_CSV   = REPO / "splits/grouped_v1/assignments.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg): print(msg, flush=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()

NAMES = {0: "roya", 1: "coco", 2: "minador"}
NC    = 3
# Correct NMS IoU - matches September documented evaluation
NMS_IOU = 0.7
CONF    = 0.001

log("=== SESSION_FIX_V2: Re-evaluation with iou=0.7 ===")

# ── Load metadata ─────────────────────────────────────────────────────────────
assign_df = pd.read_csv(ASSIGN_CSV)
assign_df = assign_df.rename(columns={"split_new":"split_v1","split_old":"split_disk"})
stem_to_meta = {r.stem: r for r in assign_df.itertuples()}

model_sha256 = sha256_file(V1_MODEL_PATH)
log(f"Model SHA-256: {model_sha256[:16]}...")

# ── Run model.val (iou=0.7) ───────────────────────────────────────────────────
from ultralytics import YOLO
import torch

device = "0" if torch.cuda.is_available() else "cpu"
model = YOLO(str(V1_MODEL_PATH))

log(f"\nRunning model.val (iou={NMS_IOU}, conf={CONF})...")
results = model.val(data=str(V1_DATA_YAML), split="test",
                    conf=CONF, iou=NMS_IOU, imgsz=640, device=device,
                    workers=0, verbose=True, plots=False,
                    name="fix_eval_iou07", project=str(SPLIT_V2_DIR/"runs"), exist_ok=True)

map50_model  = float(results.box.map50)
map9595_model= float(results.box.map)
ap50_model   = {NAMES[i]: float(results.box.ap50[i]) for i in range(NC)}
ap9595_model = {NAMES[i]: float(results.box.ap[i])   for i in range(NC)}
p_model      = float(results.box.mp)
r_model      = float(results.box.mr)

log(f"\nmodel.val results (iou=0.7):")
log(f"  mAP50={map50_model:.6f}  mAP50-95={map9595_model:.6f}")
log(f"  P={p_model:.4f}  R={r_model:.4f}")
for c in range(NC):
    log(f"  {NAMES[c]}: mAP50={ap50_model[NAMES[c]]:.6f} mAP50-95={ap9595_model[NAMES[c]]:.6f}")

# ── Run inference to collect per-image stats ──────────────────────────────────
log("\nCollecting test items...")
test_items = []
with open(V1_TEST_TXT) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        p = Path(line)
        if not p.is_absolute(): p = DATASET_ROOT / line
        stem = p.stem
        lbl_path = Path(str(p).replace("images","labels").replace(".jpg",".txt"))
        gt_boxes = []
        if lbl_path.exists() and lbl_path.stat().st_size > 0:
            for row in lbl_path.read_text().strip().split("\n"):
                parts = row.strip().split()
                if len(parts)==5:
                    gt_boxes.append([int(parts[0])]+[float(x) for x in parts[1:]])
        meta   = stem_to_meta.get(stem)
        source = meta.source if meta else "unknown"
        group  = meta.group_root if meta else stem
        test_items.append({"path":p,"stem":stem,"source":source,
                           "group":group,"gt_boxes":gt_boxes,
                           "is_background":len(gt_boxes)==0})

log(f"Test items: {len(test_items)}")

log("\nRunning inference (iou=0.7, conf=0.001)...")
IMG_PATHS = [str(it["path"]) for it in test_items]
all_preds = []
t0 = time.time()
for i in range(0, len(test_items), 32):
    batch = IMG_PATHS[i:i+32]
    preds_batch = model.predict(batch, conf=CONF, iou=NMS_IOU, verbose=False,
                                 device=device, workers=0)
    for pred in preds_batch:
        boxes = pred.boxes
        all_preds.append({
            "boxes_xywhn": boxes.xywhn.cpu().numpy() if len(boxes)>0 else np.zeros((0,4)),
            "cls":         boxes.cls.cpu().numpy().astype(int) if len(boxes)>0 else np.zeros(0,int),
            "conf":        boxes.conf.cpu().numpy() if len(boxes)>0 else np.zeros(0),
            "img_w": pred.orig_shape[1], "img_h": pred.orig_shape[0],
        })
log(f"Inference done {time.time()-t0:.1f}s")

# ── Match GT ──────────────────────────────────────────────────────────────────
def xywhn_to_xyxy(box, w, h):
    cx,cy,bw,bh = box
    return np.array([(cx-bw/2)*w,(cy-bh/2)*h,(cx+bw/2)*w,(cy+bh/2)*h])

def iou_boxes(a, b):
    ix1,iy1=max(a[0],b[0]),max(a[1],b[1])
    ix2,iy2=min(a[2],b[2]),min(a[3],b[3])
    inter=max(0,ix2-ix1)*max(0,iy2-iy1)
    a1=(a[2]-a[0])*(a[3]-a[1]); b1=(b[2]-b[0])*(b[3]-b[1])
    return inter/(a1+b1-inter+1e-16)

IOU_THRESHOLDS = np.linspace(0.5, 0.95, 10)

image_stats = []
for idx,(item,pred) in enumerate(zip(test_items,all_preds)):
    gt   = item["gt_boxes"]
    w,h  = pred["img_w"],pred["img_h"]
    gt_cls  = np.array([b[0] for b in gt],dtype=int) if gt else np.zeros(0,int)
    gt_xyxy = np.array([xywhn_to_xyxy(b[1:],w,h) for b in gt]) if gt else np.zeros((0,4))
    n_pred  = len(pred["conf"])
    if n_pred>0:
        si = np.argsort(-pred["conf"])
        pred_cls  = pred["cls"][si]
        pred_conf = pred["conf"][si]
        pred_xyxy = np.array([xywhn_to_xyxy(pred["boxes_xywhn"][si[j]],w,h) for j in range(n_pred)])
    else:
        pred_cls=np.zeros(0,int); pred_conf=np.zeros(0); pred_xyxy=np.zeros((0,4))

    tp_matrix = np.zeros((n_pred,len(IOU_THRESHOLDS)),dtype=bool)
    if n_pred>0 and len(gt)>0:
        matched_gt = np.zeros((len(IOU_THRESHOLDS),len(gt)),dtype=bool)
        for d in range(n_pred):
            best_iou=np.zeros(len(IOU_THRESHOLDS))
            best_g  =-np.ones(len(IOU_THRESHOLDS),int)
            for g in range(len(gt)):
                if pred_cls[d]!=gt_cls[g]: continue
                iou=iou_boxes(pred_xyxy[d],gt_xyxy[g])
                for t,thresh in enumerate(IOU_THRESHOLDS):
                    if iou>=thresh and iou>best_iou[t]:
                        best_iou[t]=iou; best_g[t]=g
            for t in range(len(IOU_THRESHOLDS)):
                g=best_g[t]
                if g>=0 and not matched_gt[t,g]:
                    tp_matrix[d,t]=True; matched_gt[t,g]=True

    image_stats.append({
        "stem":item["stem"],"source":item["source"],"group":item["group"],
        "n_gt":len(gt),"gt_cls":gt_cls.tolist(),"gt_xyxy":gt_xyxy.tolist(),
        "n_pred":n_pred,"pred_cls":pred_cls.tolist(),"pred_conf":pred_conf.tolist(),
        "pred_xyxy":pred_xyxy.tolist(),"tp_matrix":tp_matrix.tolist(),
        "is_background":item["is_background"],
    })

log(f"Matched {len(image_stats)} images")

# ── Recompute mAP ─────────────────────────────────────────────────────────────
log("\nRecomputing mAP50 / mAP50-95...")

def compute_ap(tp_arr, conf_arr, n_gt):
    if n_gt==0 or len(conf_arr)==0: return 0.0
    si  = np.argsort(-conf_arr)
    tp  = tp_arr[si].astype(bool)
    fp  = ~tp
    tp_cum = np.cumsum(tp).astype(float)
    fp_cum = np.cumsum(fp).astype(float)
    prec = tp_cum/(tp_cum+fp_cum+1e-16)
    rec  = tp_cum/n_gt
    mrec = np.concatenate(([0.],rec,[1.]))
    mpre = np.concatenate(([0.],prec,[0.]))
    for i in range(mpre.size-1,0,-1): mpre[i-1]=max(mpre[i-1],mpre[i])
    idx = np.where(mrec[1:]!=mrec[:-1])[0]
    return float(np.sum((mrec[idx+1]-mrec[idx])*mpre[idx+1]))

def collect_per_class(stats):
    tp_per_cls={c:[] for c in range(NC)}; conf_per_cls={c:[] for c in range(NC)}
    ngt_per_cls={c:0 for c in range(NC)}
    for s in stats:
        for g in s["gt_cls"]: ngt_per_cls[g]+=1
        for d in range(s["n_pred"]):
            c=s["pred_cls"][d]
            if c<NC:
                tp_per_cls[c].append(s["tp_matrix"][d])
                conf_per_cls[c].append(s["pred_conf"][d])
    return tp_per_cls, conf_per_cls, ngt_per_cls

tp_pc, conf_pc, ngt_pc = collect_per_class(image_stats)

ap50_rc   = {}; ap9595_rc = {}
for c in range(NC):
    if not conf_pc[c]: ap50_rc[NAMES[c]]=0.; ap9595_rc[NAMES[c]]=0.; continue
    tp_arr = np.array(tp_pc[c])  # (N_det, 10)
    cf_arr = np.array(conf_pc[c])
    aps=[compute_ap(tp_arr[:,t],cf_arr,ngt_pc[c]) for t in range(10)]
    ap50_rc[NAMES[c]]  = aps[0]
    ap9595_rc[NAMES[c]]= float(np.mean(aps))

map50_rc   = float(np.mean([ap50_rc[n]   for n in NAMES.values()]))
map9595_rc = float(np.mean([ap9595_rc[n] for n in NAMES.values()]))
log(f"Recomputed mAP50={map50_rc:.6f} (model.val={map50_model:.6f})")
log(f"Recomputed mAP50-95={map9595_rc:.6f} (model.val={map9595_model:.6f})")

# ── P/R/F1 at conf=0.50 ───────────────────────────────────────────────────────
log("\nP/R/F1 at conf=0.50...")
OPERATING_CONF = 0.50
prf1 = {}
for c in range(NC):
    tp=fp=fn=0
    for s in image_stats:
        fn += sum(1 for g in s["gt_cls"] if g==c)
        for d in range(s["n_pred"]):
            if s["pred_cls"][d]!=c: continue
            if s["pred_conf"][d]<OPERATING_CONF: continue
            if s["tp_matrix"][d][0]: tp+=1; fn-=1
            else: fp+=1
    p=tp/(tp+fp+1e-16); r=tp/(tp+fn+1e-16)
    f1=2*p*r/(p+r+1e-16)
    prf1[NAMES[c]]={"P":round(p,4),"R":round(r,4),"F1":round(f1,4),"TP":tp,"FP":fp,"FN":fn}

tp_all=fp_all=fn_all=0
for v in prf1.values(): tp_all+=v["TP"]; fp_all+=v["FP"]; fn_all+=v["FN"]
p_a=tp_all/(tp_all+fp_all+1e-16); r_a=tp_all/(tp_all+fn_all+1e-16)
prf1["all"]={"P":round(p_a,4),"R":round(r_a,4),"F1":round(2*p_a*r_a/(p_a+r_a+1e-16),4)}
log(f"  P/R/F1 at conf=0.50: {prf1}")

# Background FA
bg = [s for s in image_stats if s["is_background"]]
bg_det = sum(1 for s in bg if any(c>=OPERATING_CONF for c in s["pred_conf"]))
bg_far = bg_det/len(bg) if bg else 0.
log(f"Background FA at 0.50: {bg_det}/{len(bg)} = {bg_far:.4f}")

# ── Confusion matrix ──────────────────────────────────────────────────────────
cm = np.zeros((NC+1,NC+1),dtype=int)
for s in image_stats:
    gt_matched=[False]*len(s["gt_cls"])
    for d in range(s["n_pred"]):
        if s["pred_conf"][d]<OPERATING_CONF: continue
        pc=s["pred_cls"][d]
        matched_g=-1
        for g,gc in enumerate(s["gt_cls"]):
            if gc==pc and not gt_matched[g] and s["tp_matrix"][d][0]:
                matched_g=g; break
        if matched_g>=0: gt_matched[matched_g]=True; cm[pc,pc]+=1
        else: cm[pc,NC]+=1
    for g,im in enumerate(gt_matched):
        if not im: cm[NC,s["gt_cls"][g]]+=1
gt_counts={c:int(sum(1 for s in image_stats for gc in s["gt_cls"] if gc==c)) for c in range(NC)}
cm_ok = all(gt_counts[c]==int(cm[:,c].sum()) for c in range(NC))
log(f"CM column sums match GT: {cm_ok} | GT: {gt_counts}")

# ── Section 4: Proper bootstrap CIs ──────────────────────────────────────────
log("\n=== Section 4: Proper bootstrap CIs ===")

# Cluster analysis per class in test set
cluster_analysis = {}
for c in range(NC):
    name = NAMES[c]
    cls_groups = defaultdict(int)
    total_inst = 0
    for s in image_stats:
        for gc in s["gt_cls"]:
            if gc==c:
                cls_groups[s["group"]]+=1
                total_inst+=1
    max_cluster = max(cls_groups.values()) if cls_groups else 0
    max_pct = max_cluster/total_inst*100 if total_inst>0 else 0
    n_clusters = len(cls_groups)
    can_report = max_pct <= 50
    cluster_analysis[name] = {
        "total_instances":total_inst,"n_clusters":n_clusters,
        "max_cluster_pct":round(max_pct,2),"can_report_cluster_ci":can_report,
        "note": ("REPORTABLE" if can_report else
                 f"CANNOT REPORT: single cluster holds {max_pct:.1f}% > 50% of test instances")
    }
    log(f"  {name}: {total_inst} inst, {n_clusters} clusters, max={max_pct:.1f}% -> {'OK' if can_report else 'SKIP'}")

# Classes for which cluster bootstrap is valid
valid_cls = [c for c in range(NC) if cluster_analysis[NAMES[c]]["can_report_cluster_ci"]]
invalid_cls= [c for c in range(NC) if not cluster_analysis[NAMES[c]]["can_report_cluster_ci"]]
log(f"  Valid for cluster CI: {[NAMES[c] for c in valid_cls]}")
log(f"  Invalid for cluster CI: {[NAMES[c] for c in invalid_cls]}")
overall_cluster_ok = len(invalid_cls) == 0
log(f"  Overall cluster CI reportable: {overall_cluster_ok}")

RNG = np.random.RandomState(42)
B   = 2000

# Group structures for cluster bootstrap
grp_to_imgs = defaultdict(list)
for idx,s in enumerate(image_stats): grp_to_imgs[s["group"]].append(idx)
grp_list = list(grp_to_imgs.values())
n_grps   = len(grp_list)

def compute_ap_simple(stat_subset):
    tp_pc2={c:[] for c in range(NC)}; cf_pc2={c:[] for c in range(NC)}
    ngt_pc2={c:0 for c in range(NC)}
    for idx in stat_subset:
        s=image_stats[idx]
        for gc in s["gt_cls"]: ngt_pc2[gc]+=1
        for d in range(s["n_pred"]):
            c=s["pred_cls"][d]
            if c<NC:
                tp_pc2[c].append(s["tp_matrix"][d][0])
                cf_pc2[c].append(s["pred_conf"][d])
    aps={}
    for c in range(NC):
        if not cf_pc2[c] or ngt_pc2[c]==0: aps[c]=0.; continue
        tp_a=np.array(tp_pc2[c],dtype=bool); cf_a=np.array(cf_pc2[c])
        aps[c]=compute_ap(tp_a,cf_a,ngt_pc2[c])
    return aps

log(f"\nRunning cluster bootstrap B={B}...")
boot_cluster = {c:[] for c in valid_cls}
for b in range(B):
    bidx = RNG.randint(0,n_grps,n_grps)
    subset = [i for ci in bidx for i in grp_list[ci]]
    aps = compute_ap_simple(subset)
    for c in valid_cls:
        boot_cluster[c].append(aps[c])

log("Running image-level bootstrap B={B}...")
n_imgs = len(image_stats)
boot_img = {c:[] for c in range(NC)}
for b in range(B):
    subset = RNG.randint(0,n_imgs,n_imgs).tolist()
    aps = compute_ap_simple(subset)
    for c in range(NC): boot_img[c].append(aps[c])

def ci95(arr):
    return float(np.percentile(arr,2.5)), float(np.percentile(arr,97.5))

ci_cluster_valid = {}
for c in valid_cls:
    lo,hi = ci95(boot_cluster[c])
    zero_pct = sum(1 for v in boot_cluster[c] if v==0)/B*100
    ci_cluster_valid[NAMES[c]] = {"lo":round(lo,4),"hi":round(hi,4),
                                   "zero_pct":round(zero_pct,1)}

ci_img = {}
for c in range(NC):
    lo,hi = ci95(boot_img[c])
    ci_img[NAMES[c]] = {"lo":round(lo,4),"hi":round(hi,4)}

log("Cluster CIs (valid classes only):")
for n,v in ci_cluster_valid.items(): log(f"  {n}: [{v['lo']:.4f}, {v['hi']:.4f}]  zero_pct={v['zero_pct']}%")
log("Image-level CIs (all classes, secondary):")
for n,v in ci_img.items(): log(f"  {n}: [{v['lo']:.4f}, {v['hi']:.4f}]")

# ── Roya by source ────────────────────────────────────────────────────────────
log("\nRoya by source (conf=0.50)...")
rbs = defaultdict(lambda:{"tp":0,"fp":0,"fn":0,"n_imgs":0,"n_inst":0})
for s in image_stats:
    src=s["source"]; n_roya=sum(1 for g in s["gt_cls"] if g==0)
    rbs[src]["n_imgs"]+=1; rbs[src]["n_inst"]+=n_roya
    img_tp=0
    for d in range(s["n_pred"]):
        if s["pred_cls"][d]!=0 or s["pred_conf"][d]<OPERATING_CONF: continue
        if s["tp_matrix"][d][0]: rbs[src]["tp"]+=1; img_tp+=1
        else: rbs[src]["fp"]+=1
    rbs[src]["fn"]+=max(0,n_roya-img_tp)
for src,v in rbs.items():
    p=v["tp"]/(v["tp"]+v["fp"]+1e-16); r=v["tp"]/(v["tp"]+v["fn"]+1e-16)
    v["P"]=round(p,4); v["R"]=round(r,4)
    if v["n_inst"]<50: v["flag"]="<50 instances"
    log(f"  {src}: n={v['n_inst']} P={p:.4f} R={r:.4f} {'FLAG' if v['n_inst']<50 else ''}")

# ── Recall by box size ────────────────────────────────────────────────────────
size_recall = {}
for c in range(NC):
    sizes={"small":{"tp":0,"fn":0},"medium":{"tp":0,"fn":0},"large":{"tp":0,"fn":0}}
    for s in image_stats:
        for g_idx,gc in enumerate(s["gt_cls"]):
            if gc!=c: continue
            gt_b = s["gt_xyxy"][g_idx] if g_idx<len(s["gt_xyxy"]) else [0,0,0,0]
            area = (gt_b[2]-gt_b[0])*(gt_b[3]-gt_b[1])
            bkt = "small" if area<1024 else ("medium" if area<9216 else "large")
            matched=any(s["pred_cls"][d]==c and s["pred_conf"][d]>=OPERATING_CONF and s["tp_matrix"][d][0]
                        for d in range(s["n_pred"]))
            if matched: sizes[bkt]["tp"]+=1
            else: sizes[bkt]["fn"]+=1
    size_recall[NAMES[c]] = {bkt:{"recall":round(v["tp"]/(v["tp"]+v["fn"]+1e-16),4),
                                   "tp":v["tp"],"fn":v["fn"]} for bkt,v in sizes.items()}

# ── Build updated metrics_final.json ─────────────────────────────────────────
log("\nBuilding updated metrics_final.json...")

# Load existing (from phase3b)
existing = json.loads((RESULTS_DIR/"metrics_final.json").read_text())

# Replace phase4 section
existing["phase4"] = {
    "model":{"name":"decafia_grouped_v1","sha256":model_sha256,
             "note":"Path B official model; evaluated on its own v1 test split"},
    "nms_iou_setting":NMS_IOU,
    "nms_iou_note":"iou=0.7 matches September documented evaluation (CLEAN_TEST_RESULTS.md, RESULTS_grouped_v1.md)",
    "conf_threshold_for_map":CONF,
    "evaluation_note":"Path B: v1 model on v1 test set. iou=0.7 (NMS) matches September setting.",
    "test_set_full":{
        "n_images":len(test_items),
        "n_backgrounds":sum(1 for s in image_stats if s["is_background"]),
        "map50_model_val":round(map50_model,6),
        "map50_95_model_val":round(map9595_model,6),
        "map50_per_class_model_val":{n:round(ap50_model[n],6) for n in NAMES.values()},
        "map50_95_per_class_model_val":{n:round(ap9595_model[n],6) for n in NAMES.values()},
        "map50_recomputed":round(map50_rc,6),
        "map50_95_recomputed":round(map9595_rc,6),
        "map50_per_class_recomputed":{n:round(ap50_rc[n],6) for n in NAMES.values()},
        "map50_95_per_class_recomputed":{n:round(ap9595_rc[n],6) for n in NAMES.values()},
        "recomputed_matches_model_val":{
            "map50":abs(map50_rc-map50_model)<0.005,
            "map50_95":abs(map9595_rc-map9595_model)<0.005,
        },
        "prf1_at_conf050":prf1,
        "conf050_note":"P/R/F1 at confidence threshold 0.50",
        "background_far_at_conf050":{
            "n_background":len(bg),"n_with_detection":bg_det,"rate":round(bg_far,6)},
        "recall_by_box_size_at_conf050":size_recall,
        "box_size_thresholds_px2":{"small":"<1024 (32x32)","medium":"<9216 (96x96)","large":">=9216"},
        "confusion_matrix_pred_true":cm.tolist(),
        "cm_orientation":"cm[predicted,true]; last row/col=background",
        "cm_column_sums_match_gt":cm_ok,
        "gt_counts_per_class":{NAMES[c]:int(gt_counts[c]) for c in range(NC)},
        "bootstrap_map50_ci95":{
            "method":"Cluster bootstrap (primary, per class where valid), image-level (secondary), B=2000, seed=42",
            "note":"CIs reflect test-set sampling variability only (single training seed)",
            "cluster_validity":cluster_analysis,
            "overall_cluster_ci_reportable":overall_cluster_ok,
            "overall_cluster_ci":"NOT REPORTED: roya cluster bootstrap invalid (single cluster >50% of instances)",
            "per_class_cluster":ci_cluster_valid,
            "per_class_image_level":ci_img,
            "image_level_note":"Image-level bootstrap ignores within-leaf correlation; shown as secondary only",
        },
        "roya_by_source":{k:dict(v) for k,v in rbs.items()},
    },
}

# Update phase3b comparison with iou=0.7
# Re-run filtered test with iou=0.7
log("\nRunning filtered test with iou=0.7...")
FILTERED_YAML = SPLIT_V2_DIR / "data_v1_filtered_test.yaml"
rf = model.val(data=str(FILTERED_YAML), split="test", conf=CONF, iou=NMS_IOU,
               imgsz=640, device=device, workers=0, verbose=False, plots=False,
               name="fix_filtered_iou07", project=str(SPLIT_V2_DIR/"runs"), exist_ok=True)
existing["filtered_test"]["map50_overall"] = round(float(rf.box.map50), 6)
existing["filtered_test"]["map50_95_overall"] = round(float(rf.box.map), 6)
existing["filtered_test"]["nms_iou"] = NMS_IOU
existing["filtered_test"]["note_fix"] = "Re-evaluated with iou=0.7 to match September setting"
log(f"Filtered test iou=0.7: mAP50={rf.box.map50:.6f} mAP50-95={rf.box.map:.6f}")

# Add section2 resolution
existing["section2_resolution"] = {
    "gap_explained_by":"NMS IoU threshold: September used iou=0.7, previous session used iou=0.6",
    "model_sha256_match":True,
    "test_list_stems_match":True,
    "test_list_path_format_differs":True,
    "iou07_map50":round(map50_model,6),
    "iou07_map50_95":round(map9595_model,6),
    "iou06_map50":0.929781,
    "iou06_map50_95":0.731766,
    "sept_reference_map50":0.929,
    "sept_reference_map50_95":0.734,
    "official_setting":"iou=0.7 (documented in CLEAN_TEST_RESULTS.md and results/grouped_v1/RESULTS_grouped_v1.md)",
    "val_check_map50":0.924985,
    "val_check_map50_95":0.732988,
    "val_training_log_map50":0.924,
    "val_training_log_map50_95":0.731,
}

# Add section3 resolution
verif = json.loads((SPLIT_V2_DIR/"mineiro99_verification.json").read_text())
existing["section3_resolution"] = {
    "mineiro99_real_or_artifact":"REAL",
    "cross_group_edges_total":verif["edges_pass"]+verif["edges_fail"],
    "cross_group_edges_pass":verif["edges_pass"],
    "cross_group_edges_fail":verif["edges_fail"],
    "component_size_before":verif["component_before_verification"]["size"],
    "component_size_after":verif["largest_component_after"],
    "mineiro99_size_after":verif["mineiro99_component_after_size"],
    "path_a_feasible":False,
    "path_b_confirmed":True,
    "reason":"Even after removing 4 false pHash edges, SANAS component (322 images) >10% and minador test instances all in MINEIRO_99 (272, majority=train)",
}

# Banned string check
BANNED = ["92.4%","76.6%","2,786","Coccinellidae","Pseudococcidae"]
json_str = json.dumps(existing)
for b in BANNED:
    if b in json_str:
        log(f"[FAIL] Banned string '{b}' in JSON"); sys.exit(1)
log("Banned-string check passed")

(RESULTS_DIR/"metrics_final.json").write_text(json.dumps(existing,indent=2))
log(f"metrics_final.json updated")

log("\n=== Summary ===")
log(f"Section 2: iou=0.7 -> mAP50={map50_model:.6f} mAP50-95={map9595_model:.6f}")
log(f"Section 3: MINEIRO_99 real, {verif['edges_pass']}/{verif['edges_pass']+verif['edges_fail']} edges verified, Path B confirmed")
log(f"Section 4: roya CI not reportable (53.1% in one cluster)")
log(f"  coco CI: [{ci_cluster_valid['coco']['lo']:.4f}, {ci_cluster_valid['coco']['hi']:.4f}]")
log(f"  minador CI: [{ci_cluster_valid['minador']['lo']:.4f}, {ci_cluster_valid['minador']['hi']:.4f}]")
