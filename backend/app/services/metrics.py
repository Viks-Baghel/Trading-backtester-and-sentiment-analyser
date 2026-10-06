import numpy as np
import pandas as pd


def calculate_metrics(
    portfolio: pd.Series,
    trades: list[dict],
    initial_capital: float,
) -> dict:

    final_value = float(portfolio.iloc[-1])

    total_return = (
        (final_value - initial_capital)
        / initial_capital
    ) * 100

    returns = portfolio.pct_change().dropna()

    if returns.std() != 0:
        sharpe_ratio = (
            np.sqrt(252)
            * returns.mean()
            / returns.std()
        )
    else:
        sharpe_ratio = 0.0

    running_max = portfolio.cummax()

    drawdown = (
        portfolio - running_max
    ) / running_max

    max_drawdown = drawdown.min() * 100

    completed_trades = [
        trade
        for trade in trades
        if trade["type"] == "SELL"
        and "profit_loss" in trade
    ]

    if completed_trades:

        winning_trades = [
            trade
            for trade in completed_trades
            if trade["profit_loss"] > 0
        ]

        win_rate = (
            len(winning_trades)
            / len(completed_trades)
        ) * 100

    else:
        win_rate = 0.0

    return {
        "initial_capital": initial_capital,
        "final_value": final_value,
        "total_return": total_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "total_trades": len(completed_trades),
    }