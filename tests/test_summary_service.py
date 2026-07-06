from app.services.summary_service import get_summary


def test_summary_returns_expected_keys() -> None:
    result = get_summary(start_date="2024-01-01", end_date="2024-01-31")

    expected_keys = {
        "start_date",
        "end_date",
        "row_count",
        "total_first_purchases",
        "total_all_purchases",
        "total_revenue",
        "total_discount",
        "total_paid_spend",
        "total_paid_clicks",
        "total_paid_impressions",
        "overall_ctr",
        "overall_cpc",
        "average_order_value",
        "roas_like",
    }

    assert expected_keys.issubset(result.keys())
    assert result["row_count"] > 0
    assert result["total_revenue"] >= 0


def test_summary_handles_empty_date_range() -> None:
    result = get_summary(start_date="1900-01-01", end_date="1900-01-31")

    assert result["row_count"] == 0
    assert result["total_all_purchases"] == 0
    assert result["roas_like"] == 0.0
