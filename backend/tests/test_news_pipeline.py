from backend.app.services.news_service import (
    fetch_news,
    news_to_dataframe,
)

from backend.app.services.sentiment_service import (
    analyze_news_dataframe,
    aggregate_daily_sentiment,
)


SYMBOL = "RELIANCE.NS"


print("\nFETCHING NEWS")
print("=============")

news = fetch_news(
    SYMBOL,
    count=10
)

print("News articles:", len(news))

if not news:
    print("No news returned.")
    raise SystemExit


news_df = news_to_dataframe(news)

print("\nNEWS DATA")
print("=========")

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


print("\nRUNNING FINBERT")
print("================")

news_df = analyze_news_dataframe(
    news_df
)

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


print("\nDAILY SENTIMENT")
print("================")

daily_sentiment = aggregate_daily_sentiment(
    news_df
)

print(
    daily_sentiment.to_string(
        index=False
    )
)