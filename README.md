# Demographic Disparities in Criminal Sentencing: Evidence from Mongolian Courts

Quantitative analysis of sentencing disparities in Mongolian criminal first-instance decisions from `shuukh.mn`, covering the 2020-01-01 to 2026-02-04 study window.

## Status

- Data collection complete
- Publication evidence gate complete
- Submission analysis and manuscript package reproducible locally
- Author declarations complete; ethics determination remains pending
- Public replication package: https://github.com/robertritz/mongolia-sentencing-disparities
- Current working analysis dataset: `data/processed/sentencing_clean.parquet`

## Key Numbers

- 80,827 total enumerated cases
- 77,968 valid decisions
- 69,527 cleaned analysis cases across 4 validated sentence types
- 29,132 adult complete cases in the primary model
- 49 courts

## Quick Start

```bash
uv run --with-requirements requirements-lock.txt \
  python scripts/analysis/smoke_test.py
```

## Main Analysis Outputs

- `paper/manuscript.md` — canonical manuscript and results narrative
- `paper/submission/` — generated editable submission package
- `data/validation/EVIDENCE_GATE.md` — locked validation decisions and status
- `data/validation/CODING_PROTOCOL.md` — prediction-blinded recoding protocol
- `tables/` — generated tables
- `figures/` — generated figures
- `scripts/analysis/` — cleaning, descriptive, model, validation, and smoke-test scripts

`docs/analysis_results.md` and the section-level files under `paper/` are
superseded exploratory snapshots and are not submission sources.

## Reproduction

Canonical sample definitions live in `src/analysis_dataset.py`.

Recommended one-command refresh:

```bash
bash scripts/analysis/run_submission_refresh.sh
```

The refresh regenerates all descriptive outputs, retained models, figures, Word
files, and then runs the smoke and submission-integrity checks. It starts from
the hash-locked cleaned parquet; reconstruction from the archived source corpus
is a separate provenance workflow documented in `DATA_ARCHIVE.md`.

## Data Availability

The public repository contains a deidentified replication parquet with the
variables needed for the retained analyses. It excludes case identifiers, case
numbers, exact dates, court names, judge and prosecutor names, occupations,
free text, and the failed aggravating and mitigating fields. Source decisions
and case-level validation labels are not redistributed. The lock digest and
aggregate validation results preserve the audit record without publishing a
case-level linkage file.

## Citation

See `CITATION.cff`.
