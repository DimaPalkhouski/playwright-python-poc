"""Compares expected vs actual results and surfaces rich diffs on failure."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from data.models.expected_result import ActualResult, ExpectedResult
from data.models.quote_input import QuoteInput


_PREMIUM_TOLERANCE = Decimal("0.05")  # 5-cent tolerance for rounding differences


@dataclass
class ValidationResult:
    passed: bool
    messages: list[str]

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        body = "\n  ".join(self.messages)
        return f"[{status}]\n  {body}"


def validate_quote_result(
    quote: QuoteInput,
    expected: ExpectedResult,
    actual: ActualResult,
) -> ValidationResult:
    """Compare expected vs actual results and return a rich ValidationResult.

    Checks:
    - Eligibility match
    - Monthly premium within tolerance
    - Annual premium within tolerance
    """
    messages: list[str] = [f"Input: {quote}"]
    failures: list[str] = []

    # ── Eligibility ─────────────────────────────────────────────────────────
    if expected.is_eligible != actual.is_eligible:
        failures.append(
            f"Eligibility mismatch: expected={expected.is_eligible}, actual={actual.is_eligible}"
        )
        if not expected.is_eligible:
            failures.append(f"  Expected ineligibility reason: {expected.ineligibility_reason}")
        if not actual.is_eligible:
            failures.append(f"  Actual ineligibility reason: {actual.ineligibility_reason}")

    # ── Premium checks (only when both expect eligibility) ──────────────────
    if expected.is_eligible and actual.is_eligible:
        if actual.monthly_premium is None:
            failures.append("Monthly premium missing from actual result")
        elif abs(actual.monthly_premium - expected.monthly_premium) > _PREMIUM_TOLERANCE:
            failures.append(
                f"Monthly premium mismatch: "
                f"expected={expected.monthly_premium}, actual={actual.monthly_premium} "
                f"(tolerance={_PREMIUM_TOLERANCE})"
            )

        if actual.annual_premium is None:
            failures.append("Annual premium missing from actual result")
        elif abs(actual.annual_premium - expected.annual_premium) > _PREMIUM_TOLERANCE:
            failures.append(
                f"Annual premium mismatch: "
                f"expected={expected.annual_premium}, actual={actual.annual_premium} "
                f"(tolerance={_PREMIUM_TOLERANCE})"
            )

    if failures:
        messages.extend(failures)
        return ValidationResult(passed=False, messages=messages)

    messages.append("All checks passed ✓")
    return ValidationResult(passed=True, messages=messages)


def assert_quote_result(
    quote: QuoteInput,
    expected: ExpectedResult,
    actual: ActualResult,
) -> None:
    """Validate and assert, raising AssertionError with full context on failure."""
    result = validate_quote_result(quote, expected, actual)
    assert result.passed, str(result)
