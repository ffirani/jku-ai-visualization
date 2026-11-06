"""Scores, strategies and threshold-free measures computed from CLIP output logits only."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import rankdata

from .config import N_BOOT, SEED
from .prompts import PROMPT_PAIRS, SCENE_PROMPTS


def bank_slices(n_species: int = 200):
    """Column ranges of the prompt bank: pairs, species, scenes."""
    n_pair = 2 * len(PROMPT_PAIRS)
    return (slice(0, n_pair), slice(n_pair, n_pair + n_species),
            slice(n_pair + n_species, n_pair + n_species + len(SCENE_PROMPTS)))


def strategy_scores(L: np.ndarray, species_label: np.ndarray) -> dict[str, np.ndarray]:
    """Water-vs-land score s(x) per strategy (positive = 'waterbird').

    - prompt pairs: logit(water prompt) - logit(land prompt)
    - species routing (hard): +1/-1 from the habitat of the argmax species
      (the continuous score used for AUCs is the soft one below)
    - species routing (soft): log P(any water species) - log P(any land species), softmax over 200 species
    """
    out = {}
    for k, (name, _, _) in enumerate(PROMPT_PAIRS):
        out[name] = L[:, 2 * k + 1] - L[:, 2 * k]
    _, sp, _ = bank_slices(len(species_label))
    S = L[:, sp]
    lp = S - logsumexp(S, axis=1, keepdims=True)
    soft = logsumexp(lp[:, species_label == 1], axis=1) - logsumexp(lp[:, species_label == 0], axis=1)
    out["species routing"] = soft
    return out


def species_routing_hard(L: np.ndarray, species_label: np.ndarray):
    _, sp, _ = bank_slices(len(species_label))
    top = L[:, sp].argmax(axis=1)
    return top, species_label[top]


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(score of a random pos > random neg), ties count half (Mann-Whitney)."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")      # e.g. a bootstrap resample without any errors in a group
    r = rankdata(np.concatenate([pos, neg]))
    n1, n0 = len(pos), len(neg)
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def species_resamples(species: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED):
    """Yield bootstrap index arrays that resample whole species (all images of a drawn species)."""
    codes = pd.factorize(np.asarray(species))[0]
    members = [np.flatnonzero(codes == k) for k in range(codes.max() + 1)]
    rng = np.random.default_rng(seed)
    for _ in range(n_boot):
        yield np.concatenate([members[k] for k in rng.integers(0, len(members), len(members))])


def _tf_stats(s, y, p, sel):
    def cell(c, b):
        j = sel[(y[sel] == c) & (p[sel] == b)]
        return s[j]
    bg = np.mean([auc(cell(c, 1), cell(c, 0)) for c in (0, 1)])
    cl = np.mean([auc(cell(1, b), cell(0, b)) for b in (0, 1)])
    return np.array([bg, cl])


def threshold_free(s: np.ndarray, df: pd.DataFrame, n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Background AUC (within class) and class AUC (within background), with species-cluster bootstrap CIs.

    background AUC = mean over classes of P(s on water bg > s on land bg | same class).
      0.5 = the background does not move the score at all.
    class AUC = mean over backgrounds of P(s of waterbird > s of landbird | same background).
    CIs resample whole species, because images of one species are not independent.
    """
    y, p = df["label"].to_numpy(), df["place"].to_numpy()
    est = _tf_stats(s, y, p, np.arange(len(s)))
    boots = np.array([_tf_stats(s, y, p, sel) for sel in species_resamples(df["species"].to_numpy(), n_boot, seed)])
    lo, hi = np.quantile(boots, [0.025, 0.975], axis=0)
    return dict(bg_auc=est[0], bg_lo=lo[0], bg_hi=hi[0], class_auc=est[1], class_lo=lo[1], class_hi=hi[1])


def threshold_free_diff(s_a: np.ndarray, s_b: np.ndarray, df: pd.DataFrame, n_boot: int = N_BOOT,
                        seed: int = SEED) -> dict:
    """Paired species-cluster bootstrap of (a - b) for background AUC and class AUC."""
    y, p = df["label"].to_numpy(), df["place"].to_numpy()
    allj = np.arange(len(s_a))
    est = _tf_stats(s_a, y, p, allj) - _tf_stats(s_b, y, p, allj)
    boots = np.array([_tf_stats(s_a, y, p, sel) - _tf_stats(s_b, y, p, sel)
                      for sel in species_resamples(df["species"].to_numpy(), n_boot, seed)])
    lo, hi = np.quantile(boots, [0.025, 0.975], axis=0)
    return dict(d_bg=est[0], d_bg_lo=lo[0], d_bg_hi=hi[0], d_class=est[1], d_class_lo=lo[1], d_class_hi=hi[1])


def paired_group_diff(correct_a: np.ndarray, correct_b: np.ndarray, groups: np.ndarray,
                      n_boot: int = N_BOOT, seed: int = SEED, species=None) -> pd.DataFrame:
    """Accuracy(a) - accuracy(b) per group, paired bootstrap (over species if given, else over images)."""
    from .stats import cluster_boot_mean
    rows = []
    rng = np.random.default_rng(seed)
    for g in pd.unique(groups):
        j = np.flatnonzero(groups == g)
        d = correct_a[j].astype(float) - correct_b[j].astype(float)
        if species is not None:
            _, lo_, hi_ = cluster_boot_mean(d, np.asarray(species)[j], n_boot, seed)
        else:
            bs = d[rng.integers(0, len(j), (n_boot, len(j)))].mean(axis=1)
            lo_, hi_ = np.quantile(bs, 0.025), np.quantile(bs, 0.975)
        rows.append(dict(group=g, n=len(j), diff=d.mean(), lo=lo_, hi=hi_,
                         fixed=int(((correct_a[j] == 1) & (correct_b[j] == 0)).sum()),
                         broken=int(((correct_a[j] == 0) & (correct_b[j] == 1)).sum())))
    return pd.DataFrame(rows)
