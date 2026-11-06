# 02 Baseline reproduction and label audit

- **Date:** 2026-11-06
- **Goal:** our own implementation of the zero-shot baseline on the full test set, reproduce the expected numbers, then apply the label fix.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Label bug, apply before any analysis: Eastern_Towhee, Western_Meadowlark and Western_Wood_Pewee are landbirds but labeled waterbird. [...] Set their label to 0, keep the old label in `label_original`, and report results before and after the fix.
  > Reproduction check: before the fix, overall accuracy should be about 70.6%. Per group: 87.6% (landbird/land), 45.1% (landbird/water), 74.9% (waterbird/land), 96.0% (waterbird/water).

## What the AI did
- Wrote `aivis/clipscore.py`: one pass over the images scores a bank of 238 prompts (baseline pair, 3 descriptive pairs, 200 species, 30 scene/context prompts). Only the resulting logits are kept.
- Wrote `aivis/data.py`: metadata table with `label_original`, the corrected `label`, `tern_bug` flag, group names before and after the fix.

## Results (from the executed run; bootstrap 95% CI, 2,000 resamples)
| | original labels | corrected labels |
|---|---|---|
| overall | 70.6% [69.4, 71.7] | 71.0% [69.8, 72.1] |
| landbird / land | 87.5% [86.2, 88.9] (n=2,255) | 87.5% [86.1, 88.9] (n=2,298) |
| landbird / water | 45.1% [43.1, 47.2] (n=2,255) | 45.1% [43.0, 47.2] (n=2,302) |
| waterbird / land | 74.9% [71.7, 78.3] (n=642) | 79.3% [76.0, 82.5] (n=599) |
| waterbird / water | 96.0% [94.2, 97.4] (n=642) | 99.2% [98.3, 99.8] (n=595) |

- Reproduced. The only deviation is landbird/land at 87.54% vs. the expected "87.6%" (1,974 of 2,255; a 1-image difference, likely rounding or fp16 in the reference).
- The 3 bug species have 90 test images (43 on land, 47 on water). CLIP calls 35.6% of them waterbird.
- Under the original labels they cause **21 of the 26 errors in waterbird/water** and **37 of the 161 errors in waterbird/land**.

## Verification of the bug itself
- In `grodino/waterbirds` the species names containing the substring "tern" (lowercased) are the 7 real terns, Western_Grebe and Western_Gull (waterbirds anyway), and exactly the 3 affected landbirds.
- The 46 species with original label 1 are the 17 water categories of `generate_waterbirds.py` (Albatross, Auklet, Cormorant, Frigatebird, Fulmar, Gull, Jaeger, Kittiwake, Pelican, Puffin, Tern, Gadwall, Grebe, Mallard, Merganser, Guillemot, Pacific_Loon), plus the 3 bug species.

## Our decision
- Check-in 1 (environment + baseline), our reply verbatim: "Yes, continue". So: accepted.
## Effect on the analysis
From here on the corrected labels are the default. The "waterbird/water is 96%" headline was mostly the label bug: with correct labels only 5 waterbird/water images are wrong.
