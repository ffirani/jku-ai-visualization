"""Bootstrap confidence intervals (percentile method) used throughout the notebook."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sps

from .config import N_BOOT, SEED


def cluster_boot_mean(x, clusters, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """Mean with a cluster bootstrap CI: resample whole clusters (e.g. species), keep all their members.

    Used wherever several images share a species (or several birds share a plate), so that
    the CI reflects the number of independent units, not the number of images.
    """
    x = np.asarray(x, float)
    cl = pd.factorize(np.asarray(clusters))[0]
    sums = np.bincount(cl, weights=x)
    cnts = np.bincount(cl).astype(float)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(sums), size=(n_boot, len(sums)))
    boots = sums[pick].sum(axis=1) / cnts[pick].sum(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(x.mean()), float(lo), float(hi)


def cluster_boot_diff(xa, ca, xb, cb, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """mean(a) - mean(b), clusters resampled independently within a and b."""
    def boots(x, c, s):
        x = np.asarray(x, float); cl = pd.factorize(np.asarray(c))[0]
        sums, cnts = np.bincount(cl, weights=x), np.bincount(cl).astype(float)
        pick = np.random.default_rng(s).integers(0, len(sums), size=(n_boot, len(sums)))
        return sums[pick].sum(axis=1) / cnts[pick].sum(axis=1)
    d = boots(xa, ca, seed) - boots(xb, cb, seed + 1)
    lo, hi = np.quantile(d, [alpha / 2, 1 - alpha / 2])
    return float(np.mean(xa) - np.mean(xb)), float(lo), float(hi)


def two_way_boot_mean(mat, row_clusters=None, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """Mean of a complete rows x columns matrix (e.g. birds x plates), resampling rows AND columns.

    Rows can be grouped into clusters (species); columns (plates) are resampled individually.
    """
    mat = np.asarray(mat, float)
    nr, nc = mat.shape
    rng = np.random.default_rng(seed)
    if row_clusters is None:
        groups = [np.array([i]) for i in range(nr)]
    else:
        cl = pd.factorize(np.asarray(row_clusters))[0]
        groups = [np.flatnonzero(cl == k) for k in range(cl.max() + 1)]
    boots = np.empty(n_boot)
    for b in range(n_boot):
        rows = np.concatenate([groups[k] for k in rng.integers(0, len(groups), len(groups))])
        cols = rng.integers(0, nc, nc)
        boots[b] = mat[np.ix_(rows, cols)].mean()
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(mat.mean()), float(lo), float(hi)


def boot_ci(x, stat=np.mean, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """Point estimate and percentile bootstrap CI of `stat` over a 1-D sample."""
    x = np.asarray(x)
    x = x[~np.isnan(x)] if x.dtype.kind == "f" else x
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = np.apply_along_axis(stat, 1, x[idx]) if stat is not np.mean else x[idx].mean(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(stat(x)), float(lo), float(hi)


def boot_diff(a, b, stat=np.mean, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """stat(a) - stat(b) for two independent samples, with a percentile bootstrap CI."""
    a, b = np.asarray(a), np.asarray(b)
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(a), size=(n_boot, len(a)))
    ib = rng.integers(0, len(b), size=(n_boot, len(b)))
    boots = a[ia].mean(axis=1) - b[ib].mean(axis=1) if stat is np.mean else (
        np.apply_along_axis(stat, 1, a[ia]) - np.apply_along_axis(stat, 1, b[ib]))
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(stat(a) - stat(b)), float(lo), float(hi)


def group_table(df: pd.DataFrame, value: str, by, n_boot: int = N_BOOT, seed: int = SEED) -> pd.DataFrame:
    """Mean of `value` per group with n and a bootstrap 95% CI."""
    rows = []
    for key, g in df.groupby(by, sort=True, observed=True):
        est, lo, hi = boot_ci(g[value].to_numpy(dtype=float), n_boot=n_boot, seed=seed)
        key = key if isinstance(key, tuple) else (key,)
        rows.append((*key, len(g), est, lo, hi))
    cols = list(by) if isinstance(by, (list, tuple)) else [by]
    return pd.DataFrame(rows, columns=[*cols, "n", "mean", "ci_lo", "ci_hi"])


def spearman_ci(x, y, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05, clusters=None):
    """Spearman rho with a percentile bootstrap CI (pairs resampled together; whole clusters if given)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    rho = sps.spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    n = len(x)
    if clusters is not None:
        cl = pd.factorize(np.asarray(clusters)[ok])[0]
        groups = [np.flatnonzero(cl == k) for k in range(cl.max() + 1)]
    boots = np.empty(n_boot)
    for i in range(n_boot):
        if clusters is None:
            j = rng.integers(0, n, n)
        else:
            j = np.concatenate([groups[k] for k in rng.integers(0, len(groups), len(groups))])
        boots[i] = sps.spearmanr(x[j], y[j]).statistic
    lo, hi = np.nanquantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(rho), float(lo), float(hi), n


def fmt_ci(est, lo, hi, pct: bool = False, digits: int = 1) -> str:
    """'70.6% [69.4, 71.8]' or '1.23 [1.10, 1.36]'."""
    if pct:
        return f"{100*est:.{digits}f}% [{100*lo:.{digits}f}, {100*hi:.{digits}f}]"
    return f"{est:.{digits}f} [{lo:.{digits}f}, {hi:.{digits}f}]"
