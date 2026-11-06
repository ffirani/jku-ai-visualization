export const meta = {
  name: 'species-water-rating',
  description: 'Four independent AI raters score 200 CUB bird species for water association (0-3); no-consensus species adjudicated; a critic flags inconsistencies',
  phases: [
    { title: 'Rate', detail: '4 independent raters: default-model rubric, Sonnet rubric, Haiku rubric, default-model habitat-first' },
    { title: 'Fill gaps', detail: 're-ask a rater for any species it skipped' },
    { title: 'Adjudicate', detail: 'species without a 3-of-4 consensus' },
    { title: 'Critique', detail: 'consistency check across related species (flags only, not applied)' },
  ],
}

const SPECIES = args.species
const NOTES = args.notes || {}
const KNOWN = new Set(SPECIES)

const RUBRIC = `Rate how strongly each bird species is tied to water habitats (open water, shores, wetlands) on a 0-3 scale. Think about where the species typically feeds, nests and spends its time across its normal range, not about any single photo.

0 = no water tie. Typical habitat is forest, woodland, grassland, desert, scrub, mountains or towns; water plays no special role. (Example not in the list: Wild Turkey.)
1 = weak tie. Regularly seen near water or in damp habitats, or sometimes forages over water, but does not depend on it. (Example not in the list: American Robin.)
2 = strong tie. Mostly lives in wetlands, marshes, swamps, mangroves, riverbanks or shorelines, but feeds mainly on land, in vegetation or in the air rather than in the water. (Example not in the list: Swamp Sparrow.)
3 = aquatic. Gets its food from the water (swimming, diving, plunge-diving, wading for aquatic prey, or snatching food from the water surface) and/or spends most of its life on open water or at sea. (Examples not in the list: Common Loon, Great Blue Heron.)

Rate each species independently, based on its ecology only. The reason must be one short line (at most about 15 words) naming the habitat or behavior that decides the rating. Confidence is how sure you are of the rating (low / medium / high).`

const label = s => (NOTES[s] ? `${s} (${NOTES[s]})` : s)

const ITEM = {
  type: 'object',
  properties: {
    species: { type: 'string' },
    rating: { type: 'integer', minimum: 0, maximum: 3 },
    reason: { type: 'string' },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
  },
  required: ['species', 'rating', 'reason', 'confidence'],
}
const ITEM_H = {
  type: 'object',
  properties: {
    species: { type: 'string' },
    habitat: { type: 'string' },
    rating: { type: 'integer', minimum: 0, maximum: 3 },
    reason: { type: 'string' },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
  },
  required: ['species', 'habitat', 'rating', 'reason', 'confidence'],
}
const listSchema = (item, n) => ({
  type: 'object',
  properties: { ratings: { type: 'array', items: item, minItems: n, maxItems: n } },
  required: ['ratings'],
})

const RATERS = [
  { key: 'A', desc: 'default model, rubric', model: undefined, habitat: false },
  { key: 'B', desc: 'Sonnet, rubric', model: 'sonnet', habitat: false },
  { key: 'C', desc: 'Haiku, rubric', model: 'haiku', habitat: false },
  { key: 'D', desc: 'default model, habitat-first', model: undefined, habitat: true },
]

function raterPrompt(r, names) {
  const head = 'You are rating bird species for a research dataset. Answer from your own ornithological knowledge only: do not use any tools, do not search the web and do not read or write files.'
  const how = r.habitat
    ? 'For each species, FIRST write `habitat`: where it typically feeds and nests (at most about 20 words). THEN decide `rating` from that description using the rubric, and give a one-line `reason`.'
    : 'For each species give `rating`, a one-line `reason` and `confidence`.'
  return `${head}\n\n${RUBRIC}\n\n${how}\n\nSpecies identifiers use underscores for spaces; notes in parentheses clarify ambiguous names. Return exactly one entry per species, in the same order, with \`species\` copied exactly as the identifier before any parentheses.\n\n${names.map(label).join('\n')}`
}

function clean(list) {
  const out = {}
  for (const e of (list || [])) {
    if (e && KNOWN.has(e.species) && !(e.species in out)) out[e.species] = e
  }
  return out
}

phase('Rate')
const raterResults = await pipeline(
  RATERS,
  r => agent(raterPrompt(r, SPECIES), {
    label: `rater ${r.key} (${r.desc})`, phase: 'Rate', model: r.model,
    schema: listSchema(r.habitat ? ITEM_H : ITEM, SPECIES.length),
  }).then(res => clean(res && res.ratings)),
  async (got, r) => {
    const missing = SPECIES.filter(s => !(s in (got || {})))
    if (!missing.length) return got
    log(`rater ${r.key} skipped ${missing.length} species; re-asking`)
    const more = await agent(raterPrompt(r, missing), {
      label: `rater ${r.key} gap fill (${missing.length})`, phase: 'Fill gaps', model: r.model,
      schema: listSchema(r.habitat ? ITEM_H : ITEM, missing.length),
    })
    return Object.assign({}, got || {}, clean(more && more.ratings))
  },
)

const byRater = {}
RATERS.forEach((r, i) => { byRater[r.key] = raterResults[i] || {} })

// Consensus rule: final = the rating given by at least 3 of the 4 raters; otherwise adjudicate.
const consensus = {}
const disputed = []
for (const s of SPECIES) {
  const votes = RATERS.map(r => byRater[r.key][s]).filter(Boolean).map(e => e.rating)
  const counts = {}
  votes.forEach(v => { counts[v] = (counts[v] || 0) + 1 })
  let best = null, bestN = 0
  for (const k of Object.keys(counts)) if (counts[k] > bestN) { best = Number(k); bestN = counts[k] }
  if (bestN >= 3) consensus[s] = { rating: best, n_agree: bestN }
  else disputed.push(s)
}
log(`${SPECIES.length - disputed.length} species reached 3-of-4 consensus; ${disputed.length} go to adjudication`)

let adjudicated = {}
if (disputed.length) {
  phase('Adjudicate')
  const lines = disputed.map(s => {
    const parts = RATERS.map(r => {
      const e = byRater[r.key][s]
      return e ? `  ${r.key}: ${e.rating} (${e.confidence}) - ${e.reason}${e.habitat ? ' | habitat: ' + e.habitat : ''}` : `  ${r.key}: (missing)`
    })
    return `${label(s)}\n${parts.join('\n')}`
  }).join('\n\n')
  const res = await agent(
    `You are adjudicating disagreements between four independent raters who scored bird species for water association. Answer from your own ornithological knowledge only: do not use tools, search or files.\n\n${RUBRIC}\n\nFor each species below, read the four ratings and reasons, then give the final rating under the rubric and a one-line reason. Do not average: pick the rubric level that best fits the species' ecology.\n\n${lines}`,
    { label: `adjudicator (${disputed.length} species)`, phase: 'Adjudicate', schema: listSchema(ITEM, disputed.length) },
  )
  adjudicated = clean(res && res.ratings)
}

const final = SPECIES.map(s => {
  if (s in consensus) {
    const pick = RATERS.map(r => byRater[r.key][s]).find(e => e && e.rating === consensus[s].rating)
    return { species: s, rating: consensus[s].rating, reason: pick ? pick.reason : '', source: 'consensus', n_agree: consensus[s].n_agree }
  }
  const a = adjudicated[s]
  return { species: s, rating: a ? a.rating : null, reason: a ? a.reason : '', source: a ? 'adjudicated' : 'unresolved', n_agree: 0 }
})

phase('Critique')
const table = final.map(f => `${label(f.species)}: ${f.rating} - ${f.reason}`).join('\n')
const critique = await agent(
  `Below are final water-association ratings (0-3) for 200 bird species, using this rubric:\n\n${RUBRIC}\n\nCheck them for consistency: related species (same family or genus, or very similar ecology) rated differently without a good ecological reason, or ratings that clearly contradict the rubric. Be conservative: flag only clear cases. Answer from your own knowledge only: do not use tools, search or files. Return an empty list if nothing is clearly wrong.\n\n${table}`,
  {
    label: 'consistency critic', phase: 'Critique',
    schema: {
      type: 'object',
      properties: { flags: { type: 'array', items: { type: 'object', properties: {
        species: { type: 'string' }, current: { type: 'integer' }, suggested: { type: 'integer', minimum: 0, maximum: 3 }, why: { type: 'string' },
      }, required: ['species', 'current', 'suggested', 'why'] } } },
      required: ['flags'],
    },
  },
)

return {
  rubric: RUBRIC,
  raters: RATERS.map(r => ({ key: r.key, desc: r.desc, ratings: Object.values(byRater[r.key]) })),
  final,
  disputed,
  adjudicated: Object.values(adjudicated),
  flags: (critique && critique.flags) || [],
}
