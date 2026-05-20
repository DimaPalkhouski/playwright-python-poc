"""Page object for epam.com homepage.

Locators discovered by inspecting the live site.
The page has a cookie consent banner that must be dismissed before interacting.
"""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class EpamPage(BasePage):
    URL = "https://www.epam.com"

    def __init__(self, page: Page) -> None:
        super().__init__(page, base_url=self.URL)

        # Cookie consent
        self.cookie_accept_btn = page.locator("#onetrust-accept-btn-handler")

        # Header
        self.logo = page.locator(".header__logo-dark")
        self.logo_link = page.locator(".header__logo-link")
        self.search_btn = page.locator(".header-search__button")

        # Main navigation links
        self.services_link = page.locator("a[href='/services']").first
        self.about_link = page.locator("a[href='/about']").first

        # Hero section — page renders desktop + mobile h1, take the first (desktop)
        self.hero_title = page.locator("h1").first

    def open(self) -> "EpamPage":
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self._accept_cookies()
        return self

    def _accept_cookies(self) -> None:
        if self.cookie_accept_btn.is_visible(timeout=5000):
            self.cookie_accept_btn.click()
            self.cookie_accept_btn.wait_for(state="hidden", timeout=5000)

    def get_hero_title(self) -> str:
        return self.hero_title.inner_text().strip()

    def click_services(self) -> "EpamPage":
        # dispatch_event bypasses the background <video> that intercepts pointer events
        self.services_link.dispatch_event("click")
        # Services page has continuous analytics requests — networkidle never fires
        self.page.wait_for_load_state("domcontentloaded")
        return self

    def click_search(self) -> "EpamPage":
        self.search_btn.click()
        return self
