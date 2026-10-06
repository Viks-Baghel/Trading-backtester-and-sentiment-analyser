from backend.app.services.data_loader import load_market_data
from backend.app.services.indicators import add_indicators
from backend.app.services.signals import generate_technical_signals
from backend.app.services.engine import run_backtest
from backend.app.services.metrics import calculate_metrics


def run_test():

    data = load_market_data(
        symbol="RELIANCE.NS",
        start_date="2024-01-01",
        end_date="2025-01-01",
    )

    print("Downloaded rows:", len(data))

    data = add_indicators(data)

    print(
        "Indicators:",
        [
            "SMA_20",
            "SMA_50",
            "EMA_20",
            "RSI",
            "MACD",
        ],
    )

    data = generate_technical_signals(data)

    print(
        "Signals:",
        data["Signal"].value_counts().to_dict(),
    )

    results, trades = run_backtest(
        data,
        initial_capital=100000,
    )

    metrics = calculate_metrics(
        results["Portfolio_Value"],
        trades,
        100000,
    )

    print("\nBACKTEST RESULT")
    print("================")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print("\nTrades:", len(trades))


if __name__ == "__main__":
    run_test()