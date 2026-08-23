import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="KoinX - Tax Loss Harvesting", layout="wide")

# Mock Initial Data
BASE_CAPITAL_GAINS = {
    "stcg_profits": 70200.88,
    "stcg_losses": 1548.53,
    "ltcg_profits": 5020.00,
    "ltcg_losses": 3050.00,
}

HOLDINGS_DATA = [
    {
        "coin": "USDC",
        "coinName": "USDC",
        "currentPrice": 85.41,
        "totalHolding": 0.001534,
        "averageBuyPrice": 1.586,
        "stcg_gain": 0.128,
        "ltcg_gain": 0.0,
    },
    {
        "coin": "WETH",
        "coinName": "Polygon PoS Bridged WETH",
        "currentPrice": 211756.0,
        "totalHolding": 0.000240,
        "averageBuyPrice": 3599.85,
        "stcg_gain": 49.95,
        "ltcg_gain": 0.0,
    },
    {
        "coin": "WPOL",
        "coinName": "Wrapped POL",
        "currentPrice": 22.08,
        "totalHolding": 2.317,
        "averageBuyPrice": 0.522,
        "stcg_gain": 49.95,
        "ltcg_gain": 20.0,
    },
    {
        "coin": "EZ",
        "coinName": "EasyFi V2",
        "currentPrice": 0.885,
        "totalHolding": 0.000542,
        "averageBuyPrice": 6.539,
        "stcg_gain": -0.003,
        "ltcg_gain": 0.0,
    },
    {
        "coin": "SPHERE",
        "coinName": "Sphere Finance",
        "currentPrice": 0.007,
        "totalHolding": 0.0000001,
        "averageBuyPrice": 0.011,
        "stcg_gain": -0.0008,
        "ltcg_gain": 0.0,
    },
]

st.title("Tax Loss Harvesting Dashboard")

# Convert holdings to DataFrame
df = pd.DataFrame(HOLDINGS_DATA)
df["Select"] = False  # Add selection column

# Layout: Capital Gains Summary Cards
col1, col2 = st.columns(2)

# Calculate Pre-Harvesting Values
pre_net_stcg = BASE_CAPITAL_GAINS["stcg_profits"] - BASE_CAPITAL_GAINS["stcg_losses"]
pre_net_ltcg = BASE_CAPITAL_GAINS["ltcg_profits"] - BASE_CAPITAL_GAINS["ltcg_losses"]
pre_realised = pre_net_stcg + pre_net_ltcg

with col1:
    st.subheader("Pre-Harvesting Gains")
    st.metric("Realised Capital Gains", f"₹{pre_realised:,.2f}")
    st.write(f"**Short-Term Gains:** ₹{pre_net_stcg:,.2f} (Profits: +₹{BASE_CAPITAL_GAINS['stcg_profits']:,.2f} | Losses: -₹{BASE_CAPITAL_GAINS['stcg_losses']:,.2f})")
    st.write(f"**Long-Term Gains:** ₹{pre_net_ltcg:,.2f} (Profits: +₹{BASE_CAPITAL_GAINS['ltcg_profits']:,.2f} | Losses: -₹{BASE_CAPITAL_GAINS['ltcg_losses']:,.2f})")

# Interactive Holdings Table
st.subheader("Select Holdings to Harvest")
edited_df = st.data_editor(
    df,
    column_config={
        "Select": st.column_config.CheckboxColumn("Harvest?", default=False),
        "currentPrice": st.column_config.NumberColumn("Current Price (₹)", format="₹%.2f"),
        "stcg_gain": st.column_config.NumberColumn("STCG Gain (₹)", format="₹%.2f"),
        "ltcg_gain": st.column_config.NumberColumn("LTCG Gain (₹)", format="₹%.2f"),
    },
    disabled=["coin", "coinName", "currentPrice", "totalHolding", "averageBuyPrice", "stcg_gain", "ltcg_gain"],
    hide_index=True,
)

# Calculate Post-Harvesting Logic
selected_rows = edited_df[edited_df["Select"]]

post_stcg_profits = BASE_CAPITAL_GAINS["stcg_profits"] + selected_rows[selected_rows["stcg_gain"] > 0]["stcg_gain"].sum()
post_stcg_losses = BASE_CAPITAL_GAINS["stcg_losses"] + abs(selected_rows[selected_rows["stcg_gain"] < 0]["stcg_gain"].sum())

post_ltcg_profits = BASE_CAPITAL_GAINS["ltcg_profits"] + selected_rows[selected_rows["ltcg_gain"] > 0]["ltcg_gain"].sum()
post_ltcg_losses = BASE_CAPITAL_GAINS["ltcg_losses"] + abs(selected_rows[selected_rows["ltcg_gain"] < 0]["ltcg_gain"].sum())

post_net_stcg = post_stcg_profits - post_stcg_losses
post_net_ltcg = post_ltcg_profits - post_ltcg_losses
post_realised = post_net_stcg + post_net_ltcg

with col2:
    st.subheader("After Harvesting Gains")
    st.metric("Realised Capital Gains", f"₹{post_realised:,.2f}", delta=f"{post_realised - pre_realised:,.2f}", delta_color="inverse")
    st.write(f"**Short-Term Gains:** ₹{post_net_stcg:,.2f} (Profits: +₹{post_stcg_profits:,.2f} | Losses: -₹{post_stcg_losses:,.2f})")
    st.write(f"**Long-Term Gains:** ₹{post_net_ltcg:,.2f} (Profits: +₹{post_ltcg_profits:,.2f} | Losses: -₹{post_ltcg_losses:,.2f})")

    # Savings Alert Banner
    if pre_realised > post_realised:
        st.success(f"🎉 You're going to save ₹{(pre_realised - post_realised):,.2f} in taxable gains!")
