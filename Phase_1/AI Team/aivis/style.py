"""One visual encoding for every figure (Okabe-Ito, colorblind-safe).

- Class (true bird label): landbird = orange, waterbird = blue.
- Background (place): same hues, but shown with a different channel
  (land background = filled marker / solid line, water background = open marker / dashed line).
- Cue type: bird = bluish green, background scene = reddish purple, written word = near-black.
- Correctness: correct = gray, error = vermillion.
- Margin m(x): diverging vermillion (wrong) -> light gray (0) -> dark slate (right).
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .config import OUT_DIR

LAND = "#E69F00"
WATER = "#0072B2"
CLASS_COLORS = {"landbird": LAND, "waterbird": WATER, 0: LAND, 1: WATER}
PLACE_COLORS = {"land": LAND, "water": WATER, 0: LAND, 1: WATER}

CUE_COLORS = {"bird": "#009E73", "background": "#CC79A7", "text": "#222222"}
CORRECT = "#9A9A9A"
ERROR = "#D55E00"
NEUTRAL = "#BBBBBB"

GROUPS = ["landbird / land", "landbird / water", "waterbird / land", "waterbird / water"]
GROUP_SHORT = {"landbird / land": "LB/land", "landbird / water": "LB/water",
               "waterbird / land": "WB/land", "waterbird / water": "WB/water"}
GROUP_COLOR = {g: (LAND if g.startswith("land") else WATER) for g in GROUPS}
# background channel: filled vs open markers, solid vs dashed lines
GROUP_FILLED = {g: g.endswith("/ land") for g in GROUPS}
GROUP_MARKER = {"landbird / land": "o", "landbird / water": "s",
                "waterbird / land": "^", "waterbird / water": "D"}
GROUP_LS = {g: ("-" if g.endswith("/ land") else "--") for g in GROUPS}

MARGIN_CMAP = LinearSegmentedColormap.from_list("margin", [ERROR, "#F2F2F2", "#2F3E46"])


def setup():
    """Readable-at-video-size defaults."""
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#E6E6E6",
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "svg.fonttype": "none",
        "font.family": "DejaVu Sans",
    })


def save(fig, name: str, svg: bool = True, dpi: int | None = None):
    """Write PNG (+ SVG) to outputs/ and return the PNG path.

    Photo grids (contact sheets) use svg=False: an SVG would only wrap the same raster images.
    """
    png = OUT_DIR / f"{name}.png"
    fig.savefig(png, bbox_inches="tight", facecolor="white", **({"dpi": dpi} if dpi else {}))
    svg_path = OUT_DIR / f"{name}.svg"
    if svg:
        fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    elif svg_path.exists():
        svg_path.unlink()
    return png


def group_scatter_kw(group: str, size: float = 18, alpha: float = 0.8) -> dict:
    """Marker style for one class x background group."""
    c = GROUP_COLOR[group]
    filled = GROUP_FILLED[group]
    return dict(marker=GROUP_MARKER[group], s=size, alpha=alpha,
                facecolors=c if filled else "none", edgecolors=c, linewidths=0.9)


def suptitle(fig, finding: str, sub: str | None = None, wrap: int = 115):
    """Figure title = the finding; optional grey subtitle = what is shown, n, CI method.

    Both sit above the axes (outside the figure box); savefig(bbox_inches='tight') keeps them.
    Call after tight_layout().
    """
    import textwrap
    h = fig.get_figheight()
    finding = "\n".join(textwrap.wrap(finding, wrap))
    sub = "\n".join(textwrap.wrap(sub, int(wrap * 1.35))) if sub else None
    n_sub = sub.count("\n") + 1 if sub else 0
    y_sub = 1 + 0.12 / h
    y_title = y_sub + (n_sub * 0.2 + 0.08) / h if sub else y_sub
    fig.text(0.01, y_title, finding, ha="left", va="bottom", fontsize=14, fontweight="bold")
    if sub:
        fig.text(0.01, y_sub, sub, ha="left", va="bottom", fontsize=10, color="#555555")
