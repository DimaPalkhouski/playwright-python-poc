# Skill: Implement Insurance Test Steps
<!-- applyTo: "tests/**,pages/**,flows/**,rules/**,data/**" -->

Use this skill when asked to:
- Add a new test scenario or test case
- Add a new state rule
- Add a new locator when real app access is received
- Extend the pairwise parameter space
- Add a golden case

---

## Step 1 — Identify what kind of task it is

| Request | What to touch |
|---|---|
| New test scenario (known input → known outcome) | `data/datasets/golden_cases.yaml` + nothing else |
| New data combination to cover | `data/generators/quote_generator.py` `_PARAMETERS` dict |
| New state rule | `rules/state_rules/<state>.py` + `rules/rule_registry.py` |
| New locator (real app arrived) | `pages/poc_quote_page.py` `__init__` only |
| New form field on the app | `pages/poc_quote_page.py` + `data/models/quote_input.py` + `flows/quote_flow.py` |
| New compliance check | `rules/state_rules/<state>.py` `compliance_requirements()` + golden case in YAML |

---

## Step 2 — Adding a golden test case (most common task)

Edit `data/datasets/golden_cases.yaml`. Follow this exact structure:

```yaml
- id: <state>_<short_description>          # snake_case, unique, no spaces
  description: "One sentence explaining what this case proves"
  input:
    state: CA                              # 2-letter code, must be in rule_registry
    age: 35
    coverage_level: standard              # basic | standard | premium
    vehicle_type: sedan                   # sedan | suv | truck | motorcycle
    credit_tier: good                     # excellent | good | fair | poor
    marital_status: single                # single | married | divorced
    prior_claims: 0
    deductible: 500                       # 250 | 500 | 1000
  expected_eligible: true                 # true | false
```

The test in `tests/test_compliance_rules.py::TestGoldenCases` picks it up automatically — no Python changes needed.

---

## Step 3 — Adding a new state rule

### 3a. Create the rule file
```
rules/state_rules/<statename>.py
```

Follow this template exactly:

```python
from __future__ import annotations
from decimal import Decimal
from data.models.expected_result import ComplianceRequirement
from data.models.quote_input import CoverageLevel, CreditTier, QuoteInput, VehicleType
from rules.base_rule import StateRule

_COVERAGE_BASE: dict[CoverageLevel, Decimal] = {
    CoverageLevel.BASIC:    Decimal("XX.00"),
    CoverageLevel.STANDARD: Decimal("XX.00"),
    CoverageLevel.PREMIUM:  Decimal("XX.00"),
}

_CREDIT_MULTIPLIER: dict[CreditTier, Decimal] = {
    CreditTier.EXCELLENT: Decimal("0.9X"),
    CreditTier.GOOD:      Decimal("1.00"),
    CreditTier.FAIR:      Decimal("1.1X"),
    CreditTier.POOR:      Decimal("1.3X"),
}

_MIN_ELIGIBLE_AGE = 16      # check state DMV rules
_MAX_CLAIMS = 3             # check state underwriting rules
_BASE_RATE_MULTIPLIER = Decimal("1.XX")

class <StateName>Rule(StateRule):

    def is_eligible(self, quote: QuoteInput) -> tuple[bool, str]:
        if quote.age < _MIN_ELIGIBLE_AGE:
            return False, f"Minimum eligible age in <XX> is {_MIN_ELIGIBLE_AGE}"
        if quote.prior_claims > _MAX_CLAIMS:
            return False, f"<XX> does not insure drivers with more than {_MAX_CLAIMS} prior claims"
        return True, ""

    def calculate_premium(self, quote: QuoteInput) -> Decimal:
        base   = _COVERAGE_BASE[quote.coverage_level]
        credit = _CREDIT_MULTIPLIER[quote.credit_tier]
        age_surcharge    = Decimal("1.20") if quote.age < 25 else Decimal("1.00")
        claims_surcharge = Decimal(str(1 + quote.prior_claims * 0.10))
        return (base * _BASE_RATE_MULTIPLIER * credit * age_surcharge * claims_surcharge
                ).quantize(Decimal("0.01"))

    def compliance_requirements(self, quote: QuoteInput) -> list[ComplianceRequirement]:
        return [
            ComplianceRequirement(
                name="Liability Coverage",
                required=True,
                description="Min $XX,000 bodily injury / $XX,000 property damage",
            ),
        ]
```

### 3b. Register it
In `rules/rule_registry.py`, add to `build_default_registry()`:
```python
from rules.state_rules.<statename> import <StateName>Rule
registry.register("XX", <StateName>Rule())
```

### 3c. Add to active states
In `utils/config.py`:
```python
ACTIVE_STATES: list[str] = os.getenv("ACTIVE_STATES", "CA,TX,NY,FL,XX").split(",")
```
And in `.env.example`:
```
ACTIVE_STATES=CA,TX,NY,FL,XX
```

### 3d. Add unit tests
In `tests/unit/test_rules_engine.py`, add a `Test<StateName>Rule` class following the existing `TestCaliforniaRule` pattern. Cover at minimum:
- eligible driver returns positive premium
- annual = monthly × 12
- ineligible when over max claims
- any state-specific compliance requirements

---

## Step 4 — Wiring real app locators (when app access arrives)

Open `pages/poc_quote_page.py`. In `__init__`, replace the mock IDs with real ones:

```python
# BEFORE (mock)
self.state_select = page.locator("#state")

# AFTER (real app — use whatever selector is most stable)
self.state_select = page.locator("#state-selector")           # prefer #id
self.state_select = page.locator("[data-testid='state']")     # or data-testid
self.state_select = page.get_by_label("State")                # or label
```

**Locator priority (always):**
1. `#id`
2. `[data-testid="..."]`
3. `page.get_by_role(...)` with `name=`
4. `page.get_by_label(...)`
5. CSS class — only if stable
6. XPath — last resort

After updating locators, run the smoke suite to verify wiring:
```bash
HEADLESS=false pytest -m smoke
```

---

## Step 5 — Adding a new QuoteInput field

When the real app has a field not yet in `QuoteInput`:

1. **Add to the model** (`data/models/quote_input.py`):
```python
@dataclass(frozen=True)
class QuoteInput:
    ...
    new_field: NewFieldType = DefaultValue
```

2. **Add to the builder** (`data/generators/builders.py`):
```python
def with_new_field(self, value: NewFieldType) -> "QuoteInputBuilder":
    self._new_field = value
    return self
```

3. **Add to the generator** (`data/generators/quote_generator.py`) if it should be part of pairwise combinations:
```python
_PARAMETERS: dict[str, list] = {
    ...
    "new_field": [value1, value2, value3],
}
```

4. **Wire in the flow** (`flows/quote_flow.py`) — add the fill step in `get_quote()`.

5. **Wire in the page** (`pages/poc_quote_page.py`) — add locator + action method.

6. **Update state rules** if the new field affects premium calculation.

---

## Quick reference — enum values

```python
# CoverageLevel
CoverageLevel.BASIC | STANDARD | PREMIUM

# VehicleType
VehicleType.SEDAN | SUV | TRUCK | MOTORCYCLE

# CreditTier
CreditTier.EXCELLENT | GOOD | FAIR | POOR

# MaritalStatus
MaritalStatus.SINGLE | MARRIED | DIVORCED
```

---

## Checklist before marking a task done

- [ ] Unit tests pass: `pytest -m unit`
- [ ] Smoke suite passes: `pytest -m smoke`
- [ ] No locators inlined in action methods
- [ ] No assertions inside page objects
- [ ] No hard-coded values — all from `Config` or `QuoteInput`
- [ ] New state rule registered in `rule_registry.py`
- [ ] New golden case added to `golden_cases.yaml` if applicable
