# 03 Species water association: a GenAI-derived attribute

- **Date:** 2026-11-06
- **Goal:** rate each of the 200 species for how tied it is to water habitats (0-3 plus a one-line reason), as an interpretable attribute for the error analysis (Lab 03: "GenAI as tool to transform your data"). Because "GenAI-derived data is not ground truth", the AI also measured its own reliability and prepared a blind human check.
- **Key prompt from us (verbatim, from `00_master_prompt.md`):**
  > Species water association (GenAI-derived attribute): rate each of the 200 species for how tied it is to water habitats (0-3 plus a one-line reason) and save to `species_water_rating.csv`. We will hand-check at least 30 against a field guide or Wikipedia; report the agreement.

## What the AI proposed and did
Instead of one rating pass, the AI ran a small multi-agent workflow (Claude Code `Workflow` tool, run `wf_e49be750-b0a`, 6 agents, about 4 minutes):

| rater | model | prompting |
|---|---|---|
| A | claude-opus-5-5 | rubric, rating + reason + confidence |
| B | claude-sonnet-5-5 | same rubric |
| C | claude-haiku-5-5 | same rubric |
| D | claude-opus-5-5 | same rubric, but "first describe where it feeds and nests, then rate" |

- All raters answered from their own knowledge, without web search, and none saw CLIP's results or the dataset labels.
- **Final rating rule:** the value given by at least 3 of the 4 raters. Otherwise an adjudicator agent (opus) read all four ratings and reasons and picked a level.
- A final "consistency critic" agent (opus) read all 200 final ratings and flagged clear inconsistencies between related species. Its flags are only recorded (column `critic_flag`), not applied.
- Anchor examples in the rubric were deliberately chosen from species **not** in the dataset (Wild Turkey, American Robin, Swamp Sparrow, Common Loon, Great Blue Heron). This keeps the rubric from pre-deciding e.g. the kingfishers.
- For ambiguous CUB names the raters got a clarifying note (e.g. `Sayornis (phoebes, genus Sayornis)`, `White_breasted_Kingfisher (White-throated Kingfisher, Halcyon smyrnensis)`, `Tree_Sparrow (American Tree Sparrow)`).

### Rubric (verbatim, given to every agent)
> Rate how strongly each bird species is tied to water habitats (open water, shores, wetlands) on a 0-3 scale. Think about where the species typically feeds, nests and spends its time across its normal range, not about any single photo.
>
> 0 = no water tie. Typical habitat is forest, woodland, grassland, desert, scrub, mountains or towns; water plays no special role. (Example not in the list: Wild Turkey.)
> 1 = weak tie. Regularly seen near water or in damp habitats, or sometimes forages over water, but does not depend on it. (Example not in the list: American Robin.)
> 2 = strong tie. Mostly lives in wetlands, marshes, swamps, mangroves, riverbanks or shorelines, but feeds mainly on land, in vegetation or in the air rather than in the water. (Example not in the list: Swamp Sparrow.)
> 3 = aquatic. Gets its food from the water (swimming, diving, plunge-diving, wading for aquatic prey, or snatching food from the water surface) and/or spends most of its life on open water or at sea. (Examples not in the list: Common Loon, Great Blue Heron.)
>
> Rate each species independently, based on its ecology only. The reason must be one short line (at most about 15 words) naming the habitat or behavior that decides the rating. Confidence is how sure you are of the rating (low / medium / high).

Rater instruction around the rubric (verbatim, A-C):
> You are rating bird species for a research dataset. Answer from your own ornithological knowledge only: do not use any tools, do not search the web and do not read or write files. [rubric] For each species give `rating`, a one-line `reason` and `confidence`. Species identifiers use underscores for spaces; notes in parentheses clarify ambiguous names. Return exactly one entry per species, in the same order, with `species` copied exactly as the identifier before any parentheses. [200 species]

Rater D replaced the middle sentence with:
> For each species, FIRST write `habitat`: where it typically feeds and nests (at most about 20 words). THEN decide `rating` from that description using the rubric, and give a one-line `reason`.

The workflow script is `03_species_ratings_workflow.js`; every agent's raw answer is in `03_species_ratings_raw.json`.

## Results (from the workflow output)
- 193 of 200 species reached 3-of-4 consensus. 7 were adjudicated: Gray_Catbird → 1, Yellow_breasted_Chat → 1, Olive_sided_Flycatcher → 1, Nighthawk → 1, Le_Conte_Sparrow → 2, Louisiana_Waterthrush → 3, Cedar_Waxwing → 1.
- Exact agreement with rater A: Sonnet 94.0%, Haiku 88.5%, the habitat-first prompt 97.5%. The notebook (section 2) reports the weighted kappas.
- Distribution: 111 species rated 0, 26 rated 1, 15 rated 2, 48 rated 3. All 43 dataset waterbirds are rated 3. **20 dataset landbirds are rated 2 or 3**: the 4 American kingfishers (Belted, Green, Pied, Ringed; rated 3), Louisiana Waterthrush (3), and marsh/shore species such as Red-winged and Yellow-headed Blackbird, Marsh Wren, Seaside and Nelson's Sparrow, Prothonotary Warbler, Tree and Bank Swallow (rated 2).
- White-breasted (White-throated) Kingfisher was *not* rated 2-3: it often hunts away from water.
- The critic flagged one item: Northern_Waterthrush (2) should match Louisiana_Waterthrush (3).

## Our decision
- AI decision (small, logged): the critic flag is **not** applied automatically. Both waterthrushes are in the human hand-check sample instead.


## Revised after the critique (check-in 5)
- The section 2 CIs now resample species, and the main test is a species-level permutation test.
- **Only the 5 rating-3 landbirds stand out:** the 4 kingfishers and Louisiana Waterthrush, 49.4% wrong on land vs. 11.8% (p = 0.0001). The 15 rating-2 marsh landbirds are not distinguishable from dry-land species (p = 0.40 on land, 0.08 on water).
- **Excess-risk decomposition.** The label definition explains 4.3% [1.0, 8.2] of the errors instead of the rule-ordered 15.5%. Background excess: 61.7% [56.8, 66.5].
- The earlier image-level claim "the gap also exists on land backgrounds for rating ≥ 2" did not survive species clustering.

## Effect on the analysis
- Section 2 of the notebook uses `water_rating` to split the errors into label bug / definition disagreement / background shortcut.
- The hand-check agreement is computed in the notebook once `human_rating` is filled in.

## How it will be verified
- Inter-rater agreement between different models and prompts (done above; this checks consistency, not correctness).
- Blind human check of 40 species against Wikipedia or a field guide: all 20 high-rated landbirds, all 7 disputed, plus random ones.

## AI mistakes / limits seen in this step
- **Overstated trend in the notebook text.** The first draft of the section 2 finding said "error rate rises with the rating". The species-level Spearman ρ was 0.14 [−0.02, 0.30], so the CI includes 0. Caught by the AI when reading the executed output. The text now says the trend is weak and the effect sits in the few strongly water-tied species; an `assert` checks that the CI includes 0.
- None of the four raters returned malformed or missing entries; the gap-filling step never triggered.
- Agreement between raters is not evidence of correctness: all four share similar training data. The human check is still needed.
