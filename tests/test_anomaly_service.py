from app.services.anomaly_service import get_anomaly_report


def test_anomaly_report_returns_expected_shape() -> None:
    result = get_anomaly_report(
        start_date="2024-01-01",
        end_date="2024-01-07",
        limit=5,
        max_training_rows=200,
    )

    assert result["row_count"] > 0
    assert result["detector_type"] == "pytorch_autoencoder"
    assert result["threshold"] is not None
    assert len(result["anomalies"]) <= 5

    first_anomaly = result["anomalies"][0]
    expected_keys = {
        "date",
        "channel",
        "spend",
        "clicks",
        "impressions",
        "ctr",
        "cpc",
        "cpm",
        "anomaly_score",
        "is_anomaly",
    }
    assert expected_keys.issubset(first_anomaly.keys())
