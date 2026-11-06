"""Input editing for the controlled cue-conflict experiment.

Everything here edits *inputs* (allowed in Phase I): segmentation masks from a
separate model (rembg / U^2-Net), OpenCV inpainting, compositing and text
rendering. CLIP is only called afterwards, on the edited images.

All edited images live on a 224 x 224 canvas: the original image is
center-cropped to a square and resized, which is what CLIPProcessor does
anyway (resize shortest side to 224, center-crop 224). So the processor
leaves our canvases unchanged and text or pasted birds are never cropped away.
"""
from __future__ import annotations

from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CANVAS = 224
GRAY = (128, 128, 128)


# ----------------------------------------------------------------- geometry
def square_canvas(img: Image.Image, size: int = CANVAS) -> Image.Image:
    """Center-crop to a square, then resize to size x size (bicubic)."""
    img = img.convert("RGB")
    w, h = img.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return img.crop((left, top, left + s, top + s)).resize((size, size), Image.BICUBIC)


def square_mask(mask: np.ndarray, size: int = CANVAS) -> np.ndarray:
    """Same crop/resize for a float mask in [0, 1]."""
    h, w = mask.shape
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    m = mask[top:top + s, left:left + s]
    return cv2.resize(m.astype(np.float32), (size, size), interpolation=cv2.INTER_LINEAR)


# ------------------------------------------------------------- segmentation
@lru_cache(maxsize=1)
def _rembg_session(model: str = "u2net"):
    from rembg import new_session
    return new_session(model, providers=["CPUExecutionProvider"])


def segment(img: Image.Image, model: str = "u2net") -> np.ndarray:
    """Soft foreground mask (float32 in [0, 1]) at the image's own resolution."""
    from rembg import remove
    m = remove(img.convert("RGB"), session=_rembg_session(model), only_mask=True)
    return np.asarray(m, dtype=np.float32) / 255.0


def mask_stats(mask: np.ndarray, thr: float = 0.5) -> dict:
    """Quality numbers for one mask: area, fragmentation, border contact, softness."""
    b = (mask > thr).astype(np.uint8)
    area = b.mean()
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    if n > 1:
        sizes = st[1:, cv2.CC_STAT_AREA]
        largest = sizes.max() / max(sizes.sum(), 1)
        n_comp = int((sizes >= 0.01 * sizes.sum()).sum())
    else:
        largest, n_comp = 0.0, 0
    border = np.concatenate([b[0], b[-1], b[:, 0], b[:, -1]]).mean()
    soft = ((mask > 0.1) & (mask < 0.9)).sum() / max((mask > 0.1).sum(), 1)
    ys, xs = np.nonzero(b)
    bbox = (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else (0, 0, 0, 0)
    return dict(mask_area=float(area), mask_largest_cc=float(largest), mask_n_comp=n_comp,
                mask_border=float(border), mask_soft=float(soft),
                bbox_w=int(bbox[2] - bbox[0] + 1) if len(xs) else 0,
                bbox_h=int(bbox[3] - bbox[1] + 1) if len(xs) else 0)


def is_clean(st: dict, min_area=0.02, max_area=0.6, min_cc=0.9, max_comp=2, max_border=0.15,
             max_soft=0.35) -> bool:
    """Rule for 'clean' masks (documented in the notebook)."""
    return (min_area <= st["mask_area"] <= max_area and st["mask_largest_cc"] >= min_cc
            and st["mask_n_comp"] <= max_comp and st["mask_border"] <= max_border
            and st["mask_soft"] <= max_soft)


def keep_largest(mask: np.ndarray, thr: float = 0.5) -> np.ndarray:
    """Zero out everything but the largest connected component (soft edges kept)."""
    b = (mask > thr).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    if n <= 2:
        return mask
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    near = cv2.dilate((lab == k).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    return mask * near


# ------------------------------------------------------------- conditions
def bird_on_gray(img224: Image.Image, mask224: np.ndarray) -> Image.Image:
    """Bird kept where it was, everything else neutral gray."""
    a = np.clip(mask224, 0, 1)[..., None]
    out = np.asarray(img224, np.float32) * a + np.array(GRAY, np.float32) * (1 - a)
    return Image.fromarray(out.round().astype(np.uint8))


def inpaint(img224: Image.Image, mask224: np.ndarray, dilate: int = 9, radius: int = 7) -> Image.Image:
    """Remove the bird: dilate the mask, then OpenCV Telea inpainting."""
    m = (mask224 > 0.2).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((dilate, dilate), np.uint8))
    arr = cv2.inpaint(np.asarray(img224)[:, :, ::-1].copy(), m, radius, cv2.INPAINT_TELEA)
    return Image.fromarray(arr[:, :, ::-1])


def cutout(img224: Image.Image, mask224: np.ndarray):
    """RGBA crop of the bird (bounding box of the mask)."""
    a = (np.clip(mask224, 0, 1) * 255).astype(np.uint8)
    ys, xs = np.nonzero(a > 127)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([np.asarray(img224), a])[y0:y1, x0:x1]
    return Image.fromarray(rgba, "RGBA")


def paste(plate224: Image.Image, bird_rgba: Image.Image, scale: float, fill: float = 0.8) -> Image.Image:
    """Paste the bird centered on a plate.

    scale = 1.0 means the bird's longer bounding-box side is `fill` x canvas
    (0.8 x 224 = 179 px); scale 0.15 means 27 px.
    """
    w, h = bird_rgba.size
    target = max(2, int(round(scale * fill * CANVAS)))
    f = target / max(w, h)
    b = bird_rgba.resize((max(1, int(round(w * f))), max(1, int(round(h * f)))), Image.LANCZOS)
    out = plate224.copy()
    x = (CANVAS - b.size[0]) // 2
    y = (CANVAS - b.size[1]) // 2
    out.paste(b, (x, y), b)
    return out


@lru_cache(maxsize=64)
def _font(px: int):
    for name in ["arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def overlay_text(img224: Image.Image, word: str, size: float, band: str = "bottom", fill: str = "black") -> Image.Image:
    """Black word on a white box, centered horizontally in the top or bottom band.

    size = cap height of the font as a fraction of the canvas height. The word is
    shrunk if it would be wider than 96% of the canvas, so long words keep the
    same width limit (we record the actual box area for every overlay).
    """
    out = img224.copy()
    d = ImageDraw.Draw(out)
    px = max(6, int(round(size * CANVAS / 0.72)))  # cap height ~0.72 em for bold sans fonts
    font = _font(px)
    l, t, r, b = d.textbbox((0, 0), word, font=font)
    while (r - l) > 0.96 * CANVAS - 6 and px > 6:
        px -= 1
        font = _font(px)
        l, t, r, b = d.textbbox((0, 0), word, font=font)
    tw, th = r - l, b - t
    pad = max(2, int(0.15 * th))
    x = (CANVAS - tw) // 2
    y = (CANVAS - th - 2 * pad - 4) if band == "bottom" else 4 + pad
    d.rectangle([x - pad, y - pad, x + tw + pad, y + th + pad], fill="white")
    d.text((x - l, y - t), word, font=font, fill=fill)   # fill="white" gives a blank box of the same size
    return out


def text_box_area(word: str, size: float) -> float:
    """Fraction of the canvas covered by the white box for this word and size."""
    blank = Image.new("RGB", (CANVAS, CANVAS), (0, 0, 0))
    a = np.asarray(overlay_text(blank, word, size)).sum(axis=2) > 0
    return float(a.mean())


def free_band(mask224: np.ndarray) -> str:
    """Top or bottom third, whichever overlaps the bird less."""
    third = CANVAS // 3
    return "top" if mask224[:third].sum() < mask224[-third:].sum() else "bottom"
