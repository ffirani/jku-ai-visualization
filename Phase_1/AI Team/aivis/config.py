"""Paths and constants shared by the notebook and the helper modules."""
from __future__ import annotations

import os
from pathlib import Path

# Folder of this package's parent = "Phase_1/AI Team"
TEAM_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = TEAM_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# Heavy, regenerable data lives OUTSIDE the repo (the repo sits in iCloud Drive).
CACHE_DIR = Path(os.environ.get("AIVIS_CACHE", Path.home() / "aivis_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "openai/clip-vit-base-patch32"
DATASET_ID = "grodino/waterbirds"
SPLIT = "test"

BASE_PROMPTS = ["a photo of a landbird.", "a photo of a waterbird."]

# Species that the original generate_waterbirds.py labels as waterbirds only
# because their lowercased name contains the substring "tern".
TERN_BUG_SPECIES = ["Eastern_Towhee", "Western_Meadowlark", "Western_Wood_Pewee"]

SEED = 0
N_BOOT = 2000
