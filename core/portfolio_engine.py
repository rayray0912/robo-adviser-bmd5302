"""
portfolio_engine.py
Core portfolio optimization functions for the Robot Adviser.

Implements:
  - Global Minimum Variance Portfolio (GMVP)
  - Efficient Frontier (with / without short sales)
  - Optimal portfolio under utility U = r - σ²·A/2
  - Optional concentration cap (industry-standard diversification constraint)
"""

import numpy as np
from scipy.optimize import minimize


# ---------- 1. GMVP ----------
def gmvp_unconstrained(sigma: np.ndarray) -> np.ndarray:
    """Closed-form GMVP (allows short sales). w = Σ⁻¹·1 / (1ᵀ·Σ⁻¹·1)"""
    n = sigma.shape[0]
    ones = np.ones(n)
    inv_sigma = np.linalg.inv(sigma)
    w = inv_sigma @ ones / (ones @ inv_sigma @ ones)
    return w


def gmvp_no_short(sigma: np.ndarray, max_weight: float = 1.0) -> np.ndarray:
    """GMVP with no-short constraint (w_i ≥ 0) and optional concentration cap."""
    n = sigma.shape[0]
    w0 = np.ones(n) / n
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
    bounds = [(0.0, max_weight)] * n
    res = minimize(
        lambda w: w @ sigma @ w,
        w0, method="SLSQP", bounds=bounds, constraints=constraints,
    )
    return res.x


# ---------- 2. Efficient Frontier ----------
def efficient_frontier(mu, sigma, n_points=50, allow_short=True, max_weight=1.0):
    """Generate (sigma, return, weights) tuples along the efficient frontier."""
    target_returns = np.linspace(mu.min(), mu.max(), n_points)
    n = len(mu)
    frontier = []

    for target in target_returns:
        w0 = np.ones(n) / n
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: w @ mu - t},
        ]
        if allow_short:
            bounds = [(None, None)] * n
        else:
            bounds = [(0.0, max_weight)] * n
        res = minimize(
            lambda w: w @ sigma @ w,
            w0, method="SLSQP", bounds=bounds, constraints=constraints,
        )
        if res.success:
            port_var = res.x @ sigma @ res.x
            frontier.append((np.sqrt(port_var), target, res.x))
    return frontier


# ---------- 3. Optimal portfolio (utility maximization) ----------
def optimal_portfolio(mu, sigma, A, allow_short=False, max_weight=0.30):
    """
    Maximize U = w·μ - (A/2)·wᵀΣw   subject to Σw = 1.

    Args:
        mu: Nx1 expected return vector
        sigma: NxN covariance matrix
        A: risk aversion coefficient
        allow_short: if True, allow negative weights
        max_weight: upper bound on each weight (default 30%, industry standard).
                    Set to 1.0 to disable concentration cap.
    """
    n = len(mu)
    w0 = np.ones(n) / n
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)

    if allow_short:
        bounds = [(None, None)] * n
    else:
        bounds = [(0.0, max_weight)] * n

    def neg_utility(w):
        return -(w @ mu - 0.5 * A * (w @ sigma @ w))

    res = minimize(neg_utility, w0, method="SLSQP",
                   bounds=bounds, constraints=constraints)
    w = res.x
    ret = w @ mu
    vol = np.sqrt(w @ sigma @ w)
    util = ret - 0.5 * A * vol ** 2
    sharpe = ret / vol if vol > 0 else 0.0
    return {
        "weights": w, "return": ret, "volatility": vol,
        "utility": util, "sharpe": sharpe,
    }


# ---------- 4. Quick sanity check ----------
if __name__ == "__main__":
    import pandas as pd

    try:
        mu = pd.read_csv("data/mu.csv", index_col=0)["expected_return"].values
        sigma = pd.read_csv("data/sigma.csv", index_col=0).values
        label = "real data"
    except FileNotFoundError:
        np.random.seed(0)
        n = 10
        mu = np.random.uniform(0.02, 0.12, n) / 12
        A_rand = np.random.randn(n, n)
        sigma = A_rand @ A_rand.T / 1000
        label = "synthetic"

    print(f"--- Sanity check ({label}) ---")
    print(f"GMVP (short): σ = "
          f"{np.sqrt(gmvp_unconstrained(sigma)@sigma@gmvp_unconstrained(sigma)):.4f}")
    print(f"GMVP (no short, 30% cap): σ = "
          f"{np.sqrt(gmvp_no_short(sigma, 0.3)@sigma@gmvp_no_short(sigma, 0.3)):.4f}")

    print("\nOptimal under utility (with 30% cap):")
    for A in [1.5, 3.5, 5.5, 7.5, 10.0]:
        r = optimal_portfolio(mu, sigma, A, max_weight=0.30)
        top = sorted(enumerate(r['weights']), key=lambda x: -x[1])[:5]
        top_str = ', '.join([f'F{i+1:02d}={w*100:.0f}%' for i, w in top if w > 0.01])
        ann_ret = r['return'] * 12 * 100
        ann_vol = r['volatility'] * np.sqrt(12) * 100
        print(f"  A={A:.1f}: ret(ann)={ann_ret:5.2f}%, vol(ann)={ann_vol:5.2f}%")
        print(f"         {top_str}")
