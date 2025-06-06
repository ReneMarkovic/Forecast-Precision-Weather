from pathlib import Path
import requests
from typing import Dict, Tuple, List

# Directory to save daily forecast files
Path("data/daily_forecasts").mkdir(parents=True, exist_ok=True)

# Coordinates for cities
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Koper": (45.5469, 13.7290),
    "Ljubljana": (46.0569, 14.5058),
    "Maribor": (46.5547, 15.6459),
}

# Open-Meteo daily forecast endpoint
DAILY_FORECAST_API = "https://api.open-meteo.com/v1/forecast"

def fetch_daily_forecast(city: str, days: int = 10) -> Dict:
    """Fetch daily forecast data for the next `days` days for a given city."""
    if city not in CITY_COORDS:
        raise ValueError(f"City '{city}' is not supported.")

    lat, lon = CITY_COORDS[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "temperature_2m_min",
            "temperature_2m_max",
            "temperature_2m_mean",
            "precipitation_sum",
            "cloudcover_mean",
            "windspeed_10m_max"
        ]),
        "forecast_days": days,
        "timezone": "Europe/Ljubljana"
    }
    response = requests.get(DAILY_FORECAST_API, params=params, timeout=10)
    response.raise_for_status()
    return response.json()