from typing import Any

from langchain_core.tools import tool

from config import settings
from utils.weather_info import WeatherInfo


class WeatherTool:
    def __init__(self):
        self.tools = self._setup_tools()

    def _service(self) -> WeatherInfo:
        if not settings.openweathermap_api_key:
            raise RuntimeError(
                "Weather lookup is unavailable. Set OPENWEATHERMAP_API_KEY."
            )
        return WeatherInfo(api_key=settings.openweathermap_api_key)

    def _setup_tools(self) -> list[Any]:
        @tool
        def get_current_weather(place: str) -> str:
            """Get the current weather for a given place."""
            weather_data = self._service().get_current_weather(place)
            temperature = weather_data.get("main", {}).get("temp", "N/A")
            description = weather_data.get("weather", [{}])[0].get(
                "description", "N/A"
            )
            return f"Current weather in {place}: {temperature}°C, {description}"

        @tool
        def get_weather_forecast(city: str) -> str:
            """Get a five-day weather forecast for a city."""
            forecast_data = self._service().get_forecast_weather(city)
            summaries = []
            for item in forecast_data.get("list", []):
                date = item.get("dt_txt", "").split(" ")[0]
                temperature = item.get("main", {}).get("temp", "N/A")
                description = item.get("weather", [{}])[0].get(
                    "description", "N/A"
                )
                summaries.append(f"{date}: {temperature}°C, {description}")
            if not summaries:
                raise RuntimeError(f"No forecast data was returned for {city}.")
            return f"Weather forecast for {city}:\n" + "\n".join(summaries)

        return [get_current_weather, get_weather_forecast]
