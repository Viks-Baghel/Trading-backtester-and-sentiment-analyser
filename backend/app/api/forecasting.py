
import numpy as np
import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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


# =========================================================
# REQUEST MODELS
# =========================================================

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


# =========================================================
# PRICE FORECAST ENDPOINT
# =========================================================

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

        if data.empty or "Close" not in data.columns:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No usable closing-price data was found "
                    "for this symbol and date range."
                ),
            )

        data = data.sort_index().copy()
        data["Close"] = pd.to_numeric(
            data["Close"],
            errors="coerce",
        )
        data = data.dropna(subset=["Close"])

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No valid closing prices were found.",
            )

        if request.model == "arima":
            forecasts = forecast_arima(
                data,
                column="Close",
                steps=request.steps,
            )

            forecast_prices = [
                float(value)
                for value in forecasts.tolist()
            ]

        else:
            if request.steps != 1:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "The current LSTM service supports "
                        "one-step forecasts only."
                    ),
                )

            forecast_prices = [
                forecast_lstm(
                    data,
                    column="Close",
                    lookback=30,
                    epochs=50,
                )
            ]

        if not forecast_prices:
            raise HTTPException(
                status_code=422,
                detail="The model returned no forecast values.",
            )

        current_price = float(data["Close"].iloc[-1])

        if (
            not np.isfinite(current_price)
            or current_price <= 0
        ):
            raise HTTPException(
                status_code=422,
                detail="The latest closing price is invalid.",
            )

        if not all(
            np.isfinite(value)
            for value in forecast_prices
        ):
            raise HTTPException(
                status_code=422,
                detail="The model produced invalid forecast values.",
            )

        latest_forecast = forecast_prices[-1]

        signal = calculate_forecast_signal(
            current_price=current_price,
            forecast_price=latest_forecast,
        )

        # Return actual historical prices for visualization.
        historical = data[["Close"]].tail(90)

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
            "last_historical_date": pd.Timestamp(
                data.index[-1]
            ).isoformat(),
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
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting failed: {exc}",
        ) from exc


# =========================================================
# OUT-OF-SAMPLE ARIMA EVALUATION
# =========================================================

@router.post("/evaluate")
def evaluate_arima_forecasts(
    request: ForecastEvaluationRequest,
):
    """
    Evaluate one-step-ahead ARIMA forecasts using an expanding
    training window.

    For each test observation:
    - Train using earlier closing prices only.
    - Predict the next closing price.
    - Compare against the actual closing price.
    - Compare against a naive forecast equal to the previous close.

    Directional accuracy measures whether the forecast correctly
    predicts UP, DOWN, or FLAT relative to the previous close.
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
            data["Close"],
            errors="coerce",
        )

        data = data.dropna(subset=["Close"])

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No valid closing prices were found.",
            )

        test_size = request.test_size

        # Ensure adequate training history.
        minimum_observations = 60 + test_size

        if len(data) < minimum_observations:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Not enough data. At least "
                    f"{minimum_observations} valid closing prices "
                    "are required."
                ),
            )

        split_index = len(data) - test_size

        actual_values = []
        predicted_values = []
        baseline_values = []
        previous_close_values = []
        test_dates = []

        # -----------------------------------------------------
        # EXPANDING-WINDOW EVALUATION
        # -----------------------------------------------------

        for index in range(split_index, len(data)):
            # The observation being predicted is excluded.
            training_data = data.iloc[:index]

            prediction = forecast_arima(
                training_data,
                column="Close",
                steps=1,
            )

            predicted_price = float(prediction.iloc[0])
            actual_price = float(data["Close"].iloc[index])
            previous_close = float(data["Close"].iloc[index - 1])

            values = (
                predicted_price,
                actual_price,
                previous_close,
            )

            if not all(np.isfinite(value) for value in values):
                continue

            predicted_values.append(predicted_price)
            actual_values.append(actual_price)

            # Naive baseline: next close equals previous close.
            baseline_values.append(previous_close)
            previous_close_values.append(previous_close)

            test_dates.append(
                pd.Timestamp(
                    data.index[index]
                ).strftime("%Y-%m-%d")
            )

        evaluated_samples = len(actual_values)

        if evaluated_samples < 5:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Too few valid predictions were generated "
                    "to evaluate the model."
                ),
            )

        # -----------------------------------------------------
        # ERROR METRICS
        # -----------------------------------------------------

        actual_array = np.asarray(
            actual_values,
            dtype=float,
        )

        arima_array = np.asarray(
            predicted_values,
            dtype=float,
        )

        baseline_array = np.asarray(
            baseline_values,
            dtype=float,
        )

        previous_array = np.asarray(
            previous_close_values,
            dtype=float,
        )

        arima_errors = actual_array - arima_array
        baseline_errors = actual_array - baseline_array

        arima_mae = float(
            np.mean(np.abs(arima_errors))
        )

        arima_rmse = float(
            np.sqrt(np.mean(arima_errors ** 2))
        )

        baseline_mae = float(
            np.mean(np.abs(baseline_errors))
        )

        baseline_rmse = float(
            np.sqrt(np.mean(baseline_errors ** 2))
        )

        # -----------------------------------------------------
        # DIRECTIONAL ACCURACY
        # -----------------------------------------------------

        actual_movements = actual_array - previous_array
        predicted_movements = arima_array - previous_array

        actual_directions = np.sign(actual_movements)
        predicted_directions = np.sign(predicted_movements)

        directional_accuracy = float(
            np.mean(
                actual_directions == predicted_directions
            ) * 100
        )

        # The naive price baseline predicts the previous closing price.
        # It therefore predicts no directional movement.
        # Do not score this as 0% directional accuracy.
        baseline_directional_accuracy = None

        # Positive improvement means ARIMA has lower error.
        mae_improvement_percent = (
            float(
                (baseline_mae - arima_mae)
                / baseline_mae
                * 100
            )
            if baseline_mae > 0
            else None
        )

        rmse_improvement_percent = (
            float(
                (baseline_rmse - arima_rmse)
                / baseline_rmse
                * 100
            )
            if baseline_rmse > 0
            else None
        )

        metrics = {
            "arima": {
                "mae": arima_mae,
                "rmse": arima_rmse,
                "directional_accuracy": directional_accuracy,
                "samples": evaluated_samples,
            },
            "naive_baseline": {
                "mae": baseline_mae,
                "rmse": baseline_rmse,
                "directional_accuracy": (
                    baseline_directional_accuracy
                ),
                "samples": evaluated_samples,
            },
            "improvement_percent": {
                "mae": mae_improvement_percent,
                "rmse": rmse_improvement_percent,
            },
        }

        # -----------------------------------------------------
        # PER-OBSERVATION RESULTS
        # -----------------------------------------------------

        predictions = []

        for index in range(evaluated_samples):
            actual_direction = (
                "UP"
                if actual_movements[index] > 0
                else "DOWN"
                if actual_movements[index] < 0
                else "FLAT"
            )

            predicted_direction = (
                "UP"
                if predicted_movements[index] > 0
                else "DOWN"
                if predicted_movements[index] < 0
                else "FLAT"
            )

            predictions.append(
                {
                    "date": test_dates[index],
                    "previous_close": float(
                        previous_array[index]
                    ),
                    "actual_price": float(
                        actual_array[index]
                    ),
                    "predicted_price": float(
                        arima_array[index]
                    ),
                    "baseline_price": float(
                        baseline_array[index]
                    ),
                    "absolute_error": float(
                        abs(
                            actual_array[index]
                            - arima_array[index]
                        )
                    ),
                    "baseline_absolute_error": float(
                        abs(
                            actual_array[index]
                            - baseline_array[index]
                        )
                    ),
                    "actual_direction": actual_direction,
                    "predicted_direction": predicted_direction,
                }
            )

        return {
            "symbol": request.symbol,
            "model": "arima",
            "evaluation_method": (
                "expanding_window_one_step_ahead"
            ),
            "training_cutoff_date": pd.Timestamp(
                data.index[split_index - 1]
            ).strftime("%Y-%m-%d"),
            "requested_test_size": test_size,
            "evaluated_samples": evaluated_samples,
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
