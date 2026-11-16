# The AI Label Paradox

Analysis code and anonymised data for the MSc dissertation *The AI Label Paradox*
(LSE MSc Behavioural Science): a pre-registered 2×2 (Label × Transparency)
between-subjects negotiation experiment testing whether disclosing an AI counterpart,
as mandated by Article 50 of the EU AI Act, changes trust and bargaining when the
counterpart's numerical conduct is held constant.

## Contents

- `study_analysis.Rmd` — the full analysis pipeline (reliability, CFA, confirmatory
  tests, equivalence and Bayesian analyses, specification curve, mediation, and the
  exploratory analyses).
- `prolific_192_anon.csv` — the anonymised participant dataset.
- `oshea_function_words_277.csv` — function-word lexicon used by the stylometric
  register analysis.
- `suspicion_coding_sheet.csv`, `suspicion_coding_sheet_CODED.csv` — single-rater
  coding of free-text identity reasons into the pre-registered cue categories.
- `coding_review.txt` — human-readable coding worksheet for the above.

## Data and anonymisation

All participant identifiers (Prolific IDs, oTree participant and session codes) have
been removed. A within-file integer key (`participant_id`) preserves participant-level
grouping for the repeated-measures models. Free-text responses have been screened for
identifying content. The payment step in the pipeline is disabled on this anonymised
data. The recruitment target was N = 200; the achieved analytical sample was N = 201.

## Reproducing the analysis

Open `study_analysis.Rmd` in R and knit. The data path points to
`prolific_192_anon.csv`. Package dependencies are loaded at the top of the file.

## Pre-registration

Pre-registered on OSF Registries (24 May 2026):
https://doi.org/10.17605/OSF.IO/VYSHM

## The experiment application

The oTree experiment application is in the `otree` folder at the repository root.

## Licence

Released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), matching the
OSF registration. You may share and adapt this material with attribution.
