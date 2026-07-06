from datetime import date

from fastapi import FastAPI, Query

from app.services.anomaly_service import get_anomaly_report
from app.services.channel_service import get_channel_performance
from app.services.summary_service import get_summary


app = FastAPI(
    title="AI Analytics Copilot API",
    description="FastAPI backend for marketing performance summaries and anomaly detection.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    """Health check and project landing endpoint."""
    return {
        "message": "AI Analytics Copilot API",
        "docs": "/docs",
    }


@app.get("/summary")
def summary(
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """Return aggregate business metrics for an optional date range."""
    return get_summary(start_date=start_date, end_date=end_date)


@app.get("/channel-performance")
def channel_performance(
    start_date: date | None = None,
    end_date: date | None = None,
    channel: str | None = None,
    sort_by: str = Query(default="spend"),
) -> dict:
    """Return channel-level performance aggregates."""
    return get_channel_performance(
        start_date=start_date,
        end_date=end_date,
        channel=channel,
        sort_by=sort_by,
    )


@app.get("/anomaly-report")
def anomaly_report(
    start_date: date | None = None,
    end_date: date | None = None,
    channel: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
) -> dict:
    """Return likely anomalies from channel-level performance data."""
    return get_anomaly_report(
        start_date=start_date,
        end_date=end_date,
        channel=channel,
        limit=limit,
    )
