import pandas as pd

from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


SYMBOL = "RELIANCE.NS"
START_DATE = "2026-01-01"
END_DATE = "2026-09-05"
INITIAL_CAPITAL = 100000.0


print("\n")
print("=" * 80)
print("DAY 3 — STRATEGY COMPARISON")
print("=" * 80)


# ==========================================================
# LOAD DATA
# ==========================================================

data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

data = add_indicators(data)

print(f"\nPrice rows: {len(data)}")


# ==========================================================
# BUY & HOLD
# ==========================================================

buy_price = float(data.iloc[0]["Close"])
final_price = float(data.iloc[-1]["Close"])

buy_hold_value = (
    INITIAL_CAPITAL
    * final_price
    / buy_price
)

buy_hold_return = (
    (buy_hold_value - INITIAL_CAPITAL)
    / INITIAL_CAPITAL
) * 100


# ==========================================================
# STRATEGY RESULTS
# ==========================================================

strategies = []


def add_result(
    name,
    final_value,
    total_return,
    sharpe,
    drawdown,
    win_rate,
    trades,
):

    strategies.append(
        {
            "Strategy": name,
            "Final Value": final_value,
            "Return %": total_return,
            "Sharpe": sharpe,
            "Max Drawdown %": drawdown,
            "Win Rate %": win_rate,
            "Trades": trades,
        }
    )


add_result(
    "Buy & Hold",
    buy_hold_value,
    buy_hold_return,
    None,
    None,
    None,
    1,
)


# ==========================================================
# TECHNICAL STRATEGY
# ==========================================================

from backend.app.services.signals import (
    generate_technical_signals,
)

technical_data = generate_technical_signals(
    data
)

technical_result, technical_trades = run_backtest(
    technical_data,
    INITIAL_CAPITAL,
)

technical_metrics = calculate_metrics(
    technical_result["Portfolio_Value"],
    technical_trades,
    INITIAL_CAPITAL,
)

add_result(
    "Technical",
    technical_metrics["final_value"],
    technical_metrics["total_return"],
    technical_metrics["sharpe_ratio"],
    technical_metrics["max_drawdown"],
    technical_metrics["win_rate"],
    technical_metrics["total_trades"],
)


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

results = pd.DataFrame(
    strategies
)

print("\n")
print("=" * 80)
print("COMPARISON RESULTS")
print("=" * 80)

print(
    results.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


# ==========================================================
# BEST STRATEGY
# ==========================================================

best_strategy = results.loc[
    results["Return %"].idxmax()
]

print("\n")
print("=" * 80)
print("BEST RETURN")
print("=" * 80)

print(
    f"Strategy: "
    f"{best_strategy['Strategy']}"
)

print(
    f"Return: "
    f"{best_strategy['Return %']:.2f}%"
)

print(
    f"Final Value: "
    f"₹{best_strategy['Final Value']:.2f}"
)