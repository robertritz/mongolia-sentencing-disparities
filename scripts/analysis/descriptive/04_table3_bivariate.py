#!/usr/bin/env python3
"""
Step 4: Table 3 — Bivariate Severity Analysis.

Tests each demographic predictor against severity (winsorized) individually.
Reports: group means, t-test/ANOVA, effect sizes (Cohen's d or eta-squared).

Uses Sample A (complete cases) for consistency with the primary model.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
TABLES = PROJECT / "tables"
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import build_sample, load_analysis_data  # noqa: E402

# Use the canonical preregistered adult Sample A.
df = load_analysis_data()
sa = build_sample(df, "sample_a")
sa["sev"] = sa["severity_winsorized"]

print(f"Sample A: N = {len(sa):,}")
print(f"Severity (winsorized): mean={sa['sev'].mean():.2f}, median={sa['sev'].median():.2f}, SD={sa['sev'].std():.2f}")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    s_pooled = np.sqrt(((n1 - 1) * g1.std()**2 + (n2 - 1) * g2.std()**2) / (n1 + n2 - 2))
    return (g1.mean() - g2.mean()) / s_pooled if s_pooled > 0 else 0

def eta_squared(groups):
    grand_mean = np.concatenate(groups).mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
    ss_total = sum(((g - grand_mean)**2).sum() for g in groups)
    return ss_between / ss_total if ss_total > 0 else 0

# ============================================================
# H1: GENDER
# ============================================================
print("\n" + "=" * 70)
print("H1: GENDER AND SEVERITY")
print("=" * 70)

male = sa[sa["female"] == 0]["sev"]
female = sa[sa["female"] == 1]["sev"]

print(f"\n  Male:   N={len(male):>6,}, mean={male.mean():>7.2f}, median={male.median():>6.2f}, SD={male.std():>6.2f}")
print(f"  Female: N={len(female):>6,}, mean={female.mean():>7.2f}, median={female.median():>6.2f}, SD={female.std():>6.2f}")

t, p = stats.ttest_ind(male, female)
d = cohens_d(male, female)
# Mann-Whitney for non-normal data
u, p_mw = stats.mannwhitneyu(male, female, alternative='two-sided')

print(f"\n  t-test: t={t:.3f}, p={p:.6f}")
print(f"  Mann-Whitney U: U={u:,.0f}, p={p_mw:.6f}")
print(f"  Cohen's d: {d:.3f} ({'males higher' if d > 0 else 'females higher'})")
print(f"  Mean difference: {male.mean() - female.mean():.2f} months")

# By crime category
print("\n  Gender gap by crime category:")
for cat in ["violent", "property", "traffic", "drug", "other"]:
    m = sa[(sa["female"] == 0) & (sa["crime_category"] == cat)]["sev"]
    f = sa[(sa["female"] == 1) & (sa["crime_category"] == cat)]["sev"]
    if len(f) >= 10:
        d_cat = cohens_d(m, f)
        print(f"    {cat:12s}: male={m.mean():.2f} (N={len(m):,}), female={f.mean():.2f} (N={len(f):,}), d={d_cat:.3f}")
    else:
        print(f"    {cat:12s}: female N={len(f)} (too small)")

# ============================================================
# H2: EDUCATION
# ============================================================
print("\n" + "=" * 70)
print("H2: EDUCATION AND SEVERITY")
print("=" * 70)

edu_labels = {0: "none", 1: "primary", 2: "basic", 3: "secondary", 4: "vocational", 5: "higher"}
groups = []
print()
for level in sorted(edu_labels.keys()):
    g = sa[sa["education_level"] == level]["sev"]
    if len(g) > 0:
        groups.append(g.values)
        print(f"  {edu_labels[level]:12s} (level {level}): N={len(g):>6,}, mean={g.mean():>7.2f}, median={g.median():>6.2f}")

F, p_anova = stats.f_oneway(*groups)
eta2 = eta_squared(groups)
print(f"\n  One-way ANOVA: F={F:.3f}, p={p_anova:.6f}")
print(f"  Eta-squared: {eta2:.4f}")

# Kruskal-Wallis (non-parametric)
H, p_kw = stats.kruskal(*groups)
print(f"  Kruskal-Wallis: H={H:.3f}, p={p_kw:.6f}")

# Linear trend test (correlation of education_level with severity)
education_r, p_corr = stats.spearmanr(sa["education_level"], sa["sev"])
print(f"  Spearman correlation (trend): r={education_r:.4f}, p={p_corr:.6f}")

# ============================================================
# H3: AGE (non-linear)
# ============================================================
print("\n" + "=" * 70)
print("H3: AGE AND SEVERITY")
print("=" * 70)

# Age brackets
brackets = [(18, 24, "18-24"), (25, 34, "25-34"), (35, 44, "35-44"),
            (45, 54, "45-54"), (55, 100, "55+")]
age_groups = []
print()
for lo, hi, label in brackets:
    g = sa[(sa["age"] >= lo) & (sa["age"] <= hi)]["sev"]
    age_groups.append(g.values)
    print(f"  {label:8s}: N={len(g):>6,}, mean={g.mean():>7.2f}, median={g.median():>6.2f}")

F, p_anova = stats.f_oneway(*age_groups)
eta2 = eta_squared(age_groups)
print(f"\n  One-way ANOVA: F={F:.3f}, p={p_anova:.6f}")
print(f"  Eta-squared: {eta2:.4f}")

# Correlation
r_lin, p_lin = stats.pearsonr(sa["age"], sa["sev"])
r_sp, p_sp = stats.spearmanr(sa["age"], sa["sev"])
print(f"  Pearson r (linear): {r_lin:.4f}, p={p_lin:.6f}")
print(f"  Spearman r (monotonic): {r_sp:.4f}, p={p_sp:.6f}")

# Check non-linearity: compare linear vs quadratic fit
from numpy.polynomial import polynomial as P
x = sa["age"].values.astype(float)
y = sa["sev"].values.astype(float)

# Fit linear
slope, intercept, r_val, p_val, se = stats.linregress(x, y)
ss_res_lin = np.sum((y - (intercept + slope * x))**2)

# Fit quadratic
coeffs = np.polyfit(x, y, 2)
y_pred_quad = np.polyval(coeffs, x)
ss_res_quad = np.sum((y - y_pred_quad)**2)

# F-test for improvement
n = len(x)
f_improve = ((ss_res_lin - ss_res_quad) / 1) / (ss_res_quad / (n - 3))
p_improve = 1 - stats.f.cdf(f_improve, 1, n - 3)
print(f"  Quadratic improvement F-test: F={f_improve:.3f}, p={p_improve:.6f}")
print(f"  Quadratic coefficients: a={coeffs[0]:.5f}, b={coeffs[1]:.4f}, c={coeffs[2]:.2f}")
peak_age = -coeffs[1] / (2 * coeffs[0]) if coeffs[0] != 0 else None
if peak_age:
    print(f"  Peak/trough at age: {peak_age:.1f}")

# ============================================================
# H4: EMPLOYMENT
# ============================================================
print("\n" + "=" * 70)
print("H4: EMPLOYMENT AND SEVERITY")
print("=" * 70)

employed = sa[sa["employed"] == True]["sev"]
unemployed = sa[sa["employed"] == False]["sev"]

print(f"\n  Employed:   N={len(employed):>6,}, mean={employed.mean():>7.2f}, median={employed.median():>6.2f}")
print(f"  Unemployed: N={len(unemployed):>6,}, mean={unemployed.mean():>7.2f}, median={unemployed.median():>6.2f}")

t, p = stats.ttest_ind(employed, unemployed)
d = cohens_d(employed, unemployed)
u, p_mw = stats.mannwhitneyu(employed, unemployed, alternative='two-sided')

print(f"\n  t-test: t={t:.3f}, p={p:.6f}")
print(f"  Mann-Whitney U: U={u:,.0f}, p={p_mw:.6f}")
print(f"  Cohen's d: {d:.3f} ({'employed higher' if d > 0 else 'unemployed higher'})")

# ============================================================
# ADDITIONAL CONTROLS
# ============================================================
print("\n" + "=" * 70)
print("ADDITIONAL PREDICTORS")
print("=" * 70)

# Prior criminal
print("\n--- Prior Criminal Record ---")
has_prior = sa[sa["prior_criminal"] == True]["sev"]
no_prior = sa[sa["prior_criminal"] == False]["sev"]
print(f"  With prior:    N={len(has_prior):>6,}, mean={has_prior.mean():>7.2f}")
print(f"  Without prior: N={len(no_prior):>6,}, mean={no_prior.mean():>7.2f}")
d = cohens_d(has_prior, no_prior)
t, p = stats.ttest_ind(has_prior, no_prior)
print(f"  t={t:.3f}, p={p:.6f}, d={d:.3f}")

# Crime category
print("\n--- Crime Category ---")
crime_groups = []
for cat in ["violent", "property", "traffic", "drug", "other"]:
    g = sa[sa["crime_category"] == cat]["sev"]
    crime_groups.append(g.values)
    print(f"  {cat:12s}: N={len(g):>6,}, mean={g.mean():>7.2f}, median={g.median():>6.2f}")
F, p = stats.f_oneway(*crime_groups)
eta2 = eta_squared(crime_groups)
print(f"  F={F:.3f}, p={p:.6f}, eta²={eta2:.4f}")

# Court location
print("\n--- Court Location (UB vs Aimag) ---")
ub_sev = sa[sa["is_ub"] == 1]["sev"]
aimag_sev = sa[sa["is_ub"] == 0]["sev"]
print(f"  UB:    N={len(ub_sev):>6,}, mean={ub_sev.mean():>7.2f}")
print(f"  Aimag: N={len(aimag_sev):>6,}, mean={aimag_sev.mean():>7.2f}")
d = cohens_d(ub_sev, aimag_sev)
t, p = stats.ttest_ind(ub_sev, aimag_sev)
print(f"  t={t:.3f}, p={p:.6f}, d={d:.3f}")

# Year trend
print("\n--- Year Trend ---")
for year in sorted(sa["year"].unique()):
    g = sa[sa["year"] == year]["sev"]
    print(f"  {int(year)}: N={len(g):>5,}, mean={g.mean():>7.2f}")
r, p = stats.spearmanr(sa["year"], sa["sev"])
print(f"  Spearman r (year trend): {r:.4f}, p={p:.6f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("BIVARIATE SUMMARY")
print("=" * 70)

age_summary = (
    "No significant quadratic improvement"
    if p_improve >= 0.05
    else f"Significant quadratic pattern, vertex at {peak_age:.0f} years"
)

print(f"""
  H1 (Gender):     Males receive higher severity (d={cohens_d(male, female):.3f})
  H2 (Education):  {'Higher education → lower severity' if education_r < 0 else 'Higher education → higher severity'} (Spearman r={education_r:.4f})
  H3 (Age):        {age_summary}
  H4 (Employment): {'Employed receive lower severity' if cohens_d(employed, unemployed) < 0 else 'Unemployed receive lower severity'} (d={cohens_d(employed, unemployed):.3f})

  Strongest bivariate predictors:
  - Crime category (eta²={eta_squared(crime_groups):.4f})
  - Prior criminal record (d={cohens_d(has_prior, no_prior):.3f})
  - Gender (d={cohens_d(male, female):.3f})
  - Court location (d={cohens_d(ub_sev, aimag_sev):.3f})
""")

# ============================================================
# EXPORT
# ============================================================
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)

rows = [
    {"variable": "Female (H1)", "group1": "Male", "group2": "Female",
     "mean1": male.mean(), "mean2": female.mean(),
     "test": "t-test", "statistic": stats.ttest_ind(male, female)[0],
     "p_value": stats.ttest_ind(male, female)[1],
     "effect_size": cohens_d(male, female), "effect_type": "Cohen's d"},
    {"variable": "Education (H2)", "group1": "All levels", "group2": "",
     "mean1": "", "mean2": "",
     "test": "ANOVA", "statistic": stats.f_oneway(*groups)[0],
     "p_value": stats.f_oneway(*groups)[1],
     "effect_size": eta_squared(groups), "effect_type": "eta²"},
    {"variable": "Age non-linear (H3)", "group1": "Linear", "group2": "Quadratic",
     "mean1": "", "mean2": "",
     "test": "Quadratic F", "statistic": f_improve,
     "p_value": p_improve,
     "effect_size": r_lin, "effect_type": "Pearson r"},
    {"variable": "Employed (H4)", "group1": "Employed", "group2": "Unemployed",
     "mean1": employed.mean(), "mean2": unemployed.mean(),
     "test": "t-test", "statistic": stats.ttest_ind(employed, unemployed)[0],
     "p_value": stats.ttest_ind(employed, unemployed)[1],
     "effect_size": cohens_d(employed, unemployed), "effect_type": "Cohen's d"},
    {"variable": "Prior criminal", "group1": "With", "group2": "Without",
     "mean1": has_prior.mean(), "mean2": no_prior.mean(),
     "test": "t-test", "statistic": stats.ttest_ind(has_prior, no_prior)[0],
     "p_value": stats.ttest_ind(has_prior, no_prior)[1],
     "effect_size": cohens_d(has_prior, no_prior), "effect_type": "Cohen's d"},
    {"variable": "Crime category", "group1": "5 categories", "group2": "",
     "mean1": "", "mean2": "",
     "test": "ANOVA", "statistic": stats.f_oneway(*crime_groups)[0],
     "p_value": stats.f_oneway(*crime_groups)[1],
     "effect_size": eta_squared(crime_groups), "effect_type": "eta²"},
]

pd.DataFrame(rows).to_csv(TABLES / "table3_bivariate.csv", index=False)
print(f"\nSaved to {TABLES / 'table3_bivariate.csv'}")
