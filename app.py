"""Robot Adviser — Streamlit Main Entry."""
import streamlit as st

st.set_page_config(
    page_title="Robot Adviser",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global state init ----
if "questionnaire_done" not in st.session_state:
    st.session_state.questionnaire_done = False
if "A" not in st.session_state:
    st.session_state.A = None
if "scores" not in st.session_state:
    st.session_state.scores = {}

# ---- Landing page ----
st.title("🤖 Robot Adviser")
st.markdown("### Get a data-driven, personalized investment portfolio in 3 minutes.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Funds Universe", "10")
with col2:
    st.metric("📝 Questions", "10")
with col3:
    st.metric("⏱ Time Required", "~3 min")

st.divider()

st.markdown("""
#### How it works
1. **Answer a quick risk questionnaire** to determine your risk profile
2. **Get a personalized portfolio** based on Markowitz optimization
3. **Explore the efficient frontier** and see where your portfolio sits
4. **Calculate** how much to invest in each fund based on your capital

⚠️ *This is an academic project. Not financial advice.*
""")

st.info("👈 Start by clicking **Risk Assessment** in the sidebar.")
