from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class CoverageLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


class CreditTier(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"


@dataclass(frozen=True)
class QuoteInput:
    """Immutable representation of all inputs required to request an insurance quote.

    Frozen to prevent accidental mutation across parametrized test runs.
    """

    state: str
    age: int
    coverage_level: CoverageLevel
    vehicle_type: VehicleType
    credit_tier: CreditTier
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    annual_mileage: int = 12000
    prior_claims: int = 0
    deductible: int = 500

    def __str__(self) -> str:
        return (
            f"QuoteInput(state={self.state}, age={self.age}, "
            f"coverage={self.coverage_level.value}, vehicle={self.vehicle_type.value}, "
            f"credit={self.credit_tier.value})"
        )
