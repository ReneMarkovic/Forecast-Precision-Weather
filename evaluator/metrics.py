# evaluator/metrics.py

import numpy as np
import pandas as pd

def compue_mape_mape(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean Absolute Percentage Error"""
    return np.mean(np.abs((actual - forecast) / actual)) * 100 if not actual.empty else np.nan

def compute_mae(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean Absolute Error"""
    return np.mean(np.abs(actual - forecast))


def compute_rmse(actual: pd.Series, forecast: pd.Series) -> float:
    """Root Mean Squared Error"""
    return np.sqrt(np.mean((actual - forecast) ** 2))


METRIC_FUNCTIONS = {
    "MAPE": compue_mape_mape,
    "MAE": compute_mae,
    "RMSE": compute_rmse,
}

def evaluate_metrics(actual: pd.Series, forecast: pd.Series, metrics: list) -> dict:
    """Evaluate given metrics between actual and forecast series"""
    results = {}
    for metric in metrics:
        func = METRIC_FUNCTIONS.get(metric)
        if func:
            results[metric] = func(actual, forecast)
    return results
