"""
extract_from_excel.py
Extract μ, Σ, prices, and fund info from the all-in-one Excel file.

Place the Excel file in the same directory, then run:
    python extract_from_excel.py

Outputs to data/:
    - fund_info.csv
    - mu.csv, mu_annualized.csv
    - sigma.csv, sigma_annualized.csv
    - prices.csv, returns.csv
"""
import openpyxl
import pandas as pd
from pathlib import Path

# ---- Config ----
EF_FILE = "EfficientFrontier_4_.xlsm"   # 👈 updated to latest
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


wb = openpyxl.load_workbook(EF_FILE, data_only=True)

# ---- 1. Fund names (from Prices sheet row 2, then tickers from row 3) ----
ws_p = wb["Prices"]
fund_names_full = [ws_p.cell(row=2, column=c).value for c in range(2, 12)]
tickers = [ws_p.cell(row=3, column=c).value for c in range(2, 12)]

# ---- 2. Extract prices (rows 4 onwards, column A = month index, B-K = fund prices) ----
prices_rows = []
for row_idx in range(4, ws_p.max_row + 1):
    month_idx = ws_p.cell(row=row_idx, column=1).value
    if month_idx is None:
        break
    prices = [ws_p.cell(row=row_idx, column=c).value for c in range(2, 12)]
    prices_rows.append([month_idx] + prices)

prices_df = pd.DataFrame(prices_rows, columns=["month"] + tickers)
prices_df = prices_df.set_index("month")
prices_df.to_csv(DATA_DIR / "prices.csv")

# ---- 3. Build fund_info.csv ----
# Asset class mapping (updated: Fund_06 is now JPM Income, a bond fund)
asset_class_map = {
    "Franklin Technology":             ("Equity", "Global Tech"),
    "Allianz US Equity":               ("Equity", "US"),
    "BlackRock World Healthscience":   ("Equity", "Global Healthcare"),
    "abrdn India Opportunities":       ("Equity", "India"),
    "Amova Singapore Dividend":        ("Equity", "Singapore"),
    "JPM Income":                      ("Bond", "Global"),
    "Amova Japan Equity":              ("Equity", "Japan"),
    "Allianz Oriental Income":         ("Multi-Asset", "Asia"),
    "First Sentier Bridge":            ("Balanced", "Asia"),
    "United SGD Fund":                 ("Bond", "SGD"),
    "LionGlobal Short Duration Bond":  ("Bond", "SGD"),
}

fund_info_rows = []
for ticker, name in zip(tickers, fund_names_full):
    cls, region = asset_class_map.get(name, ("Unknown", "Unknown"))
    fund_info_rows.append([ticker, name, cls, region])

fund_info = pd.DataFrame(fund_info_rows,
                         columns=["ticker", "name", "asset_class", "region"])
fund_info.to_csv(DATA_DIR / "fund_info.csv", index=False)


# ---- 4. Extract μ and Σ from Stats sheet ----
ws_s = wb["Stats"]

# μ monthly: rows 4-13, column B
mu_monthly = [ws_s.cell(row=r, column=2).value for r in range(4, 14)]

# Σ monthly: rows 19-28, columns B-K
sigma_monthly = []
for row in range(19, 29):
    sigma_row = [ws_s.cell(row=row, column=c).value for c in range(2, 12)]
    sigma_monthly.append(sigma_row)

mu_df = pd.DataFrame({"ticker": tickers, "expected_return": mu_monthly})
mu_df.to_csv(DATA_DIR / "mu.csv", index=False)

sigma_df = pd.DataFrame(sigma_monthly, index=tickers, columns=tickers)
sigma_df.to_csv(DATA_DIR / "sigma.csv")

# Annualized versions
mu_ann = mu_df.copy()
mu_ann["expected_return"] = mu_ann["expected_return"] * 12
mu_ann.to_csv(DATA_DIR / "mu_annualized.csv", index=False)

(sigma_df * 12).to_csv(DATA_DIR / "sigma_annualized.csv")

# Returns for backtest
returns_df = prices_df.pct_change().dropna()
returns_df.to_csv(DATA_DIR / "returns.csv")


# ---- Summary ----
import numpy as np
print(f"✅ Extracted from {EF_FILE}")
print(f"\nFund list:")
for t, n in zip(tickers, fund_names_full):
    cls, _ = asset_class_map.get(n, ("?", "?"))
    print(f"  {t}: {n} [{cls}]")

print(f"\nSanity checks:")
print(f"  Prices shape: {prices_df.shape}")
print(f"  μ (monthly): min={min(mu_monthly):.4f}, max={max(mu_monthly):.4f}")
print(f"  μ (annualized): min={min(mu_monthly)*12:.4f}, max={max(mu_monthly)*12:.4f}")
eigvals = np.linalg.eigvalsh(np.array(sigma_monthly))
print(f"  Σ min eigenvalue: {eigvals.min():.6f} (should be > 0)")
