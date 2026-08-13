#!/usr/bin/env python3
"""
Step 5: Descriptive Figures.

Figure 1: Demographic distributions (2x2)
Figure 2: Sentence distributions (2x2)
Figure 3: Bivariate severity relationships (2x2)
Figure 4: Crime composition by demographics (1x2)

Uses Sample A for bivariate plots, full sample for distributions.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = Path(__file__).parent.parent.parent.parent
DATA = PROJECT / "data" / "processed"
FIGURES = PROJECT / "figures"
FIGURES.mkdir(exist_ok=True)
sys.path.insert(0, str(PROJECT / "src"))

from analysis_dataset import build_sample, load_analysis_data  # noqa: E402

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.facecolor": "white",
    "figure.dpi": 150,
    "ps.fonttype": 42,
})

JOURNAL_WIDTH_IN = 6.40  # leaves room for tight-bbox labels under the 174 mm maximum

df = load_analysis_data(DATA / "sentencing_clean.parquet")

# Canonical adult Sample A
sa = build_sample(df, "sample_a")
sa["sev"] = sa["severity_winsorized"]


def save_figure(fig, preview_stem: str, submission_stem: str) -> None:
    """Save a manuscript preview and journal-preferred editable vector art."""
    png = FIGURES / f"{preview_stem}.png"
    eps = FIGURES / f"{submission_stem}.eps"
    fig.savefig(png, bbox_inches="tight", dpi=300)
    fig.savefig(eps, bbox_inches="tight", format="eps")
    print(f"Saved {png}")
    print(f"Saved {eps}")


def cohens_d(first: pd.Series, second: pd.Series) -> float:
    n1, n2 = len(first), len(second)
    pooled = np.sqrt(
        ((n1 - 1) * first.var(ddof=1) + (n2 - 1) * second.var(ddof=1))
        / (n1 + n2 - 2)
    )
    return (first.mean() - second.mean()) / pooled

# ============================================================
# FIGURE 1: Demographic Distributions
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(JOURNAL_WIDTH_IN, 5.12))

# 1a: Age histogram
ax = axes[0, 0]
age = df["age"].dropna()
ax.hist(age, bins=range(14, 90, 2), color="#4C72B0", edgecolor="white", alpha=0.8)
ax.axvline(age.mean(), color="red", linestyle="--", linewidth=1, label=f"Mean = {age.mean():.1f}")
ax.axvline(age.median(), color="orange", linestyle="--", linewidth=1, label=f"Median = {age.median():.0f}")
ax.set_xlabel("Age")
ax.set_ylabel("Count")
ax.set_title("(a) Age")
ax.legend(fontsize=7)

# 1b: Gender bar
ax = axes[0, 1]
gen = df["gender"].value_counts()
bars = ax.bar(["Male", "Female"], [gen.get("male", 0), gen.get("female", 0)],
              color=["#4C72B0", "#DD8452"])
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 500, f"{h:,}",
            ha="center", va="bottom", fontsize=10)
ax.set_ylabel("Count")
ax.set_title("(b) Gender")
ax.margins(y=0.16)

# 1c: Education bar
ax = axes[1, 0]
edu_order = ["none", "primary", "basic", "secondary", "vocational", "higher"]
edu_labels = ["None", "Primary", "Basic", "Secondary", "Vocat.", "Higher"]
edu_counts = [df[df["education_clean"] == e].shape[0] for e in edu_order]
bars = ax.bar(edu_labels, edu_counts, color="#55A868")
ax.set_ylabel("Count")
ax.set_title("(c) Education")
ax.tick_params(axis="x", rotation=35, labelsize=7)
ax.margins(y=0.16)
for bar in bars:
    h = bar.get_height()
    if h > 500:
        ax.text(bar.get_x() + bar.get_width()/2, h + 300, f"{h:,}",
                ha="center", va="bottom", fontsize=8)

# 1d: Crime category bar
ax = axes[1, 1]
cat_order = ["violent", "property", "traffic", "drug", "other"]
cat_labels = ["Violent", "Property", "Traffic", "Drug", "Other"]
cat_counts = [df[df["crime_category"] == c].shape[0] for c in cat_order]
bars = ax.bar(cat_labels, cat_counts, color="#C44E52")
ax.set_ylabel("Count")
ax.set_title("(d) Crime category")
ax.tick_params(axis="x", rotation=20, labelsize=7)
ax.margins(y=0.16)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 300, f"{h:,}",
            ha="center", va="bottom", fontsize=8)

plt.tight_layout()
save_figure(fig, "fig1_demographics", "Fig1")
plt.close()

# ============================================================
# FIGURE 2: Sentence Distributions
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(JOURNAL_WIDTH_IN, 5.12))

# 2a: Sentence type bar
ax = axes[0, 0]
st_order = ["fine", "imprisonment", "community_service", "suspended"]
st_labels = ["Fine", "Imprison.", "Community\nservice", "Suspended"]
st_counts = [df[df["sentence_type"] == s].shape[0] for s in st_order]
colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
bars = ax.bar(st_labels, st_counts, color=colors)
ax.set_ylabel("Count")
ax.set_title("(a) Sentence type")
ax.tick_params(axis="x", labelsize=7)
ax.margins(y=0.16)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 300, f"{h:,}",
            ha="center", va="bottom", fontsize=8)

# 2b: Severity histogram (winsorized, log scale)
ax = axes[0, 1]
sev = df["severity_winsorized"].dropna()
ax.hist(sev[sev > 0], bins=50, color="#4C72B0", edgecolor="white", alpha=0.8)
ax.set_xlabel("Severity (month-equivalents, winsorized)")
ax.set_ylabel("Count")
ax.set_title("(b) Severity distribution")
ax.set_yscale("log")

# 2c: Severity by sentence type (boxplot)
ax = axes[1, 0]
box_data = []
box_labels = []
for s, label in zip(st_order, ["Fine", "Imprison.", "Com.Svc", "Susp."]):
    vals = df[df["sentence_type"] == s]["severity_winsorized"].dropna()
    if len(vals) > 0:
        box_data.append(vals.values)
        box_labels.append(label)

bp = ax.boxplot(box_data, tick_labels=box_labels, patch_artist=True, showfliers=False)
for patch, color in zip(bp["boxes"], colors[:len(box_data)]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel("Severity (winsorized)")
ax.set_title("(c) Severity by sentence type")

# 2d: Severity over time (yearly means with CI)
ax = axes[1, 1]
yearly = sa.groupby("year")["sev"].agg(["mean", "std", "count"]).reset_index()
yearly["se"] = yearly["std"] / np.sqrt(yearly["count"])
yearly = yearly[yearly["count"] >= 30]  # exclude 2026 if too small
ax.errorbar(yearly["year"], yearly["mean"], yerr=1.96 * yearly["se"],
            marker="o", capsize=3, color="#4C72B0", linewidth=1.5)
ax.set_xlabel("Year")
ax.set_ylabel("Mean severity (95% CI)")
ax.set_title("(d) Severity trend (Sample A)")
ax.set_xticks([2020, 2022, 2024, 2026])

plt.tight_layout()
save_figure(fig, "fig2_sentences", "Fig2")
plt.close()

# ============================================================
# FIGURE 3: Bivariate Severity Relationships
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(JOURNAL_WIDTH_IN, 5.12))

# 3a: Severity by gender (violin or box)
ax = axes[0, 0]
male_sev = sa[sa["female"] == 0]["sev"]
female_sev = sa[sa["female"] == 1]["sev"]
bp = ax.boxplot([male_sev.values, female_sev.values],
                tick_labels=["Male", "Female"], patch_artist=True, showfliers=False)
bp["boxes"][0].set_facecolor("#4C72B0")
bp["boxes"][1].set_facecolor("#DD8452")
for box in bp["boxes"]:
    box.set_alpha(0.7)
ax.set_ylabel("Severity (winsorized)")
ax.set_title(f"(a) By gender (d = {cohens_d(male_sev, female_sev):.3f})")

# 3b: Severity by education
ax = axes[0, 1]
edu_medians = []
edu_means = []
edu_ns = []
for i, (code, label) in enumerate(zip(
    [0, 1, 2, 3, 4, 5],
    ["None", "Primary", "Basic", "Secondary", "Vocational", "Higher"]
)):
    g = sa[sa["education_level"] == code]["sev"]
    if len(g) >= 10:
        edu_medians.append(g.median())
        edu_means.append(g.mean())
        edu_ns.append(len(g))

edu_plot_labels = ["None", "Primary", "Basic", "Secondary", "Vocational", "Higher"]
ax.bar(range(len(edu_means)), edu_means, color="#55A868", alpha=0.7, label="Mean")
ax.plot(range(len(edu_medians)), edu_medians, "ro-", markersize=5, label="Median")
ax.set_xticks(range(len(edu_plot_labels)))
ax.set_xticklabels(edu_plot_labels, rotation=30, fontsize=9)
ax.set_ylabel("Severity")
ax.set_title("(b) By education level")
ax.legend(fontsize=8)

# 3c: Severity by age (binned means + LOESS-like moving average)
ax = axes[1, 0]
age_bins = list(range(18, 82, 2))
sa_sorted = sa.sort_values("age")
binned = sa_sorted.groupby(
    pd.cut(sa_sorted["age"], bins=age_bins), observed=False
)["sev"].agg(["mean", "count"])
binned = binned[binned["count"] >= 20]
mid_ages = [(b.left + b.right) / 2 for b in binned.index]
ax.scatter(mid_ages, binned["mean"], s=binned["count"]/10, alpha=0.6, color="#4C72B0")
# Rolling average (smoothed)
window = 5
if len(binned) >= window:
    smoothed = binned["mean"].rolling(window, center=True).mean()
    smooth_ages = [(b.left + b.right) / 2 for b in smoothed.dropna().index]
    ax.plot(smooth_ages, smoothed.dropna().values, "r-", linewidth=2, label="Smoothed")
ax.set_xlabel("Age")
ax.set_ylabel("Mean severity")
ax.set_title("(c) By age (binned means)")
ax.legend(fontsize=8)

# 3d: Severity by employment
ax = axes[1, 1]
emp_means = [
    sa[sa["employed"] == True]["sev"].mean(),
    sa[sa["employed"] == False]["sev"].mean(),
]
emp_medians = [
    sa[sa["employed"] == True]["sev"].median(),
    sa[sa["employed"] == False]["sev"].median(),
]
x = [0, 1]
width = 0.35
ax.bar([xi - width/2 for xi in x], emp_means, width, label="Mean", color="#4C72B0", alpha=0.7)
ax.bar([xi + width/2 for xi in x], emp_medians, width, label="Median", color="#DD8452", alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(["Employed", "Unemployed"])
ax.set_ylabel("Severity")
employed_sev = sa[sa["employed"] == True]["sev"]
unemployed_sev = sa[sa["employed"] == False]["sev"]
ax.set_title(
    f"(d) By employment (d = {cohens_d(employed_sev, unemployed_sev):.3f})"
)
ax.legend(fontsize=8)

plt.tight_layout()
save_figure(fig, "fig3_bivariate", "Fig3")
plt.close()

# ============================================================
# FIGURE 4: Crime Composition by Demographics
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(JOURNAL_WIDTH_IN, 2.96))

crime_colors = {"violent": "#C44E52", "property": "#4C72B0", "traffic": "#55A868",
                "drug": "#8172B3", "other": "#CCB974"}
crime_hatches = {"violent": "", "property": "///", "traffic": "\\\\",
                 "drug": "xx", "other": ".."}

# 4a: Crime composition by gender
ax = axes[0]
for gender_label, gender_val in [("Male", "male"), ("Female", "female")]:
    g = df[df["gender"] == gender_val]
    total = g["crime_category"].notna().sum()
    bottom = 0
    for cat in cat_order:
        pct = (g["crime_category"] == cat).sum() / total * 100
        ax.barh(gender_label, pct, left=bottom, color=crime_colors[cat],
                hatch=crime_hatches[cat], edgecolor="white", linewidth=0.4,
                label=cat.capitalize() if gender_label == "Male" else "")
        if pct >= 10:
            ax.text(bottom + pct/2, gender_label, f"{pct:.0f}%",
                    ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        bottom += pct

ax.set_xlabel("Percentage")
ax.set_title("(a) By gender")
handles, labels = ax.get_legend_handles_labels()

# 4b: Crime composition by education
ax = axes[1]
edu_plot_cats = [("Primary", "primary"), ("Secondary", "secondary"),
                 ("Vocational", "vocational"), ("Higher", "higher")]
for edu_label, edu_val in edu_plot_cats:
    g = df[df["education_clean"] == edu_val]
    total = g["crime_category"].notna().sum()
    bottom = 0
    for cat in cat_order:
        pct = (g["crime_category"] == cat).sum() / total * 100
        ax.barh(edu_label, pct, left=bottom, color=crime_colors[cat],
                hatch=crime_hatches[cat], edgecolor="white", linewidth=0.4)
        if pct >= 10:
            ax.text(bottom + pct/2, edu_label, f"{pct:.0f}%",
                    ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        bottom += pct

ax.set_xlabel("Percentage")
ax.set_title("(b) By education")

fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=7,
           bbox_to_anchor=(0.5, -0.03), frameon=False)

plt.tight_layout(rect=(0, 0.10, 1, 1))
save_figure(fig, "fig4_crime_composition", "Fig4")
plt.close()

print("\nAll figures saved.")
