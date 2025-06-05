import requests
from typing import Dict, Tuple

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

# Coordinates for supported cities
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


def fetch_forecast(city: str, days: int = 7) -> Dict:
    """Fetch hourly temperature forecast for the next `days` days."""
    lat, lon = _get_coords(city)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "forecast_days": days,
        "timezone": "Europe/Ljubljana",
    }
    response = requests.get(OPEN_METEO_API_URL, params=params, timeout=10)


def fetch_current(city: str) -> Dict:
    """Fetch current weather for a city."""
    lat, lon = _get_coords(city)
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "Europe/Ljubljana",
    }
    response = requests.get(OPEN_METEO_API_URL, params=params, timeout=10)

def fetch_current(city: str, api_key: str = None) -> Dict:
    """Fetch current weather data for a city."""
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not provided")

    url = f"{OPENWEATHER_API_URL}/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
