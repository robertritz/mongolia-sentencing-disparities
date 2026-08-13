# Publication Evidence Gate

## Objective

Independently validate the extracted fields that support the manuscript's
employment and sentencing-factor claims against a fixed, reproducible sample
of source decisions before treating those claims as publication-ready.

## Fixed Sample

- 300 unique first-instance criminal decisions
- 60 decisions from each of five extracted sentence-type labels
- Within each sentence type: 30 `complete` and 30 `partial` extraction-quality
  records
- Random seed: `42`
- Prediction-blinded coding order

## Pass Criteria

| Field | Required evidence |
|---|---|
| Employment | Accuracy >= 0.90 and Cohen's kappa >= 0.80 |
| Aggravating-factor presence | F1 >= 0.85 |
| Aggravating-factor count | Mean absolute error <= 1.0 |
| Mitigating-factor presence | F1 >= 0.85 |
| Mitigating-factor count | Mean absolute error <= 1.0 |

Prediction coverage for employment, sentence-type agreement, and sentence-
length agreement will also be reported even though they are not separate gate
criteria.

## Independence Requirement

The gold labels must be assigned from the public source decisions without
opening `manual_validation_sample.csv` or otherwise seeing the Grok/regex
predictions. Automated passage retrieval may be used to flag passages for
review, but it is not a substitute for case-by-case source coding under the
locked protocol.

Uncertain cases must be resolved from the source under `CODING_PROTOCOL.md`
before the predictions are unblinded. Gold labels must not be changed merely
because they disagree with the extracted values.

## Legal-Evidence Requirement

The employment interpretation must be consistent with the current official
Criminal Code and with observed sentencing reasoning in the validation sample.
The code does not enumerate employment in Article 6.5.1; it permits courts to
consider a defendant's broader personal circumstances under Article 6.1.2.
Sample-wide court-practice claims remain gated on completion of the blinded
coding.

## Failure Rule

If any required metric misses its threshold, do not publish the affected
claim from the current extraction. Diagnose the disagreement, correct the
field definition or extraction if justified without altering the gold labels,
rerun the affected analysis, and report the failure and remediation.

## Current Status

- [x] Fixed sample drawn
- [x] All 300 public source decisions retrieved
- [x] Blinded coding sheet and source packets generated
- [x] First 25-case packet audited without exposing predictions
- [x] Coding protocol v1.0 locked before scoring
- [x] Primary-law review completed
- [x] Prediction-blinded source coding completed
- [x] Uncertain cases adjudicated
- [x] Metrics scored against locked gold labels
- [x] Affected analyses rerun after factor-field failures
- [x] Sentence-type audit completed and contaminated category excluded
- [x] Manuscript claims revised to match the evidence

**Gate disposition:** Closed 2026-08-12 after partial pass and remediation.
Employment passed. Neither factor field passed; all count-dependent analyses
and manuscript claims were removed pending corrected extraction and renewed
validation. The supplementary sentence-type audit found zero precision for
the extracted probation label; all records carrying that label were excluded
and affected analyses and manuscript claims were regenerated.

## Blinded Pilot Audit (Cases 1-25)

Completed 2026-08-12 without opening `manual_validation_sample.csv`.

- The packet order and coding sheet remain prediction-blinded. The blank sheet
  SHA-256 at protocol lock was
  `253f8450d45103d4670526db1ee829528936871ece85e35461f9a6c7e58fc75c`.
- All 25 pilot source files match their SHA-256 entries in
  `source_manifest.csv`.
- The compact packet is not sufficient by itself for every case: four cases
  did not expose a `ТОГТООХ` heading, three did not locate a biography heading,
  five did not locate an employment phrase, and two did not locate a factor
  phrase. These are packet-search limitations, not missing-source findings;
  the full saved decision is controlling.
- The pilot exposed and resolved protocol edges for historical versus current
  employment, bare professions, multi-defendant attribution, offense elements
  versus sentencing factors, zero versus unknown counts, separately cited
  grounds, and combined dispositions.
- No gold label was assigned by an automated system during the protocol audit.

## Lock Record

- Protocol: version 1.0, 2026-08-12
- Predictions exposed: only after all 300 labels were merged and locked
- Gold coding-sheet SHA-256:
  `d7582b941d275867e677cea89878bdf032fc6cb7d79ab4cb14ec0de230f3cbf9`
- Coders: Codex blinded coders 001-100, 101-200, and 201-300
- Adjudicator: Codex sentence-type protocol adjudication

## Scoring Result

| Field | Metric | Result | Threshold | Pass |
|---|---|---:|---:|---|
| Employment | Accuracy | 0.978 | >= 0.90 | Yes |
| Employment | Cohen's kappa | 0.956 | >= 0.80 | Yes |
| Aggravating presence | F1 | 0.150 | >= 0.85 | No |
| Aggravating count | MAE | 1.035 | <= 1.00 | No |
| Mitigating presence | F1 | 0.665 | >= 0.85 | No |
| Mitigating count | MAE | 1.933 | <= 1.00 | No |

Employment accuracy and kappa use the 183 cases with both a gold label and a
prediction. Factor metrics use 283 decisions with readable sentencing
rationales.

## Sentence-Type Audit and Remediation

- Overall extracted sentence-type accuracy was 0.790 and Cohen's kappa was
  0.750. The error was concentrated in one systematic class rather than spread
  across the outcome.
- The four retained categories were correct in 237 of 240 sampled cases
  (98.75%): fine 60/60, imprisonment 58/60, community service 59/60, and
  suspended 60/60.
- The extracted probation category had precision 0/60. Gold coding identified
  58 as `other`, chiefly travel-restriction dispositions, and two as suspended.
- Four initially coded imprisonment cases were adjudicated to `other` because
  the operative order converted the nominal imprisonment term to a travel
  restriction under amnesty. These corrections implement the already locked
  rule to use the final effective disposition; they were not made to improve
  agreement with predictions.
- The full source archive needed for case-level reclassification of all 5,796
  affected records is not present in this checkout. Rather than infer labels,
  the canonical analysis parquet conservatively excludes the entire class.
  Future full cleaning applies the same rule.
- The cleaned sample changed from 75,323 to 69,527; after restoring the
  preregistered juvenile exclusion, Sample A changed from 29,847 to 29,132.
  All descriptive outputs, Models 1-2, robustness checks,
  and Figures 1-6 were regenerated. Employment remains significant in Model 1
  (B = -6.280, p < 0.001) and Model 2 (B = -2.834, p < 0.001).

## Failure Diagnosis and Remediation

- Factor-presence recall was 1.00 for both fields, but precision was 0.081 for
  aggravating factors and 0.498 for mitigating factors.
- The extractor systematically overincluded offense elements, narrative facts,
  personal circumstances, and party arguments that the court did not expressly
  characterize as sentencing factors. This is a construct-definition failure,
  not random count noise.
- Removed factor means from Table 1, factor correlations from Table 3, Model 3
  and its factor coefficients from Table 4, the factor variance-decomposition
  block, and Model 3 from Figures 5-6.
- Reran the affected descriptive scripts, validated Models 1-2, robustness
  checks, and figures after both factor and sentence-type remediation. Model 1
  employment is -6.280 month-equivalents and Model 2 is -2.834, both p < 0.001.
- Revised the manuscript to report employment validation, disclose the failed
  pre-registered factor specification, remove factor-mediation claims, and
  correct the legal treatment of employment under Articles 6.5.1 and 6.1.2.
