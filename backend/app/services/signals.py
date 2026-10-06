import pandas as pd


# =========================================================
# TECHNICAL STRATEGY
# =========================================================

def generate_technical_signals(
    data: pd.DataFrame,
) -> pd.DataFrame:

    df = data.copy()

    df["Signal"] = "HOLD"

    buy_condition = (
        (df["SMA_20"] > df["SMA_50"])
        & (df["RSI"] < 70)
        & (df["MACD"] > df["MACD_SIGNAL"])
    )

    sell_condition = (
        (df["SMA_20"] < df["SMA_50"])
        | (df["RSI"] > 70)
        | (df["MACD"] < df["MACD_SIGNAL"])
    )

    df.loc[buy_condition, "Signal"] = "BUY"
    df.loc[sell_condition, "Signal"] = "SELL"

    return df


# =========================================================
# SENTIMENT STRATEGY
# =========================================================

def generate_sentiment_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
    buy_threshold: float = 0.20,
    sell_threshold: float = -0.20,
) -> pd.DataFrame:

    df = data.copy()

    df["Signal"] = "HOLD"

    df.loc[
        df[sentiment_column] >= buy_threshold,
        "Signal"
    ] = "BUY"

    df.loc[
        df[sentiment_column] <= sell_threshold,
        "Signal"
    ] = "SELL"

    return df


# =========================================================
# BASIC HYBRID STRATEGY
# Technical + Sentiment
# =========================================================

def generate_hybrid_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
    buy_sentiment_threshold: float = 0.20,
    sell_sentiment_threshold: float = -0.20,
) -> pd.DataFrame:

    df = data.copy()

    df["Signal"] = "HOLD"

    # ---------------------------------------------------------
    # Technical components
    # ---------------------------------------------------------

    trend_score = pd.Series(
        0.0,
        index=df.index
    )

    trend_score += (
        df["SMA_20"] > df["SMA_50"]
    ).astype(float)

    trend_score += (
        df["MACD"] > df["MACD_SIGNAL"]
    ).astype(float)

    trend_score += (
        df["RSI"] < 70
    ).astype(float)

    df["technical_score"] = trend_score / 3.0

    # ---------------------------------------------------------
    # Sentiment component
    # ---------------------------------------------------------

    sentiment_score = (
        df[sentiment_column]
        .fillna(0.0)
        .clip(
            lower=-1.0,
            upper=1.0,
        )
    )

    df["sentiment_normalized"] = (
        sentiment_score + 1.0
    ) / 2.0

    # ---------------------------------------------------------
    # Hybrid score
    #
    # 60% Technical
    # 40% Sentiment
    # ---------------------------------------------------------

    df["hybrid_score"] = (
        0.60 * df["technical_score"]
        + 0.40 * df["sentiment_normalized"]
    )

    # ---------------------------------------------------------
    # BUY
    # ---------------------------------------------------------

    buy_condition = (
        (df[sentiment_column] >= buy_sentiment_threshold)
        & (df["technical_score"] >= 0.66)
        & (df["hybrid_score"] >= 0.65)
    )

    # ---------------------------------------------------------
    # SELL
    # ---------------------------------------------------------

    sell_condition = (
        (df[sentiment_column] <= sell_sentiment_threshold)
        & (df["technical_score"] <= 0.33)
        & (df["hybrid_score"] <= 0.35)
    )

    df.loc[
        buy_condition,
        "Signal"
    ] = "BUY"

    df.loc[
        sell_condition,
        "Signal"
    ] = "SELL"

    return df


# =========================================================
# AI-AUGMENTED HYBRID STRATEGY
#
# Technical Indicators
#        +
# FinBERT Sentiment
#        +
# ARIMA Forecast
# =========================================================

def generate_ai_hybrid_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
    forecast_column: str = "forecast_price",
) -> pd.DataFrame:

    df = data.copy()

    df["Signal"] = "HOLD"

    # =========================================================
    # 1. TECHNICAL COMPONENT
    # =========================================================

    # ---------------------------------------------------------
    # SMA direction
    # ---------------------------------------------------------

    sma_score = (
        df["SMA_20"] > df["SMA_50"]
    ).astype(float)

    # ---------------------------------------------------------
    # MACD direction
    # ---------------------------------------------------------

    macd_score = (
        df["MACD"] > df["MACD_SIGNAL"]
    ).astype(float)

    # ---------------------------------------------------------
    # RSI component
    #
    # RSI >= 50 -> bullish contribution
    # RSI < 50  -> bearish contribution
    # ---------------------------------------------------------

    df["rsi_score"] = 0.5

    df.loc[
        df["RSI"] >= 50,
        "rsi_score"
    ] = 1.0

    df.loc[
        df["RSI"] < 50,
        "rsi_score"
    ] = 0.0

    # ---------------------------------------------------------
    # Combined technical score
    #
    # SMA  = 40%
    # MACD = 40%
    # RSI  = 20%
    # ---------------------------------------------------------

    df["technical_score"] = (
        0.40 * sma_score
        + 0.40 * macd_score
        + 0.20 * df["rsi_score"]
    )

    # ---------------------------------------------------------
    # Technical direction
    # ---------------------------------------------------------

    df["technical_direction"] = "NEUTRAL"

    df.loc[
        df["technical_score"] >= 0.65,
        "technical_direction"
    ] = "BULLISH"

    df.loc[
        df["technical_score"] <= 0.35,
        "technical_direction"
    ] = "BEARISH"

    # =========================================================
    # 2. FINBERT SENTIMENT COMPONENT
    # =========================================================

    sentiment = (
        df[sentiment_column]
        .fillna(0.0)
        .clip(
            -1.0,
            1.0,
        )
    )

    # Convert [-1, 1] -> [0, 1]

    df["sentiment_normalized"] = (
        sentiment + 1.0
    ) / 2.0

    # ---------------------------------------------------------
    # Sentiment direction
    # ---------------------------------------------------------

    df["sentiment_direction"] = "NO_NEWS"

    df.loc[
        sentiment >= 0.15,
        "sentiment_direction"
    ] = "BULLISH"

    df.loc[
        sentiment <= -0.15,
        "sentiment_direction"
    ] = "BEARISH"

    # =========================================================
    # 3. ARIMA FORECAST COMPONENT
    # =========================================================

    current_price = pd.to_numeric(
        df["Close"],
        errors="coerce",
    )

    forecast_price = pd.to_numeric(
        df[forecast_column],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # Expected return
    # ---------------------------------------------------------

    expected_return = (
        forecast_price - current_price
    ) / current_price

    df["forecast_expected_return"] = expected_return

    # ---------------------------------------------------------
    # Forecast direction
    #
    # >= +0.30% -> bullish
    # <= -0.30% -> bearish
    # otherwise  -> neutral
    # ---------------------------------------------------------

    df["forecast_direction"] = "NEUTRAL"

    df.loc[
        expected_return >= 0.003,
        "forecast_direction"
    ] = "BULLISH"

    df.loc[
        expected_return <= -0.003,
        "forecast_direction"
    ] = "BEARISH"

    # ---------------------------------------------------------
    # Convert forecast return into 0-1 score
    # ---------------------------------------------------------

    df["forecast_score"] = (
        0.5 + expected_return / 0.04
    ).clip(
        0.0,
        1.0,
    )

    # =========================================================
    # 4. AI HYBRID SCORE
    #
    # Technical = 45%
    # Sentiment = 30%
    # Forecast  = 25%
    # =========================================================

    df["ai_hybrid_score"] = (
        0.45 * df["technical_score"]
        + 0.30 * df["sentiment_normalized"]
        + 0.25 * df["forecast_score"]
    )

    # =========================================================
    # 5. DIRECTIONAL FLAGS
    # =========================================================

    technical_bullish = (
        df["technical_direction"] == "BULLISH"
    )

    technical_bearish = (
        df["technical_direction"] == "BEARISH"
    )

    forecast_bullish = (
        df["forecast_direction"] == "BULLISH"
    )

    forecast_bearish = (
        df["forecast_direction"] == "BEARISH"
    )

    sentiment_bullish = (
        df["sentiment_direction"] == "BULLISH"
    )

    sentiment_bearish = (
        df["sentiment_direction"] == "BEARISH"
    )

    no_news = (
        df["sentiment_direction"] == "NO_NEWS"
    )

    # =========================================================
    # 6. BUY CONDITION
    #
    # Technical must be bullish
    # Forecast must be bullish
    # Sentiment must be bullish OR no news
    # AI score must be >= 0.60
    # =========================================================

    buy_condition = (
        technical_bullish
        & forecast_bullish
        & (
            sentiment_bullish
            | no_news
        )
        & (
            df["ai_hybrid_score"] >= 0.60
        )
    )

    # =========================================================
    # 7. SELL CONDITION
    #
    # Technical must be bearish
    # Forecast must be bearish
    # Sentiment must be bearish OR no news
    # AI score must be <= 0.40
    # =========================================================

    sell_condition = (
        technical_bearish
        & forecast_bearish
        & (
            sentiment_bearish
            | no_news
        )
        & (
            df["ai_hybrid_score"] <= 0.40
        )
    )

    # =========================================================
    # 8. APPLY SIGNALS
    # =========================================================

    df.loc[
        buy_condition,
        "Signal"
    ] = "BUY"

    df.loc[
        sell_condition,
        "Signal"
    ] = "SELL"

    # =========================================================
    # 9. EXPLAINABILITY
    # =========================================================

    df["signal_reason"] = "No strong agreement"

    df.loc[
        buy_condition,
        "signal_reason"
    ] = "Technical + ARIMA bullish"

    df.loc[
        sell_condition,
        "signal_reason"
    ] = "Technical + ARIMA bearish"

    # =========================================================
    # 10. ADD COMPONENT SUMMARY
    # =========================================================

    df["signal_explanation"] = (
        "Technical: "
        + df["technical_direction"].astype(str)
        + " | Sentiment: "
        + df["sentiment_direction"].astype(str)
        + " | Forecast: "
        + df["forecast_direction"].astype(str)
    )

    return df


