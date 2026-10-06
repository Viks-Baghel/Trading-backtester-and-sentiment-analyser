import pandas as pd


# =========================================================
# ALIGN PRICE DATA WITH NEWS SENTIMENT
# =========================================================

def align_price_and_sentiment(
    price_data: pd.DataFrame,
    sentiment_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Align daily news sentiment with trading-price data.

    IMPORTANT:
    News published on day D becomes available for trading
    on the NEXT trading day.

    This prevents look-ahead bias.
    """

    if price_data.empty:
        return price_data.copy()

    price = price_data.copy()

    # =========================================================
    # 1. NORMALIZE PRICE DATES
    # =========================================================

    if not isinstance(
        price.index,
        pd.DatetimeIndex,
    ):

        price.index = pd.to_datetime(
            price.index,
            errors="coerce",
        )

    else:

        price.index = pd.to_datetime(
            price.index,
            errors="coerce",
        )

    # Remove invalid dates
    price = price[
        ~price.index.isna()
    ].copy()

    price.index = price.index.normalize()

    price = price.sort_index()

    # Preserve original trading date
    price["price_date"] = price.index

    # =========================================================
    # 2. HANDLE EMPTY SENTIMENT
    # =========================================================

    if sentiment_data.empty:

        price["sentiment_score"] = 0.0
        price["news_count"] = 0

        return price

    sentiment = sentiment_data.copy()

    # =========================================================
    # 3. NORMALIZE NEWS DATE
    # =========================================================

    if "news_date" not in sentiment.columns:

        if "published_at" in sentiment.columns:

            sentiment["news_date"] = pd.to_datetime(
                sentiment["published_at"],
                errors="coerce",
                utc=True,
            ).dt.tz_convert(None).dt.normalize()

        else:

            raise ValueError(
                "sentiment_data must contain "
                "'news_date' or 'published_at'"
            )

    else:

        sentiment["news_date"] = pd.to_datetime(
            sentiment["news_date"],
            errors="coerce",
        )

        # Remove timezone if present
        if hasattr(
            sentiment["news_date"].dt,
            "tz"
        ):

            try:

                sentiment["news_date"] = (
                    sentiment["news_date"]
                    .dt.tz_localize(None)
                )

            except TypeError:
                pass

        sentiment["news_date"] = (
            sentiment["news_date"]
            .dt.normalize()
        )

    # Remove invalid news dates
    sentiment = sentiment[
        ~sentiment["news_date"].isna()
    ].copy()

    if sentiment.empty:

        price["sentiment_score"] = 0.0
        price["news_count"] = 0

        return price

    # =========================================================
    # 4. MAKE SURE SENTIMENT IS NUMERIC
    # =========================================================

    if "sentiment_score" not in sentiment.columns:

        sentiment["sentiment_score"] = 0.0

    sentiment["sentiment_score"] = pd.to_numeric(
        sentiment["sentiment_score"],
        errors="coerce",
    ).fillna(0.0)

    # =========================================================
    # 5. MAKE SURE NEWS COUNT EXISTS
    # =========================================================

    if "news_count" not in sentiment.columns:

        if "headline" in sentiment.columns:

            sentiment["news_count"] = 1

        else:

            sentiment["news_count"] = 1

    sentiment["news_count"] = pd.to_numeric(
        sentiment["news_count"],
        errors="coerce",
    ).fillna(0)

    # =========================================================
    # 6. AGGREGATE NEWS BY DAY
    # =========================================================

    daily_sentiment = (
        sentiment
        .groupby("news_date", as_index=False)
        .agg(
            sentiment_score=(
                "sentiment_score",
                "mean",
            ),
            news_count=(
                "news_count",
                "sum",
            ),
        )
    )

    # =========================================================
    # 7. PREVENT LOOK-AHEAD BIAS
    #
    # News from:
    #
    # July 25
    #
    # becomes available:
    #
    # July 26 onward
    #
    # merge_asof(direction="forward") then maps it to
    # the first trading day >= available_from.
    # =========================================================

    daily_sentiment["available_from"] = (
        daily_sentiment["news_date"]
        + pd.Timedelta(days=1)
    )

    # =========================================================
    # 8. PREPARE PRICE DATA FOR merge_asof
    # =========================================================

    price_for_merge = (
        price.reset_index(
            drop=True
        )[
            [
                "price_date",
            ]
        ]
        .sort_values(
            "price_date"
        )
    )

    sentiment_for_merge = (
        daily_sentiment[
            [
                "available_from",
                "sentiment_score",
                "news_count",
            ]
        ]
        .sort_values(
            "available_from"
        )
    )

    # =========================================================
    # 9. FORWARD ALIGN NEWS TO NEXT TRADING DAY
    # =========================================================

    combined = pd.merge_asof(
        price_for_merge,
        sentiment_for_merge,
        left_on="price_date",
        right_on="available_from",
        direction="forward",
    )

    # =========================================================
    # 10. RESTORE PRICE INDEX
    # =========================================================

    combined = combined.set_index(
        "price_date"
    )

    # =========================================================
    # 11. NUMERIC CLEANUP
    # =========================================================

    combined["sentiment_score"] = pd.to_numeric(
        combined["sentiment_score"],
        errors="coerce",
    )

    combined["news_count"] = pd.to_numeric(
        combined["news_count"],
        errors="coerce",
    )

    # =========================================================
    # 12. NO NEWS = NEUTRAL
    # =========================================================

    combined["sentiment_score"] = (
        combined["sentiment_score"]
        .fillna(0.0)
    )

    combined["news_count"] = (
        combined["news_count"]
        .fillna(0)
        .astype(int)
    )

    # =========================================================
    # 13. JOIN ORIGINAL PRICE COLUMNS
    # =========================================================

    price_without_date = price.drop(
        columns=[
            "price_date",
        ],
        errors="ignore",
    )

    combined = price_without_date.join(
        combined[
            [
                "sentiment_score",
                "news_count",
            ]
        ],
        how="left",
    )

    # Final safety cleanup
    combined["sentiment_score"] = (
        pd.to_numeric(
            combined["sentiment_score"],
            errors="coerce",
        )
        .fillna(0.0)
    )

    combined["news_count"] = (
        pd.to_numeric(
            combined["news_count"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    return combined