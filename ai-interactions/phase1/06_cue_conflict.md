# 06 Controlled cue-conflict experiment

- **Date:** 2026-11-06
- **Goal:** separate bird, background and written word by editing the inputs, and measure how strongly each moves CLIP's margin.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Controlled cue-conflict experiment (sample about 600 test images, 150 per class × background group, stratified by species, clean masks only; scale up if it runs fast) [...] Conditions: bird only, on neutral gray; background only, with the bird region filled; bird pasted on matching vs. conflicting plates at about 8 scales (1.0 down to 0.15); text overlays "landbird" / "waterbird" / a neutral word at about 8 sizes; extra words at 1-2 sizes: ocean, lake, beach, forest, tree, grass, duck, seagull, sparrow, a nonsense string, "watrbird".

## What the AI proposed beyond the prompt
- **Bird on gray at every scale**, as a control. Without it, "the bird gets smaller" and "the background takes over" can't be told apart.
- **Words and real scenes on the same base image** (the bird pasted at scale 0.5 on gray), so figure (d) compares a word and a scene with everything else held fixed.
- **Text in the band away from the bird.** Neutral word "triangle" (similar length to the class words) as the occlusion control. Nonsense string "xkqzvrtb".
- **One canvas for all edits.** All edits on a 224 × 224 canvas (center-crop, then resize), so CLIP's preprocessing can't crop away text or birds.
- **Larger sample.** Scaled up to 300 birds per group (1,200 birds, 87 conditions each, 104,400 edited images; 654 s), round-robin over species (all 200 species covered).

## Results (executed notebook, section 4)
- Additive fit on the water score: s(orig) ≈ 0.67·s(bird) + 0.65·s(background) + 0.31, R² = 0.83.
- When bird and background disagree (570 birds), the bird wins 65.4% [61.6, 69.3].
- Asymmetry: for landbirds on water the background wins 48.6% of conflicts, for waterbirds on land 15.2%.
- **Shrinking the bird.**
  - Landbirds on a conflicting water plate: wrong 39.0% at full size, 98.7% at scale 0.15.
  - Waterbirds on a conflicting land plate: wrong 20.8% at full size, 50.0% at scale 0.15.
- **A small word.** The misleading class word at 4% cap height (white box = 1.5% of the image) flips 96.7% of landbirds and 78.3% of waterbirds.
- **Word vs. scene, on the same base image.**
  - "waterbird" +4.81 vs. real water scene +1.49 (3.2×). "watrbird" +4.21, "ocean" +1.75, "duck" +1.62.
  - "tree" −1.09 and "sparrow" −1.24 vs. real land scene −0.62.
  - "triangle" −0.13. The nonsense string pushes towards water (+0.90), unexplained.
- **Shared weakness or two shortcuts?** Within each class, background resistance and text resistance are uncorrelated (ρ = −0.05 landbirds, 0.08 waterbirds). The pooled ρ = 0.16 is only the class difference.

## AI mistakes in this step, and how they were caught
1. **Figure 4a title drafted before the data:** "When bird and background disagree, CLIP sides with the background …". The data says the bird wins 65% of conflicts. Caught by the AI reading the executed output before showing it. Rewritten, with an `assert` that the bird-win CI lies above 50%.
2. **Figure 4b title compared unequal conditions:** the largest text size against the full-size bird. It now compares the *small* 4% word with the full-size scene, and an `assert` checks the claim.
3. **The planned plate method failed** (see `05_masks_plates.md`).

## Revised after the critique (check-in 5, we chose "Fix high items 1-7")
The critique (`09_critique.md`) showed that the results above used the wrong uncertainty model and, in places, unequal comparisons.

**What changed in the method:**
- A follow-up run pastes every bird on all 20 plates at all 8 scales and adds a same-base word grid (256,800 more images, 1,293 s). Scene CIs now resample species and plates.

**What changed in the findings:**
- **"Two separate shortcuts": reversed.** Measured as "fooled", the same birds fall for both cues: ρ = 0.39 [0.32, 0.46] for landbirds and 0.32 [0.23, 0.41] for waterbirds. On one shared base the cue-specific shifts correlate too (0.19 / 0.33). Both track weak bird evidence (ρ with the original margin −0.85 / −0.86 for text).
- **"Water scenes pull harder": reframed.** The water-vs-land swing is the same for both classes (2.14 vs. 2.18 logits at scale 0.5). The error asymmetry comes from CLIP's default, which leans "waterbird": a small landbird on plain gray gets s = +0.44.
- **"'ocean' outweighs a real water scene": dropped.** Real water scenes give +1.50 [0.96, 2.06] once plates are resampled, and 'ocean' (+1.75) lies inside that interval and inside the range of the 10 plates.
- **'waterbird' vs. a real water scene: holds.** The word moves the score 3.2× [2.4, 4.9] as far.
- **"A small word beats a whole scene": now dose-matched and holds.** On the same base, a misleading word at 4% flips 89-100% of correctly classified birds, against 16-97% for a conflicting scene. New caveat: at the smallest bird size even meaningless text flips up to 66% of landbirds, and random letter strings push towards water (up to +0.95).
- **"The bird wins 65% of conflicts": holds,** now with a species-cluster CI.

## Our decision
- Check-in 4: we asked for no changes to the figure drafts and chose explorer design B. Check-in 5: "Fix high items 1-7" (see above and `09_critique.md`).

## Effect on the analysis
The story changed from "CLIP looks at the background instead of the bird" to "CLIP adds bird and background evidence about equally; water scenes pull harder than land scenes, and a small written word outweighs both". It also gives Phase II a concrete question: are the scene route and the text route separate inside the model?
