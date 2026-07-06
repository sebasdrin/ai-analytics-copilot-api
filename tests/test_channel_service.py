from app.services.channel_service import get_channel_performance


def test_channel_performance_returns_channel_rows() -> None:
    result = get_channel_performance(
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result["row_count"] > 0
    assert len(result["channels"]) > 0

    first_channel = result["channels"][0]
    expected_keys = {
        "channel",
        "spend",
        "clicks",
        "impressions",
        "purchases",
        "revenue",
        "ctr",
        "cpc",
        "cpm",
    }
    assert expected_keys.issubset(first_channel.keys())


def test_channel_filter_limits_results_to_one_channel() -> None:
    result = get_channel_performance(
        start_date="2024-01-01",
        end_date="2024-01-31",
        channel="google_paid_search",
    )

    assert result["row_count"] > 0
    assert len(result["channels"]) == 1
    assert result["channels"][0]["channel"] == "google_paid_search"
