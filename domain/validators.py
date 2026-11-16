from __future__ import annotations

import math
from datetime import date
from typing import Iterable
from urllib.parse import urlparse

from domain.schemas.triprequest import TripRequest
from domain.schemas.travelplan import (
    BudgetBreakdown,
    ItineraryDay,
    TravelPlan,
)

MONEY_TOLERANCE = 0.01


def _assert_close(actual: float, expected: float, message: str) -> None:
    if not math.isclose(actual, expected, abs_tol=MONEY_TOLERANCE):
        raise ValueError(f"{message} Expected {expected:.2f}, got {actual:.2f}.")


def _validate_finite(values: Iterable[float], field_name: str) -> None:
    if any(not math.isfinite(value) for value in values):
        raise ValueError(f"{field_name} must contain only finite numbers.")


def validate_trip_request(request: TripRequest) -> TripRequest:
    """Validate cross-field rules for a user trip request."""
    if not request.origin.strip():
        raise ValueError("origin cannot be blank.")
    if not request.destination.strip():
        raise ValueError("destination cannot be blank.")
    if request.duration_days > 30:
        raise ValueError("Trip duration cannot exceed 30 calendar days.")
    if not request.traveler_types:
        raise ValueError("traveler_types must contain at least one traveller type.")
    return request


def validate_budget_breakdown(
    budget: BudgetBreakdown,
    *,
    trip_budget: float | None = None,
    travellers: int | None = None,
    duration_days: int | None = None,
) -> BudgetBreakdown:
    """Validate budget arithmetic and optional trip-level totals."""
    components = (
        budget.accommodation,
        budget.food,
        budget.transportation,
        budget.activities,
        budget.taxes_and_fees,
        budget.contingency,
    )
    _validate_finite(
        components
        + (budget.total_cost, budget.per_person_cost, budget.per_day_cost),
        "Budget",
    )
    _assert_close(
        sum(components),
        budget.total_cost,
        "Budget components do not equal total_cost.",
    )

    if travellers is not None:
        if travellers <= 0:
            raise ValueError("travellers must be greater than zero.")
        _assert_close(
            budget.per_person_cost,
            budget.total_cost / travellers,
            "per_person_cost is inconsistent with total_cost.",
        )

    if duration_days is not None:
        if duration_days <= 0:
            raise ValueError("duration_days must be greater than zero.")
        _assert_close(
            budget.per_day_cost,
            budget.total_cost / duration_days,
            "per_day_cost is inconsistent with total_cost.",
        )

    if trip_budget is not None and budget.within_budget != (
        budget.total_cost <= trip_budget + MONEY_TOLERANCE
    ):
        raise ValueError("within_budget is inconsistent with total_cost and trip budget.")

    return budget


def _validate_itinerary_days(
    itinerary: list[ItineraryDay],
    *,
    start_date: date,
    duration_days: int,
) -> None:
    if len(itinerary) != duration_days:
        raise ValueError(
            f"Itinerary must contain {duration_days} days, got {len(itinerary)}."
        )

    expected_dates = {
        start_date.fromordinal(start_date.toordinal() + offset)
        for offset in range(duration_days)
    }
    actual_dates = {day.trip_date for day in itinerary}
    if actual_dates != expected_dates:
        raise ValueError("Itinerary dates must cover every date of the requested trip.")

    day_numbers = [day.day_number for day in itinerary]
    if day_numbers != list(range(1, duration_days + 1)):
        raise ValueError("Itinerary day_number values must be sequential starting at 1.")


def _validate_recommendations(plan: TravelPlan) -> None:
    groups = (
        ("accommodation_options", plan.accommodation_options, "hotel"),
        ("restaurants", plan.restaurants, "restaurant"),
        ("activities", plan.activities, "activity"),
        ("transportation", plan.transportation, "transport"),
    )
    for field_name, recommendations, expected_category in groups:
        for recommendation in recommendations:
            if recommendation.category != expected_category:
                raise ValueError(
                    f"{field_name} contains a {recommendation.category} recommendation; "
                    f"expected {expected_category}."
                )


def _validate_source_urls(urls: list[str]) -> None:
    if len(urls) != len(set(urls)):
        raise ValueError("sources must not contain duplicate URLs.")
    for source in urls:
        parsed = urlparse(source)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid source URL: {source}")


def validate_travel_plan(
    plan: TravelPlan,
    *,
    request: TripRequest | None = None,
) -> TravelPlan:
    """Validate a generated plan, optionally against its original request."""
    _validate_recommendations(plan)
    _validate_source_urls(plan.sources)

    if request is not None:
        validate_trip_request(request)
        validate_budget_breakdown(
            plan.budget_breakdown,
            trip_budget=request.budget,
            travellers=request.no_of_travelers,
            duration_days=request.duration_days,
        )
        _validate_itinerary_days(
            plan.itinerary,
            start_date=request.start_date,
            duration_days=request.duration_days,
        )
        if plan.budget_breakdown.currency != request.currency:
            raise ValueError("Plan currency must match the request currency.")
    else:
        validate_budget_breakdown(plan.budget_breakdown)

    return plan
