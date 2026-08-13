#!/usr/bin/env python3
"""
Step 2: Focused robustness checks.

1. Sample B (no age requirement)
2. Temporal split (2020-2022 vs 2023-2025)
3. Log-severity (alternative DV scale)
4. Two-part imprisonment model (descriptive decomposition)
5. Legal-controls subsample (individual case controls replacing agg/mit)
6. Severity conversion, estimator, and within-sentence-type sensitivity
7. Statutory personal-fine range sensitivity

Outputs:
- tables/table5_robustness.csv
- tables/table5b_two_part_stage1.csv
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
    LEGAL_CONTROL_COLS,
    build_sample,
    build_two_part_stage2,
    ensure_model_dtypes,
    load_analysis_data,
)

# ── FORMULAS ──────────────────────────────────────────────────

MODEL1_FORMULA = (
    "sev ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year) + C(court_id)"
)

MODEL1_NO_AGE_FORMULA = (
    "sev ~ female + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year) + C(court_id)"
)

LOG_MODEL1_FORMULA = (
    "log_sev ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year) + C(court_id)"
)

LOGIT_STAGE1_FORMULA = (
    "imprisoned ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year)"
)

OLS_STAGE2_FORMULA = (
    "months ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "C(year) + C(court_id)"
)

LEGAL_CONTROLS_FORMULA = (
    "sev ~ female + age + age_sq + education_level + employed + "
    "C(crime_category, Treatment(reference='violent')) + prior_criminal + "
    "victim_minor + injury_serious + intoxicated_at_crime + restitution_paid + "
    "C(year) + C(court_id)"
)

KEY_VARS = ["female", "education_level", "employed", "prior_criminal"]


# ── HELPERS ───────────────────────────────────────────────────

def fit_clustered_ols(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster",
        cov_kwds={"groups": data["court_id"]},
    )


def coef_row(
    model, var: str, model_name: str, n: int, r_squared: float, notes: str = "",
) -> dict:
    ci = model.conf_int().loc[var]
    return {
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
        "notes": notes,
    }


def extract_logit_results(logit_model, variables: list[str]) -> pd.DataFrame:
    rows = []
    for var in variables:
        if var not in logit_model.params.index:
            continue
        ci = logit_model.conf_int().loc[var]
        rows.append({
            "variable": var,
            "coefficient": logit_model.params[var],
            "se": logit_model.bse[var],
            "z": logit_model.tvalues[var],
            "p": logit_model.pvalues[var],
            "odds_ratio": np.exp(logit_model.params[var]),
            "or_ci_low": np.exp(ci[0]),
            "or_ci_high": np.exp(ci[1]),
        })
    return pd.DataFrame(rows)


# ── MAIN ──────────────────────────────────────────────────────

def main() -> None:
    df = load_analysis_data(DATA / "sentencing_clean.parquet")

    # Build samples
    sa = build_sample(df, "sample_a")
    sa["sev"] = sa["severity_winsorized"]
    sa = ensure_model_dtypes(
        sa,
        ["female", "age", "age_sq", "education_level", "employed", "prior_criminal"],
    )

    sb = build_sample(df, "sample_b")
    sb["sev"] = sb["severity_winsorized"]
    sb = ensure_model_dtypes(
        sb,
        ["female", "education_level", "employed", "prior_criminal"],
    )

    stage1 = ensure_model_dtypes(
        build_sample(df, "two_part_stage1"),
        ["female", "age", "age_sq", "education_level", "employed", "prior_criminal"],
    )
    stage1["imprisoned"] = (stage1["sentence_type"] == "imprisonment").astype(int)

    stage2 = build_two_part_stage2(stage1)
    stage2["months"] = stage2["sentence_months"].astype(float)

    all_rows: list[dict] = []

    # ── 1. SAMPLE B (no age) ─────────────────────────────────

    print("=" * 70)
    print("ROBUSTNESS 1: Sample B (no age requirement)")
    print("=" * 70)

    sb_model = fit_clustered_ols(MODEL1_NO_AGE_FORMULA, sb)
    print(f"N = {len(sb):,}, R² = {sb_model.rsquared:.4f}")
    for var in KEY_VARS:
        coef = sb_model.params[var]
        p = sb_model.pvalues[var]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {var:<20}: {coef:>8.3f}{stars} (p={p:.4f})")
        all_rows.append(coef_row(
            sb_model, var, "Sample B (no age)", len(sb), sb_model.rsquared,
            "Model 1 without age/age_sq",
        ))

    # ── 2. TEMPORAL SPLIT ─────────────────────────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 2: Temporal split")
    print("=" * 70)

    for period, year_filter in [("2020-2022", sa["year"] <= 2022), ("2023-2025", (sa["year"] >= 2023) & (sa["year"] <= 2025))]:
        subset = sa[year_filter].copy()
        if len(subset) < 500:
            print(f"  {period}: skipped (N={len(subset)})")
            continue
        model = fit_clustered_ols(MODEL1_FORMULA, subset)
        print(f"  {period}: N = {len(subset):,}, R² = {model.rsquared:.4f}")
        for var in KEY_VARS:
            coef = model.params[var]
            p = model.pvalues[var]
            stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"    {var:<20}: {coef:>8.3f}{stars} (p={p:.4f})")
            all_rows.append(coef_row(
                model, var, period, len(subset), model.rsquared,
                "Model 1 temporal subset",
            ))

    # ── 3. LOG-SEVERITY ───────────────────────────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 3: Log-severity")
    print("=" * 70)

    sa_log = sa[sa["sev"] > 0].copy()
    sa_log["log_sev"] = np.log(sa_log["sev"])
    log_model = fit_clustered_ols(LOG_MODEL1_FORMULA, sa_log)
    print(f"N = {len(sa_log):,}, R² = {log_model.rsquared:.4f}")
    for var in KEY_VARS:
        coef = log_model.params[var]
        p = log_model.pvalues[var]
        pct = (np.exp(coef) - 1) * 100
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {var:<20}: {coef:>8.4f}{stars} ({pct:+.1f}%) (p={p:.4f})")
        all_rows.append(coef_row(
            log_model, var, "Log-severity", len(sa_log), log_model.rsquared,
            "DV = log(severity); coefficients are log units",
        ))

    # ── 4. TWO-PART IMPRISONMENT ──────────────────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 4: Two-part imprisonment model")
    print("=" * 70)

    logit = smf.logit(LOGIT_STAGE1_FORMULA, data=stage1).fit(disp=0)
    print(f"Stage 1 (logit): N = {len(stage1):,}, imprisoned = {stage1['imprisoned'].mean()*100:.1f}%")
    for var in KEY_VARS:
        coef = logit.params[var]
        or_val = np.exp(coef)
        p = logit.pvalues[var]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {var:<20}: OR={or_val:.2f}{stars} (p={p:.4f})")

    ols2 = fit_clustered_ols(OLS_STAGE2_FORMULA, stage2)
    print(f"Stage 2 (OLS): N = {len(stage2):,}, R² = {ols2.rsquared:.4f}")
    for var in KEY_VARS:
        coef = ols2.params[var]
        p = ols2.pvalues[var]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {var:<20}: {coef:>8.3f}{stars} (p={p:.4f})")
        all_rows.append(coef_row(
            ols2, var, "Two-part stage 2", len(stage2), ols2.rsquared,
            "OLS on imprisoned cases with sentence_months",
        ))

    # ── 5. LEGAL CONTROLS (APPENDIX) ─────────────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 5: Legal-controls subsample")
    print("=" * 70)

    legal_cols = list(LEGAL_CONTROL_COLS)
    sa_legal = sa.dropna(subset=legal_cols).copy()
    for col in legal_cols:
        sa_legal[col] = sa_legal[col].astype(float)

    if len(sa_legal) >= 500:
        legal_model = fit_clustered_ols(LEGAL_CONTROLS_FORMULA, sa_legal)
        print(f"N = {len(sa_legal):,}, R² = {legal_model.rsquared:.4f}")
        print(f"NOTE: subsample is not representative (fewer females, more fines)")
        for var in KEY_VARS:
            coef = legal_model.params[var]
            p = legal_model.pvalues[var]
            stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {var:<20}: {coef:>8.3f}{stars} (p={p:.4f})")
            all_rows.append(coef_row(
                legal_model, var, "Legal controls subsample", len(sa_legal),
                legal_model.rsquared,
                "Replaces agg/mit with victim_minor, injury_serious, intoxicated, restitution; non-representative subsample",
            ))
    else:
        print(f"Skipped — only {len(sa_legal)} cases")

    # ── 6. SEVERITY / ESTIMATOR SENSITIVITY ──────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 6: Severity conversion and estimator sensitivity")
    print("=" * 70)

    scenario_columns = [
        (
            "Severity: Article 5.4 community conversion",
            "severity_legal_community",
            "Community service = hours/240; other default weights unchanged",
        ),
        (
            "Severity: higher noncustodial weights",
            "severity_conservative",
            "Fine divisor 300,000; suspended weight 0.7; community service hours/160",
        ),
        (
            "Severity: lower noncustodial weights",
            "severity_liberal",
            "Fine divisor 600,000; suspended weight 0.3; community service hours/160",
        ),
    ]

    for model_name, column, notes in scenario_columns:
        subset = sa.dropna(subset=[column]).copy()
        subset["sev"] = subset[column].clip(upper=subset[column].quantile(0.99))
        model = fit_clustered_ols(MODEL1_FORMULA, subset)
        print(
            f"  {model_name}: N={len(subset):,}, "
            f"employment={model.params['employed']:.3f}, "
            f"p={model.pvalues['employed']:.4g}"
        )
        for var in KEY_VARS:
            all_rows.append(coef_row(
                model, var, model_name, len(subset), model.rsquared, notes,
            ))

    hc3_model = smf.ols(MODEL1_FORMULA, data=sa).fit(cov_type="HC3")
    print(
        f"  Preregistered HC3 estimator: N={len(sa):,}, "
        f"employment={hc3_model.params['employed']:.3f}, "
        f"p={hc3_model.pvalues['employed']:.4g}"
    )
    for var in KEY_VARS:
        all_rows.append(coef_row(
            hc3_model, var, "Preregistered HC3 estimator", len(sa),
            hc3_model.rsquared, "Model 1 with HC3 rather than court-clustered SE",
        ))

    within_type = [
        ("Fine-only log amount", "fine", "sentence_fine_mnt"),
        ("Imprisonment-only log months", "imprisonment", "sentence_months"),
    ]
    for model_name, sentence_type, outcome in within_type:
        subset = sa[
            sa["sentence_type"].eq(sentence_type)
            & sa[outcome].notna()
            & sa[outcome].gt(0)
        ].copy()
        subset["sev"] = np.log(subset[outcome].astype(float))
        model = fit_clustered_ols(MODEL1_FORMULA, subset)
        print(
            f"  {model_name}: N={len(subset):,}, "
            f"employment={model.params['employed']:.3f} "
            f"({(np.exp(model.params['employed']) - 1) * 100:+.1f}%), "
            f"p={model.pvalues['employed']:.4g}"
        )
        for var in KEY_VARS:
            all_rows.append(coef_row(
                model, var, model_name, len(subset), model.rsquared,
                f"DV = log({outcome}); within {sentence_type} only",
            ))

    # ── 7. STATUTORY PERSONAL-FINE RANGE ───────────────────────

    print(f"\n{'=' * 70}")
    print("ROBUSTNESS 7: Statutory personal-fine range")
    print("=" * 70)

    # Criminal Code Article 5.3.2-.3 sets the fine range for a person at up
    # to 40,000 units, with one unit equal to 1,000 MNT. Larger extracted
    # values are likely damages, restitution, or legal-entity amounts.
    personal_fine_max = 40_000_000
    implausible_fine = sa["sentence_type"].eq("fine") & sa[
        "sentence_fine_mnt"
    ].gt(personal_fine_max)
    plausible = sa[~implausible_fine].copy()
    plausible_model = fit_clustered_ols(MODEL1_FORMULA, plausible)
    print(
        f"  Exclude fines >40m MNT: removed={int(implausible_fine.sum())}, "
        f"N={len(plausible):,}, employment={plausible_model.params['employed']:.3f}, "
        f"p={plausible_model.pvalues['employed']:.4g}"
    )
    for var in KEY_VARS:
        all_rows.append(coef_row(
            plausible_model,
            var,
            "Exclude fines above personal statutory maximum",
            len(plausible),
            plausible_model.rsquared,
            "Excludes fine cases above 40,000,000 MNT under Article 5.3.2-.3",
        ))

    fine_plausible = sa[
        sa["sentence_type"].eq("fine")
        & sa["sentence_fine_mnt"].gt(0)
        & sa["sentence_fine_mnt"].le(personal_fine_max)
    ].copy()
    fine_plausible["sev"] = np.log(fine_plausible["sentence_fine_mnt"].astype(float))
    fine_plausible_model = fit_clustered_ols(MODEL1_FORMULA, fine_plausible)
    print(
        f"  Fine-only log amount within statutory range: N={len(fine_plausible):,}, "
        f"employment={fine_plausible_model.params['employed']:.3f} "
        f"({(np.exp(fine_plausible_model.params['employed']) - 1) * 100:+.1f}%), "
        f"p={fine_plausible_model.pvalues['employed']:.4g}"
    )
    for var in KEY_VARS:
        all_rows.append(coef_row(
            fine_plausible_model,
            var,
            "Fine-only log amount (statutory range)",
            len(fine_plausible),
            fine_plausible_model.rsquared,
            "DV = log(sentence_fine_mnt); excludes amounts above 40,000,000 MNT",
        ))

    # ── EXPORT ────────────────────────────────────────────────

    pd.DataFrame(all_rows).to_csv(TABLES / "table5_robustness.csv", index=False)

    logit_results = extract_logit_results(logit, KEY_VARS)
    logit_results.to_csv(TABLES / "table5b_two_part_stage1.csv", index=False)

    print(f"\nSaved {TABLES / 'table5_robustness.csv'}")
    print(f"Saved {TABLES / 'table5b_two_part_stage1.csv'}")


if __name__ == "__main__":
    main()
