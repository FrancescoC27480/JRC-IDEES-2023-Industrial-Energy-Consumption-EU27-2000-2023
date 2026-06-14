import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import load_data, get_filter_options

st.set_page_config(page_title="European Overview", layout="wide")

# --- Styles ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Serif+Display&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f1923; }
    [data-testid="stSidebar"] * { color: #c9d4e0 !important; }
    [data-testid="stSidebar"] label { color: #7a9bbf !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
    .main { background-color: #f7f8fa; }
    .page-title { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #0f1923; margin-bottom: 0.2rem; }
    .page-subtitle { font-size: 0.9rem; color: #5a6a7a; margin-bottom: 1.5rem; font-weight: 300; }
    .section-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; color: #c84b31; font-weight: 600; margin-bottom: 0.4rem; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Load data ---
df = load_data()
options = get_filter_options(df)

# --- Sidebar filters ---
st.sidebar.markdown("### 🗺 European Overview")
st.sidebar.markdown("---")

selected_sector = st.sidebar.selectbox(
    "Sector",
    ["All sectors"] + options["sectors"]
)

if selected_sector != "All sectors":
    available_subsectors = sorted(
        df[df["sector"] == selected_sector]["subsector"].dropna().unique()
    )
    selected_subsector = st.sidebar.selectbox(
        "Subsector",
        ["All subsectors"] + available_subsectors
    )
else:
    st.sidebar.selectbox("Subsector", ["Select a sector first"], disabled=True)
    selected_subsector = "All subsectors"

selected_fuel = st.sidebar.selectbox(
    "Fuel",
    ["All fuels"] + options["fuels"]
)

selected_end_use = st.sidebar.selectbox(
    "End Use Type",
    ["All end use types"] + options["end_use_types"]
)

selected_year = st.sidebar.slider(
    "Year",
    min_value=int(df["year"].min()),
    max_value=int(df["year"].max()),
    value=2023,
    step=1
)

unit = st.sidebar.radio("Unit", ["TWh", "ktoe"])
value_col = "value_twh" if unit == "TWh" else "value_ktoe"

# --- Filter data ---
dff = df[df["year"] == selected_year].copy()

if selected_sector != "All sectors":
    dff = dff[dff["sector"] == selected_sector]
if selected_subsector != "All subsectors":
    dff = dff[dff["subsector"] == selected_subsector]
if selected_fuel != "All fuels":
    dff = dff[dff["fuel"] == selected_fuel]
if selected_end_use != "All end use types":
    dff = dff[dff["end_use_type"] == selected_end_use]

# --- Aggregate by country ---
country_totals = (
    dff.groupby("country")[value_col]
    .sum()
    .reset_index()
    .rename(columns={value_col: "total"})
)

# --- ISO alpha-3 codes for Plotly choropleth ---
iso_map = {
    "Austria": "AUT", "Belgium": "BEL", "Bulgaria": "BGR", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Germany": "DEU", "Denmark": "DNK", "Estonia": "EST",
    "Greece": "GRC", "Spain": "ESP", "Finland": "FIN", "France": "FRA",
    "Croatia": "HRV", "Hungary": "HUN", "Ireland": "IRL", "Italy": "ITA",
    "Lithuania": "LTU", "Luxembourg": "LUX", "Latvia": "LVA", "Malta": "MLT",
    "Netherlands": "NLD", "Poland": "POL", "Portugal": "PRT", "Romania": "ROU",
    "Sweden": "SWE", "Slovenia": "SVN", "Slovakia": "SVK"
}

country_totals["iso_alpha"] = country_totals["country"].map(iso_map)
country_totals = country_totals.dropna(subset=["iso_alpha"])

# --- Page header ---
st.markdown('<p class="section-label">European Overview</p>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Industrial Energy Consumption across EU27</h1>', unsafe_allow_html=True)

filter_desc = f"{selected_sector} · {selected_year} · {unit}"
st.markdown(f'<p class="page-subtitle">{filter_desc}</p>', unsafe_allow_html=True)

# --- Summary metrics ---
col1, col2, col3 = st.columns(3)
total = country_totals["total"].sum()
top_country = country_totals.loc[country_totals["total"].idxmax(), "country"] if not country_totals.empty else "—"
top_value = country_totals["total"].max() if not country_totals.empty else 0

with col1:
    st.metric("Total EU27", f"{total:,.1f} {unit}")
with col2:
    st.metric("Largest consumer", top_country)
with col3:
    st.metric(f"{top_country} share", f"{(top_value/total*100):.1f}%" if total > 0 else "—")

st.markdown("---")

# --- Choropleth map ---
if country_totals.empty:
    st.warning("No data matches the selected filters.")
else:
    fig_map = px.choropleth(
        country_totals,
        locations="iso_alpha",
        color="total",
        hover_name="country",
        hover_data={"total": ":.1f", "iso_alpha": False},
        color_continuous_scale=[
            [0.0, "#e8f0f7"],
            [0.3, "#7aafd4"],
            [0.6, "#2a6fa8"],
            [1.0, "#0f1923"]
        ],
        scope="europe",
        labels={"total": unit},
        title=f"Final Energy Consumption by Country — {selected_year}"
    )

    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type="natural earth",
            bgcolor="#f7f8fa",
            lataxis_range=[34, 72],
            lonaxis_range=[-12, 35]
        ),
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="#f7f8fa",
        margin=dict(l=0, r=0, t=40, b=0),
        height=520,
        font=dict(family="Inter", size=12, color="#0f1923"),
        coloraxis_colorbar=dict(
            title=unit,
            thickness=12,
            len=0.6,
            tickfont=dict(size=10)
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # --- Bar chart ranking ---
    st.markdown('<p class="section-label">Country Ranking</p>', unsafe_allow_html=True)

    fig_bar = px.bar(
        country_totals.sort_values("total", ascending=True),
        x="total",
        y="country",
        orientation="h",
        labels={"total": unit, "country": ""},
        color="total",
        color_continuous_scale=[
            [0.0, "#e8f0f7"],
            [1.0, "#0f1923"]
        ]
    )

    fig_bar.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="#f7f8fa",
        showlegend=False,
        coloraxis_showscale=False,
        height=600,
        margin=dict(l=0, r=20, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        xaxis=dict(gridcolor="#e8ecf0", title=unit),
        yaxis=dict(gridcolor="rgba(0,0,0,0)")
    )

    st.plotly_chart(fig_bar, use_container_width=True)
