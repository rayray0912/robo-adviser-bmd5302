"""Your Risk Profile — A value, 4-dimension radar, persona description."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
from core.questionnaire import PERSONA_DESCRIPTIONS

st.title("🎯 Your Risk Profile")

# ---- Guard ----
if not st.session_state.get("questionnaire_done"):
    st.warning("⚠️ Please complete the Risk Assessment first.")
    st.page_link("pages/1_Risk_Assessment.py", label="👉 Go to Risk Assessment", icon="📝")
    st.stop()

A = st.session_state.A
tier = st.session_state.risk_tier
dim_scores = st.session_state.dimension_scores

# ---- Top section ----
col_a, col_tier = st.columns([1, 2])

with col_a:
    st.metric("Risk Aversion Coefficient", f"A = {A:.2f}",
              help="A ∈ [1.5, 10]. Higher A = more risk-averse.")

with col_tier:
    st.markdown(f"### {tier}")
    st.markdown(f"*{PERSONA_DESCRIPTIONS[tier]}*")

st.divider()

# ---- A value position indicator ----
st.subheader("📍 Where You Sit on the Risk Spectrum")

A_MIN, A_MAX = 1.5, 10.0

fig_gauge = go.Figure()

# 4 tier colored bands
tier_ranges = [
    ("🚀 Aggressive", 1.5, 3.5, "#E63946"),
    ("📈 Growth", 3.5, 5.5, "#F4A261"),
    ("⚖️ Balanced", 5.5, 7.5, "#2A9D8F"),
    ("🛡️ Conservative", 7.5, 10.0, "#264653"),
]

for label, lo, hi, color in tier_ranges:
    fig_gauge.add_shape(
        type="rect",
        x0=lo, x1=hi, y0=0, y1=1,
        fillcolor=color, opacity=0.35, line=dict(width=0),
    )
    fig_gauge.add_annotation(
        x=(lo + hi) / 2, y=0.5, text=label,
        showarrow=False, font=dict(size=12, color="white"),
    )

# User's position marker — put annotation ABOVE the bar, not overlapping axis
fig_gauge.add_shape(
    type="line", x0=A, x1=A, y0=-0.1, y1=1.1,
    line=dict(color="black", width=3),
)
fig_gauge.add_annotation(
    x=A, y=1.35,
    text=f"<b>You are here: A = {A:.2f}</b>",
    showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
    arrowcolor="black", ax=0, ay=-15,
    font=dict(size=13, color="black"),
    bgcolor="rgba(255, 255, 0, 0.7)",
    bordercolor="black", borderwidth=1, borderpad=4,
)

fig_gauge.update_layout(
    xaxis=dict(range=[A_MIN, A_MAX], showgrid=False,
               tickvals=[1.5, 3.5, 5.5, 7.5, 10],
               ticktext=["1.5", "3.5", "5.5", "7.5", "10"],
               fixedrange=True),
    yaxis=dict(range=[-0.2, 1.8], visible=False, fixedrange=True),
    height=220,
    margin=dict(t=60, b=30, l=40, r=40),
    showlegend=False,
    plot_bgcolor="white",
)
st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# ---- 4-dimension radar chart ----
st.subheader("Your Risk Profile Across 4 Dimensions")

MAX_SCORES = {
    "Capacity": 4 * 4,
    "Horizon":  3 * 4,
    "Tolerance": 5 * 4,
    "Knowledge": 3 * 4,
}

normalized = {dim: dim_scores[dim] / MAX_SCORES[dim] * 100 for dim in dim_scores}

categories = list(normalized.keys())
values = list(normalized.values())
categories_closed = categories + [categories[0]]
values_closed = values + [values[0]]

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=values_closed,
    theta=categories_closed,
    fill="toself",
    fillcolor="rgba(46, 134, 171, 0.3)",
    line=dict(color="#2E86AB", width=2),
    name="Your Profile",
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%"),
    ),
    showlegend=False,
    height=400,
    margin=dict(t=30, b=30, l=30, r=30),
)

col_radar, col_explain = st.columns([1, 1])

with col_radar:
    st.plotly_chart(fig_radar, use_container_width=True)

with col_explain:
    st.markdown("**How to read this chart**")
    st.markdown("""
    Higher % on a dimension = **more risk-averse** on that axis.
    - **Capacity**: Financial ability to absorb losses
    - **Horizon**: Time available before needing funds
    - **Tolerance**: Psychological comfort with volatility
    - **Knowledge**: Investment experience
    """)

    top_dim = max(normalized, key=normalized.get)
    low_dim = min(normalized, key=normalized.get)
    st.info(f"💡 **Most risk-averse on**: {top_dim} ({normalized[top_dim]:.0f}%)")
    st.info(f"💡 **Least risk-averse on**: {low_dim} ({normalized[low_dim]:.0f}%)")

st.divider()

# ---- Dimension scores table ----
with st.expander("🔍 Detailed Scores"):
    import pandas as pd
    weights_map = {"Capacity": 1.0, "Horizon": 1.0, "Tolerance": 1.4, "Knowledge": 0.6}
    detail_df = pd.DataFrame({
        "Dimension": list(dim_scores.keys()),
        "Raw Score": list(dim_scores.values()),
        "Max Possible": [MAX_SCORES[d] for d in dim_scores],
        "Weight": [weights_map[d] for d in dim_scores],
        "Weighted Score": [dim_scores[d] * weights_map[d] for d in dim_scores],
    })
    st.dataframe(detail_df, hide_index=True, use_container_width=True)
    st.caption(f"**Total weighted score**: {st.session_state.total_score} → mapped to A = {A:.2f}")

st.divider()
st.success("✅ Your risk profile is ready. Next: see your personalized portfolio.")
st.page_link("pages/3_Portfolio.py", label="👉 View Recommended Portfolio", icon="💼")
