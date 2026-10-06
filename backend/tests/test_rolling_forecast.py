from backend.app.services.data_loader import load_market_data
from backend.app.services.forecasting_service import (
    generate_rolling_arima_forecasts,
)


SYMBOL = "RELIANCE.NS"
START_DATE = "2026-01-01"
END_DATE = "2026-09-05"


print("\n============================================================")
print("ROLLING ARIMA FORECAST TEST")
print("============================================================")


print("\n1. Loading market data...")

data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print(f"Historical rows: {len(data)}")


print("\n2. Generating rolling ARIMA forecasts...")

forecasted_data = generate_rolling_arima_forecasts(
    data,
    column="Close",
    min_history=60,
)


valid_forecasts = forecasted_data[
    forecasted_data["ARIMA_Forecast"].notna()
]


print(
    f"Valid forecasts: {len(valid_forecasts)}"
)


print("\n3. Latest forecasts:")

print("============================================================")

for index, row in valid_forecasts.tail(10).iterrows():

    print(
        f"{index.date()} | "
        f"Close: ₹{row['Close']:.2f} | "
        f"Forecast: ₹{row['ARIMA_Forecast']:.2f} | "
        f"Expected: {row['Forecast_Return'] * 100:.2f}% | "
        f"Direction: {row['Forecast_Direction']}"
    )


print("\n============================================================")
print("ROLLING FORECAST SUMMARY")
print("============================================================")

latest = valid_forecasts.iloc[-1]

print(
    f"Latest Close: ₹{latest['Close']:.2f}"
)

print(
    f"ARIMA Forecast: ₹{latest['ARIMA_Forecast']:.2f}"
)

print(
    f"Expected Change: "
    f"{latest['Forecast_Return'] * 100:.2f}%"
)

print(
    f"Forecast Direction: "
    f"{latest['Forecast_Direction']}"
)