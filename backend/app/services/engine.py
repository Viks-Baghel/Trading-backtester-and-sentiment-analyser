import pandas as pd


def run_backtest(
    data: pd.DataFrame,
    initial_capital: float = 100000.0,
) -> tuple:
    """
    Run a simple long-only backtest.

    BUY:
        Opens a position when no position is currently held.

    SELL:
        Closes the position when a SELL signal is generated.

    If a position remains open at the end of the dataset,
    it is closed using the final available price.
    """

    df = data.copy()

    cash = float(initial_capital)

    position = 0
    entry_price = 0.0

    trades = []
    portfolio_values = []

    # =========================================================
    # BACKTEST LOOP
    # =========================================================

    for index, row in df.iterrows():

        price = float(row["Close"])
        signal = row.get("Signal", "HOLD")

        # -----------------------------------------------------
        # BUY
        # -----------------------------------------------------

        if signal == "BUY" and position == 0:

            quantity = int(
                cash / price
            )

            if quantity > 0:

                position = quantity
                entry_price = price

                cash -= (
                    quantity * price
                )

                trades.append(
                    {
                        "date": index,
                        "type": "BUY",
                        "price": price,
                        "quantity": quantity,

                        # Explainability
                        "signal_reason": row.get(
                            "signal_reason",
                            "BUY signal",
                        ),
                        "technical_direction": row.get(
                            "technical_direction",
                            None,
                        ),
                        "sentiment_direction": row.get(
                            "sentiment_direction",
                            None,
                        ),
                        "forecast_direction": row.get(
                            "forecast_direction",
                            None,
                        ),
                        "technical_score": row.get(
                            "technical_score",
                            None,
                        ),
                        "sentiment_score": row.get(
                            "sentiment_score",
                            None,
                        ),
                        "forecast_expected_return": row.get(
                            "forecast_expected_return",
                            None,
                        ),
                        "ai_hybrid_score": row.get(
                            "ai_hybrid_score",
                            None,
                        ),
                        "bullish_votes": row.get(
                            "bullish_votes",
                            None,
                        ),
                        "bearish_votes": row.get(
                            "bearish_votes",
                            None,
                        ),
                    }
                )

        # -----------------------------------------------------
        # SELL
        # -----------------------------------------------------

        elif signal == "SELL" and position > 0:

            cash += (
                position * price
            )

            profit_loss = (
                price - entry_price
            ) * position

            trades.append(
                {
                    "date": index,
                    "type": "SELL",
                    "price": price,
                    "quantity": position,
                    "profit_loss": profit_loss,
                    "reason": "SIGNAL",

                    # Explainability
                    "signal_reason": row.get(
                        "signal_reason",
                        "SELL signal",
                    ),
                    "technical_direction": row.get(
                        "technical_direction",
                        None,
                    ),
                    "sentiment_direction": row.get(
                        "sentiment_direction",
                        None,
                    ),
                    "forecast_direction": row.get(
                        "forecast_direction",
                        None,
                    ),
                    "technical_score": row.get(
                        "technical_score",
                        None,
                    ),
                    "sentiment_score": row.get(
                        "sentiment_score",
                        None,
                    ),
                    "forecast_expected_return": row.get(
                        "forecast_expected_return",
                        None,
                    ),
                    "ai_hybrid_score": row.get(
                        "ai_hybrid_score",
                        None,
                    ),
                    "bullish_votes": row.get(
                        "bullish_votes",
                        None,
                    ),
                    "bearish_votes": row.get(
                        "bearish_votes",
                        None,
                    ),
                }
            )

            position = 0
            entry_price = 0.0

        # -----------------------------------------------------
        # PORTFOLIO VALUE
        # -----------------------------------------------------

        portfolio_value = (
            cash
            + position * price
        )

        portfolio_values.append(
            portfolio_value
        )

    # =========================================================
    # CLOSE OPEN POSITION AT END
    # =========================================================

    if position > 0:

        final_date = df.index[-1]

        final_price = float(
            df.iloc[-1]["Close"]
        )

        cash += (
            position * final_price
        )

        profit_loss = (
            final_price - entry_price
        ) * position

        final_row = df.iloc[-1]

        trades.append(
            {
                "date": final_date,
                "type": "SELL",
                "price": final_price,
                "quantity": position,
                "profit_loss": profit_loss,
                "reason": "END_OF_BACKTEST",

                # Explainability
                "signal_reason": final_row.get(
                    "signal_reason",
                    "End of backtest",
                ),
                "technical_direction": final_row.get(
                    "technical_direction",
                    None,
                ),
                "sentiment_direction": final_row.get(
                    "sentiment_direction",
                    None,
                ),
                "forecast_direction": final_row.get(
                    "forecast_direction",
                    None,
                ),
                "technical_score": final_row.get(
                    "technical_score",
                    None,
                ),
                "sentiment_score": final_row.get(
                    "sentiment_score",
                    None,
                ),
                "forecast_expected_return": final_row.get(
                    "forecast_expected_return",
                    None,
                ),
                "ai_hybrid_score": final_row.get(
                    "ai_hybrid_score",
                    None,
                ),
                "bullish_votes": final_row.get(
                    "bullish_votes",
                    None,
                ),
                "bearish_votes": final_row.get(
                    "bearish_votes",
                    None,
                ),
            }
        )

        position = 0
        entry_price = 0.0

        if portfolio_values:
            portfolio_values[-1] = cash

    # =========================================================
    # STORE PORTFOLIO VALUE
    # =========================================================

    df["Portfolio_Value"] = portfolio_values

    return df, trades