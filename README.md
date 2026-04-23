# 🤖 Robot Adviser — BMD5302 Group Project

A Streamlit web application that delivers personalized investment portfolios using Modern Portfolio Theory and a 15-question risk profiling system.

> **Live demo**: (will add URL after deployment)

## ✨ Features

- 📝 **Risk Assessment** — 15-question survey across 4 dimensions (Capacity, Horizon, Tolerance, Knowledge) with weighted scoring
- 🎯 **Risk Profile** — Interactive radar chart, tier classification, continuous risk aversion coefficient A ∈ [1.5, 10]
- 💼 **Personalized Portfolio** — Markowitz mean-variance optimization with 30% concentration cap (industry standard)
- 📈 **Efficient Frontier** — Interactive visualization with three frontiers: short-allowed, no-short, and capped
- 💰 **Investment Calculator** — Dollar-level fund allocation based on user capital

## 🏗 Architecture

```
robo-adviser/
├── app.py                          # Landing page
├── pages/
│   ├── 1_Risk_Assessment.py        # 15-question questionnaire
│   ├── 2_Your_Profile.py           # A value + radar chart
│   ├── 3_Portfolio.py              # Recommended portfolio
│   └── 4_Efficient_Frontier.py     # MPT visualization
├── core/
│   ├── portfolio_engine.py         # GMVP, frontier, utility optimization
│   └── questionnaire.py            # Question definitions, scoring logic
├── data/                           # Fund universe data
│   ├── fund_info.csv
│   ├── mu.csv                      # Expected returns (monthly)
│   ├── sigma.csv                   # Covariance matrix (monthly)
│   └── prices.csv                  # 61 months of historical prices
├── requirements.txt
└── README.md
```

## 📊 Methodology

**Optimization**: Maximize utility function
$$U = r - \frac{\sigma^2 A}{2}$$
subject to $\sum w_i = 1$, $w_i \geq 0$, $w_i \leq 0.30$.

**Risk aversion mapping**:
$$A = 1.5 + \frac{\text{Score} - S_{\min}}{S_{\max} - S_{\min}} \times 8.5$$

**Risk tiers**: Aggressive [1.5–3.5), Growth [3.5–5.5), Balanced [5.5–7.5), Conservative [7.5–10]

## 🛠 Tech Stack

- **Backend**: Python, NumPy, SciPy (SLSQP optimizer), Pandas
- **Frontend**: Streamlit, Plotly
- **Deployment**: Streamlit Community Cloud

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/robo-adviser-bmd5302.git
cd robo-adviser-bmd5302
pip install -r requirements.txt
streamlit run app.py
```

## 📚 References

- Markowitz, H. (1952). *Portfolio Selection*. Journal of Finance.
- Grable, J. E., & Lytton, R. H. (1999). *Financial Risk Tolerance Revisited*.
- Mehra, R., & Prescott, E. C. (1985). *The Equity Premium: A Puzzle*.

## ⚠️ Disclaimer

This is an academic project for BMD5302 Financial Modeling at NUS. Not financial advice.
