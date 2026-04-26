"""Your Risk Profile — total score, R-tier, A value, score breakdown."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.questionnaire import PERSONA_DESCRIPTIONS, RISK_TIERS

st.title("Your Risk Profile")

# ---- Guard ----
if not st.session_state.get("questionnaire_done"):
    st.warning("Please complete the Risk Assessment first.")
    st.page_link("pages/1_Risk_Assessment.py",
                 label="Go to Risk Assessment",
                 icon="📝")
    st.stop()

A = st.session_state.A
R = st.session_state.R
tier_full = st.session_state.risk_tier_full
tier = st.session_state.risk_tier
total_score = st.session_state.total_score
block_scores = st.session_state.block_scores
tier_color = st.session_state.tier_color

# ============================================================================
# Top section
# ============================================================================
col_a, col_score, col_tier = st.columns([1, 1, 2])

with col_a:
    st.metric("Risk Aversion (A)", f"{A}",
              help="One of {1, 2, 4, 6, 8} based on your R tier.")

with col_score:
    st.metric("Total Weighted Score", f"{total_score} / 75",
              help="Block 1 (Q1–Q5, ×1) + Block 2 (Q6–Q10, ×2)")

with col_tier:
    st.markdown(f"### {R}: {tier}")
    st.markdown(f"*{PERSONA_DESCRIPTIONS[R]}*")

st.divider()

# ============================================================================
# 5-tier risk spectrum gauge
# ============================================================================
st.subheader("Where You Sit on the Risk Spectrum")

fig_gauge = go.Figure()

# Score range is 15 to 75
SCORE_MIN = 15
SCORE_MAX = 75

# 5 tier colored bands
for label, full, lo, hi, A_val, color, emoji in RISK_TIERS:
    fig_gauge.add_shape(
        type="rect",
        x0=lo, x1=hi, y0=0, y1=1,
        fillcolor=color, opacity=0.5, line=dict(width=0),
    )
    fig_gauge.add_annotation(
        x=(lo + hi) / 2, y=0.5,
        text=f"<b>{label}</b><br>{full}<br>(A={A_val})",
        showarrow=False,
        font=dict(size=11, color="white"),
    )

# User position
fig_gauge.add_shape(
    type="line",
    x0=total_score, x1=total_score, y0=-0.05, y1=1.05,
    line=dict(color="black", width=3),
)
fig_gauge.add_annotation(
    x=total_score, y=1.35,
    text=f"<b>You: score = {total_score}</b>",
    showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
    arrowcolor="black", ax=0, ay=-15,
    font=dict(size=13, color="black"),
    bgcolor="rgba(255, 230, 100, 0.85)",
    bordercolor="black", borderwidth=1, borderpad=4,
)

fig_gauge.update_layout(
    xaxis=dict(
        range=[SCORE_MIN, SCORE_MAX], showgrid=False,
        tickvals=[15, 27, 39, 51, 63, 75],
        ticktext=["15", "27", "39", "51", "63", "75"],
        fixedrange=True,
        title="Total weighted score",
    ),
    yaxis=dict(range=[-0.2, 1.8], visible=False, fixedrange=True),
    height=240,
    margin=dict(t=60, b=40, l=40, r=40),
    showlegend=False,
    plot_bgcolor="white",
)
st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# ============================================================================
# Score breakdown
# ============================================================================
st.subheader("Score Breakdown")

col_bar, col_explain = st.columns([3, 2])

with col_bar:
    # Stacked bar: Block 1 vs Block 2
    block1 = block_scores["Block 1 (Q1–Q5)"]
    block2 = block_scores["Block 2 (Q6–Q10, ×2)"]

    fig_blocks = go.Figure()
    fig_blocks.add_trace(go.Bar(
        x=["Your score"],
        y=[block1],
        name="Block 1: Capacity (Q1–Q5, ×1)",
        marker_color="#457B9D",
        text=[f"{block1}"],
        textposition="inside",
        textfont=dict(color="white", size=14),
    ))
    fig_blocks.add_trace(go.Bar(
        x=["Your score"],
        y=[block2],
        name="Block 2: Tolerance (Q6–Q10, ×2)",
        marker_color="#1D3557",
        text=[f"{block2}"],
        textposition="inside",
        textfont=dict(color="white", size=14),
    ))

    # Reference lines for max possible
    fig_blocks.add_hline(y=25, line=dict(color="#457B9D", width=1, dash="dash"),
                          annotation_text="Block 1 max = 25",
                          annotation_position="left",
                          annotation_font_size=10)
    fig_blocks.add_hline(y=75, line=dict(color="black", width=1, dash="dash"),
                          annotation_text="Total max = 75",
                          annotation_position="left",
                          annotation_font_size=10)

    fig_blocks.update_layout(
        barmode="stack",
        height=400,
        yaxis=dict(range=[0, 80], title="Score"),
        xaxis=dict(showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5),
        margin=dict(t=20, b=80, l=60, r=20),
        plot_bgcolor="white",
    )
    fig_blocks.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    st.plotly_chart(fig_blocks, use_container_width=True)

with col_explain:
    st.markdown("**How the score breaks down**")
    st.markdown(f"""
    **Block 1 — Capacity (Q1–Q5, weight ×1)**
    Objective factors: age, income, investable share,
    portfolio composition, experience.
    Your score: **{block1}** / 25.

    **Block 2 — Tolerance (Q6–Q10, weight ×2)**
    Subjective factors: attitude, lottery preference,
    horizon, objective, loss tolerance.
    Your score: **{block2}** / 50.

    Block 2 is weighted **2×** because behavioural research
    (Kahneman & Tversky, 1979) shows psychological tolerance
    is the strongest predictor of whether an investor stays
    the course during a drawdown.
    """)

st.divider()

# ============================================================================
# All tiers reference table
# ============================================================================
with st.expander("All Risk Tiers Reference"):
    tier_df = pd.DataFrame([
        {
            "Tier": label,
            "Description": full,
            "Score Range": f"{lo} – {hi}",
            "Risk Aversion A": A_val,
        }
        for label, full, lo, hi, A_val, _, _ in RISK_TIERS
    ])
    st.dataframe(tier_df, hide_index=True, use_container_width=True)
    st.caption(
        "These boundaries match the scoring rubric implemented in the team's "
        "Excel workbook (`Risk_Assessment` sheet)."
    )

st.divider()
st.success("Your risk profile is ready. Next: see your personalised portfolio.")
st.page_link("pages/3_Portfolio.py",
             label="View Recommended Portfolio",
             icon="💼")
