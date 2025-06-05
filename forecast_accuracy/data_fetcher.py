import os
import requests
from typing import Dict

OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5"


def fetch_forecast(city: str, api_key: str = None) -> Dict:
    """Fetch 7 day forecast for a given city using OpenWeatherMap."""
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not provided")

    url = f"{OPENWEATHER_API_URL}/forecast"  # 5 day/3 hour forecast
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


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
