# Data Collection Pipeline

End-to-end flow from a performance recording to a system-level human-evaluation
score.

```
ATEPP performance audio (reference, .flac)
        │
        ▼
AMT model transcription  ──►  MIDI
   (aria_amt, bytedance_piano, transkun, ismir2021,
    ismir2022_base, ismir2022_small, mt3, basic_pitch_new)
        │
        ▼
MIDI → score (symbolic) conversion
   (MIDI2ScoreTransformer | musescore | music21)
        │
        ▼
Score → audio rendering  ──►  candidate WAV
   (rendered with the SGM SoundFont)
        │
        ├──────────────► Audio-level evaluation (Component A)
        │                 reference.flac vs candidate.wav → DTW / TWED score
        │
        ▼
Listening comparison task (Component B)
   reference + candidate A + candidate B → forced choice (A/B) + confidence
        │
        ▼
Sanitized preference judgments  (data/public/)
        │
        ▼
System-level human-evaluation scores
   (Bradley–Terry and 5 other methods → data/public/system_scores.csv)
```

## Pipeline details

| Step | Description |
|---|---|
| Reference | ATEPP performance recordings (Zhang et al., ISMIR 2022; github.com/BetsyTang/ATEPP) |
| 3-minute test set | ATEPP test split, ASAP overlaps excluded (avoids leakage for ASAP-trained models), filtered to duration < 180 s → 230 clips / 28 pieces |
| Systems | 8 AMT models × 3 MIDI→score converters = 24 pipelines |
| Rendering | each generated score rendered to audio with the SGM SoundFont |
| Excerpts | 230 reference excerpts |
| Listening task | reference-anchored forced choice (A/B) with confidence and playback counts |
| Scoring | Bradley–Terry (headline) and five other ranking methods |
