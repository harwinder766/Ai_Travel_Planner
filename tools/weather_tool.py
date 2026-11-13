from config import settings
from langchain.tools import tool
from typing import Any
from utils.weather_info import WeatherInfo

class WeatherTool:
    def __init__(self):
        self.weather_info = WeatherInfo(api_key=settings.OPENWEATHERMAP_API_KEY)
        self.weather_tool_list = self._setup_tools()

    def _setup_tools(self) -> list:
        """Set up the tools for weather information retrieval."""

        @tool()
        def get_current_weather(place: str) -> Any:
            """Get the current weather for a given place."""
            weather_data = self.weather_info.get_current_weather(place)
            if weather_data:
                temp = weather_data.get('main', {}).get('temp', 'N/A')
                desc = weather_data.get('weather', [{}])[0].get('description', 'N/A')
                return f"Current weather in {place}: {temp}°C, {desc}"
            return f"Could not fetch weather for {place}"

        @tool()
        def get_weather_forecast(city: str) -> str:
            """Get weather forecast for a city"""
            forecast_data = self.weather_service.get_forecast_weather(city)
            if forecast_data and 'list' in forecast_data:
                forecast_summary = []
                for i in range(len(forecast_data['list'])):
                    item = forecast_data['list'][i]
                    date = item['dt_txt'].split(' ')[0]
                    temp = item['main']['temp']
                    desc = item['weather'][0]['description']
                    forecast_summary.append(f"{date}: {temp} degree celcius , {desc}")
                return f"Weather forecast for {city}:\n" + "\n".join(forecast_summary)
            return f"Could not fetch forecast for {city}"

        return [get_current_weather, get_weather_forecast]
        