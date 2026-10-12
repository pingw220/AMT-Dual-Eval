"""DTW audio distance.

Implements the DTW scoring routine used by AMT-Dual-Eval. Frames are compared
with a cosine cost matrix (scipy.cdist), accumulated with the standard symmetric
3-direction DTW recurrence, and the total cost is divided by the warping-path
length:

    normalized_cost = total_cost / path_length

Lower normalized_cost indicates more similar audio; identical inputs give ~0.

Determinism: the cost matrix and DP are pure float arithmetic with fixed
tie-breaking, so a fixed audio pair always yields the same score.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.distance import cdist

from .features import extract_features
from .utils import load_config


@dataclass(frozen=True)
class DTWResult:
    total_cost: float
    normalized_cost: float
    path_length: int
    metric: str
    feature: str


def _accumulate(cost: np.ndarray) -> tuple[float, int]:
    """Standard DTW accumulation returning (total_cost, path_length).

    Two rolling rows for cost (D) and path length (L). Step set:
    diagonal (match), up (insertion), left (deletion). Ties are broken in the
    order diagonal -> up -> left.
    """
    t1, t2 = cost.shape
    inf = np.inf
    d_prev = np.empty(t2, dtype=np.float64)
    l_prev = np.empty(t2, dtype=np.int64)
    d_cur = np.empty(t2, dtype=np.float64)
    l_cur = np.empty(t2, dtype=np.int64)

    # First row: only left moves are possible.
    acc = 0.0
    for j in range(t2):
        acc += cost[0, j]
        d_prev[j] = acc
        l_prev[j] = j + 1

    for i in range(1, t1):
        # j = 0: only "up" move available.
        d_cur[0] = d_prev[0] + cost[i, 0]
        l_cur[0] = l_prev[0] + 1
        for j in range(1, t2):
            diag = d_prev[j - 1]
            up = d_prev[j]
            left = d_cur[j - 1]
            best = diag
            best_len = l_prev[j - 1]
            if up < best:
                best = up
                best_len = l_prev[j]
            if left < best:
                best = left
                best_len = l_cur[j - 1]
            d_cur[j] = best + cost[i, j]
            l_cur[j] = best_len + 1
        d_prev, d_cur = d_cur, d_prev
        l_prev, l_cur = l_cur, l_prev

    return float(d_prev[t2 - 1]), int(l_prev[t2 - 1])


def dtw_distance(
    features1: np.ndarray,
    features2: np.ndarray,
    metric: str = "cosine",
    feature_name: str = "",
) -> DTWResult:
    """Compute the DTW distance between two (n_features x n_frames) matrices."""
    f1 = np.ascontiguousarray(features1.T, dtype=np.float64)  # (T1, d)
    f2 = np.ascontiguousarray(features2.T, dtype=np.float64)  # (T2, d)
    cost = cdist(f1, f2, metric=metric)
    if not np.all(np.isfinite(cost)):
        max_cost = 2.0 if metric == "cosine" else np.nanmax(cost[np.isfinite(cost)])
        cost = np.nan_to_num(cost, nan=max_cost, posinf=max_cost, neginf=0.0)
    total, path_len = _accumulate(cost.astype(np.float64, copy=False))
    norm = total / max(1, path_len)
    return DTWResult(total, norm, path_len, metric, feature_name)


def score_audio_dtw(
    reference: str,
    candidate: str,
    feature: str,
    metric: str | None = None,
) -> DTWResult:
    """Score one (reference, candidate) audio pair with DTW for ``feature``."""
    cfg = load_config("dtw_default.yaml")
    metric = metric or cfg["metric"]
    fr = extract_features(reference, feature)
    fc = extract_features(candidate, feature)
    return dtw_distance(fr, fc, metric=metric, feature_name=feature)
