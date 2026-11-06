# Reflection on GenAI use in Phase I (midpoint)

**AI-aided pair:** Mohamed Ali (k01635875), Rostislav Budarin (k12348049)
**GenAI used:** Claude (Opus 5.5) in Claude Code

## 1. How we worked
1. **Brainstorming.** We gave the model the course material and our registered project idea and brainstormed different directions for examining our research question with it. We decided on one idea: a controlled cue-conflict study. It asks which cue CLIP follows when the bird, the background and text written on the image disagree.
2. **Master prompt.** We then created a master prompt with the model that describes the whole Phase I: the analyses, the figures, and five check-ins where the AI stops and we decide.
3. **Execution.** A Claude Code session carried out the prompt and built the notebook, the figures and the interactive explorer. At the check-ins we reviewed its results and made the decisions: replacing two background images, choosing the explorer design, and deciding which points of the final critique to fix.
4. **Critique.** At the end we had the AI review its own analysis, fixed the main weaknesses it found, and updated our findings.

Every step is logged in `ai-interactions/phase1/`.



## 2. Failure patterns
- The AI sometimes made claims after only a shallow check, e.g. about the Python setup on our PC.
- Some draft text and figure titles were written before the numbers existed and had to be corrected.
- One planned method (making background images by inpainting) did not work and was replaced.
- Some first-draft statistics were too optimistic; the critique step corrected them.

## 3. Best practices
- Brainstorm first, then put the agreed plan into one master prompt.
- Build in check-ins where we decide, instead of letting the AI run unchecked.
- Every number in the text must come from executed code, with automatic checks for the claims.
- Look at the inputs (e.g. contact sheets of the edited images) before running an experiment.
- End with a critique pass where the AI reviews its own results.



