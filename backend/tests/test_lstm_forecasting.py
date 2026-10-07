
import unittest

import numpy as np
import pandas as pd

from backend.app.services.lstm_service import forecast_lstm


class TestLSTMForecasting(unittest.TestCase):

    def test_lstm_prediction(self):
        rng = np.random.default_rng(42)

        prices = 100 + np.cumsum(
            rng.normal(0.2, 1.0, 100)
        )

        data = pd.DataFrame({
            "Close": prices
        })

        prediction = forecast_lstm(
            data,
            lookback=20,
            epochs=10,
        )

        self.assertTrue(np.isfinite(prediction))
        self.assertGreater(prediction, 0)

    def test_insufficient_history(self):
        data = pd.DataFrame({
            "Close": [100, 101, 102]
        })

        with self.assertRaises(ValueError):
            forecast_lstm(data, lookback=20)


if __name__ == "__main__":
    unittest.main()
