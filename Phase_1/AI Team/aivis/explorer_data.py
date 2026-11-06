"""Data for the interactive explorer: compact records + base64 WebP thumbnails (offline, < ~20 MB)."""
from __future__ import annotations

import base64
import io

import numpy as np
import pandas as pd
from PIL import Image


def b64_webp(arr: np.ndarray, size: int, quality: int = 60) -> str:
    im = Image.fromarray(np.asarray(arr)).resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def image_records(df: pd.DataFrame, canvases, thumb: int = 44, cols=None) -> list[dict]:
    cols = cols or ["idx", "species", "group", "label", "place", "margin", "correct", "water_rating", "mask_area",
                    "ux", "uy", "dx", "dy", "cluster"]
    out = []
    for r in df[cols].itertuples(index=False):
        d = {c: (round(float(v), 3) if isinstance(v, (float, np.floating)) else (int(v) if isinstance(v, (np.integer, np.bool_, bool)) else v))
             for c, v in zip(cols, r)}
        d["img"] = b64_webp(canvases[d["idx"]], thumb)
        out.append(d)
    return out


def bird_records(cue: pd.DataFrame, thumbs: dict, strip_idx, thumb: int = 56) -> dict:
    """Per experiment bird: margin curves (all birds) + condition thumbnails (strip birds only)."""
    out = {}
    keys = [k for k in thumbs["keys"]]
    pos = {int(i): k for k, i in enumerate(thumbs["idx"])}
    strip_idx = set(int(i) for i in strip_idx)
    for i, d in cue.groupby("idx"):
        rec = {}
        get = lambda c: d[d.cond == c]
        rec["orig"] = round(float(get("original").margin.iloc[0]), 2)
        rec["bird"] = round(float(get("bird_only").margin.iloc[0]), 2)
        rec["bg"] = round(float(get("bg_only").margin.iloc[0]), 2)
        for c in ("paste_gray", "paste_match", "paste_conflict"):
            g = get(c).sort_values("scale", ascending=False)
            rec[c] = [round(float(v), 2) for v in g.margin]
        t = get("text")
        lab = int(d.label.iloc[0])
        mis = "waterbird" if lab == 0 else "landbird"
        cor = "landbird" if lab == 0 else "waterbird"
        for role, w in [("text_mis", mis), ("text_cor", cor), ("text_neu", "triangle")]:
            rec[role] = [round(float(v), 2) for v in t[t.word == w].sort_values("size").margin]
        if int(i) in strip_idx and int(i) in pos:
            rec["thumbs"] = [b64_webp(thumbs["thumbs"][pos[int(i)], k], thumb) for k in range(len(keys))]
        out[int(i)] = rec
    return out
