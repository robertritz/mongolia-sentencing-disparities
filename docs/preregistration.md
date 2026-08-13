# OSF Pre-Registration Draft

**Copy this content into the OSF Prereg template at osf.io**

---

## Study Information

### 1. Title

Demographic Disparities in Criminal Sentencing: Evidence from Mongolian Courts

### 2. Authors

[Your name and affiliations]

### 3. Description

This study examines whether defendant demographics (gender, age, education, employment status) are associated with sentencing severity in Mongolian criminal courts, controlling for legally relevant factors such as crime type, criminal history, and aggravating/mitigating circumstances.

We analyze publicly available court decisions from shuukh.mn, the official database of Mongolian court decisions. This is the first large-scale quantitative analysis of sentencing patterns in Mongolia and contributes to the sparse literature on sentencing disparities in post-socialist legal systems.

### 4. Hypotheses

**H1 (Gender):** Female defendants receive less severe sentences than male defendants for equivalent offenses.

- _Rationale:_ Consistent finding across jurisdictions (Starr, 2015; Zhuchkova & Kazun, 2023)
- _Direction:_ Negative coefficient on female indicator

**H2 (Education):** Defendants with higher education receive less severe sentences than those with lower education.

- _Rationale:_ Education signals social status and rehabilitation potential (Mustard, 2001)
- _Direction:_ Negative coefficient on education level

**H3 (Age):** Sentencing severity varies non-linearly with age, with relative leniency for younger (under 25) and older (over 60) defendants.

- _Rationale:_ Young offenders seen as redeemable; elderly seen as lower risk
- _Direction:_ Negative coefficient on age-squared term (inverted U-shape)

**H4 (Employment):** Employed defendants receive less severe sentences than unemployed defendants.

- _Rationale:_ Employment signals social integration and lower recidivism risk
- _Direction:_ Negative coefficient on employed indicator

---

## Design Plan

### 5. Study type

Observational study - secondary analysis of administrative court records

### 6. Blinding

No blinding. This is an observational study of existing records.

### 7. Is there any additional blinding in this study?

N/A

### 8. Study design

**Design:** Cross-sectional analysis of criminal court decisions

**Unit of analysis:** Individual court case

**Population:** All criminal court of first instance decisions in Mongolia available on shuukh.mn

**Time period:** All available dates (actual range to be documented after data collection)

**Key design features:**

- Publicly available administrative data (no sampling)
- Controls for legally relevant factors (crime type, criminal history)
- Year and court fixed effects to control for temporal trends and court-level variation
- Robust standard errors to address heteroskedasticity

---

## Sampling Plan

### 9. Existing data

**Registration prior to accessing the data.** We have not accessed shuukh.mn case data beyond confirming that the database exists and is publicly accessible. No case content has been viewed or analyzed.

### 10. Explanation of existing data

We confirmed the existence of the shuukh.mn database and its public accessibility through the website interface. We have not scraped, downloaded, or analyzed any case data.

### 11. Data collection procedures

1. Enumerate all available case IDs for criminal court of first instance via the shuukh.mn API
2. Scrape individual case pages (HTML)
3. Extract structured and unstructured fields using rule-based parsing and LLM-assisted extraction
4. Validate extraction accuracy on a 200-case manually coded sample (target: >90% accuracy per field)

### 12. Sample size

**Expected:** 5,000-20,000 cases (based on estimated volume of ~200 cases/month)
**Actual:** To be determined after data collection

### 13. Sample size rationale

We collect all available cases (population, not sample). Power is not a primary concern given the expected large N. With 5,000+ cases, we have >99% power to detect small effect sizes (d=0.1) at α=0.05.

### 14. Stopping rule

We will collect all available cases on shuukh.mn for criminal court of first instance. No early stopping.

---

## Variables

### 15. Manipulated variables

None. This is an observational study.

### 16. Measured variables

**Dependent Variable:**

`sentence_severity` - Unified severity score in "imprisonment-month equivalents"

Conversion scale:
| Sentence Type | Weight |
|---------------|--------|
| Imprisonment | 1.0 × months |
| Suspended sentence | 0.5 × months |
| Probation | 0.3 × months |
| Community service | hours / 160 |
| Fine | To be calibrated based on legal conversion rates |

_Sensitivity analyses will test alternative weights._

**Independent Variables (Demographics):**

| Variable      | Operationalization                                       |
| ------------- | -------------------------------------------------------- |
| `female`      | Binary: 1 if female, 0 if male                           |
| `age`         | Years at time of case decision                           |
| `age_squared` | Age² for non-linear effects                              |
| `education`   | Ordinal 1-5 (бага, суурь, бүрэн дунд, тусгай дунд, дээд) |
| `employed`    | Binary: 1 if employed, 0 if unemployed                   |

**Control Variables:**

| Variable            | Operationalization                                          |
| ------------------- | ----------------------------------------------------------- |
| `crime_category`    | Categorical: violent, property, drug, traffic, other        |
| `prior_criminal`    | Binary: 1 if prior criminal history                         |
| `aggravating_count` | Count of aggravating factors mentioned                      |
| `mitigating_count`  | Count of mitigating factors mentioned                       |
| `year`              | Year fixed effects                                          |
| `court_id`          | Court fixed effects (or random effects in multilevel model) |

### 17. Indices

No composite indices constructed.

---

## Analysis Plan

### 18. Statistical models

**Primary Model:** OLS regression with robust (HC3) standard errors

```
severity ~ female + age + age_squared + education + employed +
           crime_category + prior_criminal +
           aggravating_count + mitigating_count +
           year_FE + court_FE
```

**Robustness Model 1:** Multilevel model with court random intercepts

```
severity ~ female + age + age_squared + education + employed +
           crime_category + prior_criminal +
           aggravating_count + mitigating_count +
           year_FE + (1 | court_id)
```

**Robustness Model 2:** Two-stage selection model

- Stage 1: Logistic regression for P(imprisonment | convicted)
- Stage 2: OLS for sentence length | imprisoned

### 19. Transformations

- `age_squared` = age × age (to capture non-linear age effects)
- Crime articles collapsed into 5 categories based on Criminal Code structure
- Severity scale transformation as described above

### 20. Inference criteria

- α = 0.05 (two-tailed) for primary hypothesis tests
- Report 95% confidence intervals for all coefficients
- Report effect sizes (standardized coefficients) alongside unstandardized
- Distinguish confirmatory (H1-H4) from exploratory analyses

### 21. Data exclusion

Exclude cases with:

- Missing dependent variable (no sentence recorded)
- Missing gender (required for H1)
- > 50% missing control variables
- Juvenile defendants (different legal framework)

Report: N excluded per criterion, comparison of excluded vs. included cases

### 22. Missing data

- **Primary analysis:** Complete case analysis for core variables
- **Sensitivity:** Multiple imputation if education/occupation missing <20%
- Report missing data rates per variable

### 23. Exploratory analyses (not confirmatory)

The following analyses are explicitly exploratory and will be labeled as such:

- Judge-level effects (if identifiable)
- Prosecutor effects
- Temporal trends in disparity
- Interaction effects (e.g., gender × crime type)
- Geographic variation (Ulaanbaatar vs. aimag courts)

---

## Other

### 24. Other

**Limitations acknowledged a priori:**

1. Cannot control for unobserved case characteristics (demeanor, evidence quality, victim preferences)
2. Only completed cases observed; dismissals/acquittals not in sample
3. Disparity ≠ discrimination; cannot make causal claims without stronger identification

**Data and code availability:**

- Analysis code will be made public on GitHub/OSF upon publication
- Raw data are public records from shuukh.mn

**Ethical considerations:**

- Data are public court records; no IRB required
- Aggregate analysis only; no individual cases highlighted
- Will use careful language distinguishing disparity from discrimination

---

## References

Mustard, D. B. (2001). Racial, ethnic, and gender disparities in sentencing: Evidence from the US federal courts. The Journal of Law and Economics, 44(1), 285-314.

Starr, S. B. (2015). Estimating gender disparities in federal criminal cases. American Law and Economics Review, 17(1), 127-159.

Zhuchkova, S., & Kazun, A. (2023). Exploring gender bias in homicide sentencing: An empirical study of Russian court decisions using text mining. Homicide Studies.

---

_Draft created: 2026-02-03_
_Status: Ready for OSF submission_
