# 09 Critique pass (check-in 5)

- **Date:** 2026-11-06
- **Goal:** let the AI attack its own analysis before we present it (Lab 03: "GenAI as collaborator to critique your design and findings").
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Critique pass: you list weaknesses, alternative explanations and missing checks; we decide what to act on.

## How it was done
A multi-agent workflow (`09_critique_workflow.js`, run `wf_e66f4890-c55`, 8 agents, about 33 min).
- **Review:** five independent reviewers, one lens each:
  - statistics
  - confounds and alternative explanations
  - course rules and reproducibility
  - visualization
  - the GenAI-derived species attribute
- **Material:** each reviewer read a text dump of the executed notebook and the figure PNGs, read only. Several recomputed numbers from the cache without changing files.
- **Synthesis:** one synthesizer merged the 40 raw items into 14.
- **Verification:** two adversarial verifiers tried to refute every item against the notebook (verdict valid / partly valid / refuted).

All 14 items and the verifiers' evidence are in `09_critique_raw.json`. In short:

| # | severity | verdict | item |
|---|---|---|---|
| 1 | high | valid | Scene effects ignore that each of the 10 plates is shared by about 120 birds. With a plate-then-bird bootstrap, the water scene is +1.49 [0.94, 2.04] and the land scene −0.62 [−1.12, −0.19]. "'ocean' outweighs a real water scene" and "'tree' moves further than a real land scene" no longer hold, and the 3.2× ratio becomes about [2.4, 5.0]. Single plates drive the 39% / 21% headline. |
| 2 | high | valid | "Two separate shortcuts" depends on the metric. Measured as *being fooled* (share of scales or sizes wrong), ρ = 0.30 (landbirds) and 0.23 (waterbirds): the same weak-evidence birds are fooled by both cues. Margin-loss resistance removes exactly that shared factor. |
| 3 | high | partly valid | "Water scenes pull harder" depends on the zero threshold and the intercept. The paired background swing (matching − conflicting plate) is the same for both classes. |
| 4 | high | valid | Section 2 CIs resample images, not species. With a species-cluster bootstrap, the land-background "definition effect" (19.9% vs. 11.8%) loses significance and rests mostly on the kingfishers. |
| 5 | high | valid | The error decomposition by rule order counts base-rate errors as "definition". Measured as excess risk, the definition share is about 4%, not 15.5%. |
| 6 | high | valid | "A small word beats a whole scene" compares different bases, doses and controls. A conflicting plate at scale 0.15 fools 98.7% of landbirds. |
| 7 | high | valid | The section 5 error clusters do not beat the trivial group label (the group label concentrates errors with lift 1.89, the clusters with 1.55). C1 is below its composition-expected error. |
| 8 | medium | partly valid | "The bird wins because its evidence is larger" compares a clean bird on gray with an inpainting-damaged background. The large-mask smudge is not calibrated. |
| 9 | medium | valid | Section 2's ecology and section 5's appearance (black birds) overlap. Rated-2 species include several black icterids; neither analysis controls for the other. |
| 10 | medium | partly valid | Section 3 cannot fully separate word from image: every rewording adds habitat words, and panels b/c start far from the 0.5/1.0 reference. |
| 11 | medium | partly valid | Alternative mechanism: plain or dark inputs (the gray canvas itself) may lean "waterbird". No empty-canvas control exists. |
| 12 | medium | partly valid | Section 5 projects a 230-d *linear readout* of CLIP's image embedding (prompt logits). Allowed as "outputs" by our reading of the rules, but a grader could see it as projecting embeddings. Ask the instructors, or show that the findings survive on a few named scores. |
| 13 | medium | partly valid | Rating reliability: κ is inflated by the many easy cases; the raters share model families; the binary ≥ 2 set differs between raters (15 by all four, 24 by at least one). Validate against a non-LLM trait source (e.g. AVONET). |
| 14 | low | partly valid | Reproducibility: cache files are not keyed to their inputs; the font silently falls back; no `revision=` pins; a few numbers in markdown cells are not computed. |

## Assessment by the AI (facts only)
- Items 1, 2, 4, 5 and 6 each contradict a sentence or figure title that the notebook currently states as a finding. The asserts did not catch them because they tested the claims against CIs that were too narrow (1, 4) or against a single chosen metric (2, 5, 6).
- This is a new failure pattern, added to the reflection as pattern 8 ("claims backed by the wrong uncertainty model"); see `ai_reflection_midpoint.md`.

## Our decision (check-in 5, 2026-11-06)
**"Fix high items 1-7".** Items 8-14 stay as stated limitations or Phase II questions.

## What the AI changed
- **All CIs resample whole species** (sections 1-5); scene effects resample species and plates (crossed). New helpers: `stats.cluster_boot_mean`, `stats.two_way_boot_mean`, and species-cluster versions of the AUC tests.
- **Item 1:** a follow-up run pastes every bird on all 20 plates at all 8 scales (192,000 images) and adds a same-base word grid (64,800 images): `experiment.run_v2`, cached with the sample and plates it was built from. Figure 4d shows the per-plate means and the range of the meaningless controls.
- **Item 2:** figure 4c shows both "same birds fooled?" (share of conditions wrong) and "same shift?" (cue-specific shift on one shared base).
- **Item 3:** new figure 4e: each scene type against the gray base, and the reference-free water-vs-land swing per class. Figure 4a now draws the fitted decision lines instead of reading wins at 0.
- **Item 4:** section 2 reports ratings 2 and 3 separately, per background, with species-cluster CIs and a species-level permutation test.
- **Item 5:** section 2's decomposition is now an additive excess-risk decomposition.
- **Item 6:** new figure 4f: a dose-matched word vs. scene comparison on the same base, counting only birds correct on that base.
- **Item 7:** error clusters are now defined by excess over the group-expected error. The k-NN test adds CLIP's own prediction, a version with the score regressed out, and within-group AUCs, with CIs. Every part of each cluster description is tested, and failed parts are shown, not forced.

## Effect on the analysis (final run, 66 cells, 0 errors)
| first draft | after the fixes |
|---|---|
| Label definition explains 15.5% of errors (rule order) | 4.3% [1.0, 8.2] as excess risk; background excess 61.7% [56.8, 66.5] |
| Water-tied landbirds (rating ≥ 2) misread more, also on land | Only the 5 rating-3 species (4 kingfishers, Louisiana Waterthrush): 49.4% vs. 11.8% on land, p = 0.0001; rating 2 not different (p = 0.40) |
| "Two separate shortcuts" | Reversed: the same weak birds fall for both cues (fooled ρ = 0.39 / 0.32; same-base shifts 0.19 / 0.33) |
| "Water scenes pull harder" | Reframed: the scene swing is symmetric (2.14 vs. 2.18 logits); CLIP's default leans "waterbird" (small landbird on gray: s = +0.44) |
| "'ocean' outweighs a real water scene" | Dropped: real water scenes +1.50 [0.96, 2.06]; "ocean" lies within the plate range. "waterbird" = 3.2× [2.4, 4.9] a real water scene |
| "A small word beats a whole scene" (unequal doses) | Dose-matched: a 4% word flips 89-100% of correct birds vs. 16-97% for a conflicting scene; meaningless text flips up to 66% of tiny landbirds |
| 5 error clusters vs. the overall error rate | 4 clusters with excess over the group-expected error (+10 to +21 points); C1 dropped (only its group mix) |
| Errors cluster in CLIP's outputs more than in DINOv2 (0.89 vs. 0.80) | Mostly self-prediction: 0.77 with CLIP's score removed (DINOv2 0.80; within groups 0.71 vs. 0.76) |

Unchanged: the baseline and the label bug, "the shortcut is not in the word" (section 3, now with species-cluster CIs), and the additive cue model, where the bird wins 65% of conflicts.
