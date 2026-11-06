# 00 Scoping chat: plan, label bug, master prompt

- **Date:** 2026-11-06
- **Who:** Mohamed Ali with Claude (Opus 5.5) in Claude Code (desktop app)
- **Goal:** read the course material and the team repo, agree on a Phase I plan for the AI-aided pair, and write a reusable master prompt for the work sessions.

## Key prompts (verbatim)
Opening prompt:
> we are the teams the will do ai phase 1 ,all pdf are relevant to explaining what we mean , could you figuer exactly what we should do

After the first plan, we pasted our registered project description and asked:
> this also an option ,what do you think best way to go

Asking for ambition:
> dont not ran out of a good idea even if it ambitious ,if and only if is good

Asking for the master prompt:
> could you give me a promt that make you do the whole thing , , i want the final vis to be impressive as asked for and want the prompt to do every thing untell this ass is done in a notebook,

The resulting master prompt is saved verbatim in [`00_master_prompt.md`](00_master_prompt.md).

## How the brainstorming went
1. **First plan from the AI.** It read the course PDFs, our repo and the human-only pair's notebook, summarised the Phase I rules, listed what the human-only pair had already done, and proposed:
   - an explorer with a UMAP of DINOv2 image features
   - GenAI-derived image attributes (bird size, background type), checked by hand-labelling about 50 images
   - a bird-only vs. background-only counterfactual
2. **Our registered direction.** We showed it our registered project description and asked which way was best. It advised keeping our framing but pointed out three problems:
   - Waterbirds contains no swapped images; every photo is a different bird.
   - A UMAP of CLIP's own embeddings belongs to Phase II.
   - CLIP has no cross-modal attention.

   It added that if AI had helped write the registration text, these errors would be an example of an AI failure pattern for the reflection.

   It merged our topics into one question: when the bird, the background and the text disagree, which one decides? It described this as combining our description with its first plan.
3. **Asking for ambition.** It listed five ideas, best first:
   1. label error vs. label definition vs. background shortcut
   2. is the shortcut in the image or in the word "waterbird"
   3. tipping points for background and text
   4. a written word vs. a real scene
   5. an explorer that ties it all together

   It named the ideas it dropped and why. LIME, occlusion, Grad-CAM and a UMAP of CLIP's embeddings belong to Phase II. Other CLIP models would make the work wider rather than deeper. CLIP's training data was never released.
4. **Rules check.** We asked whether our plan differs from the human-only pair's and whether that is allowed. It compared both approaches (same question, model and data; different methods and depth) and pointed to the Moodle rules: the AI-aided pair should broaden the analysis, the pipelines should stay different, and the common direction must be agreed with the whole group.
5. **Master prompt.** At our request it wrote the master prompt, with five built-in check-ins. After we gave our hardware (RTX 3070 Ti, 8 GB, 32 GB RAM) it updated the prompt for the GPU, a larger sample, a DINOv2 comparison and caches outside iCloud Drive.

## What the AI proposed (summary)
- The Phase I plan written down in `00_master_prompt.md`:
  - label audit
  - a GenAI-derived "species water association" attribute
  - prompt variants (image vs. word)
  - a controlled cue-conflict experiment (bird / background / overlaid text)
  - a projection of CLIP output scores
  - a linked interactive explorer
- **Found a label bug.** Three landbird species (Eastern_Towhee, Western_Meadowlark, Western_Wood_Pewee) show up as waterbirds in the human-only pair's per-species error table. In the "ideas" reply the AI named the likely cause: the original `generate_waterbirds.py` (group_DRO repo) labels every species whose lowercased name contains the substring `"tern"` as a waterbird, so "eas**tern**" and "wes**tern**" match as well as real terns. When we later asked whether the Hugging Face copy already had the bug, it said it had checked this rule in the script. At our request it drafted a message for our teammates, telling them to make the fix themselves so their pair stays AI-free.

## Our decision
- **Accepted** the plan as the AI-aided pair's direction (the shared group direction is still to be confirmed with the human-only pair).
- **Accepted** the label fix: set the three species to label 0, keep the old label in `label_original`, report results before and after the fix.
- **Modified** the master prompt after we gave our hardware details (GPU, RAM).

## Effect on the analysis
- Every per-group result is reported twice (original vs. corrected labels). The corrected labels are the default from analysis 2 on.
- The bug is a finding in itself for the comparison with the human-only pair: it was visible in their table but not flagged there.

## How it was verified
- The AI read the "tern" rule in the `generate_waterbirds.py` source.
- Re-checked in the work session (see [`02_baseline_label_audit.md`](02_baseline_label_audit.md)): in `grodino/waterbirds` the names containing "tern" are the 7 real terns, Western_Grebe and Western_Gull (waterbirds anyway), and exactly the three affected landbirds.

## AI mistakes in this step and how they were caught
1. **"This PC has no Python."** The AI only checked the `python` command (which is just the Microsoft Store alias) and missed the `py` launcher. It corrected this itself in the reply after we gave our hardware details.
2. **"Python 3.12 is installed through the `py` launcher" (written into the master prompt after the correction).** Only half right. `py -0p` lists a 3.12, but it is registered from another Windows user's profile (`C:\Users\abdo\...`) and running it fails with "Access is denied" for our user. Caught by the work session on its first `py -3.12` call; see [`01_environment.md`](01_environment.md).
