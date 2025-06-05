import pandas as pd
from forecast_accuracy import data_fetcher, storage, analysis, visualization

CITIES = ["Koper", "Ljubljana", "Maribor"]


def main():
    for city in CITIES:
        print(f"Fetching data for {city}...")
        forecast_data = data_fetcher.fetch_forecast(city)
        current_data = data_fetcher.fetch_current(city)

        hours = forecast_data.get("hourly", {}).get("time", [])
        temps = forecast_data.get("hourly", {}).get("temperature_2m", [])
        forecast_records = [
            {"time": t, "temp": temp} for t, temp in zip(hours, temps)
        ]
        storage.save_records(f"forecast_{city}.csv", forecast_records)

        current_record = current_data.get("current_weather")
        if current_record:
            storage.save_records(f"current_{city}.csv", [current_record])

        if not forecast_records or not current_record:
            print(f"No data for {city}")
            continue

        df = pd.DataFrame({
            "timestamp": hours,
            "forecast": temps,
            "actual": [current_record["temperature"]] * len(temps),
        })

        mae = analysis.compute_mae(df["actual"], df["forecast"])
        rmse = analysis.compute_rmse(df["actual"], df["forecast"])
        print(f"{city} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        df["timestamp"] = [item["dt_txt"] for item in forecast_data.get("list", [])]
        visualization.plot_forecast_vs_actual(df, "timestamp", "actual", "forecast", city)


if __name__ == "__main__":
    main()
