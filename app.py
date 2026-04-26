"""Robot Adviser — Landing Page"""
import streamlit as st

st.set_page_config(
    page_title="Robot Adviser | BMD5302",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global state init ----
for key, default in [
    ("questionnaire_done", False),
    ("A", None),
    ("risk_tier", None),
    ("dimension_scores", {}),
    ("total_score", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---- Custom CSS ----
st.markdown("""
<style>
.hero-title {
    font-size: 3.4rem;
    font-weight: 700;
    color: #1D3557;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-highlight {
    color: #E9C46A;
}
.hero-subtitle {
    font-size: 1.25rem;
    color: #457B9D;
    font-weight: 400;
    margin-bottom: 2rem;
}
.step-card {
    background: linear-gradient(135deg, #F1FAEE 0%, #FFFFFF 100%);
    border-left: 4px solid #1D3557;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: transform 0.15s ease;
}
.step-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.step-number {
    color: #E9C46A;
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
}
.step-title {
    color: #1D3557;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0.3rem 0;
}
.step-desc {
    color: #6c757d;
    font-size: 0.95rem;
    line-height: 1.4;
}
.feature-box {
    background: #FFFFFF;
    border: 1px solid #E9ECEF;
    border-radius: 10px;
    padding: 1.5rem;
    height: 100%;
    text-align: center;
}
.feature-icon {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
}
.feature-title {
    color: #1D3557;
    font-size: 1.15rem;
    font-weight: 600;
    margin: 0.5rem 0;
}
.feature-desc {
    color: #6c757d;
    font-size: 0.9rem;
    line-height: 1.5;
}
.disclaimer-box {
    background: #FFF8E1;
    border-left: 3px solid #E9C46A;
    padding: 0.8rem 1.2rem;
    border-radius: 6px;
    font-size: 0.9rem;
    color: #6c757d;
    margin-top: 2rem;
}
div[data-testid="stMetricValue"] {
    color: #1D3557;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Hero section
# ============================================================================
col_hero_1, col_hero_2 = st.columns([3, 2])

with col_hero_1:
    st.markdown(
        '<div class="hero-title">Know your risk.<br>'
        'Own your <span class="hero-highlight">portfolio</span>.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'An evidence-based robo-adviser built on '
        '<b>Modern Portfolio Theory</b> — turning a 10-question risk profile '
        'into your personalized investment portfolio.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.page_link("pages/1_Risk_Assessment.py",
                 label="Start your assessment →",
                 icon="")

with col_hero_2:
    st.markdown("&nbsp;")
    m1, m2 = st.columns(2)
    m1.metric("Funds in universe", "10",
              help="Real FSMOne unit trusts spanning equity, bond, "
                   "and multi-asset classes")
    m2.metric("Questions", "10",
              help="2 blocks: Q1–Q5 (capacity, ×1) and Q6–Q10 (tolerance, ×2)")
    m3, m4 = st.columns(2)
    m3.metric("Risk profiles", "5 tiers",
              help="R1 Conservative / R2 Mod. Conservative / R3 Balanced / R4 Growth / R5 Aggressive")
    m4.metric("Time needed", "~3 min", help="End-to-end walkthrough")

st.divider()

# ============================================================================
# How it works — 3 step horizontal flow
# ============================================================================
st.markdown("### How it works")

col_s1, col_arrow1, col_s2, col_arrow2, col_s3 = st.columns(
    [3, 0.3, 3, 0.3, 3]
)

with col_s1:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-title">Assess your risk</div>
        <div class="step-desc">
            Answer 10 carefully designed questions to be classified into
            one of five risk tiers (R1 Conservative through R5 Aggressive),
            mapped to a discrete risk aversion A ∈ {1, 2, 4, 6, 8}.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_arrow1:
    st.markdown("<div style='text-align:center; color:#E9C46A; "
                "font-size:2rem; padding-top:1.5rem;'>→</div>",
                unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-title">Optimize your portfolio</div>
        <div class="step-desc">
            Markowitz mean-variance optimization maximizes your
            utility function U = r − σ²A/2 to find the ideal mix.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_arrow2:
    st.markdown("<div style='text-align:center; color:#E9C46A; "
                "font-size:2rem; padding-top:1.5rem;'>→</div>",
                unsafe_allow_html=True)

with col_s3:
    st.markdown("""
    <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-title">Visualize & compare</div>
        <div class="step-desc">
            Explore the efficient frontier, compare across risk levels,
            and calculate your dollar-level allocation.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================================
# What you get — feature cards
# ============================================================================
st.markdown("### What's inside")

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">▸</div>
        <div class="feature-title">Risk Assessment</div>
        <div class="feature-desc">
            10-question survey with two weighted scoring blocks:
            Q1–Q5 (objective capacity) and Q6–Q10 (subjective tolerance, ×2).
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">▸</div>
        <div class="feature-title">Risk Profile</div>
        <div class="feature-desc">
            Risk-spectrum gauge, tier classification (R1–R5),
            and discrete A value mapped from your weighted total score.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">▸</div>
        <div class="feature-title">Portfolio Builder</div>
        <div class="feature-desc">
            Personalized fund allocation with interactive pie chart
            and dollar-level investment calculator.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-icon">▸</div>
        <div class="feature-title">MPT Visualizer</div>
        <div class="feature-desc">
            Efficient frontier with side-by-side comparison
            across 5 risk levels and heatmap weight breakdown.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================================
# Methodology highlight
# ============================================================================
with st.expander("The science behind the adviser"):
    st.markdown("""
    Our robo-adviser is built on three academically rigorous foundations:

    1. **Modern Portfolio Theory** (Markowitz, 1952) — The mean-variance
       optimization framework that underpins institutional portfolio
       construction.

    2. **Utility-based optimization** — We find the portfolio that maximizes
       your personal utility $U = r - \\frac{\\sigma^2 A}{2}$, where $A$
       reflects your individual risk aversion.

    3. **Two-block risk profiling** — Our 10-question questionnaire splits
       items into objective capacity (Q1–Q5, weight ×1) and subjective
       tolerance (Q6–Q10, weight ×2). The doubled weight on tolerance
       reflects behavioural-finance findings (Kahneman & Tversky, 1979)
       that psychological response to drawdowns is the strongest predictor
       of investor behaviour.

    **Data**: 10 real FSMOne unit trusts with 5 years of monthly price
    history (Apr 2021 – Apr 2026), covering global equity, Asia-focused
    multi-asset, and fixed-income exposure.

    **Implementation**: Two independent engines validate each other —
    Python/SLSQP (this app) and Excel/Solver (our companion workbook) —
    producing identical optimal portfolios across all tested risk levels.
    """)

# ============================================================================
# CTA
# ============================================================================
st.markdown("&nbsp;")
cta_col_1, cta_col_2, cta_col_3 = st.columns([1, 2, 1])
with cta_col_2:
    st.markdown(
        "<div style='text-align:center;'>"
        "<h3 style='color:#1D3557;'>Ready to build your portfolio?</h3>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Risk_Assessment.py",
                 label="Begin Risk Assessment",
                 icon="")

# ============================================================================
# Disclaimer footer
# ============================================================================
st.markdown("""
<div class="disclaimer-box">
<b>⚠ Academic project disclaimer:</b> This application was built for
BMD5302 Financial Modeling (NUS MSc Digital Financial Technology).
It is not financial advice. Past performance does not guarantee future
results. Consult a licensed financial advisor before making investment
decisions.
</div>
""", unsafe_allow_html=True)
