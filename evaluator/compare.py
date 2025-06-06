# evaluator/compare.py

import pandas as pd
from evaluator.metrics import evaluate_metrics

def align_and_evaluate(
    forecast_df: pd.DataFrame,
    actual_df: pd.DataFrame,
    timestamp_col: str,
    parameters: list,
    metrics: list,
    city: str = None,
    timestamp: str = None
) -> pd.DataFrame:
    """
    Align forecast and actual data by timestamp, and compute evaluation metrics for each parameter.
    Returns a dataframe with timestamp, parameter, and computed metric values.
    """
    merged = pd.merge(
        forecast_df,
        actual_df,
        on=timestamp_col,
        suffixes=("_forecast", "_actual")
    )

    results = []

    for param in parameters:
        print(f"working on parameter: {param}")
        if f"{param}_forecast" in merged.columns and f"{param}_actual" in merged.columns:
            actual_series = pd.to_numeric(merged[f"{param}_actual"], errors='coerce')
            forecast_series = pd.to_numeric(merged[f"{param}_forecast"], errors='coerce')
            if actual_series.empty or forecast_series.empty:
                print(f"[WARNING] No data for parameter {param} in city {city}")
                continue
            valid_mask = actual_series.notna() & forecast_series.notna()
            if valid_mask.sum() == 0:
                continue

            eval_result = evaluate_metrics(
                actual_series[valid_mask],
                forecast_series[valid_mask],
                metrics
            )

            results.append({
                "parameter": param,
                **eval_result,
                "city": city,
                "timestamp": timestamp
            })
    print(results)
    return pd.DataFrame(results)
