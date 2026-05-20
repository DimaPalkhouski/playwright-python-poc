"""QuoteFlow — orchestrates the full insurance quote journey.

Uses PocQuotePage during POC phase.
When real app is available: update PocQuotePage locators (or split into
focused page objects) — this flow layer stays unchanged.
"""
from __future__ import annotations

from playwright.sync_api import Page

from data.models.expected_result import ActualResult
from data.models.quote_input import QuoteInput
from pages.poc_quote_page import PocQuotePage
from utils.config import Config


class QuoteFlow:
    """Drives the full insurance quote flow from customer info to result.

    Usage::

        flow = QuoteFlow(page, Config.BASE_URL)
        actual = flow.get_quote(quote_input)
    """

    def __init__(self, page: Page, base_url: str = Config.BASE_URL) -> None:
        self._page = PocQuotePage(page, base_url)

    def get_quote(self, quote: QuoteInput) -> ActualResult:
        """Fill all form steps and return the scraped result."""
        (
            self._page
            .open()
            .select_state(quote.state)
            .enter_age(quote.age)
            .select_marital_status(quote.marital_status.value)
            .submit_customer_info()
            .select_coverage_level(quote.coverage_level.value)
            .select_vehicle_type(quote.vehicle_type.value)
            .select_credit_tier(quote.credit_tier.value)
            .enter_annual_mileage(quote.annual_mileage)
            .enter_prior_claims(quote.prior_claims)
            .select_deductible(quote.deductible)
            .submit_coverage()
        )
        return self._page.scrape_result()

    def get_compliance_requirements(self, quote: QuoteInput) -> list[str]:
        """Return compliance requirement names displayed for the given quote."""
        self.get_quote(quote)
        return self._page.get_compliance_requirements()
