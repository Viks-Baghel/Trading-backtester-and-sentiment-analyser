import unittest

from backend.app.services.forecasting_service import (
    compare_forecasts,
)


class TestForecastModels(unittest.TestCase):

    def test_models_agree(self):

        result = compare_forecasts(
            current_price=100,
            arima_forecast=102,
            lstm_forecast=103,
        )

        self.assertEqual(
            result["arima_direction"],
            "BULLISH",
        )

        self.assertEqual(
            result["lstm_direction"],
            "BULLISH",
        )

        self.assertTrue(
            result["models_agree"]
        )

    def test_models_disagree(self):

        result = compare_forecasts(
            current_price=100,
            arima_forecast=102,
            lstm_forecast=98,
        )

        self.assertEqual(
            result["arima_direction"],
            "BULLISH",
        )

        self.assertEqual(
            result["lstm_direction"],
            "BEARISH",
        )

        self.assertFalse(
            result["models_agree"]
        )


if __name__ == "__main__":
    unittest.main()