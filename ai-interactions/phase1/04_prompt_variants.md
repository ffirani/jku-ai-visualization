# 04 Image or word? Prompt variants and species routing

- **Date:** 2026-11-06
- **Goal:** test whether the background shortcut lives in the word "waterbird" or in the image.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Is the shortcut in the image or in the word? Same images, different text: the baseline prompts; 2-3 descriptive prompt pairs (e.g. "seabird or waterfowl" vs. "land bird"); species routing: zero-shot over the 200 species names, then map species to land/water using the corrected labels. Compare per-group accuracy and the background gap with CIs, and show which images each strategy fixes or breaks.

## What the AI proposed
- Three descriptive pairs: "habitat words" (land bird / seabird or waterfowl), "example taxa" (songbird, woodpecker, … / gull, duck, pelican, …), "lives on" (lives on land / lives on water). Species prompts "a photo of a {species}, a type of bird." with readable names for 9 CUB names (e.g. Geococcyx → Greater Roadrunner, Sayornis → Phoebe, Artic → Arctic).
- **Addition by the AI:** threshold-free measures. Each prompt pair moves the decision threshold, so accuracy alone confuses "prefers one class" with "uses the background". The AI added a background AUC (within class, water vs. land background) and a class AUC (within background), each with a paired bootstrap difference to the baseline.
- Hard (arg-max species) and soft (probability mass on water species) routing.

## Our decision
- accepted 

## Results (executed notebook, section 3)
- Worst-group accuracy: baseline 45.1%, habitat words 30.9%, example taxa 32.6%, lives on 10.5%, species routing (hard) 68.3%, (soft) 64.1%.
- Background AUC: baseline 0.813. The descriptive pairs give 0.870 / 0.917 / 0.918, i.e. they make the background effect stronger (paired differences +0.057, +0.104, +0.105, all CIs above 0). Species routing gives 0.807 (difference −0.006 [−0.018, +0.006]).
- Class AUC: baseline 0.910, species routing 0.959 [0.953, 0.964].
- Species routing fixes 750 and breaks 81 landbirds on water. 595 of 2,302 landbirds on water are still routed to a water species, most often Brown Pelican, Long-tailed Jaeger and California Gull.

## AI mistake in this step, and how it was caught
**The AI wrote the finding text before seeing the numbers, and two claims were wrong.** The first draft of the notebook text said the background AUC "barely moves across the four pairs" and that species routing "lowers the background AUC". The executed output showed the opposite. The descriptive pairs *raise* it from 0.81 to 0.87-0.92, and routing leaves it unchanged; its gain comes from class separation. The figure title had the same error.
- **Caught by:** the AI reading its own executed output before showing it to us. The numbers in the text were computed from cells, so they were right; the words around them ("barely", "lowers") were not.
- **Fix:** the text was rewritten to match the data. The notebook now has `assert` checks for every qualitative claim in a finding or title, e.g. `assert (desc.d_bg_lo > 0).all(), "claim: every rewording makes the background effect stronger"`. If the data changes, the notebook stops instead of showing a wrong sentence.
- **Lesson (best practice candidate):** computed numbers are not enough. Qualitative words ("stronger", "unchanged", "most") need machine checks too.

## Effect on the analysis
The conclusion changed. "Species names reduce the shortcut" became "species names add bird evidence; the background pull is the same". This points Phase II at *why* the coarse class words carry less bird evidence than species names.
