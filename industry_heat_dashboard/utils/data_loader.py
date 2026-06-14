import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "eu27_industry_fec_2000_2023.parquet"

@st.cache_data
def load_data():
    """
    Load the EU27 industrial energy consumption dataset.
    Cached so it only reads from disk once per session.
    """
    df = pd.read_parquet(DATA_PATH)
    return df


def get_filter_options(df):
    """
    Return sorted unique values for each filterable dimension.
    """
    return {
        "countries":    sorted(df["country"].dropna().unique()),
        "sectors":      sorted(df["sector"].dropna().unique()),
        "subsectors":   sorted(df["subsector"].dropna().unique()),
        "processes":    sorted(df["process"].dropna().unique()),
        "end_use_types":sorted(df["end_use_type"].dropna().unique()),
        "fuels":        sorted(df["fuel"].dropna().unique()),
        "years":        sorted(df["year"].dropna().unique()),
    }
