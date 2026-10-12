# Data

`public/` holds the sanitized human-evaluation release. Every file and column is
documented in [../DATA_DICTIONARY.md](../DATA_DICTIONARY.md); the governance terms
are in [../ETHICS_AND_DATA_GOVERNANCE.md](../ETHICS_AND_DATA_GOVERNANCE.md).

## Contents of `public/`

- `atepp_3min_test_set.csv` — clean 3-minute ATEPP test manifest (230 clips / 28
  pieces; under-180 s subset). ATEPP-relative paths only; audio/scores not bundled.
- `system_scores.csv` — system-level human-evaluation scores (6 methods).
- `aggregate_pairwise_results.csv` — per system-pair win counts and preference rates.
- `trials_public.csv` — de-identified comparison design metadata.
- `participant_summary_aggregate.csv` — aggregate counts and demographic distributions.
- `participant_background_summary.csv` — proficiency level and binned years-of-training
  counts (for the appendix table).
- `proficiency_training_crosstab.csv` — proficiency x years-of-training joint counts
  (training-year breakdown for Music major / Amateur, separately and combined).
- `responses_public.csv` — de-identified per-judgment response-level data
  (surrogate IDs only; see the ethics document).
- `cost_benchmark_summary.csv` — DTW/TWED cost-benchmark results (see
  [../docs/evaluation_cost_report.md](../docs/evaluation_cost_report.md)).
- `cloud_cpu_price_assumption.csv` — cloud CPU price used for the cost estimate.

## Not included

Raw exports, participant records, gift-card/compensation data, reference/rendered
audio, and model outputs are **not** in this repository.
