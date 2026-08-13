# Publication Validation Evidence

This directory documents the prediction-blinded 300-decision source-recoding
audit used for publication readiness.

## Public files

- `EVIDENCE_GATE.md`: fixed design, thresholds, results, remediation, and final
  gate disposition.
- `CODING_PROTOCOL.md`: rules locked after the 25-case pilot and before model
  predictions were exposed.
- `legal_evidence.md`: primary-law findings governing the employment claim.
- `gold_labels.lock.json`: row count, protocol version, coding roles, and the
  SHA-256 digest of the locked coding sheet.
- `../../tables/validation_metrics.csv`: aggregate validation metrics.

## Files intentionally not released

The private provenance archive retains the sampled case IDs, saved source
decisions, coder packets, case-level gold labels, prediction file, source hash
manifest, disagreement diagnostics, and sentence-type audit rows. They are not
part of the public replication package because they create a case-level linkage
file for sensitive criminal records.

The public lock digest permits integrity comparison with the private coding
sheet without redistributing the linkage data. The aggregate results are:

- Employment accuracy 0.978 and Cohen's kappa 0.956: pass.
- Aggravating-factor presence F1 0.150 and count MAE 1.035: fail.
- Mitigating-factor presence F1 0.665 and count MAE 1.933: fail.
- Extracted probation precision 0/60: fail; the entire category was excluded.

The failed factor fields are not included in the public dataset or retained
models. The source recoding was performed by three separate prediction-blinded
Codex sessions under the locked protocol. It is not described as independent
human manual validation.
