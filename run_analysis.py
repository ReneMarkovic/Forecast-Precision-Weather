import pandas as pd
from forecast_accuracy import data_fetcher, storage, analysis, visualization

CITIES = ["Koper", "Ljubljana", "Maribor"]


def main():
    for city in CITIES:
        print(f"Fetching data for {city}...")
        forecast_data = data_fetcher.fetch_forecast(city)
        current_data = data_fetcher.fetch_current(city)

        storage.save_records(f"forecast_{city}.csv", forecast_data.get("list", []))
        storage.save_records(f"current_{city}.csv", [current_data])

        # Example analysis: this expects that forecast_data has 'main' field
        forecast_temps = [item["main"]["temp"] for item in forecast_data.get("list", [])]
        actual_temp = current_data["main"]["temp"] if current_data else None
        if actual_temp is None or not forecast_temps:
            print(f"No data for {city}")
            continue

        df = pd.DataFrame({
            "forecast": forecast_temps,
            "actual": [actual_temp] * len(forecast_temps)
        })
        mae = analysis.compute_mae(df["actual"], df["forecast"])
        rmse = analysis.compute_rmse(df["actual"], df["forecast"])
        print(f"{city} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        df["timestamp"] = [item["dt_txt"] for item in forecast_data.get("list", [])]
        visualization.plot_forecast_vs_actual(df, "timestamp", "actual", "forecast", city)


if __name__ == "__main__":
    main()
