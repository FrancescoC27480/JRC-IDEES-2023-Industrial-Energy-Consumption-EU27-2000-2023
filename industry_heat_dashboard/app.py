import streamlit as st

st.set_page_config(
    page_title="EU27 Industrial Energy consumption",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global styles ---
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    /* Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1923;
        border-right: 1px solid #1e2d3d;
    }
    [data-testid="stSidebar"] * {
        color: #c9d4e0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiselect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #7a9bbf !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Main background */
    .main {
        background-color: #f7f8fa;
    }

    /* Page title style */
    .page-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.2rem;
        color: #0f1923;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #5a6a7a;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #e8ecf0;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #7a8a9a;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0f1923;
        line-height: 1;
    }
    .metric-unit {
        font-size: 0.8rem;
        color: #7a8a9a;
        margin-left: 0.3rem;
    }

    /* Section divider */
    .section-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #c84b31;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Landing page content ---
st.markdown('<h1 class="page-title">EU27 Industrial Energy Consumption</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Process-level final energy consumption across 27 Member States, 11 industrial sectors, and 24 years (2000–2023). Source: JRC-IDEES 2023.</p>', unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Coverage</div>
        <div class="metric-value">27<span class="metric-unit">Member States</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Industrial Sectors</div>
        <div class="metric-value">11<span class="metric-unit">sectors</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Time Series</div>
        <div class="metric-value">24<span class="metric-unit">years (2000–2023)</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
### How to use this dashboard

Use the **sidebar** to navigate between the three sections:

- ** European Overview** — Choropleth map of energy consumption across EU27. Filter by sector, subsector and year to see how industrial heat demand is distributed geographically.

- ** Country Profile** — Select a country and explore its full industrial energy breakdown — by sector, fuel mix, and how it sits relative to the EU27 average.

- ** Deep Dive** — The most granular view. Compare countries, sectors, subsectors and processes. Track how consumption evolved from 2000 to 2023.

---

**Data source:** JRC-IDEES 2023 — Joint Research Centre Integrated Database of the European Energy System  
**Unit:** Final energy consumption in TWh (converted from ktoe; 1 ktoe = 0.01163 TWh)  
""")
