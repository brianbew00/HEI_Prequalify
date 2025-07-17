
import streamlit as st
import locale

# Set locale to format currency
locale.setlocale(locale.LC_ALL, '')

st.set_page_config(page_title="HEA Premium Calculator")

st.title("HEA Premium Calculator")

st.markdown("Enter the values below to calculate the eligible HEA premium.")

# User inputs
home_value = st.number_input("Home Value ($)", min_value=0.0, value=500000.0, step=1000.0, format="%.2f")
loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, value=300000.0, step=1000.0, format="%.2f")
HEA_CLTV_Max = st.number_input("Max CLTV (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0, format="%.0f") / 100
HEA_PremPercent_Max = st.number_input("Max Premium % of Home Value", min_value=0.0, max_value=100.0, value=20.0, step=1.0, format="%.0f") / 100
HEA_Premium_Max = st.number_input("Max Premium ($)", min_value=0.0, value=500000.0, step=1000.0, format="%.2f")
HEA_Premium_Min = st.number_input("Min Premium ($)", min_value=0.0, value=30000.0, step=1000.0, format="%.2f")

# Calculation logic
def calculate_HEA_premium(home_value, loan_amount, HEA_CLTV_Max, HEA_PremPercent_Max, HEA_Premium_Max, HEA_Premium_Min):
    cltv_gap = max(0, (home_value * HEA_CLTV_Max) - loan_amount)
    max_prem_by_percent = home_value * HEA_PremPercent_Max
    lesser_of_gap_or_percent = min(max_prem_by_percent, cltv_gap)
    capped_at_max = min(lesser_of_gap_or_percent, HEA_Premium_Max)
    final_premium = 0 if capped_at_max < HEA_Premium_Min else capped_at_max
    return round(final_premium, 2)

# Trigger calculation
if st.button("Calculate Premium"):
    result = calculate_HEA_premium(
        home_value,
        loan_amount,
        HEA_CLTV_Max,
        HEA_PremPercent_Max,
        HEA_Premium_Max,
        HEA_Premium_Min
    )
    st.success(f"Calculated HEA Premium: ${result:,.2f}")
