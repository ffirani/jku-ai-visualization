export const meta = {
  name: 'phase1-critique',
  description: 'Five independent lens reviewers critique the Phase I analysis; a synthesizer dedups and ranks; two verifiers adversarially check each item against the notebook',
  phases: [
    { title: 'Review', detail: '5 lenses: statistics, confounds, course rules + reproducibility, visualization, GenAI attribute' },
    { title: 'Synthesize', detail: 'merge, dedup, rank by severity' },
    { title: 'Verify', detail: 'try to refute each item against the notebook text' },
  ],
}

const NB = args.notebook_dump
const FIG_DIR = args.fig_dir
const CONTEXT = `You are reviewing a university lab analysis (JKU "AI and Visualization", Phase I: black-box analysis of a model). Model: CLIP ViT-B/32 zero-shot on the Waterbirds test set (5,794 images), prompts "a photo of a landbird." / "a photo of a waterbird.". Question: when bird, background and overlaid text disagree, which cue drives CLIP's answer, how strongly, and why? Phase I rules: black box only (inputs and CLIP's output logits; no hidden states, attention, gradients, no plotting/projecting CLIP embeddings; other models may describe or edit the inputs). Patterns must be shown to be systematic (n, CIs) and explained by drill-down, not a performance report.

Read these files first (they are the full material, do not skip):
- ${NB}  (text dump of the executed notebook: every markdown cell, code cell and printed output; figures are omitted)
- the figure PNGs in ${FIG_DIR} (open the ones relevant to your lens with the Read tool; titles state the claimed finding)
Do not edit any file. Do not run code that changes files. You may run read-only Python if needed, but prefer reading.`

const ITEM = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    section: { type: 'string', description: 'notebook section or figure the item concerns' },
    kind: { type: 'string', enum: ['weakness', 'alternative explanation', 'missing check'] },
    claim_affected: { type: 'string', description: 'the specific claim in the notebook that is at risk, quoted or closely paraphrased' },
    argument: { type: 'string', description: 'why this is a problem, concretely' },
    suggested_check: { type: 'string', description: 'a concrete check or fix, black-box compatible' },
    effort: { type: 'string', enum: ['minutes', 'about an hour', 'half a day or more'] },
    severity: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['title', 'section', 'kind', 'claim_affected', 'argument', 'suggested_check', 'effort', 'severity'],
}
const LIST = { type: 'object', properties: { items: { type: 'array', items: ITEM } }, required: ['items'] }

const LENSES = [
  { key: 'statistics', text: 'Statistical validity: bootstrap design (are images independent? species clustering, paired vs. unpaired), multiple comparisons, selection effects in samples (clean masks, balanced groups, plate choice), whether CIs support each worded claim, effect sizes vs. significance, regression/additive-model interpretation, k-NN AUC and clustering choices.' },
  { key: 'confounds', text: 'Alternative explanations and confounds for each finding: artifacts of the edited images (hard paste edges, inpainting smudge, gray canvas, white text box, text position, crop/resize preprocessing), plate selection and only 10 plates per type, word length/font, prompt bank choice for the projection, label definitions, and anything else that could produce the same numbers without the claimed mechanism.' },
  { key: 'rules_repro', text: 'Course-rule compliance and reproducibility: does anything use CLIP internals beyond output logits (e.g. computing logits from features), is DINOv2 use allowed, are findings systematic and drilled down as the course demands, does the notebook run top to bottom from a cold cache, hard-coded values, numbers in text that are not computed, missing seeds, environment assumptions.' },
  { key: 'visualization', text: 'Visualization quality: does each figure answer one question with a title that states the finding and is supported, consistent colorblind-safe encoding across figures, readability at video size, clutter/overlap, misleading scales, missing n/uncertainty, legends, and whether a different chart would show the finding better.' },
  { key: 'genai_attribute', text: 'The GenAI-derived species water-association rating and its use: rubric validity, rater independence (same model family), consistency vs. correctness, the pending human check, circularity, the error-decomposition rule (priority order, threshold choice), and whether conclusions in sections 2 and 5 lean on the ratings more than their reliability allows.' },
]

phase('Review')
const reviews = await parallel(LENSES.map(l => () => agent(
  `${CONTEXT}\n\nYour lens: ${l.text}\n\nFind the most important weaknesses, alternative explanations and missing checks through this lens. Be specific and concrete (cite the section, the number, the claim). Do not list generic advice or things the notebook already handles (read its limitation paragraphs first). At most 8 items, ranked by severity.`,
  { label: `review: ${l.key}`, phase: 'Review', schema: LIST },
)))
const all = reviews.filter(Boolean).flatMap((r, i) => (r.items || []).map(it => ({ ...it, lens: LENSES[i].key })))
log(`${all.length} raw items from ${reviews.filter(Boolean).length} reviewers`)

phase('Synthesize')
const syn = await agent(
  `${CONTEXT}\n\nBelow are ${all.length} critique items from five independent reviewers with different lenses. Merge duplicates (keep the clearest wording and the most concrete check; list all lenses that raised it), drop items that are generic or already handled by the notebook's own limitation text, and rank the rest by severity and by how much the claimed finding depends on it. Return at most 14 items.\n\n${JSON.stringify(all, null, 1)}`,
  { label: 'synthesize', phase: 'Synthesize', schema: { type: 'object', properties: { items: { type: 'array', items: { ...ITEM, properties: { ...ITEM.properties, lenses: { type: 'array', items: { type: 'string' } } } } } }, required: ['items'] } },
)
const items = (syn && syn.items) || []

phase('Verify')
const half = Math.ceil(items.length / 2)
const VERDICT = {
  type: 'object',
  properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
    title: { type: 'string' }, verdict: { type: 'string', enum: ['valid', 'partly valid', 'refuted'] },
    evidence: { type: 'string', description: 'what in the notebook text or figures supports or refutes it' },
  }, required: ['title', 'verdict', 'evidence'] } } },
  required: ['verdicts'],
}
const verdicts = await parallel([items.slice(0, half), items.slice(half)].filter(b => b.length).map((batch, b) => () => agent(
  `${CONTEXT}\n\nYou are an adversarial verifier. For each critique item below, try to REFUTE it using the notebook text, its printed outputs and the figures: is the problem already handled, is the description factually wrong about what the notebook does, or is the claimed risk negligible given the numbers shown? Mark "refuted" only with concrete evidence; "partly valid" if the item is right in part; otherwise "valid". Return one verdict per item, same titles.\n\n${JSON.stringify(batch, null, 1)}`,
  { label: `verify batch ${b + 1}`, phase: 'Verify', schema: VERDICT },
)))
const vmap = {}
verdicts.filter(Boolean).forEach(v => (v.verdicts || []).forEach(x => { vmap[x.title] = x }))
return { raw_count: all.length, items: items.map(it => ({ ...it, verification: vmap[it.title] || null })) }
