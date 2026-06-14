import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import load_data, get_filter_options

st.set_page_config(page_title="Country Profile", layout="wide")

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
st.sidebar.markdown("### 📊 Country Profile")
st.sidebar.markdown("---")

selected_country = st.sidebar.selectbox("Country", options["countries"])
unit = st.sidebar.radio("Unit", ["TWh", "ktoe"])
value_col = "value_twh" if unit == "TWh" else "value_ktoe"

# --- Page header ---
st.markdown('<p class="section-label">Country Profile</p>', unsafe_allow_html=True)
st.markdown(f'<h1 class="page-title">{selected_country}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">Industrial final energy consumption — all sectors, 2000–2023</p>', unsafe_allow_html=True)

# --- Filter to selected country ---
dfc = df[df["country"] == selected_country].copy()

# --- Summary metrics for latest year ---
latest_year = int(df["year"].max())
dfc_latest = dfc[dfc["year"] == latest_year]
total_latest = dfc_latest[value_col].sum()

eu27_latest = df[df["year"] == latest_year][value_col].sum()
eu27_avg = eu27_latest / df["country"].nunique()

top_sector = (
    dfc_latest.groupby("sector")[value_col].sum().idxmax()
    if not dfc_latest.empty else "—"
)
top_fuel = (
    dfc_latest.groupby("fuel")[value_col].sum().idxmax()
    if not dfc_latest.empty else "—"
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"Total FEC {latest_year}", f"{total_latest:,.1f} {unit}")
with col2:
    st.metric("vs EU27 average", f"{(total_latest / eu27_avg * 100):.0f}%",
              delta=f"{total_latest - eu27_avg:+.1f} {unit}")
with col3:
    st.markdown(
        f'<p style="font-size:0.85rem;color:#5a6a7a;margin-bottom:0.1rem;">Top sector</p>'
        f'<p style="font-size:1rem;font-weight:600;color:#0f1923;line-height:1.3;margin:0;">{top_sector}</p>',
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f'<p style="font-size:0.85rem;color:#5a6a7a;margin-bottom:0.1rem;">Top fuel</p>'
        f'<p style="font-size:1rem;font-weight:600;color:#0f1923;line-height:1.3;margin:0;">{top_fuel}</p>',
        unsafe_allow_html=True
    )

st.markdown("---")

# --- Chart 1: Total consumption over time by sector (stacked area) ---
st.markdown('<p class="section-label">Energy consumption by sector — 2000 to 2023</p>', unsafe_allow_html=True)

sector_time = (
    dfc.groupby(["year", "sector"])[value_col]
    .sum()
    .reset_index()
)

PALETTE = [
    "#0f4c81", "#2a6fa8", "#4a9fd4", "#7aafd4", "#c84b31",
    "#e07b5a", "#f0a882", "#1a6b3c", "#4a9b6a", "#f5c842", "#9b6b2a"
]

fig_area = px.area(
    sector_time,
    x="year",
    y=value_col,
    color="sector",
    labels={value_col: unit, "year": "Year", "sector": "Sector"},
    color_discrete_sequence=PALETTE
)
fig_area.update_layout(
    paper_bgcolor="#f7f8fa",
    plot_bgcolor="white",
    height=380,
    margin=dict(l=0, r=0, t=10, b=0),
    font=dict(family="Inter", size=11, color="#0f1923"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(gridcolor="#e8ecf0", title=""),
    yaxis=dict(gridcolor="#e8ecf0", title=unit)
)
st.plotly_chart(fig_area, use_container_width=True)

st.markdown("---")

# --- Chart 2: Fuel mix in latest year (donut) and over time (stacked bar) ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(f'<p class="section-label">Fuel mix — {latest_year}</p>', unsafe_allow_html=True)

    fuel_latest = (
        dfc_latest.groupby("fuel")[value_col]
        .sum()
        .reset_index()
        .sort_values(value_col, ascending=False)
    )
    # keep top 8, group rest as Other
    if len(fuel_latest) > 8:
        top8 = fuel_latest.head(8)
        other_val = fuel_latest.iloc[8:][value_col].sum()
        other_row = pd.DataFrame([{"fuel": "Other", value_col: other_val}])
        fuel_latest = pd.concat([top8, other_row], ignore_index=True)

    fig_donut = px.pie(
        fuel_latest,
        names="fuel",
        values=value_col,
        hole=0.55,
        color_discrete_sequence=PALETTE
    )
    fig_donut.update_traces(textposition="outside", textinfo="percent+label")
    fig_donut.update_layout(
        paper_bgcolor="#f7f8fa",
        height=340,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=10, color="#0f1923"),
        showlegend=False
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.markdown('<p class="section-label">Fuel mix evolution — 2000 to 2023</p>', unsafe_allow_html=True)

    fuel_time = (
        dfc.groupby(["year", "fuel"])[value_col]
        .sum()
        .reset_index()
    )

    fig_fuel_bar = px.bar(
        fuel_time,
        x="year",
        y=value_col,
        color="fuel",
        labels={value_col: unit, "year": "Year", "fuel": "Fuel"},
        color_discrete_sequence=PALETTE
    )
    fig_fuel_bar.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=340,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=9)),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit),
        barmode="stack"
    )
    st.plotly_chart(fig_fuel_bar, use_container_width=True)

st.markdown("---")

# --- Chart 3: Sector breakdown for latest year ---
st.markdown(f'<p class="section-label">Sector breakdown — {latest_year}</p>', unsafe_allow_html=True)

sector_latest = (
    dfc_latest.groupby("sector")[value_col]
    .sum()
    .reset_index()
    .sort_values(value_col, ascending=True)
)

fig_sector = px.bar(
    sector_latest,
    x=value_col,
    y="sector",
    orientation="h",
    labels={value_col: unit, "sector": ""},
    color=value_col,
    color_continuous_scale=[[0, "#e8f0f7"], [1, "#0f4c81"]]
)
fig_sector.update_layout(
    paper_bgcolor="#f7f8fa",
    plot_bgcolor="white",
    height=360,
    margin=dict(l=0, r=20, t=10, b=0),
    font=dict(family="Inter", size=11, color="#0f1923"),
    coloraxis_showscale=False,
    xaxis=dict(gridcolor="#e8ecf0", title=unit),
    yaxis=dict(gridcolor="rgba(0,0,0,0)")
)
st.plotly_chart(fig_sector, use_container_width=True)
