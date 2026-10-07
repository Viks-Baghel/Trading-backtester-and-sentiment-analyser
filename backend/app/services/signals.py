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

    sma_score = (
        df["SMA_20"] > df["SMA_50"]
    ).astype(float)

    macd_score = (
        df["MACD"] > df["MACD_SIGNAL"]
    ).astype(float)

    df["rsi_score"] = 0.5

    df.loc[
        df["RSI"] >= 50,
        "rsi_score"
    ] = 1.0

    df.loc[
        df["RSI"] < 50,
        "rsi_score"
    ] = 0.0

    # Technical score
    df["technical_score"] = (
        0.40 * sma_score
        + 0.40 * macd_score
        + 0.20 * df["rsi_score"]
    )

    # Technical direction
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
    # 2. FINBERT SENTIMENT
    # =========================================================

    sentiment = (
        df[sentiment_column]
        .fillna(0.0)
        .clip(-1.0, 1.0)
    )

    df["sentiment_normalized"] = (
        sentiment + 1.0
    ) / 2.0

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
    # 3. ARIMA FORECAST
    # =========================================================

    current_price = pd.to_numeric(
        df["Close"],
        errors="coerce",
    )

    forecast_price = pd.to_numeric(
        df[forecast_column],
        errors="coerce",
    )

    expected_return = (
        forecast_price - current_price
    ) / current_price

    df["forecast_expected_return"] = expected_return

    df["forecast_direction"] = "NEUTRAL"

    df.loc[
        expected_return >= 0.003,
        "forecast_direction"
    ] = "BULLISH"

    df.loc[
        expected_return <= -0.003,
        "forecast_direction"
    ] = "BEARISH"

    df["forecast_score"] = (
        0.5 + expected_return / 0.04
    ).clip(
        0.0,
        1.0,
    )

    # =========================================================
    # 4. AI HYBRID SCORE
    # =========================================================

    df["ai_hybrid_score"] = (
        0.45 * df["technical_score"]
        + 0.30 * df["sentiment_normalized"]
        + 0.25 * df["forecast_score"]
    )

    # =========================================================
    # 5. DIRECTIONAL VOTING
    #
    # Three components:
    #
    # Technical
    # Sentiment
    # Forecast
    #
    # BUY  = 2 or more bullish votes
    # SELL = 2 or more bearish votes
    # HOLD = otherwise
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

    # ---------------------------------------------------------
    # Bullish votes
    # ---------------------------------------------------------

    bullish_votes = (
        technical_bullish.astype(int)
        + forecast_bullish.astype(int)
        + sentiment_bullish.astype(int)
    )

    # ---------------------------------------------------------
    # Bearish votes
    # ---------------------------------------------------------

    bearish_votes = (
        technical_bearish.astype(int)
        + forecast_bearish.astype(int)
        + sentiment_bearish.astype(int)
    )

    df["bullish_votes"] = bullish_votes
    df["bearish_votes"] = bearish_votes

    # =========================================================
    # 6. BUY
    #
    # At least 2 bullish components
    # and AI score >= 0.60
    # =========================================================

    buy_condition = (
        (bullish_votes >= 2)
        & (df["ai_hybrid_score"] >= 0.60)
    )

    # =========================================================
    # 7. SELL
    #
    # At least 2 bearish components
    # and AI score <= 0.40
    # =========================================================

    sell_condition = (
        (bearish_votes >= 2)
        & (df["ai_hybrid_score"] <= 0.40)
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
    ] = "2+ bullish components"

    df.loc[
        sell_condition,
        "signal_reason"
    ] = "2+ bearish components"

    # =========================================================
    # 10. COMPONENT EXPLANATION
    # =========================================================

    df["signal_explanation"] = (
        "Technical: "
        + df["technical_direction"].astype(str)
        + " | Sentiment: "
        + df["sentiment_direction"].astype(str)
        + " | Forecast: "
        + df["forecast_direction"].astype(str)
        + " | Bullish votes: "
        + df["bullish_votes"].astype(str)
        + " | Bearish votes: "
        + df["bearish_votes"].astype(str)
    )

    return df

def generate_lstm_hybrid_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
    forecast_column: str = "lstm_forecast_price",
) -> pd.DataFrame:
    """
    Generate AI hybrid signals using:

    1. Technical indicators
    2. FinBERT sentiment
    3. LSTM price forecast

    A BUY/SELL signal requires agreement from
    at least 2 of the 3 components.
    """

    df = data.copy()

    df["Signal"] = "HOLD"

    # --------------------------------------------------
    # 1. TECHNICAL COMPONENT
    # --------------------------------------------------

    sma_score = (
        df["SMA_20"] > df["SMA_50"]
    ).astype(float)

    macd_score = (
        df["MACD"] > df["MACD_SIGNAL"]
    ).astype(float)

    df["rsi_score"] = 0.5

    df.loc[
        df["RSI"] >= 50,
        "rsi_score"
    ] = 1.0

    df.loc[
        df["RSI"] < 50,
        "rsi_score"
    ] = 0.0

    df["technical_score"] = (
        0.40 * sma_score
        + 0.40 * macd_score
        + 0.20 * df["rsi_score"]
    )

    df["technical_direction"] = "NEUTRAL"

    df.loc[
        df["technical_score"] >= 0.65,
        "technical_direction"
    ] = "BULLISH"

    df.loc[
        df["technical_score"] <= 0.35,
        "technical_direction"
    ] = "BEARISH"

    # --------------------------------------------------
    # 2. FINBERT SENTIMENT COMPONENT
    # --------------------------------------------------

    sentiment = (
        pd.to_numeric(
            df[sentiment_column],
            errors="coerce"
        )
        .fillna(0.0)
        .clip(-1.0, 1.0)
    )

    df["sentiment_normalized"] = (
        sentiment + 1.0
    ) / 2.0

    df["sentiment_direction"] = "NO_NEWS"

    df.loc[
        sentiment >= 0.15,
        "sentiment_direction"
    ] = "BULLISH"

    df.loc[
        sentiment <= -0.15,
        "sentiment_direction"
    ] = "BEARISH"

    # --------------------------------------------------
    # 3. LSTM FORECAST COMPONENT
    # --------------------------------------------------

    current_price = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    lstm_forecast = pd.to_numeric(
        df[forecast_column],
        errors="coerce"
    )

    expected_return = (
        lstm_forecast - current_price
    ) / current_price

    df["lstm_expected_return"] = expected_return

    df["lstm_direction"] = "NEUTRAL"

    df.loc[
        expected_return >= 0.005,
        "lstm_direction"
    ] = "BULLISH"

    df.loc[
        expected_return <= -0.005,
        "lstm_direction"
    ] = "BEARISH"

    # Convert forecast into a 0-1 score.
    df["lstm_score"] = (
        0.5 + expected_return / 0.04
    ).clip(0.0, 1.0)

    # --------------------------------------------------
    # 4. THREE-WAY VOTING
    # --------------------------------------------------

    technical_bullish = (
        df["technical_direction"]
        == "BULLISH"
    )

    technical_bearish = (
        df["technical_direction"]
        == "BEARISH"
    )

    sentiment_bullish = (
        df["sentiment_direction"]
        == "BULLISH"
    )

    sentiment_bearish = (
        df["sentiment_direction"]
        == "BEARISH"
    )

    lstm_bullish = (
        df["lstm_direction"]
        == "BULLISH"
    )

    lstm_bearish = (
        df["lstm_direction"]
        == "BEARISH"
    )

    df["bullish_votes"] = (
        technical_bullish.astype(int)
        + sentiment_bullish.astype(int)
        + lstm_bullish.astype(int)
    )

    df["bearish_votes"] = (
        technical_bearish.astype(int)
        + sentiment_bearish.astype(int)
        + lstm_bearish.astype(int)
    )

    # --------------------------------------------------
    # 5. FINAL SIGNAL
    # --------------------------------------------------

    buy_condition = (
        (df["bullish_votes"] >= 2)
        & (df["technical_score"] >= 0.50)
        & (df["lstm_score"] >= 0.50)
    )

    sell_condition = (
        (df["bearish_votes"] >= 2)
        & (df["technical_score"] <= 0.50)
        & (df["lstm_score"] <= 0.50)
    )

    df.loc[
        buy_condition,
        "Signal"
    ] = "BUY"

    df.loc[
        sell_condition,
        "Signal"
    ] = "SELL"

    # --------------------------------------------------
    # 6. EXPLAINABILITY
    # --------------------------------------------------

    df["signal_reason"] = (
        "No strong agreement"
    )

    df.loc[
        buy_condition,
        "signal_reason"
    ] = "2+ bullish components"

    df.loc[
        sell_condition,
        "signal_reason"
    ] = "2+ bearish components"

    df["signal_explanation"] = (
        "Technical: "
        + df["technical_direction"].astype(str)
        + " | Sentiment: "
        + df["sentiment_direction"].astype(str)
        + " | LSTM: "
        + df["lstm_direction"].astype(str)
        + " | Bullish votes: "
        + df["bullish_votes"].astype(str)
        + " | Bearish votes: "
        + df["bearish_votes"].astype(str)
    )

    return df


