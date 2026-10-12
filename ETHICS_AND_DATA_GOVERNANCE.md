# Ethics and Data Governance

## Raw sources used privately (NOT in this repository)

The sanitized release was produced from private inputs that are **never** committed:

- The joined human-evaluation responses export (the only file read by the build
  script), which itself originated from a study-platform export.
- The participant/gift-card verification export, which contains highly sensitive
  fields and is used **only** for the optional validation cross-check (its values
  are loaded into memory and never printed or written).

Private filesystem locations are passed to scripts as command-line arguments and
are not hard-coded in any committed file.

## Sensitive information excluded

The following are **never** read into public outputs: names, email addresses, phone
numbers, student IDs, tokens, payee/recipient/gift-card information, compensation
contact and citizenship, postal addresses, SSNs, raw participant IDs, and all
timestamps. Private storage URLs and cluster paths are also excluded.

## Sanitization procedure (summary)

The released tables were produced from the raw study export using an explicit
allow-list of columns (never a copy-then-delete). Raw participant, excerpt, and trial
identifiers are replaced with surrogate ids (`listener_NNNN`, `excerpt_NNNN`,
`trial_NNNN`); the raw-to-surrogate mapping is **not** released. Demographics are
emitted only as aggregate category counts.

## IRB / HSD Status

The study "Human Evaluation of Automatic Music Transcription Systems" was reviewed
by the University of Washington Human Subjects Division. On March 12, 2026, UW HSD
determined that the study qualifies for Exempt status, Category 2, under IRB ID
STUDY00025192. The official HSD determination letter is retained in private project
records and is not redistributed in this repository.

The public release includes de-identified response-level judgments. It excludes
direct identifiers, raw participant IDs, contact information, usernames, account IDs,
compensation/gift-card records, timestamps, private filesystem paths, private storage
URLs, raw platform exports, reference audio, rendered audio, MusicXML/MIDI outputs,
and third-party model outputs.

## Consent

Participants were 18 years or older. Before starting, each participant was shown an
electronic consent form describing the purpose, procedure, duration, risks, benefits
and compensation of the study and the voluntary nature of participation, and gave
consent by indicating agreement. Documentation of written consent was waived because
the study is an anonymous, minimal-risk online behavioural experiment. Participation
was voluntary and could be stopped at any time without penalty. Compensation took the
form of a modest gift certificate and did not require participants to provide
identifying personal information. The study was conducted in accordance with the
Declaration of Helsinki.

## Data release boundaries

The release comprises de-identified aggregate tables (`system_scores.csv`,
`aggregate_pairwise_results.csv`, `trials_public.csv`,
`participant_summary_aggregate.csv`, `participant_background_summary.csv`,
`proficiency_training_crosstab.csv`), the `atepp_3min_test_set.csv` manifest, and the
de-identified response-level data (`responses_public.csv`, per-judgment rows with
surrogate IDs). Raw participant identifiers, raw-to-surrogate mappings, and the raw
study-platform exports are not included.

## Licensing and reuse expectations

- **Code:** MIT License (see [LICENSE](LICENSE)).
- **Data** under `data/public/` (aggregate tables and de-identified response-level
  data): CC BY 4.0, unless otherwise noted (see [DATA_LICENSE.md](DATA_LICENSE.md)).
- **Reference/rendered audio, MusicXML/MIDI, model outputs, and other third-party
  artifacts:** not redistributed here and not covered by the repository's licenses;
  they remain subject to their own licenses and terms of use.
- Suggested reuse: cite the repository and the associated paper (see CITATION.cff).
