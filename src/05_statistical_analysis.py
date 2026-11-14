# Step 5: statistical analysis (trend test, group comparisons, correlation, ANOVA, confidence intervals)

import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parents[1]
charts = BASE / "outputs" / "charts"
tables = BASE / "outputs" / "tables"
sns.set_style("whitegrid")
colors = {"Rice": "#2e8b57", "Wheat": "#d4a017", "Sugarcane": "#8b4513"}

conn = sqlite3.connect(BASE / "greenindia.db")
df = pd.read_sql("SELECT * FROM crop_production", conn)
rec = pd.read_sql("SELECT * FROM crop_recommendation", conn)
conn.close()

rows = []   # all test results go in this list

# ---------- 1. Is the yield going up over the years? (linear trend test) ----------
yearly = df.groupby(["crop", "year"]).agg(p=("production_t", "sum"), a=("area_ha", "sum")).reset_index()
yearly["yield"] = yearly["p"] / yearly["a"]
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, crop in zip(axes, colors):
    d = yearly[yearly["crop"] == crop]
    res = stats.linregress(d["year"], d["yield"])
    ax.scatter(d["year"], d["yield"], color=colors[crop])
    ax.plot(d["year"], res.intercept + res.slope * d["year"], color="black", linestyle="--")
    ax.set_title(f"{crop}: slope {res.slope:+.3f} t/ha per year (p = {res.pvalue:.3f})", fontsize=10)
    ax.set_xticks(range(1997, 2015, 4))
    ax.set_xlabel("Year")
    ax.set_ylabel("Yield (t/ha)")
    rows.append([f"Yield trend: {crop}", "Linear regression of yearly yield on year",
                 f"slope = {res.slope:+.3f} t/ha per year, R2 = {res.rvalue**2:.2f}", res.pvalue])
plt.tight_layout()
plt.savefig(charts / "13_yield_trend_tests.png", dpi=150)
plt.close()

# ---------- 2. Does the season change rice yield? (Kruskal-Wallis, yields are skewed) ----------
rice = df[df["crop"] == "Rice"]
groups = [g["yield_t_ha"].values for _, g in rice.groupby("season") if len(g) >= 50]
names = [s for s, g in rice.groupby("season") if len(g) >= 50]
h, p = stats.kruskal(*groups)
med = rice.groupby("season")["yield_t_ha"].median().round(2).to_dict()
rows.append(["Rice yield by season", "Kruskal-Wallis test across seasons", f"H = {h:.0f}; medians: " + ", ".join(f"{k} {v}" for k, v in med.items()), p])
plt.figure(figsize=(8, 4.5))
order = rice.groupby("season")["yield_t_ha"].median().sort_values().index
sns.boxplot(data=rice, x="season", y="yield_t_ha", order=order, color="#2e8b57", showfliers=False)
plt.title("Rice yield by season (district-level records)")
plt.xlabel("Season")
plt.ylabel("Yield (t/ha)")
plt.tight_layout()
plt.savefig(charts / "14_rice_yield_by_season.png", dpi=150)
plt.close()

# ---------- 3. Is Punjab different from the other states for wheat? (Mann-Whitney) ----------
wheat = df[df["crop"] == "Wheat"].copy()
wheat["group"] = np.where(wheat["state"] == "Punjab", "Punjab", "Other states")
a = wheat[wheat["group"] == "Punjab"]["yield_t_ha"]
b = wheat[wheat["group"] == "Other states"]["yield_t_ha"]
u, p = stats.mannwhitneyu(a, b, alternative="greater")
rows.append(["Wheat yield: Punjab vs other states", "Mann-Whitney U test (one-sided)",
             f"median Punjab {a.median():.2f} t/ha vs others {b.median():.2f} t/ha", p])
plt.figure(figsize=(6, 4.5))
sns.boxplot(data=wheat, x="group", y="yield_t_ha", order=["Punjab", "Other states"], color="#d4a017", showfliers=False)
plt.title("Wheat yield: Punjab vs other states")
plt.xlabel("")
plt.ylabel("Yield (t/ha)")
plt.tight_layout()
plt.savefig(charts / "15_wheat_punjab_vs_others.png", dpi=150)
plt.close()

# ---------- 4. Do bigger districts have higher yield? (Spearman correlation) ----------
for crop in colors:
    d = df[df["crop"] == crop]
    r, p = stats.spearmanr(d["area_ha"], d["yield_t_ha"])
    rows.append([f"Area vs yield: {crop}", "Spearman correlation (district-level records)", f"rho = {r:+.2f}", p])

# ---------- 5. Why we use log(yield): skewness ----------
sk_raw = stats.skew(df["yield_t_ha"])
sk_log = stats.skew(np.log(df["yield_t_ha"]))
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(df["yield_t_ha"], bins=60, color="#2e8b57")
axes[0].set_title(f"Yield (skewness = {sk_raw:.1f})")
axes[1].hist(np.log(df["yield_t_ha"]), bins=60, color="#2e8b57")
axes[1].set_title(f"log(Yield) (skewness = {sk_log:.1f})")
for ax in axes:
    ax.set_ylabel("Records")
axes[0].set_xlabel("Yield (t/ha)")
axes[1].set_xlabel("log(yield)")
plt.tight_layout()
plt.savefig(charts / "16_yield_skewness.png", dpi=150)
plt.close()
rows.append(["Yield distribution", "Skewness before and after log transform", f"skewness {sk_raw:.1f} -> {sk_log:.1f}", np.nan])

# ---------- 6. ANOVA: do soil and climate features differ between crops? ----------
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
anova = []
for f in features:
    groups = [g[f].values for _, g in rec.groupby("label")]
    F, p = stats.f_oneway(*groups)
    grand = rec[f].mean()
    ss_between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ss_total = ((rec[f] - grand) ** 2).sum()
    eta = ss_between / ss_total          # eta squared = how much of the variation is explained by the crop
    anova.append([f, F, p, eta])
    rows.append([f"ANOVA: {f} across 22 crops", "One-way ANOVA", f"F = {F:.0f}, eta squared = {eta:.2f}", p])
anova = pd.DataFrame(anova, columns=["feature", "F", "p_value", "eta_squared"]).sort_values("eta_squared")
plt.figure(figsize=(7, 4))
plt.barh(anova["feature"], anova["eta_squared"], color="#2e8b57")
plt.xlabel("Eta squared (share of variation explained by the crop)")
plt.title("Which features differ most between crops?")
plt.tight_layout()
plt.savefig(charts / "17_anova_effect_size.png", dpi=150)
plt.close()

# ---------- 7. 95% confidence interval of the mean yield ----------
ci_rows = []
for crop in colors:
    y = df[df["crop"] == crop]["yield_t_ha"]
    lo, hi = stats.t.interval(0.95, len(y) - 1, loc=y.mean(), scale=stats.sem(y))
    ci_rows.append([crop, len(y), y.mean(), lo, hi])
ci = pd.DataFrame(ci_rows, columns=["crop", "records", "mean_yield", "ci_low", "ci_high"])
ci.to_csv(tables / "yield_confidence_intervals.csv", index=False)

out = pd.DataFrame(rows, columns=["test", "method", "result", "p_value"])
out.to_csv(tables / "statistical_tests.csv", index=False)
anova.sort_values("eta_squared", ascending=False).to_csv(tables / "anova_features.csv", index=False)
pd.set_option("display.width", 200, "display.max_colwidth", 90)
print(out.to_string(index=False))
print(ci.round(3).to_string(index=False))
