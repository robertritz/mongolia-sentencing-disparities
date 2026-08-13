#!/usr/bin/env python3
"""Canonical sample registry and count audit."""

from pathlib import Path
import sys

import pandas as pd

PROJECT = Path(__file__).parent.parent.parent.parent
TABLES = PROJECT / "tables"
TABLES.mkdir(exist_ok=True)
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import load_analysis_data, sample_registry_rows  # noqa: E402


def main() -> None:
    df = load_analysis_data()
    registry = pd.DataFrame(sample_registry_rows(df))

    print("=" * 90)
    print("CANONICAL SAMPLE REGISTRY")
    print("=" * 90)
    print(registry.to_string(index=False))

    output = TABLES / "sample_registry.csv"
    registry.to_csv(output, index=False)
    print(f"\nSaved {output}")


if __name__ == "__main__":
    main()
