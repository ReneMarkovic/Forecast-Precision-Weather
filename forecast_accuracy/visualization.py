import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)


def plot_forecast_vs_actual(df: pd.DataFrame, date_col: str, actual_col: str, forecast_col: str, city: str) -> Path:
    fig, ax = plt.subplots()
    df.plot(x=date_col, y=actual_col, ax=ax, label="Actual")
    df.plot(x=date_col, y=forecast_col, ax=ax, label="Forecast")
    ax.set_title(f"Forecast vs Actual - {city}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    path = PLOT_DIR / f"forecast_vs_actual_{city}.png"
    fig.savefig(path)
    plt.close(fig)
    return path
