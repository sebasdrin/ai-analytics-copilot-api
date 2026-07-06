from datetime import date
from typing import Any

import pandas as pd

from app.data_loader import load_channel_data


ALLOWED_SORT_FIELDS = {
    "spend",
    "clicks",
    "impressions",
    "ctr",
    "cpc",
    "cpm",
    "revenue",
    "purchases",
}


def _parse_optional_date(value: date | str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    return pd.to_datetime(value)


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def get_channel_performance(
    start_date: date | str | None = None,
    end_date: date | str | None = None,
    channel: str | None = None,
    sort_by: str = "spend",
) -> dict[str, Any]:
    """Aggregate paid media performance by channel for an optional filter."""
    df = load_channel_data().copy()

    start = _parse_optional_date(start_date)
    end = _parse_optional_date(end_date)

    if start is not None:
        df = df[df["DATE_DAY"] >= start]
    if end is not None:
        df = df[df["DATE_DAY"] <= end]
    if channel:
        df = df[df["channel"].str.lower() == channel.lower()]

    sort_field = sort_by if sort_by in ALLOWED_SORT_FIELDS else "spend"

    response: dict[str, Any] = {
        "filters": {
            "start_date": start.date().isoformat() if start is not None else None,
            "end_date": end.date().isoformat() if end is not None else None,
            "channel": channel,
            "sort_by": sort_field,
        },
        "row_count": int(len(df)),
        "channels": [],
    }

    if df.empty:
        return response

    grouped = (
        df.groupby("channel", as_index=False)
        .agg(
            spend=("spend", "sum"),
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
            purchases=("ALL_PURCHASES", "sum"),
            revenue=("ALL_PURCHASES_ORIGINAL_PRICE", "sum"),
        )
        .fillna(0)
    )

    grouped["ctr"] = grouped.apply(
        lambda row: _safe_divide(row["clicks"], row["impressions"]), axis=1
    )
    grouped["cpc"] = grouped.apply(
        lambda row: _safe_divide(row["spend"], row["clicks"]), axis=1
    )
    grouped["cpm"] = grouped.apply(
        lambda row: _safe_divide(row["spend"] * 1000, row["impressions"]), axis=1
    )

    grouped = grouped.sort_values(sort_field, ascending=False)

    response["channels"] = [
        {
            "channel": str(row["channel"]),
            "spend": round(float(row["spend"]), 2),
            "clicks": int(row["clicks"]),
            "impressions": int(row["impressions"]),
            "purchases": int(row["purchases"]),
            "revenue": round(float(row["revenue"]), 2),
            "ctr": float(row["ctr"]),
            "cpc": float(row["cpc"]),
            "cpm": float(row["cpm"]),
        }
        for _, row in grouped.iterrows()
    ]

    return response
