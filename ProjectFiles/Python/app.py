"""
BrewNest Coffee Chain — Analytics Dashboard
Main Streamlit application with sidebar navigation across 9 functionalities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os

# Page config
st.set_page_config(
    page_title="BrewNest Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.5rem; }
h1 { color: #d4a76a; }
h2 { color: #c9956b; }
h3 { color: #b8860b; }
.stMetric label { font-size: 0.85rem !important; }
div[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #d4a76a !important; }
.stTabs [data-baseweb="tab"] { font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# Data Loading 
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_data():
    stores = pd.read_csv(os.path.join(DATA_DIR, "stores.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    sales = pd.read_csv(os.path.join(DATA_DIR, "sales.csv"))
    employees = pd.read_csv(os.path.join(DATA_DIR, "employees.csv"))
    sales["date"] = pd.to_datetime(sales["date"])
    stores["opening_date"] = pd.to_datetime(stores["opening_date"])
    customers["registration_date"] = pd.to_datetime(customers["registration_date"])
    employees["hire_date"] = pd.to_datetime(employees["hire_date"])
    return stores, products, customers, sales, employees

stores, products, customers, sales, employees = load_data()

# Import page modules 
from sections import (
    pg_dashboard,
    pg_cleaning,
    pg_encoding,
    pg_scaling,
    pg_statistics,
    pg_merging,
    pg_matplotlib,
    pg_sklearn,
    pg_statsmodels,
)

# Sidebar Navigation 
st.sidebar.image("https://img.icons8.com/emoji/96/hot-beverage.png", width=64)
st.sidebar.title("BrewNest Analytics")
st.sidebar.markdown("---")

PAGES = {
    "1. Dashboard Overview":        pg_dashboard,
    "2. Data Cleaning":             pg_cleaning,
    "3. Encoding Methods":          pg_encoding,
    "4. Scaling Methods":           pg_scaling,
    "5. Statistical Analysis":      pg_statistics,
    "6. Data Integration":          pg_merging,
    "7. Matplotlib Visualizations": pg_matplotlib,
    "8. Machine Learning":          pg_sklearn,
    "9. Regression Analysis":       pg_statsmodels,
}

page = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption("BrewNest Coffee Chain")
st.sidebar.caption("Activity & Expansion Analysis")

# Render selected page 
data = {
    "stores": stores,
    "products": products,
    "customers": customers,
    "sales": sales,
    "employees": employees,
}
PAGES[page].render(data)
