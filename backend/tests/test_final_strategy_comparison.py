import pandas as pd


results = [
    {
        "Strategy": "Buy & Hold",
        "Final Value": 95748.54,
        "Return %": -4.25,
        "Sharpe": None,
        "Max Drawdown %": None,
        "Win Rate %": None,
        "Trades": 1,
    },
    {
        "Strategy": "Technical",
        "Final Value": 93724.01,
        "Return %": -6.28,
        "Sharpe": -2.4040,
        "Max Drawdown %": -6.28,
        "Win Rate %": 0.00,
        "Trades": 4,
    },
    {
        "Strategy": "Sentiment",
        "Final Value": 95773.60,
        "Return %": -4.23,
        "Sharpe": -0.3009,
        "Max Drawdown %": -13.92,
        "Win Rate %": 0.00,
        "Trades": 1,
    },
    {
        "Strategy": "AI Hybrid + ARIMA",
        "Final Value": 86646.80,
        "Return %": -13.35,
        "Sharpe": -2.2639,
        "Max Drawdown %": -16.28,
        "Win Rate %": 33.33,
        "Trades": 3,
    },
    {
        "Strategy": "AI Hybrid + LSTM",
        "Final Value": 99542.50,
        "Return %": -0.46,
        "Sharpe": -0.0210,
        "Max Drawdown %": -4.53,
        "Win Rate %": 0.00,
        "Trades": 1,
    },
]


df = pd.DataFrame(results)


print("\n")
print("=" * 90)
print("FINAL DAY 3 — STRATEGY COMPARISON")
print("=" * 90)

print(
    df.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}",
    )
)


# ==========================================================
# BEST RESULTS
# ==========================================================

best_return = df.loc[
    df["Return %"].idxmax()
]

best_drawdown = df.dropna(
    subset=["Max Drawdown %"]
).loc[
    df.dropna(
        subset=["Max Drawdown %"]
    )["Max Drawdown %"].idxmax()
]

best_sharpe = df.dropna(
    subset=["Sharpe"]
).loc[
    df.dropna(
        subset=["Sharpe"]
    )["Sharpe"].idxmax()
]


print("\n")
print("=" * 90)
print("BEST RESULTS")
print("=" * 90)

print(
    f"Best Return: "
    f"{best_return['Strategy']} "
    f"({best_return['Return %']:.2f}%)"
)

print(
    f"Best Max Drawdown: "
    f"{best_drawdown['Strategy']} "
    f"({best_drawdown['Max Drawdown %']:.2f}%)"
)

print(
    f"Best Sharpe: "
    f"{best_sharpe['Strategy']} "
    f"({best_sharpe['Sharpe']:.4f})"
)


# ==========================================================
# CAPITAL COMPARISON
# ==========================================================

print("\n")
print("=" * 90)
print("CAPITAL COMPARISON")
print("=" * 90)

for _, row in df.iterrows():

    difference = (
        row["Final Value"] - 100000
    )

    print(
        f"{row['Strategy']:<22} "
        f"₹{row['Final Value']:>10.2f} "
        f"({difference:+.2f})"
    )