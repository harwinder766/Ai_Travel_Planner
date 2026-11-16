from __future__ import annotations

from dataclasses import dataclass

from domain.schemas.triprequest import TripRequest
from domain.schemas.travelplan import TravelPlan
from domain.validators import validate_travel_plan

HIGH_COST_REVIEW_RATIO = 1.10
LOW_CONFIDENCE_REVIEW_RATIO = 0.50


@dataclass(frozen=True)
class PolicyResult:
    """The result of applying product rules to a generated travel plan."""

    allowed: bool
    requires_review: bool
    warnings: tuple[str, ...] = ()


def get_plan_policy_result(
    plan: TravelPlan,
    request: TripRequest,
) -> PolicyResult:
    """Apply travel-product rules without hiding validation failures."""
    validate_travel_plan(plan, request=request)
    warnings: list[str] = []

    if plan.budget_breakdown.total_cost > request.budget:
        warnings.append("The estimated trip cost exceeds the user's budget.")

    if plan.overall_confidence == "low":
        warnings.append("The plan contains a low-confidence recommendation.")

    if not plan.sources:
        warnings.append("The plan has no source URLs and requires verification.")

    if not plan.is_verified:
        warnings.append("The plan has not been reviewed by the verifier agent.")

    requires_review = bool(warnings)
    if plan.budget_breakdown.total_cost > request.budget * HIGH_COST_REVIEW_RATIO:
        warnings.append("The estimated cost is more than 10% above the user's budget.")
        requires_review = True

    if (
        plan.overall_confidence == "low"
        and plan.budget_breakdown.total_cost
        < request.budget * LOW_CONFIDENCE_REVIEW_RATIO
    ):
        warnings.append("Low-confidence pricing is unusually far below the budget.")
        requires_review = True

    return PolicyResult(
        allowed=True,
        requires_review=requires_review,
        warnings=tuple(warnings),
    )


def enforce_plan_policy(plan: TravelPlan, request: TripRequest) -> TravelPlan:
    """Validate a plan and reject only hard policy violations."""
    result = get_plan_policy_result(plan, request)
    if not result.allowed:
        raise ValueError("Travel plan does not satisfy application policies.")
    return plan
