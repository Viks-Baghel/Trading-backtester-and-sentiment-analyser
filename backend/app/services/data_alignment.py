import pandas as pd


def align_price_and_sentiment(
    price_data: pd.DataFrame,
    sentiment_data: pd.DataFrame,
) -> pd.DataFrame:

    prices = price_data.copy()
    sentiment = sentiment_data.copy()

    # Normalize dates
    prices.index = pd.to_datetime(prices.index).normalize()

    sentiment["news_date"] = pd.to_datetime(
        sentiment["news_date"]
    ).dt.normalize()

    prices = prices.sort_index()
    sentiment = sentiment.sort_values("news_date")

    # ---------------------------------------------------------
    # Move sentiment to the NEXT calendar day first.
    #
    # Then merge forward to the first available trading day.
    #
    # Example:
    #
    # News:          Saturday 25 July
    # Target date:   Sunday 26 July
    # Next trading:  Monday 27 July
    #
    # News:          Monday 31 August
    # Target date:   Tuesday 1 September
    # Next trading:  Tuesday 1 September
    # ---------------------------------------------------------

    sentiment["available_from"] = (
        sentiment["news_date"] + pd.Timedelta(days=1)
    )

    trading_days = pd.DataFrame({
        "trade_date": prices.index
    })

    mapped_sentiment = pd.merge_asof(
        sentiment,
        trading_days,
        left_on="available_from",
        right_on="trade_date",
        direction="forward",
    )

    mapped_sentiment = mapped_sentiment.dropna(
        subset=["trade_date"]
    )

    # ---------------------------------------------------------
    # Aggregate multiple news articles mapped to same day
    # ---------------------------------------------------------

    daily_sentiment = (
        mapped_sentiment
        .groupby("trade_date")
        .agg(
            sentiment_score=("sentiment_score", "mean"),
            news_count=("news_count", "sum"),
        )
    )

    # ---------------------------------------------------------
    # Join with price data
    # ---------------------------------------------------------

    combined = prices.join(
        daily_sentiment,
        how="left",
    )

    # Missing news = neutral sentiment
    combined["sentiment_score"] = (
        combined["sentiment_score"]
        .fillna(0.0)
    )

    combined["news_count"] = (
        combined["news_count"]
        .fillna(0)
        .astype(int)
    )

    return combined