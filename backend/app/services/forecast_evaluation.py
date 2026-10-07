import numpy as np
import pandas as pd


def calculate_forecast_metrics(
    actual: pd.Series,
    predicted: pd.Series,
) -> dict:
    """
    Calculate forecasting accuracy metrics.
    """

    comparison = pd.DataFrame({
        "actual": pd.to_numeric(actual, errors="coerce"),
        "predicted": pd.to_numeric(predicted, errors="coerce"),
    }).dropna()

    if comparison.empty:
        raise ValueError("No valid actual/predicted values.")

    errors = (
        comparison["actual"]
        - comparison["predicted"]
    )

    mae = np.mean(np.abs(errors))

    rmse = np.sqrt(
        np.mean(errors ** 2)
    )

    actual_direction = np.sign(
        comparison["actual"].diff()
    )

    predicted_direction = np.sign(
        comparison["predicted"].diff()
    )

    valid_direction = (
        actual_direction != 0
    ) & (
        predicted_direction != 0
    )

    if valid_direction.sum() > 0:
        directional_accuracy = (
            actual_direction[valid_direction]
            == predicted_direction[valid_direction]
        ).mean() * 100
    else:
        directional_accuracy = 0.0

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "directional_accuracy": float(
            directional_accuracy
        ),
        "samples": int(len(comparison)),
    }