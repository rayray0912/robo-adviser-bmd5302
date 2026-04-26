"""Recommended Portfolio Page — annualized display with 30% concentration cap."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from core.portfolio_engine import optimal_portfolio

MAX_WEIGHT = 1.0  # No cap (aligned with teammate's Excel implementation)

st.title("Your Recommended Portfolio")

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
    st.metric("Your Risk Aversion (A)", f"{A}")
with col_header_2:
    st.markdown(f"### Risk Profile: {tier}")
    st.caption(f"Portfolio optimized to maximize $U = r - \\frac{{\\sigma^2 A}}{{2}}$ "
               f"with $A = {A}$, subject to a {int(MAX_WEIGHT*100)}% concentration cap.")

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
st.subheader("Portfolio Metrics (Annualized)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Expected Return", f"{ann_return*100:.2f}%",
          help="Annualized expected return = monthly return × 12")
c2.metric("Volatility (σ)", f"{ann_volatility*100:.2f}%",
          help="Annualized standard deviation = monthly σ × √12")
c3.metric("Sharpe Ratio", f"{ann_sharpe:.2f}",
          help="Return / Volatility (assuming risk-free rate = 0)")
c4.metric("Utility U", f"{ann_utility:.4f}",
          help=f"U = r - σ²A/2, with A = {A}")

st.divider()

# ---- Asset allocation ----
st.subheader("Asset Allocation")

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

st.divider()

# ---- Investment calculator ----
st.subheader("Investment Calculator")

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

# ============================================================================
# Historical Performance Section
# Append this block to the END of pages/3_Portfolio.py
# ============================================================================

st.divider()
st.subheader("Historical Performance")
st.caption("Based on 61 months of actual price data (Apr 2021 – Apr 2026). "
           "All portfolios start at $10,000 under a buy-and-hold strategy.")

# ---- Load price data (add to existing load_data if preferred, or standalone) ----
@st.cache_data
def load_prices():
    prices = pd.read_csv("data/prices.csv", index_col=0)
    return prices

prices = load_prices()

# Generate human-readable month labels (Apr 2021 → Apr 2026)
# Month 0 = April 2021
month_labels = pd.date_range(start="2021-04-01", periods=len(prices), freq="MS")
month_str = month_labels.strftime("%b %Y")

# ---- Chart 1: 10 funds normalized price trends ----
st.markdown("**Individual Fund Performance (Normalized to 100)**")

normalized_prices = prices / prices.iloc[0] * 100

fig_trends = go.Figure()
for i, col in enumerate(normalized_prices.columns):
    fund_name = fund_info["name"].iloc[i]
    fig_trends.add_trace(go.Scatter(
        x=month_labels,
        y=normalized_prices[col],
        mode="lines",
        name=fund_name,
        line=dict(color=FUND_COLORS[i], width=2),
        hovertemplate=f"<b>{fund_name}</b><br>"
                      "%{x|%b %Y}<br>"
                      "Value: %{y:.2f}<extra></extra>",
    ))

# Add a horizontal reference line at 100
fig_trends.add_hline(y=100, line=dict(color="gray", width=1, dash="dash"),
                     annotation_text="Start", annotation_position="right")

fig_trends.update_layout(
    height=450,
    xaxis=dict(title="Date", showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(title="Normalized Price (Start = 100)",
               showgrid=True, gridcolor="#f0f0f0"),
    hovermode="x unified",
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
                font=dict(size=10)),
    margin=dict(t=20, b=40, l=60, r=180),
    plot_bgcolor="white",
)

st.plotly_chart(fig_trends, use_container_width=True)

# Summary of best/worst performers
ending_values = normalized_prices.iloc[-1]
best_idx = ending_values.idxmax()
worst_idx = ending_values.idxmin()
best_name = fund_info["name"].iloc[list(prices.columns).index(best_idx)]
worst_name = fund_info["name"].iloc[list(prices.columns).index(worst_idx)]

col_insight_1, col_insight_2, col_insight_3 = st.columns(3)
col_insight_1.metric("Best performer", best_name,
                     f"+{ending_values.max() - 100:.1f}%")
col_insight_2.metric("Worst performer", worst_name,
                     f"{ending_values.min() - 100:.1f}%")
col_insight_3.metric("Performance spread",
                     f"{ending_values.max() - ending_values.min():.1f} pts",
                     help="Difference between best and worst")

st.divider()

# ---- Chart 2: User portfolio backtest vs equal-weight benchmark ----
st.markdown("**Your Portfolio vs. Equal-Weight Benchmark (Buy & Hold)**")

INITIAL_CAPITAL = 10_000

# User portfolio value over time (buy and hold)
user_shares = INITIAL_CAPITAL * weights / prices.iloc[0].values
user_values = (prices.values * user_shares).sum(axis=1)
user_series = pd.Series(user_values, index=month_labels)

# Equal-weight benchmark
eq_weights = np.ones(len(weights)) / len(weights)
eq_shares = INITIAL_CAPITAL * eq_weights / prices.iloc[0].values
eq_values = (prices.values * eq_shares).sum(axis=1)
eq_series = pd.Series(eq_values, index=month_labels)

fig_backtest = go.Figure()

fig_backtest.add_trace(go.Scatter(
    x=month_labels, y=user_series.values,
    mode="lines", name=f"Your Portfolio (A={A})",
    line=dict(color="#1D3557", width=3),
    hovertemplate="<b>Your Portfolio</b><br>"
                  "%{x|%b %Y}<br>"
                  "Value: $%{y:,.0f}<extra></extra>",
))

fig_backtest.add_trace(go.Scatter(
    x=month_labels, y=eq_series.values,
    mode="lines", name="Equal-Weight Benchmark",
    line=dict(color="#E76F51", width=2, dash="dash"),
    hovertemplate="<b>Equal-Weight Benchmark</b><br>"
                  "%{x|%b %Y}<br>"
                  "Value: $%{y:,.0f}<extra></extra>",
))

# Horizontal reference line at initial capital
fig_backtest.add_hline(y=INITIAL_CAPITAL,
                       line=dict(color="gray", width=1, dash="dot"),
                       annotation_text=f"${INITIAL_CAPITAL:,}",
                       annotation_position="right")

fig_backtest.update_layout(
    height=420,
    xaxis=dict(title="Date", showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(title="Portfolio Value (SGD)",
               showgrid=True, gridcolor="#f0f0f0",
               tickprefix="$", tickformat=","),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.15,
                xanchor="center", x=0.5),
    margin=dict(t=20, b=80, l=80, r=40),
    plot_bgcolor="white",
)

st.plotly_chart(fig_backtest, use_container_width=True)

# Performance summary metrics
user_total_return = (user_series.iloc[-1] / INITIAL_CAPITAL - 1) * 100
eq_total_return = (eq_series.iloc[-1] / INITIAL_CAPITAL - 1) * 100

# Max drawdown for user portfolio
running_max = user_series.cummax()
drawdown = (user_series - running_max) / running_max
user_max_dd = drawdown.min() * 100

# Same for benchmark
eq_running_max = eq_series.cummax()
eq_drawdown = (eq_series - eq_running_max) / eq_running_max
eq_max_dd = eq_drawdown.min() * 100

col_bt_1, col_bt_2, col_bt_3, col_bt_4 = st.columns(4)

col_bt_1.metric(
    "Your Ending Value",
    f"${user_series.iloc[-1]:,.0f}",
    f"{user_total_return:+.2f}%",
)
col_bt_2.metric(
    "Benchmark Ending Value",
    f"${eq_series.iloc[-1]:,.0f}",
    f"{eq_total_return:+.2f}%",
)
col_bt_3.metric(
    "Outperformance",
    f"{user_total_return - eq_total_return:+.2f} pts",
    help="Difference in total return vs. equal-weight benchmark",
)
col_bt_4.metric(
    "Your Max Drawdown",
    f"{user_max_dd:.2f}%",
    f"vs. {eq_max_dd:.2f}% benchmark",
    delta_color="inverse",
    help="Largest peak-to-trough decline over the period",
)

st.caption(
    "**Note**: Past performance is historical simulation using actual FSMOne "
    "fund prices. Buy-and-hold assumes no transaction costs or rebalancing. "
    "Results do not predict future performance."
)