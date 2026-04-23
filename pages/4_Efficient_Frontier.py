"""Efficient Frontier — proper efficient set (upper half only)."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.portfolio_engine import (
    efficient_frontier, gmvp_unconstrained, gmvp_no_short, optimal_portfolio
)

MAX_WEIGHT = 1.0

st.title("📈 Efficient Frontier")
st.caption("Modern Portfolio Theory visualization — see how your portfolio compares.")

# ---- Load data ----
@st.cache_data
def load_data():
    fund_info = pd.read_csv("data/fund_info.csv")
    mu = pd.read_csv("data/mu.csv", index_col=0)["expected_return"].values
    sigma = pd.read_csv("data/sigma.csv", index_col=0).values
    return fund_info, mu, sigma

fund_info, mu_monthly, sigma_monthly = load_data()

# ---- Controls ----
display_mode = st.radio(
    "Display units",
    ["Annualized", "Monthly"],
    horizontal=True,
    help="All underlying data is monthly; annualized = ×12 for return, ×√12 for σ",
)

if display_mode == "Annualized":
    ret_scale = 12
    vol_scale = np.sqrt(12)
    unit_label = "Annualized"
else:
    ret_scale = 1
    vol_scale = 1
    unit_label = "Monthly"


# ---- Helper: filter the "efficient" upper-half only ----
def filter_efficient(frontier_pts, gmvp_return):
    """Keep only points on the upper half of the minimum-variance frontier.
    A point (σ, μ, w) is efficient iff μ >= GMVP return."""
    return [p for p in frontier_pts if p[1] >= gmvp_return - 1e-6]


# ---- Compute all frontiers (cached) ----
@st.cache_data
def compute_all(max_w, n_points=80):
    f_short_raw = efficient_frontier(mu_monthly, sigma_monthly, n_points, allow_short=True)
    f_ns_raw = efficient_frontier(mu_monthly, sigma_monthly, n_points,
                                   allow_short=False, max_weight=1.0)
    f_cap_raw = efficient_frontier(mu_monthly, sigma_monthly, n_points,
                                    allow_short=False, max_weight=max_w)

    w_gmvp_s = gmvp_unconstrained(sigma_monthly)
    w_gmvp_ns = gmvp_no_short(sigma_monthly, max_weight=1.0)
    w_gmvp_cap = gmvp_no_short(sigma_monthly, max_weight=max_w)

    gmvp_s_ret = w_gmvp_s @ mu_monthly
    gmvp_ns_ret = w_gmvp_ns @ mu_monthly
    gmvp_cap_ret = w_gmvp_cap @ mu_monthly

    # Filter each to keep only the efficient (upper) half
    f_short = filter_efficient(f_short_raw, gmvp_s_ret)
    f_ns = filter_efficient(f_ns_raw, gmvp_ns_ret)
    f_cap = filter_efficient(f_cap_raw, gmvp_cap_ret)

    return f_short, f_ns, f_cap, w_gmvp_s, w_gmvp_ns, w_gmvp_cap

f_short, f_ns, f_cap, w_gmvp_s, w_gmvp_ns, w_gmvp_cap = compute_all(MAX_WEIGHT)

# ---- Individual fund points ----
fund_vols = np.sqrt(np.diag(sigma_monthly))
fund_rets = mu_monthly

# ---- GMVP metrics ----
gmvp_s_vol = np.sqrt(w_gmvp_s @ sigma_monthly @ w_gmvp_s)
gmvp_s_ret = w_gmvp_s @ mu_monthly
gmvp_ns_vol = np.sqrt(w_gmvp_ns @ sigma_monthly @ w_gmvp_ns)
gmvp_ns_ret = w_gmvp_ns @ mu_monthly
gmvp_cap_vol = np.sqrt(w_gmvp_cap @ sigma_monthly @ w_gmvp_cap)
gmvp_cap_ret = w_gmvp_cap @ mu_monthly

# ---- User's optimal portfolio ----
user_point = None
if st.session_state.get("questionnaire_done"):
    A = st.session_state.A
    user_result = optimal_portfolio(mu_monthly, sigma_monthly, A,
                                    allow_short=False, max_weight=MAX_WEIGHT)
    user_point = (user_result["volatility"], user_result["return"], A)

# ---- Build Plotly figure ----
fig = go.Figure()

# Frontier 1: short sales allowed (for reference)
fig.add_trace(go.Scatter(
    x=[p[0] * vol_scale for p in f_short],
    y=[p[1] * ret_scale for p in f_short],
    mode="lines",
    name="Short sales allowed",
    line=dict(color="#A8DADC", width=2, dash="dot"),
    hovertemplate="σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# Frontier 2: no short sales
fig.add_trace(go.Scatter(
    x=[p[0] * vol_scale for p in f_ns],
    y=[p[1] * ret_scale for p in f_ns],
    mode="lines",
    name="No short sales",
    line=dict(color="#457B9D", width=2, dash="dash"),
    hovertemplate="σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# Frontier 3: with concentration cap (main one)
fig.add_trace(go.Scatter(
    x=[p[0] * vol_scale for p in f_cap],
    y=[p[1] * ret_scale for p in f_cap],
    mode="lines",
    name=f"No short + {int(MAX_WEIGHT*100)}% cap (used)",
    line=dict(color="#1D3557", width=4),
    hovertemplate="σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# Individual funds
fig.add_trace(go.Scatter(
    x=fund_vols * vol_scale,
    y=fund_rets * ret_scale,
    mode="markers+text",
    name="Individual Funds",
    text=fund_info["ticker"],
    textposition="top center",
    textfont=dict(size=10),
    marker=dict(size=10, color="#E76F51", symbol="circle",
                line=dict(color="white", width=1)),
    customdata=fund_info[["name", "asset_class"]].values,
    hovertemplate="<b>%{customdata[0]}</b><br>"
                  "Class: %{customdata[1]}<br>"
                  "σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# GMVP (short allowed)
fig.add_trace(go.Scatter(
    x=[gmvp_s_vol * vol_scale], y=[gmvp_s_ret * ret_scale],
    mode="markers", name="GMVP (short allowed)",
    marker=dict(size=14, color="#A8DADC", symbol="star",
                line=dict(color="black", width=1.5)),
    hovertemplate="<b>GMVP (short allowed)</b><br>σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# GMVP (capped)
fig.add_trace(go.Scatter(
    x=[gmvp_cap_vol * vol_scale], y=[gmvp_cap_ret * ret_scale],
    mode="markers", name=f"GMVP ({int(MAX_WEIGHT*100)}% cap)",
    marker=dict(size=16, color="#1D3557", symbol="star",
                line=dict(color="black", width=1.5)),
    hovertemplate="<b>GMVP (capped)</b><br>σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
))

# User's portfolio
if user_point is not None:
    uv, ur, uA = user_point
    fig.add_trace(go.Scatter(
        x=[uv * vol_scale], y=[ur * ret_scale],
        mode="markers", name=f"Your Portfolio (A={uA})",
        marker=dict(size=22, color="gold", symbol="diamond",
                    line=dict(color="black", width=2)),
        hovertemplate=f"<b>Your Portfolio (A={uA})</b><br>"
                      "σ=%{x:.2%}<br>μ=%{y:.2%}<extra></extra>",
    ))

# Axis range calculation
all_vols = ([gmvp_s_vol, gmvp_cap_vol] +
            list(fund_vols) +
            [p[0] for p in f_cap])
all_rets = ([gmvp_s_ret, gmvp_cap_ret] +
            list(fund_rets) +
            [p[1] for p in f_cap])
x_min, x_max = 0, max(all_vols) * vol_scale * 1.15
y_min, y_max = min(all_rets) * ret_scale * 1.15, max(all_rets) * ret_scale * 1.15

fig.update_layout(
    title=f"Efficient Frontier ({unit_label})",
    xaxis=dict(title=f"Volatility σ ({unit_label.lower()})",
               tickformat=".1%", range=[x_min, x_max]),
    yaxis=dict(title=f"Expected Return μ ({unit_label.lower()})",
               tickformat=".1%", range=[y_min, y_max]),
    height=600,
    hovermode="closest",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01,
                bgcolor="rgba(255,255,255,0.95)", bordercolor="lightgray",
                borderwidth=1, font=dict(size=11)),
    plot_bgcolor="white",
)
fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0", zeroline=True,
                 zerolinecolor="lightgray")

st.plotly_chart(fig, use_container_width=True)

st.divider()

col_info_1, col_info_2 = st.columns(2)

with col_info_1:
    st.markdown("### 💡 How to read this chart")
    st.markdown("""
    - **X-axis**: Risk (volatility σ)
    - **Y-axis**: Expected return μ
    - **Three frontiers** show how constraints progressively shrink the
      feasible set (each is the **efficient set** — upper half only):
      1. *Short sales allowed* (dotted) — theoretical best
      2. *No short sales* (dashed) — realistic base case
      3. *30% cap* (solid) — **what our robo-advisor uses**
    - **GMVP** (stars): Lowest-risk portfolio under each constraint
    - **Your portfolio** (gold diamond): Your optimal mix given your A
    """)

with col_info_2:
    st.markdown("### 🔑 Key observations")
    st.markdown(f"""
    - The **{int(MAX_WEIGHT*100)}% concentration cap** shifts the
      frontier inward — giving up some risk-adjusted return for
      **forced diversification**.
    - **GMVP (capped)** σ = {gmvp_cap_vol*vol_scale*100:.2f}% vs.
      **GMVP (no cap)** σ = {gmvp_ns_vol*vol_scale*100:.2f}%.
    - Real robo-advisors (Betterment, Wealthfront, Vanguard Digital
      Advisor) all impose similar caps to prevent over-concentration.
    """)

with st.expander("📊 GMVP Weights Comparison"):
    gmvp_df = pd.DataFrame({
        "Fund": fund_info["name"],
        "Class": fund_info["asset_class"],
        "Short allowed": [f"{w*100:+.1f}%" for w in w_gmvp_s],
        "No short": [f"{w*100:.1f}%" for w in w_gmvp_ns],
        f"With {int(MAX_WEIGHT*100)}% cap": [f"{w*100:.1f}%" for w in w_gmvp_cap],
    })
    st.dataframe(gmvp_df, hide_index=True, use_container_width=True)
    st.caption("Negative weights = short positions. The capped version is "
               "what our app actually recommends.")

if user_point is None:
    st.info("👆 Complete the Risk Assessment to see **your** optimal "
            "portfolio on the chart.")
