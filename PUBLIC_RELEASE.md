# Public Replication Package

This repository is a clean publication snapshot. It contains the deidentified
derived data and code needed to reproduce the retained analyses, tables, and
figures. It is not a copy of the private research worktree or its Git history.

The released parquet removes case identifiers, case numbers, exact dates,
court names, judge and prosecutor names, occupation text, source text, and the
aggravating and mitigating fields that failed validation. Court fixed effects
use pseudonymous codes, and dates are represented only by year. The data remain
sensitive because combinations of public-record attributes may permit linkage;
users should not attempt re-identification or individual prediction.

Case-level gold labels and the 300 saved source decisions are not redistributed.
The package includes the locked coding-sheet digest, protocol, aggregate
metrics, and evidence-gate report.
