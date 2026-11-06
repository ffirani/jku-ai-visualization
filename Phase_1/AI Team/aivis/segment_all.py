"""Segment every test image with rembg (U^2-Net, CPU) and cache 224 px masks.

Run once (about 30-60 min on CPU); the notebook reads the cache:
    python -m aivis.segment_all
Resumable: finished chunks are kept.
"""
from __future__ import annotations

import sys
import time

import numpy as np

from .config import CACHE_DIR
from .cue import segment, square_mask
from .data import load_split

CHUNK = 250


def main():
    ds = load_split()
    n = len(ds)
    out_dir = CACHE_DIR / "masks"
    out_dir.mkdir(exist_ok=True)
    t0 = time.time()
    for start in range(0, n, CHUNK):
        f = out_dir / f"mask224_{start:05d}.npy"
        if f.exists():
            continue
        stop = min(n, start + CHUNK)
        chunk = np.zeros((stop - start, 224, 224), np.uint8)
        for j, i in enumerate(range(start, stop)):
            m = segment(ds[i]["image"])
            chunk[j] = np.clip(square_mask(m) * 255, 0, 255).round().astype(np.uint8)
        np.save(f, chunk)
        el = time.time() - t0
        print(f"{stop}/{n} done, {el/60:.1f} min elapsed", flush=True)
    masks = np.concatenate([np.load(out_dir / f"mask224_{s:05d}.npy") for s in range(0, n, CHUNK)])
    np.save(CACHE_DIR / f"mask224_{n}.npy", masks)
    print("saved", CACHE_DIR / f"mask224_{n}.npy", masks.shape, flush=True)


if __name__ == "__main__":
    sys.exit(main())
