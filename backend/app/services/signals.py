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

    # Ensure required input exists.
    if sentiment_column not in df.columns:
        raise ValueError(
            f"Missing required sentiment column: {sentiment_column}"
        )

    sentiment = pd.to_numeric(
        df[sentiment_column],
        errors="coerce",
    )

    df["Signal"] = "HOLD"
    df["sentiment_direction"] = "NEUTRAL"
    df["signal_reason"] = "Sentiment score did not meet a trading threshold"

    valid = sentiment.notna()

    bullish = valid & (sentiment >= buy_threshold)
    bearish = valid & (sentiment <= sell_threshold)

    df.loc[bullish, "Signal"] = "BUY"
    df.loc[bearish, "Signal"] = "SELL"

    df.loc[bullish, "sentiment_direction"] = "BULLISH"
    df.loc[bearish, "sentiment_direction"] = "BEARISH"

    df.loc[bullish, "signal_reason"] = (
        f"Sentiment score >= {buy_threshold}"
    )
    df.loc[bearish, "signal_reason"] = (
        f"Sentiment score <= {sell_threshold}"
    )

    df.loc[~valid, "signal_reason"] = (
        "No valid sentiment score available"
    )

    df["signal_explanation"] = (
        "Sentiment score: "
        + sentiment.map(
            lambda value: f"{value:.3f}" if pd.notna(value) else "unavailable"
        )
        + " | Direction: "
        + df["sentiment_direction"].astype(str)
        + " | Signal: "
        + df["Signal"].astype(str)
    )

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



def generate_custom_signals(
    data: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """Generate configurable technical, sentiment, or hybrid signals."""

    df = data.copy()
    df["Signal"] = "HOLD"

    strategy_type = config.get("strategy_type", "technical")

    rsi_buy_max = float(config.get("rsi_buy_max", 70))
    rsi_sell_min = float(config.get("rsi_sell_min", 70))
    sentiment_buy = float(config.get("sentiment_buy_threshold", 0.20))
    sentiment_sell = float(config.get("sentiment_sell_threshold", -0.20))
    technical_weight = float(config.get("technical_weight", 0.60))
    sentiment_weight = float(config.get("sentiment_weight", 0.40))
    buy_score_threshold = float(config.get("buy_score_threshold", 0.65))
    sell_score_threshold = float(config.get("sell_score_threshold", 0.35))

    if not 0 <= rsi_buy_max <= 100 or not 0 <= rsi_sell_min <= 100:
        raise ValueError("RSI thresholds must be between 0 and 100.")

    if not -1 <= sentiment_sell < sentiment_buy <= 1:
        raise ValueError(
            "Sentiment thresholds must be between -1 and 1, "
            "with the sell threshold below the buy threshold."
        )

    if not 0 <= technical_weight <= 1 or not 0 <= sentiment_weight <= 1:
        raise ValueError("Strategy weights must be between 0 and 1.")

    if abs(technical_weight + sentiment_weight - 1.0) > 0.0001:
        raise ValueError("Technical and sentiment weights must sum to 1.")

    if not 0 <= sell_score_threshold < buy_score_threshold <= 1:
        raise ValueError(
            "Score thresholds must be between 0 and 1, "
            "with the sell threshold below the buy threshold."
        )

    required_columns = ["SMA_20", "SMA_50", "RSI", "MACD", "MACD_SIGNAL"]
    missing = [column for column in required_columns if column not in df.columns]

    if missing:
        raise ValueError(f"Missing technical indicator columns: {missing}")

    technical_score = (
        (df["SMA_20"] > df["SMA_50"]).astype(float)
        + (df["MACD"] > df["MACD_SIGNAL"]).astype(float)
        + (df["RSI"] < rsi_buy_max).astype(float)
    ) / 3.0

    df["technical_score"] = technical_score

    if strategy_type == "technical":
        buy = (
            (df["SMA_20"] > df["SMA_50"])
            & (df["MACD"] > df["MACD_SIGNAL"])
            & (df["RSI"] < rsi_buy_max)
        )

        sell = (
            (df["SMA_20"] < df["SMA_50"])
            | (df["MACD"] < df["MACD_SIGNAL"])
            | (df["RSI"] > rsi_sell_min)
        )

    elif strategy_type == "sentiment":
        if "sentiment_score" not in df.columns:
            raise ValueError("Sentiment strategy requires sentiment_score.")

        sentiment = pd.to_numeric(df["sentiment_score"], errors="coerce")

        buy = sentiment.notna() & (sentiment >= sentiment_buy)
        sell = sentiment.notna() & (sentiment <= sentiment_sell)

    elif strategy_type == "hybrid":
        if "sentiment_score" not in df.columns:
            raise ValueError("Hybrid strategy requires sentiment_score.")

        sentiment = pd.to_numeric(df["sentiment_score"], errors="coerce")
        available = sentiment.notna()
        normalized_sentiment = (sentiment.clip(-1, 1) + 1) / 2

        df["sentiment_score"] = sentiment
        df["hybrid_score"] = (
            technical_weight * technical_score
            + sentiment_weight * normalized_sentiment
        )

        buy = (
            available
            & (sentiment >= sentiment_buy)
            & (df["hybrid_score"] >= buy_score_threshold)
        )

        sell = (
            available
            & (sentiment <= sentiment_sell)
            & (df["hybrid_score"] <= sell_score_threshold)
        )

    else:
        raise ValueError(
            "strategy_type must be 'technical', 'sentiment', or 'hybrid'."
        )

    # Prevent missing indicator values from creating accidental signals.
    valid = df[required_columns].notna().all(axis=1)
    if strategy_type == "technical":
        buy &= valid
        sell &= valid

    df.loc[buy, "Signal"] = "BUY"
    df.loc[sell, "Signal"] = "SELL"

    
    df["signal_reason"] = "No custom strategy condition met"
    df.loc[buy, "signal_reason"] = "Custom strategy BUY conditions met"
    df.loc[sell, "signal_reason"] = "Custom strategy SELL conditions met"

    sentiment_for_explanation = pd.to_numeric(
        df.get(
            "sentiment_score",
            pd.Series(float("nan"), index=df.index),
        ),
        errors="coerce",
    )

    df["signal_explanation"] = (
        "Strategy: " + str(strategy_type)
        + " | Technical score: " + df["technical_score"].round(3).astype(str)
        + " | Sentiment: " + sentiment_for_explanation.round(3).astype(str)
        + " | Signal: " + df["Signal"].astype(str)
    )

    return df



def generate_full_hybrid_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
) -> pd.DataFrame:
    """
    Four-component hybrid:
    technical indicators + sentiment + ARIMA + LSTM.
    A BUY or SELL requires agreement from at least 3 components.
    """
    df = data.copy()

    required = [
        "Close", "SMA_20", "SMA_50", "RSI", "MACD",
        "MACD_SIGNAL", "forecast_price", "lstm_forecast_price",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing hybrid input columns: {missing}")

    if sentiment_column not in df.columns:
        df[sentiment_column] = float("nan")

    close = pd.to_numeric(df["Close"], errors="coerce").replace(0, float("nan"))
    sentiment = pd.to_numeric(df[sentiment_column], errors="coerce")

    # Component 1: technical indicators
    technical_score = (
        (df["SMA_20"] > df["SMA_50"]).astype(float)
        + (df["MACD"] > df["MACD_SIGNAL"]).astype(float)
        + (df["RSI"] >= 50).astype(float)
    ) / 3.0

    technical_direction = pd.Series("NEUTRAL", index=df.index)
    technical_direction.loc[technical_score >= 2 / 3] = "BULLISH"
    technical_direction.loc[technical_score <= 1 / 3] = "BEARISH"

    # Component 2: sentiment; missing news is neutral, not bullish/bearish.
    sentiment_direction = pd.Series("NEUTRAL", index=df.index)
    sentiment_direction.loc[sentiment >= 0.15] = "BULLISH"
    sentiment_direction.loc[sentiment <= -0.15] = "BEARISH"

    # Components 3 and 4: model forecasts versus current close.
    arima_return = (
        pd.to_numeric(df["forecast_price"], errors="coerce") - close
    ) / close
    lstm_return = (
        pd.to_numeric(df["lstm_forecast_price"], errors="coerce") - close
    ) / close

    arima_direction = pd.Series("NEUTRAL", index=df.index)
    arima_direction.loc[arima_return >= 0.003] = "BULLISH"
    arima_direction.loc[arima_return <= -0.003] = "BEARISH"

    lstm_direction = pd.Series("NEUTRAL", index=df.index)
    lstm_direction.loc[lstm_return >= 0.003] = "BULLISH"
    lstm_direction.loc[lstm_return <= -0.003] = "BEARISH"

    directions = pd.DataFrame({
        "technical": technical_direction,
        "sentiment": sentiment_direction,
        "arima": arima_direction,
        "lstm": lstm_direction,
    }, index=df.index)

    bullish_votes = (directions == "BULLISH").sum(axis=1)
    bearish_votes = (directions == "BEARISH").sum(axis=1)

    # Require valid prices and both forecast outputs before issuing a signal.
    valid = (
        close.notna()
        & pd.to_numeric(df["forecast_price"], errors="coerce").notna()
        & pd.to_numeric(df["lstm_forecast_price"], errors="coerce").notna()
    )

    df["technical_score"] = technical_score
    df["arima_expected_return"] = arima_return
    df["lstm_expected_return"] = lstm_return
    df["technical_direction"] = technical_direction
    df["sentiment_direction"] = sentiment_direction
    df["forecast_direction"] = arima_direction
    df["lstm_direction"] = lstm_direction
    df["bullish_votes"] = bullish_votes
    df["bearish_votes"] = bearish_votes
    df["Signal"] = "HOLD"

    df.loc[valid & (bullish_votes >= 3), "Signal"] = "BUY"
    df.loc[valid & (bearish_votes >= 3), "Signal"] = "SELL"

    df["signal_reason"] = "Fewer than 3 components agree"
    df.loc[df["Signal"] == "BUY", "signal_reason"] = "At least 3 bullish components"
    df.loc[df["Signal"] == "SELL", "signal_reason"] = "At least 3 bearish components"

    df["signal_explanation"] = (
        "Technical: " + technical_direction.astype(str)
        + " | Sentiment: " + sentiment_direction.astype(str)
        + " | ARIMA: " + arima_direction.astype(str)
        + " | LSTM: " + lstm_direction.astype(str)
        + " | Bullish votes: " + bullish_votes.astype(str)
        + " | Bearish votes: " + bearish_votes.astype(str)
    )

    return df
