"""Risk Assessment Questionnaire — 10 questions aligned with Excel implementation."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from core.questionnaire import QUESTIONS, compute_risk_aversion, DEMO_PROFILES

st.title("Risk Assessment")
st.caption(
    f"Answer {len(QUESTIONS)} questions to determine your risk aversion. "
    "Q1–Q5 measure objective capacity (weight 1); "
    "Q6–Q10 measure subjective preferences and tolerance (weight 2)."
)

# ============================================================================
# Demo profile quick-load
# ============================================================================
with st.expander("Quick Demo Profiles (for presentation)", expanded=False):
    st.caption(
        "Skip the questionnaire and load a representative investor profile. "
        "Each persona maps to a distinct risk tier (R1–R5)."
    )

    cols = st.columns(len(DEMO_PROFILES))
    for col, (key, profile) in zip(cols, DEMO_PROFILES.items()):
        with col:
            st.markdown(f"**{profile['label']}** ({profile['age']} years old)")
            st.caption(profile["description"])
            st.caption(
                f"→ Expected: {profile['expected_R']} ({profile['expected_tier']}), "
                f"A = {profile['expected_A']}"
            )

            if st.button(f"Load {profile['label']}",
                         key=f"load_{key}",
                         use_container_width=True):
                result = compute_risk_aversion(profile["answers"])

                st.session_state.questionnaire_done = True
                st.session_state.A = result["A"]
                st.session_state.R = result["R"]
                st.session_state.risk_tier = result["risk_tier"]
                st.session_state.risk_tier_full = result["risk_tier_full"]
                st.session_state.total_score = result["total_score"]
                st.session_state.block_scores = result["block_scores"]
                st.session_state.tier_color = result["color"]
                st.session_state.demo_profile_loaded = profile["label"]

                st.success(
                    f"Loaded **{profile['label']}**: "
                    f"Total score = **{result['total_score']}**, "
                    f"Tier: **{result['R']} ({result['risk_tier_full']})**, "
                    f"A = **{result['A']}**"
                )
                st.info("Navigate to **Your Profile** in the sidebar "
                        "to see the full analysis.")

st.divider()

# ============================================================================
# Main questionnaire
# ============================================================================
with st.form("risk_form"):
    answers = {}

    for q in QUESTIONS:
        qid = q["id"]
        weight_label = "weight ×1" if q["block"] == 1 else "weight ×2"
        st.markdown(f"**{qid}.** {q['text']}  *<span style=\"color:#888\">({weight_label})</span>*",
                    unsafe_allow_html=True)

        # Build option labels with the letter prefix for readability
        choices = [f"{label}. {text}" for label, text, _ in q["options"]]
        chosen = st.radio(
            label=qid,
            options=choices,
            key=f"radio_{qid}",
            label_visibility="collapsed",
        )
        # Extract back the short label (A/B/C/...)
        answers[qid] = chosen.split(".", 1)[0].strip()
        st.divider()

    submitted = st.form_submit_button(
        "Calculate My Risk Profile", type="primary"
    )

# ============================================================================
# On submit: compute and store
# ============================================================================
if submitted:
    result = compute_risk_aversion(answers)

    st.session_state.questionnaire_done = True
    st.session_state.A = result["A"]
    st.session_state.R = result["R"]
    st.session_state.risk_tier = result["risk_tier"]
    st.session_state.risk_tier_full = result["risk_tier_full"]
    st.session_state.total_score = result["total_score"]
    st.session_state.block_scores = result["block_scores"]
    st.session_state.tier_color = result["color"]

    st.success(f"Your risk aversion coefficient: **A = {result['A']}**")
    st.info(
        f"Total weighted score: **{result['total_score']}** / 75  →  "
        f"Tier: **{result['R']} ({result['risk_tier_full']})**"
    )

    # Block scores
    c1, c2, c3 = st.columns(3)
    c1.metric("Block 1 (Q1–Q5)", result["block_scores"]["Block 1 (Q1–Q5)"])
    c2.metric("Block 2 (Q6–Q10) × 2", result["block_scores"]["Block 2 (Q6–Q10, ×2)"])
    c3.metric("Total", result["total_score"])

    st.caption("Go to **Your Profile** in the sidebar to see your portfolio.")
