"""Waterbirds test split as a DataFrame, plus the label fix and cached 224 px canvases."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CACHE_DIR, DATASET_ID, SPLIT, TERN_BUG_SPECIES

CLASS_NAMES = ["landbird", "waterbird"]
PLACE_NAMES = ["land", "water"]


def load_split(split: str = SPLIT):
    from datasets import load_dataset
    return load_dataset(DATASET_ID, split=split)


def metadata(ds) -> pd.DataFrame:
    """One row per image: idx, species, place, original label, corrected label, group names."""
    species_names = ds.features["bird"].names
    df = pd.DataFrame({
        "idx": np.arange(len(ds)),
        "label_original": np.asarray(ds["label"], dtype=int),
        "place": np.asarray(ds["place"], dtype=int),
        "species_id": np.asarray(ds["bird"], dtype=int),
    })
    df["species"] = [species_names[i] for i in df["species_id"]]
    df["tern_bug"] = df["species"].isin(TERN_BUG_SPECIES)
    # Label fix: the three "tern"-substring landbirds go back to landbird (0).
    df["label"] = np.where(df["tern_bug"], 0, df["label_original"])
    df["place_name"] = [PLACE_NAMES[p] for p in df["place"]]
    for col, lab in [("group", "label"), ("group_original", "label_original")]:
        df[col] = [f"{CLASS_NAMES[l]} / {PLACE_NAMES[p]}" for l, p in zip(df[lab], df["place"])]
    df["class_name"] = [CLASS_NAMES[l] for l in df["label"]]
    return df


def tern_substring_table(species_names) -> pd.DataFrame:
    """Every species whose lowercased name contains 'tern' (the original labeling rule)."""
    hits = [s for s in species_names if "tern" in s.lower()]
    return pd.DataFrame({"species": hits,
                         "is_real_tern": [s.lower().endswith("_tern") for s in hits]})


def canvases(ds, size: int = 224) -> np.ndarray:
    """All images center-cropped and resized to size x size, cached as a uint8 .npy memmap."""
    from .cue import square_canvas
    path = CACHE_DIR / f"canvas{size}_{len(ds)}.npy"
    if path.exists():
        return np.load(path, mmap_mode="r")
    arr = np.lib.format.open_memmap(path, mode="w+", dtype=np.uint8, shape=(len(ds), size, size, 3))
    for i in range(len(ds)):
        arr[i] = np.asarray(square_canvas(ds[i]["image"], size))
    arr.flush()
    del arr
    return np.load(path, mmap_mode="r")
