import warnings

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def forecast_arima(
    data: pd.DataFrame,
    column: str = "Close",
    steps: int = 1,
    order: tuple = (2, 1, 2),
) -> pd.Series:

    if column not in data.columns:
        raise ValueError(f"Column '{column}' not found in data.")

    series = (
        pd.to_numeric(data[column], errors="coerce")
        .dropna()
        .astype(float)
    )

    if len(series) < 30:
        raise ValueError(
            "At least 30 historical observations are required "
            "for ARIMA forecasting."
        )

    # ARIMA works better when we explicitly provide
    # a simple sequential index.
    series = pd.Series(
        series.values,
        index=pd.RangeIndex(len(series)),
        name=column,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        model = ARIMA(
            series,
            order=order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )

        fitted_model = model.fit()

        forecast = fitted_model.forecast(
            steps=steps
        )

    return pd.Series(
        forecast.values,
        name="ARIMA_Forecast"
    )
def calculate_forecast_signal(
    current_price: float,
    forecast_price: float,
    bullish_threshold: float = 0.005,
    bearish_threshold: float = -0.005,
) -> dict:
    """
    Convert a price forecast into a trading direction.

    bullish_threshold = +0.5%
    bearish_threshold = -0.5%
    """

    expected_return = (
        (forecast_price - current_price)
        / current_price
    )

    if expected_return >= bullish_threshold:
        direction = "BULLISH"

    elif expected_return <= bearish_threshold:
        direction = "BEARISH"

    else:
        direction = "NEUTRAL"

    return {
        "current_price": float(current_price),
        "forecast_price": float(forecast_price),
        "expected_return": float(expected_return),
        "expected_return_percent": float(
            expected_return * 100
        ),
        "direction": direction,
    }

def generate_rolling_arima_forecasts(
    data: pd.DataFrame,
    column: str = "Close",
    min_history: int = 60,
    order: tuple = (2, 1, 2),
) -> pd.DataFrame:
    """
    Generate one-step-ahead ARIMA forecasts using only
    historical data available before each trading day.

    This prevents look-ahead bias during backtesting.
    """

    if column not in data.columns:
        raise ValueError(f"Column '{column}' not found in data.")

    df = data.copy()

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    df.dropna(subset=[column], inplace=True)

    forecasts = [float("nan")] * len(df)

    for i in range(min_history, len(df)):
        historical_data = df[column].iloc[:i]

        try:
            model = ARIMA(
                historical_data,
                order=order,
            )

            fitted_model = model.fit()

            forecast = fitted_model.forecast(
                steps=1
            )

            forecasts[i] = float(forecast.iloc[0])

        except Exception:
            forecasts[i] = float("nan")

    df["ARIMA_Forecast"] = forecasts

    df["Forecast_Return"] = (
        (df["ARIMA_Forecast"] - df[column])
        / df[column]
    )

    df["Forecast_Direction"] = "NEUTRAL"

    df.loc[
        df["Forecast_Return"] >= 0.005,
        "Forecast_Direction"
    ] = "BULLISH"

    df.loc[
        df["Forecast_Return"] <= -0.005,
        "Forecast_Direction"
    ] = "BEARISH"

    return df