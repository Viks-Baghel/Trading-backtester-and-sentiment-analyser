import pandas as pd

from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


def run_strategy_comparison(
    technical_data: pd.DataFrame,
    sentiment_data: pd.DataFrame,
    hybrid_data: pd.DataFrame,
    ai_hybrid_data: pd.DataFrame,
    initial_capital: float = 100000.0,
) -> pd.DataFrame:
    """
    Compare multiple strategies using the same capital.

    Strategies:
        Buy & Hold
        Technical
        Sentiment
        Technical + Sentiment
        AI Hybrid
    """

    results = []

    # =========================================================
    # BUY AND HOLD
    # =========================================================

    if not technical_data.empty:

        first_price = float(
            technical_data["Close"].iloc[0]
        )

        last_price = float(
            technical_data["Close"].iloc[-1]
        )

        buy_hold_return = (
            (last_price - first_price)
            / first_price
        ) * 100.0

        results.append(
            {
                "strategy": "Buy & Hold",
                "total_return": buy_hold_return,
                "sharpe_ratio": None,
                "max_drawdown": None,
                "win_rate": None,
                "total_trades": 1,
            }
        )

    # =========================================================
    # HELPER
    # =========================================================

    def evaluate(
        name: str,
        data: pd.DataFrame,
    ):

        if data.empty:
            return

        result_data, trades = run_backtest(
            data,
            initial_capital=initial_capital,
        )

        metrics = calculate_metrics(
            result_data,
            trades,
            initial_capital=initial_capital,
        )

        results.append(
            {
                "strategy": name,
                "total_return": metrics["total_return"],
                "sharpe_ratio": metrics["sharpe_ratio"],
                "max_drawdown": metrics["max_drawdown"],
                "win_rate": metrics["win_rate"],
                "total_trades": metrics["total_trades"],
            }
        )

    # =========================================================
    # STRATEGIES
    # =========================================================

    evaluate(
        "Technical",
        technical_data,
    )

    evaluate(
        "Sentiment",
        sentiment_data,
    )

    evaluate(
        "Technical + Sentiment",
        hybrid_data,
    )

    evaluate(
        "AI Hybrid",
        ai_hybrid_data,
    )

    return pd.DataFrame(results)