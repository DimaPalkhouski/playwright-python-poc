import pytest
import time
from playwright.sync_api import Page, Browser
from flows.quote_flow import QuoteFlow
from pages.epam_page import EpamPage
from utils.config import Config
from utils.stealth import STEALTH_INIT_SCRIPT, STEALTH_LAUNCH_ARGS, USER_AGENT


# ── Browser configuration ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {
        **browser_type_launch_args,
        "slow_mo": Config.SLOW_MO,
        "args": STEALTH_LAUNCH_ARGS,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "base_url": Config.BASE_URL,
        "user_agent": USER_AGENT,
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-US",
    }


# ── Stealth init script (applied to every page) ───────────────────────────────

@pytest.fixture(autouse=True)
def apply_stealth(page: Page) -> None:
    page.add_init_script(STEALTH_INIT_SCRIPT)


# ── Page / flow fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def quote_flow(page: Page) -> QuoteFlow:
    return QuoteFlow(page, Config.BASE_URL)


@pytest.fixture
def epam_page(page: Page) -> EpamPage:
    """Fresh page per test — use for tests that need a clean state."""
    return EpamPage(page)


@pytest.fixture(scope="module")
def epam_page_loaded(browser: Browser) -> EpamPage:
    """Single page opened once per test module — avoids rate limits on live sites.

    All tests in a module share this page; no re-navigation between tests.
    """
    ctx = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1440, "height": 900},
        locale="en-US",
    )
    page = ctx.new_page()
    page.add_init_script(STEALTH_INIT_SCRIPT)
    epam = EpamPage(page)
    epam.open()
    yield epam
    ctx.close()


# ── Failure artifacts ─────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page: Page = item.funcargs.get("page")
        if page:
            screenshot_name = f"reports/FAILED_{item.name}.png"
            page.screenshot(path=screenshot_name, full_page=True)
