# Demographic Disparities in Criminal Sentencing: Evidence from Mongolian Courts

## Abstract

Quantitative sentencing research in post-socialist legal systems remains scarce, and I identified no prior large-scale study of demographic sentencing patterns in Mongolia. I collected 80,827 criminal first-instance decisions from Mongolia's public court database (shuukh.mn), covering 49 courts over the period 2020 to 2026. Using a combination of regular expressions and large language model extraction, I obtained defendant demographics, case characteristics, and sentencing outcomes for 29,132 complete adult cases. I pre-registered four hypotheses (gender, education, age non-linearity, employment) and estimated a total-association model and a within-crime-article model. Employment is the dominant finding. Unemployed defendants receive sentences 6.3 month-equivalents more severe than employed defendants, and the association remains 2.8 months within the same crime article. Prediction-blinded LLM-assisted source recoding of a stratified 300-decision sample validated employment extraction (accuracy 0.978; Cohen's kappa 0.956). The same audit found zero precision for the extracted probation category and rejected the extracted aggravating and mitigating factor counts; those records and factor-dependent analyses were excluded. Employment is not enumerated as a mitigating circumstance in Article 6.5.1 of Mongolia's Criminal Code, although courts may consider it within a defendant's broader personal circumstances under Article 6.1.2. The employment association is robust to severity conversions but differs within sentence types, indicating that sentence routing is central to the aggregate gap.

**Keywords:** sentencing disparities, employment, criminal courts, Mongolia, text mining, court records

## 1. Introduction

International sentencing research has consistently documented that defendant demographics predict sentencing outcomes, even after controlling for legally relevant case characteristics. Gender disparities have been found across multiple jurisdictions, with women typically receiving shorter sentences than men for comparable offenses [@starr2012estimating; @daly1995sex; @philippe2020gender]. Socioeconomic factors like employment and education also predict severity [@mustard2001racial; @chiricos1991unemployment; @spohn2000imprisonment]. Race and ethnicity are the most studied demographic predictors, at least in the United States [@mitchell2005meta], though the mechanisms remain debated.

Most of this evidence comes from Western legal systems, particularly US federal and state courts. Post-socialist systems are underrepresented. @zhuchkova2023exploring analyzed 20,531 Russian homicide decisions using text mining and found gender effects consistent with the international literature. @mamak2022failed studied sentencing disparities in Poland and noted the scarcity of quantitative research in post-communist contexts. My literature search identified no prior large-scale quantitative study of demographic sentencing disparities in Mongolia. @amarsanaa2014fledgling provides an overview of Mongolia's judicial system, but not a case-level sentencing-disparity analysis.

Mongolia offers a rare opportunity. The Supreme Court publishes all criminal court decisions through a public database (shuukh.mn), including defendant demographics, case details, and sentencing outcomes in the full text of each decision. I collected all 80,827 criminal first-instance decisions from this database covering January 2020 through February 2026, across 49 courts. After cleaning and excluding an unvalidated sentence-type category, 69,527 cases remain, with 29,132 adult cases complete on all variables needed for the primary analysis.

I pre-registered four hypotheses on the Open Science Framework before data collection: that female defendants, more educated defendants, defendants at the extremes of the age distribution, and employed defendants would receive less severe sentences. I extracted defendant demographics and sentencing data using a combination of regular expressions and large language model processing. The regex fields were benchmarked against a 200-case manually coded pilot, while the publication-critical LLM fields were subjected to the prediction-blinded source audit described below.

The analysis reports two validated regression specifications. Model 1 estimates the total association between demographics and sentencing severity within broad crime type. Model 2 replaces broad categories with article-level fixed effects to test within-crime associations. The pre-registered specification also included extracted counts of aggravating and mitigating factors, but prediction-blinded source validation showed that those fields did not measure expressly cited sentencing circumstances with sufficient precision. I therefore report the deviation from the pre-registration and do not interpret that specification.

Employment is the standout finding. Unemployed defendants receive sentences 6.3 month-equivalents more severe than employed defendants (Model 1), and the association persists within the same crime article (2.8 months in Model 2). The Criminal Code does not enumerate employment as mitigation under Article 6.5.1; employment may instead enter the broader assessment of personal circumstances required by Article 6.1.2. Gender operates primarily through the imprisonment decision rather than sentence length, producing a Simpson's paradox (lower overall severity for women, but longer sentences conditional on imprisonment). Education is not a stable predictor.

The closest comparable study is @zhuchkova2023exploring, who used text mining on Russian court decisions and found gender effects in homicide sentencing. This study covers a broader range of offenses (all criminal first-instance cases, not just homicide), uses a larger sample (29,132 vs. 20,531), and tests whether demographic associations persist within the same crime article. It also demonstrates why extracted legal concepts require field-specific source validation before they are used as regression controls.

## 2. Data and Methods

### 2.1 Data Source

Mongolia's Supreme Court publishes criminal court decisions through a public database at shuukh.mn. Each decision includes structured metadata (court, judge, prosecutor, date, criminal code article) and free-text sections containing defendant demographics, case facts, and sentencing rationale. I collected all criminal first-instance decisions in the database dated between January 1, 2020 and February 4, 2026, totaling 80,827 cases across 49 courts. Of these, 77,968 (96.5%) contained valid decision text; the remaining 2,859 had empty or truncated records at the source.

The data represent a near-census of published first-instance criminal sentencing decisions in Mongolia during the study period. The source decisions are public government records. The analysis reports aggregate statistics and does not identify individual defendants. The institutional ethics determination is reported in the separate declarations file.

Mongolia's criminal justice system operates under the 2015 Criminal Code [@mongoliacriminalcode2015], which replaced the 2002 code and took effect in July 2017. Criminal cases are heard in district and aimag (provincial) courts of first instance, with appeals to higher courts [@amarsanaa2014fledgling]. The system is inquisitorial, with judges making both guilt and sentencing determinations.

### 2.2 Data Extraction

I extracted structured data from each decision using a two-stage pipeline. The first stage used regular expressions to identify fields with consistent formatting: gender ("эрэгтэй"/"эмэгтэй"), age ("N настай"), education level, sentence type, and fine amounts. A 200-case validation sample (random seed 42) confirmed all regex-extracted fields exceeded 90% accuracy against independent manual coding: gender 94.3%, age 97.0%, education 97.2%, sentence type 92.1%, fine amount 95.2%.

The second stage used xAI's `grok-4-1-fast-non-reasoning` model (Grok 4.1 Fast) to extract fields requiring natural language interpretation from the full decision text: employment status, prior criminal record, aggravating and mitigating factors, victim characteristics, and injury severity. I processed all 77,968 valid cases through the xAI Batch API in 78 batches of 1,000 cases each, at a total cost of approximately $161. The LLM extraction succeeded on 77,364 cases (99.2%). This approach follows the text-mining methodology used by @zhuchkova2023exploring for Russian court decisions, adapted for Mongolian.

During publication preparation, three separate Codex coding sessions reviewed disjoint blocks of a fixed 300-decision sample, stratified by the five extracted sentence-type labels and extraction quality. The coding sessions had access to the saved source decisions and a protocol locked after a 25-case pilot, but not to the Grok or regex predictions; labels were hash-locked before scoring. This was prediction-blinded LLM-assisted source recoding, not human manual validation. Employment passed the pre-specified gate: accuracy was 0.978 and Cohen's kappa was 0.956 among 183 cases with both a locked reference label and a prediction. The four retained sentence categories were correct in 237 of 240 cases (98.75%). In contrast, none of the 60 records extracted as probation was a probation disposition: 58 were other dispositions, chiefly travel restrictions, and two were suspended sentences. Because the full source archive was unavailable for defensible case-level reclassification, I excluded all 5,796 records carrying that contaminated label. Factor extraction also did not pass. Aggravating-factor presence had F1 = 0.150 and count MAE = 1.035; mitigating-factor presence had F1 = 0.665 and count MAE = 1.933 (N = 283 readable sentencing rationales). The extractor had recall of 1.00 for both fields but low precision (0.081 aggravating; 0.498 mitigating), chiefly because it included offense elements, narrative facts, personal circumstances, and party arguments that the court did not expressly characterize as sentencing factors. All count-dependent analyses were therefore removed.

The LLM extraction produced large coverage improvements over regex alone. Prior criminal record went from 22% to 88% coverage. Sentence type went from 70% to 98%. Gender went from 66% to 88%. Where both methods produced values, I checked agreement: on the 50-case LLM pilot, all four disagreements between regex and LLM turned out to be LLM-correct.

### 2.3 Variables

**Dependent variable.** I converted the four validated sentence types to a unified severity scale measured in imprisonment-month equivalents, following the approach in @tacklingselection2020. The conversion uses the legal non-payment rate specified in Criminal Code Article 5.3.5 [@mongoliacriminalcode2015]: 15,000 MNT per day of imprisonment, or 450,000 MNT per month. Fines are divided by this rate. Imprisonment counts at face value. Suspended sentences are discounted to 0.5x their nominal duration, and community service uses the pre-registered conversion of 160 hours per month. Article 5.4.4 separately provides that eight unserved community-service hours convert to one day of imprisonment, implying 240 hours per 30-day month; I report that legally anchored alternative and upper/lower noncustodial weights as sensitivity analyses. Severity is winsorized at the 99th percentile within each conversion scenario. Article 5.3.2-.3 sets the personal fine range at no more than 40,000 units of 1,000 MNT each. Seventeen extracted fine dispositions exceeded 40 million MNT in the cleaned data, including eight in Sample A; because these may represent damages, restitution, legal-entity amounts, or extraction errors, I also report models excluding them.

**Independent variables.** The four demographic predictors correspond to the pre-registered hypotheses:

- *Female* (binary): coded from gender field. 13.4% of the primary sample is female.
- *Age* (continuous, plus a quadratic term): mean 35.3 years (SD 10.4). I set ages below 14 to missing as parsing errors and exclude known defendants younger than 18 because they face a distinct juvenile sentencing framework.
- *Education level* (ordinal, 1-5): primary, basic, secondary, vocational, higher. 60.3% of the primary sample has secondary education; 25.3% has higher education.
- *Employed* (binary): 63.6% of the primary sample is employed.

**Control variables.** Crime category classifies offenses into five groups based on Criminal Code chapter: violent (chapters 10-13), property (chapters 17-18), traffic (chapter 27), drug (chapter 20), and other. Prior criminal record is a binary indicator. All models include year and court fixed effects (45 courts in the primary sample).

### 2.4 Analytical Approach

**Validated models.** I estimate two models, each answering a different question about the relationship between demographics and sentencing.

*Model 1 (Total Association)* regresses severity on the four demographic predictors plus crime category, prior criminal record, and year and court fixed effects. This specification captures the total association between demographics and sentencing within broad crime type, without controlling for judge-assessed sentencing factors. It is the preferred specification.

*Model 2 (Same-Crime)* replaces the five broad crime categories with article-group fixed effects (91 groups, defined as the exact criminal code article when that article has at least 50 cases in the sample, otherwise grouped by chapter). This tests whether demographic associations persist within the same specific crime.

*Pre-registered factor specification.* The OSF specification added counts of aggravating and mitigating factors to Model 1. Those fields failed the pre-specified validation thresholds, and their errors were strongly directional rather than random. Estimating the specification would therefore control for an overinclusive mixture of offense facts and personal circumstances, not a validated count of formal sentencing factors. I do not interpret or present that model as evidence. This is a measurement-based deviation from the pre-registration, made under a protocol locked before predictions were exposed.

**Estimation.** The reported models use OLS with standard errors clustered at the court level [@cameron2015practitioners] to account for dependence within courts. The pre-registration specified HC3 standard errors; I therefore reproduce Model 1 with HC3 as an estimator sensitivity check. Coefficients are identical and the substantive inference is unchanged. I apply the Holm-Bonferroni correction [@holm1979simple] to the four primary hypothesis tests to control the family-wise error rate.

**Pre-registration.** The four hypotheses (H1: gender, H2: education, H3: age non-linearity, H4: employment) and the factor-count specification were registered on the Open Science Framework before data collection. The identifying registration URL is provided on the separate title page and omitted here for anonymous review. Model 1 is the primary reported specification. Known juvenile defendants are excluded as registered; the no-age robustness sample can exclude only cases known to be juveniles. The registered factor-count model is withheld from substantive interpretation because its required measures failed the locked evidence gate. Other documented deviations are the exclusion of the contaminated probation label and the use of court-clustered rather than HC3 standard errors in the reported table; the HC3 result is included in robustness. Holm-Bonferroni correction is reported for the four demographic hypotheses in Model 1.

### 2.5 Sample and Missing Data

After removing cases without usable decision text, dispositions outside the four validated categories, and all 5,796 records carrying the contaminated probation label, the cleaned dataset contains 69,527 cases. The primary analysis sample (Sample A) requires age 18 or older and complete data on all demographic predictors, crime category, prior record, and severity, leaving 29,132 cases (41.9% of the cleaned data). This excludes 127 known juveniles from the otherwise complete sample.

Table 2 reports missingness in the cleaned data. The binding constraint is age, which is missing for 42.4% of cases. Missing rates are increasing over time: age went from 32.5% missing in 2020 to 61.3% in 2025, as more recent court decisions appear to include less biographical detail. Missing data diagnostics suggest age missingness is associated with court location (Ulaanbaatar courts have better coverage) and employment status, but sentence type composition is similar regardless of age availability.

The primary sample over-represents fines (71.7% vs. 61.2% in the full data) and under-represents community service and suspended sentences, because severity coverage is structurally low for these sentence types. Our estimates apply to cases with quantifiable sentence severity, which over-represents fines and imprisonment relative to the full population of criminal dispositions.

As a robustness check, I re-estimate Model 1 on Sample B (N=35,995), which drops the age requirement, excludes known juveniles, and adds approximately 6,900 cases.

**Robustness checks.** In addition to the model hierarchy and Sample B, I report: (1) separate estimates for 2020-2022 and 2023-2025; (2) log severity; (3) a two-part imprisonment model; (4) individual case-level legal controls on the subsample where available; (5) alternative severity conversions, including Article 5.4's community-service equivalence; (6) the pre-registered HC3 estimator; (7) fine-only and imprisonment-only outcome models; and (8) exclusion of extracted fines above the Article 5.3 personal maximum.

## 3. Results

### 3.1 Descriptive Statistics

Table 1 summarizes the primary sample, while Figure 1 shows demographic and crime distributions in the cleaned data. The 29,132 adult cases in Sample A are 86.6% male, with a mean age of 35.3 years (SD 10.4). Most defendants have secondary education (60.3%) or higher (25.3%). About 64% are employed. Over a third (35.5%) have a prior criminal record.

Violent crimes make up the largest share (58.9%), followed by property (22.7%) and traffic (9.8%) offenses. The most common sentence is a fine (71.7%), followed by imprisonment (19.0%), community service (5.8%), and suspended sentences (3.5%).

Figure 2 shows sentence-type and severity distributions in the cleaned data, together with the yearly severity trend in Sample A. Severity is heavily right-skewed. The winsorized mean in Sample A is 9.5 month-equivalents but the median is only 1.6, reflecting the large number of relatively small fines at the low end and a long right tail of imprisonment sentences.

### 3.2 Bivariate Associations

Before turning to the regression models, Table 3 and Figure 3 report bivariate associations between each predictor and severity. Figure 4 shows how crime composition varies across demographic groups.

Employment shows the largest bivariate effect among the demographic variables (absolute Cohen's d = 0.394), with unemployed defendants receiving more severe sentences. Prior criminal record is similar in magnitude (d = 0.360). Gender shows a small effect (d = 0.059), though this is partly confounded by crime type composition. Education differs across categories in the bivariate comparison but does not show a stable linear gradient. Age has a weak positive linear relationship with severity; the unadjusted quadratic term is not significant (F = 0.28, p = 0.598).

### 3.3 Model Hierarchy

Table 4 and Figure 5 present the two validated core models on the primary adult sample (N = 29,132).

**Model 1 (Total Association).** Without aggravating or mitigating factor controls, three of the four demographic hypotheses reach significance after Holm-Bonferroni correction.

Employment is the strongest demographic predictor. Unemployed defendants receive sentences 6.3 month-equivalents more severe than employed defendants (B = -6.28, SE = 0.63, p < 0.001), controlling for crime type, prior record, and court. For scale, the coefficient is roughly four times the sample median of 1.6 month-equivalents, although a regression coefficient and the median of a skewed outcome describe different quantities.

Gender is significant: male defendants receive 1.5 more month-equivalents than female defendants (B = -1.51, SE = 0.30, p < 0.001). Prior criminal record adds 5.3 month-equivalents (B = 5.32, SE = 0.45, p < 0.001). Age shows a small but significant quadratic relationship (B_age = 0.30, p < 0.001; B_age-squared = -0.0027, p = 0.007), with severity increasing with age at a declining rate. Education does not reach significance (B = -0.24, p = 0.083).

In standardized terms, employment (-0.153) and prior criminal record (0.129) are the largest single-direction terms. The individual standardized terms for age (0.156) and age-squared (-0.112) partly offset one another. Gender (-0.026) and education (-0.013) are much smaller. Model 1 explains 8.0% of the variance in severity.

**Model 2 (Same-Crime).** Replacing the five broad crime categories with 91 article-group fixed effects raises R-squared to 0.625. The specific crime article explains most of the variation in sentence severity, which is expected (the penalty range for theft is fundamentally different from the range for assault).

The employment coefficient more than halves to -2.83 (SE = 0.30, p < 0.001). This attenuation is consistent with crime-article composition accounting for part of the Model 1 association, while a substantial association persists within the same article. It is not a formal causal decomposition. Gender attenuates to -0.56 (SE = 0.23, p = 0.015) but remains significant. Prior criminal record drops from 5.32 to 3.46 (p < 0.001). Education, which was not significant in Model 1, becomes significant at -0.25 (p = 0.002) once crime is controlled more precisely.

Under Holm-Bonferroni correction, Model 1 rejects H1 (gender), H3 (age non-linearity), and H4 (employment); H2 (education) is not rejected. The pre-registered factor-count model is not reported because the required measures failed validation.

### 3.4 Robustness

Table 5 and Figure 6 summarize the robustness checks. All are variations on Model 1 (no mediator controls), unless otherwise noted.

**Sample B (no age requirement, N = 35,995).** Dropping the age requirement adds approximately 6,900 cases and changes nothing: employment is -6.10 (p < 0.001), gender is -1.48 (p < 0.001), prior criminal is 5.55 (p < 0.001). The primary findings do not depend on the age-missing restriction.

**Temporal stability.** Splitting the sample at 2022, employment is -6.84 in 2020-2022 (N = 15,976) and -5.48 in 2023-2025 (N = 13,069), both significant at p < 0.001. Gender is -2.03 (p < 0.001) in the earlier period and -1.04 (p = 0.087) in the later. Employment is stable across both time windows; the gender estimate is less stable.

**Log-severity.** Fitting Model 1 with log(severity) as the dependent variable changes the interpretation to percentage terms. Employment corresponds to a 31.9% reduction in severity (B = -0.385, p < 0.001). Gender corresponds to an 18.8% reduction (B = -0.208, p < 0.001). Prior criminal record increases severity by 64.3% (B = 0.496, p < 0.001). Education reverses sign, becoming a small positive effect (+2.2%, p = 0.024). This instability across outcome scales is why I do not treat education as a finding.

**Severity and estimator sensitivity.** The employment coefficient remains negative and significant under the legally anchored 240-hour community-service conversion (B = -6.11), higher noncustodial weights (B = -5.74), lower noncustodial weights (B = -6.34), the pre-registered HC3 estimator (B = -6.28), and exclusion of the eight Sample A fines above 40 million MNT (B = -6.23); all p < 0.001. Within sentence types, however, the pattern differs. Employed defendants receive 9.4% shorter imprisonment terms (p < 0.001), while employed defendants receiving fines within the statutory personal-fine range have 4.1% larger fine amounts (p = 0.011). The aggregate employment gap is therefore robust to scale construction and the extreme fine tail but is not a uniform reduction in every sanction.

### 3.5 Imprisonment Decomposition

The two-part model separates the decision to imprison from the length of imprisonment. In stage 1 (logistic regression, N = 33,600), women are 42% less likely to be imprisoned than men (OR = 0.58, p < 0.001). Employed defendants are 60% less likely to be imprisoned (OR = 0.40, p < 0.001). Prior criminal record nearly triples the odds of imprisonment (OR = 2.86, p < 0.001). These are large effects on the incarceration decision (Online Resource 1, Table A3). Online Resource 1 also supplies the full robustness estimates, sample registry, and validation metrics.

In stage 2 (OLS on the 5,521 imprisoned defendants), the gender coefficient reverses: women who are imprisoned receive sentences 3.8 months longer than men (B = 3.78, p = 0.035). Employment remains negative and significant at -4.31 months (p < 0.001).

The gender reversal is a Simpson's paradox. Women receive lower overall severity (Model 1: -1.51 month-equivalents) and are much less likely to be imprisoned, yet the selected group of imprisoned women has longer conditional sentences. Unobserved differences in offense seriousness within the available crime controls are one possible explanation, but the data do not establish that mechanism. This decomposition is descriptive, not a formal selection correction (there is no exclusion restriction or inverse Mills ratio), and it shows that the aggregate gender pattern is concentrated in the imprisonment decision rather than uniformly present in sentence length.

## 4. Discussion

### 4.1 Employment and Personal Circumstances

Employment status is the strongest and most robust demographic predictor in this study. The coefficient attenuates from 6.3 month-equivalents in Model 1 to 2.8 with crime-article fixed effects in Model 2, indicating that article composition accounts for part, but not all, of the association. It remains negative under every cross-sentence severity conversion and in the imprisonment-only model, but the small positive fine-only association shows that it is not a universal reduction in sanction magnitude.

Prior US research has likewise linked unemployment or lower socioeconomic status to harsher sentencing outcomes, including incarceration decisions [@chiricos1991unemployment; @spohn2000imprisonment; @mustard2001racial]. Direct magnitude comparisons are not warranted because those studies use different jurisdictions, populations, outcomes, and model specifications. The Mongolian estimates therefore extend the qualitative pattern rather than establish that its size is larger or smaller than in the United States.

The comparison requires an important legal caveat. Employment is not one of the mitigating circumstances enumerated in Article 6.5.1 of Mongolia's Criminal Code. Article 6.1.2 does, however, direct courts to consider the defendant's broader personal circumstances (`хувийн байдал`) alongside offense circumstances, harm, mitigation, and aggravation. Employment may be considered within that broader inquiry, and individual decisions in the validation sample do so, but this study did not code a separate sample-wide measure of whether employment was expressly invoked in the sentencing rationale. The observed coefficient therefore cannot be described as either an expressly mandated mitigating effect or an extralegal effect.

Whether the association is equitable is a separate question. Unemployed defendants may face compounding disadvantages: less access to legal representation, less ability to pay fines (and fines account for 71% of sentences in the primary sample), and potentially more pretrial detention. Employment may also proxy for socioeconomic status more broadly. The observational estimates document disparity, not its legal or causal mechanism.

### 4.2 Measurement of Sentencing Factors

The failed factor validation is itself consequential for interpretation. The extractor found every source-recoded aggravating and mitigating circumstance in the validation sample, but it also labeled many legally and analytically different facts as factors. For aggravation, only 10 of 123 predicted-positive cases were reference positives; for mitigation, 127 of 255 were reference positives. The resulting counts substantially overstated the reference means.

This pattern explains why the unvalidated counts appeared so predictive in earlier exploratory work: they combined formal sentencing circumstances with offense severity, prior history, personal characteristics, and procedural facts. Their association with sentence severity cannot be interpreted as evidence that formal aggravating and mitigating factors mediate demographic disparities. The pre-registered specification will require a corrected full-dataset extraction and renewed validation before it can answer that question.

### 4.3 Gender: The Imprisonment Gateway

The gender coefficient in this study is smaller than a prominent US estimate: @starr2012estimating reported a 63% average gender disparity in federal sentence length. My total association (Model 1) is 1.51 month-equivalents and attenuates to 0.56 within crime article. Because the studies use different outcomes and institutional settings, this comparison is directional rather than a common-scale effect-size comparison. By the definitions used here, gender is a qualified finding.

The two-part imprisonment decomposition clarifies what is happening. Women in the sample are 42% less likely to be imprisoned (OR = 0.58), a large effect on the incarceration decision. But conditional on imprisonment, women receive sentences 3.8 months longer (p = 0.035). The overall severity gap is driven primarily by routing: women are diverted away from imprisonment at much higher rates, consistent with the "chivalry" or "paternalism" hypothesis described by @daly1995sex as operating at the incarceration threshold.

The reversal in the conditional model (longer sentences for imprisoned women) likely reflects selection. The women who are imprisoned despite the strong routing-away effect have committed offenses serious enough to overcome that threshold. They are a more selected group than imprisoned men. This is a descriptive finding, not a causal claim. I have no exclusion restriction to formally model the selection process, and I cannot rule out unobserved differences in offense severity within crime categories.

### 4.4 Education and Age

Education did not prove to be a reliable predictor. It reaches significance in Model 2 (within-crime, B = -0.25, p = 0.002) but not in Model 1 (p = 0.083). More importantly, it reverses sign in the log-severity model (+2.2%) and shows opposite effects across crime types in exploratory subgroup analysis. This instability means any education effect is heavily dependent on specification choices. Age non-linearity is statistically supported in Model 1 after multiplicity correction, but the effect is small and the unadjusted quadratic comparison is not significant.

@mustard2001racial found education differences in US federal sentencing, but direct comparison is difficult because the education categories, defendant populations, sentencing outcomes, and institutional settings differ. In the Mongolian primary sample, 60% of defendants have secondary education and 25% have higher education, leaving limited variation across the remaining categories.

The adjusted age terms imply the pre-registered shallow inverted-U pattern, peaking at approximately age 55. The age and age-squared standardized coefficients partly offset one another, and the bivariate quadratic test is not significant, so I treat this as a small qualified finding rather than a dominant result.

### 4.5 Limitations

Several limitations constrain what can be concluded from this analysis.

Age is missing for 42.4% of cases, and that rate is getting worse: 32.5% in 2020, 61.3% in 2025. The complete-case and adult requirements for the primary sample drop 58% of the cleaned data. Sample B (N = 35,995) confirms the main findings without the age requirement, but it can exclude only defendants known to be juveniles; I cannot rule out that age-missing cases differ systematically. More recent court decisions appear to include less biographical detail, and this trend may correlate with changes in sentencing practice that I cannot observe.

The severity measure is structurally missing for many community-service and suspended sentences because these dispositions often lack a natural "months" equivalent. The primary sample over-represents fines (71% vs. 61% in the full data). My estimates speak to cases with quantifiable severity, not to all criminal dispositions. The sentence-type audit also required excluding all records labeled probation; this conservative remedy avoids guessed reclassification but narrows the population represented by the estimates.

The employment variable, which is the headline finding, was extracted by a large language model. It passed prediction-blinded validation with 97.8% accuracy and kappa of 0.956 among jointly labeled cases, but employment status was absent or ambiguous in 109 of the 300 sampled decisions and the extractor produced a prediction for 95.8% of gold-labeled cases. The regression therefore remains a complete-case association among decisions with recorded employment information. In contrast, the aggravating and mitigating fields failed validation and are not used in reported analyses.

This is an observational study. I cannot control for case-level factors like demeanor, evidence quality, victim preferences, or the quality of legal representation. The `has_lawyer` variable exists in the data (70% coverage) but was not included in the primary models due to its likely endogeneity with sentencing outcomes. Disparity in this study means a documented association between demographics and sentencing, not proven discrimination.

The severity scale itself involves consequential choices. The fine conversion rate (450,000 MNT per month) is anchored to the Criminal Code, but the discount weight for suspended sentences (0.5x) and the pre-registered 160-hour community-service conversion are judgment calls. Article 5.4 implies 240 hours per imprisonment-month; using that conversion barely changes employment (B = -6.11). The extraction also produced 17 fine values above Article 5.3's personal maximum; excluding the eight such cases in Sample A barely changes employment (B = -6.23). The log-severity and within-sentence-type models nevertheless show that interpretation depends on outcome scale and sentence routing.

Finally, these findings are specific to Mongolia's legal system, criminal code, and judicial culture. The institutional context (inquisitorial system, no jury, and statutory consideration of a defendant's personal circumstances) limits generalizability to common-law systems, though it may generalize to other post-socialist jurisdictions with similar legal traditions.

## 5. Conclusion

I analyzed 29,132 criminal sentencing decisions from Mongolia's public court database, testing whether defendant demographics predict sentencing severity after controlling for crime type, prior record, and court effects.

Employment is the strongest demographic association. Unemployed defendants receive sentences 6.3 month-equivalents more severe in the total association model and 2.8 months more severe within the same crime article. The association survives every cross-sentence severity conversion and the pre-registered HC3 estimator, but its direction differs within fine and imprisonment cases, underscoring the importance of sentence routing. Employment is not enumerated as mitigation under Article 6.5.1, although it may form part of the personal circumstances considered under Article 6.1.2.

Gender operates through case routing. Women are 42% less likely to be imprisoned, but those who are imprisoned receive longer sentences than men. The overall severity gap is small (-1.51 months) and attenuates within crime article. Education is not a reliable predictor of sentencing severity in this data.

The pre-registered analysis of formal sentencing factors remains unanswered. The extracted counts failed the evidence gate because they systematically overincluded narrative and offense facts. Correcting and revalidating those fields is required before making claims about whether formal aggravating or mitigating circumstances mediate demographic associations.

Several questions remain open. Whether the employment disparity compounds other socioeconomic disadvantages (access to representation, ability to pay fines, pretrial detention) cannot be answered with this data alone. Whether the pattern holds for cases that are dismissed or acquitted before sentencing is unknown, since only completed cases appear in the database. And whether judicial training on employment status would reduce the disparity, or whether it is a reasonable proxy for recidivism risk, is a normative question beyond the scope of this analysis.

The analysis code, aggregate validation evidence, and a deidentified replication dataset have been deposited in a public repository. The identifying repository URL is provided on the separate title page and omitted here for anonymous review. Source decisions remain available through shuukh.mn, subject to the site's continued availability.

## References

::: {#refs}
:::

## Figure Captions

**Fig. 1** Defendant demographic characteristics and crime categories in the cleaned dataset: (a) age, (b) gender, (c) education, and (d) crime category; panel-specific sample sizes reflect available values

**Fig. 2** Sentencing outcomes: (a) sentence type, (b) winsorized severity distribution, (c) severity by sentence type, and (d) yearly mean severity with 95% confidence intervals in the primary adult analysis sample

**Fig. 3** Bivariate associations between sentence severity and (a) gender, (b) education, (c) age, and (d) employment in the primary adult analysis sample

**Fig. 4** Crime-category composition by (a) gender and (b) education; patterns supplement color to distinguish categories

**Fig. 5** Demographic coefficients across the total-association and same-crime models; points show coefficients and lines show 95% confidence intervals

**Fig. 6** Employment coefficients across month-equivalent robustness specifications; points show coefficients and lines show 95% confidence intervals; log-outcome and within-sentence proportional models are reported in Table 5 because their coefficients are not commensurable on this axis
