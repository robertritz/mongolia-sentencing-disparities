#!/usr/bin/env python3
"""
Step 3: Analysis figures.

Reads from CSV outputs of 01_model_hierarchy.py and 02_robustness_checks.py.
Does NOT re-fit models.

Outputs:
- figures/fig5_model_hierarchy.png
- figures/fig6_employment_robustness.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

PROJECT = Path(__file__).parent.parent.parent.parent
TABLES = PROJECT / "tables"
FIGURES = PROJECT / "figures"
FIGURES.mkdir(exist_ok=True)
plt.rcParams["ps.fonttype"] = 42
JOURNAL_WIDTH_IN = 6.45  # leaves room for tight-bbox labels under the 174 mm maximum


def save_figure(fig, preview_stem: str, submission_stem: str) -> None:
    """Save a manuscript preview and journal-preferred editable vector art."""
    png = FIGURES / f"{preview_stem}.png"
    eps = FIGURES / f"{submission_stem}.eps"
    fig.savefig(png, bbox_inches="tight", dpi=300)
    fig.savefig(eps, bbox_inches="tight", format="eps")
    plt.close(fig)
    print(f"Saved {png}")
    print(f"Saved {eps}")


# ── FIGURE 5: MODEL HIERARCHY ────────────────────────────────

def plot_model_hierarchy() -> None:
    df = pd.read_csv(TABLES / "table4_model_hierarchy.csv")

    display_vars = ["female", "education_level", "employed", "prior_criminal"]
    var_labels = {
        "female": "Female (H1)",
        "education_level": "Education level (H2)",
        "employed": "Employed (H4)",
        "prior_criminal": "Prior criminal",
    }
    model_order = [
        "Model 1 - Total Association",
        "Model 2 - Same-Crime",
    ]
    colors = ["#4C72B0", "#55A868"]

    fig, ax = plt.subplots(figsize=(JOURNAL_WIDTH_IN, 3.87))
    y_positions = np.arange(len(display_vars))
    n_models = len(model_order)
    height = 0.8 / n_models

    for i, model_name in enumerate(model_order):
        mdf = df[df["model"] == model_name]
        offsets = y_positions + (i - n_models / 2 + 0.5) * height
        label = "Model 1: total association" if i == 0 else "Model 2: same crime"

        for j, var in enumerate(display_vars):
            row = mdf[mdf["variable"] == var]
            if row.empty:
                continue
            row = row.iloc[0]
            ax.errorbar(
                row["coefficient"],
                offsets[j],
                xerr=[[row["coefficient"] - row["ci_low"]],
                      [row["ci_high"] - row["coefficient"]]],
                fmt="o",
                color=colors[i],
                capsize=4,
                markersize=7,
                label=label if j == 0 else "",
            )

    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([var_labels[v] for v in display_vars])
    ax.set_xlabel("Coefficient (severity month-equivalents)")
    ax.legend(loc="upper right", fontsize=8)
    ax.invert_yaxis()
    plt.tight_layout()

    save_figure(fig, "fig5_model_hierarchy", "Fig5")


# ── FIGURE 6: EMPLOYMENT ROBUSTNESS ──────────────────────────

def plot_employment_robustness() -> None:
    t4 = pd.read_csv(TABLES / "table4_model_hierarchy.csv")
    t5 = pd.read_csv(TABLES / "table5_robustness.csv")

    # Include only outcomes measured in month-equivalents. Log-outcome and
    # within-sentence proportional models remain in Table 5 because their
    # coefficients are not commensurable on this axis.
    specs: list[tuple[str, float, float, float]] = []

    # Hierarchy models
    for model_name in [
        "Model 1 - Total Association",
        "Model 2 - Same-Crime",
    ]:
        row = t4[(t4["model"] == model_name) & (t4["variable"] == "employed")]
        if not row.empty:
            r = row.iloc[0]
            specs.append((model_name, r["coefficient"], r["ci_low"], r["ci_high"]))

    # Robustness models
    robustness_order = [
        "Sample B (no age)",
        "2020-2022",
        "2023-2025",
        "Two-part stage 2",
        "Legal controls subsample",
        "Severity: Article 5.4 community conversion",
        "Severity: higher noncustodial weights",
        "Severity: lower noncustodial weights",
        "Preregistered HC3 estimator",
        "Exclude fines above personal statutory maximum",
    ]
    for model_name in robustness_order:
        row = t5[(t5["model"] == model_name) & (t5["variable"] == "employed")]
        if not row.empty:
            r = row.iloc[0]
            specs.append((model_name, r["coefficient"], r["ci_low"], r["ci_high"]))

    raw_labels = [s[0] for s in specs]
    display_labels = {
        "Severity: Article 5.4 community conversion": "Article 5.4 community conversion",
        "Severity: higher noncustodial weights": "Higher noncustodial weights",
        "Severity: lower noncustodial weights": "Lower noncustodial weights",
        "Preregistered HC3 estimator": "Preregistered HC3 SE",
        "Exclude fines above personal statutory maximum": "Exclude fines above 40m MNT",
    }
    labels = [display_labels.get(label, label) for label in raw_labels]
    coefs = [s[1] for s in specs]
    ci_lows = [s[2] for s in specs]
    ci_highs = [s[3] for s in specs]
    fig, ax = plt.subplots(figsize=(JOURNAL_WIDTH_IN, 5.48))
    y_pos = np.arange(len(specs))

    # Color: blue for hierarchy, gray for robustness
    n_hierarchy = 2
    for i in range(len(specs)):
        color = "#4C72B0" if i < n_hierarchy else "#666666"
        ax.errorbar(
            coefs[i], y_pos[i],
            xerr=[[coefs[i] - ci_lows[i]], [ci_highs[i] - coefs[i]]],
            fmt="o", color=color, capsize=4, markersize=7,
        )
        # Right-side annotation
        stars = ""
        # Read p-value for annotation
        if i < n_hierarchy:
            row = t4[(t4["model"] == raw_labels[i]) & (t4["variable"] == "employed")]
        else:
            row = t5[(t5["model"] == raw_labels[i]) & (t5["variable"] == "employed")]
        if not row.empty:
            p = row.iloc[0]["p"]
            stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""

        ax.annotate(
            f"{coefs[i]:.2f}{stars}",
            xy=(ci_highs[i] + 0.3, y_pos[i]),
            va="center", fontsize=8, color="#333333",
        )

    # Separator between hierarchy and robustness
    ax.axhline(n_hierarchy - 0.5, color="#cccccc", linewidth=0.8)
    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Coefficient (severity month-equivalents)")
    ax.invert_yaxis()
    plt.tight_layout()

    save_figure(fig, "fig6_employment_robustness", "Fig6")


# ── MAIN ──────────────────────────────────────────────────────

def main() -> None:
    plot_model_hierarchy()
    plot_employment_robustness()


if __name__ == "__main__":
    main()
