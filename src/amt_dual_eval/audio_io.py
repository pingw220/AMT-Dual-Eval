"""Audio loading for AMT-Dual-Eval.

Loads audio with ``librosa.load(path, sr=sr)``, which resamples to the target
sample rate and downmixes to mono. The default sample rate (44100 Hz) is read
from the global section of the packaged feature configuration.
"""
from __future__ import annotations

from typing import Optional

import librosa
import numpy as np

from .utils import feature_registry


def default_sample_rate() -> int:
    return int(feature_registry()["global"]["sample_rate"])


def load_audio(audio_path: str, sr: Optional[int] = None) -> np.ndarray:
    """Load an audio file as a mono waveform at ``sr`` Hz.

    Args:
        audio_path: Path to an audio file (wav, flac, mp3, ... anything libsndfile/
            audioread can read).
        sr: Target sample rate. Defaults to the registry sample rate (44100).

    Returns:
        1-D float32 waveform.

    Raises:
        FileNotFoundError / RuntimeError on unreadable input (propagated from librosa).
    """
    if sr is None:
        sr = default_sample_rate()
    y, _ = librosa.load(audio_path, sr=sr)
    return np.asarray(y, dtype=np.float32)
