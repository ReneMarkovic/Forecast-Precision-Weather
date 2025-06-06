from datetime import datetime
from fetcher import hourly_forecast
from fetcher import daily_forecast
from storage.save import save_records
from pathlib import Path

CITIES = ["Koper", "Ljubljana", "Maribor"]
HOURLY_FOLDER = "hourly_forecasts"
DAILY_FOLDER = "daily_forecasts"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M")

def fetch_and_store_forecasts():
    for city in CITIES:
        try:
            # Urna napoved
            hourly_data = hourly_forecast.fetch_hourly_forecast(city, days=2)
            hourly_records = []
            times = hourly_data.get("hourly", {}).get("time", [])
            for key in ["temperature_2m", "precipitation", "cloudcover", "windspeed_10m"]:
                values = hourly_data.get("hourly", {}).get(key, [])
                for i, t in enumerate(times):
                    if i >= len(hourly_records):
                        hourly_records.append({"time": t})
                    hourly_records[i][key] = values[i]
            hourly_filename = f"hourly_{city}_{TIMESTAMP}.csv"
            save_records(hourly_filename, hourly_records, subfolder=HOURLY_FOLDER)
            print(f"[INFO] Saved hourly forecast for {city}")

            # Dnevna napoved
            daily_data = daily_forecast.fetch_daily_forecast(city, days=10)
            daily_records = []
            times = daily_data.get("daily", {}).get("time", [])
            for key in ["temperature_2m_min", "temperature_2m_max", "temperature_2m_mean",
                        "precipitation_sum", "cloudcover_mean", "windspeed_10m_max"]:
                values = daily_data.get("daily", {}).get(key, [])
                for i, t in enumerate(times):
                    if i >= len(daily_records):
                        daily_records.append({"time": t})
                    daily_records[i][key] = values[i]
            daily_filename = f"forecast_{city}_{datetime.now().date()}.csv"
            save_records(daily_filename, daily_records, subfolder=DAILY_FOLDER)
            print(f"[INFO] Saved daily forecast for {city}")

        except Exception as e:
            print(f"[ERROR] Failed to fetch/save forecast for {city}: {e}")

if __name__ == "__main__":
    fetch_and_store_forecasts()
