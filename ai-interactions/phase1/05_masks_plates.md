# 05 Segmentation masks and background plates (cue-conflict setup)

- **Date:** 2026-11-06
- **Goal:** cut birds out reliably and get clean land/water background scenes for the controlled experiment (analysis 4).
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Cut the bird out with a segmentation model (e.g. `rembg`). Check masks by area and with a contact sheet.
  > Background plates: about 10 land and 10 water scenes, e.g. from Waterbirds images with small birds, with the bird removed by OpenCV inpainting. Check them visually and document the choice.

## What the AI did
1. **Masks.** rembg (U^2-Net, CPU) on all 5,794 test images, about 40 min, cached as 224 px masks. "Clean" rule fixed from mask statistics and contact sheets *before* any edited image was scored by CLIP: area 2-60%, largest component ≥ 90% with ≤ 2 components, ≤ 15% border contact, ≤ 35% soft pixels. Result: 5,102 of 5,794 masks clean (88.1%), similar across the 4 groups (86.7-89.3%).
2. **Plates, first attempt (the plan's suggestion): rejected.** Images with tiny masks (0.2-3%) plus OpenCV inpainting. The contact sheet (`outputs/fig4_qc_plates_rejected_attempt.png`) showed that tiny masks are mostly *failed, partial* segmentations. In 4 of 10 land plates the bird (e.g. a whole Black-billed Cuckoo, a Ruby-throated Hummingbird) was still visible after inpainting, and only 4 water images qualified.
3. **Plates, used: bird-free crops.** For 120 random clean-mask images per background type, the full-resolution image is segmented with two independent models (U^2-Net and IS-Net). The union of both masks is dilated by 3% of the short side, and the largest bird-free square (chessboard distance transform) is cropped and resized to 224 px. Candidates were ranked by crop size. The AI walked down the list and kept a crop if (1) no bird part is visible, (2) the scene type is recognisable and (3) it is a colour photo, until it had 10 per type. Rejected: #1554 grayscale; #361 person in crop, mostly trees; #4839 palm trees and roof, water barely visible; #253 dune, no water; #5538 hills, no water; #1269 flat teal area; #3086 snowy reeds, unclear. No CLIP score was used anywhere in plate selection.
4. **Condition check.** `outputs/fig4_qc_conditions.png` shows every condition type for 2 birds.

## AI mistakes / limits in this step
- **The plan's plate method did not work as stated.** The master prompt (written by the AI in the scoping chat) suggested "Waterbirds images with small birds, bird removed by inpainting". Small masks select segmentation failures, not small birds. **Caught by** the contact sheet the plan required, before any experiment was run. **Fix:** crop-based plates with two segmenters (above).
- The AI also picked plates by eye. This is a judgment call; the rule and every rejection are logged, and we confirm the picks at check-in 2.
- **Tooling slip.** When switching the notebook to the crop-based plates, the AI patched the notebook source with a script. The script turned `\n` escape sequences inside a Python string into real line breaks, so the notebook run stopped with a `SyntaxError` (unterminated f-string). The AI then fixed the cell with a direct edit.
- Known limitation that remains: the "background only" condition uses inpainting over the full bird region, which leaves a visible smudge where a large bird was (see the condition sheet). CLIP may read that blob.

## Our decision (check-in 2, 2026-11-06)
- Masks rule and the crop method: **accepted**.
- Plates: **modified.** The AI flagged water-3 (#66, mostly trees with a strip of river) and water-4 (#3294, mostly mountain above a fjord) as borderline; we chose "Replace water-3/4". The AI tightened the rule (water must be a large part of the crop) and continued down the ranked list. It rejected #4583 (mostly bushes, water at the edge) and #2066 (trees only) and accepted #1162 (breaking wave) and #818 (sea at dusk).
- Final plates: land #5639, 4757, 2270, 128, 3330, 4579, 898, 1703, 3598, 5238; water #4926, 2772, 1788, 4314, 4613, 3097, 5570, 2461, 1162, 818.
- Why it matters: the AI's own visual check had been too lenient for "water" scenes. Its criterion "water visible" let through scenes where land dominates, which would have weakened the conflicting-background condition for landbirds.

## Effect on the analysis
Plates no longer contain birds, so "bird on conflicting plate" really means one bird against a scene.
