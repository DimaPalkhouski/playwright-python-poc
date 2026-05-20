"""POC quote page — single page object covering the full insurance quote flow.

Intentionally covers all steps (customer info, coverage, result, compliance)
in one class because the real app structure is not yet known.

When real app access is received:
    1. Rename this file to reflect the actual page structure
    2. Split into focused page objects (one per screen) under pages/quote/
    3. Update locators to match real selectors
    4. Update flows/quote_flow.py to compose the new pages
    5. Nothing else in the framework needs to change
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from playwright.sync_api import Page

from data.models.expected_result import ActualResult
from data.models.quote_input import QuoteInput
from pages.base_page import BasePage


class PocQuotePage(BasePage):
    """Single-page object for the POC mock app.

    All locator IDs here correspond to mocks/insurance_app.html.
    Replace with real selectors once app access is granted.
    """

    # ── Entry point ──────────────────────────────────────────────────────────
    PATH = "/quote/customer"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # Step 1 — customer info
        self.state_select = page.locator("#state")
        self.age_input = page.locator("#age")
        self.marital_status_select = page.locator("#marital-status")
        self.next_customer_btn = page.locator("#btn-next-customer")

        # Step 2 — coverage
        self.coverage_level_select = page.locator("#coverage-level")
        self.vehicle_type_select = page.locator("#vehicle-type")
        self.credit_tier_select = page.locator("#credit-tier")
        self.annual_mileage_input = page.locator("#annual-mileage")
        self.prior_claims_input = page.locator("#prior-claims")
        self.deductible_select = page.locator("#deductible")
        self.next_coverage_btn = page.locator("#btn-next-coverage")

        # Step 3 — result
        self.monthly_premium_el = page.locator("#monthly-premium")
        self.annual_premium_el = page.locator("#annual-premium")
        self.ineligibility_banner = page.locator("#ineligibility-banner")
        self.ineligibility_reason_el = page.locator("#ineligibility-reason")

        # Compliance
        self.compliance_status_el = page.locator("#compliance-status")
        self.compliance_items = page.locator(".compliance-item")

    # ── Step 1 ───────────────────────────────────────────────────────────────

    def open(self) -> "PocQuotePage":
        self.navigate(self.PATH)
        self.wait_for_load()
        return self

    def select_state(self, state: str) -> "PocQuotePage":
        self.state_select.select_option(value=state)
        return self

    def enter_age(self, age: int) -> "PocQuotePage":
        self.age_input.fill(str(age))
        return self

    def select_marital_status(self, status: str) -> "PocQuotePage":
        self.marital_status_select.select_option(value=status)
        return self

    def submit_customer_info(self) -> "PocQuotePage":
        self.next_customer_btn.click()
        self.wait_for_load()
        return self

    # ── Step 2 ───────────────────────────────────────────────────────────────

    def select_coverage_level(self, level: str) -> "PocQuotePage":
        self.coverage_level_select.select_option(value=level)
        return self

    def select_vehicle_type(self, vehicle_type: str) -> "PocQuotePage":
        self.vehicle_type_select.select_option(value=vehicle_type)
        return self

    def select_credit_tier(self, tier: str) -> "PocQuotePage":
        self.credit_tier_select.select_option(value=tier)
        return self

    def enter_annual_mileage(self, mileage: int) -> "PocQuotePage":
        self.annual_mileage_input.fill(str(mileage))
        return self

    def enter_prior_claims(self, claims: int) -> "PocQuotePage":
        self.prior_claims_input.fill(str(claims))
        return self

    def select_deductible(self, deductible: int) -> "PocQuotePage":
        self.deductible_select.select_option(value=str(deductible))
        return self

    def submit_coverage(self) -> "PocQuotePage":
        self.next_coverage_btn.click()
        self.wait_for_load()
        return self

    # ── Result reading ───────────────────────────────────────────────────────

    def is_ineligible(self) -> bool:
        return self.ineligibility_banner.is_visible()

    def _parse_currency(self, text: str) -> Decimal | None:
        try:
            return Decimal(text.strip().replace("$", "").replace(",", ""))
        except InvalidOperation:
            return None

    def scrape_result(self) -> ActualResult:
        """Read the result page and return a typed ActualResult."""
        ineligible = self.is_ineligible()
        return ActualResult(
            is_eligible=not ineligible,
            ineligibility_reason=(
                self.ineligibility_reason_el.inner_text().strip() if ineligible else ""
            ),
            monthly_premium=(
                None if ineligible
                else self._parse_currency(self.monthly_premium_el.inner_text())
            ),
            annual_premium=(
                None if ineligible
                else self._parse_currency(self.annual_premium_el.inner_text())
            ),
        )

    # ── Compliance reading ───────────────────────────────────────────────────

    def get_compliance_requirements(self) -> list[str]:
        return self.compliance_items.all_inner_texts()

    def is_compliant(self) -> bool:
        return "compliant" in self.compliance_status_el.inner_text().lower()
