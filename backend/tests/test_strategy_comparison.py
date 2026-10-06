import pandas as pd

from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
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
from backend.app.services.forecasting_service import (
    forecast_arima,
)
from backend.app.services.signals import (
    generate_technical_signals,
    generate_sentiment_signals,
    generate_hybrid_signals,
    generate_ai_hybrid_signals,
)
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


# =========================================================
# CONFIGURATION
# =========================================================

SYMBOL = "RELIANCE.NS"

START_DATE = "2026-01-01"
END_DATE = "2026-09-05"

INITIAL_CAPITAL = 100000.0

MINIMUM_HISTORY = 30


# =========================================================
# HEADER
# =========================================================

print("\n")
print("=" * 70)
print("STRATEGY COMPARISON")
print("=" * 70)


# =========================================================
# 1. LOAD PRICE DATA
# =========================================================

price_data = load_market_data(
    SYMBOL,
    START_DATE,
    END_DATE,
)

print(
    f"\nPrice rows: {len(price_data)}"
)


# =========================================================
# 2. LOAD NEWS
# =========================================================

news_items = fetch_news(
    SYMBOL,
    count=5,
)

news_df = news_to_dataframe(
    news_items
)

print(
    f"News articles: {len(news_df)}"
)


# =========================================================
# 3. FINBERT SENTIMENT
# =========================================================

if not news_df.empty:

    news_df = analyze_news_dataframe(
        news_df
    )

    daily_sentiment = (
        aggregate_daily_sentiment(
            news_df
        )
    )

else:

    daily_sentiment = pd.DataFrame(
        columns=[
            "news_date",
            "sentiment_score",
            "news_count",
        ]
    )


# =========================================================
# 4. ALIGN PRICE + SENTIMENT
# =========================================================

combined = align_price_and_sentiment(
    price_data,
    daily_sentiment,
)


# =========================================================
# 5. ADD TECHNICAL INDICATORS
# =========================================================

combined = add_indicators(
    combined
)

print(
    f"Rows after indicators: "
    f"{len(combined)}"
)


# =========================================================
# 6. CREATE ROLLING ARIMA FORECAST
# =========================================================

forecast_values = []

for i in range(
    len(combined)
):

    if i < MINIMUM_HISTORY:

        forecast_values.append(
            float("nan")
        )

        continue

    historical_data = (
        combined.iloc[:i]
    )

    try:

        forecast = forecast_arima(
            historical_data,
            column="Close",
            steps=1,
        )

        forecast_price = float(
            forecast.iloc[0]
        )

        forecast_values.append(
            forecast_price
        )

    except Exception:

        forecast_values.append(
            float("nan")
        )


combined["forecast_price"] = (
    forecast_values
)


# =========================================================
# 7. CREATE DATASETS FOR EACH STRATEGY
# =========================================================

# ---------------------------------------------------------
# Technical
# ---------------------------------------------------------

technical_data = (
    combined.dropna(
        subset=[
            "SMA_20",
            "SMA_50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )
    .copy()
)

technical_data = (
    generate_technical_signals(
        technical_data
    )
)


# ---------------------------------------------------------
# Sentiment
# ---------------------------------------------------------

sentiment_data = (
    combined.copy()
)

sentiment_data = (
    generate_sentiment_signals(
        sentiment_data
    )
)


# ---------------------------------------------------------
# Technical + Sentiment
# ---------------------------------------------------------

hybrid_data = (
    combined.dropna(
        subset=[
            "SMA_20",
            "SMA_50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )
    .copy()
)

hybrid_data = (
    generate_hybrid_signals(
        hybrid_data
    )
)


# ---------------------------------------------------------
# AI Hybrid requires ARIMA forecast
# ---------------------------------------------------------

ai_hybrid_data = (
    combined.dropna(
        subset=[
            "forecast_price",
            "SMA_20",
            "SMA_50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )
    .copy()
)

ai_hybrid_data = (
    generate_ai_hybrid_signals(
        ai_hybrid_data
    )
)


# =========================================================
# 8. BACKTEST HELPER
# =========================================================

comparison_results = []


def evaluate_strategy(
    strategy_name,
    data,
):
    """
    Run a strategy and store its metrics.
    """

    if data.empty:

        print(
            f"\nSkipping {strategy_name}: "
            "no data"
        )

        return

    result_data, trades = (
        run_backtest(
            data,
            initial_capital=INITIAL_CAPITAL,
        )
    )

    metrics = calculate_metrics(
        result_data[
            "Portfolio_Value"
        ],
        trades,
        INITIAL_CAPITAL,
    )

    comparison_results.append(
        {
            "strategy": strategy_name,
            "initial_capital": metrics[
                "initial_capital"
            ],
            "final_value": metrics[
                "final_value"
            ],
            "total_return": metrics[
                "total_return"
            ],
            "sharpe_ratio": metrics[
                "sharpe_ratio"
            ],
            "max_drawdown": metrics[
                "max_drawdown"
            ],
            "win_rate": metrics[
                "win_rate"
            ],
            "total_trades": metrics[
                "total_trades"
            ],
        }
    )


# =========================================================
# 9. BUY & HOLD BASELINE
# =========================================================

first_price = float(
    combined["Close"].iloc[0]
)

last_price = float(
    combined["Close"].iloc[-1]
)

buy_hold_return = (
    (last_price - first_price)
    / first_price
) * 100.0

buy_hold_final = (
    INITIAL_CAPITAL
    * (1 + buy_hold_return / 100)
)

comparison_results.append(
    {
        "strategy": "Buy & Hold",
        "initial_capital": INITIAL_CAPITAL,
        "final_value": buy_hold_final,
        "total_return": buy_hold_return,
        "sharpe_ratio": None,
        "max_drawdown": None,
        "win_rate": None,
        "total_trades": 1,
    }
)


# =========================================================
# 10. EVALUATE STRATEGIES
# =========================================================

evaluate_strategy(
    "Technical",
    technical_data,
)

evaluate_strategy(
    "Sentiment",
    sentiment_data,
)

evaluate_strategy(
    "Technical + Sentiment",
    hybrid_data,
)

evaluate_strategy(
    "AI Hybrid",
    ai_hybrid_data,
)


# =========================================================
# 11. CREATE COMPARISON DATAFRAME
# =========================================================

comparison_df = pd.DataFrame(
    comparison_results
)


# =========================================================
# 12. PRINT COMPARISON
# =========================================================

print("\n")
print("=" * 70)
print("STRATEGY PERFORMANCE COMPARISON")
print("=" * 70)

print(
    comparison_df[
        [
            "strategy",
            "total_return",
            "sharpe_ratio",
            "max_drawdown",
            "win_rate",
            "total_trades",
        ]
    ].to_string(
        index=False
    )
)


# =========================================================
# 13. FORMATTED TABLE
# =========================================================

print("\n")
print("=" * 70)
print("FORMATTED RESULTS")
print("=" * 70)

for _, row in comparison_df.iterrows():

    print(
        f"\n{row['strategy']}"
    )

    print(
        f"  Final Value: "
        f"₹{row['final_value']:.2f}"
    )

    print(
        f"  Return: "
        f"{row['total_return']:.2f}%"
    )

    if pd.notna(
        row["sharpe_ratio"]
    ):

        print(
            f"  Sharpe: "
            f"{row['sharpe_ratio']:.4f}"
        )

    else:

        print(
            "  Sharpe: N/A"
        )

    if pd.notna(
        row["max_drawdown"]
    ):

        print(
            f"  Max Drawdown: "
            f"{row['max_drawdown']:.2f}%"
        )

    else:

        print(
            "  Max Drawdown: N/A"
        )

    if pd.notna(
        row["win_rate"]
    ):

        print(
            f"  Win Rate: "
            f"{row['win_rate']:.2f}%"
        )

    else:

        print(
            "  Win Rate: N/A"
        )

    print(
        f"  Trades: "
        f"{int(row['total_trades'])}"
    )


# =========================================================
# 14. BEST STRATEGY
# =========================================================

valid_results = comparison_df[
    comparison_df["total_return"].notna()
]

if not valid_results.empty:

    best_row = valid_results.loc[
        valid_results["total_return"].idxmax()
    ]

    print("\n")
    print("=" * 70)
    print("BEST RETURN")
    print("=" * 70)

    print(
        f"{best_row['strategy']}: "
        f"{best_row['total_return']:.2f}%"
    )