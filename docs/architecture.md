# Architecture

## Overview

The API is a simple layered FastAPI application. It reads processed marketing
performance CSV files, calculates metrics in service functions, and exposes the
results through thin API endpoints.

```text
Client
  |
  v
FastAPI routes in app/main.py
  |
  v
Service layer in app/services/
  |
  v
Data loader in app/data_loader.py
  |
  v
Processed CSV files in data/processed/
```

The anomaly route adds one extra layer:

```text
/anomaly-report route
  |
  v
app/services/anomaly_service.py
  |
  v
app/ml/anomaly_detector.py
  |
  v
PyTorch autoencoder
```

## Folder Structure

```text
app/
  data_loader.py              Loads processed CSV files
  main.py                     Defines FastAPI routes
  services/
    summary_service.py        Business-level summary metrics
    channel_service.py        Channel-level performance metrics
    anomaly_service.py        Anomaly report orchestration
  ml/
    anomaly_detector.py       Feature preparation and autoencoder scoring

tests/                        pytest tests for services and API routes
docs/                         Architecture and ML notes
data/processed/               Prepared CSV files used by the app
```

## Data Flow

1. A user calls an endpoint such as `/summary`.
2. `app/main.py` receives query parameters like `start_date` and `end_date`.
3. The endpoint calls a service function.
4. The service loads the relevant DataFrame through `app/data_loader.py`.
5. The service filters, aggregates, and formats the result.
6. FastAPI serializes the returned dictionary as JSON.

## Why Use A Data Loader

The data loader centralizes file paths and CSV loading logic. This avoids repeating
path handling across services and keeps future changes simple. For example, if the
project later moves from CSV files to SQL queries, most endpoint logic can stay the
same while the data access layer changes.

## Why Keep Services Separate From Endpoints

API endpoints should be thin. Their job is to accept request parameters and return
responses. Business logic belongs in services because services are easier to test,
reuse, and explain.

For example, `/summary` calls `get_summary()`. The endpoint does not know the details
of CTR, CPC, revenue, or ROAS-like calculations.

## Request Flow By Endpoint

### `/summary`

- Loads `business_daily_summary.csv`
- Filters by optional date range
- Aggregates purchases, revenue, discount, spend, clicks, impressions, CTR, CPC,
  average order value, and ROAS-like metric

### `/channel-performance`

- Loads `channel_daily_performance.csv`
- Filters by optional date range and channel
- Groups by channel
- Returns spend, clicks, impressions, purchases, revenue, CTR, CPC, and CPM

### `/anomaly-report`

- Loads `channel_daily_performance.csv`
- Filters by optional date range and channel
- Selects numeric channel features
- Standardizes features
- Scores rows using the PyTorch autoencoder
- Returns the highest-scoring rows as likely anomalies

## Where PyTorch Fits

PyTorch is isolated in `app/ml/anomaly_detector.py`. This keeps ML code separate from
API and business-summary logic. The service layer prepares the request-specific data
and asks the detector for scores. The detector does not know about FastAPI.
