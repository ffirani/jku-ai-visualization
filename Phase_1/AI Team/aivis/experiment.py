"""Controlled cue-conflict experiment: build edited inputs, score them with CLIP, cache the scores.

Conditions per bird (all on 224 x 224 canvases, see cue.py):
- original                      the unedited canvas (reference)
- bird_only                     bird kept in place, rest neutral gray
- bg_only                       bird removed by inpainting (dilated mask, OpenCV Telea)
- paste_{gray,match,conflict}   bird cut out and pasted centered at 8 scales on gray /
                                a plate of its own habitat / a plate of the other habitat
- text                          'landbird' / 'waterbird' / neutral word on the original, 8 sizes
- word                          11 extra words (+ the 3 above) on the original, 2 sizes
- gword                         all 14 words at one size on the bird pasted at scale 0.5 on gray,
                                so words and real scenes can be compared on the same base image
Only CLIP's output logits for the baseline prompts are stored.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from PIL import Image

from . import cue
from .config import CACHE_DIR, SEED

SCALES = [1.0, 0.8, 0.65, 0.5, 0.4, 0.3, 0.2, 0.15]
TEXT_SIZES = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12]   # cap height / canvas height
NEUTRAL_WORD = "triangle"
NONSENSE_WORD = "xkqzvrtb"
EXTRA_WORDS = ["ocean", "lake", "beach", "forest", "tree", "grass", "duck", "seagull", "sparrow",
               NONSENSE_WORD, "watrbird"]
EXTRA_SIZES = [0.06, 0.12]
GWORD_SCALE, GWORD_SIZE = 0.5, 0.08
ALL_WORDS = ["landbird", "waterbird", NEUTRAL_WORD] + EXTRA_WORDS
THUMB = 64
THUMB_CONDS = [("original", None), ("bird_only", None), ("bg_only", None),
               ("paste_gray", 0.5), ("paste_match", 0.5), ("paste_conflict", 1.0), ("paste_conflict", 0.5),
               ("paste_conflict", 0.2), ("text_misleading", 0.08), ("text_neutral", 0.08)]


def mask_table(masks: np.ndarray) -> pd.DataFrame:
    rows = [cue.mask_stats(m.astype(np.float32) / 255.0) for m in masks]
    t = pd.DataFrame(rows)
    t["clean"] = [cue.is_clean(r) for r in rows]
    return t


def largest_free_square(occupied: np.ndarray):
    """Largest axis-aligned square that avoids every occupied pixel and stays inside the image.

    Uses the chessboard distance transform: a square of side 2d-1 centered at a pixel fits
    exactly when that pixel's chessboard distance to the nearest occupied/border pixel is d.
    Returns (x0, y0, side).
    """
    from scipy.ndimage import distance_transform_cdt
    free = np.pad(~occupied, 1, constant_values=False)
    d = distance_transform_cdt(free, metric="chessboard")[1:-1, 1:-1]
    y, x = np.unravel_index(np.argmax(d), d.shape)
    k = int(d[y, x])
    return int(x - k + 1), int(y - k + 1), int(2 * k - 1)


def plate_candidates(ds, meta: pd.DataFrame, mt: pd.DataFrame, n_cand: int = 120, seed: int = SEED) -> pd.DataFrame:
    """For random clean-mask images per background type: bird-free square crop of the full-resolution image.

    The bird region is the union of two independent segmentations (U^2-Net and IS-Net) at full
    resolution, dilated by 3% of the shorter side, so a partial mask from one model does not leave
    bird pixels in the crop. Selection never looks at CLIP outputs. Cached.
    """
    import cv2
    p = CACHE_DIR / f"plate_candidates_{n_cand}_{seed}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    rng = np.random.default_rng(seed)
    rows = []
    for place in (0, 1):
        pool = meta.index[mt.clean.to_numpy() & (meta.place == place).to_numpy()].to_numpy()
        for i in sorted(rng.choice(pool, n_cand, replace=False)):
            img = ds[int(i)]["image"].convert("RGB")
            m = np.maximum(cue.segment(img, "u2net"), cue.segment(img, "isnet-general-use")) > 0.3
            k = max(3, int(0.03 * min(img.size)))
            m = cv2.dilate(m.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
            x0, y0, side = largest_free_square(m)
            rows.append(dict(idx=int(i), place=place, W=img.size[0], H=img.size[1], x0=x0, y0=y0, side=side,
                             rel_side=side / min(img.size), bird_area_full=float(m.mean())))
    out = pd.DataFrame(rows)
    out.to_parquet(p)
    return out


def crop_plate(ds, row) -> Image.Image:
    img = ds[int(row.idx)]["image"].convert("RGB")
    return img.crop((row.x0, row.y0, row.x0 + row.side, row.y0 + row.side)).resize((cue.CANVAS, cue.CANVAS), Image.BICUBIC)


def select_sample(meta: pd.DataFrame, mt: pd.DataFrame, per_group: int, exclude=(), seed: int = SEED) -> np.ndarray:
    """Clean masks only; within each class x background group, round-robin over species (max spread)."""
    rng = np.random.default_rng(seed)
    pool = meta[mt.clean.to_numpy() & ~meta.index.isin(list(exclude))]
    picked = []
    for g, d in pool.groupby("group"):
        by_sp = {s: list(rng.permutation(v.index.to_numpy())) for s, v in d.groupby("species")}
        order = list(rng.permutation(sorted(by_sp)))
        take = []
        while len(take) < per_group and any(by_sp.values()):
            for s in order:
                if by_sp[s] and len(take) < per_group:
                    take.append(by_sp[s].pop())
        picked += take
    return np.array(sorted(picked))


def conditions(i: int, meta_row, canvas: np.ndarray, mask: np.ndarray, plates: dict, rng):
    """Yield (record, PIL image) for every condition of one bird."""
    img = Image.fromarray(np.asarray(canvas))
    m = mask.astype(np.float32) / 255.0
    m = cue.keep_largest(m)
    label, place = int(meta_row.label), int(meta_row.place)
    base = dict(idx=i)
    yield {**base, "cond": "original"}, img
    yield {**base, "cond": "bird_only"}, cue.bird_on_gray(img, m)
    yield {**base, "cond": "bg_only"}, cue.inpaint(img, m)
    bird = cue.cutout(img, m)
    gray = Image.new("RGB", (cue.CANVAS, cue.CANVAS), cue.GRAY)
    own, other = label, 1 - label            # matching plate = habitat of the bird's class
    p_match = int(rng.integers(len(plates[own])))
    p_conf = int(rng.integers(len(plates[other])))
    for s in SCALES:
        yield {**base, "cond": "paste_gray", "scale": s}, cue.paste(gray, bird, s)
        yield {**base, "cond": "paste_match", "scale": s, "plate": f"{own}-{p_match}"}, cue.paste(plates[own][p_match], bird, s)
        yield {**base, "cond": "paste_conflict", "scale": s, "plate": f"{other}-{p_conf}"}, cue.paste(plates[other][p_conf], bird, s)
    band = cue.free_band(m)
    for w in ["landbird", "waterbird", NEUTRAL_WORD]:
        for sz in TEXT_SIZES:
            yield {**base, "cond": "text", "word": w, "size": sz}, cue.overlay_text(img, w, sz, band)
    for w in EXTRA_WORDS:
        for sz in EXTRA_SIZES:
            yield {**base, "cond": "word", "word": w, "size": sz}, cue.overlay_text(img, w, sz, band)
    gbase = cue.paste(gray, bird, GWORD_SCALE)
    for w in ALL_WORDS:
        yield {**base, "cond": "gword", "word": w, "size": GWORD_SIZE}, cue.overlay_text(gbase, w, GWORD_SIZE, "bottom")


V2_WORD_SCALES = [1.0, 0.5, 0.15]
V2_SIZES = [0.04, 0.08, 0.12]
V2_WORDS = [("waterbird", "black"), ("landbird", "black"), ("triangle", "black"), ("triangle", "white"),
            ("qorvtenl", "black"), ("zbxkwtpm", "black")]   # white "triangle" = blank box; two random strings


def conditions_v2(i: int, canvas: np.ndarray, mask: np.ndarray, plates: dict):
    """Follow-up after the critique (check-in 5).

    - every bird on ALL plates of both types at all 8 scales (plate becomes a crossed factor)
    - same-base word grid: bird pasted on gray at 3 scales x 3 text sizes x 6 words/controls
    """
    img = Image.fromarray(np.asarray(canvas))
    m = cue.keep_largest(mask.astype(np.float32) / 255.0)
    bird = cue.cutout(img, m)
    gray = Image.new("RGB", (cue.CANVAS, cue.CANVAS), cue.GRAY)
    for place in (0, 1):
        for k, plate in enumerate(plates[place]):
            for s in SCALES:
                yield dict(idx=i, cond="plate", plate_place=place, plate_k=k, scale=s), cue.paste(plate, bird, s)
    for s in V2_WORD_SCALES:
        base = cue.paste(gray, bird, s)
        for w, col in V2_WORDS:
            for sz in V2_SIZES:
                yield (dict(idx=i, cond="gword2", word=(w if col == "black" else "[blank box]"), size=sz, scale=s),
                       cue.overlay_text(base, w, sz, "bottom", fill=col))


def run_v2(sample: np.ndarray, canvases, masks, plates, plate_idx: dict, scorer, prompts, name: str, batch: int = 512):
    """Score the follow-up conditions. Cached; the cache records the sample and the plate images it was built from."""
    import json
    out_p = CACHE_DIR / f"cue2_{name}.parquet"
    meta_p = CACHE_DIR / f"cue2_{name}.json"
    key = dict(sample=[int(i) for i in sample], plates={str(k): [int(i) for i in v] for k, v in plate_idx.items()},
               prompts=list(prompts))
    if out_p.exists() and meta_p.exists():
        assert json.loads(meta_p.read_text()) == key, "cached follow-up scores were built from a different sample/plates"
        return pd.read_parquet(out_p)
    recs, imgs, scores = [], [], []

    def flush():
        if imgs:
            scores.append(scorer.logits(imgs, prompts, batch_size=batch))
            imgs.clear()

    for i in sample:
        for rec, im in conditions_v2(int(i), canvases[i], masks[i], plates):
            recs.append(rec); imgs.append(im)
            if len(imgs) >= batch:
                flush()
    flush()
    logits = np.concatenate(scores)
    res = pd.DataFrame(recs)
    res["s"] = logits[:, 1] - logits[:, 0]
    res.to_parquet(out_p)
    meta_p.write_text(json.dumps(key))
    return res


def _thumb_key(rec, label):
    c = rec["cond"]
    if c in ("original", "bird_only", "bg_only"):
        return (c, None)
    if c.startswith("paste"):
        return (c, rec["scale"])
    if c == "text" and rec["size"] == 0.08:
        mis = "waterbird" if label == 0 else "landbird"
        if rec["word"] == mis:
            return ("text_misleading", 0.08)
        if rec["word"] == NEUTRAL_WORD:
            return ("text_neutral", 0.08)
    return None


def run(meta: pd.DataFrame, sample: np.ndarray, canvases, masks, plates, scorer, prompts, name: str,
        batch: int = 512, seed: int = SEED):
    """Score every condition for every sampled bird. Cached as parquet + thumbnails .npz."""
    out_p = CACHE_DIR / f"cue_{name}.parquet"
    th_p = CACHE_DIR / f"cue_{name}_thumbs.npz"
    if out_p.exists() and th_p.exists():
        return pd.read_parquet(out_p), dict(np.load(th_p))
    rng = np.random.default_rng(seed)
    recs, imgs, scores = [], [], []
    keys = [f"{c}|{s}" for c, s in THUMB_CONDS]
    thumbs = np.zeros((len(sample), len(THUMB_CONDS), THUMB, THUMB, 3), np.uint8)
    pos = {i: k for k, i in enumerate(sample)}

    def flush():
        if imgs:
            scores.append(scorer.logits(imgs, prompts, batch_size=batch))
            imgs.clear()

    for i in sample:
        row = meta.loc[i]
        for rec, im in conditions(i, row, canvases[i], masks[i], plates, rng):
            recs.append(rec)
            imgs.append(im)
            tk = _thumb_key(rec, int(row.label))
            if tk is not None and f"{tk[0]}|{tk[1]}" in keys:
                thumbs[pos[i], keys.index(f"{tk[0]}|{tk[1]}")] = np.asarray(im.resize((THUMB, THUMB), Image.LANCZOS))
            if len(imgs) >= batch:
                flush()
    flush()
    logits = np.concatenate(scores)
    res = pd.DataFrame(recs)
    res["s"] = logits[:, 1] - logits[:, 0]
    res = res.merge(meta[["idx", "label", "place", "group", "species"]], on="idx", how="left")
    res["margin"] = np.where(res.label == 1, res.s, -res.s)
    res.to_parquet(out_p)
    np.savez_compressed(th_p, thumbs=thumbs, idx=np.asarray(sample), keys=np.array(keys))
    return res, dict(np.load(th_p))
