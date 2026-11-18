====================================================================
README — How to update the claude.ai project
====================================================================

Three steps, in order:

--------------------------------------------------------------------
STEP 1: DELETE old files in the project
--------------------------------------------------------------------

In the claude.ai project file browser, DELETE these files if they exist:
  - RESULTS.md  (old results from leaky baseline)
  - CLAUDE.md   (old version)
  - confusion_matrix_normalized.png  (old figure)
  - training_curves.png              (old figure)
  - pr_curves.png                    (old figure)
  - test_predictions_grid.png        (old figure)
  - Any file whose name mentions "0.924" or "0.734" or "leakage"

--------------------------------------------------------------------
STEP 2: UPLOAD new files from paper1/for_claude_project/
--------------------------------------------------------------------

Upload ALL files in this folder:
  - CLAUDE.md                           (updated source of truth)
  - RESULTS_FINAL.md                    (corrected numbers, iou=0.7)
  - figure3_confusion_counts.png        (confusion matrix, raw counts)
  - figure3_confusion_normalized.png    (confusion matrix, normalized)
  - figure5_training_curves.png         (training curves)
  - figure7_bootstrap_intervals.png     (per-class mAP with CIs, corrected)

--------------------------------------------------------------------
STEP 3: REPLACE project instructions
--------------------------------------------------------------------

Go to the project "Instructions" (or "Description") settings.
Replace BOTH the description AND instructions with the text in:
  PROJECT_INSTRUCTIONS.txt

(Copy the entire contents of that file and paste it into the
 "Project instructions" field in claude.ai.)

====================================================================
DONE. The project now reflects the correct numbers and policies.
====================================================================
