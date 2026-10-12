"""Human listening-evaluation scoring for AMT-Dual-Eval.

Implements the system-ranking methods used by the released human-evaluation
analysis: system_rank, wilson_win_rate, pairwise_matrix, bradley_terry,
least_squares, and elo.

Operates on a de-identified forced-choice table with one row per judgment and
columns:
    system_a, system_b : pipeline names of the two compared candidates
    choice             : "A" or "B" (the chosen candidate)
    (optional) row_order : observation order for the deterministic Elo pass.

Forced choice: each judgment is a binary win for system_a (choice == "A") or
system_b (choice == "B"). Judgments are unweighted.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

METHODS = ["system_rank", "wilson_win_rate", "pairwise_matrix",
           "bradley_terry", "least_squares", "elo"]


def _system_index(df: pd.DataFrame) -> List[str]:
    return sorted(set(df["system_a"]).union(df["system_b"]))


def _wins_and_counts(df: pd.DataFrame, idx: Dict[str, int], n: int):
    wins = np.zeros((n, n))
    counts = np.zeros((n, n))
    for a_name, b_name, choice in zip(df["system_a"], df["system_b"], df["choice"]):
        a, b = idx[a_name], idx[b_name]
        counts[a, b] += 1.0
        counts[b, a] += 1.0
        if choice == "A":
            wins[a, b] += 1.0
        elif choice == "B":
            wins[b, a] += 1.0
    return wins, counts


def _ranking(scores: np.ndarray, systems: List[str], method: str) -> pd.DataFrame:
    out = pd.DataFrame({"system": systems, "score": scores.astype(float)})
    out = out.sort_values(["score", "system"], ascending=[False, True], kind="mergesort")
    out = out.reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    out["method"] = method
    return out[["method", "system", "score", "rank"]]


def system_rank(df, idx, systems):
    n = len(systems)
    wins = np.zeros(n)
    exposure = np.zeros(n)
    for a_name, b_name, choice in zip(df["system_a"], df["system_b"], df["choice"]):
        a, b = idx[a_name], idx[b_name]
        exposure[a] += 1.0
        exposure[b] += 1.0
        if choice == "A":
            wins[a] += 1.0
        elif choice == "B":
            wins[b] += 1.0
    scores = np.divide(wins, exposure, out=np.full(n, 0.5), where=exposure > 0)
    return _ranking(scores, systems, "system_rank")


def wilson_win_rate(df, idx, systems):
    n = len(systems)
    wins = np.zeros(n)
    exposure = np.zeros(n)
    for a_name, b_name, choice in zip(df["system_a"], df["system_b"], df["choice"]):
        a, b = idx[a_name], idx[b_name]
        exposure[a] += 1.0
        exposure[b] += 1.0
        if choice == "A":
            wins[a] += 1.0
        elif choice == "B":
            wins[b] += 1.0
    z = 1.96
    phat = np.divide(wins, exposure, out=np.full(n, 0.5), where=exposure > 0)
    denom = 1.0 + z * z / np.maximum(exposure, 1.0)
    center = phat + z * z / (2.0 * np.maximum(exposure, 1.0))
    margin = z * np.sqrt(
        (phat * (1.0 - phat) + z * z / (4.0 * np.maximum(exposure, 1.0)))
        / np.maximum(exposure, 1.0)
    )
    scores = np.where(exposure > 0, (center - margin) / denom, 0.0)
    return _ranking(scores, systems, "wilson_win_rate")


def pairwise_matrix(df, idx, systems):
    n = len(systems)
    wins, counts = _wins_and_counts(df, idx, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        win_rate = wins / counts
    win_rate[~np.isfinite(win_rate)] = np.nan
    np.fill_diagonal(win_rate, np.nan)
    scores = np.array([
        0.5 if np.isnan(np.delete(win_rate[i], i)).all()
        else np.nanmean(np.delete(win_rate[i], i))
        for i in range(n)
    ])
    return _ranking(scores, systems, "pairwise_matrix")


def _fit_bradley_terry(wins, counts, max_iter=1000, tol=1e-8, epsilon=1e-12):
    n = wins.shape[0]
    ability = np.ones(n)
    converged = False
    n_iter = 0
    for it in range(max_iter):
        n_iter = it + 1
        old = ability.copy()
        for i in range(n):
            w_i = wins[i].sum()
            denom = 0.0
            for j in range(n):
                if i == j or counts[i, j] <= 0:
                    continue
                denom += counts[i, j] / (old[i] + old[j] + epsilon)
            if denom > 0 and w_i > 0:
                ability[i] = w_i / denom
            elif w_i <= 0:
                ability[i] = epsilon
        ability = np.maximum(ability, epsilon)
        ability /= np.exp(np.mean(np.log(ability + epsilon)))
        delta = np.max(np.abs(np.log(ability + epsilon) - np.log(old + epsilon)))
        if delta < tol:
            converged = True
            break
    return np.log(ability + epsilon), converged, n_iter


def bradley_terry(df, idx, systems):
    n = len(systems)
    wins, counts = _wins_and_counts(df, idx, n)
    theta, _, _ = _fit_bradley_terry(wins, counts)
    return _ranking(theta, systems, "bradley_terry")


def least_squares(df, idx, systems, ridge: float = 1.0):
    n = len(systems)
    rows = list(zip(df["system_a"], df["system_b"], df["choice"]))
    x = np.zeros((len(rows), n))
    y = np.zeros(len(rows))
    for k, (a_name, b_name, choice) in enumerate(rows):
        x[k, idx[a_name]] = 1.0
        x[k, idx[b_name]] = -1.0
        y[k] = 1.0 if choice == "A" else -1.0
    lhs = x.T @ x + float(ridge) * np.eye(n)
    rhs = x.T @ y
    theta = np.linalg.solve(lhs, rhs)
    theta = theta - np.mean(theta)
    return _ranking(theta, systems, "least_squares")


def elo(df, idx, systems, base_rating: float = 1500.0, k_factor: float = 24.0):
    n = len(systems)
    ratings = np.full(n, float(base_rating))
    ordered = df.sort_values("row_order", kind="mergesort") if "row_order" in df else df
    for a_name, b_name, choice in zip(ordered["system_a"], ordered["system_b"], ordered["choice"]):
        a, b = idx[a_name], idx[b_name]
        expected_a = 1.0 / (1.0 + 10.0 ** ((ratings[b] - ratings[a]) / 400.0))
        score_a = 1.0 if choice == "A" else 0.0
        delta = k_factor * (score_a - expected_a)
        ratings[a] += delta
        ratings[b] -= delta
    return _ranking(ratings, systems, "elo")


_DISPATCH = {
    "system_rank": system_rank,
    "wilson_win_rate": wilson_win_rate,
    "pairwise_matrix": pairwise_matrix,
    "bradley_terry": bradley_terry,
    "least_squares": least_squares,
    "elo": elo,
}


def score_all_methods(df: pd.DataFrame) -> pd.DataFrame:
    """Run all six ranking methods on a forced-choice table.

    Returns a long DataFrame with columns method, system, score, rank.
    """
    needed = {"system_a", "system_b", "choice"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Responses table missing columns: {sorted(missing)}")
    df = df.loc[df["choice"].isin(["A", "B"])].copy()
    systems = _system_index(df)
    idx = {s: i for i, s in enumerate(systems)}
    return pd.concat(
        [_DISPATCH[m](df, idx, systems) for m in METHODS],
        ignore_index=True,
    )
