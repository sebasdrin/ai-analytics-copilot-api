from datetime import date
from typing import Any

import pandas as pd

from app.data_loader import load_summary_data


def _parse_optional_date(value: date | str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    return pd.to_datetime(value)


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def get_summary(
    start_date: date | str | None = None,
    end_date: date | str | None = None,
) -> dict[str, Any]:
    """Return aggregate business metrics for an optional date range."""
    df = load_summary_data().copy()

    start = _parse_optional_date(start_date)
    end = _parse_optional_date(end_date)

    if start is not None:
        df = df[df["DATE_DAY"] >= start]
    if end is not None:
        df = df[df["DATE_DAY"] <= end]

    if df.empty:
        return {
            "start_date": start.date().isoformat() if start is not None else None,
            "end_date": end.date().isoformat() if end is not None else None,
            "row_count": 0,
            "total_first_purchases": 0,
            "total_all_purchases": 0,
            "total_revenue": 0.0,
            "total_discount": 0.0,
            "total_paid_spend": 0.0,
            "total_paid_clicks": 0.0,
            "total_paid_impressions": 0.0,
            "overall_ctr": 0.0,
            "overall_cpc": 0.0,
            "average_order_value": 0.0,
            "roas_like": 0.0,
        }

    total_first_purchases = float(df["FIRST_PURCHASES"].sum())
    total_all_purchases = float(df["ALL_PURCHASES"].sum())
    total_revenue = float(df["ALL_PURCHASES_ORIGINAL_PRICE"].sum())
    total_discount = float(df["ALL_PURCHASES_GROSS_DISCOUNT"].sum())
    total_paid_spend = float(df["total_paid_spend"].sum())
    total_paid_clicks = float(df["total_paid_clicks"].sum())
    total_paid_impressions = float(df["total_paid_impressions"].sum())

    return {
        "start_date": df["DATE_DAY"].min().date().isoformat(),
        "end_date": df["DATE_DAY"].max().date().isoformat(),
        "row_count": int(len(df)),
        "total_first_purchases": int(total_first_purchases),
        "total_all_purchases": int(total_all_purchases),
        "total_revenue": round(total_revenue, 2),
        "total_discount": round(total_discount, 2),
        "total_paid_spend": round(total_paid_spend, 2),
        "total_paid_clicks": int(total_paid_clicks),
        "total_paid_impressions": int(total_paid_impressions),
        "overall_ctr": _safe_divide(total_paid_clicks, total_paid_impressions),
        "overall_cpc": _safe_divide(total_paid_spend, total_paid_clicks),
        "average_order_value": _safe_divide(total_revenue, total_all_purchases),
        "roas_like": _safe_divide(total_revenue, total_paid_spend),
    }
