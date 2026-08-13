# Codebook: Public Sentencing Analysis Dataset

**Version:** 3.0 publication release  
**Study window:** 2020-01-01 to 2026-02-04  
**Rows:** 69,527

The public parquet is a deidentified derived analysis dataset. It omits case
identifiers, case numbers, exact dates, court names, judge and prosecutor names,
occupation text, source text, and the aggravating and mitigating fields that
failed validation. A row represents one published criminal first-instance
decision retained after the evidence-gated sentence-type cleaning.

## Case and offense variables

| Variable | Type | Description |
| --- | --- | --- |
| `year` | integer | Decision year, 2020-2026 |
| `court_id` | string | Pseudonymous court code used for fixed effects |
| `is_ub` | integer | 1 for Ulaanbaatar court, 0 otherwise |
| `primary_article` | string | First parsed Criminal Code article |
| `crime_chapter` | number | Criminal Code chapter parsed from the primary article |
| `crime_category` | string | `violent`, `property`, `traffic`, `drug`, or `other` |

## Defendant variables

| Variable | Type | Description |
| --- | --- | --- |
| `gender` | string | Extracted `male` or `female`; missing if unavailable |
| `female` | nullable integer | 1 for female, 0 for male |
| `age` | number | Age at decision; values below 14 removed during cleaning |
| `age_sq` | nullable integer | Squared age |
| `education_clean` | string | Normalized education category |
| `education_level` | number | Ordinal education code, 0-5 |
| `employed` | nullable boolean | Current employment status in the defendant biography |
| `family_size` | number | Reported household size |
| `prior_criminal` | nullable boolean | Extracted prior-conviction indicator |

Education codes are `0` none, `1` primary, `2` basic, `3` secondary or
incomplete secondary, `4` vocational, and `5` higher.

## Sentence variables

| Variable | Type | Description |
| --- | --- | --- |
| `sentence_type` | string | `fine`, `imprisonment`, `community_service`, or `suspended` |
| `sentence_months` | number | Imprisonment duration in months, when present |
| `sentence_fine_mnt` | number | Fine in Mongolian tugriks, when present |
| `sentence_community_hours` | number | Community-service hours, when present |
| `sentence_suspended_months` | number | Suspended duration in months, when present |
| `severity` | number | Sentence severity in month-equivalents |
| `severity_winsorized` | number | Severity winsorized at the 99th percentile |
| `severity_outlier` | boolean | 1 if severity exceeds the winsorization threshold |

The default conversion uses 450,000 MNT per month for fines and 720 community
service hours per month. The analysis code also implements registered and legal
sensitivity conversions. The extracted `probation` class had zero precision in
the stratified audit; all 5,796 records carrying that label were excluded.

## Case-characteristic and extraction variables

| Variable | Type | Description |
| --- | --- | --- |
| `victim_minor` | nullable boolean | Extracted indicator that the victim was under 18 |
| `injury_severity` | string | Extracted injury category, when stated |
| `intoxicated_at_crime` | nullable boolean | Extracted intoxication indicator |
| `has_lawyer` | nullable boolean | Extracted legal-representation indicator |
| `plea_agreement` | nullable boolean | Extracted simplified-procedure indicator |
| `plea_guilty` | nullable boolean | Extracted admission-of-guilt indicator |
| `restitution_paid` | nullable boolean | Extracted compensation indicator |
| `time_served_days` | number | Extracted pretrial detention days |
| `extraction_quality` | string | `complete`, `partial`, or `unreliable` |
| `extraction_method` | string | Provenance of the selected extracted value |

## Canonical samples

- `full`: all 69,527 cleaned cases.
- `sample_a`: complete on the four demographic hypotheses, crime category,
  prior record, and severity; known juveniles excluded (N = 29,132).
- `sample_b`: no age requirement; known juveniles excluded (N = 35,995).
- `two_part_stage1`: complete on imprisonment-routing predictors; known
  juveniles excluded (N = 33,600).
- `two_part_stage2`: imprisoned stage-one cases with a duration (N = 5,521).

## Validation boundary

Employment passed the locked evidence gate (accuracy 0.978; Cohen's kappa
0.956). Aggravating- and mitigating-factor fields failed their presence and
count thresholds and are neither released nor used in retained analyses. See
`validation/EVIDENCE_GATE.md` for the complete disposition.
