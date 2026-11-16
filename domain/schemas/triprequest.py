from datetime import date
from typing import Annotated, Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator

# Reusable constrained string type for Phase 6 input length safety
ShortStr = Annotated[str, Field(min_length=1, max_length=100)]


class TripRequest(BaseModel):
    # --- Core Route & Dates ---
    origin: str = Field(..., min_length=2, max_length=100, description="Starting city or airport.")
    destination: str = Field(..., min_length=2, max_length=100, description="Target destination.")
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD).")
    end_date: date = Field(..., description="Trip end date (YYYY-MM-DD).")

    # --- Traveller Profile (Used by Safety, Budget & Itinerary Agents) ---
    no_of_travelers: int = Field(..., ge=1, le=20, description="Total number of travelers.")
    traveler_types: list[Literal["adult", "child", "senior"]] = Field(
        default_factory=lambda: ["adult"],
        description="Age breakdown for pricing, safety, and pacing.",
    )
    nationality: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Passport country for visa and entry requirement checks.",
    )
    mobility_constraints: list[ShortStr] = Field(
        default_factory=list,
        description="Accessibility or physical limits (e.g., wheelchair, minimal walking).",
    )

    # --- Budget ---
    budget: float = Field(..., gt=0, description="Total trip budget.")
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$", description="ISO 4217 currency code.")
    budget_includes_flights: bool = Field(
        default=True,
        description="Whether the budget must cover transport between origin and destination.",
    )

    # --- Preferences & Negative Constraints ---
    pace: Literal["relaxed", "moderate", "packed"] = Field(
        default="moderate",
        description="Daily activity density and energy level.",
    )
    interests: list[ShortStr] = Field(default_factory=list, description="Preferred activities/themes.")
    food_preferences: list[ShortStr] = Field(default_factory=list, description="Dietary needs or cuisines.")
    hotel_preferences: list[ShortStr] = Field(default_factory=list, description="Accommodation style/amenities.")
    transport_preferences: list[ShortStr] = Field(
        default_factory=list,
        description="Preferred local transit (e.g., public transit, walking, taxi, rental car).",
    )
    avoid: list[ShortStr] = Field(
        default_factory=list,
        description="Things, foods, or areas to explicitly exclude.",
    )

    # --- Deterministic Validation ---
    @model_validator(mode="after")
    def validate_dates_and_travelers(self) -> "TripRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date.")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("Trip duration cannot exceed 30 days.")
        return self

    @property
    def duration_days(self) -> int:
        """Deterministic helper so agents never miscalculate trip length."""
        return (self.end_date - self.start_date).days + 1
