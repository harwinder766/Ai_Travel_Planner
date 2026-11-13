import requests
from typing import Dict, Any

class WeatherInfo:
    def __init__(self, api_key: str, units: str = "metric", timeout: int = 10):
        if not api_key:
            raise ValueError("API key must be provided.")
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.units = units
        self.timeout = timeout
        self.session = requests.Session()


    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        req_params = {
            "appid": self.api_key,
            "units": self.units,
            **params
        }

        try:
            response = self.session.get(url, params=req_params, timeout=self.timeout)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # Returns the exact OpenWeatherMap error message (e.g., 404 city not found, 401 invalid key)
            error_msg = response.json().get("message", str(http_err)) if response.content else str(http_err)
            raise RuntimeError(f"Weather API error ({response.status_code}): {error_msg}") from http_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"Network error while connecting to Weather API: {req_err}") from req_err

    def get_current_weather(self, place: str) -> Dict[str, Any]:
        return self._make_request("weather", {"q": place})

    def get_forecast_weather(self, place: str) -> Dict[str, Any]:
        return self._make_request("forecast", {"q": place})