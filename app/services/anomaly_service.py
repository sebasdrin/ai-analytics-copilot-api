from datetime import date
from typing import Any

import pandas as pd

from app.data_loader import load_channel_data
from app.ml.anomaly_detector import (
    FEATURE_COLUMNS,
    detect_with_autoencoder,
    prepare_feature_matrix,
)


def _parse_optional_date(value: date | str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    return pd.to_datetime(value)


def get_anomaly_report(
    start_date: date | str | None = None,
    end_date: date | str | None = None,
    channel: str | None = None,
    limit: int = 10,
    max_training_rows: int = 5000,
) -> dict[str, Any]:
    """Return the highest-scoring channel performance anomalies."""
    df = load_channel_data().copy()

    start = _parse_optional_date(start_date)
    end = _parse_optional_date(end_date)

    if start is not None:
        df = df[df["DATE_DAY"] >= start]
    if end is not None:
        df = df[df["DATE_DAY"] <= end]
    if channel:
        df = df[df["channel"].str.lower() == channel.lower()]

    response: dict[str, Any] = {
        "filters": {
            "start_date": start.date().isoformat() if start is not None else None,
            "end_date": end.date().isoformat() if end is not None else None,
            "channel": channel,
        },
        "row_count": int(len(df)),
        "detector_type": None,
        "threshold": None,
        "feature_columns": FEATURE_COLUMNS,
        "anomalies": [],
    }

    if df.empty:
        return response

    # Keep training fast for API usage while preserving chronological coverage.
    if len(df) > max_training_rows:
        df = df.sample(n=max_training_rows, random_state=42).sort_values("DATE_DAY")

    features, _ = prepare_feature_matrix(df)
    result = detect_with_autoencoder(features)

    scored = df.copy()
    scored["anomaly_score"] = result.scores
    scored["is_anomaly"] = scored["anomaly_score"] >= result.threshold
    scored = scored.sort_values("anomaly_score", ascending=False).head(limit)

    response["row_count"] = int(len(df))
    response["detector_type"] = result.detector_type
    response["threshold"] = float(result.threshold)
    response["anomalies"] = [
        {
            "date": row["DATE_DAY"].date().isoformat(),
            "channel": str(row["channel"]),
            "spend": round(float(row["spend"]), 2),
            "clicks": int(row["clicks"]),
            "impressions": int(row["impressions"]),
            "ctr": float(row["ctr"]),
            "cpc": float(row["cpc"]),
            "cpm": float(row["cpm"]),
            "anomaly_score": float(row["anomaly_score"]),
            "is_anomaly": bool(row["is_anomaly"]),
        }
        for _, row in scored.iterrows()
    ]

    return response
