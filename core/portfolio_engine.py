"""
portfolio_engine.py
Core portfolio optimization functions for the Robot Adviser.
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
    """GMVP with no-short constraint and optional concentration cap."""
    n = sigma.shape[0]
    w0 = np.ones(n) / n
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
    bounds = [(0.0, max_weight)] * n
    res = minimize(
        lambda w: w @ sigma @ w,
        w0, method="SLSQP", bounds=bounds, constraints=constraints,
        options={"ftol": 1e-10, "maxiter": 500},
    )
    return res.x


# ---------- 2. Efficient Frontier (with warm-start) ----------
def efficient_frontier(mu, sigma, n_points=50, allow_short=True, max_weight=1.0):
    """Generate (sigma, return, weights) tuples along the efficient frontier.

    Uses warm-start: sort target returns ascending, start each optimization
    from the previous solution. This avoids local minima when the data has
    highly asymmetric Sharpe ratios.
    """
    target_returns = np.sort(np.linspace(mu.min(), mu.max(), n_points))
    n = len(mu)
    frontier = []

    # Start from GMVP-ish point for the lowest target
    if allow_short:
        bounds = [(None, None)] * n
        w_init = gmvp_unconstrained(sigma)
    else:
        bounds = [(0.0, max_weight)] * n
        w_init = gmvp_no_short(sigma, max_weight=max_weight)

    w_current = w_init.copy()

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: w @ mu - t},
        ]

        # Try multi-start: current warm-start + uniform + GMVP
        best_res = None
        best_var = np.inf

        candidate_starts = [w_current, np.ones(n) / n, w_init]
        for w0 in candidate_starts:
            try:
                res = minimize(
                    lambda w: w @ sigma @ w,
                    w0, method="SLSQP", bounds=bounds, constraints=constraints,
                    options={"ftol": 1e-10, "maxiter": 500},
                )
                if res.success and res.fun < best_var:
                    best_var = res.fun
                    best_res = res
            except Exception:
                continue

        if best_res is not None:
            w_current = best_res.x
            port_var = best_res.x @ sigma @ best_res.x
            frontier.append((np.sqrt(port_var), target, best_res.x))

    return frontier


# ---------- 3. Optimal portfolio ----------
def optimal_portfolio(mu, sigma, A, allow_short=False, max_weight=0.30):
    """Maximize U = w·μ - (A/2)·wᵀΣw subject to Σw = 1."""
    n = len(mu)

    if allow_short:
        bounds = [(None, None)] * n
        w0_options = [np.ones(n) / n, gmvp_unconstrained(sigma)]
    else:
        bounds = [(0.0, max_weight)] * n
        w0_options = [np.ones(n) / n,
                      gmvp_no_short(sigma, max_weight=max_weight)]

    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)

    def neg_utility(w):
        return -(w @ mu - 0.5 * A * (w @ sigma @ w))

    best_u = -np.inf
    best_w = None
    for w0 in w0_options:
        res = minimize(neg_utility, w0, method="SLSQP",
                       bounds=bounds, constraints=constraints,
                       options={"ftol": 1e-10, "maxiter": 500})
        if res.success and -res.fun > best_u:
            best_u = -res.fun
            best_w = res.x

    w = best_w if best_w is not None else np.ones(n) / n
    ret = w @ mu
    vol = np.sqrt(w @ sigma @ w)
    util = ret - 0.5 * A * vol ** 2
    sharpe = ret / vol if vol > 0 else 0.0
    return {
        "weights": w, "return": ret, "volatility": vol,
        "utility": util, "sharpe": sharpe,
    }


# ---------- 4. Sanity check ----------
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

    print(f"--- Sanity check ({label}) ---\n")

    print("Testing frontier monotonicity (warm-start):")
    for cap in [1.0, 0.30]:
        f = efficient_frontier(mu, sigma, 50, allow_short=False, max_weight=cap)
        print(f"\n  cap={cap*100:.0f}%:")
        # Check monotonicity: σ should generally increase as we move up the efficient part
        w_gmvp = gmvp_no_short(sigma, max_weight=cap)
        gmvp_ret = w_gmvp @ mu
        eff = [p for p in f if p[1] >= gmvp_ret - 1e-6]
        eff_sorted = sorted(eff, key=lambda x: x[1])
        prev_vol = eff_sorted[0][0]
        violations = 0
        for sigma_p, mu_p, _ in eff_sorted[1:]:
            if sigma_p < prev_vol - 1e-4:
                violations += 1
            prev_vol = sigma_p
        print(f"    points: {len(eff)}, monotonicity violations: {violations}")
        print(f"    σ range (ann): [{eff_sorted[0][0]*np.sqrt(12)*100:.2f}%, "
              f"{eff_sorted[-1][0]*np.sqrt(12)*100:.2f}%]")
        print(f"    μ range (ann): [{eff_sorted[0][1]*12*100:.2f}%, "
              f"{eff_sorted[-1][1]*12*100:.2f}%]")
