import time
from datetime import datetime
from fetcher.actual_data import fetch_current_weather
from storage.save import save_records

CITIES = ["Koper", "Ljubljana", "Maribor"]
SAVE_FOLDER = "actual_data"
FETCH_INTERVAL_SECONDS = 60 * 60  # 1 hour

def continuously_fetch_weather_data():
    print("[INFO] Starting continuous weather data collection...")
    while True:
        now = datetime.now()
        date_str = now.date().isoformat()
        time_str = now.strftime("%H:%M")

        for city in CITIES:
            try:
                result = fetch_current_weather(city)
                if "current_weather" in result:
                    record = result["current_weather"]
                    record["fetched_time"] = now.isoformat()
                    record["api_time"] = record.get("time")  # original timestamp from Open-Meteo
                    filename = f"actual_{city}_{date_str}_{time_str.replace(':', '-')}.csv"
                    save_records(filename, [record], subfolder=SAVE_FOLDER)
                    print(f"[{now:%Y-%m-%d %H:%M}] Saved weather for {city}")
            except Exception as e:
                print(f"[ERROR] Failed to fetch data for {city}: {e}")

        print(f"[INFO] Sleeping for {FETCH_INTERVAL_SECONDS // 60} minutes...\n")
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    continuously_fetch_weather_data()