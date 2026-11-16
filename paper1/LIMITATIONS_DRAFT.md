# LIMITATIONS_DRAFT.md

Only what the data supports:

1. Bootstrap CIs reflect test-set sampling variability with a single training seed.
   Training stochasticity is not quantified.

2. Path B was chosen because the MINEIRO component (290 images, 12.5% of dataset)
   exceeded the 10% threshold, and all minador test images are in this component,
   making it impossible to have >=100 minador test instances while maintaining
   split proportions within 2 percentage points. A new split would require manual
   group re-assignment or a different grouping strategy.

3. The roya-by-source comparison has limited statistical power for subsets with
   fewer than 50 instances (flagged in metrics_final.json).

4. The sensitivity analysis (full vs filtered test) shows a 0.37pp mAP50 drop
   when 49 contaminated images are excluded. This bounds but does not fully
   characterize the effect of transformed-copy leakage, since:
   (a) the two test sets have different compositions;
   (b) the filtered test set still uses the same train set (not a re-trained model).

5. 'coco' class refers to Curculionidae (bean weevil); per Hard Rule 6
   the taxonomy must not be listed as other beetle families.
