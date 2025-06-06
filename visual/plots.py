from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Ensure plots directory exists
PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)


def plot_forecast_vs_actual(
    df: pd.DataFrame,
    date_col: str,
    actual_col: str,
    forecast_col: str,
    city: str,
    label: str = ""
) -> Path:
    """
    Plots actual vs forecasted values for a given city.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    df.plot(x=date_col, y=actual_col, ax=ax, label="Actual", linestyle='-', marker='o')
    df.plot(x=date_col, y=forecast_col, ax=ax, label="Forecast", linestyle='--', marker='x')

    ax.set_title(f"Forecast vs Actual - {city} {label}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"forecast_vs_actual_{city.replace(' ', '_')}_{label.replace(' ', '_')}.png"
    path = PLOT_DIR / filename
    fig.savefig(path)
    plt.close(fig)
    return path

