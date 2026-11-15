import requests

class CurrencyConverter:
    def __init__(self, api_key: str, timeout: int = 10):
        self.base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/"
        self.timeout = timeout
    
    def convert(self, amount:float, from_currency:str, to_currency:str):
        """Convert the amount from one currency to another"""
        url = f"{self.base_url}{from_currency.upper()}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("result") != "success":
            raise RuntimeError(
                f"Currency API error: {payload.get('error-type', 'unknown error')}"
            )
        rates = payload.get("conversion_rates", {})
        target_currency = to_currency.upper()
        if target_currency not in rates:
            raise ValueError(f"{to_currency} not found in exchange rates.")
        return amount * rates[target_currency]
    