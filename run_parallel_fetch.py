import threading
import time
from datetime import datetime

from fetcher.actual_data import fetch_current_weather
from fetcher.hourly_forecast import fetch_hourly_forecast
from fetcher.daily_forecast import fetch_daily_forecast
from storage.save import save_records

CITIES = ["Koper", "Ljubljana", "Maribor"]
INTERVAL_MINUTES = 60  # how often to repeat
TIMESTAMP = lambda: datetime.now().strftime("%Y-%m-%d_%H-%M")

def fetch_actual_loop():
    while True:
        now = datetime.now()
        date_str = now.date().isoformat()
        time_str = now.strftime("%H-%M")
        for city in CITIES:
            try:
                result = fetch_current_weather(city)
                if "current_weather" in result:
                    record = result["current_weather"]
                    record["fetched_time"] = now.isoformat()
                    record["api_time"] = record.get("time")
                    filename = f"actual_{city}_{date_str}_{time_str}.csv"
                    save_records(filename, [record], subfolder="actual_data")
                    print(f"[ACTUAL] {city} @ {time_str} saved.")
            except Exception as e:
                print(f"[ERROR] actual {city}: {e}")
        time.sleep(INTERVAL_MINUTES * 60)

def fetch_hourly_loop():
    while True:
        stamp = TIMESTAMP()
        for city in CITIES:
            try:
                data = fetch_hourly_forecast(city, days=2)
                records = []
                times = data.get("hourly", {}).get("time", [])
                for key in ["temperature_2m", "precipitation", "cloudcover", "windspeed_10m"]:
                    for i, val in enumerate(data["hourly"].get(key, [])):
                        if i >= len(records):
                            records.append({"time": times[i]})
                        records[i][key] = val
                save_records(f"hourly_{city}_{stamp}.csv", records, subfolder="hourly_forecasts")
                print(f"[HOURLY] {city} @ {stamp} saved.")
            except Exception as e:
                print(f"[ERROR] hourly {city}: {e}")
        time.sleep(INTERVAL_MINUTES * 60)

def fetch_daily_loop():
    while True:
        today = datetime.now().date()
        for city in CITIES:
            try:
                data = fetch_daily_forecast(city, days=10)
                records = []
                times = data.get("daily", {}).get("time", [])
                for key in ["temperature_2m_min", "temperature_2m_max", "temperature_2m_mean",
                            "precipitation_sum", "cloudcover_mean", "windspeed_10m_max"]:
                    for i, val in enumerate(data["daily"].get(key, [])):
                        if i >= len(records):
                            records.append({"time": times[i]})
                        records[i][key] = val
                save_records(f"forecast_{city}_{today}.csv", records, subfolder="daily_forecasts")
                print(f"[DAILY] {city} @ {today} saved.")
            except Exception as e:
                print(f"[ERROR] daily {city}: {e}")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    threading.Thread(target=fetch_actual_loop, daemon=True).start()
    threading.Thread(target=fetch_hourly_loop, daemon=True).start()
    threading.Thread(target=fetch_daily_loop, daemon=True).start()

    print("[INFO] Forecast and actual fetch loops started. Press Ctrl+C to stop.")
    while True:
        time.sleep(10)
