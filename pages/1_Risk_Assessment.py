"""Risk Assessment Questionnaire — uses core/questionnaire.py"""
import sys
from pathlib import Path

# 让 Streamlit 能找到 core/ 模块
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from core.questionnaire import QUESTIONS, compute_risk_aversion

st.title("Risk Assessment")
st.caption(f"Answer {len(QUESTIONS)} questions to determine your risk aversion (A).")

# ---- Render form ----
with st.form("risk_form"):
    answers = {}  # {qid: option_text}

    for i, (qid, q_text, opts, dim) in enumerate(QUESTIONS):
        st.markdown(f"**{qid}. {q_text}**")
        st.caption(f"Dimension: {dim}")

        choice = st.radio(
            label=qid,
            options=[label for label, _ in opts],
            key=f"radio_{qid}",
            label_visibility="collapsed",
        )
        answers[qid] = choice
        st.divider()

    submitted = st.form_submit_button("Calculate My Risk Profile", type="primary")

# ---- Compute A on submit ----
if submitted:
    result = compute_risk_aversion(answers)

    # 保存到 session_state 给其他页面用
    st.session_state.questionnaire_done = True
    st.session_state.A = result["A"]
    st.session_state.risk_tier = result["risk_tier"]
    st.session_state.dimension_scores = result["dimension_scores"]
    st.session_state.total_score = result["total_score"]

    # 展示结果
    st.success(f"Your risk aversion coefficient: **A = {result['A']}**")
    st.info(f"Risk Tier: **{result['risk_tier']}**")

    # 简单展示各维度得分
    cols = st.columns(4)
    for col, (dim, score) in zip(cols, result["dimension_scores"].items()):
        col.metric(dim, score)

    st.caption("Go to **Your Profile** in the sidebar to see your portfolio.")
