# GreenIndia - Crop Analytics App (Streamlit)
# Run with:  streamlit run app.py

import sqlite3
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DB = BASE / "greenindia.db"

st.set_page_config(page_title="GreenIndia Crop Analytics", page_icon="🌾", layout="wide")

if not DB.exists():
    st.error("Database not found. Please run  python run_all.py  first.")
    st.stop()


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB)
    data = pd.read_sql("SELECT * FROM crop_production", conn)
    conn.close()
    return data


@st.cache_resource
def load_model(name):
    return joblib.load(BASE / "models" / name)


df = load_data()

st.title("🌾 GreenIndia: Crop Analytics")
st.caption("Rice, Wheat and Sugarcane in India | district-wise data 1997-2014 | soil and climate based crop recommendation")

page = st.sidebar.radio("Go to", ["Dashboard", "Crop Recommender", "Yield Predictor", "About"])

# ---------------------------------------------------------------- Dashboard
if page == "Dashboard":
    st.sidebar.header("Filters")
    crops = st.sidebar.multiselect("Crop", ["Rice", "Wheat", "Sugarcane"], default=["Rice", "Wheat", "Sugarcane"])
    years = st.sidebar.slider("Years", 1997, 2014, (1997, 2014))
    seasons = st.sidebar.multiselect("Season", sorted(df["season"].unique()), default=sorted(df["season"].unique()))

    d = df[df["crop"].isin(crops) & df["year"].between(years[0], years[1]) & df["season"].isin(seasons)]
    if d.empty:
        st.warning("No data for these filters.")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", f"{len(d):,}")
    c2.metric("States / UTs", d["state"].nunique())
    c3.metric("Total area (million ha)", f"{d['area_ha'].sum() / 1e6:,.1f}")
    c4.metric("Average yield (t/ha)", f"{d['production_t'].sum() / d['area_ha'].sum():.2f}")

    st.subheader("Yield trend")
    st.caption("Sugarcane yield is much higher than rice and wheat, so it is shown separately.")
    trend = d.groupby(["year", "crop"]).agg(prod=("production_t", "sum"), area=("area_ha", "sum")).reset_index()
    trend["yield"] = trend["prod"] / trend["area"]
    small = trend[trend["crop"].isin(["Rice", "Wheat"])].pivot(index="year", columns="crop", values="yield")
    left, right = st.columns(2)
    with left:
        st.write("Rice and Wheat (t/ha)")
        if not small.empty:
            st.line_chart(small)
    with right:
        st.write("Sugarcane (t/ha)")
        cane = trend[trend["crop"] == "Sugarcane"].set_index("year")["yield"]
        if not cane.empty:
            st.line_chart(cane)

    st.subheader("Top states")
    crop_for_states = st.selectbox("Choose crop", crops)
    top = (d[d["crop"] == crop_for_states].groupby("state")["production_t"].sum()
           .sort_values(ascending=False).head(10) / 1e6)
    st.bar_chart(top)
    st.caption("Total production in million tonnes (sum of all selected years).")

    st.subheader("Season comparison")
    seas = d.groupby(["season", "crop"])["production_t"].sum().reset_index()
    seas["production_t"] = seas["production_t"] / 1e6
    st.bar_chart(seas.pivot(index="season", columns="crop", values="production_t").fillna(0))

    with st.expander("Show data table"):
        st.dataframe(d.head(1000))
        st.download_button("Download filtered data (CSV)", d.to_csv(index=False), "filtered_crop_data.csv")

# ---------------------------------------------------------------- Crop recommender
elif page == "Crop Recommender":
    st.subheader("Which crop is best for my soil and climate?")
    saved = load_model("crop_recommender.joblib")
    model = saved["model"]
    st.write(f"Model: **{saved['name']}** | test accuracy: **{saved['test_accuracy']:.1%}** (22 crops)")

    c1, c2, c3 = st.columns(3)
    N = c1.slider("Nitrogen (N)", 0, 140, 90)
    P = c2.slider("Phosphorus (P)", 5, 145, 42)
    K = c3.slider("Potassium (K)", 5, 205, 43)
    temp = c1.slider("Temperature (°C)", 8.0, 44.0, 21.0)
    hum = c2.slider("Humidity (%)", 14.0, 100.0, 80.0)
    ph = c3.slider("Soil pH", 3.5, 9.9, 6.5)
    rain = c1.slider("Rainfall (mm)", 20.0, 300.0, 203.0)

    if st.button("Recommend crop"):
        x = pd.DataFrame([[N, P, K, temp, hum, ph, rain]], columns=saved["features"])
        probs = pd.Series(model.predict_proba(x)[0], index=model.classes_).sort_values(ascending=False)
        st.success(f"Recommended crop: **{probs.index[0].upper()}** ({probs.iloc[0]:.0%} confidence)")
        st.write("Top 3 crops")
        st.bar_chart(probs.head(3))
    st.caption("Trained on the Kaggle Crop Recommendation dataset. This is a learning project, not agronomic advice.")

# ---------------------------------------------------------------- Yield predictor
elif page == "Yield Predictor":
    st.subheader("Predict crop yield")
    saved = load_model("yield_model.joblib")
    c1, c2, c3 = st.columns(3)
    state = c1.selectbox("State", saved["states"])
    crop = c2.selectbox("Crop", ["Rice", "Wheat", "Sugarcane"])
    season = c3.selectbox("Season", saved["seasons"])
    year = c1.slider("Year", 1997, 2020, 2014)
    area = c2.number_input("Area (hectares)", min_value=1.0, value=float(saved["median_area"][crop]))

    if st.button("Predict yield"):
        row = pd.DataFrame(0, index=[0], columns=saved["columns"])
        row["year"] = year
        row["log_area"] = np.log(area)
        for col in [f"state_{state}", f"crop_{crop}", f"season_{season}"]:
            if col in row.columns:
                row[col] = 1
        pred = float(np.exp(saved["model"].predict(row)[0]))
        st.success(f"Predicted yield: **{pred:.2f} tonnes/hectare**  |  Expected production: **{pred * area:,.0f} tonnes**")
    st.caption("Random Forest trained on district-level data for 1997-2014. Years after 2014 are extrapolation.")

# ---------------------------------------------------------------- About
else:
    st.subheader("About this project")
    st.write("""
GreenIndia started as a small crop-information website (HTML/PHP). It has now been rebuilt as a data analytics project:

1. Cleaned district-wise crop production data and stored it in a **SQL database**
2. Analysed production and yield trends with **SQL queries**
3. Built a **crop recommendation model** from soil and climate data
4. Built a **yield prediction model** and this **dashboard**

Data: Ministry of Agriculture & Farmers Welfare (data.gov.in, via Kaggle) and the Kaggle Crop Recommendation dataset.
""")
