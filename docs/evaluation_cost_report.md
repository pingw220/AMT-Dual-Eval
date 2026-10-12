# Evaluation Cost Report

This report compares the cost of the three evaluators used in AMT-Dual-Eval on
different, non-interchangeable axes:

- **DTW/TWED** — compute cost measured in CPU core-hours and peak RAM; cloud-equivalent
  cost estimated from public CPU pricing.
- **Gemini/AudioLM** — API cost measured in requests and token/audio usage.
- **Human ABX** — labor cost measured in participant judgments and compensation.

Benchmark/metric settings were recovered from the original local experiment
logs/configuration: 44.1 kHz mono audio, 10 ms hop, path-normalized DTW/TWED scores,
and the released top-feature configurations.

## Benchmark conditions

- Hardware: AMD EPYC 9534 (x86-64), Linux; single-threaded
  (`OMP_NUM_THREADS=OPENBLAS=MKL=NUMEXPR=VECLIB=1`).
- **DTW/TWED were run on CPU only; no GPU was used** (`gpu_used = false`).
- Each pair-metric-feature evaluation ran in its own subprocess so peak RSS reflects a
  single evaluation. Sampled pairs span the `<=60s` and `<=120s` duration bins; the full
  test set extends to ≈180 s, so wall-clock estimates for the longest clips are
  conservative (longer pairs cost more, quadratically).
- A single-feature full evaluation = 230 reference clips × 24 systems = **5,520** pairs;
  top-3 = **16,560** pair-feature evaluations.
- Cloud-equivalent price: Google Cloud `c3-highcpu-4`, us-central1, 4 vCPU / 8 GB,
  $0.1701/hour on-demand = **$0.042525 per vCPU-hour** (accessed 2026-06-06; see
  `data/public/cloud_cpu_price_assumption.csv`). DTW/TWED actually ran on institutional
  CPU resources at **$0 direct cost**; the cloud figure is a comparison only.

## DTW/TWED measured cost (scaled to the full evaluation)

Per-pair means are pooled over the sampled bins; full-run estimates are serial.

| Metric | Feature | dim | s/pair | peak RAM (GB) | pairs/hour | full CPU core-h (5,520) | cloud-equiv (5,520) |
|---|---|---|---|---|---|---|---|
| DTW | tempogram (default) | 384 | 83.3 | 0.95 | 43.2 | 79.1 | $3.37 |
| DTW | chroma_cens | 12 | 147.3 | 6.77 | 24.4 | 161.2 | $6.86 |
| DTW | chroma | 12 | 155.5 | 6.77 | 23.1 | 158.2 | $6.73 |
| DTW | mfcc | 40 | 62.1 | 0.57 | 58.0 | 63.3 | $2.69 |
| DTW | **top-3** (tempogram+chroma_cens+chroma) | — | 386.1 | 6.77 | 9.3 | 398.6 | **$16.95** |
| TWED | mfcc (default) | 40 | 223.5 | 0.28 | 16.1 | 229.0 | $9.74 |
| TWED | chroma_cens | 12 | 318.7 | 6.77 | 11.3 | 319.4 | $13.58 |
| TWED | chroma | 12 | 287.2 | 6.77 | 12.5 | 317.3 | $13.49 |
| TWED | tempogram | 384 | 311.2 | 0.34 | 11.6 | 265.4 | $11.29 |
| TWED | **top-3** (mfcc+chroma_cens+tempogram) | — | 853.4 | 6.77 | 4.2 | 813.8 | **$34.61** |

Notes:
- TWED peak RAM stays ≈0.3 GB even for the longest sampled clips (rolling-row DP); the
  high-RAM rows (≈6.8 GB) come from DTW's dense cost matrix plus CQT-based feature
  extraction (chroma / chroma_cens). For DTW the dense matrix alone needs ≈
  frames_ref × frames_candidate × 8 bytes.
- Time ranking was measured, not assumed: for DTW, `mfcc` (40-d) was fastest and
  `chroma`/`chroma_cens` (12-d, CQT-based) slowest; feature dimension alone does not
  predict runtime.
- Full per-(metric, feature, duration_bin) statistics: `data/public/cost_benchmark_summary.csv`.

## Human ABX cost

- Participants: **106**; valid ABX judgments: **3,180**.
- Compensation: **$10 per participant → 106 × $10 = $1,060** direct participant
  compensation.
- Platform/recruitment/administrative fees: **not included** (not available here).

## Gemini/AudioLM cost

- Human-matched judge model: **Gemini 3 Pro** (`gemini-3-pro-preview`).
- ABX requests: **≈1,800** (same reference-anchored A/B format as the human study).
- Token/audio usage (logged totals): **≈187,200** input text tokens, **≈2,145,916**
  audio-input tokens (≈32 tokens/audio-second), **≈18,617** output text tokens.
- Direct monetary cost under the access used: **$0** (preview tier).
- **Paid-equivalent (Gemini 3 Pro list pricing):** $2.00 / 1M input text and
  $12.00 / 1M output (≤200K context). The Gemini 3 Pro Preview audio-input price is
  not officially published, so audio is priced as a range — at the text-input rate
  ($2/1M) to 2× ($4/1M):
  - On-demand: **≈$4.89 to ≈$9.18** total (≈$2.72–$5.10 per 1,000 requests).
  - Batch mode (50% off): **≈$2.44 to ≈$4.59**.
  - Pricing accessed 2026-06-06; the official preview price is listed as
    "not available", so these use third-party-reported Gemini 3 Pro list rates.

## Cross-evaluator comparison

The three evaluators are run very differently, so absolute totals are not directly
comparable: **DTW/TWED exhaustively score every system–clip pair** (deterministic, full
coverage), whereas **AudioLM and Human use sampled pairwise ABX judgments**. The last
column normalizes cost to a common per-unit basis (USD per 1,000 evaluation units) for
a *relative* comparison — note the unit itself differs (an audio-pair score vs. an ABX
judgment), so it is indicative, not like-for-like.

| Evaluator | Evaluation unit | # units | Direct monetary cost | CPU/API/labor cost unit | Peak memory / infra | Cloud-/paid-equivalent total | **Normalized (USD / 1,000 units)** |
|---|---|---|---|---|---|---|---|
| DTW single feature (default `tempogram`) | audio pair | 5,520 | $0 (institutional CPU) | 79.1 CPU core-h | ≈0.95 GB | ≈$3.37 cloud-equiv | **≈$0.61** |
| DTW top-3 | pair-feature | 16,560 | $0 (institutional CPU) | 398.6 CPU core-h | ≈6.8 GB | ≈$16.95 cloud-equiv | **≈$1.02** |
| TWED single feature (default `mfcc`) | audio pair | 5,520 | $0 (institutional CPU) | 229.0 CPU core-h | ≈0.28 GB | ≈$9.74 cloud-equiv | **≈$1.76** |
| TWED top-3 | pair-feature | 16,560 | $0 (institutional CPU) | 813.8 CPU core-h | ≈6.8 GB | ≈$34.61 cloud-equiv | **≈$2.09** |
| Gemini/AudioLM ABX (Gemini 3 Pro) | request | ≈1,800 | $0 (preview access) | ≈187k text-in + ≈2.15M audio-in + ≈18.6k out tokens | model API | ≈$4.89–$9.18 on-demand (≈$2.44–$4.59 batch) | **≈$2.72–$5.10** |
| Human ABX | judgment | 3,180 (106 participants) | $1,060 | $10 / participant | — | $1,060 | **≈$333.33** |

Serial CPU core-hours are at one core; running across allocated cores divides wall-clock
time roughly proportionally while CPU core-hours stay similar.

## Summary

Per evaluation unit, **human evaluation is ≈2 orders of magnitude more expensive**
(≈$333 / 1,000 judgments) than either automated method. The **AudioLM judge (Gemini 3
Pro)** costs roughly **$5–$9 on-demand** (≈$2.7–$5.1 / 1,000 requests) in real paid API
spend, while the released top-3 audio metrics cost **$0 direct** on institutional CPU
(≈$17 DTW / ≈$35 TWED cloud-equivalent for the full 16,560 pair-feature evaluation;
≈$0.6–$2.1 / 1,000 units). DTW is cheapest per unit, TWED is in between (≈2–4× slower
per pair than DTW but far lower memory), and the audio metrics additionally cover all
5,520 pairs exhaustively rather than a sampled subset.

The benchmarking and cost-estimation scripts are maintained in the authors' private
project records and are not part of this release; this report and the accompanying
`data/public/cost_benchmark_summary.csv` and `data/public/cloud_cpu_price_assumption.csv`
contain the released results.
