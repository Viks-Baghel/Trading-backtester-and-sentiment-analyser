
from datetime import date
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics
from backend.app.services.signals import (
    generate_technical_signals,
    generate_sentiment_signals,
    generate_ai_hybrid_signals,
    generate_lstm_hybrid_signals,
)
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
from backend.app.services.lstm_service import (
    forecast_lstm,
)

def to_json_safe(value):
    """Convert NumPy and pandas values into JSON-compatible values."""

    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, np.ndarray):
        return to_json_safe(value.tolist())

    if isinstance(value, np.generic):
        return to_json_safe(value.item())

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None

    if isinstance(value, (int, np.integer)):
        return int(value)

    return value

router = APIRouter(prefix="/backtests", tags=["Backtests"])


class BacktestRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    start_date: date = date(2026, 1, 1)
    end_date: date = date(2026, 9, 5)
    initial_capital: float = Field(default=100000, gt=0)
    strategy: Literal[
        "technical",
        "sentiment",
        "hybrid_arima",
        "hybrid_lstm",
    ] = "technical"


def prepare_market_data(request: BacktestRequest) -> pd.DataFrame:
    prices = load_market_data(
        request.symbol,
        request.start_date.isoformat(),
        request.end_date.isoformat(),
    )

    if prices.empty:
        raise HTTPException(
            status_code=404,
            detail="No market data found for this symbol and date range.",
        )

    prices = prices.sort_index()

    news_items = fetch_news(request.symbol, count=20)
    news_df = news_to_dataframe(news_items)

    if not news_df.empty:
        news_df = analyze_news_dataframe(news_df)
        daily_sentiment = aggregate_daily_sentiment(news_df)
    else:
        daily_sentiment = pd.DataFrame(
            columns=["news_date", "sentiment_score", "news_count"]
        )

    combined = align_price_and_sentiment(
        prices,
        daily_sentiment,
    )

    combined = add_indicators(combined)
    return combined


def generate_rolling_forecasts(
    data: pd.DataFrame,
    model: str,
    min_history: int = 60,
) -> pd.DataFrame:
    """
    Each prediction uses only observations preceding that row.
    Actual current-day close is used only to evaluate the prediction,
    not to generate it.
    """
    df = data.copy()
    forecasts = [float("nan")] * len(df)

    for i in range(min_history, len(df)):
        history = df.iloc[:i]

        try:
            if model == "arima":
                prediction = forecast_arima(
                    history,
                    column="Close",
                    steps=1,
                ).iloc[0]
            else:
                prediction = forecast_lstm(
                    history,
                    column="Close",
                    lookback=30,
                    epochs=50,
                )

            prediction = float(prediction)

            if np.isfinite(prediction):
                forecasts[i] = prediction

        except (ValueError, RuntimeError, np.linalg.LinAlgError):
            continue

    column = (
        "forecast_price"
        if model == "arima"
        else "lstm_forecast_price"
    )

    df[column] = forecasts
    df = df.dropna(subset=[column]).copy()

    return df


@router.post("/run")
def run_backtest_api(request: BacktestRequest):
    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date.",
        )

    try:
        data = prepare_market_data(request)

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="Not enough market data to calculate indicators.",
            )

        if request.strategy == "technical":
            signals = generate_technical_signals(data)

        elif request.strategy == "sentiment":
            signals = generate_sentiment_signals(data)

        elif request.strategy == "hybrid_arima":
            data = generate_rolling_forecasts(data, "arima")

            if data.empty:
                raise HTTPException(
                    status_code=422,
                    detail="Not enough historical data for ARIMA forecasts.",
                )

            signals = generate_ai_hybrid_signals(data)

        else:
            data = generate_rolling_forecasts(data, "lstm")

            if data.empty:
                raise HTTPException(
                    status_code=422,
                    detail="Not enough historical data for LSTM forecasts.",
                )

            signals = generate_lstm_hybrid_signals(data)

        result, trades = run_backtest(
            signals,
            initial_capital=request.initial_capital,
        )

        metrics = calculate_metrics(
            result["Portfolio_Value"],
            trades,
            request.initial_capital,
        )

        equity_curve = []

        for index, value in result["Portfolio_Value"].items():
            if pd.isna(value) or not np.isfinite(float(value)):
                continue

            equity_curve.append({
                "date": pd.Timestamp(index).isoformat(),
                "portfolio_value": float(value),
            })

        serialized_trades = []

        for trade in trades:
            serialized_trades.append({
                "date": str(trade["date"]),
                "type": trade["type"],
                "price": float(trade["price"]),
                "quantity": int(trade["quantity"]),
                "profit_loss": (
                    float(trade["profit_loss"])
                    if "profit_loss" in trade
                    else None
                ),
                "reason": trade.get("reason"),
                "signal_reason": trade.get("signal_reason"),
                "signal_explanation": trade.get("signal_explanation"),
                "technical_direction": trade.get("technical_direction"),
                "sentiment_direction": trade.get("sentiment_direction"),
                "forecast_direction": (
                    trade.get("forecast_direction")
                    or trade.get("lstm_direction")
                ),
                "bullish_votes": trade.get("bullish_votes"),
                "bearish_votes": trade.get("bearish_votes"),
            })

        return to_json_safe({
            "symbol": request.symbol,
            "strategy": request.strategy,
            "metrics": metrics,
            "equity_curve": equity_curve,
            "trades": serialized_trades,
            "signal_distribution": {
                str(key): int(value)
                for key, value in signals["Signal"].value_counts().items()
            },
        })

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {str(exc)}",
        )
