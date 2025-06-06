from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict # Added for type hinting

from storage.load import load_records
# Original align_and_evaluate might not be directly used in the new approach,
# but its metric calculation logic can be adapted.
# from evaluator.compare import align_and_evaluate

CITIES = ["Koper", "Ljubljana", "Maribor"]
PARAMETERS = ["temperature_2m", "precipitation", "cloudcover", "windspeed_10m"]
METRICS = ["MAE", "RMSE","MAPE"] # METRICS constant might not be directly used by name in new logic
FORECAST_FOLDER = "hourly_forecasts"
ACTUAL_FOLDER = "actual_data"
# Original result file for single point latest forecast
# RESULT_FILE = "data/results/hourly_accuracy_results.csv"
HORIZON_RESULT_FILE = "data/results/hourly_horizon_accuracy_results.csv"

for sub_folder in ["data", "data/hourly_forecasts", "data/actual_data", "data/results"]: # Added data/actual_data
    Path(sub_folder).mkdir(parents=True, exist_ok=True)

def parse_forecast_filename(filename_str: str) -> datetime:
    """
    Parses the forecast generation datetime from the filename.
    Filename format: hourly_{city}_{YYYY-MM-DD}_{HH-MM}.csv
    """
    stem = Path(filename_str).stem
    parts = stem.split('_')
    date_str = parts[-2]
    time_str = parts[-1].replace('-', ':') # Convert HH-MM to HH:MM
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def calculate_metrics(series_actual: pd.Series, series_forecast: pd.Series) -> Dict[str, float]:
    """Calculates MAE, RMSE, and MAPE between two series."""
    if series_actual.empty or series_forecast.empty:
        return {"MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan}
        
    errors = series_actual - series_forecast
    mae = errors.abs().mean()
    rmse = np.sqrt((errors**2).mean())
    
    # Ensure series_actual does not contain zeros where division occurs for MAPE
    # Replace 0 with a very small number or handle as NaN if actual is 0
    safe_actual = series_actual.replace(0, np.nan) # Or a small epsilon if preferred
    mape_terms = (errors.abs() / safe_actual.abs())
    
    # Filter out inf/NaN from division by zero or near-zero actuals
    mape = mape_terms[np.isfinite(mape_terms)].mean() * 100 
    if pd.isna(mape): # If all terms were NaN (e.g. all actuals were 0)
        mape = np.nan 
        
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape}

def run_hourly_horizon_accuracy_evaluation():
    """
    Evaluates forecast accuracy for different forecast horizons (1h, 2h, ..., 24h ahead).
    """
    all_results = []

    # Pre-load and process all actual data for efficiency
    actual_data_all_cities = {}
    for city in CITIES:
        actual_files = sorted(Path("data", ACTUAL_FOLDER).glob(f"actual_{city}_*.csv"))
        city_actual_records = []
        for f_path in actual_files:
            try:
                recs = load_records(f_path.name, ACTUAL_FOLDER)
                if recs:
                    city_actual_records.extend(recs)
            except Exception as e:
                print(f"[WARNING] Could not load actual data from {f_path.name}: {e}")
        
        if not city_actual_records:
            print(f"[WARNING] No actual data found for {city}")
            actual_data_all_cities[city] = pd.DataFrame() # Empty DataFrame
            continue

        df_actual_city = pd.DataFrame(city_actual_records)
        # Ensure 'api_time' exists before trying to convert
        if "api_time" not in df_actual_city.columns:
            print(f"[WARNING] 'api_time' column missing in actual data for {city}. Skipping this city for actuals.")
            actual_data_all_cities[city] = pd.DataFrame()
            continue
            
        df_actual_city["time"] = pd.to_datetime(df_actual_city["api_time"]).dt.floor("h")
        df_actual_city = df_actual_city.rename(
            columns={
                "temperature": "temperature_2m", # Standard Open-Meteo name
                "windspeed": "windspeed_10m",    # Standard Open-Meteo name
                "precipitation": "precipitation", # Assuming it's already named this or needs mapping
                "cloudcover": "cloudcover"      # Assuming it's already named this or needs mapping
            }
        )
        # Ensure all PARAMETERS are present, add them with NaN if missing, before selecting
        for p in PARAMETERS:
            if p not in df_actual_city.columns:
                df_actual_city[p] = np.nan

        relevant_actual_cols = ["time"] + PARAMETERS
        if "time" in df_actual_city.columns : # ensure time column exists after processing
            actual_data_all_cities[city] = df_actual_city[relevant_actual_cols].drop_duplicates(subset=['time']).set_index("time")
        else:
             actual_data_all_cities[city] = pd.DataFrame()
        print(f"[INFO] Loaded and preprocessed all actual data for {city}")

    for city in CITIES:
        df_actual_city = actual_data_all_cities.get(city)
        if df_actual_city is None or df_actual_city.empty:
            print(f"[INFO] Skipping {city} due to no preprocessed actual data.")
            continue

        forecast_files = sorted(Path("data", FORECAST_FOLDER).glob(f"hourly_{city}_*.csv"))
        
        city_horizon_comparisons = []

        for forecast_file_path in forecast_files:
            try:
                forecast_generation_time = parse_forecast_filename(forecast_file_path.name)
                
                raw_forecast_data = load_records(forecast_file_path.name, FORECAST_FOLDER)
                if not raw_forecast_data: # Handles None or empty list from load_records
                    print(f"[INFO] No data in forecast file {forecast_file_path.name}")
                    continue
                forecast_df = pd.DataFrame(raw_forecast_data)
                if forecast_df.empty:
                    continue
                
                forecast_df["time"] = pd.to_datetime(forecast_df["time"])
                print(f"[INFO] Processing forecast {forecast_file_path.name} generated at {forecast_generation_time}")

                for _, forecast_row in forecast_df.iterrows():
                    predicted_time = forecast_row["time"]
                    horizon_timedelta = predicted_time - forecast_generation_time
                    horizon_hours = int(round(horizon_timedelta.total_seconds() / 3600))

                    if not (1 <= horizon_hours <= 24): # Focus on 1 to 24 hours ahead
                        continue

                    if predicted_time in df_actual_city.index:
                        actual_row_series = df_actual_city.loc[predicted_time]
                        # If loc returns a DataFrame due to duplicate index, take the first row
                        if isinstance(actual_row_series, pd.DataFrame):
                            if not actual_row_series.empty:
                                actual_row_series = actual_row_series.iloc[0]
                            else:
                                continue # No actual data for this specific duplicate index case
                                
                        for param in PARAMETERS:
                            if param in forecast_row and param in actual_row_series and \
                               pd.notna(forecast_row[param]) and pd.notna(actual_row_series[param]):
                                city_horizon_comparisons.append({
                                    "city": city,
                                    "parameter": param,
                                    "horizon_hours": horizon_hours,
                                    "forecast_value": forecast_row[param],
                                    "actual_value": actual_row_series[param],
                                    "forecast_generation_time": forecast_generation_time,
                                    "target_time": predicted_time
                                })
            except Exception as e:
                print(f"[ERROR] Could not process forecast file {forecast_file_path.name} for {city}: {e}")
        
        if not city_horizon_comparisons:
            print(f"[INFO] No valid comparisons found for {city} to calculate horizon accuracy.")
            continue

        df_comparisons = pd.DataFrame(city_horizon_comparisons)
        
        # Ensure 'actual_value' and 'forecast_value' are numeric before grouping and metric calculation
        df_comparisons['actual_value'] = pd.to_numeric(df_comparisons['actual_value'], errors='coerce')
        df_comparisons['forecast_value'] = pd.to_numeric(df_comparisons['forecast_value'], errors='coerce')
        
        # Ensure no duplicate comparisons for the same target_time, parameter, and horizon from different forecast files
        # This can happen if multiple forecasts cover the same target hour with the same horizon.
        # We should ideally pick one, e.g., the one generated closest to the target time, or average.
        # For simplicity now, we'll group and if there are multiple, metrics will be on all of them.
        # A more sophisticated approach might filter df_comparisons before grouping.
        # Example: sort by forecast_generation_time and drop duplicates keeping the latest forecast for a given target_time & horizon
        df_comparisons = df_comparisons.sort_values(by='forecast_generation_time', ascending=False)
        df_comparisons = df_comparisons.drop_duplicates(subset=['city', 'parameter', 'horizon_hours', 'target_time'], keep='first')


        grouped = df_comparisons.groupby(["city", "parameter", "horizon_hours"])
        
        for (c, p, h), group_data in grouped:
            if group_data.empty or len(group_data) < 1: # Ensure there's data to calculate
                print(f"[INFO] Insufficient data for {c}, {p}, horizon {h}h. Count: {len(group_data)}")
                metrics_calculated = {"MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan} # Store NaN if no data
            else:
                metrics_calculated = calculate_metrics(group_data["actual_value"], group_data["forecast_value"])

            all_results.append({
                "city": c,
                "parameter": p,
                "horizon_hours": h,
                "MAE": metrics_calculated["MAE"],
                "RMSE": metrics_calculated["RMSE"],
                "MAPE": metrics_calculated["MAPE"],
                "count": len(group_data), # Number of data points used for this metric
                "evaluation_timestamp": datetime.now().isoformat()
            })
        print(f"[INFO] Calculated horizon-based accuracy for {city}")

    if all_results:
        final_df = pd.DataFrame(all_results)
        final_df = final_df.sort_values(by=["city", "parameter", "horizon_hours"])
        final_df.to_csv(HORIZON_RESULT_FILE, index=False, float_format='%.3f') # Format floats
        print(f"[INFO] Horizon-based accuracy results saved to {HORIZON_RESULT_FILE}")
    else:
        print("[INFO] No results to save for horizon-based accuracy.")


# The old function for single latest forecast evaluation.
# You can remove or comment it out if it's no longer needed.
def run_hourly_accuracy_evaluation_old():
    today = datetime.now().date()
    results = []

    for city in CITIES:
        # Najdi najnovejšo napoved in meritve
        forecast_files = sorted(Path("data", FORECAST_FOLDER).glob(f"hourly_{city}_*.csv"), reverse=True)
        actual_files = sorted(Path("data", ACTUAL_FOLDER).glob(f"actual_{city}_{today}_*.csv")) # Original logic for "today"

        if not forecast_files:
            print(f"[WARNING] No forecast files found for {city}")
            continue
        # if not actual_files: # This check might be too restrictive if actual data is collected less frequently
        #     print(f"[WARNING] No actual files found for {city} for date {today}")
        #     continue

        try:
            # This part assumes 'align_and_evaluate' is available and works as before
            # For the new horizon-based analysis, this function is not directly used.
            forecast_df = pd.DataFrame(load_records(forecast_files[0].name, FORECAST_FOLDER))
            if forecast_df.empty:
                print(f"[INFO] Forecast file {forecast_files[0].name} for {city} is empty.")
                continue
            print(f"[INFO] Loaded forecast data for {city} from {forecast_files[0].name}")
            
            actual_records = []
            for f_path in actual_files: # Renamed f to f_path to avoid conflict
                recs = load_records(f_path.name, ACTUAL_FOLDER)
                if recs:
                    print(f"[INFO] Loaded {len(recs)} actual records from {f_path.name}")
                    actual_records.extend(recs)
            
            if not actual_records:
                print(f"[WARNING] No actual records loaded for {city} for date {today}")
                continue

            actual_df = pd.DataFrame(actual_records)
            if actual_df.empty:
                print(f"[WARNING] Actual data DataFrame is empty for {city} for date {today}")
                continue

            # Ensure 'time' column exists and is datetime
            if "time" not in forecast_df.columns or "api_time" not in actual_df.columns:
                 print(f"[ERROR] Time column missing in forecast or actual data for {city}")
                 continue
            forecast_df["time"] = pd.to_datetime(forecast_df["time"])
            actual_df["time"] = pd.to_datetime(actual_df["api_time"]).dt.floor('h') # Match forecast hourly
            
            # Preimenuj actual stolpce
            actual_df = actual_df.rename(columns={
                "temperature": "temperature_2m",
                "windspeed": "windspeed_10m",
                # Add other mappings if actual data uses different names
            })
            # Select only relevant parameters for actual_df to avoid issues in align_and_evaluate
            actual_df_params = [p for p in PARAMETERS if p in actual_df.columns]
            actual_df = actual_df[["time"] + actual_df_params]


            # Ensure align_and_evaluate is defined or imported
            # For now, this part is commented out as align_and_evaluate is not fully defined in this context
            # merged_results = align_and_evaluate( 
            #     forecast_df,
            #     actual_df,
            #     timestamp_col="time",
            #     parameters=PARAMETERS,
            #     metrics=METRICS, # METRICS constant
            #     city=city,
            #     timestamp=datetime.now().isoformat()
            # )
            
            # Placeholder if align_and_evaluate is not used/defined in this context for old function
            print(f"[INFO] Old evaluation logic for {city} would run here using align_and_evaluate.")
            # if merged_results is not None and not merged_results.empty:
            #     merged_results["city"] = city
            #     merged_results["timestamp"] = datetime.now().isoformat()
            #     results.append(merged_results)
            #     print(f"[INFO] Evaluated hourly forecast for {city}")
            # else:
            #     print(f"[INFO] No results from align_and_evaluate for {city}")


        except Exception as e:
            print(f"[ERROR] Could not evaluate {city} in old function: {e}")

    if results:
        # df = pd.concat(results)
        # df.to_csv(RESULT_FILE, index=False) # Original RESULT_FILE
        # print(f"[INFO] Results saved to {RESULT_FILE}")
        print("[INFO] Old evaluation logic finished. Results would be concatenated and saved here.")
    else:
        print("[INFO] Old evaluation logic finished. No results to save.")


if __name__ == "__main__":
    run_hourly_horizon_accuracy_evaluation()
    # If you still need the old functionality, you can call it too:
    # print("\n--- Running old single-point accuracy evaluation (if enabled) ---")
    # run_hourly_accuracy_evaluation_old()
