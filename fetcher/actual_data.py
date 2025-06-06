from pathlib import Path
import requests
from typing import Dict, Tuple

# Directory for storing actual measurements
Path("data/actual_data").mkdir(parents=True, exist_ok=True)

# Coordinates for cities
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Koper": (45.5469, 13.7290),
    "Ljubljana": (46.0569, 14.5058),
    "Maribor": (46.5547, 15.6459),
}

# Open-Meteo current weather endpoint (same as forecast with `current_weather=true`)
CURRENT_WEATHER_API = "https://api.open-meteo.com/v1/forecast"

def fetch_current_weather(city: str) -> Dict:
    """
    Fetch current weather data for a given city.
    Returns temperature, windspeed, etc. at current time.
    """
    if city not in CITY_COORDS:
        raise ValueError(f"City '{city}' is not supported.")

    lat, lon = CITY_COORDS[city]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "Europe/Ljubljana"
    }
    response = requests.get(CURRENT_WEATHER_API, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

