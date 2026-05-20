"""Data-driven pairwise E2E tests for insurance quote calculation."""
import pytest
from playwright.sync_api import Page

from data.generators.quote_generator import generate_quote_inputs
from flows.quote_flow import QuoteFlow
from rules.rule_registry import default_registry
from rules.validators import assert_quote_result
from utils.config import Config


def _pairwise_cases():
    """Generate pairwise QuoteInput cases and assign stable IDs."""
    return [
        pytest.param(inp, id=str(inp))
        for inp in generate_quote_inputs()
    ]


@pytest.mark.regression
class TestQuotePairwise:

    @pytest.mark.parametrize("quote_input", _pairwise_cases())
    def test_premium_matches_rules_engine(self, quote_flow: QuoteFlow, quote_input):
        """For each pairwise input, UI result must match rules engine expected output."""
        expected = default_registry.get(quote_input.state).expected_result(quote_input)
        actual = quote_flow.get_quote(quote_input)
        assert_quote_result(quote_input, expected, actual)
