# Audio Metric Usage (DTW & TWED)

## What is measured

Given a **reference** performance recording and a **candidate** audio rendering of
a system's transcription, the tool extracts a time series of audio features from
each and computes an alignment-based distance. **Lower = more similar**; identical
audio scores ≈ 0.

## Features

All features use sr=44100 Hz (mono), 10 ms hop (hop_length=441), and a final
per-frame L2 normalization. They are defined centrally in the packaged
`feature_registry.yaml` configuration.

| Feature | What it captures | In DTW top-3 | In TWED top-3 |
|---|---|---|---|
| `tempogram` | Rhythmic/periodic structure (log1p autocorrelation tempogram, win=384) | ✅ (best) | ✅ |
| `chroma_cens` | Smoothed, octave-invariant harmony (CENS, win_len_smooth=41) | ✅ | ✅ |
| `chroma` | Octave-invariant pitch-class content (CQT chroma, 12 bins) | ✅ | — |
| `mfcc` | Timbre (20 MFCC + delta = 40-d) | — | ✅ (best) |

The top-3 sets were selected by correlating each feature's metric system-ranking
with the human consensus ranking (Spearman). DTW and TWED top-3 **differ**: they
share `tempogram` and `chroma_cens`; DTW adds `chroma`, TWED adds `mfcc`. `mfcc` is
the best TWED feature but the worst DTW feature. Defaults: DTW → `tempogram`,
TWED → `mfcc`.

## DTW

Cosine cost matrix over feature frames (`scipy.cdist`), standard symmetric DTW
accumulation, score `= total_cost / path_length`. Defaults are in the packaged
`dtw_default.yaml` configuration.

```bash
python -m amt_dual_eval.cli audio-score --metric dtw --feature tempogram \
  --reference ref.wav --candidate cand.wav
# -> dtw_score: <number>   (lower = more similar)
```

## TWED

Marteau Time-Warp Edit Distance: euclidean distance on L2-normalized frames, time
stamps = frame indices, match term `d(i,j)+d(i-1,j-1)`, deletion penalty
`||frame_i - frame_{i-1}||`, score `= total_cost / path_length`. Default
parameters: **`nu=0.001`, `lambda=2.0`**, defined in the packaged
`twed_default.yaml` configuration.

```bash
python -m amt_dual_eval.cli audio-score --metric twed --feature mfcc \
  --reference ref.wav --candidate cand.wav
# override hyperparameters:
python -m amt_dual_eval.cli audio-score --metric twed --feature mfcc \
  --reference ref.wav --candidate cand.wav --nu 0.01 --lambda-value 1.0
```

## Multi-feature and output formats

```bash
python -m amt_dual_eval.cli audio-score --metric twed --all-top3 \
  --reference ref.wav --candidate cand.wav \
  --output-format {text|json|csv} [--output-path out.csv]
```

`--all-top3` evaluates the verified top-3 features for the chosen metric and prints
a readable table (or JSON/CSV). To reproduce the paper experiment, use the default
features and (for TWED) the default `nu`/`lambda`.

## Score interpretation

The number is an alignment-normalized distance in feature space. It is comparable
across candidates for a **fixed** feature and metric (the experiments rank systems
by mean score across the 230 excerpts). It is not calibrated across different
features. Lower means the rendered transcription is acoustically closer to the
reference performance.
