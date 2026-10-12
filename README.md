# AMT-Dual-Eval: Dual Evaluation of Automatic Music Transcription Systems

[![arXiv](https://img.shields.io/badge/arXiv-2608.04511-b31b1b.svg)](https://arxiv.org/abs/2608.04511)

Code and data for the paper [**A Dual Evaluation for Music Transcription**](https://arxiv.org/abs/2608.04511)
(Ping Wang, Guang Yang, Nazif Can Tamer, Victoria Ebert, Noah A. Smith; arXiv:2608.04511, 2026).

AMT-Dual-Eval evaluates **audio-to-score** transcription systems — pipelines that
take an audio recording and produce a symbolic score (MusicXML). We argue such
systems must be assessed along **two complementary dimensions of faithfulness**:

1. **Symbolic score faithfulness** — how close the generated score is to the
   ground-truth score, measured with **OMR-NED** (a normalized notation edit
   distance, computed with [musicdiff](https://github.com/gregchapman-dev/musicdiff));
   and
2. **Rendered-audio faithfulness** — how close the audio rendered from the generated
   score is to the original recording, measured with **DTW** and **TWED** over
   musical audio features.

To validate the audio-level metrics, we collected a human perceptual gold standard
via an **ABX-style listening test**, confirming that the chosen DTW/TWED metrics
correlate highly with human judgment.

**This repository releases the rendered-audio dimension (DTW/TWED) and the
human-evaluation study that validates it.** The score-level dimension (OMR-NED via
`musicdiff`) is described under [Score-level faithfulness](#score-level-faithfulness-omr-ned--musicdiff).
The packaged default configurations define the released evaluation protocol; see
[docs/audio_metric_usage.md](docs/audio_metric_usage.md) for the settings.

> **Lower DTW/TWED score = more similar audio.** A signal compared with itself
> yields a score of ≈ 0.

---

## Repository contents

- **Component A — audio metrics** ([src/amt_dual_eval/](src/amt_dual_eval/)):
  a reproducible DTW/TWED audio-comparison tool with a CLI; defaults are defined in
  the packaged configuration files.
- **Component B — human-evaluation release** ([data/public/](data/public/),
  [scripts/](scripts/)): a sanitized, de-identified version of the listening-study
  results plus scripts that reproduce the system rankings.
- **Documentation** ([docs/](docs/)) and **governance**
  ([ETHICS_AND_DATA_GOVERNANCE.md](ETHICS_AND_DATA_GOVERNANCE.md),
  [DATA_DICTIONARY.md](DATA_DICTIONARY.md)).

No raw experiment dumps, participant identifiers, compensation/gift-card records,
or private paths are included. See the ethics statement below.

### Released public data (`data/public/`)

- `responses_public.csv` — de-identified per-judgment response-level data
- `system_scores.csv` — system-level human-evaluation scores (six methods)
- `aggregate_pairwise_results.csv` — per system-pair win counts and preference rates
- `trials_public.csv` — de-identified comparison design metadata
- `participant_summary_aggregate.csv` — aggregate counts and demographic distributions
- `participant_background_summary.csv` — proficiency and years-of-training counts
- `proficiency_training_crosstab.csv` — proficiency × years-of-training joint counts
- `atepp_3min_test_set.csv` — clean 3-minute ATEPP test-set manifest

---

## Quick start: DTW / TWED audio scoring

```bash
pip install -e .
```

Score one reference/candidate pair (DTW, default feature `tempogram`):

```bash
python -m amt_dual_eval.cli audio-score \
  --metric dtw \
  --feature tempogram \
  --reference path/to/reference.wav \
  --candidate path/to/transcribed_rendered.wav
```

Score with TWED (default feature `mfcc`, default `nu=0.001`, `lambda=2.0`):

```bash
python -m amt_dual_eval.cli audio-score \
  --metric twed \
  --feature mfcc \
  --reference path/to/reference.wav \
  --candidate path/to/transcribed_rendered.wav
```

Score across all verified top-3 features:

```bash
python -m amt_dual_eval.cli audio-score \
  --metric twed --all-top3 \
  --reference path/to/reference.wav \
  --candidate path/to/transcribed_rendered.wav \
  --output-format csv --output-path results.csv
```

Override TWED hyperparameters:

```bash
python -m amt_dual_eval.cli audio-score --metric twed --feature mfcc \
  --reference ref.wav --candidate cand.wav --lambda-value 1.0 --nu 0.01
```

A console entry point `amt-dual-eval audio-score …` is also installed.

### Verified settings (recovered from prior experiments)

| Item | Value |
|---|---|
| Sample rate / channels | 44100 Hz, mono |
| Hop | 10 ms (hop_length = 441) |
| Per-frame normalization | L2 |
| **DTW** distance / aggregation | cosine / `total_cost / path_length` |
| **DTW** default feature | `tempogram` |
| **DTW** top-3 features | `tempogram`, `chroma_cens`, `chroma` |
| **TWED** distance | euclidean on L2-normalized frames; time unit = frames |
| **TWED** best params | `nu = 0.001`, `lambda = 2.0` |
| **TWED** default feature | `mfcc` |
| **TWED** top-3 features | `mfcc`, `chroma_cens`, `tempogram` |
| Score direction | **lower = more similar** |

The DTW and TWED top-3 sets **differ**: they share `chroma_cens` and `tempogram`;
`mfcc` is the best TWED feature but the worst DTW feature. See
[docs/audio_metric_usage.md](docs/audio_metric_usage.md) for what each feature
represents and why these were selected.

---

## Human evaluation dataset summary

All numbers below are computed from the sanitized release
(`data/public/participant_summary_aggregate.csv`).

| Quantity | Value |
|---|---|
| Completed participants | 106 |
| Retained after quality filtering | 106 (no exclusions applied in this set) |
| Valid forced-choice judgments | 3180 |
| Trials per participant | 30 |
| AMT systems evaluated | 24 (8 models × 3 converters) |
| Reference excerpts | 230 |
| Distinct system comparisons | 276 (= C(24,2), all pairs) |
| Attention trials | 0 (in this completed set) |
| Anchor trials | 0 (in this completed set) |
| Human-score aggregation | system_rank, wilson_win_rate, pairwise_matrix, **bradley_terry**, least_squares, elo |
| Reference-audio source | ATEPP (real piano performances) |
| Candidate rendering | AMT → MIDI → converter → score → SGM SoundFont → WAV |

**Models:** `aria_amt`, `bytedance_piano`, `transkun`, `ismir2021`, `ismir2022_base`,
`ismir2022_small`, `mt3`, `basic_pitch_new`.
**Converters:** `MIDI2ScoreTransformer`, `musescore`, `music21`.

### System ranking (Bradley–Terry; from `data/public/system_scores.csv`)

| Rank | System | BT score | # judgments |
|---|---|---|---|
| 1 | aria_amt+musescore | 1.8907 | 266 |
| 2 | bytedance_piano+musescore | 1.5421 | 274 |
| 3 | transkun+musescore | 1.4451 | 259 |
| 4 | ismir2021+musescore | 1.2087 | 269 |
| 5 | ismir2022_small+musescore | 0.6326 | 268 |
| … | … | … | … |
| 22 | bytedance_piano+music21 | -1.0096 | 273 |
| 23 | transkun+music21 | -1.3852 | 281 |
| 24 | ismir2021+music21 | -1.7970 | 271 |

The `musescore` converter dominates and `music21` is consistently worst; the six
scoring methods agree almost perfectly (Spearman ≈ 0.999). Full table in
`data/public/system_scores.csv`.

---

## Human evaluation procedure

In each trial a participant heard a **reference** performance excerpt and two
**candidate** renderings, *A* and *B*, each produced by a different AMT pipeline for
the same excerpt. Candidates were presented left/right in randomized order
(`shown_left` recorded per response). The participant chose which candidate sounded
closer to the reference (`chosen_candidate_label ∈ {A, B}`) and reported a
confidence. Each judgment is a binary win for the chosen pipeline.

Final system scores are computed from these forced-choice outcomes by six methods,
of which **Bradley–Terry** is the headline. Only `A`/`B` responses are counted;
the completed set contains no attention or anchor trials. See
[docs/human_evaluation_protocol.md](docs/human_evaluation_protocol.md).

---

## Dataset provenance

- **Reference performances:** the **ATEPP** dataset of real expressive piano
  performances (Zhang et al., ISMIR 2022; <https://github.com/BetsyTang/ATEPP>).
  Each performance has a paired MusicXML score used as the symbolic ground truth.
- **Clean 3-minute test set (230 clips):** the audio-level evaluation used a curated
  subset of the ATEPP test split. Performances overlapping the **ASAP** dataset are
  **excluded** (several AMT models are trained on ASAP, so this avoids train/test
  leakage), non-two-staff scores are dropped (leaving 1495 entries), and the result is
  filtered to **duration < 180 s (3 minutes)**, yielding exactly **230 clips across
  28 pieces**. The clean, path-relative manifest is released as
  [`data/public/atepp_3min_test_set.csv`](data/public/atepp_3min_test_set.csv).
- **Systems:** 8 AMT models transcribe each performance to MIDI; 3 converters turn
  MIDI into a MusicXML score; the score is rendered to audio with the SGM SoundFont.
- **Released here:** the 3-minute test manifest, sanitized human-evaluation tables,
  and reproduction scripts.
- **Not redistributed:** reference/rendered audio, MusicXML scores, and model outputs
  (obtain ATEPP from its original release), raw platform exports, and participant
  records. These third-party artifacts are not covered by this repository's licenses
  and remain subject to their own licenses and terms of use.

See [docs/data_collection_pipeline.md](docs/data_collection_pipeline.md).

---

## Score-level faithfulness (OMR-NED / musicdiff)

Evaluating an audio-to-score system is not only a question of whether the rendered
audio sounds right — it also requires asking whether the generated **symbolic score**
(MusicXML) preserves the notated musical structure. We therefore frame audio-to-score
evaluation as a **two-dimensional** problem, assessing each system along two
complementary axes of faithfulness:

1. **Symbolic score faithfulness** — how close the generated MusicXML score is to the
   ground-truth score (notes, rhythms, rests, barlines, and other notation), measured
   with **OMR-NED**, a normalized edit distance over symbolic score representations.
2. **Rendered-audio faithfulness** — how close the audio rendered from the generated
   score is to the original reference recording (pitch, onset timing, duration, rhythm,
   overall musical continuity), measured with **DTW** and **TWED** (this repository).

These two dimensions are complementary, not redundant: a score can be symbolically
close to the ground truth yet sound different once rendered, and a score can contain
notation differences while still preserving most of the perceived musical content.

OMR-NED is computed with [**musicdiff**](https://github.com/gregchapman-dev/musicdiff)
(notation-aware diff/edit distance over MusicXML/MEI/Humdrum via `music21`): align the
two notations and normalize the edit cost by score length. It operates directly on the
MusicXML produced by the MIDI→score converters (`MIDI2ScoreTransformer` / `musescore` /
`music21`), so it needs no rendering step.

> The OMR-NED (score-level) dimension is documented here for completeness; this
> repository currently releases the **rendered-audio** dimension (DTW/TWED) and the
> human listening study that validates it. See `musicdiff` above to compute the
> score-level dimension over the converter MusicXML outputs.

---

## Supplementary: audio-language model (AudioLM) judges

Extending the rendered-audio dimension, we also test whether **audio-language models**
can perform the same pairwise listening comparison as human raters, as a scalable
(but computationally expensive) automated judge. Each request shows the model a
reference clip and two candidate renderings and asks it to pick the closer candidate,
using the exact prompt in
the packaged `audiolm_judge_prompt.txt` configuration. The forced
`A`/`B` output is parsed into a binary preference and scored with the same six methods.

The best AudioLM judge (Gemini 3 Pro) reaches **Spearman ≈ 0.963** with the human
consensus ranking — higher than the best TWED feature (≈ 0.922) and DTW feature
(≈ 0.889) — confirming AudioLMs are strong proxies for the listening test at higher
cost. This judge is **not bundled** (it needs model/API access and the anchored audio);
see [docs/audiolm_judge.md](docs/audiolm_judge.md) for the full protocol.

---

## Ethical release statement

The study **"Human Evaluation of Automatic Music Transcription Systems"** was reviewed
by the University of Washington Human Subjects Division (UW HSD). On **March 12, 2026**,
UW HSD determined that the study qualifies for **Exempt status, Category 2**, under
**IRB ID STUDY00025192**. The HSD determination letter is retained in private project
records and is **not redistributed** in this repository.

The public release includes de-identified response-level judgments. It excludes
direct identifiers, raw participant IDs, contact information, usernames, account IDs,
compensation/gift-card records, timestamps, private filesystem paths, private storage
URLs, raw platform exports, reference audio, rendered audio, MusicXML/MIDI outputs, and
third-party model outputs. See [ETHICS_AND_DATA_GOVERNANCE.md](ETHICS_AND_DATA_GOVERNANCE.md).

---

## Reproduction

```bash
# Score one audio pair with the released metrics (Component A)
python -m amt_dual_eval.cli audio-score --metric twed --all-top3 \
  --reference ref.wav --candidate cand.wav

# Reproduce the human-evaluation system rankings from the released responses
python scripts/reproduce_human_eval_results.py --method bradley_terry
python scripts/reproduce_human_eval_results.py --method all
```

The reproduced human rankings match `data/public/system_scores.csv`; Bradley–Terry
is the headline method (others: system rank, Wilson win rate, pairwise matrix, least
squares, Elo).

---

## Citation

If you use this repository, please cite the paper:

```bibtex
@article{wang2026dual,
  title         = {A Dual Evaluation for Music Transcription},
  author        = {Wang, Ping and Yang, Guang and Tamer, Nazif Can and Ebert, Victoria and Smith, Noah A.},
  journal       = {arXiv preprint arXiv:2608.04511},
  year          = {2026},
  eprint        = {2608.04511},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SD},
  doi           = {10.48550/arXiv.2608.04511},
  url           = {https://arxiv.org/abs/2608.04511},
}
```

To cite the software release specifically:

```bibtex
@software{amt_dual_eval,
  title  = {AMT-Dual-Eval: Dual Evaluation of Automatic Music Transcription Systems},
  author = {Wang, Ping and Smith, Noah A.},
  year   = {2026},
  url    = {https://github.com/pingw220/AMT-Dual-Eval},
}
```

A Zenodo DOI will be added after archival release.

## Use of generative AI

Generative AI tools were used to check grammar and wording in the documentation and
to assist with writing parts of the evaluation and analysis code in this repository.
They were not used to generate research ideas, to design the evaluation, or to
produce or interpret any result. All code was reviewed and tested by the authors, and
every number in the released tables comes from running this pipeline.

## License

Licensing is separated by artifact type:

- **Code:** MIT License — see [LICENSE](LICENSE).
- **Data** under `data/public/` (de-identified aggregate tables and response-level
  judgments): Creative Commons Attribution 4.0 International (CC BY 4.0), unless
  otherwise noted — see [DATA_LICENSE.md](DATA_LICENSE.md).
- **Reference audio, rendered audio, MusicXML/MIDI outputs, model outputs, and other
  third-party artifacts:** not redistributed and not covered by the repository's
  licenses; they remain subject to their own licenses and terms of use.
