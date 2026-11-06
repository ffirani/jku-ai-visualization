# 07 Overview projection of CLIP's outputs, error clusters, DINOv2 comparison

- **Date:** 2026-11-06
- **Goal:** an overview of all 5,794 images that shows where the errors are, and a drill-down into what sets the error regions apart.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Overview projection [...]: UMAP of each image's vector of CLIP similarity scores over a prompt bank (200 species prompts plus about 30 scene/context prompts). Use outputs only, not embeddings. Color = margin, shape = group. Check stability across seeds and parameters. Drill into the error clusters and describe what sets them apart. You may draft cluster descriptions, but verify them against the data. If time allows, compare with a UMAP of a separate image encoder (e.g. DINOv2-small).

## What the AI did
- Output vector = 230 logits (200 species + 30 scene/context prompts), centered per image and z-scored per prompt. UMAP for display.
- Stability check: 3 seeds × 2 settings.

## AI mistakes in this step, and how they were caught
1. **The first design clustered on the 2-d UMAP map (HDBSCAN), and the map is not stable.** Only 20-33% of each image's 15 nearest neighbours survive a change of seed or settings. Cluster agreement between runs was ARI 0.01-0.40. The draft title of the stability figure ("neighbourhoods are kept") was false.
   - **Caught by:** the stability check the master prompt asked for.
   - **Fix:** clusters are now found in the full 230-d space (k-means on 30 principal components, 93.4% of variance). k is chosen by subsample stability alone (k = 10, ARI 0.90). Per-cluster bootstrap Jaccard is 0.75-0.92. These clusters stay together in every UMAP layout (62-69% of 2-d neighbours share the cluster), so the map is used for display only.
2. **A cluster description drafted from 10 thumbnails failed its data check.** C9 was described as "landbirds on shore, beach and rocky-coast scenes"; the shore prompts were only +0.28 sd above the rest. The description now says what the data supports: landbirds on water backgrounds (89% vs. 50%). The "drab species" part is marked "(by eye)".
3. **A cluster description described the members, not the errors.** C4 was described as "black-and-white birds: woodpeckers next to auks", but most of its members are real waterbirds (99% correct). Its errors are the 281 landbirds in it, 96.8% wrong: kingfishers, large woodpeckers, ravens. The description and its check were rewritten.
   - **Caught by (2, 3):** a rule the AI added after the first failure. Every description must state a testable claim, and an `assert` stops the notebook if any check fails. The first run with the rule stopped on C9.

## Results (executed notebook, section 5)
- 5 of 10 clusters are error clusters (error-rate CI above 29.0%, Jaccard ≥ 0.6). They hold 79.5% of all errors in 51.2% of the images:
  - **C9**, 59% wrong: landbirds on water backgrounds.
  - **C3**, 44% wrong: small birds; median mask 14.0% vs. 17.2%.
  - **C4**, 40% wrong: landbirds in the waterfowl region.
  - **C1**, 39% wrong: yellow/orange songbirds, mostly against water.
  - **C0**, 39% wrong: all-black birds.
- **k-NN AUC** (15 neighbours, full spaces):

  | property | CLIP outputs | DINOv2-small |
  |---|---|---|
  | error | 0.89 | 0.80 |
  | water background | 0.97 | 0.90 |
  | class | 0.96 | 1.00 |

  The class information is in the images; CLIP's outputs weight the background more.

## Revised after the critique (check-in 5)
- **Error clusters.** They are now defined by excess over the error expected from each image's class × background group, with a species-cluster CI.
  - 4 clusters remain: C3 +21, C4 +15, C9 +11 and C0 +10 percentage points.
  - C1 ("yellow songbirds") dropped out: it was below its expected error (39% vs. 49%).
  - For comparison, the group label alone concentrates errors with lift 1.89.
- **Cluster descriptions.** Every part of every description is now tested with one fixed rule (enrichment ≥ 1.5×, or a smaller median bird), including the named species lists. All parts passed; failures would be shown, not forced.
- **k-NN test.** Errors cluster in CLIP's outputs (0.89) mostly because the 230 logits encode CLIP's own prediction. With the score regressed out it drops to 0.77, below DINOv2 (0.80; within groups 0.71 vs. 0.76). New finding: error images look alike to an independent image encoder too.

## Our decision
- Check-in 4: we asked for no changes to the figure drafts. Check-in 5: "Fix high items 1-7".

## Effect on the analysis
Two of the five error clusters (C0 black birds, C4 kingfishers/woodpeckers/ravens) point to a cue that is neither background nor text: **bird appearance** that resembles seabirds or waterfowl.
