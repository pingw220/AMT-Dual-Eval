"""AMT-Dual-Eval: dual evaluation of automatic music transcription systems.

Two components:
  * Audio-level evaluation (DTW and TWED over selected audio features).
  * Human listening-evaluation scoring (forced-choice system rankings).

Public API:
    from amt_dual_eval import score_audio_dtw, score_audio_twed
    from amt_dual_eval.evaluate_audio import score_pair, score_all_top3
"""
from __future__ import annotations

__version__ = "0.1.0"

from .dtw import DTWResult, dtw_distance, score_audio_dtw
from .twed import TWEDResult, twed_distance, score_audio_twed
from .evaluate_audio import score_pair, score_all_top3, default_feature
from .utils import top3, supported_features

__all__ = [
    "__version__",
    "DTWResult",
    "TWEDResult",
    "dtw_distance",
    "twed_distance",
    "score_audio_dtw",
    "score_audio_twed",
    "score_pair",
    "score_all_top3",
    "default_feature",
    "top3",
    "supported_features",
]
