import pandas as pd

from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.news_service import fetch_news, news_to_dataframe
from backend.app.services.sentiment_service import (
    analyze_news_dataframe,
    aggregate_daily_sentiment,
)
from backend.app.services.data_alignment import align_price_and_sentiment
from backend.app.services.lstm_service import forecast_lstm
from backend.app.services.signals import generate_lstm_hybrid_signals
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


SYMBOL = "RELIANCE.NS"
START_DATE = "2026-01-01"
END_DATE = "2026-09-05"
INITIAL_CAPITAL = 100000.0


print("\n")
print("=" * 70)
print("LSTM-ENHANCED AI HYBRID BACKTEST")
print("=" * 70)


# ==========================================================
# 1. LOAD MARKET DATA
# ==========================================================

price_data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print(f"\nPrice rows: {len(price_data)}")


# ==========================================================
# 2. LOAD NEWS
# ==========================================================

news_items = fetch_news(
    SYMBOL,
    count=5,
)

news_df = news_to_dataframe(
    news_items
)

print(f"News articles: {len(news_df)}")


# ==========================================================
# 3. FINBERT SENTIMENT
# ==========================================================

if not news_df.empty:

    news_df = analyze_news_dataframe(
        news_df
    )

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


# ==========================================================
# 4. ALIGN PRICE + SENTIMENT
# ==========================================================

combined = align_price_and_sentiment(
    price_data,
    daily_sentiment,
)

combined = add_indicators(
    combined
)

print(
    f"Rows after indicators: {len(combined)}"
)


# ==========================================================
# 5. ROLLING LSTM FORECAST
# ==========================================================

forecast_values = []

minimum_history = 60

print("\nGenerating rolling LSTM forecasts...")
print("This may take some time.")


for i in range(len(combined)):

    if i < minimum_history:

        forecast_values.append(
            float("nan")
        )

        continue

    historical_data = combined.iloc[:i]

    try:

        forecast_price = forecast_lstm(
            historical_data,
            column="Close",
            lookback=30,
            epochs=50,
        )

        forecast_values.append(
            float(forecast_price)
        )

    except Exception as error:

        print(
            f"LSTM forecast failed at row {i}: "
            f"{error}"
        )

        forecast_values.append(
            float("nan")
        )


combined["lstm_forecast_price"] = (
    forecast_values
)


combined.dropna(
    subset=["lstm_forecast_price"],
    inplace=True,
)


print(
    f"Rows with valid LSTM forecasts: "
    f"{len(combined)}"
)


# ==========================================================
# 6. GENERATE LSTM HYBRID SIGNALS
# ==========================================================

combined = generate_lstm_hybrid_signals(
    combined
)


print("\n")
print("=" * 70)
print("SIGNAL DISTRIBUTION")
print("=" * 70)

print(
    combined["Signal"].value_counts()
)


# ==========================================================
# 7. DISPLAY SIGNAL EVENTS
# ==========================================================

signal_events = combined[
    combined["Signal"] != "HOLD"
]


print("\n")
print("=" * 70)
print("LSTM HYBRID SIGNAL EVENTS")
print("=" * 70)


for index, row in signal_events.iterrows():

    print(
        f"{index.date()} | "
        f"Close: ₹{row['Close']:.2f} | "
        f"Sentiment: "
        f"{row['sentiment_score']:.3f} | "
        f"LSTM: "
        f"₹{row['lstm_forecast_price']:.2f} | "
        f"Expected: "
        f"{row['lstm_expected_return'] * 100:.2f}% | "
        f"Technical: "
        f"{row['technical_direction']} | "
        f"Sentiment: "
        f"{row['sentiment_direction']} | "
        f"LSTM: "
        f"{row['lstm_direction']} | "
        f"Votes: "
        f"{row['bullish_votes']}/"
        f"{row['bearish_votes']} | "
        f"Signal: "
        f"{row['Signal']}"
    )


# ==========================================================
# 8. RUN BACKTEST
# ==========================================================

result_data, trades = run_backtest(
    combined,
    initial_capital=INITIAL_CAPITAL,
)


# ==========================================================
# 9. CALCULATE METRICS
# ==========================================================

metrics = calculate_metrics(
    result_data["Portfolio_Value"],
    trades,
    INITIAL_CAPITAL,
)


# ==========================================================
# 10. RESULTS
# ==========================================================

print("\n")
print("=" * 70)
print("LSTM HYBRID BACKTEST RESULTS")
print("=" * 70)

print(
    f"Initial Capital: "
    f"₹{metrics['initial_capital']:.2f}"
)

print(
    f"Final Value: "
    f"₹{metrics['final_value']:.2f}"
)

print(
    f"Total Return: "
    f"{metrics['total_return']:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{metrics['sharpe_ratio']:.4f}"
)

print(
    f"Maximum Drawdown: "
    f"{metrics['max_drawdown']:.2f}%"
)

print(
    f"Win Rate: "
    f"{metrics['win_rate']:.2f}%"
)

print(
    f"Completed Trades: "
    f"{metrics['total_trades']}"
)


# ==========================================================
# 11. EXPLAINABILITY
# ==========================================================

print("\n")
print("=" * 70)
print("TRADE EXPLAINABILITY")
print("=" * 70)


for trade in trades:

    print(
        f"{trade['date']} | "
        f"{trade['type']} | "
        f"Price: ₹{trade['price']:.2f}"
    )

    if "signal_reason" in trade:

        print(
            f"Reason: "
            f"{trade['signal_reason']}"
        )

    if "signal_explanation" in trade:

        print(
            f"Explanation: "
            f"{trade['signal_explanation']}"
        )

    print("-" * 50)