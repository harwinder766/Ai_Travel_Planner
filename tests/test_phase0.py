import unittest
from dataclasses import replace
from unittest.mock import patch


class CalculatorTests(unittest.TestCase):
    def test_daily_budget_rejects_zero_days(self):
        from utils.expense_calculator import Calculator

        with self.assertRaises(ValueError):
            Calculator.calculate_daily_budget(100, 0)

    def test_hotel_calculation_supports_decimal_prices(self):
        from utils.expense_calculator import Calculator

        self.assertEqual(Calculator.multiply(125.50, 3), 376.50)


class ConfigurationTests(unittest.TestCase):
    def test_model_loader_reports_missing_provider_key(self):
        from config import settings
        from utils.model_loader import ModelLoader

        missing_key_settings = replace(settings, groq_api_key=None)
        with patch("utils.model_loader.settings", missing_key_settings):
            with self.assertRaisesRegex(RuntimeError, "GROQ"):
                ModelLoader("groq")()


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self):
        from fastapi.testclient import TestClient

        from main import app

        response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_query_validation_rejects_short_questions(self):
        from fastapi.testclient import TestClient

        from main import app

        response = TestClient(app).post("/query", json={"question": "Hi"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
