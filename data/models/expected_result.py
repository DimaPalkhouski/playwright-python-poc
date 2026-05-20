from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ComplianceRequirement:
    """A single state compliance requirement."""

    name: str
    required: bool
    description: str = ""


@dataclass(frozen=True)
class ExpectedResult:
    """Expected outcome for a given QuoteInput, computed by the rules engine."""

    monthly_premium: Decimal
    annual_premium: Decimal
    compliance_requirements: tuple[ComplianceRequirement, ...] = field(default_factory=tuple)
    is_eligible: bool = True
    ineligibility_reason: str = ""

    @classmethod
    def ineligible(cls, reason: str) -> "ExpectedResult":
        return cls(
            monthly_premium=Decimal("0"),
            annual_premium=Decimal("0"),
            is_eligible=False,
            ineligibility_reason=reason,
        )


@dataclass(frozen=True)
class ActualResult:
    """Actual outcome scraped from the UI after form submission."""

    monthly_premium: Decimal | None
    annual_premium: Decimal | None
    is_eligible: bool
    ineligibility_reason: str = ""
    raw_text: str = ""
