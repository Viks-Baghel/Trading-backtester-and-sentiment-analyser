import pandas as pd
import numpy as np

from backend.app.services.data_loader import (
    load_market_data,
)

from backend.app.services.forecasting_service import (
    forecast_arima,
)

from backend.app.services.lstm_service import (
    forecast_lstm,
)

from backend.app.services.forecast_evaluation import (
    calculate_forecast_metrics,
)


SYMBOL = "RELIANCE.NS"

START_DATE = "2026-01-01"
END_DATE = "2026-09-05"

MIN_HISTORY = 60


print("\n")
print("=" * 70)
print("ARIMA vs LSTM FORECAST COMPARISON")
print("=" * 70)


data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

data = data.reset_index(drop=True)

print(f"\nPrice rows: {len(data)}")


arima_actual = []
arima_predictions = []

lstm_actual = []
lstm_predictions = []


for i in range(
    MIN_HISTORY,
    len(data),
):

    historical_data = data.iloc[:i]

    actual_price = float(
        data.iloc[i]["Close"]
    )

    # -------------------------
    # ARIMA
    # -------------------------

    try:

        arima_forecast = forecast_arima(
            historical_data,
            column="Close",
            steps=1,
        )

        arima_price = float(
            arima_forecast.iloc[0]
        )

        if np.isfinite(arima_price):

            arima_actual.append(
                actual_price
            )

            arima_predictions.append(
                arima_price
            )

    except Exception:

        pass


    # -------------------------
    # LSTM
    # -------------------------

    try:

        lstm_price = forecast_lstm(
            historical_data,
            column="Close",
            lookback=20,
            epochs=10,
        )

        if np.isfinite(lstm_price):

            lstm_actual.append(
                actual_price
            )

            lstm_predictions.append(
                lstm_price
            )

    except Exception:

        pass


print("\nARIMA samples:", len(
    arima_predictions
))

print("LSTM samples:", len(
    lstm_predictions
))


# -------------------------
# Metrics
# -------------------------

arima_metrics = calculate_forecast_metrics(
    pd.Series(arima_actual),
    pd.Series(arima_predictions),
)

lstm_metrics = calculate_forecast_metrics(
    pd.Series(lstm_actual),
    pd.Series(lstm_predictions),
)


print("\n")
print("=" * 70)
print("ARIMA RESULTS")
print("=" * 70)

for key, value in arima_metrics.items():

    print(
        f"{key}: {value:.4f}"
        if isinstance(value, float)
        else f"{key}: {value}"
    )


print("\n")
print("=" * 70)
print("LSTM RESULTS")
print("=" * 70)

for key, value in lstm_metrics.items():

    print(
        f"{key}: {value:.4f}"
        if isinstance(value, float)
        else f"{key}: {value}"
    )


print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)


if lstm_metrics["rmse"] < arima_metrics["rmse"]:

    print("Winner: LSTM")

else:

    print("Winner: ARIMA")