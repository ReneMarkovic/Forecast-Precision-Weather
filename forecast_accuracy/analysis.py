from typing import List
import pandas as pd
import numpy as np


def compute_mae(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean Absolute Error."""
    return np.mean(np.abs(actual - forecast))


def compute_rmse(actual: pd.Series, forecast: pd.Series) -> float:
    """Root Mean Squared Error."""
    return np.sqrt(np.mean((actual - forecast) ** 2))


METRIC_FUNCTIONS = {
    "MAE": compute_mae,
    "RMSE": compute_rmse,
}


def evaluate_metrics(actual: pd.Series, forecast: pd.Series, metrics: List[str]):
    results = {}
    for m in metrics:
        func = METRIC_FUNCTIONS.get(m)
        if func:
            results[m] = func(actual, forecast)
    return results
