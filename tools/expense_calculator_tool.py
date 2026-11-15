from typing import Any

from langchain_core.tools import tool

from utils.expense_calculator import Calculator


class CalculatorTool:
    def __init__(self):
        self.calculator = Calculator()
        self.tools = self._setup_tools()

    def _setup_tools(self) -> list[Any]:
        @tool
        def estimate_total_hotel_cost(
            price_per_night: float, total_days: int
        ) -> float:
            """Calculate the total hotel cost."""
            return self.calculator.multiply(price_per_night, total_days)

        @tool
        def calculate_total_expense(costs: list[float]) -> float:
            """Calculate the total expense from a list of costs."""
            return self.calculator.calculate_total(*costs)

        @tool
        def calculate_daily_expense_budget(total_cost: float, days: int) -> float:
            """Calculate the average daily expense."""
            if days <= 0:
                raise ValueError("Days must be greater than zero.")
            return self.calculator.calculate_daily_budget(total_cost, days)

        return [
            estimate_total_hotel_cost,
            calculate_total_expense,
            calculate_daily_expense_budget,
        ]
