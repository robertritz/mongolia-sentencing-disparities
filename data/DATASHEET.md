# Datasheet: Mongolian Criminal Sentencing Analysis Dataset

This datasheet follows the questions proposed by Gebru et al. (2021) and
documents the publication release rather than the private source archive.

## Motivation

The dataset was created to study whether defendant gender, age, education, and
employment are associated with sentence severity in Mongolia after accounting
for offense and case characteristics. Robert Ritz created the dataset as part
of his institutional role at the American University of Mongolia. No specific
grant or external funding supported the study.

## Composition

The source population comprises 80,827 criminal first-instance decisions
listed by Mongolia's public judicial database for 2020-01-01 through
2026-02-04. Of these, 77,968 contained usable decision text. The publication
dataset contains 69,527 decisions after quality cleaning and exclusion of all
5,796 records carrying an invalidated `probation` extraction label.

Each public-release row contains deidentified derived variables needed for the
retained analysis: year; a pseudonymous court code; offense article, chapter,
and category; defendant demographics; sentence outcomes; selected case
characteristics; and extraction-quality fields. The complete schema is in
`CODEBOOK.md`.

The release excludes case identifiers, case numbers, exact dates, court names,
judge and prosecutor names, occupations, decision text, and the failed
aggravating and mitigating fields. Missingness remains substantial because
public decisions vary in how much biographical information they provide. Age
is the binding variable for the primary complete-case sample.

The source population is intended as a census of published decisions within
the fixed period, not a census of all criminal proceedings. Unpublished,
dismissed, and otherwise unavailable cases are outside the sampling frame.

## Collection and processing

Cases were enumerated and downloaded from shuukh.mn from February 4-9, 2026.
Structured metadata were parsed from the page tables. Regular expressions and
xAI's `grok-4-1-fast-non-reasoning` model extracted fields from the Mongolian
decision text. The LLM stage processed 77,968 valid records in 78 batches and
returned usable output for 77,364.

For publication, three separate prediction-blinded Codex coding sessions
reviewed disjoint portions of a fixed stratified sample of 300 saved public
decisions under a protocol locked before predictions were exposed. Employment
passed its accuracy and kappa thresholds. Aggravating and mitigating fields
failed their presence and count thresholds and were removed from the retained
analyses. The audit also found zero precision for the extracted probation
category, which was excluded in full. This was LLM-assisted source recoding,
not independent human manual validation.

The raw decision corpus and pre-cleaning extraction file are retained privately
for provenance and are not part of the public replication package.

## Recommended uses

The dataset supports reproduction and extension of aggregate analyses of
sentencing patterns, missingness, and model sensitivity. It may also support
methodological work on public court records when users respect the validation
boundaries.

It should not be used to identify defendants, predict outcomes for individuals,
rank judges or courts, or make causal claims about discrimination. The data are
observational and cover only published completed cases.

## Ethics and privacy

No formal ethics committee approval was obtained before release preparation.
The study uses secondary public judicial records; no individuals were recruited
or contacted and no intervention occurred. The author has requested an
independent institutional determination for journal submission.

Public availability at the source does not eliminate privacy risk. Combinations
of offense, year, sentence, court code, and demographics may still permit
linkage. Direct identifiers and free text were therefore removed, time was
coarsened to year, court names were pseudonymized, source decisions were not
redistributed, and results are reported in aggregate. Users should not attempt
re-identification.

Consent was not sought because the study did not contact individuals and uses
records published by the judiciary. The journal declaration reports consent as
not applicable and does not claim a committee exemption that has not been
documented.

## Distribution and licensing

The replication package is available at
https://github.com/robertritz/mongolia-sentencing-disparities. Code is licensed
under the MIT License. The deidentified derived dataset is licensed under CC BY
4.0, subject to the separate rights and terms applying to the source judicial
records.

The study population is fixed and no routine updates are planned. Corrections
will be versioned through GitHub releases. Questions and reproducibility issues
may be filed in the repository's issue tracker.

## Reference

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé
III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the
ACM, 64*(12), 86-92.
