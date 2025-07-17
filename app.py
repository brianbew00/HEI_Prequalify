
import streamlit as st
import pandas as pd

# Constants (editable defaults)
DEFAULTS = {
    "home_value": 500000.0,
    "loan_amount": 300000.0,
    "HEA_CLTV": 75.0,
    "HEA_PremPercent": 20.0,
    "HEA_Premium_Max": 500000.0,
    "HEA_Premium_Min": 30000.0
}

# Calculation function
def calculate_HEA_premium(home_value, loan_amount, HEA_CLTV, HEA_PremPercent, HEA_Premium_Max, HEA_Premium_Min):
    cltv_gap = max(0, (home_value * (HEA_CLTV / 100)) - loan_amount)
    max_prem_by_percent = home_value * (HEA_PremPercent / 100)
    lesser_of_gap_or_percent = min(max_prem_by_percent, cltv_gap)
    capped_at_max = min(lesser_of_gap_or_percent, HEA_Premium_Max)
    final_premium = 0 if capped_at_max < HEA_Premium_Min else capped_at_max
    return round(final_premium, 2)

# Page settings
st.set_page_config(page_title="HEA Premium Explorer", layout="wide")

st.title("🏠 HEA Premium Explorer")
st.markdown("Use the inputs to explore how premium eligibility is affected by different home and loan values.")

# Layout: Inputs (col1), Outputs/Charts (col2)
col1, col2 = st.columns([1, 2])

with col1:
    home_value = st.number_input("Home Value ($)", format="%.2f", value=DEFAULTS["home_value"], step=1000.00)
    loan_amount = st.number_input("Loan Amount ($)", format="%.2f", value=DEFAULTS["loan_amount"], step=1000.00)
    HEA_CLTV = st.number_input("Max CLTV (%)", format="%.0f", value=DEFAULTS["HEA_CLTV"], step=1.0)
    HEA_PremPercent = st.number_input("Max Premium % of Home Value", format="%.0f", value=DEFAULTS["HEA_PremPercent"], step=1.0)
    HEA_Premium_Max = st.number_input("Max Premium ($)", format="%.2f", value=DEFAULTS["HEA_Premium_Max"], step=1000.00)
    HEA_Premium_Min = st.number_input("Min Premium ($)", format="%.2f", value=DEFAULTS["HEA_Premium_Min"], step=1000.00)

    calculate = st.button("💰 Calculate Premium")

if calculate:
    premium = calculate_HEA_premium(
        home_value, loan_amount, HEA_CLTV, HEA_PremPercent, HEA_Premium_Max, HEA_Premium_Min
    )

    # Simulated chart data: premium over range of home values
    home_values = list(range(int(home_value * 0.8), int(home_value * 1.21), 10000))
    premium_series = [
        calculate_HEA_premium(hv, loan_amount, HEA_CLTV, HEA_PremPercent, HEA_Premium_Max, HEA_Premium_Min)
        for hv in home_values
    ]
    df_chart = pd.DataFrame({
        "Home Value ($)": home_values,
        "Premium ($)": premium_series
    })

    with col2:
        st.subheader("📈 Premium vs Home Value")
        st.line_chart(df_chart.rename(columns={"Home Value ($)": "index"}).set_index("index"))

        st.subheader("💡 Results")
        st.metric("Calculated HEA Premium", f"${premium:,.2f}")
