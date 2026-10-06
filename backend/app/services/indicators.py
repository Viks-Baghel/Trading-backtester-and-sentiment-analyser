import pandas as pd

from ta.momentum import RSIIndicator
from ta.trend import (
    EMAIndicator,
    MACD,
    SMAIndicator,
)
from ta.volatility import BollingerBands


def add_indicators(
    data: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50,
) -> pd.DataFrame:

    df = data.copy()

    df["SMA_20"] = SMAIndicator(
        close=df["Close"],
        window=short_window,
    ).sma_indicator()

    df["SMA_50"] = SMAIndicator(
        close=df["Close"],
        window=long_window,
    ).sma_indicator()

    df["EMA_20"] = EMAIndicator(
        close=df["Close"],
        window=20,
    ).ema_indicator()

    df["RSI"] = RSIIndicator(
        close=df["Close"],
        window=14,
    ).rsi()

    macd = MACD(
        close=df["Close"],
        window_slow=26,
        window_fast=12,
        window_sign=9,
    )

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["MACD_HIST"] = macd.macd_diff()

    bollinger = BollingerBands(
        close=df["Close"],
        window=20,
        window_dev=2,
    )

    df["BB_HIGH"] = bollinger.bollinger_hband()
    df["BB_LOW"] = bollinger.bollinger_lband()
    df["BB_MIDDLE"] = bollinger.bollinger_mavg()

    df.dropna(inplace=True)

    return df