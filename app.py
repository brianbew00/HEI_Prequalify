import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="HEI Calculator", layout="wide")
st.title("🏡 Home Equity Investment (HEI) Calculator")

st.success("✅ The latest version of the app has been loaded.")

# --- Helper functions ---
def parse_currency(x):
    return float(x.replace('$', '').replace(',', '').strip())

def parse_percent(x):
    return float(x.replace('%', '').strip()) / 100

def parse_multiplier(x):
    return float(x.lower().replace('x', '').strip())

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📌 Input Parameters")
    home_value_str = st.text_input("Home Value", "$1,000,000")
    loan_amount_str = st.text_input("Current Loan Balance", "$300,000")
    max_cltv_str = st.text_input("Max CLTV", "75%")
    max_premium_percent_str = st.text_input("Max Premium % of Home Value", "20%")
    max_premium_dollar_str = st.text_input("Max Premium ($)", "$500,000")
    min_premium_dollar_str = st.text_input("Min Premium ($)", "$30,000")
    appreciation_rate_str = st.text_input("Annual Appreciation", "2.00%")
    hei_multiplier_str = st.text_input("HEI Multiplier", "2.0x")
    investor_cap_str = st.text_input("Investor Cap", "20.00%")

# --- Parse and Validate Inputs ---
try:
    home_value = parse_currency(home_value_str)
    loan_amount = parse_currency(loan_amount_str)
    max_cltv = parse_percent(max_cltv_str)
    max_premium_pct = parse_percent(max_premium_percent_str)
    max_premium_dollar = parse_currency(max_premium_dollar_str)
    min_premium_dollar = parse_currency(min_premium_dollar_str)
    appreciation_rate = parse_percent(appreciation_rate_str)
    hei_multiplier = parse_multiplier(hei_multiplier_str)
    investor_cap_rate = parse_percent(investor_cap_str)
except ValueError:
    st.error("⚠️ Please verify your input formats.")
    st.stop()

# --- Premium Calculation Logic ---
cltv_gap = max(0, (home_value * max_cltv) - loan_amount)
max_premium_by_pct = home_value * max_premium_pct
raw_premium = min(max_premium_by_pct, cltv_gap)
capped_premium = min(raw_premium, max_premium_dollar)
final_premium = 0 if capped_premium < min_premium_dollar else capped_premium
premium_percentage_used = final_premium / home_value if home_value else 0
investor_percentage = premium_percentage_used * hei_multiplier

# --- Future Value Projections ---
years = list(range(11))
home_values, hei_caps, contract_values, settlement_values = [], [], [], []

current_home_value = home_value
current_hei_cap = final_premium

for year in years:
    if year != 0:
        current_home_value *= (1 + appreciation_rate)
        current_hei_cap *= (1 + investor_cap_rate)

    contract_value = current_home_value * investor_percentage
    settlement_value = min(current_hei_cap, contract_value)

    home_values.append(current_home_value)
    hei_caps.append(current_hei_cap)
    contract_values.append(contract_value)
    settlement_values.append(settlement_value)

# --- Results DataFrame ---
df_results = pd.DataFrame({
    "Year": years,
    "Home Value": home_values,
    "HEI Cap": hei_caps,
    "Contract Value": contract_values,
    "Settlement Value": settlement_values
}).set_index("Year")

# --- Highlight Conditional Formatting ---
def highlight_min(row):
    highlight = [""] * len(row)
    if row["HEI Cap"] < row["Contract Value"]:
        highlight[1] = "background-color: #90ee90"
    elif row["Contract Value"] < row["HEI Cap"]:
        highlight[2] = "background-color: #90ee90"
    return highlight

styled_df = df_results.style.format("${:,.0f}") \
    .apply(highlight_min, axis=1) \
    .set_table_styles([
        {'selector': 'th, td', 'props': [('padding', '4px'), ('text-align', 'center')]},
        {'selector': 'th.col_heading', 'props': [('width', '22%')]},
        {'selector': 'th.row_heading', 'props': [('width', '12%')]}
    ])

# --- Display Metrics ---
col1, col2 = st.columns(2)
col1.metric("🏷️ Final Premium Amount", f"${final_premium:,.0f}")
col2.metric("📈 Investor Percentage", f"{investor_percentage:.2%}")

# --- Plotly Chart ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=home_values, name="Home Value"))
fig.add_trace(go.Scatter(x=years, y=hei_caps, name="HEI Cap"))
fig.add_trace(go.Scatter(x=years, y=contract_values, name="Contract Value"))
fig.add_trace(go.Scatter(x=years, y=settlement_values, name="Settlement Value", fill='tozeroy'))

fig.update_layout(
    title='HEI Values Over 10 Years',
    xaxis_title='Year',
    yaxis_title='Value ($)',
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# --- Display Table ---
st.subheader("📊 Annual HEI Breakdown")
row_height_px = 35
table_height = (len(df_results) + 1) * row_height_px + 10

st.dataframe(
    styled_df,
    use_container_width=True,
    height=table_height
)
