#!/usr/bin/env python3
"""
Step 2: Table 1 — Sample Characteristics.

Three-panel table comparing full cleaned sample, Sample A (primary model),
and Sample B (canonical no-age robustness).

Output: tables/table1_characteristics.csv + console summary
"""

from pathlib import Path
import sys

import pandas as pd
from scipy import stats

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import SAMPLE_A_REQUIRED, build_sample, load_analysis_data  # noqa: E402

df = load_analysis_data(DATA / "sentencing_clean.parquet")

# Define samples
sample_a = build_sample(df, "sample_a")
sample_b = build_sample(df, "sample_b")

samples = {
    "Full (N={:,})".format(len(df)): df,
    "Sample A (N={:,})".format(len(sample_a)): sample_a,
    "Sample B (N={:,})".format(len(sample_b)): sample_b,
}

# ============================================================
# BUILD TABLE
# ============================================================
rows = []

def add_row(label, values):
    rows.append({"Variable": label, **dict(zip(samples.keys(), values))})

def pct(n, total):
    return f"{n:,} ({n/total*100:.1f}%)" if total > 0 else "—"

def mean_sd(series):
    s = series.dropna()
    if len(s) == 0:
        return "—"
    return f"{s.mean():.1f} ({s.std():.1f})"

def median_iqr(series):
    s = series.dropna()
    if len(s) == 0:
        return "—"
    return f"{s.median():.1f} [{s.quantile(0.25):.1f}–{s.quantile(0.75):.1f}]"

# --- Panel A: Demographics ---
add_row("Panel A: Demographics", ["", "", ""])

# N
add_row("  N", [f"{len(s):,}" for s in samples.values()])

# Female
add_row("  Female", [
    pct((s["female"] == 1).sum(), s["female"].notna().sum())
    for s in samples.values()
])

# Age
add_row("  Age, mean (SD)", [mean_sd(s["age"]) for s in samples.values()])
add_row("  Age, median [IQR]", [median_iqr(s["age"]) for s in samples.values()])

# Education
edu_labels = [("none", "None"), ("primary", "Primary"), ("basic", "Basic"),
              ("secondary", "Secondary"), ("vocational", "Vocational"), ("higher", "Higher")]
add_row("  Education", ["", "", ""])
for code, label in edu_labels:
    add_row(f"    {label}", [
        pct((s["education_clean"] == code).sum(), s["education_clean"].notna().sum())
        for s in samples.values()
    ])

# Employment
add_row("  Employed", [
    pct(s["employed"].sum(), s["employed"].notna().sum())
    for s in samples.values()
])

# Prior criminal
add_row("  Prior criminal record", [
    pct(s["prior_criminal"].sum(), s["prior_criminal"].notna().sum())
    for s in samples.values()
])

# --- Panel B: Crime Characteristics ---
add_row("", ["", "", ""])
add_row("Panel B: Crime", ["", "", ""])

crime_labels = [("violent", "Violent"), ("property", "Property"),
                ("traffic", "Traffic"), ("drug", "Drug"), ("other", "Other")]
for code, label in crime_labels:
    add_row(f"  {label}", [
        pct((s["crime_category"] == code).sum(), s["crime_category"].notna().sum())
        for s in samples.values()
    ])

# --- Panel C: Sentencing ---
add_row("", ["", "", ""])
add_row("Panel C: Sentencing", ["", "", ""])

st_labels = [("fine", "Fine"), ("imprisonment", "Imprisonment"),
             ("community_service", "Community service"),
             ("suspended", "Suspended")]
for code, label in st_labels:
    add_row(f"  {label}", [
        pct((s["sentence_type"] == code).sum(), len(s))
        for s in samples.values()
    ])

# Severity
add_row("  Severity (winsorized), mean (SD)", [
    mean_sd(s["severity_winsorized"]) for s in samples.values()
])
add_row("  Severity (winsorized), median [IQR]", [
    median_iqr(s["severity_winsorized"]) for s in samples.values()
])

# --- Panel D: Context ---
add_row("", ["", "", ""])
add_row("Panel D: Context", ["", "", ""])

add_row("  UB (Ulaanbaatar)", [
    pct((s["is_ub"] == 1).sum(), len(s))
    for s in samples.values()
])

add_row("  Unique courts", [
    str(s["court_id"].nunique()) for s in samples.values()
])

yr_range = [
    f"{int(s['year'].min())}–{int(s['year'].max())}" for s in samples.values()
]
add_row("  Year range", yr_range)

# ============================================================
# OUTPUT
# ============================================================
table = pd.DataFrame(rows)

# Console output
print("=" * 90)
print("TABLE 1: Sample Characteristics")
print("=" * 90)
for _, row in table.iterrows():
    var = row["Variable"]
    vals = [str(row[col]) for col in table.columns[1:]]
    if var.startswith("Panel") or var == "":
        print(f"\n{var}")
    else:
        print(f"{var:45s} {vals[0]:>15s} {vals[1]:>15s} {vals[2]:>15s}")

# CSV export
table.to_csv(TABLES / "table1_characteristics.csv", index=False)
print(f"\nSaved to {TABLES / 'table1_characteristics.csv'}")

# ============================================================
# SAMPLE A vs FULL: Selection bias check
# ============================================================
print("\n" + "=" * 90)
print("SELECTION BIAS CHECK: Full sample vs Sample A")
print("=" * 90)

# Gender
full_female = (df["female"] == 1).sum() / df["female"].notna().sum()
sa_female = (sample_a["female"] == 1).mean()
chi2_tab = pd.crosstab(
    df["female"].notna() & df[list(SAMPLE_A_REQUIRED)].notna().all(axis=1),
    df["female"]
)
if chi2_tab.shape == (2, 2):
    chi2, p_chi2, _, _ = stats.chi2_contingency(chi2_tab)
    print(f"Female: full={full_female*100:.1f}%, A={sa_female*100:.1f}%, chi2={chi2:.2f}, p={p_chi2:.4f}")

# Age
full_age = df["age"].dropna()
sa_age = sample_a["age"]
t_age, p_age = stats.ttest_ind(full_age, sa_age)
print(f"Age: full mean={full_age.mean():.1f}, A mean={sa_age.mean():.1f}, t={t_age:.2f}, p={p_age:.4f}")

# Crime category
for cat in ["violent", "property", "traffic", "drug", "other"]:
    full_pct = (df["crime_category"] == cat).sum() / df["crime_category"].notna().sum() * 100
    sa_pct = (sample_a["crime_category"] == cat).sum() / len(sample_a) * 100
    print(f"Crime {cat:10s}: full={full_pct:.1f}%, A={sa_pct:.1f}%, diff={sa_pct-full_pct:+.1f}pp")

# Sentence type
for st in ["fine", "imprisonment", "community_service", "suspended"]:
    full_pct = (df["sentence_type"] == st).sum() / len(df) * 100
    sa_pct = (sample_a["sentence_type"] == st).sum() / len(sample_a) * 100
    print(f"Sentence {st:20s}: full={full_pct:.1f}%, A={sa_pct:.1f}%, diff={sa_pct-full_pct:+.1f}pp")
