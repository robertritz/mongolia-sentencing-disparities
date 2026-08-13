#!/usr/bin/env python3
"""
Step 1: Validated Core Models.

Model 1 (Total Association):
  No aggravating/mitigating mediators. Captures full demographic effect
  within broad crime type.

Model 2 (Same-Crime):
  Article-group FE instead of broad crime categories. Captures
  within-crime-article demographic effect.

The pre-registered specification adding aggravating/mitigating counts is not
estimated for publication because those extracted fields failed the locked
manual-validation thresholds.

All on Sample A, OLS with court-clustered SE.

Outputs:
- tables/table4_model_hierarchy.csv
- tables/table4b_variance_decomposition.csv
- tables/table4c_holm_bonferroni.csv
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import (  # noqa: E402
    add_article_group,
    build_sample,
    ensure_model_dtypes,
    load_analysis_data,
)

# ── FORMULAS ──────────────────────────────────────────────────

MODEL1_FORMULA = (
    "sev ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year) + C(court_id)"
)

MODEL2_FORMULA = (
    "sev ~ female + age + age_sq + education_level + employed + "
    "C(article_group) + prior_criminal + "
    "C(year) + C(court_id)"
)

MODEL_NAMES = {
    1: "Model 1 - Total Association",
    2: "Model 2 - Same-Crime",
}

HYPOTHESIS_VARS = [
    "female", "age", "age_sq", "education_level", "employed", "prior_criminal",
]

PRIMARY_HYPOTHESES = [
    ("H1 (Gender)", "female"),
    ("H2 (Education)", "education_level"),
    ("H3 (Age non-linear)", "age_sq"),
    ("H4 (Employment)", "employed"),
]


# ── HELPERS ───────────────────────────────────────────────────

def fit_clustered_ols(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster",
        cov_kwds={"groups": data["court_id"]},
    )


def extract_coefs(
    model, variables: list[str], model_name: str, n: int, r_squared: float,
) -> list[dict]:
    rows = []
    for var in variables:
        if var not in model.params.index:
            continue
        ci = model.conf_int().loc[var]
        rows.append({
            "model": model_name,
            "variable": var,
            "coefficient": model.params[var],
            "se": model.bse[var],
            "t": model.tvalues[var],
            "p": model.pvalues[var],
            "ci_low": ci[0],
            "ci_high": ci[1],
            "r_squared": r_squared,
            "n": n,
        })
    return rows


def holm_bonferroni(model, tests: list[tuple[str, str]], model_name: str) -> pd.DataFrame:
    p_values = [(name, var, model.pvalues[var]) for name, var in tests]
    p_sorted = sorted(p_values, key=lambda x: x[2])
    k = len(tests)
    rows = []
    for rank, (name, var, p) in enumerate(p_sorted):
        threshold = 0.05 / (k - rank)
        rows.append({
            "model": model_name,
            "hypothesis": name,
            "variable": var,
            "p": p,
            "rank": rank + 1,
            "threshold": threshold,
            "reject": p < threshold,
        })
    return pd.DataFrame(rows)


def print_model_results(model, model_name: str, variables: list[str]) -> None:
    print(f"\n{'=' * 70}")
    print(f"{model_name}")
    print(f"{'=' * 70}")
    print(f"R² = {model.rsquared:.4f}, Adj R² = {model.rsquared_adj:.4f}, N = {model.nobs:.0f}")
    print(f"\n{'Variable':<20} {'Coeff':>8} {'SE':>8} {'p':>10} {'95% CI':>22}")
    print("-" * 70)
    for var in variables:
        if var not in model.params.index:
            continue
        coef = model.params[var]
        se = model.bse[var]
        p = model.pvalues[var]
        ci = model.conf_int().loc[var]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{var:<20} {coef:>8.3f}{stars:<4} {se:>8.3f} {p:>10.4f} [{ci[0]:>8.3f}, {ci[1]:>8.3f}]")


# ── MAIN ──────────────────────────────────────────────────────

def main() -> None:
    df = load_analysis_data(DATA / "sentencing_clean.parquet")
    sa = build_sample(df, "sample_a")
    sa["sev"] = sa["severity_winsorized"]
    sa = ensure_model_dtypes(
        sa,
        ["female", "age", "age_sq", "education_level", "employed",
         "prior_criminal"],
    )
    sa = add_article_group(sa, based_on=sa, min_cases=50)

    print(f"Sample A: N = {len(sa):,}")
    print(f"DV (severity winsorized): mean={sa['sev'].mean():.2f}, SD={sa['sev'].std():.2f}")
    print(f"Courts: {sa['court_id'].nunique()}, Article groups: {sa['article_group'].nunique()}")

    # ── FIT MODELS ────────────────────────────────────────────

    m1 = fit_clustered_ols(MODEL1_FORMULA, sa)
    m2 = fit_clustered_ols(MODEL2_FORMULA, sa)

    print_model_results(m1, MODEL_NAMES[1], HYPOTHESIS_VARS)
    print_model_results(m2, MODEL_NAMES[2], HYPOTHESIS_VARS)

    # ── HOLM-BONFERRONI ───────────────────────────────────────

    hb1 = holm_bonferroni(m1, PRIMARY_HYPOTHESES, MODEL_NAMES[1])

    for label, hb in [("Model 1", hb1)]:
        print(f"\n{'=' * 70}")
        print(f"HOLM-BONFERRONI: {label}")
        print(f"{'=' * 70}")
        for _, row in hb.iterrows():
            status = "REJECT" if row["reject"] else "fail"
            print(f"  {row['hypothesis']:<25} p={row['p']:.4f}  threshold={row['threshold']:.4f}  {status}")

    # ── STANDARDIZED COEFFICIENTS (Model 1) ───────────────────

    print(f"\n{'=' * 70}")
    print("STANDARDIZED COEFFICIENTS (Model 1)")
    print(f"{'=' * 70}")

    std_vars = ["female", "age", "age_sq", "education_level", "employed", "prior_criminal"]
    sa_std = sa.copy()
    for var in std_vars:
        sa_std[var] = (sa_std[var] - sa_std[var].mean()) / sa_std[var].std()
    sa_std["sev"] = (sa_std["sev"] - sa_std["sev"].mean()) / sa_std["sev"].std()

    m1_std = smf.ols(MODEL1_FORMULA, data=sa_std).fit()

    std_results = [(var, abs(m1_std.params[var]), m1_std.params[var]) for var in std_vars]
    std_results.sort(key=lambda x: x[1], reverse=True)
    for rank, (var, _, beta) in enumerate(std_results, 1):
        print(f"  {rank}. {var:<20}: {beta:>8.4f}")

    # ── VARIANCE DECOMPOSITION ────────────────────────────────

    print(f"\n{'=' * 70}")
    print("VARIANCE DECOMPOSITION")
    print(f"{'=' * 70}")

    decomp_steps = [
        ("Demographics only",
         "sev ~ female + age + age_sq + education_level + employed"),
        ("+ Crime + prior criminal",
         "sev ~ female + age + age_sq + education_level + employed + "
         "C(crime_category, Treatment(reference='violent')) + prior_criminal"),
        ("+ Year/Court FE (= Model 1)",
         MODEL1_FORMULA),
    ]

    decomp_rows = []
    prev_r2 = 0
    for block_name, formula in decomp_steps:
        m = smf.ols(formula, data=sa).fit()
        delta = m.rsquared - prev_r2
        decomp_rows.append({
            "block": block_name,
            "r_squared": m.rsquared,
            "delta_r_squared": delta,
        })
        print(f"  {block_name:<40}: R²={m.rsquared:.4f} (Δ={delta:+.4f})")
        prev_r2 = m.rsquared

    # ── EXPORT ────────────────────────────────────────────────

    n = len(sa)
    all_coefs = []
    all_coefs.extend(extract_coefs(m1, HYPOTHESIS_VARS, MODEL_NAMES[1], n, m1.rsquared))
    all_coefs.extend(extract_coefs(m2, HYPOTHESIS_VARS, MODEL_NAMES[2], n, m2.rsquared))

    pd.DataFrame(all_coefs).to_csv(TABLES / "table4_model_hierarchy.csv", index=False)
    pd.DataFrame(decomp_rows).to_csv(TABLES / "table4b_variance_decomposition.csv", index=False)
    hb1.to_csv(TABLES / "table4c_holm_bonferroni.csv", index=False)

    print(f"\nSaved {TABLES / 'table4_model_hierarchy.csv'}")
    print(f"Saved {TABLES / 'table4b_variance_decomposition.csv'}")
    print(f"Saved {TABLES / 'table4c_holm_bonferroni.csv'}")


if __name__ == "__main__":
    main()
