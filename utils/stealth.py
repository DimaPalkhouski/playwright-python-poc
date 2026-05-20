"""Browser stealth helpers — removes signals that reveal Playwright automation.

Applied via conftest.py browser_context_args so every test benefits automatically.
"""
from __future__ import annotations


# Injected into every page before any script runs.
# Hides navigator.webdriver and common automation fingerprints.
STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
window.chrome = { runtime: {} };
"""

# Realistic browser args — strips Playwright's automation flags
STEALTH_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

# A real-looking user agent (Chrome on macOS)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
