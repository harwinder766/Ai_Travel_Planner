from typing import Any

from langchain_core.tools import tool

from config import settings


class PlaceSearchTool:
    def __init__(self):
        self.tools = self._setup_tools()

    def _search(self, place: str, category: str) -> str:
        if not settings.tavily_api_key:
            raise RuntimeError(
                f"{category.title()} search is unavailable. Set TAVILY_API_KEY."
            )

        from langchain_tavily import TavilySearch
        from langchain_tavily._utilities import TavilySearchAPIWrapper

        result = TavilySearch(
            max_results=5,
            topic="travel",
            api_wrapper=TavilySearchAPIWrapper(
                tavily_api_key=settings.tavily_api_key
            ),
        ).invoke(
            f"Find current {category} recommendations in {place}. "
            "Return names, locations, useful details, and source URLs."
        )
        return str(result)

    def _setup_tools(self) -> list[Any]:
        @tool
        def search_attractions(place: str) -> str:
            """Search current attractions for a place."""
            return self._search(place, "attractions")

        @tool
        def search_restaurants(place: str) -> str:
            """Search current restaurants for a place."""
            return self._search(place, "restaurants")

        @tool
        def search_activities(place: str) -> str:
            """Search current activities for a place."""
            return self._search(place, "activities")

        @tool
        def search_transportation(place: str) -> str:
            """Search transportation options for a place."""
            return self._search(place, "transportation")

        return [
            search_attractions,
            search_restaurants,
            search_activities,
            search_transportation,
        ]
