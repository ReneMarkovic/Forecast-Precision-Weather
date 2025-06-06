import re
from pathlib import Path
from datetime import datetime
import pandas as pd

from storage.load import load_records
from evaluator.metrics import evaluate_metrics

CITIES = ["Koper", "Ljubljana", "Maribor"]
PARAMETERS = ["temperature_2m", "precipitation", "cloudcover", "windspeed_10m"]
METRICS = ["MAE", "RMSE"]
FORECAST_FOLDER = "hourly_forecasts"
ACTUAL_FOLDER = "actual_data"
RESULT_FILE = "data/results/hourly_horizon_accuracy.csv"

for sub_folder in ["data", "data/hourly_forecasts", "data/results"]:
    Path(sub_folder).mkdir(parents=True, exist_ok=True)

def parse_generation_time(filename: str) -> datetime:
    match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})", filename)
    if not match:
        raise ValueError(f"Cannot parse timestamp from {filename}")
    date_part, time_part = match.groups()
    time_part = time_part.replace("-", ":")
    return datetime.fromisoformat(f"{date_part} {time_part}")

def run_hourly_horizon_accuracy():
    today = datetime.now().date()
    results = []

    for city in CITIES:
        forecast_files = sorted(Path("data", FORECAST_FOLDER).glob(f"hourly_{city}_*.csv"), reverse=True)
        actual_files = sorted(Path("data", ACTUAL_FOLDER).glob(f"actual_{city}_{today}_*.csv"))

        if not forecast_files or not actual_files:
            print(f"[WARNING] Missing forecast or actual data for {city}")
            continue

        forecast_path = forecast_files[0]
        generation_time = parse_generation_time(forecast_path.name)
        forecast_df = pd.DataFrame(load_records(forecast_path.name, FORECAST_FOLDER))
        forecast_df["time"] = pd.to_datetime(forecast_df["time"])
        forecast_df["horizon"] = ((forecast_df["time"] - generation_time).dt.total_seconds() / 3600).round().astype(int)
        forecast_df = forecast_df[forecast_df["horizon"].between(1, 24)]
        forecast_df = forecast_df.rename(columns={p: f"{p}_forecast" for p in PARAMETERS})

        actual_records = []
        for f in actual_files:
            recs = load_records(f.name, ACTUAL_FOLDER)
            if recs:
                actual_records.extend(recs)
        actual_df = pd.DataFrame(actual_records)
        actual_df["time"] = pd.to_datetime(actual_df["api_time"]).dt.floor("H")
        actual_df = actual_df.rename(columns={"temperature": "temperature_2m", "windspeed": "windspeed_10m"})
        actual_df = actual_df.rename(columns={p: f"{p}_actual" for p in PARAMETERS if p in actual_df.columns})

        merged = pd.merge(forecast_df, actual_df, on="time")

        for horizon in range(1, 25):
            df_h = merged[merged["horizon"] == horizon]
            if df_h.empty:
                continue
            for param in PARAMETERS:
                f_col = f"{param}_forecast"
                a_col = f"{param}_actual"
                if f_col in df_h.columns and a_col in df_h.columns:
                    actual_series = pd.to_numeric(df_h[a_col], errors="coerce")
                    forecast_series = pd.to_numeric(df_h[f_col], errors="coerce")
                    mask = actual_series.notna() & forecast_series.notna()
                    if mask.sum() == 0:
                        continue
                    eval_result = evaluate_metrics(actual_series[mask], forecast_series[mask], METRICS)
                    results.append({
                        "city": city,
                        "horizon_hours": horizon,
                        "parameter": param,
                        **eval_result
                    })

    if results:
        df = pd.DataFrame(results)
        df.to_csv(RESULT_FILE, index=False)
        print(f"[INFO] Results saved to {RESULT_FILE}")

if __name__ == "__main__":
    run_hourly_horizon_accuracy()
