from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from storage.load import load_records
from evaluator.metrics import evaluate_metrics


for subdir in ["data", "data/daily_forecasts", "data/actual_data"]:
    Path(subdir).mkdir(parents=True, exist_ok=True)

forecast_dir = Path("data/daily_forecasts")
actual_dir = Path("data/actual_data")
    
cities = ["Koper", "Ljubljana", "Maribor"]
metrics = ["MAE", "RMSE"]

def run_daily_accuracy_evaluation():
    today = datetime.now().date()
    results = []

    for city in cities:
        actual_filename = f"actual_{city}_{today}.csv"
        actual_data = load_records(actual_filename, "actual_data")
        if not actual_data:
            print(f"[WARNING] Missing actual data for {city} on {today}")
            continue

        for day_offset in range(1, 11):  # 1 to 10 days ago
            forecast_date = today - timedelta(days=day_offset)
            forecast_filename = f"forecast_{city}_{forecast_date}.csv"
            forecast_data = load_records(forecast_filename, "daily_forecasts")
            if not forecast_data:
                continue

            row_forecast = next((row for row in forecast_data if row.get("time") == str(today)), None)
            if not row_forecast:
                continue

            for param in ["temperature_2m_min", "temperature_2m_max", "temperature_2m_mean",
                          "precipitation_sum", "cloudcover_mean", "windspeed_10m_max"]:
                try:
                    actual_val = float(actual_data[0].get(param, 0))
                    forecast_val = float(row_forecast.get(param, 0))
                except (ValueError, TypeError):
                    continue

                eval_result = evaluate_metrics(
                    pd.Series([actual_val]),
                    pd.Series([forecast_val]),
                    metrics
                )

                results.append({
                    "city": city,
                    "target_date": str(today),
                    "forecast_made_on": str(forecast_date),
                    "parameter": param,
                    **eval_result
                })

    df_results = pd.DataFrame(results)
    output_path = Path("data") / "daily_accuracy_results.csv"
    df_results.to_csv(output_path, index=False)
    print(f"[INFO] Saved daily accuracy results to {output_path}")

if __name__ == "__main__":
    run_daily_accuracy_evaluation()
