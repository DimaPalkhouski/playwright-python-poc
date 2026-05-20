"""Base tests for epam.com — smoke checks against the live site.

All tests share a single page load via `epam_page_loaded` to avoid
Cloudflare rate limiting when running the full suite.
"""
import pytest
from playwright.sync_api import expect

from pages.epam_page import EpamPage


@pytest.mark.smoke
class TestEpamHomepage:
    """Homepage smoke checks — one page load shared across all tests in class."""

    def test_page_title_contains_epam(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.page).to_have_title(
            "EPAM | Software Engineering & Product Development Services"
        )

    def test_logo_is_visible(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.logo).to_be_visible()

    def test_logo_link_points_to_homepage(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.logo_link).to_have_attribute("href", "https://www.epam.com")

    def test_hero_title_is_visible(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.hero_title).to_be_visible()

    def test_hero_title_contains_expected_text(self, epam_page_loaded: EpamPage):
        title = epam_page_loaded.get_hero_title()
        assert "Engineering" in title

    def test_services_nav_link_is_visible(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.services_link).to_be_visible()

    def test_search_button_is_visible(self, epam_page_loaded: EpamPage):
        expect(epam_page_loaded.search_btn).to_be_visible()


@pytest.mark.smoke
class TestEpamNavigation:
    """Navigation tests — each requires its own page load."""

    def test_services_link_navigates_to_services_page(self, epam_page: EpamPage):
        epam_page.open()
        epam_page.click_services()
        expect(epam_page.page).to_have_url("https://www.epam.com/services")
