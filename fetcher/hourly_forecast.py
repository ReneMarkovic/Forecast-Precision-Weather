from pathlib import Path
import requests
from typing import Dict, Tuple

# Directory to save hourly forecast files
Path("data/hourly_forecasts").mkdir(parents=True, exist_ok=True)

# Coordinates for cities
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Koper": (45.5469, 13.7290),
    "Ljubljana": (46.0569, 14.5058),
    "Maribor": (46.5547, 15.6459),
}

# Open-Meteo hourly forecast endpoint
HOURLY_FORECAST_API = "https://api.open-meteo.com/v1/forecast"

def fetch_hourly_forecast(city: str, days: int = 2) -> Dict:
    """
    Fetch hourly forecast data for the next `days` days for a given city.
    Default is 2 days (i.e., 48 hourly entries).
    """
    if city not in CITY_COORDS:
        raise ValueError(f"City '{city}' is not supported.")

    lat, lon = CITY_COORDS[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m",
            "precipitation",
            "cloudcover",
            "windspeed_10m"
        ]),
        "forecast_days": days,
        "timezone": "Europe/Ljubljana"
    }
    response = requests.get(HOURLY_FORECAST_API, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

