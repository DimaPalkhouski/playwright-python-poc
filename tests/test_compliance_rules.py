"""Golden case E2E tests — hand-picked must-pass scenarios loaded from YAML."""
import pytest
import yaml
from pathlib import Path
from decimal import Decimal

from data.generators.builders import QuoteInputBuilder
from data.models.quote_input import CoverageLevel, CreditTier, MaritalStatus, VehicleType
from flows.quote_flow import QuoteFlow
from rules.rule_registry import default_registry
from rules.validators import assert_quote_result


def _load_golden_cases():
    path = Path(__file__).parent.parent / "data" / "datasets" / "golden_cases.yaml"
    with open(path) as f:
        cases = yaml.safe_load(f)
    return [pytest.param(case, id=case["id"]) for case in cases]


def _build_input_from_yaml(raw: dict):
    return (
        QuoteInputBuilder()
        .for_state(raw["state"])
        .with_age(raw["age"])
        .with_coverage(CoverageLevel(raw["coverage_level"]))
        .with_vehicle(VehicleType(raw["vehicle_type"]))
        .with_credit(CreditTier(raw["credit_tier"]))
        .with_marital_status(MaritalStatus(raw["marital_status"]))
        .with_prior_claims(raw["prior_claims"])
        .with_deductible(raw["deductible"])
        .build()
    )


@pytest.mark.smoke
class TestGoldenCases:

    @pytest.mark.parametrize("case", _load_golden_cases())
    def test_golden_case(self, quote_flow: QuoteFlow, case):
        """Every golden case must produce the expected eligibility outcome."""
        quote_input = _build_input_from_yaml(case["input"])
        expected = default_registry.get(quote_input.state).expected_result(quote_input)

        assert expected.is_eligible == case["expected_eligible"], (
            f"[{case['id']}] Eligibility mismatch: "
            f"expected={case['expected_eligible']}, rules_engine={expected.is_eligible}\n"
            f"Input: {quote_input}"
        )

        actual = quote_flow.get_quote(quote_input)
        assert_quote_result(quote_input, expected, actual)


@pytest.mark.compliance
class TestStateCompliance:

    @pytest.mark.parametrize("state", ["CA", "TX", "NY", "FL"])
    def test_compliance_requirements_displayed_for_state(
        self, quote_flow: QuoteFlow, state: str
    ):
        """Compliance items shown in UI must match rules engine requirements."""
        quote_input = QuoteInputBuilder().for_state(state).build()
        expected_reqs = default_registry.get(state).compliance_requirements(quote_input)
        expected_names = {r.name for r in expected_reqs}

        displayed = quote_flow.get_compliance_requirements(quote_input)
        displayed_text = " ".join(displayed)

        for name in expected_names:
            assert name in displayed_text, (
                f"[{state}] Expected compliance requirement '{name}' not found in UI.\n"
                f"Displayed: {displayed}"
            )
