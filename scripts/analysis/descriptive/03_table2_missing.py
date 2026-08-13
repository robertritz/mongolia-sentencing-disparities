#!/usr/bin/env python3
"""
Step 3: Table 2 — Missing Data Analysis.

Reports:
- Missing rates by variable
- Missing rates by year (temporal pattern)
- MAR diagnostics: compare demographics for cases with/without key missing variables
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
TABLES = PROJECT / "tables"

df = pd.read_parquet(DATA / "sentencing_clean.parquet")

# ============================================================
# OVERALL MISSING RATES
# ============================================================
print("=" * 70)
print("TABLE 2A: Missing Data Rates")
print("=" * 70)

core_vars = [
    ("gender", "Gender"),
    ("age", "Age"),
    ("education_level", "Education"),
    ("employed", "Employment"),
    ("prior_criminal", "Prior record"),
    ("crime_category", "Crime category"),
    ("sentence_type", "Sentence type"),
    ("severity", "Severity score"),
    ("sentence_months", "Sentence months"),
    ("sentence_fine_mnt", "Fine amount"),
]

print(f"\n{'Variable':<25} {'N Present':>10} {'N Missing':>10} {'% Missing':>10}")
print("-" * 57)
for var, label in core_vars:
    present = df[var].notna().sum()
    missing = df[var].isna().sum()
    pct = missing / len(df) * 100
    print(f"{label:<25} {present:>10,} {missing:>10,} {pct:>9.1f}%")

# ============================================================
# MISSING BY YEAR
# ============================================================
print("\n" + "=" * 70)
print("TABLE 2B: Missing Rates by Year (% missing)")
print("=" * 70)

year_vars = ["gender", "age", "education_level", "employed", "prior_criminal", "severity"]

header = f"{'Year':>6}"
for var in year_vars:
    header += f" {var:>12}"
print(header)
print("-" * (6 + 13 * len(year_vars)))

for year in sorted(df["year"].unique()):
    yr_df = df[df["year"] == year]
    row = f"{int(year):>6}"
    for var in year_vars:
        pct = yr_df[var].isna().mean() * 100
        row += f" {pct:>11.1f}%"
    n = len(yr_df)
    row += f"  (N={n:,})"
    print(row)

# Overall
row = f"{'Total':>6}"
for var in year_vars:
    pct = df[var].isna().mean() * 100
    row += f" {pct:>11.1f}%"
print(row)

# ============================================================
# MAR DIAGNOSTICS
# ============================================================
print("\n" + "=" * 70)
print("MAR DIAGNOSTICS: Are missing values associated with observables?")
print("=" * 70)

def mar_test(df, missing_var, test_var, test_type="continuous"):
    """Test if missingness of missing_var is associated with test_var."""
    has_val = df[df[missing_var].notna()]
    no_val = df[df[missing_var].isna()]

    if test_type == "continuous":
        s1 = has_val[test_var].dropna()
        s2 = no_val[test_var].dropna()
        if len(s1) < 10 or len(s2) < 10:
            return None
        t, p = stats.ttest_ind(s1, s2)
        d = (s1.mean() - s2.mean()) / np.sqrt((s1.std()**2 + s2.std()**2) / 2)
        return {"mean_present": s1.mean(), "mean_missing": s2.mean(),
                "t": t, "p": p, "cohens_d": d, "n1": len(s1), "n2": len(s2)}
    elif test_type == "binary":
        s1 = has_val[test_var].dropna()
        s2 = no_val[test_var].dropna()
        if len(s1) < 10 or len(s2) < 10:
            return None
        p1 = s1.mean()
        p2 = s2.mean()
        # Two-proportion z-test
        p_pool = (s1.sum() + s2.sum()) / (len(s1) + len(s2))
        if p_pool == 0 or p_pool == 1:
            return None
        se = np.sqrt(p_pool * (1 - p_pool) * (1/len(s1) + 1/len(s2)))
        z = (p1 - p2) / se
        p_val = 2 * (1 - stats.norm.cdf(abs(z)))
        return {"pct_present": p1*100, "pct_missing": p2*100,
                "z": z, "p": p_val, "n1": len(s1), "n2": len(s2)}

# Key missing variables to diagnose
print("\n--- Is missingness of AGE associated with observables? ---")
for test_var, label, ttype in [
    ("female", "Female", "binary"),
    ("prior_criminal", "Prior criminal", "binary"),
    ("employed", "Employed", "binary"),
    ("is_ub", "UB court", "binary"),
]:
    result = mar_test(df, "age", test_var, ttype)
    if result and ttype == "binary":
        print(f"  {label:20s}: present={result['pct_present']:.1f}%, "
              f"missing={result['pct_missing']:.1f}%, "
              f"z={result['z']:.2f}, p={result['p']:.4f}")

# Sentence type composition for age missing vs present
print("\n  Sentence type composition:")
for st in ["fine", "imprisonment", "community_service", "suspended"]:
    has_age = (df[df["age"].notna()]["sentence_type"] == st).mean() * 100
    no_age = (df[df["age"].isna()]["sentence_type"] == st).mean() * 100
    print(f"    {st:20s}: age present={has_age:.1f}%, age missing={no_age:.1f}%, diff={no_age-has_age:+.1f}pp")

print("\n--- Is missingness of SEVERITY associated with observables? ---")
for test_var, label, ttype in [
    ("female", "Female", "binary"),
    ("age", "Age", "continuous"),
    ("prior_criminal", "Prior criminal", "binary"),
    ("is_ub", "UB court", "binary"),
]:
    result = mar_test(df, "severity", test_var, ttype)
    if result and ttype == "binary":
        print(f"  {label:20s}: present={result['pct_present']:.1f}%, "
              f"missing={result['pct_missing']:.1f}%, "
              f"z={result['z']:.2f}, p={result['p']:.4f}")
    elif result and ttype == "continuous":
        print(f"  {label:20s}: present={result['mean_present']:.1f}, "
              f"missing={result['mean_missing']:.1f}, "
              f"t={result['t']:.2f}, p={result['p']:.4f}, d={result['cohens_d']:.3f}")

# Sentence type for severity missing vs present
print("\n  Sentence type composition:")
for st in ["fine", "imprisonment", "community_service", "suspended"]:
    has_sev = (df[df["severity"].notna()]["sentence_type"] == st).mean() * 100
    no_sev = (df[df["severity"].isna()]["sentence_type"] == st).mean() * 100
    print(f"    {st:20s}: sev present={has_sev:.1f}%, sev missing={no_sev:.1f}%, diff={no_sev-has_sev:+.1f}pp")

print("\n--- Is missingness of EDUCATION associated with observables? ---")
for test_var, label, ttype in [
    ("female", "Female", "binary"),
    ("age", "Age", "continuous"),
    ("prior_criminal", "Prior criminal", "binary"),
    ("is_ub", "UB court", "binary"),
]:
    result = mar_test(df, "education_level", test_var, ttype)
    if result and ttype == "binary":
        print(f"  {label:20s}: present={result['pct_present']:.1f}%, "
              f"missing={result['pct_missing']:.1f}%, "
              f"z={result['z']:.2f}, p={result['p']:.4f}")
    elif result and ttype == "continuous":
        print(f"  {label:20s}: present={result['mean_present']:.1f}, "
              f"missing={result['mean_missing']:.1f}, "
              f"t={result['t']:.2f}, p={result['p']:.4f}, d={result['cohens_d']:.3f}")

# ============================================================
# PAIRWISE MISSING PATTERNS
# ============================================================
print("\n" + "=" * 70)
print("PAIRWISE MISSING PATTERNS")
print("=" * 70)

key_vars = ["gender", "age", "education_level", "employed", "prior_criminal", "severity"]
print("\nCases with complete data for each pair:")
print(f"{'':>20}", end="")
for v in key_vars:
    print(f"{v:>14}", end="")
print()

for v1 in key_vars:
    print(f"{v1:>20}", end="")
    for v2 in key_vars:
        both = df[[v1, v2]].notna().all(axis=1).sum()
        print(f"{both:>14,}", end="")
    print()

# Complete case counts for progressively adding variables
print("\nProgressive complete case counts:")
cumulative = df.copy()
for var in ["crime_category", "prior_criminal", "female", "severity",
            "employed", "education_level", "age"]:
    cumulative = cumulative.dropna(subset=[var])
    print(f"  + {var:20s}: N = {len(cumulative):>6,}")

# ============================================================
# EXPORT
# ============================================================
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)

# Table 2A: overall missing rates
rows = []
for var, label in core_vars:
    present = df[var].notna().sum()
    missing = df[var].isna().sum()
    rows.append({"variable": label, "n_present": present, "n_missing": missing,
                 "pct_missing": missing / len(df) * 100})
pd.DataFrame(rows).to_csv(TABLES / "table2a_missing_rates.csv", index=False)

# Table 2B: missing by year
rows = []
for year in sorted(df["year"].unique()):
    yr_df = df[df["year"] == year]
    row = {"year": int(year), "n": len(yr_df)}
    for var in year_vars:
        row[f"{var}_pct_missing"] = yr_df[var].isna().mean() * 100
    rows.append(row)
pd.DataFrame(rows).to_csv(TABLES / "table2b_missing_by_year.csv", index=False)

print(f"\nSaved table2a_missing_rates.csv and table2b_missing_by_year.csv")
