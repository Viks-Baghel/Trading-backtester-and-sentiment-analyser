import pandas as pd

from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.news_service import fetch_news, news_to_dataframe
from backend.app.services.sentiment_service import (
    analyze_news_dataframe,
    aggregate_daily_sentiment,
)
from backend.app.services.data_alignment import align_price_and_sentiment
from backend.app.services.forecasting_service import forecast_arima
from backend.app.services.signals import generate_ai_hybrid_signals
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


SYMBOL = "RELIANCE.NS"
START_DATE = "2026-01-01"
END_DATE = "2026-09-05"
INITIAL_CAPITAL = 100000.0


print("\n")
print("=" * 60)
print("AI-AUGMENTED HYBRID BACKTEST")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD PRICE DATA
# ---------------------------------------------------------

price_data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print(f"\nPrice rows: {len(price_data)}")


# ---------------------------------------------------------
# 2. LOAD NEWS
# ---------------------------------------------------------

news_items = fetch_news(
    SYMBOL,
    count=5,
)

news_df = news_to_dataframe(news_items)

print(f"News articles: {len(news_df)}")


# ---------------------------------------------------------
# 3. FINBERT SENTIMENT
# ---------------------------------------------------------

if not news_df.empty:

    news_df = analyze_news_dataframe(news_df)

    daily_sentiment = aggregate_daily_sentiment(
        news_df
    )

else:

    daily_sentiment = pd.DataFrame(
        columns=[
            "news_date",
            "sentiment_score",
            "news_count",
        ]
    )


# ---------------------------------------------------------
# 4. ALIGN NEWS WITH TRADING DAYS
# ---------------------------------------------------------

combined = align_price_and_sentiment(
    price_data,
    daily_sentiment,
)


# ---------------------------------------------------------
# 5. TECHNICAL INDICATORS
# ---------------------------------------------------------

combined = add_indicators(combined)


print(f"Rows after indicators: {len(combined)}")


# ---------------------------------------------------------
# 6. ROLLING ARIMA FORECAST
# ---------------------------------------------------------

forecast_values = []

minimum_history = 30

for i in range(len(combined)):

    if i < minimum_history:

        forecast_values.append(float("nan"))
        continue

    historical_data = combined.iloc[:i]

    current_price = float(
        combined.iloc[i]["Close"]
    )

    try:

        forecast = forecast_arima(
            historical_data,
            column="Close",
            steps=1,
        )

        forecast_price = float(
            forecast.iloc[0]
        )

        forecast_values.append(
            forecast_price
        )

    except Exception:

        forecast_values.append(
            float("nan")
        )


combined["forecast_price"] = forecast_values


# ---------------------------------------------------------
# 7. REMOVE ROWS WITHOUT FORECAST
# ---------------------------------------------------------

combined.dropna(
    subset=["forecast_price"],
    inplace=True,
)


print(
    f"Rows with valid forecasts: {len(combined)}"
)


# ---------------------------------------------------------
# 8. GENERATE AI HYBRID SIGNALS
# ---------------------------------------------------------

combined = generate_ai_hybrid_signals(
    combined,
)


print("\nSignal distribution:")
print(
    combined["Signal"].value_counts()
)


# ---------------------------------------------------------
# 9. DISPLAY AI SIGNAL EVENTS
# ---------------------------------------------------------

signal_events = combined[
    combined["Signal"] != "HOLD"
]

print("\nAI SIGNAL EVENTS")
print("=" * 60)

for index, row in signal_events.iterrows():

    print(
        f"{index.date()} | "
        f"Close: ₹{row['Close']:.2f} | "
        f"Sentiment: {row['sentiment_score']:.3f} | "
        f"Forecast: ₹{row['forecast_price']:.2f} | "
        f"Expected: "
        f"{row['forecast_expected_return'] * 100:.2f}% | "
        f"Tech: {row['technical_score']:.2f} | "
        f"AI Score: {row['ai_hybrid_score']:.3f} | "
        f"Signal: {row['Signal']}"
    )


# ---------------------------------------------------------
# 10. RUN BACKTEST
# ---------------------------------------------------------

result_data, trades = run_backtest(
    combined,
    initial_capital=INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 11. CALCULATE METRICS
# ---------------------------------------------------------

metrics = calculate_metrics(
    result_data["Portfolio_Value"],
    trades,
    INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 12. PRINT RESULTS
# ---------------------------------------------------------

print("\n")
print("=" * 60)
print("AI HYBRID BACKTEST RESULT")
print("=" * 60)

for key, value in metrics.items():

    if isinstance(value, float):

        if "return" in key or "drawdown" in key or "rate" in key:

            print(
                f"{key}: {value:.2f}%"
            )

        else:

            print(
                f"{key}: {value:.4f}"
            )

    else:

        print(
            f"{key}: {value}"
        )


print("\nTRADES")
print("=" * 60)

for trade in trades:

    print(trade)