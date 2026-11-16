import unittest
from datetime import date

from domain.policies import get_plan_policy_result
from domain.schemas.triprequest import TripRequest
from domain.schemas.travelplan import (
    BudgetBreakdown,
    ItineraryDay,
    TravelPlan,
)
from domain.validators import validate_budget_breakdown, validate_travel_plan


def make_request() -> TripRequest:
    return TripRequest(
        origin="Delhi",
        destination="Goa",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 11),
        no_of_travelers=2,
        budget=1000,
        currency="USD",
    )


def make_budget(total: float = 800, within_budget: bool = True) -> BudgetBreakdown:
    return BudgetBreakdown(
        currency="USD",
        accommodation=400,
        food=150,
        transportation=100,
        activities=100,
        taxes_and_fees=25,
        contingency=25,
        total_cost=total,
        per_person_cost=total / 2,
        per_day_cost=total / 2,
        within_budget=within_budget,
    )


def make_plan() -> TravelPlan:
    return TravelPlan(
        trip_summary="A short Goa trip.",
        itinerary=[
            ItineraryDay(day_number=1, trip_date=date(2026, 12, 10), title="Beaches", daily_cost=400),
            ItineraryDay(day_number=2, trip_date=date(2026, 12, 11), title="Food", daily_cost=400),
        ],
        budget_breakdown=make_budget(),
        sources=["https://example.com/goa"],
    )


class DomainValidatorTests(unittest.TestCase):
    def test_budget_components_must_match_total(self):
        budget = make_budget()
        invalid_budget = budget.model_copy(update={"total_cost": 801})

        with self.assertRaisesRegex(ValueError, "components"):
            validate_budget_breakdown(invalid_budget)

    def test_plan_must_cover_requested_dates(self):
        request = make_request()
        invalid_plan = make_plan().model_copy(
            update={
                "itinerary": [
                    ItineraryDay(
                        day_number=1,
                        trip_date=date(2026, 12, 10),
                        title="Beaches",
                        daily_cost=400,
                    ),
                    ItineraryDay(
                        day_number=2,
                        trip_date=date(2026, 12, 12),
                        title="Food",
                        daily_cost=400,
                    ),
                ]
            }
        )

        with self.assertRaisesRegex(ValueError, "dates"):
            validate_travel_plan(invalid_plan, request=request)


class DomainPolicyTests(unittest.TestCase):
    def test_unverified_plan_requires_review(self):
        result = get_plan_policy_result(make_plan(), make_request())

        self.assertTrue(result.allowed)
        self.assertTrue(result.requires_review)
        self.assertIn("verifier", " ".join(result.warnings))

    def test_over_budget_plan_requires_review(self):
        request = make_request()
        plan = make_plan().model_copy(
            update={
                "budget_breakdown": BudgetBreakdown(
                    currency="USD",
                    accommodation=600,
                    food=200,
                    transportation=150,
                    activities=100,
                    taxes_and_fees=100,
                    contingency=50,
                    total_cost=1200,
                    per_person_cost=600,
                    per_day_cost=600,
                    within_budget=False,
                )
            }
        )

        result = get_plan_policy_result(plan, request)

        self.assertTrue(result.requires_review)
        self.assertIn("exceeds", " ".join(result.warnings))


if __name__ == "__main__":
    unittest.main()
