from datetime import date, datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Unified schema for hotels, restaurants, and activities."""
    name: str = Field(..., description="Official name of the place or service.")
    category: Literal["hotel", "restaurant", "activity", "transport"]
    location: str = Field(..., description="Neighborhood, address, or coordinates.")
    estimated_cost: float = Field(..., ge=0, description="Estimated cost in trip currency.")
    opening_hours: Optional[str] = Field(None, description="Operating hours if available.")
    notes: Optional[str] = Field(None, description="Why this fits the user's preferences.")
    source_url: Optional[str] = Field(None, description="Citation URL from MCP tool.")
    retrieved_at: Optional[datetime] = Field(None, description="Timestamp when data was fetched.")
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="High if backed by live MCP data; low if LLM-estimated.",
    )


class ScheduledStop(BaseModel):
    time_slot: str = Field(..., description="e.g., '09:00 - 11:30'")
    place_name: str
    activity_description: str
    transit_from_previous: Optional[str] = Field(
        None, description="e.g., '15 min walk' or '20 min metro via Maps MCP'"
    )
    estimated_cost: float = Field(default=0.0, ge=0)


class ItineraryDay(BaseModel):
    day_number: int = Field(..., ge=1)
    trip_date: date
    title: str = Field(..., description="Theme for the day, e.g., 'Historic Old Town & Food Tour'")
    stops: list[ScheduledStop] = Field(default_factory=list)
    daily_cost: float = Field(..., ge=0)


class BudgetBreakdown(BaseModel):
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")
    accommodation: float = Field(default=0.0, ge=0)
    food: float = Field(default=0.0, ge=0)
    transportation: float = Field(default=0.0, ge=0)
    activities: float = Field(default=0.0, ge=0)
    taxes_and_fees: float = Field(default=0.0, ge=0)
    contingency: float = Field(default=0.0, ge=0)
    total_cost: float = Field(..., ge=0)
    per_person_cost: float = Field(..., ge=0)
    per_day_cost: float = Field(..., ge=0)
    within_budget: bool


class WeatherSummary(BaseModel):
    overview: str
    temperature_range: str = Field(..., description="e.g., '18°C - 24°C'")
    rain_risk: Literal["low", "moderate", "high"]
    alerts: list[str] = Field(default_factory=list)


class SafetyReport(BaseModel):
    advisory_level: str = Field(..., description="e.g., 'Normal Precautions' or 'Exercise Caution'")
    visa_notes: Optional[str] = None
    health_and_safety_tips: list[str] = Field(default_factory=list)


class TravelPlan(BaseModel):
    # --- Overview & Metadata ---
    plan_version: int = Field(default=1, ge=1)
    trip_summary: str = Field(..., description="Concise overview of the trip plan.")
    assumptions: list[str] = Field(default_factory=list, description="Key assumptions made during planning.")

    # --- Core Schedule & Recommendations ---
    itinerary: list[ItineraryDay] = Field(..., description="Day-by-day schedule.")
    accommodation_options: list[RecommendationItem] = Field(default_factory=list)
    restaurants: list[RecommendationItem] = Field(default_factory=list)
    activities: list[RecommendationItem] = Field(default_factory=list)
    transportation: list[RecommendationItem] = Field(default_factory=list)

    # --- Financials, Weather & Compliance ---
    budget_breakdown: BudgetBreakdown
    weather: Optional[WeatherSummary] = None
    safety_notes: Optional[SafetyReport] = None

    # --- Provenance, Verification & Evaluation (Phases 1, 6, 7) ---
    sources: list[str] = Field(default_factory=list, description="Deduplicated citation URLs.")
    overall_confidence: Literal["high", "medium", "low"] = Field(default="medium")
    is_verified: bool = Field(default=False, description="Set to True only by the Critic/Verifier agent.")
    verification_notes: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))