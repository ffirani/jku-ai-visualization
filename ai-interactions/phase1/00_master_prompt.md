# Master prompt for Phase I (AI-aided pair)

Written by Claude (Opus 5.5) at our request, in the scoping chat on 2026-11-06, and updated for our hardware.
Paste everything below the line into a new Claude Code session.

---

You are working with the AI-aided pair of a university team on Phase I of the "AI and Visualization" lab (JKU Linz, WS 2026). Deadline: Wed 11.11.2026, 23:59. Work until everything under "Definition of done" is finished.

## Where things are
- Team repo: `C:\Users\medo\iCloudDrive\Downloads\Informatik\3m\vis\code_team_proj\jku-ai-visualization`
- Course PDFs: `C:\Users\medo\iCloudDrive\Downloads\Informatik\3m\vis\` (folders `Lab`, `VL`, and the Moodle PDF `Kurs_ ... JKU Moodle.pdf`). Read the Moodle PDF and the Lab 02/03 slides first for the rules.
- AI-aided pair (us): Mohamed Ali (k01635875), Rostislav Budarin (k12348049).
- Human-only pair: Parimala Sabau and Farshid Famil Irani. Their work is in `Phase_1/Manual Team/`. **Never edit anything there and don't copy their code.** They must stay AI-free and the two pipelines must stay independent. Read their notebook only for the comparison in the reflection.

## Hardware and setup
- NVIDIA RTX 3070 Ti Laptop GPU (8 GB VRAM, driver 566.36, supports CUDA up to 12.7), 32 GB RAM. Use the GPU for CLIP and pick batch sizes that stay under 8 GB VRAM.
- Python 3.12 is installed through the `py` launcher. Plain `python` is only the Microsoft Store alias, and there is no conda.
- The repo is inside iCloud Drive, so put the virtual environment, the Hugging Face cache and large intermediate images **outside** iCloud Drive, otherwise gigabytes get uploaded. For example: venv in `C:\Users\medo\venvs\aivis` (`py -3.12 -m venv`), and the Hugging Face cache in its default `~/.cache/huggingface`.
- Install PyTorch with CUDA 12.6 wheels (`--index-url https://download.pytorch.org/whl/cu126`; not cu128, the driver is too old). Check `torch.cuda.is_available()` and register the venv as a Jupyter kernel.
- rembg can run on CPU; don't spend time on onnxruntime-gpu.

## The project (agreed by the whole group)
- Model: `openai/clip-vit-base-patch32` (Hugging Face transformers), zero-shot, prompts "a photo of a landbird." / "a photo of a waterbird.".
- Data: Hugging Face `grodino/waterbirds`, split `test` (5,794 images; columns image, label, place, bird).
- Question: cross-modal shortcut learning. When the bird, the background and overlaid text disagree, which cue drives CLIP's answer, how strongly, and why?
- Margin m(x) = logit(true class) − logit(other class).
- **Label bug, apply before any analysis:** Eastern_Towhee, Western_Meadowlark and Western_Wood_Pewee are landbirds but labeled waterbird. The original `generate_waterbirds.py` (group_DRO repo) labels any species whose lowercased name contains "tern" as a waterbird. Set their label to 0, keep the old label in `label_original`, and report results before and after the fix.
- Reproduction check: before the fix, overall accuracy should be about 70.6%. Per group: 87.6% (landbird/land), 45.1% (landbird/water), 74.9% (waterbird/land), 96.0% (waterbird/water).

## Phase I rules (from the course)
- Black box only. Use only the inputs and CLIP's output scores (logits / image-text similarities for any image and prompt). Do not use hidden states, attention or gradients, and do not plot or project CLIP's embedding vectors; that is Phase II. Other models may be used to describe or edit the *inputs* (segmentation, a separate encoder).
- Not a performance report. Show that every pattern is systematic (n, bootstrap 95% CIs), then explain it by drilling down: what distinguishes these cases, and are there sub-groups?
- The AI-aided pair is expected to go broader and build richer interaction than the human-only pair.

## Analyses to build
1. **Baseline + label audit** (full test set): your own implementation, with per-group results before and after the fix.
2. **Species water association (GenAI-derived attribute):** rate each of the 200 species for how tied it is to water habitats (0-3 plus a one-line reason) and save to `species_water_rating.csv`. We will hand-check at least 30 against a field guide or Wikipedia; report the agreement.
   - Chart error rate vs. rating per species (color = label, flag the 3 bug species, annotate kingfishers etc.).
   - Split each group's errors into: label bug / definition disagreement (water-associated species labeled landbird) / remaining background shortcut. State the rule you used.
3. **Is the shortcut in the image or in the word?** Same images, different text:
   - the baseline prompts
   - 2-3 descriptive prompt pairs (e.g. "seabird or waterfowl" vs. "land bird")
   - species routing: zero-shot over the 200 species names, then map species to land/water using the corrected labels

   Compare per-group accuracy and the background gap with CIs, and show which images each strategy fixes or breaks.
4. **Controlled cue-conflict experiment** (sample about 600 test images, 150 per class × background group, stratified by species, clean masks only; scale up if it runs fast):
   - Cut the bird out with a segmentation model (e.g. `rembg`). Check masks by area and with a contact sheet.
   - Background plates: about 10 land and 10 water scenes, e.g. from Waterbirds images with small birds, with the bird removed by OpenCV inpainting. Check them visually and document the choice.
   - Conditions:
     - bird only, on neutral gray
     - background only, with the bird region filled
     - bird pasted on matching vs. conflicting plates at about 8 scales (1.0 down to 0.15)
     - text overlays "landbird" / "waterbird" / a neutral word at about 8 sizes
     - extra words at 1-2 sizes: ocean, lake, beach, forest, tree, grass, duck, seagull, sparrow, a nonsense string, "watrbird"
   - Figures:
     - (a) cue quadrant scatter: bird-only margin vs. background-only margin, colored by whether the original prediction was correct
     - (b) dose-response curves for bird scale and for text size, with faint per-bird lines and a bold mean per group (ICE style)
     - (c) per-bird "background resistance" vs. "text resistance" scatter with marginal distributions and Spearman ρ with CI: one shared weakness, or two separate shortcuts?
     - (d) word vs. real scene: Δmargin per cue on one axis, with CIs
5. **Overview projection** (it's in our registration): UMAP of each image's vector of CLIP similarity scores over a prompt bank (200 species prompts plus about 30 scene/context prompts). Use outputs only, not embeddings.
   - Color = margin, shape = group. Check stability across seeds and parameters.
   - Drill into the error clusters and describe what sets them apart. You may draft cluster descriptions, but verify them against the data.
   - If time allows, compare with a UMAP of a separate image encoder (e.g. DINOv2-small) to show what the images themselves have in common.
6. **Interactive explorer** linking it all: projection overview + species panel + a per-bird strip of all conditions (thumbnails with margins).
   - It must work in the notebook AND as a standalone offline HTML file in `Phase_1/AI Team/outputs/` (e.g. Altair/Vega-Lite linked selections or Plotly, with small base64 thumbnails). Keep the file under about 20 MB.
   - Before building it, propose 2 alternative designs and let us choose.

## Visual quality bar
- Each figure answers one question, and its title states the finding, not the topic.
- Use one consistent, colorblind-safe encoding across all figures (class, background, cue type).
- Show n and uncertainty, and annotate the key points.
- No 3D, no rainbow scales. Readable at video size.
- Export PNG + SVG (+ HTML for interactive figures) to `outputs/`.

## Files to produce
- `Phase_1/AI Team/phase1_ai_pair.ipynb`: for each analysis, the story goes question → method → figure → finding → limitation. End with a findings summary and what Phase II should investigate. It must run top to bottom after "Restart & Run All". Cache heavy results outside iCloud Drive (see setup).
- `Phase_1/AI Team/requirements.txt` (with the PyTorch install line in the readme) and `Phase_1/AI Team/readme.md` (how to run, runtime, outputs).
- `Phase_1/AI Team/video_notes.md`: a 2-minute script for our part of the 5-minute video, saying which figure to show when.
- `ai-interactions/phase1/` at the repo root. Log as you go, one markdown file per step: date, goal, key prompt (verbatim), what the AI proposed, our decision (accepted / modified / rejected, and why), effect on the analysis, how it was verified.
  - This prompt is already saved there as `00_master_prompt.md`.
  - Entry `00_scoping.md`: in an earlier chat the AI read the course PDFs and proposed this plan. It also found the "tern" label bug in the human-only pair's species table and verified it in `generate_waterbirds.py`. It also wrongly said this PC had no Python, because it only checked the `python` command; the `py` launcher had Python 3.12.
  - Also log every AI mistake and how it was caught.
- `ai_reflection_midpoint.md` at the repo root. Start with our names and IDs. Sections: process, failure patterns, best practices, comparison with the human-only pair (insights found or missed, visualization choices, breadth/depth, speed vs. verification effort, confidence and evidence). Fill in facts and evidence only, and leave clearly marked TODOs for our own opinions. Never invent them.
- Root `README.md`: draft the task, model, dataset and shared direction, marked "to be reviewed by the whole group".
- Update `.gitignore` for anything generated inside the repo that shouldn't be pushed.

## Check-ins (stop, ask us briefly, then continue)
1. Environment ready (GPU working) and baseline reproduced.
2. Contact sheet of masks and background plates.
3. Species ratings ready for our hand-check.
4. Drafts of all main figures + the 2 explorer designs.
5. Critique pass: you list weaknesses, alternative explanations and missing checks; we decide what to act on.

Between check-ins, decide small things yourself, log them, and keep going.

## Working rules
- Never make up numbers: every number in the text must come from an executed cell.
- If a tool fails (e.g. rembg), pick an alternative and log why.
- Don't commit or push; we review first.

## Definition of done
- The notebook runs cleanly top to bottom.
- All figures and the explorer HTML are in `outputs/` and open offline.
- The log, reflection draft, README draft and video notes exist.

Finish with a summary of findings (with numbers) and a list of what we still have to do ourselves:
- hand-check the ratings
- write our opinions in the reflection
- agree on the README with the other pair
- record the video
- commit and push
- submit on Moodle by 11.11.2026 23:59
