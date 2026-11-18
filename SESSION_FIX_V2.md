# DECAFIA Paper 1: resolve three blockers from the split-v2 session (one session)

> **For Esteban:** save as `SESSION_FIX_V2.md` in `C:\Users\luise\temp\decafia-research`. Open **Claude Code on your PC** in that folder, select Fable, and send:
> *"Read SESSION_FIX_V2.md and execute it end to end on branch split-v2. Do not stop to ask me questions; follow its decision rules."*
> You authorize in advance: evaluations and, only if Section 3 says so, the one training run already authorized in SESSION_SPLIT_V2.md.

---

## 0. Context

The previous session (`SESSION_SPLIT_V2.md`, branch `split-v2`) chose Path B and reported:
- full v1 test: mAP50 0.9281 / mAP50-95 0.7228;
- filtered v1 test (307 images): 0.9261 / 0.7269;
- cluster-bootstrap 95% CI for mAP50 [0.847, 0.943];
- Path A failed because component `MINEIRO_99` holds 290 images (12.5% of the dataset), including every minador test image.

Three of these results block the manuscript:

1. **Not reproduced.** CLAUDE.md states test mAP50-95 = 0.734; the session measured 0.7228 (Δ = −0.011, about 5× a reasonable tolerance of 0.002). mAP50 matches (0.9281 vs 0.929). The session did not flag this.
2. **MINEIRO_99 may be an artifact of my own merge rule.** Tier A merged every pair with dihedral pHash distance ≤ 4 **without geometric verification**. The minador images come from Silva et al. (Mendeley, DOI 10.17632/vfxf4trtcg.5), whose description says most photos were taken in a laboratory on a white background. Different leaves on a uniform white background can have very close perceptual hashes, and a few false links chain everything into one component. If the component is real, minador cannot be evaluated on held-out leaves at all. If it is an artifact, Path A may be feasible.
3. **The confidence interval is not interpretable.** The interval [0.847, 0.943] around 0.928 is lopsided. It probably measures whether the giant cluster is drawn in a resample, not sampling uncertainty.

Rules from `SESSION_SPLIT_V2.md` Section 1 still apply: read-only data and v1 artifacts, no installs, no steering toward expected numbers, numbers rendered from JSON, banned strings, Git on `split-v2` only, fail loudly, and don't stop to ask.

---

## 1. Freeze

- **Do not** paste or apply `paper1/PASTE_INTO_CLAUDE_PROJECT.md`.
- If the previous session changed CLAUDE.md's "Source of truth" section, revert that change on this branch now (separate commit, with the diff in the report). It goes back in only after Section 2 is resolved.

---

## 2. Reproduction: explain 0.734 vs 0.7228

1. Find the September evaluation that produced 0.929 / 0.734. Search the repo, `_cache/`, the `runs/` folders, and `manuscript_checks/` for result files, logs, or JSON containing those values, the September full-test table (P 0.876, R 0.870), or `CLEAN_TEST_RESULTS.md`. List every candidate with path, modification time, and hash.
2. Record the settings of both evaluations side by side: Ultralytics version, `conf`, `iou`, `imgsz`, `batch`, `rect`, `half`, `device`, the exact model file hash, and the exact test list hash.
3. Re-run `model.val` with the September settings if they can be recovered. Report both runs.
4. **Model identity.** All trainings (April/May on the old dataset, August/September on the corrected ones) were run on this same computer, so there are several model files from different datasets here.
   - Compute the SHA-256 of the weights file evaluated in the previous session and of `weights/best.pt` inside the September `decafia_grouped_v1` run directory. Several copies of models and datasets exist on this computer, so also list every `*grouped_v1*.pt` file anywhere under `C:\Users\luise` with its hash.
   - **Decisive check:** evaluate the September `best.pt` on the **val** split now and compare against the val mAP50 / mAP50-95 logged at the best epoch in that run's `results.csv` (expected about 0.924 / 0.731). That value was computed by the same weights during training.
   - If today's val matches the log, the model and settings are consistent, so look for the test gap in the test list (compare hashes) or the test-time settings.
   - If today's val is also lower by a similar amount, the gap comes from the evaluation settings or a package update since September, not from the model.
   - If the hashes differ, the previous session evaluated a different model (for example, one from April/May or the leaky `decafia_clean` model): report which file it used and re-run everything with the right one.
5. **Decision rule:**
   - If a different weights file, a settings difference, or a version difference explains the gap: the official number is the one from a run whose settings are fully documented and reproducible today. Report which one it is and why.
   - If nothing explains it (same model hash, same list hash, same settings, different result): stop Sections 3–4, write `paper1/DISCREPANCY.md`, and go to Section 5.

---

## 3. MINEIRO_99: real or artifact?

1. **Anatomy.** List nodes by filename prefix, split, and class. List edges by type (v1 crop–parent link, v1 capture-series block, Tier A, Tier B). Report the degree distribution and the **bridges / minimum edge cut**: the fewest edges whose removal splits the component.
2. **Verify every Tier A and Tier B edge globally,** not just inside the component. Use the edge's best dihedral transform plus SIFT + RANSAC restricted to a **foreground mask suited to each image**: non-white pixels for white-background laboratory images (saturation/brightness threshold), and the green-leaf HSV mask for field images. Merge only if inliers ≥ 30 and hull coverage ≥ 0.50 of the foreground. Keep v1 crop–parent and capture-series links as they are.
3. **Count and map.** Count minador images and roya images that come from Silva et al. The source dataset describes 285 rust and 257 leaf-miner photos. Map DECAFIA files to original Silva photos where filenames allow it, and report how many distinct original photos underlie the minador class and how many DECAFIA images are crops or transformed derivatives of each.
4. Rebuild components with **verified edges only** and re-check the four Path A conditions from `SESSION_SPLIT_V2.md` Phase 2.
5. **Decision rule:**
   - **All Path A conditions now hold → execute Path A** exactly as specified in `SESSION_SPLIT_V2.md` (build `split_grouped_v2` with minimal movement, verify zero cross-split verified copies, one training run with v1 hyperparameters, evidence package on v2).
   - **Still a giant verified component →** the minador copies are real. Stay on Path B, and in every output state that minador test images are linked to training images through verified transformed copies, so minador performance cannot be estimated on held-out leaves with this data. Report the headline results **both** with all three classes and with roya + coco only (mean over those two classes), each clearly labeled.

---

## 4. Confidence intervals done properly

For the final split and model:
- Report the number of clusters (components) per split and per class in test.
- Run the cluster bootstrap **per class**. For each class, report the fraction of resamples in which that class has zero test instances, and how such resamples were handled (excluded, never silently imputed).
- If a single cluster holds more than 50% of a class's test instances, state that the cluster bootstrap cannot estimate that class's interval, and don't report one.
- The overall interval is reported only if every class passes that check. Otherwise report per-class intervals for the classes that pass.
- Keep the image-level bootstrap as a secondary, clearly labeled "ignores within-leaf correlation".

---

## 5. Outputs and report

- Update `paper1/results/metrics_final.json`, `RESULTS_FINAL.md`, `NUMBERS_FOR_MANUSCRIPT.md`, `MANUSCRIPT_CHANGES.md`, and the figures affected by the outcome.
- Re-run the independent verification subagent (fresh, receives only the briefs and outputs).
- Restore the CLAUDE.md update and regenerate `PASTE_INTO_CLAUDE_PROJECT.md` **only** if Section 2 is resolved and verification passes.
- Write `split_v2/REPORT_FIX.md`. Page one has five short answers:
  1. Which number is the official test mAP50-95, and why the 0.734 / 0.7228 gap happened.
  2. Is MINEIRO_99 real or an artifact? Give the number of edges that survived verification and the size of the largest verified component.
  3. Which path was finally taken (A or B).
  4. The final headline numbers with valid intervals, or the reason an interval isn't reported.
  5. Exactly what the manuscript must say about minador.

Then details. Push the branch. Do not merge into `main`.
