# Video notes: AI-aided pair, about 2 minutes

Our part of the 5-minute progress video, about 300 words spoken. Numbers are copied from the executed notebook (final run of 2026-11-06, after the critique fixes). If we change the species ratings after the hand-check, re-check the section 2 numbers (marked †).

| time | show | say |
|---|---|---|
| 0:00-0:15 | `fig1_baseline_label_audit.png` | "We asked CLIP to tell landbirds from waterbirds. Landbirds on land backgrounds are right 87.5% of the time, on water backgrounds only 45.1%. And the dataset script has a bug: every species with 'tern' in its name became a waterbird, including Eastern Towhee and Western Meadowlark." |
| 0:15-0:30 | `fig2b_error_decomposition.png`, then `fig2a_error_vs_water_rating.png` | "An AI rated all 200 species for how tied they are to water. 62% of CLIP's errors are background excess. The label definition adds only about 4%†: just the kingfishers stand out, misread half the time even on land." |
| 0:30-0:45 | `fig3_prompt_strategies.png` | "Is it the word 'waterbird'? No. Every rewording made the background effect stronger. Asking for 200 species names helps only because it adds bird evidence." |
| 0:45-1:00 | `fig4_qc_conditions.png`, then `fig4a_cue_quadrant.png` | "So we took the images apart: bird on gray, background only, birds pasted on 20 real scenes, words written on the image. CLIP adds up bird and background evidence; the bird wins 65% of conflicts. But its default leans 'waterbird', so landbirds need more evidence." |
| 1:00-1:20 | `fig4f_word_vs_scene_dose_matched.png`, then `fig4d_word_vs_scene.png` | "Text beats scenes at every dose. A word only 4% tall flips 89 to 100% of correctly classified birds; a whole conflicting scene flips 16 to 97%. The word 'waterbird' moves CLIP 3.2 times as far as a real water scene." |
| 1:20-1:30 | `fig4c_background_vs_text_resistance.png` | "And it is the same weakly recognised birds that fall for both cues: one shared weakness." |
| 1:30-1:50 | `explorer.html`: click an error cluster, then one bird (e.g. Groove-billed Ani #89) | "Our explorer shows a third cue: appearance. Black birds and kingfishers are read as waterbirds. Here is one Groove-billed Ani: right on its own, wrong on its own water background." |
| 1:50-2:00 | `ai-interactions/phase1/09_critique.md` | "The AI wrote most of the code. An AI critique pass then found seven serious problems in our first draft, and two findings reversed. We fixed them all, and logged everything." |

## Notes for recording
- Rehearse the explorer clicks once: open `outputs/explorer.html` in a browser before recording (about 12 MB, loads in a few seconds).
- Show one figure at a time, full screen, so the titles are readable.
- TODO (us): agree with the human-only pair who speaks when, and keep the whole video under 5:00.
