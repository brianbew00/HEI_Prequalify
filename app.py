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

# --- Constants ---
default_values = {
    "max_cltv": 0.75,
    "max_premium_pct": 0.20,
    "max_premium_dollar": 500000.0,
    "min_premium_dollar": 30000.0,
    "hei_multiplier": 2.0,
    "investor_cap_rate": 0.20,
}

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📌 Input Parameters")

    # Editable inputs
    home_value_str = st.text_input("Home Value", "$1,000,000")
    loan_amount_str = st.text_input("Current Loan Balance", "$300,000")
    appreciation_rate_str = st.text_input("Annual Appreciation", "2.00%")

    # Premium paid with optional override
    premium_override_str = st.text_input("Premium Paid to Homeowner (Defaults to Max Available)", "")

    # Display-only fields with corrected formatting
    st.markdown("### 🔒 System Settings (Read-only)")
    st.markdown(f"**Investor Cap:** {default_values['investor_cap_rate']:.0%}")
    st.markdown(f"**Max Premium % of Home Value:** {default_values['max_premium_pct']:.0%}")
    st.markdown(f"**Max CLTV:** {default_values['max_cltv']:.0%}")
    st.markdown(f"**HEI Multiplier:** {default_values['hei_multiplier']:.1f}x")
    st.markdown(f"**Max Premium ($):** ${default_values['max_premium_dollar']:,.0f}")
    st.markdown(f"**Min Premium ($):** ${default_values['min_premium_dollar']:,.0f}")

# --- Parse and Validate Inputs ---
try:
    home_value = parse_currency(home_value_str)
    loan_amount = parse_currency(loan_amount_str)
    appreciation_rate = parse_percent(appreciation_rate_str)
    premium_override = parse_currency(premium_override_str) if premium_override_str else None
except ValueError:
    st.error("⚠️ Please verify your input formats.")
    st.stop()

# --- Premium Calculation Logic ---
cltv_gap = max(0, (home_value * default_values["max_cltv"]) - loan_amount)
max_premium_by_pct = home_value * default_values["max_premium_pct"]
raw_premium = min(max_premium_by_pct, cltv_gap)
capped_premium = min(raw_premium, default_values["max_premium_dollar"])
calculated_premium = 0 if capped_premium < default_values["min_premium_dollar"] else capped_premium

# --- Apply Override if Valid ---
if premium_override is not None:
    if premium_override < default_values["min_premium_dollar"]:
        st.warning(f"⚠️ Premium override is below the minimum of ${default_values['min_premium_dollar']:,.0f}. Using default.")
        final_premium = calculated_premium
    elif premium_override > calculated_premium:
        st.warning(f"⚠️ Premium override exceeds max available (${calculated_premium:,.0f}). Using default.")
        final_premium = calculated_premium
    else:
        final_premium = premium_override
else:
    final_premium = calculated_premium

premium_percentage_used = final_premium / home_value if home_value else 0
investor_percentage = premium_percentage_used * default_values["hei_multiplier"]

# --- Future Value Projections ---
years = list(range(11))
home_values, hei_caps, contract_values, settlement_values = [], [], [], []

current_home_value = home_value
current_hei_cap = final_premium

for year in years:
    if year != 0:
        current_home_value *= (1 + appreciation_rate)
        current_hei_cap *= (1 + default_values["investor_cap_rate"])

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
