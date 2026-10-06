from backend.app.services.data_loader import load_market_data
from backend.app.services.forecasting_service import (
    forecast_arima,
    calculate_forecast_signal,
)


SYMBOL = "RELIANCE.NS"

START_DATE = "2026-01-01"
END_DATE = "2026-09-05"


print("\n" + "=" * 60)
print("ARIMA FORECAST TEST")
print("=" * 60)


# ---------------------------------------------------------
# 1. Load historical market data
# ---------------------------------------------------------

print("\n1. Loading market data...")

data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print("Historical rows:", len(data))


# ---------------------------------------------------------
# 2. Run ARIMA
# ---------------------------------------------------------

print("\n2. Running ARIMA...")

forecast = forecast_arima(
    data,
    column="Close",
    steps=5,
    order=(2, 1, 2),
)


# ---------------------------------------------------------
# 3. Display forecast
# ---------------------------------------------------------

print("\n3. Forecast:")
print("=" * 60)

for i, value in enumerate(forecast, start=1):

    print(
        f"Day +{i}: {float(value):.2f}"
    )


# ---------------------------------------------------------
# 4. Compare latest price
# ---------------------------------------------------------

latest_price = float(
    data["Close"].iloc[-1]
)

final_forecast = float(
    forecast.iloc[-1]
)
forecast_signal = calculate_forecast_signal(
    current_price=latest_price,
    forecast_price=final_forecast,
)

forecast_change = (
    (final_forecast - latest_price)
    / latest_price
) * 100


print("\n" + "=" * 60)
print("FORECAST SUMMARY")
print("=" * 60)

print(
    f"Latest Close: ₹{latest_price:.2f}"
)

print(
    f"Day +5 Forecast: ₹{final_forecast:.2f}"
)

print(
    f"Expected Change: {forecast_change:.2f}%"
)

print(
    f"Forecast Direction: "
    f"{forecast_signal['direction']}"
)