"""Fluent builder for constructing QuoteInput instances in tests."""
from __future__ import annotations

from data.models.quote_input import (
    CoverageLevel,
    CreditTier,
    MaritalStatus,
    QuoteInput,
    VehicleType,
)


class QuoteInputBuilder:
    """Builds a QuoteInput step by step with sensible defaults.

    Usage::

        input_ = (
            QuoteInputBuilder()
            .for_state("CA")
            .with_age(35)
            .with_coverage(CoverageLevel.PREMIUM)
            .build()
        )
    """

    def __init__(self) -> None:
        self._state = "CA"
        self._age = 35
        self._coverage_level = CoverageLevel.STANDARD
        self._vehicle_type = VehicleType.SEDAN
        self._credit_tier = CreditTier.GOOD
        self._marital_status = MaritalStatus.SINGLE
        self._annual_mileage = 12000
        self._prior_claims = 0
        self._deductible = 500

    def for_state(self, state: str) -> "QuoteInputBuilder":
        self._state = state
        return self

    def with_age(self, age: int) -> "QuoteInputBuilder":
        self._age = age
        return self

    def with_coverage(self, level: CoverageLevel) -> "QuoteInputBuilder":
        self._coverage_level = level
        return self

    def with_vehicle(self, vehicle_type: VehicleType) -> "QuoteInputBuilder":
        self._vehicle_type = vehicle_type
        return self

    def with_credit(self, tier: CreditTier) -> "QuoteInputBuilder":
        self._credit_tier = tier
        return self

    def with_marital_status(self, status: MaritalStatus) -> "QuoteInputBuilder":
        self._marital_status = status
        return self

    def with_annual_mileage(self, mileage: int) -> "QuoteInputBuilder":
        self._annual_mileage = mileage
        return self

    def with_prior_claims(self, claims: int) -> "QuoteInputBuilder":
        self._prior_claims = claims
        return self

    def with_deductible(self, deductible: int) -> "QuoteInputBuilder":
        self._deductible = deductible
        return self

    def build(self) -> QuoteInput:
        return QuoteInput(
            state=self._state,
            age=self._age,
            coverage_level=self._coverage_level,
            vehicle_type=self._vehicle_type,
            credit_tier=self._credit_tier,
            marital_status=self._marital_status,
            annual_mileage=self._annual_mileage,
            prior_claims=self._prior_claims,
            deductible=self._deductible,
        )
