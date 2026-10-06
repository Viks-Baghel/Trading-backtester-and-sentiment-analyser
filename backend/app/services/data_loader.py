import os
from typing import Optional

import pandas as pd
import yfinance as yf


CACHE_DIR = "data/price_cache"


def load_market_data(
    symbol: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:

    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_name = (
        f"{symbol.replace('/', '_')}_"
        f"{start_date}_{end_date}.csv"
    )

    cache_path = os.path.join(
        CACHE_DIR,
        cache_name,
    )

    if os.path.exists(cache_path):
        return pd.read_csv(
            cache_path,
            index_col=0,
            parse_dates=True,
        )

    data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError(
            f"No market data found for {symbol}"
        )

    # Handle yFinance multi-level columns.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data[
        [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
        ]
    ].copy()

    data.dropna(inplace=True)

    data.to_csv(cache_path)

    return data