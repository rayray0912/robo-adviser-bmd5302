"""
Risk Assessment Questionnaire — aligned with team's Excel implementation.

10 questions, 5 risk-level classification (R1-R5), discrete A values.
Q1-Q5 weighted x1; Q6-Q10 weighted x2 (psychological factors weighted higher).

Score mapping replicates the IF-formulas in EfficientFrontier_4_.xlsm
Risk_Assessment sheet.
"""

# ---------------------------------------------------------------------------
# 10 questions
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "id": "Q1",
        "block": 1,  # Q1-Q5 weight 1
        "text": "What is your age?",
        "options": [
            ("A", "18 – 30",  5),
            ("B", "31 – 50",  4),
            ("C", "51 – 60",  2),
            ("D", "Above 60", 1),
        ],
    },
    {
        "id": "Q2",
        "block": 1,
        "text": "What is your annual household income (in SGD)?",
        "options": [
            ("A", "Below S$60,000",       1),
            ("B", "S$60,000 – 120,000",   2),
            ("C", "S$120,000 – 180,000",  3),
            ("D", "S$180,000 – 300,000",  4),
            ("E", "Above S$300,000",      5),
        ],
    },
    {
        "id": "Q3",
        "block": 1,
        "text": "What proportion of your annual household income can be used for financial investments?",
        "options": [
            ("A", "Less than 10%",  1),
            ("B", "10% to 25%",     2),
            ("C", "25% to 50%",     4),
            ("D", "More than 50%",  5),
        ],
    },
    {
        "id": "Q4",
        "block": 1,
        "text": "Which of the following best describes your current investment portfolio?",
        "options": [
            ("A", "Other than bank deposits and government bonds, I rarely invest in other financial products.", 1),
            ("B", "Most of my investments are in bank deposits and government bonds, with only a small portion in higher-risk products.", 2),
            ("C", "My assets are fairly diversified across deposits, bonds, fixed-income products, and equities/funds.", 4),
            ("D", "Most of my investments are in higher-risk products such as equities, funds, and derivatives.", 5),
        ],
    },
    {
        "id": "Q5",
        "block": 1,
        "text": "How many years of experience do you have investing in higher-risk products such as stocks, equity funds, foreign exchange, or derivatives?",
        "options": [
            ("A", "No experience",     1),
            ("B", "Less than 2 years", 2),
            ("C", "2 to 5 years",      3),
            ("D", "5 to 8 years",      4),
            ("E", "More than 8 years", 5),
        ],
    },
    {
        "id": "Q6",
        "block": 2,  # Q6-Q10 weight 2
        "text": "Which of the following best describes your investment attitude?",
        "options": [
            ("A", "I am highly risk-averse, do not want any loss of principal, and hope to obtain stable returns above bank deposits.", 1),
            ("B", "I prefer conservative investments, do not want any loss of principal, and am willing to accept lower returns.", 2),
            ("C", "I seek higher returns and capital growth, and am willing to bear limited losses.", 4),
            ("D", "I aim for the highest possible return and am willing to bear relatively large losses.", 5),
        ],
    },
    {
        "id": "Q7",
        "block": 2,
        "text": "In the following situation, which option would you choose?",
        "options": [
            ("A", "100% chance of receiving S$5,000 in cash",   1),
            ("B", "50% chance of receiving S$20,000 in cash",   2),
            ("C", "25% chance of receiving S$80,000 in cash",   4),
            ("D", "10% chance of receiving S$200,000 in cash",  5),
        ],
    },
    {
        "id": "Q8",
        "block": 2,
        "text": "What is your planned investment horizon?",
        "options": [
            ("A", "Less than 1 year",   1),
            ("B", "1 – 3 years",        2),
            ("C", "3 – 5 years",        4),
            ("D", "More than 5 years",  5),
        ],
    },
    {
        "id": "Q9",
        "block": 2,
        "text": "What is your investment objective?",
        "options": [
            ("A", "Capital preservation",   1),
            ("B", "Steady capital growth",  3),
            ("C", "Rapid capital growth",   5),
        ],
    },
    {
        "id": "Q10",
        "block": 2,
        "text": "If the value of your investment product fluctuates to the following extent, what is the maximum loss you can accept?",
        "options": [
            ("A", "No loss of principal, but returns fall short of expectations",  1),
            ("B", "A slight loss of principal",                                    2),
            ("C", "A loss of up to 10% of principal",                              3),
            ("D", "A loss of 20% – 50% of principal",                              4),
            ("E", "A loss of more than 50% of principal",                          5),
        ],
    },
]


# ---------------------------------------------------------------------------
# Risk-level classification (R1-R5) and A value mapping
# ---------------------------------------------------------------------------
# Score range: theoretical min = 15, max = 75
# Boundaries replicate Excel formula:
#   IF(N1<=27, R1, IF(N1<=39, R2, IF(N1<=51, R3, IF(N1<=63, R4, R5))))
RISK_TIERS = [
    # (label_short, label_full, lo, hi, A_value, color, emoji)
    ("R1", "Conservative",            15, 27, 8, "#1D3557", "🛡️"),
    ("R2", "Moderately Conservative", 28, 39, 6, "#457B9D", "⚖️"),
    ("R3", "Balanced",                40, 51, 4, "#F4A261", "📈"),
    ("R4", "Growth",                  52, 63, 2, "#E76F51", "📈"),
    ("R5", "Aggressive",              64, 75, 1, "#9D2226", "🚀"),
]


PERSONA_DESCRIPTIONS = {
    "R1": (
        "You are a **Conservative** investor. Capital preservation is your "
        "primary concern. Your portfolio will be heavily weighted toward "
        "low-volatility bond funds, with limited equity exposure to provide "
        "modest growth above inflation."
    ),
    "R2": (
        "You are a **Moderately Conservative** investor. You prefer stability "
        "but accept some equity exposure for modest growth. Your portfolio "
        "balances bonds with diversified equity holdings."
    ),
    "R3": (
        "You are a **Balanced** investor. You seek a measured trade-off "
        "between growth and stability. Your portfolio has roughly equal "
        "exposure to equities and defensive assets, optimised for long-term "
        "wealth accumulation with manageable volatility."
    ),
    "R4": (
        "You are a **Growth** investor. You prioritise capital appreciation "
        "and accept higher volatility for higher expected returns. Your "
        "portfolio is tilted heavily toward equities with selective "
        "diversification."
    ),
    "R5": (
        "You are an **Aggressive** investor. You target maximum long-term "
        "growth and have the capacity to weather significant short-term "
        "drawdowns. Your portfolio concentrates in high-return equity "
        "holdings."
    ),
}


# ---------------------------------------------------------------------------
# Scoring function
# ---------------------------------------------------------------------------
def compute_risk_aversion(answers: dict) -> dict:
    """
    Compute total weighted score, R-tier, and A value from answers.

    Args:
        answers: dict mapping question id (e.g. "Q1") to the option label
                 of the chosen answer (e.g. "B"). Either label-only ("B")
                 or full text matching one of the options is accepted.

    Returns:
        dict with keys:
            "total_score"   : int weighted score, range 15-75
            "block_scores"  : {"Block 1 (Q1-Q5)": int, "Block 2 (Q6-Q10)": int}
            "R"             : "R1" through "R5"
            "risk_tier_full": e.g. "Balanced"
            "risk_tier"     : e.g. "📈 Balanced"  (with emoji, for display)
            "A"             : int, one of {1, 2, 4, 6, 8}
            "color"         : hex string for tier display
    """
    block1_total = 0
    block2_total = 0

    for q in QUESTIONS:
        chosen = answers.get(q["id"])
        if chosen is None:
            raise ValueError(f"Missing answer for {q['id']}")

        # Find matching option (accept either short label "A" or full text)
        score = None
        for label, text, sc in q["options"]:
            if chosen == label or chosen == text:
                score = sc
                break
        if score is None:
            raise ValueError(f"Invalid answer for {q['id']}: {chosen}")

        if q["block"] == 1:
            block1_total += score
        else:
            block2_total += score

    total_score = block1_total + 2 * block2_total

    # Determine R tier
    R_label = "R5"
    full_name = "Aggressive"
    A_value = 1
    color = "#9D2226"
    emoji = "🚀"

    for label, full, lo, hi, A, c, em in RISK_TIERS:
        if total_score <= hi:
            R_label = label
            full_name = full
            A_value = A
            color = c
            emoji = em
            break

    return {
        "total_score": total_score,
        "block_scores": {
            "Block 1 (Q1–Q5)": block1_total,
            "Block 2 (Q6–Q10, ×2)": 2 * block2_total,
        },
        "R": R_label,
        "risk_tier_full": full_name,
        "risk_tier": f"{emoji} {full_name}",
        "A": A_value,
        "color": color,
    }


# ---------------------------------------------------------------------------
# Demo profiles for video / presentation
# ---------------------------------------------------------------------------
DEMO_PROFILES = {
    "Alex": {
        "label": "Alex",
        "age": 28,
        "description": "Software engineer, long horizon, high risk appetite.",
        "expected_R": "R5",
        "expected_tier": "Aggressive",
        "expected_A": 1,
        "answers": {
            "Q1": "A",   # 18-30        → 5
            "Q2": "C",   # 120-180k     → 3
            "Q3": "D",   # >50%         → 5
            "Q4": "D",   # high-risk    → 5
            "Q5": "D",   # 5-8 yrs      → 4
            "Q6": "D",   # max return   → 5
            "Q7": "D",   # 10% S$200k   → 5
            "Q8": "D",   # >5 years     → 5
            "Q9": "C",   # rapid growth → 5
            "Q10": "E",  # >50% loss OK → 5
        },
        # Total = (5+3+5+5+4) + 2*(5+5+5+5+5) = 22 + 50 = 72 → R5 → A=1
    },
    "Sarah": {
        "label": "Sarah",
        "age": 42,
        "description": "Mid-career manager with family, balanced outlook.",
        "expected_R": "R3",
        "expected_tier": "Balanced",
        "expected_A": 4,
        "answers": {
            "Q1": "B",   # 31-50      → 4
            "Q2": "C",   # 120-180k   → 3
            "Q3": "C",   # 25-50%     → 4
            "Q4": "C",   # diversified → 4
            "Q5": "C",   # 2-5 yrs    → 3
            "Q6": "C",   # higher returns, limited loss → 4
            "Q7": "B",   # 50% 20k    → 2
            "Q8": "C",   # 3-5 years  → 4
            "Q9": "B",   # steady     → 3
            "Q10": "C",  # up to 10% loss → 3
        },
        # Total = (4+3+4+4+3) + 2*(4+2+4+3+3) = 18 + 32 = 50 → R3 → A=4
    },
    "Mr. Tan": {
        "label": "Mr. Tan",
        "age": 60,
        "description": "Near-retirement, capital preservation priority.",
        "expected_R": "R1",
        "expected_tier": "Conservative",
        "expected_A": 8,
        "answers": {
            "Q1": "D",   # >60        → 1
            "Q2": "B",   # 60-120k    → 2
            "Q3": "A",   # <10%       → 1
            "Q4": "A",   # mostly cash/bonds → 1
            "Q5": "A",   # no exp     → 1
            "Q6": "A",   # highly risk-averse → 1
            "Q7": "A",   # 100% 5k    → 1
            "Q8": "B",   # 1-3 yrs    → 2
            "Q9": "A",   # preservation → 1
            "Q10": "B",  # slight loss → 2
        },
        # Total = (1+2+1+1+1) + 2*(1+1+2+1+2) = 6 + 14 = 20 → R1 → A=8
    },
}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Demo profile validation ===\n")
    for name, profile in DEMO_PROFILES.items():
        result = compute_risk_aversion(profile["answers"])
        ok = (result["R"] == profile["expected_R"]
              and result["A"] == profile["expected_A"])
        mark = "✓" if ok else "✗"
        print(f"{mark} {name}: total={result['total_score']}, "
              f"R={result['R']}, A={result['A']} "
              f"(expected R={profile['expected_R']}, A={profile['expected_A']})")
        print(f"   block scores: {result['block_scores']}")
        print()

    print("\n=== Excel example user (D,B,A,A,A,A,D,D,C,E) ===")
    excel_test = compute_risk_aversion({
        "Q1": "D", "Q2": "B", "Q3": "A", "Q4": "A", "Q5": "A",
        "Q6": "A", "Q7": "D", "Q8": "D", "Q9": "C", "Q10": "E",
    })
    print(f"Total = {excel_test['total_score']} (expected 48)")
    print(f"R = {excel_test['R']} (expected R3)")
    print(f"A = {excel_test['A']} (expected 4)")
