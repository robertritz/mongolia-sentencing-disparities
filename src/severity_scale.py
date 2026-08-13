"""
Sentence severity scale conversion.

Converts all sentence types to a unified "imprisonment-month equivalent" scale.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SeverityWeights:
    """Weights for converting sentence types to month-equivalents."""
    imprisonment: float = 1.0
    suspended: float = 0.5
    probation: float = 0.3
    community_service_hours_per_month: float = 160.0
    # Fine conversion: MNT per month-equivalent of imprisonment
    # Legal rate: 15,000 MNT = 1 day (Criminal Code 5.3.5)
    # 15,000 * 30 = 450,000 MNT = 1 month
    fine_mnt_per_month: float = 450_000.0


# Default weights (will test sensitivity)
DEFAULT_WEIGHTS = SeverityWeights()

# Article 5.4.4 converts eight unserved community-service hours to one day of
# imprisonment. On the same 30-day convention used for fines, this implies
# 240 hours per imprisonment-month. The preregistered primary scale remains
# 160 hours; this legally anchored alternative is reported as sensitivity.
LEGAL_COMMUNITY_WEIGHTS = SeverityWeights(community_service_hours_per_month=240.0)

# Alternative weight sets for sensitivity analysis
CONSERVATIVE_WEIGHTS = SeverityWeights(suspended=0.7, probation=0.5, fine_mnt_per_month=300_000.0)
LIBERAL_WEIGHTS = SeverityWeights(suspended=0.3, probation=0.1, fine_mnt_per_month=600_000.0)


def calculate_severity(
    sentence_type: str,
    sentence_months: Optional[float] = None,
    sentence_fine_mnt: Optional[float] = None,
    community_service_hours: Optional[float] = None,
    weights: SeverityWeights = DEFAULT_WEIGHTS,
) -> Optional[float]:
    """
    Calculate unified severity score in imprisonment-month equivalents.

    Args:
        sentence_type: Type of sentence (imprisonment, suspended, probation, fine, community_service)
        sentence_months: Duration in months (for imprisonment/suspended/probation)
        sentence_fine_mnt: Fine amount in MNT
        community_service_hours: Community service hours
        weights: Weight configuration for conversion

    Returns:
        Severity score in month-equivalents, or None if cannot calculate
    """
    if sentence_type == "imprisonment":
        if sentence_months is not None:
            return sentence_months * weights.imprisonment
        return None

    elif sentence_type == "suspended":
        if sentence_months is not None:
            return sentence_months * weights.suspended
        return None

    elif sentence_type == "probation":
        if sentence_months is not None:
            return sentence_months * weights.probation
        return None

    elif sentence_type == "community_service":
        if community_service_hours is not None:
            return community_service_hours / weights.community_service_hours_per_month
        return None

    elif sentence_type == "fine":
        if sentence_fine_mnt is not None:
            # Criminal Code 5.3.5: 15,000 MNT = 1 day imprisonment
            # 450,000 MNT = 1 month
            return sentence_fine_mnt / weights.fine_mnt_per_month
        return None

    elif sentence_type == "acquittal":
        return 0.0

    else:
        return None


def add_severity_column(df, weights: SeverityWeights = DEFAULT_WEIGHTS):
    """
    Add severity column to DataFrame.

    Args:
        df: DataFrame with sentence_type, sentence_months, sentence_fine_mnt columns
        weights: Weight configuration

    Returns:
        DataFrame with new 'severity' column
    """
    import pandas as pd

    df = df.copy()
    df["severity"] = df.apply(
        lambda row: calculate_severity(
            sentence_type=row.get("sentence_type"),
            sentence_months=row.get("sentence_months"),
            sentence_fine_mnt=row.get("sentence_fine_mnt"),
            community_service_hours=row.get("community_service_hours"),
            weights=weights,
        ),
        axis=1,
    )
    return df


def sensitivity_analysis(df) -> dict:
    """
    Run severity calculation with multiple weight configurations.

    Returns dict mapping weight_name -> DataFrame with that severity column.
    """
    results = {
        "default": add_severity_column(df, DEFAULT_WEIGHTS),
        "conservative": add_severity_column(df, CONSERVATIVE_WEIGHTS),
        "liberal": add_severity_column(df, LIBERAL_WEIGHTS),
    }
    return results


# Fine conversion notes:
#
# Criminal Code 5.3.5: Non-payment conversion rate is 15,000 MNT = 1 day
# Confirmed empirically across 25 cases with explicit conversion formulas
# Default: 450,000 MNT/month (15,000 * 30)
# Sensitivity: 300,000 (conservative) and 600,000 (liberal) tested in robustness
