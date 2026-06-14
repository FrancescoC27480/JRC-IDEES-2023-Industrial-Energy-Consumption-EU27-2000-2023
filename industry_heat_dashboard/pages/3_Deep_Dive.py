import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import load_data, get_filter_options

st.set_page_config(page_title="Deep Dive", layout="wide")

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
    .info-box { background: white; border: 1px solid #e8ecf0; border-left: 3px solid #c84b31; border-radius: 4px; padding: 0.8rem 1rem; font-size: 0.85rem; color: #3a4a5a; margin-bottom: 1rem; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

PALETTE = [
    "#0f4c81", "#c84b31", "#1a6b3c", "#f5c842", "#4a9fd4",
    "#e07b5a", "#4a9b6a", "#9b6b2a", "#7aafd4", "#f0a882", "#2a6fa8"
]

# --- Load data ---
df = load_data()
options = get_filter_options(df)

# --- Sidebar ---
st.sidebar.markdown("### 🔍 Deep Dive")
st.sidebar.markdown("---")

# Mode selector
mode = st.sidebar.radio(
    "Analysis mode",
    ["Single selection", "Compare countries", "Compare sectors"]
)

st.sidebar.markdown("---")

unit = st.sidebar.radio("Unit", ["TWh", "ktoe"])
value_col = "value_twh" if unit == "TWh" else "value_ktoe"

# --- Page header ---
st.markdown('<p class="section-label">Deep Dive Analysis</p>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Process-Level Energy Breakdown</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Drill down from sector to subsector to individual process and fuel type. Track evolution from 2000 to 2023.</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# MODE 1 — Single selection
# ============================================================
if mode == "Single selection":

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_country = st.selectbox("Country", options["countries"])
    with col_f2:
        selected_sector = st.selectbox("Sector", ["All sectors"] + options["sectors"])

    col_f3, col_f4 = st.columns(2)
    with col_f3:
        selected_subsector = st.selectbox("Subsector", ["All subsectors"] + options["subsectors"])
    with col_f4:
        selected_end_use = st.selectbox("End Use Type", ["All end use types"] + options["end_use_types"])

    selected_fuels = st.multiselect(
        "Fuels (leave empty for all)",
        options["fuels"],
        default=[]
    )

    year_range = st.slider(
        "Year range",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=(2000, 2023)
    )

    # --- Filter ---
    dff = df[
        (df["country"] == selected_country) &
        (df["year"] >= year_range[0]) &
        (df["year"] <= year_range[1])
    ].copy()

    if selected_sector != "All sectors":
        dff = dff[dff["sector"] == selected_sector]
    if selected_subsector != "All subsectors":
        dff = dff[dff["subsector"] == selected_subsector]
    if selected_end_use != "All end use types":
        dff = dff[dff["end_use_type"] == selected_end_use]
    if selected_fuels:
        dff = dff[dff["fuel"].isin(selected_fuels)]

    if dff.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    st.markdown("---")

    # --- Chart 1: Time series by process ---
    st.markdown('<p class="section-label">Energy consumption by process over time</p>', unsafe_allow_html=True)

    process_time = (
        dff.groupby(["year", "process"])[value_col]
        .sum()
        .reset_index()
    )

    fig_line = px.line(
        process_time,
        x="year",
        y=value_col,
        color="process",
        labels={value_col: unit, "year": "Year", "process": "Process"},
        color_discrete_sequence=PALETTE,
        markers=True
    )
    fig_line.update_traces(line=dict(width=2), marker=dict(size=4))
    fig_line.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=9)),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Chart 2: Process × Fuel breakdown for selected snapshot year ---
    col_left, col_right = st.columns(2)

    available_years = sorted(dff["year"].unique())
    latest = st.select_slider(
        "Snapshot year (for process & fuel breakdown)",
        options=available_years,
        value=year_range[1]
    )
    dff_latest = dff[dff["year"] == latest]

    with col_left:
        st.markdown(f'<p class="section-label">Process breakdown — {latest}</p>', unsafe_allow_html=True)

        proc_latest = (
            dff_latest.groupby("process")[value_col]
            .sum()
            .reset_index()
            .sort_values(value_col, ascending=True)
        )

        fig_proc = px.bar(
            proc_latest,
            x=value_col,
            y="process",
            orientation="h",
            labels={value_col: unit, "process": ""},
            color=value_col,
            color_continuous_scale=[[0, "#e8f0f7"], [1, "#0f4c81"]]
        )
        fig_proc.update_layout(
            paper_bgcolor="#f7f8fa",
            plot_bgcolor="white",
            height=380,
            margin=dict(l=0, r=20, t=10, b=0),
            font=dict(family="Inter", size=10, color="#0f1923"),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#e8ecf0", title=unit),
            yaxis=dict(gridcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_proc, use_container_width=True)

    with col_right:
        st.markdown(f'<p class="section-label">Fuel breakdown — {latest}</p>', unsafe_allow_html=True)

        fuel_latest = (
            dff_latest.groupby("fuel")[value_col]
            .sum()
            .reset_index()
            .sort_values(value_col, ascending=True)
        )

        fig_fuel = px.bar(
            fuel_latest,
            x=value_col,
            y="fuel",
            orientation="h",
            labels={value_col: unit, "fuel": ""},
            color=value_col,
            color_continuous_scale=[[0, "#fdf0ec"], [1, "#c84b31"]]
        )
        fig_fuel.update_layout(
            paper_bgcolor="#f7f8fa",
            plot_bgcolor="white",
            height=380,
            margin=dict(l=0, r=20, t=10, b=0),
            font=dict(family="Inter", size=10, color="#0f1923"),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#e8ecf0", title=unit),
            yaxis=dict(gridcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_fuel, use_container_width=True)

    # --- Chart 3: End use type breakdown ---
    st.markdown('<p class="section-label">End use type — how energy is delivered</p>', unsafe_allow_html=True)

    end_use_time = (
        dff.groupby(["year", "end_use_type"])[value_col]
        .sum()
        .reset_index()
    )

    fig_end = px.bar(
        end_use_time,
        x="year",
        y=value_col,
        color="end_use_type",
        labels={value_col: unit, "year": "Year", "end_use_type": "End Use Type"},
        color_discrete_sequence=PALETTE,
        barmode="stack"
    )
    fig_end.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=340,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=9)),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_end, use_container_width=True)


# ============================================================
# MODE 2 — Compare countries
# ============================================================
elif mode == "Compare countries":

    selected_countries = st.multiselect(
        "Select countries to compare",
        options["countries"],
        default=["Germany", "France", "Italy", "Spain", "Poland"]
    )

    selected_sector = st.selectbox("Sector", ["All sectors"] + options["sectors"])

    year_range = st.slider(
        "Year range",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=(2000, 2023)
    )

    if not selected_countries:
        st.info("Select at least one country to begin.")
        st.stop()

    dff = df[
        (df["country"].isin(selected_countries)) &
        (df["year"] >= year_range[0]) &
        (df["year"] <= year_range[1])
    ].copy()

    if selected_sector != "All sectors":
        dff = dff[dff["sector"] == selected_sector]

    st.markdown("---")

    # Time series comparison
    st.markdown('<p class="section-label">Energy consumption over time — country comparison</p>', unsafe_allow_html=True)

    country_time = (
        dff.groupby(["year", "country"])[value_col]
        .sum()
        .reset_index()
    )

    fig_comp = px.line(
        country_time,
        x="year",
        y=value_col,
        color="country",
        labels={value_col: unit, "year": "Year", "country": "Country"},
        color_discrete_sequence=PALETTE,
        markers=True
    )
    fig_comp.update_traces(line=dict(width=2.5), marker=dict(size=5))
    fig_comp.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Fuel mix comparison for selected snapshot year
    available_years = sorted(dff["year"].unique())
    latest = st.select_slider(
        "Snapshot year (for fuel mix comparison)",
        options=available_years,
        value=year_range[1]
    )
    st.markdown(f'<p class="section-label">Fuel mix comparison — {latest}</p>', unsafe_allow_html=True)

    fuel_comp = (
        dff[dff["year"] == latest]
        .groupby(["country", "fuel"])[value_col]
        .sum()
        .reset_index()
    )

    fig_fuel_comp = px.bar(
        fuel_comp,
        x="country",
        y=value_col,
        color="fuel",
        labels={value_col: unit, "country": "", "fuel": "Fuel"},
        color_discrete_sequence=PALETTE,
        barmode="stack"
    )
    fig_fuel_comp.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=380,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=9)),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_fuel_comp, use_container_width=True)


# ============================================================
# MODE 3 — Compare sectors
# ============================================================
elif mode == "Compare sectors":

    selected_country = st.selectbox("Country", ["All EU27"] + options["countries"])

    selected_sectors = st.multiselect(
        "Sectors to compare",
        options["sectors"],
        default=options["sectors"][:4]
    )

    year_range = st.slider(
        "Year range",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=(2000, 2023)
    )

    if not selected_sectors:
        st.info("Select at least one sector to begin.")
        st.stop()

    dff = df[
        (df["sector"].isin(selected_sectors)) &
        (df["year"] >= year_range[0]) &
        (df["year"] <= year_range[1])
    ].copy()

    if selected_country != "All EU27":
        dff = dff[dff["country"] == selected_country]

    st.markdown("---")

    # Time series by sector
    st.markdown('<p class="section-label">Sector comparison over time</p>', unsafe_allow_html=True)

    sector_time = (
        dff.groupby(["year", "sector"])[value_col]
        .sum()
        .reset_index()
    )

    fig_sec_comp = px.line(
        sector_time,
        x="year",
        y=value_col,
        color="sector",
        labels={value_col: unit, "year": "Year", "sector": "Sector"},
        color_discrete_sequence=PALETTE,
        markers=True
    )
    fig_sec_comp.update_traces(line=dict(width=2.5), marker=dict(size=5))
    fig_sec_comp.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_sec_comp, use_container_width=True)

    # Process breakdown per sector for selected snapshot year
    available_years = sorted(dff["year"].unique())
    latest = st.select_slider(
        "Snapshot year (for process breakdown per sector)",
        options=available_years,
        value=year_range[1]
    )
    st.markdown(f'<p class="section-label">Process breakdown per sector — {latest}</p>', unsafe_allow_html=True)

    proc_sec = (
        dff[dff["year"] == latest]
        .groupby(["sector", "process"])[value_col]
        .sum()
        .reset_index()
    )

    fig_proc_sec = px.bar(
        proc_sec,
        x="sector",
        y=value_col,
        color="process",
        labels={value_col: unit, "sector": "", "process": "Process"},
        color_discrete_sequence=PALETTE,
        barmode="stack"
    )
    fig_proc_sec.update_layout(
        paper_bgcolor="#f7f8fa",
        plot_bgcolor="white",
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter", size=11, color="#0f1923"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=9)),
        xaxis=dict(gridcolor="#e8ecf0", title="", tickangle=-20),
        yaxis=dict(gridcolor="#e8ecf0", title=unit)
    )
    st.plotly_chart(fig_proc_sec, use_container_width=True)
