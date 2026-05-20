"""Abstract contract for state-specific insurance rules."""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from data.models.expected_result import ComplianceRequirement, ExpectedResult
from data.models.quote_input import QuoteInput


class StateRule(ABC):
    """Base class for all state-specific insurance rule strategies.

    Each state subclass implements premium calculation and compliance validation
    independently. Tests depend on this abstraction, not concrete states.
    """

    @abstractmethod
    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        """Compute the expected monthly premium for the given input.

        Returns:
            Monthly premium as a Decimal (e.g., Decimal("125.50")).
        """

    @abstractmethod
    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        """Return the compliance requirements applicable to this input."""

    def is_eligible(self, quote: QuoteInput) -> tuple[bool, str]:
        """Return (eligible, reason). Override for state-specific eligibility rules."""
        return True, ""

    def expected_result(self, quote: QuoteInput) -> ExpectedResult:
        """Compute the full ExpectedResult for a given QuoteInput."""
        eligible, reason = self.is_eligible(quote)
        if not eligible:
            return ExpectedResult.ineligible(reason)

        monthly = self.calculate_premium(quote)
        annual = (monthly * 12).quantize(Decimal("0.01"))
        requirements = self.compliance_requirements(quote)

        return ExpectedResult(
            monthly_premium=monthly,
            annual_premium=annual,
            compliance_requirements=tuple(requirements),
            is_eligible=True,
        )
