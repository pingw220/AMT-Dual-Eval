# Human Evaluation Protocol

This describes the design of the human listening study whose de-identified results
are released in this repository.

## Task

A reference-anchored, two-alternative forced-choice (pairwise) listening test.
In each trial the participant could play:

- a **reference** excerpt — a real performance recording of a piano piece; and
- two **candidate** renderings, **A** and **B** — audio rendered from two different
  AMT pipelines' transcriptions of that same excerpt.

The participant selected the candidate that sounded **closer to the reference**
(`chosen_candidate_label ∈ {A, B}`) and reported a confidence. Playback counts for
the reference and each candidate were logged (`play_ref`, `play_left`, `play_right`).

## Presentation and assignment

- Candidates A and B were shown on the left/right; presentation order varied across
  listeners for the same trial (`shown_left` per response; `assignment_ui_seed`,
  `trial_seed` recorded), i.e. **left/right was randomized**.
- Each participant completed **30** trials; assignments were tracked via
  `assignment_order_index` / `assignment_completed`.
- Across the completed set, all **C(24,2) = 276** system pairs were compared over
  **230** reference excerpts.

## Systems

24 pipelines = 8 AMT models × 3 MIDI→score converters (see the packaged
`systems.yaml` configuration).

## Quality control

- Only `A`/`B` forced-choice responses are counted as valid judgments.
- The platform and analysis support attention and anchor trials
  (`trial_is_attention`, `trial_is_anchor`), excluded from scoring by default.
  **The released dataset contains zero attention/anchor trials.**
- No participant exclusions were applied to the completed set (106 completed →
  106 retained).

## Aggregation (system scores)

From the binary forced-choice outcomes, six methods produce system scores/ranks:

1. **system_rank** — direct win rate (wins / exposures).
2. **wilson_win_rate** — 95% Wilson lower bound on the win rate.
3. **pairwise_matrix** — mean per-opponent win rate.
4. **bradley_terry** — Bradley–Terry abilities via MM iteration (headline method).
5. **least_squares** — ridge-regularized pairwise skill (ridge=1.0).
6. **elo** — deterministic Elo over the observed order (base 1500, K=24).

The methods agree almost perfectly (Spearman ≈ 0.999; Elo slightly lower).
Reproduce with `scripts/reproduce_human_eval_results.py` (requires
`responses_public.csv`); system-level results are in `data/public/system_scores.csv`.
