"""Audio feature extraction for AMT-Dual-Eval.

Implements the four audio features used by the released DTW/TWED pipeline. Each
extractor:

  * loads mono audio at 44100 Hz,
  * uses a 10 ms hop (hop_length = 441 samples),
  * applies a final per-frame L2 normalization and a non-finite cleanup.

Parameters are sourced from the packaged feature configuration so that the config
and the code stay in sync. Output convention: a (n_features x n_frames) float array.
"""
from __future__ import annotations

from typing import Callable, Dict

import librosa
import numpy as np

from .audio_io import load_audio
from .utils import feature_registry

_EPS = 1e-8


def _frame_l2(x: np.ndarray) -> np.ndarray:
    """Per-frame (column) L2 normalization + non-finite cleanup."""
    norms = np.linalg.norm(x, axis=0, keepdims=True)
    norms = np.maximum(norms, _EPS)
    x = x / norms
    if np.any(~np.isfinite(x)):
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return x


def _params(name: str) -> Dict:
    reg = feature_registry()
    feats = reg["features"]
    if name not in feats:
        raise ValueError(
            f"Unsupported feature {name!r}. Supported: {sorted(feats)}"
        )
    return feats[name]


def _hop_length() -> int:
    return int(feature_registry()["global"]["hop_length"])


def _sample_rate() -> int:
    return int(feature_registry()["global"]["sample_rate"])


# --------------------------------------------------------------------------- #
# Individual extractors (one per registry feature name).
# --------------------------------------------------------------------------- #
def _extract_tempogram(y: np.ndarray, sr: int, hop: int, p: Dict) -> np.ndarray:
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tg = librosa.feature.tempogram(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop,
        win_length=int(p["win_length"]),
    )
    tg = np.log1p(tg)
    return _frame_l2(tg)


def _extract_chroma_cens(y: np.ndarray, sr: int, hop: int, p: Dict) -> np.ndarray:
    tuning = librosa.estimate_tuning(y=y, sr=sr) if p.get("use_tuning", True) else 0.0
    cens = librosa.feature.chroma_cens(
        y=y,
        sr=sr,
        hop_length=hop,
        n_chroma=int(p["n_chroma"]),
        tuning=tuning,
        win_len_smooth=int(p["win_len_smooth"]),
    )
    return _frame_l2(cens)


def _extract_chroma(y: np.ndarray, sr: int, hop: int, p: Dict) -> np.ndarray:
    tuning = librosa.estimate_tuning(y=y, sr=sr) if p.get("use_tuning", True) else 0.0
    chroma = librosa.feature.chroma_cqt(
        y=y,
        sr=sr,
        hop_length=hop,
        n_chroma=int(p["n_chroma"]),
        tuning=tuning,
        norm=p.get("norm", 2),
    )
    return _frame_l2(chroma)


def _extract_mfcc(y: np.ndarray, sr: int, hop: int, p: Dict) -> np.ndarray:
    fmax = p.get("fmax")
    if fmax is None:
        fmax = sr / 2.0
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_fft=int(p["n_fft"]),
        hop_length=hop,
        n_mfcc=int(p["n_mfcc"]),
        n_mels=int(p["n_mels"]),
        fmin=float(p.get("fmin", 0.0)),
        fmax=float(fmax),
    )
    stack = [mfcc]
    if p.get("use_delta", True):
        stack.append(librosa.feature.delta(mfcc))
    if p.get("use_delta2", False):
        stack.append(librosa.feature.delta(mfcc, order=2))
    if len(stack) > 1:
        mfcc = np.vstack(stack)
    return _frame_l2(mfcc)


_EXTRACTORS: Dict[str, Callable[[np.ndarray, int, int, Dict], np.ndarray]] = {
    "tempogram": _extract_tempogram,
    "chroma_cens": _extract_chroma_cens,
    "chroma": _extract_chroma,
    "mfcc": _extract_mfcc,
}


def extract_features(audio_path: str, feature: str) -> np.ndarray:
    """Extract a (n_features x n_frames) feature matrix for ``feature``.

    Args:
        audio_path: Path to an audio file.
        feature: One of the registry feature names (e.g. ``"mfcc"``).

    Returns:
        float32 array of shape (n_features, n_frames), per-frame L2 normalized.
    """
    if feature not in _EXTRACTORS:
        raise ValueError(
            f"Unsupported feature {feature!r}. Implemented: {sorted(_EXTRACTORS)}"
        )
    p = _params(feature)["feature_specific_parameters"]
    sr = _sample_rate()
    hop = _hop_length()
    y = load_audio(audio_path, sr=sr)
    feats = _EXTRACTORS[feature](y, sr, hop, p or {})
    return np.ascontiguousarray(feats, dtype=np.float32)


def available_features() -> list[str]:
    """Feature names with a working extractor implementation."""
    return sorted(_EXTRACTORS)
