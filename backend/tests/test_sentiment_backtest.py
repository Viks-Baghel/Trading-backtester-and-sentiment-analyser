from backend.app.services.data_loader import load_market_data
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
    generate_sentiment_signals,
)
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


SYMBOL = "RELIANCE.NS"

START_DATE = "2026-07-01"
END_DATE = "2026-09-05"

INITIAL_CAPITAL = 100000.0


print("\n" + "=" * 60)
print("SENTIMENT STRATEGY BACKTEST")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD PRICE DATA
# ---------------------------------------------------------

print("\n1. Loading market data...")

price_data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print("Price rows:", len(price_data))


# ---------------------------------------------------------
# 2. FETCH NEWS
# ---------------------------------------------------------

print("\n2. Fetching financial news...")

news = fetch_news(
    SYMBOL,
    count=20,
)

print("News articles:", len(news))

if not news:
    print("No news available.")
    raise SystemExit


# ---------------------------------------------------------
# 3. CONVERT NEWS TO DATAFRAME
# ---------------------------------------------------------

news_df = news_to_dataframe(news)

print("\nNews dataframe:")
print(
    news_df[
        [
            "headline",
            "source",
            "published_at",
            "news_date",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 4. RUN FINBERT
# ---------------------------------------------------------

print("\n3. Running FinBERT...")

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
# 5. AGGREGATE DAILY SENTIMENT
# ---------------------------------------------------------

print("\n4. Aggregating daily sentiment...")

daily_sentiment = aggregate_daily_sentiment(
    news_df
)

print(
    daily_sentiment.to_string(index=False)
)


# ---------------------------------------------------------
# 6. ALIGN PRICE + SENTIMENT
# ---------------------------------------------------------

print("\n5. Aligning price and sentiment...")

combined = align_price_and_sentiment(
    price_data,
    daily_sentiment,
)

print("\nAligned dataset:")

print(
    combined[
        [
            "Close",
            "sentiment_score",
            "news_count",
        ]
    ].tail(15).to_string()
)


# ---------------------------------------------------------
# 7. GENERATE SENTIMENT SIGNALS
# ---------------------------------------------------------

print("\n6. Generating sentiment signals...")

combined = generate_sentiment_signals(
    combined,
    sentiment_column="sentiment_score",
    buy_threshold=0.20,
    sell_threshold=-0.20,
)

print("\nSignal distribution:")

print(
    combined["Signal"].value_counts()
)


# ---------------------------------------------------------
# 8. RUN BACKTEST
# ---------------------------------------------------------

print("\n7. Running backtest...")

backtest_data, trades = run_backtest(
    combined,
    initial_capital=INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 9. CALCULATE METRICS
# ---------------------------------------------------------

metrics = calculate_metrics(
    backtest_data["Portfolio_Value"],
    trades,
    INITIAL_CAPITAL,
)


# ---------------------------------------------------------
# 10. DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("SENTIMENT BACKTEST RESULT")
print("=" * 60)

for key, value in metrics.items():

    if isinstance(value, float):

        if "return" in key or "drawdown" in key or "rate" in key:
            print(f"{key}: {value:.2f}%")
        else:
            print(f"{key}: {value:.4f}")

    else:
        print(f"{key}: {value}")


# ---------------------------------------------------------
# 11. DISPLAY TRADES
# ---------------------------------------------------------

print("\nTRADES")
print("=" * 60)

if trades:

    for trade in trades:
        print(trade)

else:

    print("No trades generated.")