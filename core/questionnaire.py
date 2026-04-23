"""
questionnaire.py
Risk profiling questionnaire for the Robot Adviser.

Design principles:
- 15 questions across 4 dimensions (Capacity, Horizon, Tolerance, Knowledge)
- Weighted scoring: Tolerance (1.4) > Capacity = Horizon (1.0) > Knowledge (0.6)
- Linear mapping to A ∈ [1.5, 10]
- 4-tier risk classification for portfolio recommendations
"""

# ============================================================================
# 1. QUESTIONNAIRE DEFINITION
# ============================================================================
# Format: (id, question_text, [(option_text, score)], dimension)

QUESTIONS = [
    # ---------- Capacity (4 questions, weight 1.0) ----------
    ("Q1", "What is your current age group?",
     [("Under 30", 1), ("30 to 45", 2), ("46 to 60", 3), ("Over 60", 4)],
     "Capacity"),
    ("Q2", "What percentage of your total savings can you commit to investing?",
     [("More than 50%", 1), ("25% to 50%", 2),
      ("10% to 25%", 3), ("Less than 10%", 4)],
     "Capacity"),
    ("Q3", "Do you have an emergency fund covering your living expenses?",
     [("Yes, more than 12 months", 1), ("Yes, 6 to 12 months", 2),
      ("Yes, 3 to 6 months", 3), ("No, less than 3 months", 4)],
     "Capacity"),
    ("Q4", "Which best describes your current income situation?",
     [("Stable salary plus other passive income", 1),
      ("Stable salary only", 2),
      ("Variable income (commission, freelance)", 3),
      ("No regular income", 4)],
     "Capacity"),

    # ---------- Horizon (3 questions, weight 1.0) ----------
    ("Q5", "How long do you plan to keep this money invested?",
     [("More than 10 years", 1), ("5 to 10 years", 2),
      ("3 to 5 years", 3), ("Less than 3 years", 4)],
     "Horizon"),
    ("Q6", "When might you need to withdraw more than 30% of this investment?",
     [("Not in the foreseeable future", 1),
      ("In 5+ years for a major purchase", 2),
      ("In 2 to 5 years", 3),
      ("Within the next 2 years", 4)],
     "Horizon"),
    ("Q7", "What is the primary goal of this investment?",
     [("Long-term wealth accumulation / retirement (20+ years)", 1),
      ("Major future expense in 5-10 years", 2),
      ("Supplementing income within 5 years", 3),
      ("Capital preservation with modest growth", 4)],
     "Horizon"),

    # ---------- Tolerance (5 questions, weight 1.4) ----------
    ("Q8", "If your portfolio dropped 20% in one year, you would:",
     [("Buy more — it's a great opportunity", 1),
      ("Hold and wait for recovery", 2),
      ("Sell some to reduce further losses", 3),
      ("Sell everything immediately", 4)],
     "Tolerance"),
    ("Q9", "Imagine two investment options. Which would you choose?",
     [("50% chance to gain 30%, 50% chance to lose 10%", 1),
      ("50% chance to gain 20%, 50% chance to lose 5%", 2),
      ("Guaranteed 5% return", 3),
      ("Guaranteed 2% return with capital protection", 4)],
     "Tolerance"),
    ("Q10", "Which return-volatility profile appeals most over 10 years?",
     [("Average 12% return, swings of ±25% per year", 1),
      ("Average 8% return, swings of ±15% per year", 2),
      ("Average 5% return, swings of ±7% per year", 3),
      ("Average 3% return, very stable", 4)],
     "Tolerance"),
    ("Q11", "How would you feel if your portfolio underperformed the market "
            "by 10% for two consecutive years?",
     [("Confident — long-term strategies have rough patches", 1),
      ("Slightly concerned but would stay the course", 2),
      ("Anxious and would consider rebalancing", 3),
      ("Would lose faith and exit the strategy", 4)],
     "Tolerance"),
    ("Q12", "What does 'risk' mean to you in the context of investing?",
     [("Opportunity for higher returns", 1),
      ("Necessary trade-off for growth", 2),
      ("Possibility of losing some money", 3),
      ("Possibility of losing everything", 4)],
     "Tolerance"),

    # ---------- Knowledge (3 questions, weight 0.6) ----------
    ("Q13", "How would you rate your investment experience?",
     [("5+ years of active investing across multiple asset classes", 1),
      ("2 to 5 years with stocks or funds", 2),
      ("Less than 2 years, limited products", 3),
      ("No prior investment experience", 4)],
     "Knowledge"),
    ("Q14", "Which of these investment concepts are you familiar with?",
     [("All of: diversification, Sharpe ratio, efficient frontier, rebalancing", 1),
      ("Most of them", 2),
      ("Only diversification and basic asset allocation", 3),
      ("None of these terms", 4)],
     "Knowledge"),
    ("Q15", "Which statement about market behavior do you most agree with?",
     [("Markets reward patient long-term investors despite volatility", 1),
      ("Markets generally trend upward but with significant cycles", 2),
      ("Markets are unpredictable and risky", 3),
      ("Markets are essentially gambling", 4)],
     "Knowledge"),
]


# ============================================================================
# 2. SCORING WEIGHTS BY DIMENSION
# ============================================================================
DIMENSION_WEIGHTS = {
    "Capacity":  1.0,   # Objective financial capacity
    "Horizon":   1.0,   # Time available
    "Tolerance": 1.4,   # Psychological — most influential per behavioral finance
    "Knowledge": 0.6,   # Lack of knowledge ≠ should be high A
}


# ============================================================================
# 3. SCORING FUNCTION
# ============================================================================
def compute_risk_aversion(answers: dict) -> dict:
    """
    Compute risk aversion A from questionnaire answers.

    Args:
        answers: {question_id: option_text} mapping
                 e.g., {"Q1": "Under 30", "Q2": "More than 50%", ...}

    Returns:
        dict with: total_score, dimension_scores, A, risk_tier
    """
    # Build lookup: question_id -> (options_dict, dimension)
    q_lookup = {qid: (dict(opts), dim) for qid, _, opts, dim in QUESTIONS}

    # Compute weighted score per dimension
    dim_scores = {"Capacity": 0, "Horizon": 0, "Tolerance": 0, "Knowledge": 0}
    for qid, choice in answers.items():
        opts, dim = q_lookup[qid]
        raw_score = opts[choice]
        dim_scores[dim] += raw_score

    # Apply dimension weights
    total = sum(dim_scores[d] * DIMENSION_WEIGHTS[d] for d in dim_scores)

    # Score range derivation:
    # min raw = 4×1 + 3×1 + 5×1 + 3×1 = 15 (each question = 1)
    # weighted min = 4×1.0 + 3×1.0 + 5×1.4 + 3×0.6 = 15.8
    # weighted max = 16×1.0 + 12×1.0 + 20×1.4 + 12×0.6 = 63.2
    S_MIN, S_MAX = 15.8, 63.2
    A_MIN, A_MAX = 1.5, 10.0

    A = A_MIN + (total - S_MIN) / (S_MAX - S_MIN) * (A_MAX - A_MIN)
    A = max(A_MIN, min(A_MAX, A))  # clamp

    # Discretize into 4 tiers
    if A < 3.5:
        tier = "🚀 Aggressive"
    elif A < 5.5:
        tier = "📈 Growth"
    elif A < 7.5:
        tier = "⚖️ Balanced"
    else:
        tier = "🛡️ Conservative"

    return {
        "total_score": round(total, 2),
        "dimension_scores": dim_scores,
        "A": round(A, 2),
        "risk_tier": tier,
    }


# ============================================================================
# 4. PERSONA DESCRIPTIONS (for the result page)
# ============================================================================
PERSONA_DESCRIPTIONS = {
    "🚀 Aggressive": (
        "You have a strong appetite for risk and a long investment horizon. "
        "Your portfolio will emphasize equities and growth assets to maximize "
        "long-term returns, accepting significant short-term volatility."
    ),
    "📈 Growth": (
        "You seek meaningful long-term growth and can tolerate moderate "
        "fluctuations. Your portfolio balances equities with some defensive "
        "assets to capture upside while smoothing returns."
    ),
    "⚖️ Balanced": (
        "You value stability but still want meaningful growth. Your portfolio "
        "weights equities and bonds roughly equally, suitable for medium-term "
        "goals with moderate volatility."
    ),
    "🛡️ Conservative": (
        "Capital preservation is your priority. Your portfolio emphasizes "
        "bonds and stable assets, with minimal equity exposure to protect "
        "against significant drawdowns."
    ),
}


# ============================================================================
# 5. SANITY CHECK / DEMO
# ============================================================================
if __name__ == "__main__":
    # Persona 1: Aggressive Alex
    alex = {
        "Q1": "Under 30", "Q2": "More than 50%",
        "Q3": "Yes, 6 to 12 months", "Q4": "Stable salary only",
        "Q5": "More than 10 years",
        "Q6": "Not in the foreseeable future",
        "Q7": "Long-term wealth accumulation / retirement (20+ years)",
        "Q8": "Buy more — it's a great opportunity",
        "Q9": "50% chance to gain 30%, 50% chance to lose 10%",
        "Q10": "Average 12% return, swings of ±25% per year",
        "Q11": "Confident — long-term strategies have rough patches",
        "Q12": "Opportunity for higher returns",
        "Q13": "2 to 5 years with stocks or funds",
        "Q14": "Most of them",
        "Q15": "Markets reward patient long-term investors despite volatility",
    }

    # Persona 3: Conservative Mr. Tan
    tan = {qid: opts[-1][0] for qid, _, opts, _ in QUESTIONS}  # all worst-case

    for name, ans in [("Alex", alex), ("Mr. Tan", tan)]:
        result = compute_risk_aversion(ans)
        print(f"\n--- {name} ---")
        print(f"Dimension scores: {result['dimension_scores']}")
        print(f"Total weighted: {result['total_score']}")
        print(f"A = {result['A']}  →  {result['risk_tier']}")
