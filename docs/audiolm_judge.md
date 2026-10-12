# Audio-Language Model (AudioLM) Judges

As a **supplementary** automated evaluator for the rendered-audio dimension, we test
whether audio-language models can perform the same pairwise listening comparison as
human raters. They are highly effective but computationally expensive, so they
complement — rather than replace — the DTW/TWED metrics.

## Task format (same as the human ABX test)

Each request shows the model a **reference** clip and two candidate renderings
(**A** and **B**), and asks it to choose the candidate whose musical content is
closer to the reference. The exact prompt is in the packaged
`audiolm_judge_prompt.txt` configuration:

```text
Reference: [audio link/file]
Candidate A: [audio link/file]
Candidate B: [audio link/file]

Please compare Candidate A and Candidate B relative to Reference
based on musical content similarity (pitch, onset, duration).
You must choose exactly one option: "A" or "B" (no Tie).
Output format: reply with a single character, either A or B.
Do not provide explanation or any extra text.
```

The three `[audio link/file]` placeholders are replaced by the actual audio
attachments (reference, candidate A, candidate B) sent with the request. The forced
single-character `A`/`B` output is parsed into a binary win, exactly like the human
forced choice, so the same six ranking methods (Bradley–Terry, etc.) apply.

## Run configuration

| Setting | Value |
|---|---|
| Providers/models | Gemini family (e.g. 2.0 flash-lite, 2.5 flash, 2.5 pro, 3 pro, 3.1 pro) |
| Decoding | `temperature = 0.0` (deterministic), `seed = 1234` |
| Pairs per run | 1800; `max_retries = 3`, `timeout = 180 s` |
| Reference anchoring | reference truncated to short anchored windows (≈10 s; `anchor_id`, `anchor_fraction`), with candidates rendered to matching windows |
| Output | single character `A`/`B`, parsed to a binary preference |

## Result

The best AudioLM judge (Gemini 3 Pro) reaches **Spearman ≈ 0.963** with the human
consensus system ranking — higher than the best TWED feature (≈ 0.922) and the best
DTW feature (≈ 0.889). This shows AudioLMs are strong, scalable proxies for the human
listening test, at materially higher compute/API cost.

## Status in this repository

The AudioLM judge is **not bundled** here: it requires model/API access and the
anchored reference/candidate audio (not redistributed). This document and the prompt
config record the exact protocol so it can be reproduced. To run it, send the prompt
above with the three audio attachments to the model, parse the `A`/`B` response, and
score the resulting forced-choice judgments with `amt_dual_eval.human_eval`.
