# CBA Sizing Tool – Streamlit app (v0.3)
# ------------------------------------------------------
# This version implements the following updates:
#   • Interest rate on debt = user‑supplied Federal Funds Rate + fixed 2 % margin
#   • CBA base band tightened to 0.25 % – 0.75 %
#   • Total CAPEX input shows thousand‑separator formatting with no decimals
#   • Consistent terminology: EJ & Urban Density *Adders*
#   • Minor UI text tweaks

import streamlit as st
from pathlib import Path

# ------------------------------------------------------
# Page / UI config
# ------------------------------------------------------
st.set_page_config(
    page_title="CBA Sizer",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------
# Logo (optional) – place 'northwestern_logo.png' in repo root
# ------------------------------------------------------
logo_path = Path(__file__).parent / "northwestern_logo.png"
if logo_path.exists():
    st.image(str(logo_path), width=160)

st.title("Community Benefit Agreement (CBA) Sizing Tool")

# ------------------------------------------------------
# Two‑tab layout: Calculator | Recommendations
# ------------------------------------------------------
calc_tab, rec_tab = st.tabs(["Calculator", "Recommendations"])

# =============================================================================
# ▶  CALCULATOR TAB
# =============================================================================
with calc_tab:
    st.header("Project Financial Inputs")

    # ── CAPEX input mode ───────────────────────────────────────────────────────
    input_mode = st.radio(
        "CAPEX Input Mode",
        ["Estimate CAPEX from cost per kW", "Enter total CAPEX directly"],
    )

    if input_mode == "Estimate CAPEX from cost per kW":
        st.markdown(
            "[Cost benchmarks – NREL ATB](https://atb.nrel.gov/electricity/2024/utility-scale_battery_storage)",
            help="Opens the NREL Annual Technology Baseline for utility‑scale batteries.",
        )
        size_mw = st.number_input("Battery Size (MW)", 10, 1000, 500, 10)
        capex_kw = st.number_input("CAPEX $/kW", 500, 2000, 1100, 50)
        capex_total = size_mw * 1000 * capex_kw
    else:
        capex_total = st.number_input(
            "Total CAPEX ($)",
            min_value=1_000_000,
            max_value=2_000_000_000,
            value=670_000_000,
            step=1_000_000,
            format="%d",
        )
        size_mw = st.number_input("Battery Size (MW)", 10, 1000, 500, 10)
        capex_kw = capex_total / (size_mw * 1000)

    st.divider()
    st.subheader("Financing Assumptions")

    # Federal Funds Rate + fixed margin → Interest on Debt
    st.markdown("[Current Effective Federal Funds Rate](https://www.newyorkfed.org/markets/reference-rates/effr)")
    fed_rate = st.number_input("Enter current Federal Funds Rate (%)", 0.0, 15.0, 5.25, 0.01)

    margin = 2.0  # fixed margin over Fed rate
    interest_rate_pct = fed_rate + margin
    st.write(f"**Interest Rate on Debt:** {interest_rate_pct:.2f}% (Fed Rate + {margin:.0f} %)")

    target_irr = st.slider("Target Levered IRR (%)", 8.0, 20.0, 15.0, 0.5)

    leverage = 0.70  # fixed 70 % debt
    equity_share = 1 - leverage

    equity = capex_total * equity_share
    debt = capex_total * leverage

    annual_profit = (target_irr / 100) * equity + (interest_rate_pct / 100) * debt

    # ── Adders ────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Equity & Context Adders")

    ej_flag = st.checkbox(
        "Environmental‑Justice Adder (EJ)",
        value=True,
        help="Applies 1.5× multiplier to the CBA % for projects in EJ census tracts.",
    )
    urban_flag = st.checkbox(
        "Urban Density Adder",
        value=True,
        help="Applies 1.5× multiplier to the CBA % for projects in densely populated areas.",
    )

    base_low_pct, base_high_pct = 0.0025, 0.0075  # 0.25 % – 0.75 %
    pct_multiplier = 1.0
    if ej_flag:
        pct_multiplier *= 1.15
    if urban_flag:
        pct_multiplier *= 1.15

    cba_low_pct = base_low_pct * pct_multiplier
    cba_high_pct = base_high_pct * pct_multiplier

    annual_cba_low = annual_profit * cba_low_pct
    annual_cba_high = annual_profit * cba_high_pct

    project_life = 20  # fixed asset life
    lifetime_cba_low = annual_cba_low * project_life
    lifetime_cba_high = annual_cba_high * project_life

    # ── Results ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Results")

    col1, col2 = st.columns(2)
    col1.metric("Annual Profit", f"${annual_profit/1e6:,.2f} M")
    col2.metric("Debt : Equity", f"70 % : 30 %")

    col3, col4 = st.columns(2)
    col3.metric("CBA Range (Annual)", f"${annual_cba_low/1e6:,.2f} – ${annual_cba_high/1e6:,.2f} M")
    col4.metric("CBA Range (Lifetime 20 yrs)", f"${lifetime_cba_low/1e6:,.2f} – ${lifetime_cba_high/1e6:,.2f} M")

    st.info("The CBA values above represent **total contributions over the 20‑year asset life**.")

# =============================================================================
# ▶  RECOMMENDATIONS TAB
# =============================================================================
with rec_tab:
    st.header("How to Use This Tool & Key Definitions")

    st.markdown(
        """
        **Usage Steps**
        1. Choose *Estimate CAPEX* if you only know $ / kW, or switch to *Total CAPEX* if you already have a lump‑sum budget.
        2. Adjust financing assumptions: **Levered IRR** reflects investor expectations. For debt cost, enter the **current Federal Funds Rate**; the tool automatically adds a 2 % margin.
        3. Toggle the **EJ** and **Urban Density** adders if the project site qualifies; each one increases the share of profit allocated to the community.
        4. Use the *CBA Range (Lifetime)* to start negotiations with stakeholders.
        5. You can download results via browser screenshot or copy the numbers directly.

        **Adder Definitions**
        | Adder | Multiplier | Description |
        |-------|-----------:|-------------|
        | Environmental‑Justice (EJ) | 1.15 × | Census tracts with disproportionate environmental or socio‑economic burdens |
        | Urban Density | 1.15 × | Sites within densely populated areas where community impact is higher |
        """
    )
