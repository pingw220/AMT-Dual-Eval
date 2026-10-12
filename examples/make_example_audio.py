#!/usr/bin/env python3
"""Generate the synthetic example audio pair under examples/audio/.

These files are SYNTHETIC (simple additive-synthesis piano-like tones) and are
generated here, not taken from any dataset — so they are safe to redistribute.
They are only for demonstrating the CLI; they are NOT ATEPP audio and do not
reproduce any paper number. (Real reference/rendered audio is not redistributed;
see ETHICS_AND_DATA_GOVERNANCE.md.)

  * reference.wav  — a short C-major arpeggio "performance".
  * candidate.wav  — a "transcription" of the same arpeggio with realistic errors:
                     onset jitter, slightly altered note durations, and one wrong
                     pitch (a semitone off). It is close to, but not identical to,
                     the reference, so DTW/TWED return a small positive distance.

Run:  python examples/make_example_audio.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

SR = 44100
OUT = Path(__file__).resolve().parent / "audio"


def note(freq: float, dur: float, sr: int = SR) -> np.ndarray:
    """A simple piano-like note: a few harmonics with an exponential decay."""
    t = np.linspace(0.0, dur, int(sr * dur), endpoint=False)
    env = np.exp(-3.5 * t)
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.5 * np.sin(2 * np.pi * 2 * freq * t)
           + 0.25 * np.sin(2 * np.pi * 3 * freq * t))
    return (0.2 * env * sig).astype(np.float32)


def render(sequence, sr: int = SR) -> np.ndarray:
    """Concatenate (freq, duration, gap) notes into one waveform."""
    chunks = []
    for freq, dur, gap in sequence:
        chunks.append(note(freq, dur, sr))
        if gap > 0:
            chunks.append(np.zeros(int(sr * gap), dtype=np.float32))
    return np.concatenate(chunks)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # C4, E4, G4, C5, G4, E4, C4
    C4, E4, G4, C5 = 261.63, 329.63, 392.00, 523.25
    Eb4 = 311.13  # the "wrong" note in the candidate (semitone below E4)

    reference = [
        (C4, 0.5, 0.05), (E4, 0.5, 0.05), (G4, 0.5, 0.05), (C5, 0.6, 0.10),
        (G4, 0.5, 0.05), (E4, 0.5, 0.05), (C4, 0.7, 0.00),
    ]
    # Transcription errors: jittered onsets/durations + E4 -> Eb4 on the 2nd note.
    candidate = [
        (C4, 0.55, 0.03), (Eb4, 0.45, 0.07), (G4, 0.50, 0.06), (C5, 0.55, 0.12),
        (G4, 0.52, 0.04), (E4, 0.48, 0.06), (C4, 0.66, 0.00),
    ]

    sf.write(OUT / "reference.wav", render(reference), SR)
    sf.write(OUT / "candidate.wav", render(candidate), SR)
    print(f"Wrote {OUT/'reference.wav'} and {OUT/'candidate.wav'}")


if __name__ == "__main__":
    main()
