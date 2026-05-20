"""Generates QuoteInput combinations using pairwise strategy."""
from __future__ import annotations

from data.generators.pairwise import generate_pairwise
from data.models.quote_input import (
    CoverageLevel,
    CreditTier,
    MaritalStatus,
    QuoteInput,
    VehicleType,
)
from utils.config import Config


_PARAMETERS: dict[str, list] = {
    "state": Config.ACTIVE_STATES,
    "age": [20, 30, 45, 65],
    "coverage_level": list(CoverageLevel),
    "vehicle_type": list(VehicleType),
    "credit_tier": list(CreditTier),
    "marital_status": list(MaritalStatus),
    "prior_claims": [0, 1, 3],
    "deductible": [250, 500, 1000],
}


def generate_quote_inputs() -> list[QuoteInput]:
    """Return a pairwise-reduced list of QuoteInput instances.

    Covers all 2-way parameter interactions with far fewer cases than exhaustive.
    """
    raw_cases = generate_pairwise(_PARAMETERS)
    return [
        QuoteInput(
            state=case["state"],
            age=case["age"],
            coverage_level=case["coverage_level"],
            vehicle_type=case["vehicle_type"],
            credit_tier=case["credit_tier"],
            marital_status=case["marital_status"],
            prior_claims=case["prior_claims"],
            deductible=case["deductible"],
        )
        for case in raw_cases
    ]
