#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
if [[ -n "${PYTHON_BIN:-}" ]]; then
  PY=("$PYTHON_BIN")
else
  PY=(uv run --with-requirements "$ROOT/requirements-lock.txt" --with pypandoc_binary --with python-docx --with reportlab python)
fi

for script in \
  scripts/analysis/descriptive/00_sample_registry.py \
  scripts/analysis/descriptive/01_sample_overview.py \
  scripts/analysis/descriptive/02_table1_characteristics.py \
  scripts/analysis/descriptive/03_table2_missing.py \
  scripts/analysis/descriptive/04_table3_bivariate.py \
  scripts/analysis/descriptive/05_figures.py \
  scripts/analysis/models/01_model_hierarchy.py \
  scripts/analysis/models/02_robustness_checks.py \
  scripts/analysis/models/03_figures.py \
  scripts/analysis/smoke_test.py \
  scripts/analysis/build_submission.py \
  scripts/analysis/validate_submission.py
do
  "${PY[@]}" "$ROOT/$script"
done
