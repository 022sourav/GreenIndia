# Step 4: yield prediction model (regression)
# Predict yield (tonnes/hectare) from state, crop, season, year and area.
# We train on the older years (1997-2010) and test on the newer years (2011-2014),
# so the test is like predicting the "future" and not a random shuffle.

import sqlite3
from pathlib import Path
import numpy as np
import joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

BASE = Path(__file__).resolve().parents[1]
charts = BASE / "outputs" / "charts"

conn = sqlite3.connect(BASE / "greenindia.db")
df = pd.read_sql("SELECT state, crop, season, year, area_ha, yield_t_ha FROM crop_production", conn)
conn.close()

# the model predicts log(yield) because sugarcane yield is much bigger than rice and wheat
df["log_yield"] = np.log(df["yield_t_ha"])
df["log_area"] = np.log(df["area_ha"])

X = pd.get_dummies(df[["state", "crop", "season", "year", "log_area"]], columns=["state", "crop", "season"])
y = df["log_yield"]

train = df["year"] <= 2010
X_train, X_test = X[train], X[~train]
y_train, y_test = y[train], y[~train]
print("Train rows:", len(X_train), "| Test rows:", len(X_test))

# baseline: always predict the average yield of the crop (from training years)
crop_mean = df[train].groupby("crop")["yield_t_ha"].mean()
baseline_pred = df[~train]["crop"].map(crop_mean)

lr = LinearRegression().fit(X_train, y_train)
rf = RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1).fit(X_train, y_train)

actual = df[~train]["yield_t_ha"]
results = []
for name, pred in [("Baseline (crop average)", baseline_pred),
                   ("Linear Regression", np.exp(lr.predict(X_test))),
                   ("Random Forest", np.exp(rf.predict(X_test)))]:
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    # MAE for rice and wheat only (their yields are small numbers, so this is easier to read)
    small = df[~train]["crop"].isin(["Rice", "Wheat"]).values
    mae_small = mean_absolute_error(actual[small], np.asarray(pred)[small])
    results.append([name, round(mae, 3), round(mae_small, 3), round(r2, 3)])

res = pd.DataFrame(results, columns=["Model", "MAE all crops (t/ha)", "MAE rice+wheat (t/ha)", "R2 all crops"])
print(res.to_string(index=False))
res.to_csv(BASE / "outputs" / "tables" / "yield_model_results.csv", index=False)

# chart: actual vs predicted for rice and wheat
pred_rf = np.exp(rf.predict(X_test))
mask = df[~train]["crop"].isin(["Rice", "Wheat"]).values
plt.figure(figsize=(6, 6))
plt.scatter(actual[mask], pred_rf[mask], s=6, alpha=0.4, color="#2e8b57")
plt.plot([0, 7], [0, 7], color="red")
plt.xlim(0, 7)
plt.ylim(0, 7)
plt.xlabel("Actual yield (t/ha)")
plt.ylabel("Predicted yield (t/ha)")
plt.title("Random Forest: actual vs predicted (rice and wheat, 2011-2014)")
plt.tight_layout()
plt.savefig(charts / "12_yield_actual_vs_predicted.png", dpi=150)
plt.close()

# final model: train again on all the years and save for the app
rf_final = RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42, n_jobs=-1).fit(X, y)
joblib.dump({"model": rf_final, "columns": list(X.columns),
             "states": sorted(df["state"].unique()), "seasons": sorted(df["season"].unique()),
             "median_area": df.groupby("crop")["area_ha"].median().to_dict()},
            BASE / "models" / "yield_model.joblib", compress=3)
print("Model saved.")
