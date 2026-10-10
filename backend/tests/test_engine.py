import unittest
import pandas as pd

from backend.app.services.engine import run_backtest


class TestBacktestEngine(unittest.TestCase):

    def test_end_of_backtest_reason(self):

        data = pd.DataFrame(
            {
                "Close": [100.0, 105.0, 110.0],
                "Signal": ["BUY", "HOLD", "HOLD"],
            },
            index=pd.date_range(
                "2026-01-01",
                periods=3,
            ),
        )

        _, trades = run_backtest(
            data,
            initial_capital=100000.0,
        )

        final_trade = trades[-1]

        self.assertEqual(
            final_trade["type"],
            "SELL",
        )

        self.assertEqual(
            final_trade["reason"],
            "END_OF_BACKTEST",
        )

        self.assertEqual(
            final_trade["signal_reason"],
            "END_OF_BACKTEST",
        )


if __name__ == "__main__":
    unittest.main()