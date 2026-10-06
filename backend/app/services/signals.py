import pandas as pd


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
def generate_hybrid_signals(
    data: pd.DataFrame,
    sentiment_column: str = "sentiment_score",
    buy_sentiment_threshold: float = 0.20,
    sell_sentiment_threshold: float = -0.20,
) -> pd.DataFrame:

    df = data.copy()

    df["Signal"] = "HOLD"

    # Technical bullish conditions
    technical_bullish = (
        (df["SMA_20"] > df["SMA_50"])
        & (df["MACD"] > df["MACD_SIGNAL"])
        & (df["RSI"] < 70)
    )

    # Technical bearish conditions
    technical_bearish = (
        (df["SMA_20"] < df["SMA_50"])
        & (df["MACD"] < df["MACD_SIGNAL"])
    )

    # Sentiment conditions
    sentiment_bullish = (
        df[sentiment_column] >= buy_sentiment_threshold
    )

    sentiment_bearish = (
        df[sentiment_column] <= sell_sentiment_threshold
    )

    # Hybrid BUY:
    # Technical confirmation + positive sentiment
    hybrid_buy = (
        technical_bullish
        & sentiment_bullish
    )

    # Hybrid SELL:
    # Technical confirmation + negative sentiment
    hybrid_sell = (
        technical_bearish
        & sentiment_bearish
    )

    df.loc[hybrid_buy, "Signal"] = "BUY"
    df.loc[hybrid_sell, "Signal"] = "SELL"

    return df