# Four horsemen of the apocalypse: cross-modal shortcut learning in CLIP

> **DRAFT, to be reviewed by the whole group.** Written by the AI-aided pair (with Claude) from the agreed Phase I plan. The human-only pair has not reviewed it yet.

AI and Visualization lab (364.036 ff.), JKU Linz, WS 2026.

| | |
|---|---|
| Team | Rostislav Budarin (k12348049), Parimala Sabau (k52104490), Farshid Famil Irani (k12518385), Mohamed Ali (k01635875) |
| Phase I AI-aided pair | Mohamed Ali, Rostislav Budarin |
| Phase I human-only pair | Parimala Sabau, Farshid Famil Irani |

## Task
Zero-shot binary image classification: is the bird in the photo a **landbird** or a **waterbird**? We study *how* the model decides, in particular whether it relies on the bird or on shortcuts such as the background and text in the image.

## Model
[`openai/clip-vit-base-patch32`](https://huggingface.co/openai/clip-vit-base-patch32) (Hugging Face `transformers`), used zero-shot with the prompts "a photo of a landbird." and "a photo of a waterbird.". The prediction is the prompt with the higher image-text logit. The margin is m(x) = logit(true class) − logit(other class).

## Dataset
[`grodino/waterbirds`](https://huggingface.co/datasets/grodino/waterbirds), split `test`: 5,794 images with columns `image`, `label` (landbird / waterbird), `place` (land / water background) and `bird` (one of 200 CUB species). Waterbirds pastes CUB-200 birds onto Places backgrounds (bamboo/broadleaf forest vs. ocean/natural lake). In the test split the two backgrounds are balanced within each class, so landbirds on water and waterbirds on land are as common as the matching combinations.

**Known label issue.** The original generation script labels every species whose name contains "tern" as a waterbird. That catches the real terns, but also three landbirds: Eastern Towhee, Western Meadowlark, Western Wood Pewee. The AI-aided pair reports results with the original and with corrected labels.

## Shared direction (Phase I)
- **Main question:** cross-modal shortcut learning. When the bird, the background and overlaid text disagree, which cue drives CLIP's answer, how strongly, and why?
- **Data:** the full test split; edited copies of test images (background swaps, overlaid text) for controlled experiments.
- **Starting visualization:** per-group accuracy (class × background) and margin distributions.
- **Candidates for Phase II:** TODO (whole group). The AI-aided pair suggests:
  - In Phase I, the same weakly recognised birds fall for both scenes and words. Does the image encoder give these birds little attribution?
  - Why does CLIP's default lean "waterbird"? Plain gray, small birds and random letter strings all push towards water.
  - Why do species names carry more bird evidence than the word "waterbird"?
  - Which features make black birds and kingfishers look like waterbirds?

## Repository layout
- `Phase_1/Manual Team/`: human-only pair (no generative AI).
- `Phase_1/AI Team/`: AI-aided pair. Notebook `phase1_ai_pair.ipynb`, helper package `aivis/`, figures and the interactive explorer in `outputs/`, see its `readme.md`.
- `ai-interactions/phase1/`: record of the AI-aided pair's interactions with generative AI.
- `ai_reflection_midpoint.md`: reflection on GenAI use in Phase I.
- `team-info.json`, `workload.json`: team metadata.
