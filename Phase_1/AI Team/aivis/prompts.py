"""All text prompts, so that one pass over the images scores every prompt set."""
from __future__ import annotations

from .config import BASE_PROMPTS

# (name, landbird prompt, waterbird prompt)
PROMPT_PAIRS = [
    ("baseline", *BASE_PROMPTS),
    ("habitat words", "a photo of a land bird.", "a photo of a seabird or waterfowl."),
    ("example taxa", "a photo of a songbird, woodpecker, or other land bird.",
     "a photo of a gull, duck, pelican, or other water bird."),
    ("lives on", "a photo of a bird that lives on land.", "a photo of a bird that lives on water."),
]

# Readable names for the species prompts. Only typos and Latin genus names are changed.
SPECIES_ALIAS = {
    "Artic_Tern": "Arctic Tern",
    "Geococcyx": "Greater Roadrunner",
    "Sayornis": "Phoebe",
    "Chuck_will_Widow": "Chuck-will's-widow",
    "Whip_poor_Will": "Whip-poor-will",
    "Cardinal": "Northern Cardinal",
    "Mockingbird": "Northern Mockingbird",
    "Nighthawk": "Common Nighthawk",
    "Frigatebird": "Magnificent Frigatebird",
}


def species_display(name: str) -> str:
    return SPECIES_ALIAS.get(name, name.replace("_", " "))


def species_prompt(name: str) -> str:
    return f"a photo of a {species_display(name)}, a type of bird."


# Scene and context prompts for the projection (analysis 5). Places categories used
# by Waterbirds: bamboo forest and broadleaf forest (land), ocean and natural lake (water).
SCENE_PROMPTS = [
    "a photo of a bamboo forest.", "a photo of a broadleaf forest.", "a photo of a forest.",
    "a photo of grass.", "a photo of a field.", "a photo of a tree branch.", "a photo of leaves.",
    "a photo of a desert.", "a photo of rocks.", "a photo of snow.",
    "a photo of the ocean.", "a photo of a lake.", "a photo of a beach.", "a photo of a river.",
    "a photo of a marsh.", "a photo of waves.", "a photo of the sky.",
    "a close-up photo of a bird.", "a photo of a small bird far away.", "a photo of a bird in flight.",
    "a photo of a bird perched on a branch.", "a photo of a bird swimming.",
    "a photo of a bird standing on the ground.", "a photo of a bird on a feeder.",
    "a blurry photo of a bird.", "a dark photo of a bird.", "a black and white photo of a bird.",
    "a photo of a bird pasted onto a background.", "a photo of a person holding a bird.",
    "a photo of a bird's head.",
]


def prompt_bank(species_names: list[str]) -> list[str]:
    """Pairs (flattened, land then water), then 200 species prompts, then scene prompts."""
    bank = []
    for _, l, w in PROMPT_PAIRS:
        bank += [l, w]
    bank += [species_prompt(s) for s in species_names]
    bank += SCENE_PROMPTS
    return bank
