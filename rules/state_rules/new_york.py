"""New York-specific insurance rules (POC approximation)."""
from __future__ import annotations

from decimal import Decimal

from data.models.expected_result import ComplianceRequirement
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput, VehicleType
from rules.base_rule import StateRule


_COVERAGE_BASE: dict[CoverageLevel, Decimal] = {
    CoverageLevel.BASIC: Decimal("100.00"),
    CoverageLevel.STANDARD: Decimal("150.00"),
    CoverageLevel.PREMIUM: Decimal("225.00"),
}

_CREDIT_MULTIPLIER: dict[CreditTier, Decimal] = {
    CreditTier.EXCELLENT: Decimal("0.87"),
    CreditTier.GOOD: Decimal("1.00"),
    CreditTier.FAIR: Decimal("1.20"),
    CreditTier.POOR: Decimal("1.45"),
}

_VEHICLE_MULTIPLIER: dict[VehicleType, Decimal] = {
    VehicleType.SEDAN: Decimal("1.00"),
    VehicleType.SUV: Decimal("1.08"),
    VehicleType.TRUCK: Decimal("1.06"),
    VehicleType.MOTORCYCLE: Decimal("1.35"),
}

_MIN_ELIGIBLE_AGE = 17
_MAX_CLAIMS = 2
_BASE_RATE_MULTIPLIER = Decimal("1.25")


class NewYorkRule(StateRule):
    """Insurance rules for the state of New York."""

    def is_eligible(self, quote: QuoteInput) -> tuple[bool, str]:
        if quote.age < _MIN_ELIGIBLE_AGE:
            return False, f"Minimum eligible age in NY is {_MIN_ELIGIBLE_AGE}"
        if quote.prior_claims > _MAX_CLAIMS:
            return False, f"NY does not insure drivers with more than {_MAX_CLAIMS} prior claims"
        return True, ""

    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        base = _COVERAGE_BASE[quote.coverage_level]
        credit = _CREDIT_MULTIPLIER[quote.credit_tier]
        vehicle = _VEHICLE_MULTIPLIER[quote.vehicle_type]
        age_surcharge = Decimal("1.30") if quote.age < 25 else Decimal("1.00")
        claims_surcharge = Decimal(str(1 + quote.prior_claims * 0.15))

        return (
            base * _BASE_RATE_MULTIPLIER * credit * vehicle * age_surcharge * claims_surcharge
        ).quantize(Decimal("0.01"))

    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        return [
            ComplianceRequirement(
                name="Liability Coverage",
                required=True,
                description="Min $25,000 bodily injury / $10,000 property damage",
            ),
            ComplianceRequirement(
                name="Uninsured Motorist Coverage",
                required=True,
                description="Required in NY for all coverage levels",
            ),
            ComplianceRequirement(
                name="Personal Injury Protection (PIP)",
                required=True,
                description="NY no-fault state — PIP required",
            ),
        ]
