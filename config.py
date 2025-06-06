from typing import Dict, Tuple

# City coordinates
CITY_COORDS: Dict[str, Tuple[float, float]] = {
    "Koper": (45.5469, 13.7290),
    "Ljubljana": (46.0569, 14.5058),
    "Maribor": (46.5547, 15.6459),
}

# API Endpoints
OPEN_METEO_FORECAST_API = "https://api.open-meteo.com/v1/forecast"

# Timezone to be used in queries
TIMEZONE = "Europe/Ljubljana"

# Parameters for hourly forecast
HOURLY_PARAMS = [
    "temperature_2m",
    "precipitation",
    "cloudcover",
    "windspeed_10m"
]

# Parameters for daily forecast
DAILY_PARAMS = [
    "temperature_2m_min",
    "temperature_2m_max",
    "temperature_2m_mean",
    "precipitation_sum",
    "cloudcover_mean",
    "windspeed_10m_max"
]
