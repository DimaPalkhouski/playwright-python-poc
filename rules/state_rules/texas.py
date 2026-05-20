"""Texas-specific insurance rules (POC approximation)."""
from __future__ import annotations

from decimal import Decimal

from data.models.expected_result import ComplianceRequirement
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput, VehicleType
from rules.base_rule import StateRule


_COVERAGE_BASE: dict[CoverageLevel, Decimal] = {
    CoverageLevel.BASIC: Decimal("84.00"),
    CoverageLevel.STANDARD: Decimal("126.00"),
    CoverageLevel.PREMIUM: Decimal("189.00"),
}

_CREDIT_MULTIPLIER: dict[CreditTier, Decimal] = {
    CreditTier.EXCELLENT: Decimal("0.90"),
    CreditTier.GOOD: Decimal("1.00"),
    CreditTier.FAIR: Decimal("1.15"),
    CreditTier.POOR: Decimal("1.35"),
}

_VEHICLE_MULTIPLIER: dict[VehicleType, Decimal] = {
    VehicleType.SEDAN: Decimal("1.00"),
    VehicleType.SUV: Decimal("1.12"),
    VehicleType.TRUCK: Decimal("1.05"),
    VehicleType.MOTORCYCLE: Decimal("1.25"),
}

_MIN_ELIGIBLE_AGE = 16
_MAX_CLAIMS = 3
_BASE_RATE_MULTIPLIER = Decimal("1.05")


class TexasRule(StateRule):
    """Insurance rules for the state of Texas."""

    def is_eligible(self, quote: QuoteInput) -> tuple[bool, str]:
        if quote.age < _MIN_ELIGIBLE_AGE:
            return False, f"Minimum eligible age in TX is {_MIN_ELIGIBLE_AGE}"
        if quote.prior_claims > _MAX_CLAIMS:
            return False, f"TX does not insure drivers with more than {_MAX_CLAIMS} prior claims"
        return True, ""

    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        base = _COVERAGE_BASE[quote.coverage_level]
        credit = _CREDIT_MULTIPLIER[quote.credit_tier]
        vehicle = _VEHICLE_MULTIPLIER[quote.vehicle_type]
        age_surcharge = Decimal("1.20") if quote.age < 25 else Decimal("1.00")
        claims_surcharge = Decimal(str(1 + quote.prior_claims * 0.10))

        return (
            base * _BASE_RATE_MULTIPLIER * credit * vehicle * age_surcharge * claims_surcharge
        ).quantize(Decimal("0.01"))

    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        return [
            ComplianceRequirement(
                name="Liability Coverage",
                required=True,
                description="Min $30,000 bodily injury / $25,000 property damage",
            ),
        ]
