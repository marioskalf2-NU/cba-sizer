# Streamlit app for Community Benefit Agreement (CBA) Calculator

import streamlit as st

# --- App Title ---
st.set_page_config(page_title="CBA Sizing Tool", layout="centered")
st.title("Community Benefit Agreement (CBA) Sizing Tool")

# --- Sidebar Inputs ---
st.sidebar.header("Project Inputs")
project_size_mw = st.sidebar.number_input("Battery Size (MW)", min_value=10, max_value=1000, value=500, step=10)
capex_per_kw = st.sidebar.number_input("CAPEX ($/kW)", min_value=500, max_value=2000, value=1340, step=10)
target_irr = st.sidebar.slider("Target Levered IRR (%)", min_value=8.0, max_value=20.0, value=15.0, step=0.5)
interest_rate = st.sidebar.slider("Interest Rate (%)", min_value=2.0, max_value=10.0, value=5.0, step=0.5)

# --- EJ and Urban Flags ---
st.sidebar.header("Equity Filters")
ej_zone = st.sidebar.checkbox("Environmental Justice Zone", value=True)
urban_area = st.sidebar.checkbox("Urban Density", value=True)

# --- Assumptions ---
project_life_years = 20
capex_total = project_size_mw * 1000 * capex_per_kw  # Total CAPEX in $
base_annual_profit = capex_total * (target_irr / 100)  # Simplified annual profit estimation

# --- Adjustors ---
adjustor = 1.0
if ej_zone:
    adjustor *= 1.15
if urban_area:
    adjustor *= 1.10

# --- CBA Range (Low to High % of Profit) ---
cba_pct_low = 0.0025
cba_pct_high = 0.03
cba_low = base_annual_profit * cba_pct_low * adjustor
cba_high = base_annual_profit * cba_pct_high * adjustor

# --- Main Output ---
st.subheader("Illustrative Annual Outputs")
st.metric("Estimated Annual Profit", f"${base_annual_profit/1e6:,.2f}M")
st.metric("CBA Range", f"${cba_low/1e3:,.0f}K – ${cba_high/1e3:,.0f}K")

# --- Notes ---
st.markdown("---")
st.markdown("**How It Works:**")
st.markdown("""
- This tool helps estimate a fair Community Benefit Agreement size based on project economics.
- Inputs include the project's MW size, capital cost per kW, investor return targets, and interest rate.
- We apply Environmental Justice and Urban Density adjustors to increase the CBA if equity concerns apply.
- The tool estimates a range (0.25%–3%) of annual profit that could reasonably be allocated to the CBA.
- Numbers shown are illustrative and meant to support stakeholder negotiations.
""")
