from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.news_service import (
    fetch_news,
    news_to_dataframe,
)
from backend.app.services.sentiment_service import (
    analyze_news_dataframe,
    aggregate_daily_sentiment,
)
from backend.app.services.data_alignment import (
    align_price_and_sentiment,
)
from backend.app.services.signals import (
    generate_hybrid_signals,
)
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


SYMBOL = "RELIANCE.NS"

START_DATE = "2026-01-01"
END_DATE = "2026-09-05"

INITIAL_CAPITAL = 100000.0


print("\n" + "=" * 60)
print("HYBRID STRATEGY BACKTEST")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD MARKET DATA
# ---------------------------------------------------------

print("\n1. Loading market data...")

price_data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print("Price rows:", len(price_data))


# ---------------------------------------------------------
# 2. ADD TECHNICAL INDICATORS
# ---------------------------------------------------------

# print("\n2. Adding technical indicators...")

# price_data = add_indicators(price_data)

# print(
#     "Indicators:",
#     [
#         "SMA_20",
#         "SMA_50",
#         "EMA_20",
#         "RSI",
#         "MACD",
#     ],
# )


# ---------------------------------------------------------
# 3. FETCH NEWS
# ---------------------------------------------------------

print("\n3. Fetching financial news...")

news = fetch_news(
    SYMBOL,
    count=20,
)

print("News articles:", len(news))

if not news:
    print("No news available.")
    raise SystemExit


# ---------------------------------------------------------
# 4. NEWS DATAFRAME
# ---------------------------------------------------------

news_df = news_to_dataframe(news)


# ---------------------------------------------------------
# 5. FINBERT
# ---------------------------------------------------------

print("\n4. Running FinBERT...")

news_df = analyze_news_dataframe(news_df)

print(
    news_df[
        [
            "headline",
            "sentiment_label",
            "sentiment_confidence",
            "sentiment_score",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 6. DAILY SENTIMENT
# ---------------------------------------------------------

print("\n5. Aggregating sentiment...")

daily_sentiment = aggregate_daily_sentiment(
    news_df
)

print(
    daily_sentiment.to_string(index=False)
)


# ---------------------------------------------------------
# 7. ALIGN PRICE + SENTIMENT
# ---------------------------------------------------------

print("\n6. Aligning price and sentiment...")

combined = align_price_and_sentiment(
    price_data,
    daily_sentiment,
)

print("\n7. Adding technical indicators...")

combined = add_indicators(combined)

print(
    "Indicators:",
    [
        "SMA_20",
        "SMA_50",
        "EMA_20",
        "RSI",
        "MACD",
    ],
)

print("Rows after indicators:", len(combined))

# ---------------------------------------------------------
# 8. GENERATE HYBRID SIGNALS
# ---------------------------------------------------------

print("\n8. Generating hybrid signals...")

combined = generate_hybrid_signals(
    combined,
    sentiment_column="sentiment_score",
    buy_sentiment_threshold=0.20,
    sell_sentiment_threshold=-0.20,
)


print("\nSignal distribution:")

print(
    combined["Signal"].value_counts()
)
print("\nSentiment events with technical indicators:")

sentiment_events = combined[
    combined["sentiment_score"] != 0
]

if not sentiment_events.empty:
    print(
        sentiment_events[
            [
                "Close",
                "SMA_20",
                "SMA_50",
                "RSI",
                "MACD",
                "MACD_SIGNAL",
                "sentiment_score",
                "technical_score",
                "sentiment_normalized",
                "hybrid_score",
                "Signal",
            ]
        ].to_string()
    )
else:
    print("No sentiment events found.")


# ---------------------------------------------------------
# 9. SHOW SIGNALS
# ---------------------------------------------------------

signal_rows = combined[
    combined["Signal"] != "HOLD"
]

if not signal_rows.empty:

    print("\nGenerated signals:")

    print(
        signal_rows[
            [
                "Close",
                "SMA_20",
                "SMA_50",
                "RSI",
                "MACD",
                "MACD_SIGNAL",
                "sentiment_score",
                "Signal",
            ]
        ].to_string()
    )

else:

    print("\nNo hybrid signals generated.")


# ---------------------------------------------------------
# 10. RUN BACKTEST
# ---------------------------------------------------------

print("\n9. Running hybrid backtest...")

backtest_data, trades = run_backtest(
    combined,
    initial_capital=INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 11. METRICS
# ---------------------------------------------------------

metrics = calculate_metrics(
    backtest_data["Portfolio_Value"],
    trades,
    INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 12. RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("HYBRID BACKTEST RESULT")
print("=" * 60)

for key, value in metrics.items():

    if isinstance(value, float):

        if (
            "return" in key
            or "drawdown" in key
            or "rate" in key
        ):
            print(f"{key}: {value:.2f}%")
        else:
            print(f"{key}: {value:.4f}")

    else:

        print(f"{key}: {value}")


# ---------------------------------------------------------
# 13. TRADES
# ---------------------------------------------------------

print("\nTRADES")
print("=" * 60)

if trades:

    for trade in trades:
        print(trade)

else:

    print("No trades generated.")