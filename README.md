# AI Analytics Copilot API

A small FastAPI backend for marketing performance analytics. The project loads processed
CSV data, returns business and channel summaries, and flags unusual channel-performance
rows with a simple anomaly detector.

This is designed as a portfolio project for Python, data, API, and ML-adjacent roles.
The code favors clear service-layer functions and explainable model logic over complex
production infrastructure.

## Business Problem

Marketing teams need quick answers to questions like:

- How did overall performance change during a date range?
- Which paid channels drove the most spend, clicks, impressions, and revenue?
- Which channel-day rows look unusual and should be investigated?

The API exposes those answers as structured JSON so they could later be used by a UI,
dashboard, notebook, or LLM layer.

## Tech Stack

- Python
- FastAPI
- pandas
- PyTorch
- pytest
- Uvicorn

## Dataset

The app uses processed CSV files created from earlier notebook exploration:

- `data/processed/business_daily_summary.csv`
- `data/processed/channel_daily_performance.csv`

Raw source files are preserved separately:

- `data/conjura_mmm_data.csv`
- `data/conjura_mmm_data_dictionary.xlsx`

The summary dataset contains daily business metrics. The channel dataset contains
daily paid-channel metrics such as spend, clicks, impressions, CTR, CPC, and CPM.

## Install

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

If you are using the existing local venv on Windows:

```bash
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run The API

```bash
uvicorn app.main:app --reload
```

Then open:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Endpoints

### `GET /`

Health check and project landing response.

Example:

```bash
curl http://127.0.0.1:8000/
```

### `GET /summary`

Returns aggregate business metrics for an optional date range.

Example:

```bash
curl "http://127.0.0.1:8000/summary?start_date=2024-01-01&end_date=2024-01-31"
```

### `GET /channel-performance`

Returns channel-level aggregates. Supports optional date range, channel filter, and
sort field.

Example:

```bash
curl "http://127.0.0.1:8000/channel-performance?start_date=2024-01-01&end_date=2024-01-31&sort_by=spend"
```

### `GET /anomaly-report`

Returns high-scoring anomalous channel-performance rows.

Example:

```bash
curl "http://127.0.0.1:8000/anomaly-report?start_date=2024-01-01&end_date=2024-01-07&limit=5"
```

## PyTorch Anomaly Detection

The anomaly detector uses channel performance features:

- spend
- clicks
- impressions
- ctr
- cpc
- cpm

The service standardizes those features, trains a small autoencoder, computes
reconstruction error, and treats high reconstruction error as a possible anomaly.
The current threshold is the 95th percentile of reconstruction errors.

PyTorch is required for the anomaly endpoint. If `torch` is not installed, install
the dependencies from `requirements.txt` before running `/anomaly-report`.

## Run Tests

```bash
pytest
```

Or with the local venv:

```bash
.\.venv\Scripts\python.exe -m pytest
```

## Project Structure

```text
app/
  main.py
  data_loader.py
  services/
    summary_service.py
    channel_service.py
    anomaly_service.py
  ml/
    anomaly_detector.py

tests/
  test_summary_service.py
  test_channel_service.py
  test_anomaly_service.py
  test_api.py

docs/
  architecture.md
  pytorch_anomaly_detector.md
```

## Limitations

- Data is loaded from CSV files rather than a database.
- The anomaly model trains on request-time data and is intentionally small.
- The anomaly score identifies unusual rows, not proven root causes.
- There is no authentication, frontend, deployment setup, or LLM layer yet.

## Next Improvements

- Add SQL storage with reusable query functions.
- Persist trained anomaly models for faster responses.
- Add richer validation and error responses.
- Add request logging and latency metrics.
- Add an LLM explanation layer that only uses service outputs as evidence.
