import unittest
import pandas as pd

from backend.app.services.sentiment_service import (
    analyze_headlines,
    aggregate_sentiment,
)
from backend.app.services.signals import generate_sentiment_signals


class TestSentimentStrategy(unittest.TestCase):

    def test_finbert_sentiment_analysis(self):
        headlines = [
            "Reliance Industries reports strong quarterly earnings.",
            "Indian stock markets crash amid severe economic uncertainty.",
            "TCS announces a new board meeting next week.",
        ]

        results = analyze_headlines(headlines)

        self.assertEqual(len(results), 3)

        for result in results:
            self.assertIn("label", result)
            self.assertIn("confidence", result)
            self.assertIn("sentiment_score", result)

    def test_aggregate_sentiment(self):
        results = [
            {"sentiment_score": 0.5},
            {"sentiment_score": -0.5},
            {"sentiment_score": 0.0},
        ]

        average = aggregate_sentiment(results)

        self.assertEqual(average, 0.0)

    def test_sentiment_signals(self):
        data = pd.DataFrame({
            "Close": [2500, 2520, 2480],
            "sentiment_score": [
                0.5,
                -0.5,
                0.0,
            ],
        })

        result = generate_sentiment_signals(data)

        self.assertEqual(result.loc[0, "Signal"], "BUY")
        self.assertEqual(result.loc[1, "Signal"], "SELL")
        self.assertEqual(result.loc[2, "Signal"], "HOLD")


if __name__ == "__main__":
    unittest.main()