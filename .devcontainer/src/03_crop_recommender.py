# Step 3: crop recommendation model (classification)
# Input: N, P, K, temperature, humidity, ph, rainfall  ->  Output: best crop

import sqlite3
from pathlib import Path
import joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE = Path(__file__).resolve().parents[1]
charts = BASE / "outputs" / "charts"
sns.set_style("whitegrid")

conn = sqlite3.connect(BASE / "greenindia.db")
df = pd.read_sql("SELECT * FROM crop_recommendation", conn)
conn.close()
print("Shape:", df.shape, "| missing values:", df.isna().sum().sum(), "| crops:", df["label"].nunique())

features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
X = df[features]
y = df["label"]

# ---- EDA charts ----
plt.figure(figsize=(8, 7))
sns.heatmap(df[features].corr(), annot=True, fmt=".2f", cmap="RdYlGn", center=0)
plt.title("Correlation between soil and climate features")
plt.tight_layout()
plt.savefig(charts / "07_recommender_correlation.png", dpi=150)
plt.close()

crop_means = df.groupby("label")[features].mean()
plt.figure(figsize=(9, 8))
sns.heatmap((crop_means - crop_means.mean()) / crop_means.std(), cmap="coolwarm", center=0)
plt.title("Average conditions for each crop (standardised)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(charts / "08_crop_conditions_heatmap.png", dpi=150)
plt.close()

# ---- compare models using 5-fold cross validation on the training set ----
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

models = {
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
}

scores = {}
for name, model in models.items():
    cv = cross_val_score(model, X_train, y_train, cv=5)
    scores[name] = cv.mean()
    print(f"{name}: CV accuracy = {cv.mean():.4f}")

plt.figure(figsize=(7, 4))
plt.bar(scores.keys(), scores.values(), color="#2e8b57")
plt.ylim(0.8, 1.0)
plt.ylabel("5-fold CV accuracy")
plt.title("Model comparison (crop recommendation)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(charts / "09_model_comparison.png", dpi=150)
plt.close()

# ---- final model: best one from cross validation ----
best_name = max(scores, key=scores.get)
best_model = models[best_name]
best_model.fit(X_train, y_train)
pred = best_model.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"\nBest model: {best_name} | test accuracy = {acc:.4f}")

report = classification_report(y_test, pred)
(BASE / "outputs" / "recommender_report.txt").write_text(
    f"Best model: {best_name}\nTest accuracy: {acc:.4f}\n\nCV scores:\n"
    + "\n".join(f"{k}: {v:.4f}" for k, v in scores.items()) + "\n\n" + report)

cm = confusion_matrix(y_test, pred, labels=sorted(y.unique()))
plt.figure(figsize=(11, 9))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=sorted(y.unique()), yticklabels=sorted(y.unique()))
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title(f"Confusion matrix ({best_name}, test accuracy {acc:.1%})")
plt.tight_layout()
plt.savefig(charts / "10_confusion_matrix.png", dpi=150)
plt.close()

# feature importance (only works for tree models, so we fit a random forest for the chart)
rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(X_train, y_train)
imp = pd.Series(rf.feature_importances_, index=features).sort_values()
plt.figure(figsize=(7, 4))
imp.plot(kind="barh", color="#2e8b57")
plt.title("Feature importance (Random Forest)")
plt.tight_layout()
plt.savefig(charts / "11_feature_importance.png", dpi=150)
plt.close()
print("\nFeature importance:\n", imp.sort_values(ascending=False).round(3))

# save the model for the app (trained on all the data)
best_model.fit(X, y)
joblib.dump({"model": best_model, "features": features, "name": best_name, "test_accuracy": acc},
            BASE / "models" / "crop_recommender.joblib", compress=3)
print("Model saved.")
