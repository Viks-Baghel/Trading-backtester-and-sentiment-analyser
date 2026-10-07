
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.preprocessing import MinMaxScaler


class LSTMPriceModel(nn.Module):
    def __init__(self, hidden_size=32):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        output, _ = self.lstm(x)
        return self.fc(output[:, -1, :])


def forecast_lstm(
    data: pd.DataFrame,
    column: str = "Close",
    lookback: int = 30,
    epochs: int = 50,
    learning_rate: float = 0.001,
) -> float:
    """
    Predict the next closing price using only the
    historical prices supplied in data.
    """

    if column not in data.columns:
        raise ValueError(f"Column '{column}' not found.")

    if lookback < 2:
        raise ValueError("lookback must be at least 2.")

    if epochs < 1:
        raise ValueError("epochs must be positive.")

    prices = (
        pd.to_numeric(data[column], errors="coerce")
        .dropna()
        .to_numpy(dtype=np.float32)
    )

    if len(prices) < lookback + 10:
        raise ValueError("Not enough historical data for LSTM.")

    if not np.isfinite(prices).all():
        raise ValueError("Prices must be finite.")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(
        prices.reshape(-1, 1)
    ).astype(np.float32)

    x_values = []
    y_values = []

    for i in range(lookback, len(scaled)):
        x_values.append(scaled[i - lookback:i])
        y_values.append(scaled[i])

    X = torch.tensor(
        np.asarray(x_values),
        dtype=torch.float32,
    )
    y = torch.tensor(
        np.asarray(y_values),
        dtype=torch.float32,
    )

    torch.manual_seed(42)
    model = LSTMPriceModel(hidden_size=64)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.0005,
    )
    criterion = nn.MSELoss()

    model.train()

    for _ in range(epochs):
        optimizer.zero_grad()
        predictions = model(X)
        loss = criterion(predictions, y)
        loss.backward()
        optimizer.step()

    model.eval()

    last_window = torch.tensor(
        scaled[-lookback:].reshape(1, lookback, 1),
        dtype=torch.float32,
    )

    with torch.no_grad():
        predicted_scaled = model(last_window).numpy()

    predicted_price = scaler.inverse_transform(
        predicted_scaled
    )[0, 0]

    return float(predicted_price)
