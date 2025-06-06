import requests
from typing import Dict, Tuple

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_CURRENT_URL = "https://api.open-meteo.com/v1/forecast"

CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Koper": (45.5469, 13.7290),
    "Ljubljana": (46.0569, 14.5058),
    "Maribor": (46.5547, 15.6459),
}

def _get_coords(city: str) -> Tuple[float, float]:
    coords = CITY_COORDS.get(city)
    if not coords:
        raise ValueError(f"Coordinates for {city} not defined")
    return coords

def fetch_hourly_forecast(city: str, days: int = 7) -> Dict:
    """Fetch hourly forecast for the next `days` days."""
    lat, lon = _get_coords(city)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m", "relative_humidity_2m", "cloudcover", "windspeed_10m", "precipitation"
        ]),
        "forecast_days": days,
        "timezone": "Europe/Ljubljana",
    }
    response = requests.get(OPEN_METEO_API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def fetch_current_weather(city: str) -> Dict:
    """Fetch current weather for a city."""
    lat, lon = _get_coords(city)
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "Europe/Ljubljana",
    }
    response = requests.get(OPEN_METEO_CURRENT_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
