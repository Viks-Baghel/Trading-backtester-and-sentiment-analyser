import unittest

import numpy as np
import pandas as pd

from backend.app.services.forecasting_service import (
    forecast_arima,
)
from backend.app.services.lstm_service import (
    forecast_lstm,
)
from backend.app.services.forecast_evaluation import (
    calculate_forecast_metrics,
)


class TestForecastComparison(unittest.TestCase):

    def test_forecast_metrics(self):

        actual = pd.Series([
            100,
            102,
            104,
            103,
            106,
        ])

        predicted = pd.Series([
            101,
            101,
            105,
            104,
            105,
        ])

        metrics = calculate_forecast_metrics(
            actual,
            predicted,
        )

        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn(
            "directional_accuracy",
            metrics,
        )

        self.assertGreaterEqual(
            metrics["mae"],
            0,
        )

        self.assertGreaterEqual(
            metrics["rmse"],
            0,
        )

    def test_arima_forecast(self):

        rng = np.random.default_rng(42)

        prices = 100 + np.cumsum(
            rng.normal(0.2, 1.0, 100)
        )

        data = pd.DataFrame({
            "Close": prices
        })

        forecast = forecast_arima(
            data,
            column="Close",
            steps=1,
        )

        self.assertEqual(
            len(forecast),
            1,
        )

        self.assertTrue(
            np.isfinite(forecast.iloc[0])
        )

    def test_lstm_forecast(self):

        rng = np.random.default_rng(42)

        prices = 100 + np.cumsum(
            rng.normal(0.2, 1.0, 100)
        )

        data = pd.DataFrame({
            "Close": prices
        })

        forecast = forecast_lstm(
            data,
            column="Close",
            lookback=20,
            epochs=10,
        )

        self.assertTrue(
            np.isfinite(forecast)
        )

        self.assertGreater(
            forecast,
            0,
        )


if __name__ == "__main__":
    unittest.main()