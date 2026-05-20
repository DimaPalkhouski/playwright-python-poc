# Copilot Instructions — Insurance UI Automation Framework

## Domain Context
This is an insurance quoting and compliance automation framework.
- Users enter customer/coverage inputs → UI computes a premium
- Different US states have different rules and compliance requirements
- We validate: (1) premium correctness, (2) eligibility, (3) compliance requirements displayed

## POC Status — Key Rule
**We do not yet have access to the real application.**
All E2E tests run against a local mock (`mocks/server.py` + `mocks/insurance_app.html`).
When real app access arrives: **update locators in `pages/poc_quote_page.py` only.**
Everything else — flows, rules engine, generators, validators — stays untouched.

## Project Structure
```
playwright-framework/
├── pages/
│   ├── base_page.py          # Shared navigation, screenshot, wait helpers
│   └── poc_quote_page.py     # Single POC page covering full quote flow (locators here)
├── flows/
│   └── quote_flow.py         # Orchestrates poc_quote_page into business actions
├── rules/
│   ├── base_rule.py          # Abstract StateRule protocol
│   ├── rule_registry.py      # Maps state code → strategy
│   ├── validators.py         # Compares expected vs actual with rich diffs
│   └── state_rules/          # One file per state: california.py, texas.py, etc.
├── data/
│   ├── models/               # QuoteInput, ExpectedResult, ActualResult dataclasses
│   ├── generators/           # pairwise.py, quote_generator.py, builders.py
│   └── datasets/             # states.yaml (rules), golden_cases.yaml (must-pass cases)
├── mocks/
│   ├── server.py             # Flask mock server (started by conftest session fixture)
│   └── insurance_app.html    # Mock UI template
├── tests/
│   ├── unit/                 # Pure Python tests — no browser
│   ├── test_quote_pairwise.py
│   └── test_compliance_rules.py
├── utils/config.py
├── conftest.py
└── pytest.ini
```

## Architecture Layers (never mix responsibilities)
1. **Test layer** — data + assertions only. Never instantiate page objects directly in tests.
2. **Flow layer** (`flows/`) — multi-step journeys. Tests call flows, not pages.
3. **POM layer** (`pages/`) — UI mechanics only. No assertions, no business logic.
4. **Rules engine** (`rules/`) — pure Python expected value computation. No Playwright.
5. **Data layer** (`data/`) — typed models, generators, YAML datasets.

## POM Conventions (POC phase)
- All locators live in `pages/poc_quote_page.py` `__init__` — never inline in methods
- Methods return `self` (fluent): `page.select_state("CA").enter_age(35).submit_customer_info()`
- No assertions inside page objects
- Prefer `#id` > `[data-testid]` > role > label > CSS class > XPath

## Test Conventions
- Class name: `Test<Feature>` (e.g., `TestQuotePairwise`, `TestStateCompliance`)
- Method name reads as sentence: `test_ny_ineligible_with_three_prior_claims`
- Use `expect(locator)` for UI assertions, plain `assert` for Python values
- Markers: `@pytest.mark.smoke` | `regression` | `compliance` | `unit`
- Parametrize with stable IDs: `pytest.param(inp, id=str(inp))`

## Data & Rules Conventions
- `QuoteInput` is `frozen=True` — never mutate between test cases
- New test scenario → use `QuoteInputBuilder` fluent API
- New state → create `rules/state_rules/<state>.py`, register in `rule_registry.py`
- New golden case → add entry to `data/datasets/golden_cases.yaml`

## Configuration
- All env vars in `utils/config.py` + documented in `.env.example`
- Never hard-code URLs, ports, credentials
- `Config.BASE_URL` points to mock during POC, real app URL after access

## Running Tests
```bash
pytest -m unit          # rules engine + generators, no browser
pytest -m smoke         # golden cases E2E
pytest -m regression    # full pairwise suite
pytest -m compliance    # state compliance checks
HEADLESS=false SLOW_MO=500 pytest   # headed with slow motion
```
