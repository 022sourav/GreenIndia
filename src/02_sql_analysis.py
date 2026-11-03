# Step 2: run the SQL queries and make charts for the production analysis

import re
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(BASE / "greenindia.db")
charts = BASE / "outputs" / "charts"
tables = BASE / "outputs" / "tables"
sns.set_style("whitegrid")

# read the queries from the sql file
text = (BASE / "sql" / "queries.sql").read_text()
parts = re.split(r"-- name: (\w+)", text)
queries = {}
for i in range(1, len(parts), 2):
    queries[parts[i]] = parts[i + 1].strip()

results = {}
for name, q in queries.items():
    results[name] = pd.read_sql(q, conn)
    results[name].to_csv(tables / f"{name}.csv", index=False)   # these csv files can also be used in Power BI / Tableau
    print(name, results[name].shape)

colors = {"Rice": "#2e8b57", "Wheat": "#d4a017", "Sugarcane": "#8b4513"}

# chart 1: yield trend for rice and wheat
trend = results["yearly_trend"]
fig, ax = plt.subplots(figsize=(8, 4.5))
for crop in ["Rice", "Wheat"]:
    d = trend[trend["crop"] == crop]
    ax.plot(d["year"], d["yield_t_ha"], marker="o", label=crop, color=colors[crop])
ax.set_title("Yield trend of Rice and Wheat in India (1997-2014)")
ax.set_xlabel("Year")
ax.set_xticks(range(1997, 2015, 2))
ax.set_ylabel("Yield (tonnes per hectare)")
ax.legend()
plt.tight_layout()
plt.savefig(charts / "01_yield_trend_rice_wheat.png", dpi=150)
plt.close()

# chart 2: sugarcane production trend
d = trend[trend["crop"] == "Sugarcane"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(d["year"], d["total_production_t"] / 1e6, marker="o", color=colors["Sugarcane"])
ax.set_title("Sugarcane production in India (records in the dataset)")
ax.set_xlabel("Year")
ax.set_xticks(range(1997, 2015, 2))
ax.set_ylabel("Production (million tonnes)")
plt.tight_layout()
plt.savefig(charts / "02_sugarcane_production.png", dpi=150)
plt.close()

# chart 3: top 5 states for each crop
top = results["top_states"]
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, crop in zip(axes, ["Rice", "Wheat", "Sugarcane"]):
    d = top[top["crop"] == crop].sort_values("total_production_t")
    ax.barh(d["state"], d["total_production_t"] / 1e6, color=colors[crop])
    ax.set_title(f"Top 5 states: {crop}")
    ax.set_xlabel("Total production (million tonnes)")
plt.tight_layout()
plt.savefig(charts / "03_top_states_by_crop.png", dpi=150)
plt.close()

# chart 4: production by season
season = results["season_summary"]
pivot = season.pivot(index="season", columns="crop", values="total_production_t").fillna(0) / 1e6
pivot.plot(kind="bar", figsize=(8, 4.5), color=[colors[c] for c in pivot.columns])
plt.title("Production by season")
plt.ylabel("Total production (million tonnes)")
plt.xlabel("Season")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(charts / "04_production_by_season.png", dpi=150)
plt.close()

# chart 5: states with the best yield growth (rice and wheat)
growth = results["yield_growth"]
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, crop in zip(axes, ["Rice", "Wheat"]):
    d = growth[growth["crop"] == crop].head(8).sort_values("growth_percent")
    ax.barh(d["state"], d["growth_percent"], color=colors[crop])
    ax.set_title(f"{crop}: yield growth, 1998-2000 vs 2012-2014")
    ax.set_xlabel("Growth (%)")
plt.tight_layout()
plt.savefig(charts / "05_yield_growth_by_state.png", dpi=150)
plt.close()

# chart 6: heatmap of yield by state (top states by area) and crop
yield_state = pd.read_sql(
    """SELECT state, crop, SUM(production_t) / SUM(area_ha) AS yield_t_ha
       FROM crop_production
       WHERE crop IN ('Rice', 'Wheat') AND state IN (
           SELECT state FROM crop_production GROUP BY state ORDER BY SUM(area_ha) DESC LIMIT 15)
       GROUP BY state, crop""", conn)
heat = yield_state.pivot(index="state", columns="crop", values="yield_t_ha")
plt.figure(figsize=(6, 7))
sns.heatmap(heat, annot=True, fmt=".2f", cmap="YlGn")
plt.title("Average yield (t/ha) in the 15 largest states")
plt.tight_layout()
plt.savefig(charts / "06_yield_heatmap.png", dpi=150)
plt.close()

conn.close()
print("Charts saved in outputs/charts")
