"""Compare Risk Profiles — side-by-side comparison of 5 representative A values."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.portfolio_engine import optimal_portfolio

# Aligned with teammate's Excel: 5 representative risk levels
A_LEVELS = [1, 2, 4, 6, 8]
A_LABELS = {
    1: "🚀 Aggressive (A=1)",
    2: "📈 Growth (A=2)",
    4: "⚖️ Balanced (A=4)",
    6: "🛡️ Mod. Conservative (A=6)",
    8: "🧊 Conservative (A=8)",
}
# No concentration cap (aligned with teammate's Excel)
MAX_WEIGHT = 1.0

st.title("🔄 Compare Risk Profiles")
st.caption("See how your recommended portfolio changes across risk aversion levels.")

# ---- Load data ----
@st.cache_data
def load_data():
    fund_info = pd.read_csv("data/fund_info.csv")
    mu = pd.read_csv("data/mu.csv", index_col=0)["expected_return"].values
    sigma = pd.read_csv("data/sigma.csv", index_col=0).values
    return fund_info, mu, sigma

fund_info, mu_monthly, sigma_monthly = load_data()


# ---- Compute all 5 portfolios ----
@st.cache_data
def compute_all_levels(max_w):
    results = {}
    for A in A_LEVELS:
        r = optimal_portfolio(mu_monthly, sigma_monthly, A,
                              allow_short=False, max_weight=max_w)
        results[A] = r
    return results

results = compute_all_levels(MAX_WEIGHT)


# ---- Where does the user sit? ----
user_A = st.session_state.get("A")
if user_A:
    st.info(f"👤 **Your risk aversion: A = {user_A:.2f}** ({st.session_state.get('risk_tier', '')})")

st.divider()

# ---- Section 1: 5 pie charts side by side ----
st.subheader("🥧 Portfolio Allocation Across Risk Levels")

# 10 fund colors
FUND_COLORS = [
    "#1D3557", "#457B9D", "#2E86AB", "#A8DADC",
    "#F4A261", "#E76F51", "#E9C46A", "#8D99AE",
    "#6A994E", "#BC4749",
]

# Build a combined subplots figure with 5 donuts
fig_pies = make_subplots(
    rows=1, cols=5,
    specs=[[{"type": "domain"}] * 5],
    subplot_titles=[A_LABELS[A] for A in A_LEVELS],
    horizontal_spacing=0.02,
)

for i, A in enumerate(A_LEVELS):
    w = results[A]["weights"]
    # Filter out tiny weights
    labels, values, colors = [], [], []
    for j, wi in enumerate(w):
        if wi > 0.005:
            labels.append(fund_info["name"].iloc[j])
            values.append(wi)
            colors.append(FUND_COLORS[j])

    fig_pies.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors),
            textposition="inside",
            textinfo="percent",
            textfont=dict(size=10, color="white"),
            showlegend=False,
            hovertemplate="<b>%{label}</b><br>Weight: %{percent}<extra></extra>",
        ),
        row=1, col=i + 1,
    )

# Highlight the closest A tier to user
if user_A:
    closest_A = min(A_LEVELS, key=lambda a: abs(a - user_A))
    closest_idx = A_LEVELS.index(closest_A)
    # Update the subplot title for that column
    fig_pies.layout.annotations[closest_idx].text = (
        f"<b>⭐ {A_LABELS[closest_A]}</b><br>"
        f"<span style='font-size:11px'>closest to you</span>"
    )

fig_pies.update_layout(
    height=320,
    margin=dict(t=60, b=10, l=10, r=10),
)

st.plotly_chart(fig_pies, use_container_width=True)

st.divider()

# ---- Section 2: Risk-Return metrics line chart ----
st.subheader("📈 Risk-Return Profile Across A")

metrics_df = pd.DataFrame([
    {
        "A": A,
        "Expected Return (ann.)": results[A]["return"] * 12 * 100,
        "Volatility (ann.)": results[A]["volatility"] * np.sqrt(12) * 100,
        "Sharpe Ratio": (results[A]["return"] * 12) /
                        (results[A]["volatility"] * np.sqrt(12))
                        if results[A]["volatility"] > 0 else 0,
        "Utility U": results[A]["utility"] * 12,  # approx annualized
    }
    for A in A_LEVELS
])

# 3-in-1 chart
fig_metrics = make_subplots(
    rows=1, cols=3,
    subplot_titles=["Expected Return", "Volatility", "Sharpe Ratio"],
    horizontal_spacing=0.12,
)

fig_metrics.add_trace(
    go.Scatter(x=metrics_df["A"], y=metrics_df["Expected Return (ann.)"],
               mode="lines+markers", line=dict(color="#2A9D8F", width=3),
               marker=dict(size=10), name="Return"),
    row=1, col=1,
)
fig_metrics.add_trace(
    go.Scatter(x=metrics_df["A"], y=metrics_df["Volatility (ann.)"],
               mode="lines+markers", line=dict(color="#E76F51", width=3),
               marker=dict(size=10), name="Volatility"),
    row=1, col=2,
)
fig_metrics.add_trace(
    go.Scatter(x=metrics_df["A"], y=metrics_df["Sharpe Ratio"],
               mode="lines+markers", line=dict(color="#264653", width=3),
               marker=dict(size=10), name="Sharpe"),
    row=1, col=3,
)

# Highlight user's A position on each panel
if user_A:
    for col in [1, 2, 3]:
        fig_metrics.add_vline(x=user_A, line=dict(color="gold", width=2, dash="dash"),
                              row=1, col=col)

# Axis formatting
fig_metrics.update_yaxes(ticksuffix="%", row=1, col=1)
fig_metrics.update_yaxes(ticksuffix="%", row=1, col=2)
for col in [1, 2, 3]:
    fig_metrics.update_xaxes(title="Risk Aversion A", row=1, col=col,
                             tickvals=A_LEVELS)

fig_metrics.update_layout(
    height=350,
    showlegend=False,
    margin=dict(t=60, b=40, l=40, r=20),
    plot_bgcolor="white",
)
fig_metrics.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
fig_metrics.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

st.plotly_chart(fig_metrics, use_container_width=True)

if user_A:
    st.caption(f"🟨 Gold dashed line = your position (A = {user_A:.2f})")

st.divider()

# ---- Section 3: Weight heatmap ----
st.subheader("🔥 Weight Distribution Heatmap")

# Build weight matrix: rows = funds, cols = A values
weight_matrix = np.array([results[A]["weights"] for A in A_LEVELS]).T  # 10 x 5
weight_pct = weight_matrix * 100

fig_heatmap = go.Figure(data=go.Heatmap(
    z=weight_pct,
    x=[f"A={A}" for A in A_LEVELS],
    y=fund_info["name"].tolist(),
    colorscale="Blues",
    zmin=0, zmax=weight_pct.max(),
    text=[[f"{v:.0f}%" if v >= 1 else "" for v in row] for row in weight_pct],
    texttemplate="%{text}",
    textfont=dict(size=11),
    hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
    colorbar=dict(title="Weight %", ticksuffix="%"),
))

fig_heatmap.update_layout(
    height=400,
    margin=dict(t=30, b=30, l=10, r=10),
    xaxis=dict(side="top"),
    yaxis=dict(autorange="reversed"),
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.caption(
    "Each cell shows the weight of a fund in the recommended portfolio "
    "for that A value. Darker = higher allocation."
)

st.divider()

# ---- Section 4: Numerical table ----
with st.expander("📊 Detailed Numerical Comparison"):
    display_df = metrics_df.copy()
    display_df["Expected Return (ann.)"] = display_df["Expected Return (ann.)"].apply(
        lambda v: f"{v:.2f}%")
    display_df["Volatility (ann.)"] = display_df["Volatility (ann.)"].apply(
        lambda v: f"{v:.2f}%")
    display_df["Sharpe Ratio"] = display_df["Sharpe Ratio"].apply(lambda v: f"{v:.2f}")
    display_df["Utility U"] = display_df["Utility U"].apply(lambda v: f"{v:.4f}")
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.caption(
        "Cross-check reference: these five A values directly correspond "
        "to the teammate's Excel Solver implementation, enabling result validation."
    )

st.divider()

# ---- Interpretation box ----
st.subheader("🔑 Key Observations")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("**As A increases (more risk-averse)**")
    st.markdown(f"""
    - Expected return **decreases**
      (from {metrics_df['Expected Return (ann.)'].iloc[0]:.1f}%
      to {metrics_df['Expected Return (ann.)'].iloc[-1]:.1f}%)
    - Volatility **decreases**
      (from {metrics_df['Volatility (ann.)'].iloc[0]:.1f}%
      to {metrics_df['Volatility (ann.)'].iloc[-1]:.1f}%)
    """)

with col_b:
    st.markdown("**Shift in asset mix**")
    # Find which fund gains the most as A grows
    w_low = results[A_LEVELS[0]]["weights"]
    w_high = results[A_LEVELS[-1]]["weights"]
    delta = w_high - w_low
    top_gainer_idx = int(np.argmax(delta))
    top_loser_idx = int(np.argmin(delta))
    st.markdown(f"""
    - Biggest winner: **{fund_info['name'].iloc[top_gainer_idx]}**
      (+{delta[top_gainer_idx]*100:.0f}%)
    - Biggest loser: **{fund_info['name'].iloc[top_loser_idx]}**
      ({delta[top_loser_idx]*100:.0f}%)
    """)

with col_c:
    st.markdown("**Sharpe ratio**")
    sharpe_range = (metrics_df["Sharpe Ratio"].max() -
                    metrics_df["Sharpe Ratio"].min())
    st.markdown(f"""
    - Range across A: {sharpe_range:.2f}
    - Best Sharpe at A =
      **{metrics_df.loc[metrics_df['Sharpe Ratio'].idxmax(), 'A']:.0f}**
    - Risk-adjusted return stays relatively stable,
      a hallmark of efficient portfolios.
    """)
