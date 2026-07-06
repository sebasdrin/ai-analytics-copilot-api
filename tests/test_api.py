from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint_returns_200() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AI Analytics Copilot API"


def test_summary_endpoint_returns_200() -> None:
    response = client.get("/summary?start_date=2024-01-01&end_date=2024-01-31")

    assert response.status_code == 200
    assert response.json()["row_count"] > 0


def test_channel_performance_endpoint_returns_200() -> None:
    response = client.get(
        "/channel-performance?start_date=2024-01-01&end_date=2024-01-31"
    )

    assert response.status_code == 200
    assert len(response.json()["channels"]) > 0


def test_anomaly_report_endpoint_returns_200() -> None:
    response = client.get(
        "/anomaly-report?start_date=2024-01-01&end_date=2024-01-07&limit=3"
    )

    assert response.status_code == 200
    assert len(response.json()["anomalies"]) <= 3
