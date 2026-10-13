
import pandas as pd


def _get_value(row, key, default=None):
    """Return a default when a value is missing or NaN."""
    value = row.get(key, default)

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    return value


def _get_trade_metadata(row, action):
    """Preserve the actual strategy information attached to a signal."""
    reason = _get_value(row, "signal_reason", f"{action} signal")
    explanation = _get_value(row, "signal_explanation")

    if not explanation:
        technical = _get_value(row, "technical_direction", "unavailable")
        sentiment = _get_value(row, "sentiment_direction", "unavailable")
        forecast = _get_value(row, "forecast_direction", "unavailable")
        lstm = _get_value(row, "lstm_direction", "unavailable")

        explanation = (
            f"{reason}; technical={technical}; "
            f"sentiment={sentiment}; ARIMA={forecast}; LSTM={lstm}"
        )

    return {
        "signal_reason": str(reason),
        "signal_explanation": str(explanation),
        "technical_direction": _get_value(row, "technical_direction"),
        "sentiment_direction": _get_value(row, "sentiment_direction"),
        "forecast_direction": _get_value(row, "forecast_direction"),
        "lstm_direction": _get_value(row, "lstm_direction"),
        "technical_score": _get_value(row, "technical_score"),
        "sentiment_score": _get_value(row, "sentiment_score"),
        "forecast_expected_return": _get_value(
            row, "forecast_expected_return"
        ),
        "arima_expected_return": _get_value(row, "arima_expected_return"),
        "lstm_expected_return": _get_value(row, "lstm_expected_return"),
        "ai_hybrid_score": _get_value(row, "ai_hybrid_score"),
        "bullish_votes": _get_value(row, "bullish_votes"),
        "bearish_votes": _get_value(row, "bearish_votes"),
    }


def run_backtest(
    data: pd.DataFrame,
    initial_capital: float = 100000.0,
) -> tuple:
    """
    Run a long-only, all-in/all-out backtest.

    BUY:
        Opens a position when no position is held.

    SELL:
        Closes the current position.

    End of backtest:
        Closes any remaining position at the final available close.

    Note:
        This engine does not include brokerage, taxes, or slippage.
    """

    if data.empty:
        raise ValueError("Cannot run a backtest with empty market data.")

    if "Close" not in data.columns:
        raise ValueError("Market data must contain a Close column.")

    if initial_capital <= 0:
        raise ValueError("Initial capital must be greater than zero.")

    df = data.copy()

    cash = float(initial_capital)
    position = 0
    entry_price = 0.0

    trades = []
    portfolio_values = []

    for index, row in df.iterrows():
        price = float(row["Close"])

        if pd.isna(price) or price <= 0:
            raise ValueError(f"Invalid closing price at {index}.")

        signal = _get_value(row, "Signal", "HOLD")

        # BUY: invest available cash in whole shares.
        if signal == "BUY" and position == 0:
            quantity = int(cash // price)

            if quantity > 0:
                position = quantity
                entry_price = price
                cash -= quantity * price

                trades.append({
                    "date": index,
                    "type": "BUY",
                    "price": price,
                    "quantity": quantity,
                    "reason": "SIGNAL",
                    **_get_trade_metadata(row, "BUY"),
                })

        # SELL: close the open position.
        elif signal == "SELL" and position > 0:
            cash += position * price
            profit_loss = (price - entry_price) * position

            trades.append({
                "date": index,
                "type": "SELL",
                "price": price,
                "quantity": position,
                "profit_loss": profit_loss,
                "reason": "SIGNAL",
                **_get_trade_metadata(row, "SELL"),
            })

            position = 0
            entry_price = 0.0

        # Mark portfolio to market at each available close.
        portfolio_values.append(cash + position * price)

    # Close any remaining position at the final available close.
    if position > 0:
        final_date = df.index[-1]
        final_row = df.iloc[-1]
        final_price = float(final_row["Close"])

        cash += position * final_price
        profit_loss = (final_price - entry_price) * position

        metadata = _get_trade_metadata(final_row, "SELL")
        metadata["signal_reason"] = "END_OF_BACKTEST"
        metadata["signal_explanation"] = (
            "Position closed at the final available price because "
            "the backtest period ended; this was not a strategy SELL signal."
        )

        trades.append({
            "date": final_date,
            "type": "SELL",
            "price": final_price,
            "quantity": position,
            "profit_loss": profit_loss,
            "reason": "END_OF_BACKTEST",
            **metadata,
        })

        position = 0
        entry_price = 0.0

        if portfolio_values:
            portfolio_values[-1] = cash

    df["Portfolio_Value"] = portfolio_values

    return df, trades
