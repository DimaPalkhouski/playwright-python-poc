"""California-specific insurance rules (POC approximation).

Based on data/datasets/states.yaml CA values.
Update multipliers once real rate tables are available.
"""
from __future__ import annotations

from decimal import Decimal

from data.models.expected_result import ComplianceRequirement
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput, VehicleType
from rules.base_rule import StateRule


_COVERAGE_BASE: dict[CoverageLevel, Decimal] = {
    CoverageLevel.BASIC: Decimal("92.00"),
    CoverageLevel.STANDARD: Decimal("138.00"),
    CoverageLevel.PREMIUM: Decimal("207.00"),
}

_CREDIT_MULTIPLIER: dict[CreditTier, Decimal] = {
    CreditTier.EXCELLENT: Decimal("0.88"),
    CreditTier.GOOD: Decimal("1.00"),
    CreditTier.FAIR: Decimal("1.18"),
    CreditTier.POOR: Decimal("1.40"),
}

_VEHICLE_MULTIPLIER: dict[VehicleType, Decimal] = {
    VehicleType.SEDAN: Decimal("1.00"),
    VehicleType.SUV: Decimal("1.10"),
    VehicleType.TRUCK: Decimal("1.08"),
    VehicleType.MOTORCYCLE: Decimal("1.30"),
}

_MIN_ELIGIBLE_AGE = 16
_MAX_CLAIMS = 3
_BASE_RATE_MULTIPLIER = Decimal("1.15")


class CaliforniaRule(StateRule):
    """Insurance rules for the state of California."""

    def is_eligible(self, quote: QuoteInput) -> tuple[bool, str]:
        if quote.age < _MIN_ELIGIBLE_AGE:
            return False, f"Minimum eligible age in CA is {_MIN_ELIGIBLE_AGE}"
        if quote.prior_claims > _MAX_CLAIMS:
            return False, f"CA does not insure drivers with more than {_MAX_CLAIMS} prior claims"
        return True, ""

    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        base = _COVERAGE_BASE[quote.coverage_level]
        credit = _CREDIT_MULTIPLIER[quote.credit_tier]
        vehicle = _VEHICLE_MULTIPLIER[quote.vehicle_type]
        age_surcharge = Decimal("1.25") if quote.age < 25 else Decimal("1.00")
        claims_surcharge = Decimal(str(1 + quote.prior_claims * 0.12))
        deductible_discount = Decimal("0.95") if quote.deductible >= 1000 else Decimal("1.00")

        return (
            base * _BASE_RATE_MULTIPLIER * credit * vehicle * age_surcharge
            * claims_surcharge * deductible_discount
        ).quantize(Decimal("0.01"))

    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        reqs = [
            ComplianceRequirement(
                name="Liability Coverage",
                required=True,
                description="Min $15,000 bodily injury / $5,000 property damage",
            ),
        ]
        if quote.coverage_level in (CoverageLevel.STANDARD, CoverageLevel.PREMIUM):
            reqs.append(
                ComplianceRequirement(
                    name="Uninsured Motorist Coverage",
                    required=True,
                    description="Required for standard and premium plans in CA",
                )
            )
        return reqs
