from typing import Any

from langchain_core.tools import tool

from config import settings
from utils.currency_converter import CurrencyConverter


class CurrencyConverterTool:
    def __init__(self):
        self.tools = self._setup_tools()

    def _setup_tools(self) -> list[Any]:
        @tool
        def convert_currency(
            amount: float, from_currency: str, to_currency: str
        ) -> float:
            """Convert an amount between currencies using a live exchange rate."""
            if not settings.exchange_rate_api_key:
                raise RuntimeError(
                    "Currency conversion is unavailable. "
                    "Set EXCHANGE_RATE_API_KEY."
                )
            return CurrencyConverter(settings.exchange_rate_api_key).convert(
                amount, from_currency, to_currency
            )

        return [convert_currency]
