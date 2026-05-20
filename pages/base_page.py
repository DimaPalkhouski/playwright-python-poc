from playwright.sync_api import Page, Locator


class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> "BasePage":
        self.page.goto(f"{self.base_url}{path}")
        return self

    def get_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    def wait_for_load(self) -> None:
        self.page.wait_for_load_state("networkidle")

    def take_screenshot(self, name: str) -> None:
        self.page.screenshot(path=f"reports/{name}.png", full_page=True)
