
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import pandas as pd

from backend.app.services.forecast_evaluation import (
    calculate_forecast_metrics,
)
from backend.app.services.data_loader import load_market_data
from backend.app.services.forecasting_service import (
    forecast_arima,
    calculate_forecast_signal,
)
from backend.app.services.lstm_service import forecast_lstm

router = APIRouter(
    prefix="/forecasting",
    tags=["Forecasting"],
)


class ForecastRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    start_date: str = "2025-01-01"
    end_date: str = "2026-09-01"
    model: str = "arima"
    steps: int = Field(default=1, ge=1, le=10)


class ForecastEvaluationRequest(BaseModel):
    symbol: str = "RELIANCE.NS"
    start_date: str = "2024-01-01"
    end_date: str = "2026-10-10"
    test_size: int = Field(default=20, ge=5, le=30)


@router.post("/predict")
def predict_price(request: ForecastRequest):
    if request.model not in {"arima", "lstm"}:
        raise HTTPException(
            status_code=400,
            detail="Model must be 'arima' or 'lstm'.",
        )

    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date.",
        )

    try:
        data = load_market_data(
            request.symbol,
            request.start_date,
            request.end_date,
        )

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No market data found for this symbol and date range.",
            )

        data = data.sort_index()

        if request.model == "arima":
            forecasts = forecast_arima(
                data,
                column="Close",
                steps=request.steps,
            )
            forecast_prices = [
                float(value) for value in forecasts.tolist()
            ]
        else:
            if request.steps != 1:
                raise HTTPException(
                    status_code=400,
                    detail="The current LSTM service supports one-step forecasts only.",
                )

            forecast_prices = [
                forecast_lstm(
                    data,
                    column="Close",
                    lookback=30,
                    epochs=50,
                )
            ]

        current_price = float(data["Close"].dropna().iloc[-1])

        if not np.isfinite(current_price) or current_price <= 0:
            raise HTTPException(
                status_code=422,
                detail="The latest closing price is invalid.",
            )

        latest_forecast = forecast_prices[-1]

        if not np.isfinite(latest_forecast):
            raise HTTPException(
                status_code=422,
                detail="The model produced an invalid forecast.",
            )

        signal = calculate_forecast_signal(
            current_price=current_price,
            forecast_price=latest_forecast,
        )

        
        historical = data[["Close"]].dropna().tail(90)

        historical_prices = [
            {
                "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
                "close": float(row["Close"]),
            }
            for index, row in historical.iterrows()
        ]

        return {
            "symbol": request.symbol,
            "model": request.model,
            "forecast_steps": request.steps,
            "last_historical_date": data.index[-1].isoformat(),
            "current_price": current_price,
            "historical_prices": historical_prices,
            "forecast_prices": forecast_prices,
            "forecast_price": latest_forecast,
            "expected_return_percent": signal[
                "expected_return_percent"
            ],
            "direction": signal["direction"],
            "disclaimer": (
                "Model forecasts are estimates, not guaranteed "
                "future prices or investment advice."
            ),
        }

    except HTTPException:
        raise
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting failed: {str(exc)}",
        ) from exc


@router.post("/evaluate")
def evaluate_arima_forecasts(request: ForecastEvaluationRequest):
    """
    Evaluate one-step-ahead ARIMA predictions on a chronological
    holdout period. Each prediction uses only prices before its date.
    """
    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date.",
        )

    try:
        data = load_market_data(
            request.symbol,
            request.start_date,
            request.end_date,
        )

        if data.empty or "Close" not in data.columns:
            raise HTTPException(
                status_code=404,
                detail="No usable closing-price data was found.",
            )

        data = data.sort_index().copy()
        data["Close"] = pd.to_numeric(
            data["Close"], errors="coerce"
        )
        data = data.dropna(subset=["Close"])

        test_size = request.test_size

        # Keep enough earlier observations to fit ARIMA.
        if len(data) < 60 + test_size:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Not enough data. At least {60 + test_size} "
                    "valid closing prices are required."
                ),
            )

        split_index = len(data) - test_size
        actual_values = []
        predicted_values = []
        test_dates = []

        for index in range(split_index, len(data)):
            # Strictly exclude the price being predicted.
            training_data = data.iloc[:index]

            prediction = forecast_arima(
                training_data,
                column="Close",
                steps=1,
            )

            predicted_price = float(prediction.iloc[0])
            actual_price = float(data["Close"].iloc[index])

            if (
                not np.isfinite(predicted_price)
                or not np.isfinite(actual_price)
            ):
                continue

            predicted_values.append(predicted_price)
            actual_values.append(actual_price)
            test_dates.append(
                pd.Timestamp(data.index[index]).strftime("%Y-%m-%d")
            )

        if len(actual_values) < 5:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Too few valid predictions were generated "
                    "to evaluate the model."
                ),
            )

        metrics = calculate_forecast_metrics(
            actual=pd.Series(actual_values),
            predicted=pd.Series(predicted_values),
        )

        predictions = [
            {
                "date": test_dates[index],
                "actual_price": actual_values[index],
                "predicted_price": predicted_values[index],
                "absolute_error": abs(
                    actual_values[index] - predicted_values[index]
                ),
            }
            for index in range(len(actual_values))
        ]

        return {
            "symbol": request.symbol,
            "model": "arima",
            "evaluation_method": "expanding_window_one_step_ahead",
            "training_cutoff_date": pd.Timestamp(
                data.index[split_index - 1]
            ).strftime("%Y-%m-%d"),
            "requested_test_size": test_size,
            "evaluated_samples": len(actual_values),
            "metrics": metrics,
            "predictions": predictions,
            "disclaimer": (
                "Historical out-of-sample performance does not "
                "guarantee future forecasting accuracy."
            ),
        }

    except HTTPException:
        raise
    except (ValueError, IndexError, RuntimeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Forecast evaluation failed: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Forecast evaluation failed: {exc}",
        ) from exc
