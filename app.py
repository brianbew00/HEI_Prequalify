
import streamlit as st
import locale

# Set locale to format currency
locale.setlocale(locale.LC_ALL, '')

# Constants (global defaults)
HEA_CLTV_Max = 0.75
HEA_PremPercent_Max = 0.20
HEA_Premium_Max = 500000
HEA_Premium_Min = 30000

def calculate_HEA_premium(home_value, loan_amount):
    cltv_gap = max(0, (home_value * HEA_CLTV_Max) - loan_amount)
    max_prem_by_percent = home_value * HEA_PremPercent_Max
    lesser_of_gap_or_percent = min(max_prem_by_percent, cltv_gap)
    capped_at_max = min(lesser_of_gap_or_percent, HEA_Premium_Max)
    final_premium = 0 if capped_at_max < HEA_Premium_Min else capped_at_max
    return round(final_premium, 2)

st.set_page_config(page_title="HEA Premium Calculator")

st.title("HEA Premium Calculator")

st.markdown("Enter the values below to calculate the eligible HEA premium based on global settings:")

st.markdown(f"**Defaults:** Max CLTV = {int(HEA_CLTV_Max * 100)}%, Max Premium % = {int(HEA_PremPercent_Max * 100)}%, Max Premium = ${HEA_Premium_Max:,.0f}, Min Premium = ${HEA_Premium_Min:,.0f}")

home_value = st.number_input("Home Value ($)", min_value=0.0, step=1000.0, format="%.2f")
loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, step=1000.0, format="%.2f")

if st.button("Calculate Premium"):
    result = calculate_HEA_premium(home_value, loan_amount)
    st.success(f"Calculated HEA Premium: ${result:,.2f}")
