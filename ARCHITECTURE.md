# Insurance UI Automation Framework — Architecture

## 1. Context

- **Domain:** Insurance quoting & state-level compliance validation
- **Scope:** UI-only automation (no API/DB direct calls)
- **Stack:** Python 3.11+, Playwright (sync), pytest
- **Phase:** POC — application access pending; rules engine and data layer are proven via unit tests; UI layer is ready to wire the moment real app access is granted
- **Test data strategy:** Programmatic generation, **pairwise / combinatorial** (via `allpairspy`)
- **Rules:** State-specific premium calculation & compliance rules — discovered incrementally, no upfront spec

---

## 2. Architectural Goals

| Goal | How it's addressed |
|---|---|
| Scale to thousands of test combinations | Pairwise generator + `@pytest.mark.parametrize` |
| Add new state rules without touching existing code | Strategy + Registry pattern in `rules/` |
| Keep UI mechanics decoupled from business logic | Thin POM + separate Rules Engine |
| Be productive before app access | Unit tests for rules/generators run without a browser |
| Maintainable by other QA engineers | Clean Code, single-responsibility layers, typed data models |
| Fast feedback loop | Unit tests for rules/generators (no browser) + tagged smoke E2E |

---

## 3. Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│  TEST LAYER  (pytest + parametrize)                     │
│  - Data-driven scenarios                                │
│  - Assertions only                                      │
└────────────┬────────────────────────────────────────────┘
             │ uses
             ▼
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER  (Flows / Service Objects)         │
│  - QuoteFlow.get_quote(QuoteInput) → ActualResult       │
│  - Composes multiple page objects into business actions │
└────────┬───────────────────────┬────────────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐   ┌──────────────────────────────────┐
│  POM LAYER       │   │  RULES ENGINE                    │
│  - Pages         │   │  - StateRule strategies          │
│  - Components    │   │  - Registry lookup               │
│  - UI only       │   │  - Pure Python, unit-testable    │
└──────────────────┘   └──────────────────────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  DATA LAYER                                             │
│  - QuoteInput / ExpectedResult dataclasses              │
│  - Generators (pairwise via allpairspy)                 │
│  - Builders for complex inputs                          │
│  - State rule definitions (YAML, hot-reloadable)        │
└─────────────────────────────────────────────────────────┘
```

### Layer responsibilities

**Test Layer** — Knows *what* to verify, not *how*. Pulls inputs from generators, calls flows, asserts via validators.

**Orchestration (Flows)** — Owns multi-page choreography (customer info → coverage → quote → result). Returns typed result objects. Tests never juggle multiple page objects themselves.

**POM Layer** — Single-screen UI mechanics only. Fluent methods, no assertions, no business logic. Components folder for reusable widgets (state dropdown, date picker, fee table).

**Rules Engine** — Pure Python. Given a `QuoteInput`, computes the *expected* premium and *expected* compliance result for the chosen state. Has zero awareness of Playwright.

**Data Layer** — Typed input/output models (`@dataclass(frozen=True)`), generators (pairwise combos), builders (fluent construction for tests), and static YAML rule data.

---

## 4. Project Structure

```
playwright-framework/
├── pages/
│   ├── base_page.py             # navigate(), wait_for_load(), screenshot()
│   ├── poc_quote_page.py        # single POC page covering full 11-step flow
│   │                            # rename / split per-screen when real app arrives
│   └── epam_page.py             # reference page object (epam.com smoke tests)
│
├── flows/                       # orchestration layer
│   └── quote_flow.py            # QuoteFlow.get_quote(QuoteInput) → ActualResult
│
├── rules/
│   ├── base_rule.py             # StateRule protocol: calculate_premium(), validate_compliance()
│   ├── state_rules/
│   │   ├── _stub.py             # fallback for unknown states
│   │   ├── california.py        # CA — credit banned, min liability rules
│   │   ├── texas.py             # TX — standard liability
│   │   ├── new_york.py          # NY — no-fault, PIP required, 2-claim max
│   │   └── florida.py           # FL — no-fault, PIP required
│   ├── rule_registry.py         # state code → strategy (default_registry singleton)
│   └── validators.py            # assert_quote_result() with rich diff output
│
├── data/
│   ├── models/
│   │   ├── quote_input.py       # QuoteInput frozen dataclass + enums
│   │   └── expected_result.py   # ExpectedResult, ActualResult, ComplianceRequirement
│   ├── generators/
│   │   ├── pairwise.py          # allpairspy wrapper
│   │   ├── quote_generator.py   # produces pairwise QuoteInput sets
│   │   └── builders.py          # QuoteInputBuilder fluent API
│   └── datasets/
│       ├── states.yaml          # state codes + known constraints
│       ├── golden_cases.yaml    # hand-picked must-pass scenarios
│       └── state_groups.yaml    # state groupings: tort / no-fault / standard
│
├── tests/
│   ├── test_quote_pairwise.py   # data-driven E2E (requires real app — skipped until access)
│   ├── test_compliance_rules.py # golden case E2E (requires real app — skipped until access)
│   ├── test_epam.py             # 8 smoke tests against epam.com (live reference suite)
│   └── unit/                    # pure-Python tests — no browser required ✅
│       ├── test_rules_engine.py # 14 tests: CA/TX/NY/FL rules + registry + stub
│       └── test_generator.py    # 9 tests: pairwise generator + builder API
│
├── utils/
│   ├── config.py                # Config class — all settings via .env
│   └── stealth.py               # anti-bot browser args, user-agent, init script
│
├── conftest.py                  # browser config, stealth, flow/page fixtures, failure screenshots
├── pytest.ini                   # test paths, HTML report, markers
├── requirements.txt
├── .env.example                 # env var template — never commit real secrets
├── ARCHITECTURE.md
└── BUSINESS_LOGIC.md
```

---

## 5. Design Patterns

| Pattern | Where | Why |
|---|---|---|
| **Page Object Model** | `pages/` | UI abstraction, single responsibility per screen |
| **Component Object** | `pages/components/` | Reusable widgets shared across pages |
| **Service / Flow Object** | `flows/` | Multi-page business journeys as one call |
| **Strategy** | `rules/state_rules/` | Per-state rule implementations, swap without conditionals |
| **Registry** | `rules/rule_registry.py` | Decouple state selection from rule discovery |
| **Factory** | `data/generators/` | Produce diverse test data programmatically |
| **Builder** | `data/generators/builders.py` | Fluent construction of complex `QuoteInput` instances |
| **Data-Driven Testing** | `@pytest.mark.parametrize` | Scale tests without duplicating code |
| **Fluent Interface** | Page objects & builders | Readable chains: `page.select_state("CA").enter_age(35).submit()` |

---

## 6. Data Strategy

### Pairwise generation (`allpairspy`)
Exhaustive combinations explode quickly:
- 5 dimensions × 4 values each = 1,024 cases
- Pairwise covers all 2-way interactions in ~20 cases

```python
parameters = {
    "state":        ["CA", "TX", "NY", "FL"],
    "age_band":     ["18-25", "26-40", "41-65", "65+"],
    "coverage":     ["basic", "standard", "premium"],
    "vehicle_type": ["sedan", "suv", "truck"],
    "credit_tier":  ["good", "fair", "poor"],
}
```

### Two complementary data sources
1. **Generated combinations** — broad coverage, regenerated each run
2. **Golden cases** (`golden_cases.yaml`) — hand-picked edge cases / regressions that *must* pass

### Typed data models
```python
@dataclass(frozen=True)
class QuoteInput:
    state: str
    age: int
    coverage_level: CoverageLevel
    vehicle_type: VehicleType
    credit_tier: CreditTier
    # ...
```
Immutability prevents accidental mutation across parametrized runs.

---

## 7. Rules Engine

### Contract
```python
class StateRule(Protocol):
    def calculate_premium(self, q: QuoteInput) -> Decimal: ...
    def validate_compliance(self, q: QuoteInput) -> list[ComplianceViolation]: ...
```

### Registry
```python
registry.register("CA", CaliforniaRule())
rule = registry.get(quote_input.state)
expected = rule.calculate_premium(quote_input)
```

### Rules as data (where viable)
Simple multipliers and minimums live in YAML so non-engineers can maintain them:
```yaml
CA:
  min_liability: 15000
  uninsured_motorist_required: true
  base_rate_multiplier: 1.15
```
Complex branching logic still lives in Python strategies.

### Validator
Compares `expected` vs `actual` UI-scraped result. On failure, emits a rich diff: input combo, state, rule applied, expected vs actual, with a stable test ID so pairwise rows are reproducible.

---

## 8. End-to-End Flow

```
Generator produces QuoteInput
    └─► Test parametrize picks it up
          └─► Flow.get_quote(input) drives Pages
                ├─► Pages fill the form, submit
                └─► Flow reads result → ActualResult
          └─► RulesEngine.expected(input) → ExpectedResult
          └─► Validator.compare(expected, actual) → assert
```

---

## 9. POC Plan — Real-App-Ready

The mock server has been removed. The architecture is proven via unit tests.
E2E tests are scaffolded and ready; they will go green the moment real app locators are wired.

| Phase | Deliverable | Status |
|---|---|---|
| 1 | Data models + pairwise generator + state rules + validator | ✅ Done (23 unit tests passing) |
| 2 | Page objects (`poc_quote_page.py`) + `QuoteFlow` scaffold | ✅ Done (locators are TODOs) |
| 3 | Wire real locators when app access is granted | ⏳ Waiting on VPN + credentials |
| 4 | Full E2E pairwise suite green on real app | ⏳ After phase 3 |

**When real app arrives:**
1. Update `Config.BASE_URL` to `https://devpas.corp.tmnas.com/index.xhtml`
2. Replace `TODO` locators in `poc_quote_page.py` with real selectors (prefer `get_by_label()` for JSF)
3. Rename / split `poc_quote_page.py` into per-screen page objects (see `BUSINESS_LOGIC.md` page mapping)
4. Run `pytest -m smoke` — all rules engine and generator logic unchanged

---

## 10. Test Tiers

| Tier | Location | Purpose | Speed |
|---|---|---|---|
| Unit | `tests/unit/` | Rules engine, generators, validators | Milliseconds |
| Smoke (E2E) | tagged `@pytest.mark.smoke` | Critical path, runs on every PR | ~1 min |
| Pairwise regression | tagged `@pytest.mark.regression` | Full combinatorial coverage, nightly | Many minutes |
| Compliance | tagged `@pytest.mark.compliance` | State-specific rule validation | Variable |

---

## 11. Clean Code Principles Applied

- **Single Responsibility** — each layer does one thing
- **Open/Closed** — adding a state = new rule file, no edits to existing rules
- **Dependency Inversion** — tests depend on `StateRule` abstraction, not concrete states
- **DRY** — components, builders, flows eliminate duplication
- **Explicit > Implicit** — typed dataclasses, named enums, no magic strings for states/coverage levels
- **Fail Loud** — validator surfaces full context on assertion failure
- **No business logic in POM** — pages are dumb actuators; tests and rules own meaning

---

## 12. Tooling — `requirements.txt`

```
playwright==1.44.0
pytest==8.2.1
pytest-playwright==0.5.0
pytest-html==4.1.1
python-dotenv==1.0.1
allpairspy==2.5.0       # pairwise test data generation
pyyaml==6.0.1           # rule & dataset definitions
faker==25.2.0           # realistic synthetic customer data
flask==3.0.3            # (retained; used for ad-hoc local stubs if needed)
```

---

## 13. Test Status

| Suite | Command | Status |
|---|---|---|
| Unit (rules + generators) | `pytest -m unit` | ✅ 23/23 passing |
| epam.com smoke (reference) | `pytest tests/test_epam.py` | ✅ 8/8 passing |
| E2E pairwise | `pytest -m regression` | ⏳ Skipped — requires real app |
| E2E compliance / golden | `pytest -m compliance` | ⏳ Skipped — requires real app |

---

## 14. Open Questions / Future Work

- Reporting: Allure vs `pytest-html` for richer per-case visibility on large pairwise runs
- Parallelization: `pytest-xdist` once suite grows past ~50 E2E cases
- BDD hybrid: `pytest-bdd` for 5 high-level Gherkin scenarios + `@pytest.mark.parametrize` for pairwise data rows
- `TortOption` enum: add to `QuoteInput` and update PA rule (`rules/state_rules/pennsylvania.py` — to create)
- State rule inheritance: refactor to `TortStateRule` / `NoFaultStateRule` / `StandardStateRule` base classes reading from `state_groups.yaml`
- Visual regression: out of POC scope, but hook in `BasePage.screenshot()` leaves the door open
- API-level shortcuts for authentication once real app is available (skip login UI per test)
