#!/usr/bin/env python3
"""Minimal reproducibility smoke test."""

from pathlib import Path
import sys

import statsmodels.formula.api as smf

PROJECT = Path(__file__).parent.parent.parent
DATA = PROJECT / "data" / "processed" / "sentencing_clean.parquet"
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import build_sample, load_analysis_data  # noqa: E402


def main() -> None:
    df = load_analysis_data(DATA)
    sample_a = build_sample(df, "sample_a")
    sample_a["sev"] = sample_a["severity_winsorized"]
    model = smf.ols(
        "sev ~ female + age + age_sq + education_level + employed + "
        "C(crime_category, Treatment(reference='violent')) + prior_criminal",
        data=sample_a,
    ).fit()
    print(f"Loaded parquet: {len(df):,} rows")
    print(f"Sample A: {len(sample_a):,} rows")
    print(f"Smoke model R^2: {model.rsquared:.4f}")


if __name__ == "__main__":
    main()
