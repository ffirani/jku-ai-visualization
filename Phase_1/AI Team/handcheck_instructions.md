# Hand-check of the AI species water ratings

`species_water_handcheck.csv` lists 40 of the 200 species. It is **blind**: the AI ratings are not in it, so please don't open `species_water_rating.csv` while you rate.

For each species:
1. Open the Wikipedia link (or a field guide, e.g. All About Birds / Cornell) and read the habitat and feeding sections.
2. Put a rating 0-3 into `human_rating` using the rubric below. Fill `source_used` (e.g. "Wikipedia", "All About Birds") and `checked_by` (your initials). Use `notes` for doubts.
3. Save the CSV and re-run the notebook. Section 2 then reports exact agreement, agreement within ±1, and weighted kappa against the AI rating.

How the 40 were chosen: all 20 landbird species the AI rated 2 or 3 (they drive the "definition disagreement" result), all 7 species the 4 AI raters disagreed on, White-breasted Kingfisher, and 14 random others (6 landbirds rated 0, 4 rated 1, 4 waterbirds).

## Rubric (the same text the AI raters got)
Rate how strongly each bird species is tied to water habitats (open water, shores, wetlands) on a 0-3 scale. Think about where the species typically feeds, nests and spends its time across its normal range, not about any single photo.

- **0 = no water tie.** Typical habitat is forest, woodland, grassland, desert, scrub, mountains or towns; water plays no special role. (Example not in the list: Wild Turkey.)
- **1 = weak tie.** Regularly seen near water or in damp habitats, or sometimes forages over water, but does not depend on it. (Example not in the list: American Robin.)
- **2 = strong tie.** Mostly lives in wetlands, marshes, swamps, mangroves, riverbanks or shorelines, but feeds mainly on land, in vegetation or in the air rather than in the water. (Example not in the list: Swamp Sparrow.)
- **3 = aquatic.** Gets its food from the water (swimming, diving, plunge-diving, wading for aquatic prey, or snatching food from the water surface) and/or spends most of its life on open water or at sea. (Examples not in the list: Common Loon, Great Blue Heron.)
