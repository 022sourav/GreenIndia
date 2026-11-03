# Step 1: clean the crop production data and store everything in a SQLite database

import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
raw_file = BASE / "data" / "crop_production.csv"
rec_file = BASE / "data" / "Crop_recommendation.csv"
db_file = BASE / "greenindia.db"

df = pd.read_csv(raw_file)
report = []
report.append(f"Raw rows: {len(df)}")

# remove extra spaces (for example 'Kharif     ')
for col in ["State_Name", "District_Name", "Season", "Crop"]:
    df[col] = df[col].str.strip()

# keep only the three crops from the original GreenIndia website
df = df[df["Crop"].isin(["Rice", "Wheat", "Sugarcane"])]
report.append(f"Rows for Rice, Wheat, Sugarcane: {len(df)}")

# missing production values
before = len(df)
df = df.dropna(subset=["Production"])
report.append(f"Dropped {before - len(df)} rows with missing production")

# zero area or zero production is not useful for yield
before = len(df)
df = df[(df["Area"] > 0) & (df["Production"] > 0)]
report.append(f"Dropped {before - len(df)} rows with zero area or zero production")

# 2015 has very few rows, so the data for that year is incomplete
before = len(df)
df = df[df["Crop_Year"] < 2015]
report.append(f"Dropped {before - len(df)} rows from 2015 (incomplete year)")

# yield = production / area (tonnes per hectare)
df["Yield"] = df["Production"] / df["Area"]

# remove extreme yield values (above the 99th percentile for each crop)
limit = df.groupby("Crop")["Yield"].transform(lambda x: x.quantile(0.99))
before = len(df)
df = df[df["Yield"] <= limit]
report.append(f"Dropped {before - len(df)} rows with extreme yield (top 1% per crop)")

df = df.drop_duplicates()
df.columns = ["state", "district", "year", "season", "crop", "area_ha", "production_t", "yield_t_ha"]
report.append(f"Final rows: {len(df)}")
report.append(f"States: {df['state'].nunique()}, Districts: {df['district'].nunique()}, Years: {df['year'].min()} to {df['year'].max()}")

# save to SQLite
conn = sqlite3.connect(db_file)
df.to_sql("crop_production", conn, if_exists="replace", index=False)
rec = pd.read_csv(rec_file)
rec.to_sql("crop_recommendation", conn, if_exists="replace", index=False)
conn.execute("CREATE INDEX IF NOT EXISTS idx_crop_year ON crop_production(crop, year)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON crop_production(state)")
conn.commit()
conn.close()

out = BASE / "outputs" / "cleaning_report.txt"
out.write_text("\n".join(report))
print("\n".join(report))
print("Database saved:", db_file)
