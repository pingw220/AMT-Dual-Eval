"""High-level audio scoring: single-feature and top-3 evaluation."""
from __future__ import annotations

from typing import Dict, List, Optional

from .dtw import score_audio_dtw
from .twed import score_audio_twed
from .utils import load_config, top3


def score_pair(
    reference: str,
    candidate: str,
    metric: str,
    feature: str,
    nu: Optional[float] = None,
    lambd: Optional[float] = None,
) -> Dict[str, object]:
    """Score one audio pair for one (metric, feature). Returns a flat dict row."""
    metric = metric.lower()
    if metric == "dtw":
        r = score_audio_dtw(reference, candidate, feature)
        return {
            "metric": "dtw",
            "feature": feature,
            "score": r.normalized_cost,
            "total_cost": r.total_cost,
            "path_length": r.path_length,
        }
    if metric == "twed":
        r = score_audio_twed(reference, candidate, feature, nu=nu, lambd=lambd)
        return {
            "metric": "twed",
            "feature": feature,
            "score": r.normalized_cost,
            "total_cost": r.total_cost,
            "path_length": r.path_length,
            "nu": r.nu,
            "lambda": r.lambd,
        }
    raise ValueError(f"Unknown metric {metric!r}; choose 'dtw' or 'twed'")


def default_feature(metric: str) -> str:
    cfg = "dtw_default.yaml" if metric.lower() == "dtw" else "twed_default.yaml"
    return load_config(cfg)["default_feature"]


def score_all_top3(
    reference: str,
    candidate: str,
    metric: str,
    nu: Optional[float] = None,
    lambd: Optional[float] = None,
) -> List[Dict[str, object]]:
    """Score one audio pair across the verified top-3 features for ``metric``."""
    return [
        score_pair(reference, candidate, metric, feat, nu=nu, lambd=lambd)
        for feat in top3(metric)
    ]
