from pathlib import Path
from datetime import datetime
import pandas as pd

from storage.load import load_records
from evaluator.compare import align_and_evaluate

CITIES = ["Koper", "Ljubljana", "Maribor"]
PARAMETERS = ["temperature_2m", "precipitation", "cloudcover", "windspeed_10m"]
METRICS = ["MAE", "RMSE"]
FORECAST_FOLDER = "hourly_forecasts"
ACTUAL_FOLDER = "actual_data"
RESULT_FILE = "data/results/hourly_accuracy_results.csv"

for sub_folder in ["data", "data/hourly_forecasts", "data/results"]:
    
    Path(sub_folder).mkdir(parents=True, exist_ok=True)

def run_hourly_accuracy_evaluation():
    today = datetime.now().date()
    results = []

    for city in CITIES:
        # Najdi najnovejšo napoved in meritve
        forecast_files = sorted(Path("data", FORECAST_FOLDER).glob(f"hourly_{city}_*.csv"), reverse=True)
        actual_files = sorted(Path("data", ACTUAL_FOLDER).glob(f"actual_{city}_{today}_*.csv"))

        if not forecast_files or not actual_files:
            print(f"[WARNING] Missing forecast or actual data for {city}")
            continue

        try:
            forecast_df = pd.DataFrame(load_records(forecast_files[0].name, FORECAST_FOLDER))
            print(f"[INFO] Loaded forecast data for {city} from {forecast_files[0].name}")
            actual_records = []
            for f in actual_files:
                recs = load_records(f.name, ACTUAL_FOLDER)
                print(f"[INFO] Loaded {len(recs)} actual records from {f.name}")
                if recs:
                    actual_records.extend(recs)
            actual_df = pd.DataFrame(actual_records)

            # Standardiziraj ime časovnega stolpca
            forecast_df["time"] = pd.to_datetime(forecast_df["time"])
            # Open-Meteo current weather timestamps rarely align exactly with the
            # forecasted hourly steps. Use the API time and round down to the
            # nearest hour so we can merge it with forecast data.
            actual_df["time"] = (
                pd.to_datetime(actual_df["api_time"])
                .dt.floor("H")
            )

            # Map current_weather field names to forecast parameter names
            actual_df = actual_df.rename(
                columns={
                    "temperature": "temperature_2m",
                    "windspeed": "windspeed_10m",
                }
            )
            
            # Preimenuj forecast stolpce
            forecast_df = forecast_df.rename(columns={p: f"{p}_forecast" for p in PARAMETERS})

            # Preimenuj actual stolpce
            actual_df = actual_df.rename(columns={p: f"{p}_actual" for p in PARAMETERS if p in actual_df.columns})
            
            merged_results = align_and_evaluate(
                forecast_df,
                actual_df,
                timestamp_col="time",
                parameters=PARAMETERS,
                metrics=METRICS,
                city=city,
                timestamp=datetime.now().isoformat()
            )
            
            merged_results["city"] = city
            merged_results["timestamp"] = datetime.now().isoformat()
            results.append(merged_results)
            print(f"[INFO] Evaluated hourly forecast for {city}")

        except Exception as e:
            print(f"[ERROR] Could not evaluate {city}: {e}")

    if results:
        df = pd.concat(results)
        df.to_csv(RESULT_FILE, index=False)
        print(f"[INFO] Results saved to {RESULT_FILE}")

if __name__ == "__main__":
    run_hourly_accuracy_evaluation()
