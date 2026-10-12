# Data Dictionary

Documents every released CSV in `data/public/`. "Derived" = computed during
sanitization; "Aggregated" = no row maps to a single participant. No column
contains direct identifiers, contact details, timestamps, consent, or
compensation information.

---

## `atepp_3min_test_set.csv` (dataset manifest)

The clean 3-minute ATEPP test set (230 clips, 28 pieces): the under-180 s subset of
the ATEPP test split used for audio-level evaluation. Paths are ATEPP-relative (no
private cluster paths); the audio/scores themselves are not redistributed.

| Column | Type | Description | Derived? |
|---|---|---|---|
| `clip_id` | str | ATEPP performance id (e.g. `atepp__Bach_450__Gould__…`) | raw key |
| `source` | str | Dataset name (`atepp`) | raw |
| `audio_relpath` | str | Audio path relative to the ATEPP root (`audio/<clip_id>.flac`) | derived |
| `score_relpath` | str | MusicXML score path relative to the ATEPP root | derived |
| `duration_sec` | float | Performance duration in seconds (< 180) | raw |

## `system_scores.csv` (aggregated)

Human-evaluation system-level scores used in the paper. One row per (system, method).

| Column | Type | Description | Allowed values | Derived? |
|---|---|---|---|---|
| `system` | str | Pipeline name `<model>+<converter>` | 24 pipelines (see the packaged systems config) | derived |
| `system_abbreviation` | str | Short label (equals `system` here) | — | derived |
| `scoring_method` | str | Ranking method | system_rank, wilson_win_rate, pairwise_matrix, bradley_terry, least_squares, elo | derived |
| `score` | float | Method score (higher = better) | real | derived/aggregated |
| `rank` | int | Rank within the method (1 = best) | 1–24 | derived |
| `num_judgments` | int | Forced-choice judgments involving the system | ≥0 | derived/aggregated |

## `aggregate_pairwise_results.csv` (aggregated)

One row per unordered system pair that was compared.

| Column | Type | Description | Derived? |
|---|---|---|---|
| `system_a`, `system_b` | str | The two pipelines (a < b lexicographically) | derived |
| `num_valid_judgments` | int | Forced-choice judgments for this pair | aggregated |
| `wins_a`, `wins_b` | int | Times each system was chosen | aggregated |
| `preference_rate_a`, `preference_rate_b` | float | Wins / total for each (sum to 1) | aggregated |

## `trials_public.csv` (design metadata; aggregated)

One row per distinct comparison design tuple `(excerpt, system_a, system_b)`.
Contains no participant information and no file paths.

| Column | Type | Description | Derived? |
|---|---|---|---|
| `trial_public_id` | str | Surrogate id `trial_NNNN` | derived |
| `excerpt_id` | str | Surrogate excerpt id `excerpt_NNNN` | derived |
| `reference_source` | str | Reference dataset name (`ATEPP`) | constant |
| `system_a`, `system_b` | str | Compared pipelines | derived |
| `left_right_randomized` | bool | True if left/right presentation varied across listeners | derived |
| `is_attention_trial`, `is_anchor_trial` | bool | Trial-type flags (all False in this set) | derived |

## `participant_summary_aggregate.csv` (aggregated)

Non-identifying summary statistics and demographic distributions (counts only).

| Column | Type | Description |
|---|---|---|
| `statistic` | str | Statistic name (e.g. `completed_participants`, `proficiency__amateur`) |
| `value` | str/num | Value (count or label) |

Demographic rows are aggregate **counts per category** (proficiency, listening
device, years of musical training); no individual record is exposed.

## `participant_background_summary.csv` (aggregated)

Music-background counts for the appendix table, derived from the human-evaluation
responses. Reports the self-reported proficiency level
(`No experience` / `Amateur` / `Music major`) and binned years of music training.

| Column | Type | Description | Derived? |
|---|---|---|---|
| `category` | str | `Proficiency level` or `Years of music training` | derived/aggregated |
| `group` | str | Category bin (e.g. `Amateur`, `4--7 years`, `Missing / prefer not to answer`) | derived/aggregated |
| `count` | int | Number of completed participants in the bin | aggregated |

## `proficiency_training_crosstab.csv` (aggregated)

Joint distribution of self-reported proficiency level x binned years of music
training, used for the cross-tab appendix table (Music major / Amateur, separately
and combined).

| Column | Type | Description | Derived? |
|---|---|---|---|
| `proficiency` | str | `no_experience`, `amateur`, or `music_major` | aggregated |
| `training_year_bin` | str | `0 years`, `1--3 years`, `4--7 years`, `8--10 years`, `More than 10 years`, or `Missing / prefer not to answer` | aggregated |
| `count` | int | Number of completed participants in that (proficiency, bin) cell | aggregated |

## `responses_public.csv` (response-level)

De-identified per-judgment rows, one row per forced-choice judgment.

Notes:
- `listener_id` is a surrogate ID and is not the original participant ID.
- The raw-to-surrogate mapping is not released.
- No timestamps, contact fields, compensation fields, usernames, account IDs,
  platform IDs, or raw identifiers are included.

| Column | Type | Description | Kind | Allowed values |
|---|---|---|---|---|
| `listener_id` | str | De-identified listener | surrogate | `listener_####` |
| `trial_public_id` | str | De-identified trial (excerpt × system pair) | surrogate | `trial_####` |
| `excerpt_id` | str | De-identified reference excerpt | surrogate | `excerpt_####` |
| `system_a`, `system_b` | str | Compared pipelines | derived | one of 24 system names |
| `choice` | str | Chosen candidate | raw (de-identified) | `A` or `B` |
| `chosen_system`, `non_chosen_system` | str | Chosen / not-chosen pipeline | derived | one of 24 system names |
| `shown_left_system` | str | Pipeline shown on the left | derived | one of 24 system names |
| `confidence` | num | Self-reported confidence | raw (de-identified) | numeric |
| `play_reference_count`, `play_left_count`, `play_right_count` | int | Playback counts | raw (de-identified) | ≥0 |
| `is_attention_trial`, `is_anchor_trial` | bool | Trial-type flags | derived | true/false |
