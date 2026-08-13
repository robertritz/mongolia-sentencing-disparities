"""
Shared analysis dataset helpers.

Centralizes sample definitions, recurring derived variables, and common
robustness helpers so all analysis scripts use the same logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from severity_scale import (
    CONSERVATIVE_WEIGHTS,
    DEFAULT_WEIGHTS,
    LEGAL_COMMUNITY_WEIGHTS,
    LIBERAL_WEIGHTS,
    calculate_severity,
)


PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_PARQUET = PROJECT / "data" / "processed" / "sentencing_clean.parquet"


SAMPLE_A_REQUIRED = (
    "female",
    "age",
    "education_level",
    "employed",
    "crime_category",
    "prior_criminal",
    "severity",
)

SAMPLE_B_REQUIRED = (
    "female",
    "education_level",
    "employed",
    "crime_category",
    "prior_criminal",
    "severity",
)

TWO_PART_STAGE1_REQUIRED = (
    "female",
    "age",
    "education_level",
    "employed",
    "crime_category",
    "prior_criminal",
)


@dataclass(frozen=True)
class SampleSpec:
    """Canonical sample definition."""

    key: str
    description: str
    required_columns: tuple[str, ...]

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(subset=list(self.required_columns)).copy()


CANONICAL_SAMPLES = {
    "full": SampleSpec(
        key="full",
        description="Full cleaned sample",
        required_columns=tuple(),
    ),
    "sample_a": SampleSpec(
        key="sample_a",
        description="Primary confirmatory adult sample",
        required_columns=SAMPLE_A_REQUIRED,
    ),
    "sample_b": SampleSpec(
        key="sample_b",
        description="Robustness sample without age requirement; known juveniles excluded",
        required_columns=SAMPLE_B_REQUIRED,
    ),
    "two_part_stage1": SampleSpec(
        key="two_part_stage1",
        description="Two-part imprisonment model stage 1 adult sample",
        required_columns=TWO_PART_STAGE1_REQUIRED,
    ),
}


def _list_length(value: object) -> float:
    """Return length for list-like values, NA otherwise."""
    if isinstance(value, np.ndarray):
        return float(len(value))
    if isinstance(value, (list, tuple)):
        return float(len(value))
    return np.nan


def _compute_alt_severity(df: pd.DataFrame, weights) -> pd.Series:
    """Recompute severity under alternate conversion weights."""

    def _row_severity(row: pd.Series) -> float | None:
        return calculate_severity(
            sentence_type=row["sentence_type"],
            sentence_months=row.get("sentence_months"),
            sentence_fine_mnt=row.get("sentence_fine_mnt"),
            community_service_hours=row.get("sentence_community_hours"),
            weights=weights,
        )

    return df.apply(_row_severity, axis=1)


def add_analysis_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add shared derived variables used across analysis scripts."""
    df = df.copy()

    df["extraction_quality_clean"] = df["extraction_quality"].fillna("missing")
    df["llm_quality_complete"] = df["extraction_quality_clean"].eq("complete")
    df["llm_quality_partial"] = df["extraction_quality_clean"].eq("partial")
    df["llm_quality_unreliable"] = df["extraction_quality_clean"].eq("unreliable")

    for prefix in ("aggravating", "mitigating"):
        factor_col = f"{prefix}_factors"
        if factor_col not in df.columns:
            # The public replication dataset deliberately omits these failed
            # measures and their free text. Retained analyses do not use them.
            continue
        count_col = f"{prefix}_count"
        raw_col = f"{prefix}_count_raw"
        observed_col = f"{prefix}_observed"
        present_col = f"{prefix}_present"
        complete_count_col = f"{prefix}_count_complete"
        complete_present_col = f"{prefix}_present_complete"

        # Compute NA-aware counts from factor lists
        inferred_counts = df[factor_col].apply(_list_length)

        if count_col in df.columns:
            # Parquet may have 0-for-missing (old) or NA-for-missing (new).
            # Build the raw version: keep parquet value where non-null, else
            # infer from factor lists.
            raw = df[count_col].copy()
            # Treat 0 as potentially conflated with missing when factors are
            # not a list (i.e. extraction failed).  Only old parquets have this
            # issue; new ones already use NA.
            non_list_mask = ~df[factor_col].apply(lambda x: isinstance(x, (list, tuple, np.ndarray)))
            raw = raw.where(~((raw == 0) & non_list_mask))
            raw = raw.fillna(inferred_counts)
        else:
            raw = inferred_counts

        df[raw_col] = raw
        # Retain a filled compatibility column for validation diagnostics only.
        # These failed measures are not used in any retained analysis model.
        df[count_col] = raw.fillna(0)

        df[present_col] = (df[count_col] > 0).astype("Int64")

        # "complete" extraction quality is the best available proxy for
        # having fully observed factor extraction.
        df[observed_col] = df["llm_quality_complete"].astype("Int64")
        df[complete_count_col] = raw.where(df["llm_quality_complete"])
        df[complete_present_col] = df[present_col].where(df["llm_quality_complete"])
        df[f"{complete_count_col}_filled"] = df[complete_count_col].fillna(0)

    df["post_2022"] = (df["year"] >= 2023).astype("Int64")
    df["analysis_period"] = np.where(df["year"] <= 2022, "2020-2022", "2023-2025")
    df.loc[df["year"] >= 2026, "analysis_period"] = "2026"

    if "severity_default" not in df.columns:
        df["severity_default"] = df["severity"]

    if "severity_conservative" not in df.columns:
        df["severity_conservative"] = _compute_alt_severity(df, CONSERVATIVE_WEIGHTS)

    if "severity_liberal" not in df.columns:
        df["severity_liberal"] = _compute_alt_severity(df, LIBERAL_WEIGHTS)

    if "severity_legal_community" not in df.columns:
        df["severity_legal_community"] = _compute_alt_severity(
            df, LEGAL_COMMUNITY_WEIGHTS
        )

    if "severity_default_recomputed" not in df.columns:
        df["severity_default_recomputed"] = _compute_alt_severity(df, DEFAULT_WEIGHTS)

    return df


def load_analysis_data(path: Path | str = DEFAULT_PARQUET) -> pd.DataFrame:
    """Load the cleaned parquet and attach shared derived variables."""
    return add_legal_controls(add_analysis_features(pd.read_parquet(path)))


def build_sample(df: pd.DataFrame, sample_key: str) -> pd.DataFrame:
    """Return a canonical sample by key."""
    spec = CANONICAL_SAMPLES[sample_key]
    if not spec.required_columns:
        return df.copy()
    sample = spec.build(df)

    # The preregistration excludes juvenile defendants because Mongolia uses a
    # distinct juvenile sentencing framework. Sample B deliberately drops the
    # age requirement, so it can exclude only cases known to be juveniles.
    if sample_key in {"sample_a", "two_part_stage1"}:
        sample = sample[sample["age"] >= 18].copy()
    elif sample_key == "sample_b":
        sample = sample[sample["age"].isna() | (sample["age"] >= 18)].copy()

    return sample


def build_two_part_stage2(stage1_df: pd.DataFrame) -> pd.DataFrame:
    """Stage 2 sample for the two-part imprisonment model."""
    return stage1_df[
        (stage1_df["sentence_type"] == "imprisonment") & stage1_df["sentence_months"].notna()
    ].copy()


def add_article_group(
    df: pd.DataFrame,
    *,
    based_on: pd.DataFrame | None = None,
    min_cases: int = 50,
) -> pd.DataFrame:
    """Add article-group fixed-effect helper."""
    df = df.copy()
    reference = based_on if based_on is not None else df
    counts = reference["primary_article"].dropna().value_counts()

    def _map_article(row: pd.Series) -> str:
        article = row.get("primary_article")
        chapter = row.get("crime_chapter")
        if pd.notna(article) and counts.get(article, 0) >= min_cases:
            return str(article)
        if pd.notna(chapter):
            return f"chapter_rare_{int(chapter)}"
        return "chapter_rare_missing"

    df["article_group"] = df.apply(_map_article, axis=1)
    return df


LEGAL_CONTROL_COLS = (
    "victim_minor",
    "injury_serious",
    "intoxicated_at_crime",
    "restitution_paid",
)


def add_legal_controls(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare legally-grounded case-level controls.

    These replace the problematic aggravating/mitigating count variables
    with individual, interpretable controls that don't overlap with
    the demographic predictors under study.
    """
    df = df.copy()

    # Binary: victim_minor, intoxicated_at_crime, restitution_paid
    for col in ("victim_minor", "intoxicated_at_crime", "restitution_paid"):
        if col in df.columns:
            df[col] = df[col].astype("boolean")

    # Collapse injury_severity to binary serious-injury flag
    if "injury_severity" in df.columns:
        df["injury_serious"] = (
            df["injury_severity"]
            .astype(str)
            .str.contains("serious", case=False, na=False)
            .astype("Int64")
        )
        df.loc[df["injury_severity"].isna(), "injury_serious"] = pd.NA
    else:
        df["injury_serious"] = pd.NA

    return df


def filter_single_defendant(df: pd.DataFrame) -> pd.DataFrame:
    """Exclude multi-defendant cases when the flag is available.

    Returns the input unchanged if `quality_issues` or an explicit
    `multiple_defendants` column is not present.
    """
    if "multiple_defendants" in df.columns:
        return df[~df["multiple_defendants"].fillna(False)].copy()
    if "quality_issues" in df.columns:
        has_multi = df["quality_issues"].apply(
            lambda x: "multiple_defendants" in x
            if isinstance(x, (list, tuple, np.ndarray))
            else False
        )
        return df[~has_multi].copy()
    return df


def ensure_model_dtypes(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Cast common model columns to numeric dtypes as needed."""
    df = df.copy()
    int_like = {"female", "employed", "prior_criminal", "post_2022"}
    for column in columns:
        if column not in df.columns:
            continue
        if column in int_like:
            df[column] = df[column].astype(int)
        elif pd.api.types.is_integer_dtype(df[column]) or pd.api.types.is_bool_dtype(df[column]):
            df[column] = df[column].astype(float)
    return df


def sample_registry_rows(df: pd.DataFrame) -> list[dict[str, object]]:
    """Build a tabular registry of canonical samples and counts."""
    rows: list[dict[str, object]] = []
    for key, spec in CANONICAL_SAMPLES.items():
        sample = build_sample(df, key)
        rows.append(
            {
                "sample_key": key,
                "description": spec.description,
                "n": len(sample),
                "required_columns": ", ".join(spec.required_columns),
            }
        )

    stage1 = build_sample(df, "two_part_stage1")
    stage2 = build_two_part_stage2(stage1)
    rows.append(
        {
            "sample_key": "two_part_stage2",
            "description": "Two-part imprisonment model stage 2 sample",
            "n": len(stage2),
            "required_columns": ", ".join(TWO_PART_STAGE1_REQUIRED + ("sentence_months",)),
        }
    )
    return rows
