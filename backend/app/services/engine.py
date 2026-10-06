import pandas as pd


def run_backtest(
    data: pd.DataFrame,
    initial_capital: float = 100000.0,
):
    df = data.copy()

    cash = initial_capital
    position = 0
    entry_price = 0.0

    trades = []
    portfolio_values = []

    for index, row in df.iterrows():

        price = float(row["Close"])
        signal = row["Signal"]

        # -----------------------------------------------------
        # BUY
        # -----------------------------------------------------

        if signal == "BUY" and position == 0:

            quantity = int(cash / price)

            if quantity > 0:

                position = quantity
                entry_price = price

                cash -= quantity * price

                trades.append({
                    "date": index,
                    "type": "BUY",
                    "price": price,
                    "quantity": quantity,
                })

        # -----------------------------------------------------
        # SELL
        # -----------------------------------------------------

        elif signal == "SELL" and position > 0:

            cash += position * price

            profit_loss = (
                price - entry_price
            ) * position

            trades.append({
                "date": index,
                "type": "SELL",
                "price": price,
                "quantity": position,
                "profit_loss": profit_loss,
            })

            position = 0
            entry_price = 0.0

        # -----------------------------------------------------
        # Portfolio value
        # -----------------------------------------------------

        portfolio_value = (
            cash + (position * price)
        )

        portfolio_values.append(
            portfolio_value
        )

    # ---------------------------------------------------------
    # CLOSE OPEN POSITION AT END OF BACKTEST
    # ---------------------------------------------------------

    if position > 0:

        final_date = df.index[-1]
        final_price = float(df.iloc[-1]["Close"])

        cash += position * final_price

        profit_loss = (
            final_price - entry_price
        ) * position

        trades.append({
            "date": final_date,
            "type": "SELL",
            "price": final_price,
            "quantity": position,
            "profit_loss": profit_loss,
            "reason": "END_OF_BACKTEST",
        })

        position = 0
        entry_price = 0.0

        # Make final portfolio value equal to realized cash
        portfolio_values[-1] = cash

    df["Portfolio_Value"] = portfolio_values

    return df, trades