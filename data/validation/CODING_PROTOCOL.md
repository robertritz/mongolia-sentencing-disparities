# Validation Coding Protocol

**Protocol version:** 1.0, locked 2026-08-12 after a prediction-blinded audit
of cases 1-25. Do not change these rules after predictions are exposed. Record
any later exceptional adjudication without rewriting the protocol.

## Purpose

Independently code the fields that support the paper's employment and
sentencing-factor claims. Coders must not inspect the model predictions in
`manual_validation_sample.csv` until coding is complete.

Use `manual_coding_sheet.csv`, which contains case IDs and blank gold fields
only. Read the corresponding source decision in `source_decisions/{case_id}.json`.
The compact packet is a navigation aid: when a packet says that a heading or
phrase was not located, or a snippet ends before the court's reasoning is
complete, inspect the full source decision before coding.

For decisions with multiple defendants, code the first defendant only. Apply a
shared finding to the first defendant when the court expressly applies it to
all defendants; do not import a circumstance stated only for another defendant.

## Employment

Code `gold_employed` as:

- `true` when the defendant biography explicitly says `ажилтай` or otherwise
  unambiguously states a current job, business, or livelihood at the time of
  the decision (including current herding or farming);
- `false` when it explicitly says `ажилгүй`;
- blank when employment status is absent, redacted, historical, or ambiguous.

Do not infer employment from education, income, family status, or a profession
that is not stated to be current. Treat `эрхэлсэн тодорхой ажилгүй` and other
unambiguous variants of no current work as `false`. Treat a job title followed
by `ажилтай`, a named current employer and role, `хувиараа хөдөлмөр эрхэлдэг`,
or an expressly current livelihood such as `мал маллан амьдардаг` as `true`.
A bare profession or qualification (`мэргэжилтэй`) is not enough. A bare
student, pensioner, homemaker, disability, or similar status is blank unless
the source separately states current employment or unemployment.

Use status at the time described in the defendant biography or sentencing
rationale, not a job mentioned only as part of the offense narrative. When a
historical job conflicts with an explicit current biography (for example, the
person worked at a shop when the offense occurred but is now `ажилгүй`), use
the explicit current biography and note the conflict.

## Sentence

Code the primary disposition in the operative `ТОГТООХ` section as one of:
`fine`, `imprisonment`, `community_service`, `suspended`, `probation`, or
`other`. Use `other` when a prediction-stratified case actually has a different
primary disposition, such as a travel restriction; this is a model mismatch,
not a reason to force the source into one of the five sampled categories.
Record imprisonment duration in months, converting years to 12 months. Leave
months blank for non-imprisonment dispositions unless the decision states a
nominal imprisonment term that is then suspended.

Code `suspended` for a disposition expressed as `тэнссэн` or `тэнсэх`,
including `хорих ял оногдуулахгүйгээр ... тэнсэх`. Code `probation` only for
`хянан харгалзах`. If multiple penalties are combined, use the final aggregate
primary disposition in the operative section and explain the components in
`notes`.

## Aggravating and Mitigating Factors

Code only factors the court explicitly cites when selecting the sentence. Do
not count facts appearing only in the narrative, prosecutor's submission, or
party argument.

Do not count a circumstance merely because it is an element or qualifying
feature of the offense under the Special Part (for example, acting as a group,
using a weapon, or cruelty in the offense definition). Count it only if the
court separately identifies it as an aggravating or mitigating circumstance
in the sentencing analysis. Likewise, a prior conviction, guilty plea,
employment status, family circumstance, or other personal fact considered
under Article 6.1.2 is not automatically a factor: count it only when the court
expressly characterizes it as aggravating or mitigating.

- `gold_*_present`: `true` when at least one qualifying factor is cited;
  otherwise `false` when the sentencing rationale is readable and cites none;
  blank when the relevant section is absent or unclear.
- `gold_*_count`: count distinct qualifying factors, deduplicating repeated
  descriptions of the same circumstance.

Use the Criminal Code's enumerated factors where cited, plus any other
case-specific circumstance the court expressly treats as aggravating or
mitigating. Each separately cited statutory subparagraph or separately named
non-statutory circumstance counts once. Multiple facts offered as support for
one stated circumstance count once; the same circumstance repeated later in
the judgment also counts once.

When the court expressly says no qualifying circumstances were established,
code presence as `false` and count as `0`. When presence is `true`, count must
be a positive integer. When the relevant reasoning is absent or too unclear to
decide, leave both presence and count blank. Record the decisive source phrase
or the reason for uncertainty in `notes`.

## Independence and Adjudication

Complete every gold field before opening the prediction file or running the
scoring script. Flag uncertain cases in `notes`; adjudicate those cases from
the source text before calculating final metrics. Do not change gold labels in
response to disagreement with the model unless the original coding is shown
to violate this protocol.

Gold labels require prediction-blinded source coding independent of the
original Grok extraction. Automated passage retrieval may help a coder locate
relevant text, but every label must be assigned case by case from the saved
decision under this protocol. Before scoring, resolve all notes marked
uncertain, record the coder and adjudicator, and lock the completed coding
sheet with a SHA-256 hash in `EVIDENCE_GATE.md`.
