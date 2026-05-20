import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Application ─────────────────────────────────────────────────────────
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:5000")
    TEST_USERNAME: str = os.getenv("TEST_USERNAME", "")
    TEST_PASSWORD: str = os.getenv("TEST_PASSWORD", "")

    # ── Browser ─────────────────────────────────────────────────────────────
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # ── Mock server ──────────────────────────────────────────────────────────
    MOCK_SERVER_PORT: int = int(os.getenv("MOCK_SERVER_PORT", "5000"))
    MOCK_SERVER_HOST: str = os.getenv("MOCK_SERVER_HOST", "localhost")

    # ── Test data ────────────────────────────────────────────────────────────
    # States to include in combinatorial generation. Comma-separated.
    ACTIVE_STATES: list[str] = os.getenv("ACTIVE_STATES", "CA,TX,NY,FL").split(",")
