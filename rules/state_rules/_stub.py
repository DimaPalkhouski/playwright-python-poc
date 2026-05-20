"""Stub state rule — used as a placeholder for states not yet implemented.

Replace by registering a concrete state rule in rule_registry.py.
"""
from __future__ import annotations

from decimal import Decimal

from data.models.expected_result import ComplianceRequirement
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput
from rules.base_rule import StateRule


_COVERAGE_BASE: dict[CoverageLevel, Decimal] = {
    CoverageLevel.BASIC: Decimal("80.00"),
    CoverageLevel.STANDARD: Decimal("120.00"),
    CoverageLevel.PREMIUM: Decimal("180.00"),
}

_CREDIT_MULTIPLIER: dict[CreditTier, Decimal] = {
    CreditTier.EXCELLENT: Decimal("0.90"),
    CreditTier.GOOD: Decimal("1.00"),
    CreditTier.FAIR: Decimal("1.15"),
    CreditTier.POOR: Decimal("1.35"),
}


class StubStateRule(StateRule):
    """Generic rule applied to any state without a concrete implementation.

    Uses simple flat-rate calculation. Intended for POC scaffolding only.
    """

    def __init__(self, state_code: str) -> None:
        self.state_code = state_code

    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        base = _COVERAGE_BASE[quote.coverage_level]
        credit_mult = _CREDIT_MULTIPLIER[quote.credit_tier]
        age_surcharge = Decimal("1.20") if quote.age < 25 else Decimal("1.00")
        claims_surcharge = Decimal(str(1 + quote.prior_claims * 0.10))
        return (base * credit_mult * age_surcharge * claims_surcharge).quantize(Decimal("0.01"))

    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        return [
            ComplianceRequirement(
                name="Liability Coverage",
                required=True,
                description="Minimum liability coverage required in all states",
            )
        ]
