# Phase I, AI-aided pair (Mohamed Ali, Rostislav Budarin)

Cross-modal shortcut learning in zero-shot CLIP ViT-B/32 on the Waterbirds test split. When the bird, the background and overlaid text disagree, which cue drives CLIP's answer, how strongly, and why? Built with Claude (Opus 5.5) in Claude Code; the AI interaction record is in [`../../ai-interactions/phase1/`](../../ai-interactions/phase1/).

## Files
| file | what |
|---|---|
| `phase1_ai_pair.ipynb` | the analysis: baseline and label audit, species water association, prompt variants, cue-conflict experiment, output projection, explorer. Each part goes question → method → figure → finding → limitation |
| `aivis/` | helper package used by the notebook (CLIP scoring, statistics, image editing, experiment, explorer data) |
| `species_water_rating.csv` | GenAI-derived attribute: water association 0-3 + one-line reason for all 200 species, with the 4 raters' individual ratings |
| `species_water_handcheck.csv`, `handcheck_instructions.md` | blind human check of 40 species (to be filled in by us) |
| `outputs/` | all figures as PNG + SVG, and the interactive explorer as a standalone offline HTML file |
| `video_notes.md` | 2-minute script for our part of the progress video |

## Setup (Windows, NVIDIA GPU)
Python 3.12. Keep the virtual environment and caches **outside iCloud Drive**.

```bash
py -3.12 -m venv C:\Users\<you>\venvs\aivis
```
If `py -3.12` is not usable for your Windows user (as on Mohamed's PC), get a user-local Python with uv: `uv python install 3.12`, then create the venv with that interpreter's `-m venv`.

```bash
C:\Users\<you>\venvs\aivis\Scripts\python.exe -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126
C:\Users\<you>\venvs\aivis\Scripts\python.exe -m pip install -r requirements.txt
C:\Users\<you>\venvs\aivis\Scripts\python.exe -m ipykernel install --user --name aivis --display-name "Python 3.12 (aivis)"
```
Use cu126 wheels for NVIDIA drivers that support CUDA ≤ 12.7. Without a GPU everything still runs on CPU, only slower.

## Run
Open `phase1_ai_pair.ipynb` with the `aivis` kernel and run "Restart & Run All", or from this folder:
```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=7200 --ExecutePreprocessor.kernel_name=aivis phase1_ai_pair.ipynb
```
Heavy intermediate results are cached in `AIVIS_CACHE` (default `~/aivis_cache`, about 2 GB): CLIP logits, 224 px canvases, rembg masks, plate candidates, experiment scores, UMAP runs, DINOv2 vectors. Delete the folder to recompute everything.

**Runtime** (RTX 3070 Ti Laptop, 32 GB RAM, measured 2026-11-06):
- With the cache filled: about 3 min.
- From an empty cache: about 90 min. The parts:
  - rembg masks for all images on CPU: about 40 min, launched automatically as `python -m aivis.segment_all`
  - plate candidates (two segmentation models on 240 images): about 9 min
  - cue-conflict experiment (104,400 edited images): about 11 min
  - follow-up run after the critique (every bird on all 20 plates + same-base word grid, 256,800 images): about 22 min
  - DINOv2 vectors: about 3.5 min
  - UMAP runs: about 2 min
  - CLIP prompt-bank logits: about 1 min

Re-running from a cache without the UMAP/DINOv2 files reproduced them exactly (max difference 0).

## Outputs (`outputs/`, PNG + SVG)
| file | question it answers |
|---|---|
| `fig1_baseline_label_audit` | How accurate is CLIP per class × background group, and what does the label fix change? |
| `fig2a_error_vs_water_rating` | Do water-associated landbird species get misread more often? |
| `fig2b_error_decomposition` | How many errors are background shortcut vs. label definition vs. label bug? |
| `fig3_prompt_strategies`, `fig3b_fixed_broken` | Is the shortcut in the word "waterbird" or in the image? |
| `fig4a_cue_quadrant` | When bird and background disagree, which one wins? |
| `fig4b_dose_response` | How fast do a conflicting scene (shrinking bird) and a written word (growing text) flip CLIP? |
| `fig4c_background_vs_text_resistance` | Are scene and text vulnerability one weakness or two? |
| `fig4d_word_vs_scene` | How does a written word compare with a real scene, on the same base image? |
| `fig4e_scene_asymmetry` | Do water scenes pull harder than land scenes, or is CLIP's default shifted? |
| `fig4f_word_vs_scene_dose_matched` | Does a word beat a scene at every dose, counting only birds correct on the base? |
| `fig5_projection_clip_outputs`, `fig5b_projection_stability`, `fig5c_error_cluster_members`, `fig5d_dinov2_comparison` | Where are the errors in CLIP's output space, is that structure stable, and what sets the error clusters apart? |
| `fig4_qc_*` | quality control: masks (random / rejected), plates (used / rejected first attempt), example conditions |
| `explorer.html` | interactive explorer (offline, 12.1 MB): map with lasso, species table, error clusters, per-bird condition strip and curves |
