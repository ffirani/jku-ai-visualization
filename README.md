# CLIP on Waterbirds: background and text shortcuts

**Team:** Four horsemen of the apocalypse · AI and Visualization, JKU, WS 2026

| | |
|---|---|
| **Task** | Zero-shot binary classification: landbird vs. waterbird, with the prompts "a photo of a landbird" / "a photo of a waterbird" |
| **Model** | CLIP ViT-B/32, pretrained, frozen ([`openai/clip-vit-base-patch32`](https://huggingface.co/openai/clip-vit-base-patch32)) |
| **Dataset** | Waterbirds test split, 5,794 images ([`grodino/waterbirds`](https://huggingface.co/datasets/grodino/waterbirds)): CUB-200 birds pasted on land or water backgrounds (Places). Plus synthetic edits made from it: text overlays, bird/background swaps, birds on 20 real scenes |
| **Question (Phase I)** | Does CLIP follow the bird, the background, or text written on the image, and how strongly? |

## Pairs
| phase | AI-aided pair | human-only pair |
|---|---|---|
| I | Mohamed Ali (k01635875), Rostislav Budarin (k12348049) | Parimala Sabau (k52104490), Farshid Famil Irani (k12518385) |
| II | Parimala Sabau, Farshid Famil Irani | Mohamed Ali, Rostislav Budarin |

## Repository
| path | content |
|---|---|
| [`Phase_1/Manual Team/`](Phase_1/Manual%20Team/) | human-only pair: `Analysis.ipynb` (baseline, background bias, typographic attacks), `typographic_attack_results.csv`, `environment.yml` |
| [`Phase_1/AI Team/`](Phase_1/AI%20Team/) | AI-aided pair: `phase1_ai_pair.ipynb`, `aivis/` helper package, figures and interactive `outputs/explorer.html`; setup and run steps in its [readme](Phase_1/AI%20Team/readme.md) |
| [`Phase_1/Presentation/`](Phase_1/Presentation/) | progress-video slides and narration script (both pairs) |
| [`Phase_2/`](Phase_2/) | Phase II (pairs switched) |
| [`ai-interactions/`](ai-interactions/) | GenAI interaction record, one file per step (prompts, accepted / rejected suggestions, why) |
| [`ai_reflection_midpoint.md`](ai_reflection_midpoint.md) | reflection on GenAI use in Phase I |
| `team-info.json`, `workload.json` | team and workload |

## Phase I findings
**Human-only pair** (notebook sections 1-12)
- Overall accuracy 71.0%, but it depends on the background: landbirds about 88% right on land vs. 45% on water; waterbirds 79% on land vs. 99% on water.
- Typographic attack (200 images, 50 per group): accuracy 80% on the originals, 99% with the correct word, 10% with the misleading word; 70% of predictions flip.

**AI-aided pair** (notebook sections 1-5, explorer)
- Same background gap (landbirds 87.5% on land vs. 45.1% on water). The dataset script labels every species with "tern" in its name as a waterbird (e.g. Eastern Towhee); fixed.
- 62% of errors are background excess; the label definition adds only about 4% (kingfishers).
- The shortcut is in the image, not in the word "waterbird": every prompt rewording made it stronger.
- CLIP adds up bird and background evidence; the bird wins 65% of conflicts, but the default leans "waterbird".
- Text beats scenes at every dose: a word 4% tall flips 89-100% of correct birds, a whole conflicting scene 15-97%. The same weakly recognised birds fall for both cues.
- The explorer shows a third cue, appearance: black birds and kingfishers are read as waterbirds.

## Run
- **Human-only pair:** `conda env create -f "Phase_1/Manual Team/environment.yml"`, install PyTorch for your CUDA version (the run used 2.14.1, CUDA 13.0), then run `Analysis.ipynb`.
- **AI-aided pair:** see [`Phase_1/AI Team/readme.md`](Phase_1/AI%20Team/readme.md) (Python 3.12, `requirements.txt`, about 3 min with cache, 90 min from scratch). Open `outputs/explorer.html` in any browser, offline.

Both pairs download the model and dataset from Hugging Face on first run.
