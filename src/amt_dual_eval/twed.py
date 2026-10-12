"""TWED (Time-Warp Edit Distance) audio distance.

Implements exact Marteau TWED scoring with path-normalized cost. The recurrence
uses deletion penalties (``del = ||frame_i - frame_{i-1}||``), a match term
(``d(i,j) + d(i-1,j-1)``), and deterministic tie-breaking (match -> del1 -> del2).

The implementation uses rolling rows (O(m) memory, exact) so it runs on long
performance recordings without allocating the full DP matrix. The DP accumulator
is float64 while features are float32.

    normalized_cost = total_cost / path_length

Lower normalized_cost indicates more similar audio; identical inputs give 0.

Default parameters (nu, lambda, frame normalization, time unit) are defined in the
packaged TWED configuration. The CLI exposes --lambda-value / --nu overrides.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .features import extract_features
from .utils import load_config

_EPS = 1e-12


@dataclass(frozen=True)
class TWEDResult:
    total_cost: float
    normalized_cost: float
    path_length: int
    nu: float
    lambd: float
    frame_normalize: str
    time_unit: str
    feature: str


def _frame_l2(seq: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(seq, axis=1, keepdims=True)
    return seq / np.maximum(norms, _EPS)


def _frame_zscore(seq: np.ndarray) -> np.ndarray:
    mean = seq.mean(axis=1, keepdims=True)
    std = seq.std(axis=1, keepdims=True)
    return (seq - mean) / np.maximum(std, 1e-8)


def _normalize(seq: np.ndarray, mode: str) -> np.ndarray:
    if mode == "none":
        return seq
    if mode == "l2":
        return _frame_l2(seq)
    if mode == "zscore":
        return _frame_zscore(seq)
    if mode == "zscore_l2":
        return _frame_l2(_frame_zscore(seq))
    raise ValueError(f"Unknown frame_normalize={mode!r}")


def _time_axis(num_frames: int, time_unit: str, hop_length: int, sr: int) -> np.ndarray:
    if time_unit == "frames":
        return np.arange(num_frames, dtype=np.float64)
    if time_unit == "seconds":
        return np.arange(num_frames, dtype=np.float64) * hop_length / float(sr)
    raise ValueError(f"Unknown time_unit={time_unit!r}")


def twed_distance(
    seq1: np.ndarray,
    seq2: np.ndarray,
    nu: float,
    lambd: float,
    frame_normalize: str = "l2",
    time_unit: str = "frames",
    hop_length: int = 441,
    sr: int = 44100,
    feature_name: str = "",
) -> TWEDResult:
    """Exact Marteau TWED between two (n_features x n_frames) feature matrices."""
    if nu < 0:
        raise ValueError("nu must be non-negative")
    if lambd < 0:
        raise ValueError("lambd must be non-negative")

    # Work in (n_frames, dim).
    a = np.ascontiguousarray(seq1.T, dtype=np.float64)
    b = np.ascontiguousarray(seq2.T, dtype=np.float64)
    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    b = np.nan_to_num(b, nan=0.0, posinf=0.0, neginf=0.0)
    a = _normalize(a, frame_normalize)
    b = _normalize(b, frame_normalize)

    n, m = a.shape[0], b.shape[0]
    ta = _time_axis(n, time_unit, hop_length, sr)
    tb = _time_axis(m, time_unit, hop_length, sr)

    # Padded time axes: tA_pad[i] for i in 1..n equals ta[i-1]; tA_pad[0] = 0.
    tA = np.concatenate(([0.0], ta))
    tB = np.concatenate(([0.0], tb))

    # Deletion penalties del1[i] = ||a_pad[i] - a_pad[i-1]|| with a_pad[0] = 0.
    del1 = np.zeros(n + 1)
    del1[1] = np.linalg.norm(a[0]) if n >= 1 else 0.0
    if n >= 2:
        del1[2:] = np.linalg.norm(np.diff(a, axis=0), axis=1)
    del2 = np.zeros(m + 1)
    del2[1] = np.linalg.norm(b[0]) if m >= 1 else 0.0
    if m >= 2:
        del2[2:] = np.linalg.norm(np.diff(b, axis=0), axis=1)

    inf = np.inf
    # Row i-1 accumulators (i=0 row: dp[0,0]=0, dp[0,j>=1]=inf).
    dp_prev = np.full(m + 1, inf, dtype=np.float64)
    dp_prev[0] = 0.0
    len_prev = np.zeros(m + 1, dtype=np.int64)
    dp_cur = np.empty(m + 1, dtype=np.float64)
    len_cur = np.empty(m + 1, dtype=np.int64)

    prev_row_dist = None  # ||a[i-2] - b[j-2]|| over j, for the match second term
    for i in range(1, n + 1):
        dp_cur[0] = inf  # dp[i, 0] = inf for i >= 1
        len_cur[0] = 0
        # Distance of current frame a[i-1] to all b frames.
        row_dist = np.linalg.norm(b - a[i - 1], axis=1)  # length m, j-> j+1
        for j in range(1, m + 1):
            dist = row_dist[j - 1]
            if i > 1 and j > 1:
                dist += prev_row_dist[j - 2]

            htrans_match = abs(tA[i] - tB[j])
            if i > 1 and j > 1:
                htrans_match += abs(tA[i - 1] - tB[j - 1])
            d_match = dp_prev[j - 1] + dist + nu * htrans_match

            d_del1 = dp_prev[j] + del1[i] + lambd + nu * (tA[i] - tA[i - 1])
            d_del2 = dp_cur[j - 1] + del2[j] + lambd + nu * (tB[j] - tB[j - 1])

            if d_match <= d_del1 and d_match <= d_del2:
                dp_cur[j] = d_match
                len_cur[j] = len_prev[j - 1] + 1
            elif d_del1 <= d_del2:
                dp_cur[j] = d_del1
                len_cur[j] = len_prev[j] + 1
            else:
                dp_cur[j] = d_del2
                len_cur[j] = len_cur[j - 1] + 1

        dp_prev, dp_cur = dp_cur, dp_prev
        len_prev, len_cur = len_cur, len_prev
        prev_row_dist = row_dist

    total = float(dp_prev[m])
    path_len = int(len_prev[m])
    norm = total / max(1, path_len)
    return TWEDResult(
        total, norm, path_len, float(nu), float(lambd),
        frame_normalize, time_unit, feature_name,
    )


def score_audio_twed(
    reference: str,
    candidate: str,
    feature: str,
    nu: float | None = None,
    lambd: float | None = None,
) -> TWEDResult:
    """Score one (reference, candidate) audio pair with TWED for ``feature``."""
    cfg = load_config("twed_default.yaml")
    reg = load_config("feature_registry.yaml")["global"]
    nu = cfg["nu"] if nu is None else nu
    lambd = cfg["lambd"] if lambd is None else lambd
    fr = extract_features(reference, feature)
    fc = extract_features(candidate, feature)
    return twed_distance(
        fr, fc,
        nu=nu, lambd=lambd,
        frame_normalize=cfg["frame_normalize"],
        time_unit=cfg["time_unit"],
        hop_length=int(reg["hop_length"]),
        sr=int(reg["sample_rate"]),
        feature_name=feature,
    )
