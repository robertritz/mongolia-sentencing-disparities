#!/usr/bin/env python3
"""Step 1: Load cleaned parquet, print comprehensive sample overview."""

from pathlib import Path
import sys

import pandas as pd

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import build_sample, build_two_part_stage2, load_analysis_data  # noqa: E402

# ============================================================
# LOAD
# ============================================================
df = load_analysis_data(DATA / "sentencing_clean.parquet")
print(f"Total cases in cleaned data: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

# ============================================================
# SAMPLE DEFINITIONS
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS SAMPLES")
print("=" * 60)

# Sample A: Primary model (pre-registered, complete case)
sample_a = build_sample(df, "sample_a")
print(f"\nSample A (primary model, all core vars): {len(sample_a)}")

# Sample B: Canonical robustness sample (no age requirement)
sample_b = build_sample(df, "sample_b")
print(f"Sample B (canonical no-age robustness): {len(sample_b)}")

# Two-part imprisonment model
sample_c1 = build_sample(df, "two_part_stage1")
sample_c2_months = build_two_part_stage2(sample_c1)
sample_c2 = sample_c1[sample_c1["sentence_type"] == "imprisonment"]
print(f"Two-part stage 1 (imprisonment decision): {len(sample_c1)}")
print(f"Two-part stage 2 pool (imprisoned): {len(sample_c2)}")
print(f"Two-part stage 2 model (with months): {len(sample_c2_months)}")

# ============================================================
# VARIABLE DISTRIBUTIONS — FULL SAMPLE
# ============================================================
print("\n" + "=" * 60)
print("VARIABLE DISTRIBUTIONS (Full cleaned sample, N={})".format(len(df)))
print("=" * 60)

# --- Sentence Type ---
print("\n--- Sentence Type ---")
st = df["sentence_type"].value_counts()
for t, c in st.items():
    print(f"  {t:25s} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Gender ---
print("\n--- Gender ---")
gen = df["gender"].value_counts(dropna=False)
for g, c in gen.items():
    label = str(g) if pd.notna(g) else "missing"
    print(f"  {label:25s} {c:>6} ({c/len(df)*100:.1f}%)")
print(f"  Female rate (of known): {(df['female']==1).sum()} / {df['female'].notna().sum()} "
      f"= {(df['female']==1).sum() / df['female'].notna().sum() * 100:.1f}%")

# --- Age ---
print("\n--- Age ---")
age = df["age"].dropna()
print(f"  N: {len(age)} ({len(age)/len(df)*100:.1f}%)")
print(f"  Mean: {age.mean():.1f}, Median: {age.median():.0f}, SD: {age.std():.1f}")
print(f"  Range: {age.min():.0f} - {age.max():.0f}")
print(f"  Quartiles: {age.quantile(0.25):.0f}, {age.quantile(0.5):.0f}, {age.quantile(0.75):.0f}")

# --- Education ---
print("\n--- Education Level ---")
edu = df["education_clean"].value_counts(dropna=False).sort_index()
for e, c in edu.items():
    label = str(e) if pd.notna(e) else "missing"
    print(f"  {label:25s} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Employment ---
print("\n--- Employed ---")
emp = df["employed"].value_counts(dropna=False)
for e, c in emp.items():
    label = str(e) if pd.notna(e) else "missing"
    print(f"  {label:25s} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Prior Criminal ---
print("\n--- Prior Criminal ---")
pc = df["prior_criminal"].value_counts(dropna=False)
for p, c in pc.items():
    label = str(p) if pd.notna(p) else "missing"
    print(f"  {label:25s} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Crime Category ---
print("\n--- Crime Category ---")
cc = df["crime_category"].value_counts(dropna=False)
for cat, c in cc.items():
    label = str(cat) if pd.notna(cat) else "missing"
    print(f"  {label:25s} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Year ---
print("\n--- Year ---")
yr = df["year"].value_counts().sort_index()
for y, c in yr.items():
    print(f"  {int(y):25d} {c:>6} ({c/len(df)*100:.1f}%)")

# --- Court location ---
print("\n--- Court Location ---")
ub = df["is_ub"].value_counts()
print(f"  UB (Ulaanbaatar): {ub.get(1, 0):>6} ({ub.get(1, 0)/len(df)*100:.1f}%)")
print(f"  Aimag (rural):    {ub.get(0, 0):>6} ({ub.get(0, 0)/len(df)*100:.1f}%)")
print(f"  Unique courts: {df['court_id'].nunique()}")

# ============================================================
# SEVERITY DISTRIBUTION
# ============================================================
print("\n" + "=" * 60)
print("SEVERITY SCORES")
print("=" * 60)

sev = df["severity"].dropna()
print(f"\nN with severity: {len(sev)} ({len(sev)/len(df)*100:.1f}%)")
print(f"Mean: {sev.mean():.2f}, Median: {sev.median():.2f}, SD: {sev.std():.2f}")
print(f"Range: {sev.min():.2f} - {sev.max():.1f}")
print(f"Winsorized max: {df['severity_winsorized'].max():.2f}")
print(f"Outliers flagged: {df['severity_outlier'].sum()}")

print("\nSeverity by sentence type:")
for st_name in ["fine", "imprisonment", "community_service", "suspended"]:
    mask = df["sentence_type"] == st_name
    s = df.loc[mask, "severity"]
    n_total = mask.sum()
    n_sev = s.notna().sum()
    if n_sev > 0:
        print(f"  {st_name:20s}: N={n_total:>6}, with severity={n_sev:>6} ({n_sev/n_total*100:.0f}%), "
              f"mean={s.mean():.2f}, median={s.median():.2f}")
    else:
        print(f"  {st_name:20s}: N={n_total:>6}, with severity=     0 (0%)")

# v2.0 controls coverage
print("\n" + "=" * 60)
print("CASE-LEVEL CONTROL COVERAGE")
print("=" * 60)
print("\n--- v2.0 Control Variables ---")
v2_vars = ["victim_relationship", "victim_minor", "crime_amount_mnt",
           "injury_severity", "intoxicated_at_crime", "has_lawyer",
           "plea_agreement", "plea_guilty", "restitution_paid", "time_served_days"]
for var in v2_vars:
    if var in df.columns:
        n = df[var].notna().sum()
        print(f"  {var:30s} {n:>6} ({n/len(df)*100:.1f}%)")
    else:
        print(f"  {var:30s} NOT IN DATA")

# ============================================================
# SAMPLE A PROFILE
# ============================================================
print("\n" + "=" * 60)
print("SAMPLE A PROFILE (Primary model, N={})".format(len(sample_a)))
print("=" * 60)

print("\n--- Demographics ---")
print(f"Female: {(sample_a['female'] == 1).sum()} ({(sample_a['female'] == 1).mean()*100:.1f}%)")
print(f"Age: mean={sample_a['age'].mean():.1f}, SD={sample_a['age'].std():.1f}")
print(f"Education: {sample_a['education_clean'].value_counts().to_dict()}")
print(f"Employed: {sample_a['employed'].sum()} ({(sample_a['employed'].mean()*100):.1f}%)")
print(f"Prior criminal: {sample_a['prior_criminal'].sum()} ({(sample_a['prior_criminal'].mean()*100):.1f}%)")

print("\n--- Crime ---")
print(sample_a["crime_category"].value_counts().to_string())

print("\n--- Sentence ---")
print(sample_a["sentence_type"].value_counts().to_string())
print(f"Severity: mean={sample_a['severity'].mean():.2f}, median={sample_a['severity'].median():.2f}")

print("\n--- Comparison: Full vs Sample A ---")
print(f"{'':25s} {'Full':>10} {'Sample A':>10} {'Diff':>8}")
print(f"{'N':25s} {len(df):>10} {len(sample_a):>10} {'':>8}")
print(f"{'Female %':25s} {(df['female']==1).sum()/df['female'].notna().sum()*100:>9.1f}% {(sample_a['female']==1).mean()*100:>9.1f}% "
      f"{(sample_a['female']==1).mean()*100 - (df['female']==1).sum()/df['female'].notna().sum()*100:>+7.1f}pp")
age_full = df['age'].dropna()
print(f"{'Mean age':25s} {age_full.mean():>10.1f} {sample_a['age'].mean():>10.1f} {sample_a['age'].mean()-age_full.mean():>+8.1f}")
sev_full = df['severity'].dropna()
print(f"{'Mean severity':25s} {sev_full.mean():>10.2f} {sample_a['severity'].mean():>10.2f} {sample_a['severity'].mean()-sev_full.mean():>+8.2f}")
