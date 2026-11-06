# 08 Interactive explorer

- **Date:** 2026-11-06
- **Goal:** one interactive view that links the overview, the species attribute and the experiment, in the notebook and as an offline HTML file.
- **Key prompt (verbatim, from `00_master_prompt.md`):**
  > Interactive explorer linking it all: projection overview + species panel + a per-bird strip of all conditions (thumbnails with margins). It must work in the notebook AND as a standalone offline HTML file in `Phase_1/AI Team/outputs/` [...]. Keep the file under about 20 MB. Before building it, propose 2 alternative designs and let us choose.

## What the AI proposed (check-in 4, shown as two wireframes)
- **A: linked views in Altair / Vega-Lite.**
  - Layout: overview map with rectangle brush, species dot plot (error vs. water rating), bird strip on click.
  - Pros: the same Python renders in the notebook and as offline HTML; easy for us to edit.
  - Cons: rectangle brush only, no text search, no per-bird curves.
- **B: custom single-file app (plain JS + canvas), recommended by the AI.**
  - Map: lasso, zoom and pan, with a switch between the CLIP-output map and the DINOv2 map.
  - Color modes: margin, class, rating, bird size, cluster.
  - Panels: selection summary, sortable species table with the AI's rating reason, species search, error-cluster list with the verified descriptions.
  - Bird card: 10 edited versions with margins and the bird's own dose-response curves.
  - Cost: about 600 lines of hand-written JS that we have to check.

## Our decision
**B** ("B: custom app"), chosen at check-in 4.

## What was built
- `aivis/explorer_data.py` builds compact records: 5,794 images with 44 px WebP thumbnails and both map coordinates, margins for all 1,200 experiment birds, and 10 condition thumbnails (56 px) for 150 birds per group.
- `aivis/explorer_app.py` holds the HTML/JS template. Data is inlined as JSON, with no CDN or external file. Output: `outputs/explorer.html`, 12.1 MB after the critique fixes (11.9 MB at first).
- In the notebook it is shown with `IFrame`. If a viewer blocks local iframes, the file opens directly in any browser.

## How it was verified
The file was served locally and tested in a browser (Claude's built-in browser):
- **Load:** no console errors.
- **Species row (Pied Kingfisher):** selects 30 images, 96.7% wrong, matching the notebook.
- **Click a point:** opens the bird card. For an experiment bird (Groove-billed Ani #89) it shows 10 thumbnails with margins and two curves.
- **Lasso:** selects 833 images with an updated summary.
- **Map switch:** CLIP → DINOv2 keeps the selection highlighted. "Color by rating" works.
- A test hook `window.__explorer` was added so these checks can be scripted.
- Not tested: touch devices; browsers other than Chromium.

## Effect on the analysis
The explorer is the place to check single cases behind the aggregate findings (e.g. a bird that is right alone but wrong on its own background). It is also the demo for the video.
