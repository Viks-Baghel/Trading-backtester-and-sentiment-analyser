import unittest

import pandas as pd

from backend.app.services.signals import (
    generate_lstm_hybrid_signals,
)


class TestLSTMHybridStrategy(unittest.TestCase):

    def create_data(
        self,
        sentiment,
        lstm_forecast,
    ):
        return pd.DataFrame({
            "Close": [100.0],
            "SMA_20": [110.0],
            "SMA_50": [100.0],
            "RSI": [60.0],
            "MACD": [5.0],
            "MACD_SIGNAL": [2.0],
            "sentiment_score": [sentiment],
            "lstm_forecast_price": [
                lstm_forecast
            ],
        })

    def test_buy_signal(self):

        data = self.create_data(
            sentiment=0.8,
            lstm_forecast=105.0,
        )

        result = generate_lstm_hybrid_signals(
            data
        )

        self.assertEqual(
            result.loc[0, "Signal"],
            "BUY",
        )

        self.assertGreaterEqual(
            result.loc[0, "bullish_votes"],
            2,
        )

    def test_sell_signal(self):

        data = pd.DataFrame({
            "Close": [100.0],
            "SMA_20": [90.0],
            "SMA_50": [100.0],
            "RSI": [40.0],
            "MACD": [1.0],
            "MACD_SIGNAL": [5.0],
            "sentiment_score": [-0.8],
            "lstm_forecast_price": [95.0],
        })

        result = generate_lstm_hybrid_signals(
            data
        )

        self.assertEqual(
            result.loc[0, "Signal"],
            "SELL",
        )

        self.assertGreaterEqual(
            result.loc[0, "bearish_votes"],
            2,
        )

    def test_explainability(self):

        data = self.create_data(
            sentiment=0.8,
            lstm_forecast=105.0,
        )

        result = generate_lstm_hybrid_signals(
            data
        )

        self.assertIn(
            "Technical:",
            result.loc[0, "signal_explanation"],
        )

        self.assertIn(
            "Sentiment:",
            result.loc[0, "signal_explanation"],
        )

        self.assertIn(
            "LSTM:",
            result.loc[0, "signal_explanation"],
        )


if __name__ == "__main__":
    unittest.main()