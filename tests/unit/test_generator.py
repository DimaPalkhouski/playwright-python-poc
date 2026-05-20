"""Unit tests for data generators — no browser required."""
import pytest

from data.generators.builders import QuoteInputBuilder
from data.generators.pairwise import generate_pairwise
from data.generators.quote_generator import generate_quote_inputs
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput, VehicleType


@pytest.mark.unit
class TestPairwiseGenerator:

    def test_returns_fewer_cases_than_exhaustive(self):
        params = {
            "a": [1, 2, 3],
            "b": ["x", "y", "z"],
            "c": [True, False],
        }
        # Exhaustive = 3×3×2 = 18; pairwise should be significantly fewer
        cases = generate_pairwise(params)
        assert len(cases) < 18

    def test_all_parameter_keys_present_in_each_case(self):
        params = {"state": ["CA", "TX"], "age": [25, 45], "coverage": ["basic", "premium"]}
        for case in generate_pairwise(params):
            assert set(case.keys()) == {"state", "age", "coverage"}

    def test_all_values_come_from_parameter_sets(self):
        params = {"x": [1, 2], "y": ["a", "b"]}
        for case in generate_pairwise(params):
            assert case["x"] in params["x"]
            assert case["y"] in params["y"]


@pytest.mark.unit
class TestQuoteGenerator:

    def test_generates_quote_input_instances(self):
        inputs = generate_quote_inputs()
        assert all(isinstance(i, QuoteInput) for i in inputs)

    def test_generates_multiple_cases(self):
        inputs = generate_quote_inputs()
        assert len(inputs) > 1

    def test_all_cases_have_valid_state(self):
        from utils.config import Config
        inputs = generate_quote_inputs()
        for inp in inputs:
            assert inp.state in Config.ACTIVE_STATES


@pytest.mark.unit
class TestQuoteInputBuilder:

    def test_default_build_returns_quote_input(self):
        result = QuoteInputBuilder().build()
        assert isinstance(result, QuoteInput)

    def test_fluent_chain_sets_all_fields(self):
        result = (
            QuoteInputBuilder()
            .for_state("TX")
            .with_age(28)
            .with_coverage(CoverageLevel.PREMIUM)
            .with_vehicle(VehicleType.TRUCK)
            .with_credit(CreditTier.FAIR)
            .with_prior_claims(1)
            .with_deductible(1000)
            .build()
        )
        assert result.state == "TX"
        assert result.age == 28
        assert result.coverage_level == CoverageLevel.PREMIUM
        assert result.vehicle_type == VehicleType.TRUCK
        assert result.credit_tier == CreditTier.FAIR
        assert result.prior_claims == 1
        assert result.deductible == 1000

    def test_quote_input_is_immutable(self):
        inp = QuoteInputBuilder().build()
        with pytest.raises((AttributeError, TypeError)):
            inp.age = 99  # type: ignore[misc]
