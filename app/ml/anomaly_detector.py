from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


FEATURE_COLUMNS = ["spend", "clicks", "impressions", "ctr", "cpc", "cpm"]


@dataclass
class DetectionResult:
    """Container for anomaly scores and threshold metadata."""

    scores: np.ndarray
    threshold: float
    detector_type: str


def prepare_feature_matrix(df: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    """Select and standardize numeric features for anomaly detection."""
    feature_df = df[FEATURE_COLUMNS].copy()
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan).fillna(0)

    values = feature_df.to_numpy(dtype=np.float32)
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    std[std == 0] = 1.0

    normalized = (values - mean) / std
    return normalized.astype(np.float32), feature_df


def detect_with_autoencoder(
    features: np.ndarray,
    epochs: int = 20,
    learning_rate: float = 0.01,
) -> DetectionResult:
    """Train a small PyTorch autoencoder and score rows by reconstruction error."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("PyTorch is not installed.") from exc

    torch.manual_seed(42)

    class Autoencoder(nn.Module):
        def __init__(self, input_size: int) -> None:
            super().__init__()
            hidden_size = max(3, input_size // 2)
            self.encoder = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
            )
            self.decoder = nn.Linear(hidden_size, input_size)

        def forward(self, batch: torch.Tensor) -> torch.Tensor:
            encoded = self.encoder(batch)
            return self.decoder(encoded)

    tensor = torch.tensor(features, dtype=torch.float32)
    model = Autoencoder(input_size=tensor.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        reconstructed = model(tensor)
        loss = loss_fn(reconstructed, tensor)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        reconstructed = model(tensor)
        errors = torch.mean((reconstructed - tensor) ** 2, dim=1).cpu().numpy()

    threshold = float(np.percentile(errors, 95))
    return DetectionResult(
        scores=errors,
        threshold=threshold,
        detector_type="pytorch_autoencoder",
    )
