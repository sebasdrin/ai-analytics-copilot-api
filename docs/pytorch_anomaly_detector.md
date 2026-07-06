# PyTorch Anomaly Detector

## What PyTorch Is Used For

PyTorch is used to build and train a small autoencoder model. In this project, the
model learns the usual shape of channel-performance rows and gives higher anomaly
scores to rows that are harder to reconstruct.

## What An Autoencoder Is

An autoencoder is a neural network trained to copy its input to its output. It has two
main parts:

- Encoder: compresses the input features into a smaller representation
- Decoder: reconstructs the original features from that compressed representation

If a row looks normal, the model should reconstruct it fairly well. If a row looks
unusual, reconstruction error tends to be higher.

## Input Features

The detector currently uses these channel-level numeric features:

- `spend`
- `clicks`
- `impressions`
- `ctr`
- `cpc`
- `cpm`

These features are available in `data/processed/channel_daily_performance.csv`.

## Why Features Are Normalized

The raw columns have very different scales. For example, impressions can be in the
thousands while CTR is a small decimal. Without normalization, large-scale columns
would dominate the loss.

The detector standardizes each feature:

```text
standardized_value = (value - feature_mean) / feature_standard_deviation
```

This makes the features more comparable during training.

## What The Model Learns

The model learns common relationships across the input metrics. For example, it sees
typical combinations of spend, clicks, impressions, CTR, CPC, and CPM. It does not
learn business causality. It only learns patterns in the numeric feature space.

## Reconstruction Error

After training, each row is passed through the autoencoder. The detector compares the
reconstructed row with the original standardized row.

The anomaly score is mean squared reconstruction error:

```text
mean((reconstructed_features - original_features)^2)
```

Higher error means the model struggled to reconstruct the row, so the row may be
unusual.

## Threshold

The current threshold is the 95th percentile of reconstruction errors. Rows at or
above that threshold are flagged as anomalies.

This is simple and explainable:

- It does not require labeled anomaly data.
- It adapts to the date range being analyzed.
- It gives a clear "top 5 percent most unusual" interpretation.

## Dependency Requirement

The anomaly endpoint requires PyTorch. If `torch` is not installed, install the
dependencies from `requirements.txt` before running `/anomaly-report`.

## Limitations

- The model trains during the request instead of using a saved model.
- There are no labeled anomalies to validate precision or recall.
- High anomaly score does not prove a business problem.
- Date ranges with very few rows may produce less meaningful thresholds.
- The current model ignores seasonality, campaigns, and business context.

## Possible Improvements

- Train and save a model offline.
- Add rolling-window features.
- Compare each channel against its own historical baseline.
- Add labeled anomaly examples if available.
- Return plain-English explanations based on supporting metrics.
