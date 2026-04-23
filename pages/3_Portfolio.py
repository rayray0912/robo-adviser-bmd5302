"""Recommended Portfolio Page — annualized display with 30% concentration cap."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.portfolio_engine import optimal_portfolio

MAX_WEIGHT = 0.30

st.title("💼 Your Recommended Portfolio")

# ---- Guard ----
if not st.session_state.get("questionnaire_done"):
    st.warning("⚠️ Please complete the Risk Assessment first.")
    st.page_link("pages/1_Risk_Assessment.py", label="👉 Go to Risk Assessment", icon="📝")
    st.stop()

A = st.session_state.A
tier = st.session_state.get("risk_tier", "")

# ---- Header ----
col_header_1, col_header_2 = st.columns([1, 2])
with col_header_1:
    st.metric("Your Risk Aversion (A)", f"{A:.2f}")
with col_header_2:
    st.markdown(f"### Risk Profile: {tier}")
    st.caption(f"Portfolio optimized to maximize $U = r - \\frac{{\\sigma^2 A}}{{2}}$ "
               f"with $A = {A:.2f}$, subject to a {int(MAX_WEIGHT*100)}% concentration cap.")

st.divider()

# ---- Load data ----
@st.cache_data
def load_data():
    fund_info = pd.read_csv("data/fund_info.csv")
    mu = pd.read_csv("data/mu.csv", index_col=0)["expected_return"].values
    sigma = pd.read_csv("data/sigma.csv", index_col=0).values
    return fund_info, mu, sigma

fund_info, mu_monthly, sigma_monthly = load_data()

# ---- Compute optimal portfolio ----
result = optimal_portfolio(mu_monthly, sigma_monthly, A,
                           allow_short=False, max_weight=MAX_WEIGHT)
weights = result["weights"]

# ---- Annualize metrics ----
ann_return = result["return"] * 12
ann_volatility = result["volatility"] * np.sqrt(12)
ann_sharpe = ann_return / ann_volatility if ann_volatility > 0 else 0
ann_utility = ann_return - 0.5 * A * ann_volatility ** 2

# ---- Key metrics ----
st.subheader("📊 Portfolio Metrics (Annualized)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Expected Return", f"{ann_return*100:.2f}%",
          help="Annualized expected return = monthly return × 12")
c2.metric("Volatility (σ)", f"{ann_volatility*100:.2f}%",
          help="Annualized standard deviation = monthly σ × √12")
c3.metric("Sharpe Ratio", f"{ann_sharpe:.2f}",
          help="Return / Volatility (assuming risk-free rate = 0)")
c4.metric("Utility U", f"{ann_utility:.4f}",
          help=f"U = r - σ²A/2, with A = {A:.2f}")

st.divider()

# ---- Asset allocation ----
st.subheader("🥧 Asset Allocation")

df = fund_info.copy()
df["weight"] = weights
df = df[df["weight"] > 0.001].sort_values("weight", ascending=False).reset_index(drop=True)

# 10 distinct colors, one per fund
FUND_COLORS = [
    "#1D3557",  # dark navy
    "#457B9D",  # teal blue
    "#2E86AB",  # medium blue
    "#A8DADC",  # light teal
    "#F4A261",  # orange
    "#E76F51",  # coral
    "#E9C46A",  # yellow
    "#8D99AE",  # grey blue
    "#6A994E",  # green
    "#BC4749",  # red
]

col_pie, col_table = st.columns([1, 1])

with col_pie:
    fig = px.pie(
        df, values="weight", names="name", hole=0.45,
        color="name",
        color_discrete_sequence=FUND_COLORS,
    )
    fig.update_traces(textposition="inside", textinfo="percent",
                      textfont=dict(size=12, color="white"))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5,
                    xanchor="left", x=1.02, font=dict(size=10)),
        margin=dict(t=10, b=10, l=10, r=10),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    display_df = df[["name", "asset_class", "region", "weight"]].copy()
    display_df["weight"] = (display_df["weight"] * 100).round(2).astype(str) + "%"
    display_df.columns = ["Fund", "Class", "Region", "Weight"]
    st.dataframe(display_df, use_container_width=True, hide_index=True,
                 height=400)

st.info(f"📌 **Concentration cap**: No single fund exceeds "
        f"{int(MAX_WEIGHT*100)}% to ensure diversification, "
        f"consistent with industry robo-advisor practice.")

st.divider()

# ---- Investment calculator ----
st.subheader("💰 Investment Calculator")

col_input, col_summary = st.columns([1, 2])
with col_input:
    capital = st.number_input(
        "Investment amount (SGD)",
        min_value=100, value=10000, step=500,
    )
    st.caption(f"Expected 1-year value: "
               f"**${capital * (1 + ann_return):,.0f}** "
               f"± ${capital * ann_volatility:,.0f}")

with col_summary:
    df["amount"] = (df["weight"] * capital).round(2)
    df_amt = df[["name", "asset_class", "weight", "amount"]].copy()
    df_amt["weight"] = (df_amt["weight"] * 100).round(2).astype(str) + "%"
    df_amt["amount"] = df_amt["amount"].apply(lambda x: f"${x:,.2f}")
    df_amt.columns = ["Fund", "Class", "Weight", "Amount"]
    st.dataframe(df_amt, use_container_width=True, hide_index=True)

st.divider()
st.caption("⚠️ *This is an academic project output. Not financial advice. "
          "Past performance does not guarantee future results.*")
