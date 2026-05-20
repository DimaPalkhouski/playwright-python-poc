"""Unit tests for the rules engine — no browser required."""
import pytest
from decimal import Decimal

from data.generators.builders import QuoteInputBuilder
from data.models.quote_input import CoverageLevel, CreditTier, VehicleType
from rules.rule_registry import build_default_registry
from rules.state_rules.california import CaliforniaRule
from rules.state_rules.new_york import NewYorkRule


@pytest.mark.unit
class TestCaliforniaRule:

    def setup_method(self):
        self.rule = CaliforniaRule()
        self.base_input = (
            QuoteInputBuilder()
            .for_state("CA")
            .with_age(35)
            .with_coverage(CoverageLevel.STANDARD)
            .build()
        )

    def test_eligible_driver_returns_positive_premium(self):
        result = self.rule.expected_result(self.base_input)
        assert result.is_eligible
        assert result.monthly_premium > Decimal("0")

    def test_annual_premium_is_twelve_times_monthly(self):
        result = self.rule.expected_result(self.base_input)
        assert result.annual_premium == (result.monthly_premium * 12).quantize(Decimal("0.01"))

    def test_poor_credit_increases_premium(self):
        good = QuoteInputBuilder().for_state("CA").with_credit(CreditTier.GOOD).build()
        poor = QuoteInputBuilder().for_state("CA").with_credit(CreditTier.POOR).build()
        assert self.rule.calculate_premium(poor) > self.rule.calculate_premium(good)

    def test_young_driver_surcharge_applies(self):
        young = QuoteInputBuilder().for_state("CA").with_age(22).build()
        adult = QuoteInputBuilder().for_state("CA").with_age(35).build()
        assert self.rule.calculate_premium(young) > self.rule.calculate_premium(adult)

    def test_prior_claims_increase_premium(self):
        clean = QuoteInputBuilder().for_state("CA").with_prior_claims(0).build()
        risky = QuoteInputBuilder().for_state("CA").with_prior_claims(2).build()
        assert self.rule.calculate_premium(risky) > self.rule.calculate_premium(clean)

    def test_too_many_claims_marks_ineligible(self):
        over_limit = QuoteInputBuilder().for_state("CA").with_prior_claims(4).build()
        result = self.rule.expected_result(over_limit)
        assert not result.is_eligible
        assert "claims" in result.ineligibility_reason.lower()

    def test_standard_coverage_requires_uninsured_motorist(self):
        result = self.rule.expected_result(self.base_input)
        names = [r.name for r in result.compliance_requirements]
        assert "Uninsured Motorist Coverage" in names

    def test_basic_coverage_does_not_require_uninsured_motorist(self):
        basic = QuoteInputBuilder().for_state("CA").with_coverage(CoverageLevel.BASIC).build()
        result = self.rule.expected_result(basic)
        names = [r.name for r in result.compliance_requirements]
        assert "Uninsured Motorist Coverage" not in names


@pytest.mark.unit
class TestNewYorkRule:

    def setup_method(self):
        self.rule = NewYorkRule()

    def test_ny_max_claims_is_stricter_than_ca(self):
        """NY allows max 2 claims; 3 claims should be ineligible."""
        three_claims = QuoteInputBuilder().for_state("NY").with_prior_claims(3).build()
        result = self.rule.expected_result(three_claims)
        assert not result.is_eligible

    def test_ny_always_requires_pip(self):
        quote = QuoteInputBuilder().for_state("NY").build()
        reqs = self.rule.compliance_requirements(quote)
        names = [r.name for r in reqs]
        assert "Personal Injury Protection (PIP)" in names

    def test_ny_min_age_is_17(self):
        underage = QuoteInputBuilder().for_state("NY").with_age(16).build()
        eligible, reason = self.rule.is_eligible(underage)
        assert not eligible


@pytest.mark.unit
class TestRuleRegistry:

    def setup_method(self):
        self.registry = build_default_registry()

    def test_registered_states_include_all_four(self):
        states = self.registry.registered_states()
        assert set(states) >= {"CA", "TX", "NY", "FL"}

    def test_unknown_state_falls_back_to_stub(self):
        rule = self.registry.get("ZZ")
        quote = QuoteInputBuilder().for_state("ZZ").build()
        result = rule.expected_result(quote)
        # Stub should still return a positive premium for a clean driver
        assert result.monthly_premium > Decimal("0")

    def test_lookup_is_case_insensitive(self):
        rule_lower = self.registry.get("ca")
        rule_upper = self.registry.get("CA")
        assert type(rule_lower) == type(rule_upper)
