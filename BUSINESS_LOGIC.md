# Insurance Application — Business Logic & Test Context

> **Status:** POC — app access pending. Mock server removed; framework is proven via 23 unit tests.
> This document captures what is known from test case spreadsheets and app screenshots.
> Sections marked 🔲 are to be filled in once real app access is granted.

---

## 1. Application Overview

| Property | Value |
|---|---|
| **App name** | RapidSure Policy Portal |
| **Client** | Philadelphia Insurance Companies (PHLY) |
| **System** | PHLY Policy Management (PAS) |
| **Dev URL** | `https://devpas.corp.tmnas.com/index.xhtml` |
| **Tech stack** | JSF / `.xhtml` (Java Server Faces) |
| **Primary state** | Pennsylvania (PA) |
| **Policy type** | Personal Auto (PA) |

---

## 2. Application Navigation

### Left sidebar — always visible
```
Initiate
├── Account Search
├── Policy Search
├── Activity
├── Workflow
├── Agency Reporting
└── New Account

My PAS
└── Language
```

### Top navigation
```
Underwriting ▾ | EAS ▾ | Admin ▾
```

---

## 3. Core Policy Flow

Every test case follows the **same sequence of steps** from start to finish.
What differs between test cases is the **input data** and **what is validated** at the end.

```
Step 1  →  Access the system (login)
Step 2  →  Create Account (customer details)
Step 3  →  Add Contact to the Account
Step 4  →  Create Policy + answer Policy Questions
Step 5  →  Coverage screen: add Liability + Physical Damage coverages
Step 6  →  Add Garage (garage details)
Step 7  →  Add Vehicles (×2) + answer Vehicle Questions
Step 8  →  Add Driver (Policy Info page)
Step 9  →  Rate the Policy
Step 10 →  Quote and Bind
Step 11 →  Issue Policy → verify premiums + documents generated
```

### Page mapping
| Step | Screen | Page Object (to create) |
|---|---|---|
| 1 | Login | `pages/login_page.py` |
| 2 | Account Information | `pages/account_page.py` |
| 3 | Contact | `pages/contact_page.py` |
| 4 | Policy + Questions | `pages/policy_page.py` |
| 5 | Coverage | `pages/coverage_page.py` |
| 6 | Garage | `pages/garage_page.py` |
| 7 | Vehicle + Questions | `pages/vehicle_page.py` |
| 8 | Driver / Policy Info | `pages/driver_page.py` |
| 9–10 | Rating / Summary | `pages/rating_page.py` |
| 11 | Bind + Issue | `pages/bind_issue_page.py` |

---

## 4. Test Cases

All test cases live in the spreadsheet: `Regression steps - PA.xlsx`
Tabs: `SV PA regression - NBS` | `SV PA regression - Cancellation`

### 4.1 SV PA policy - ISSUE
**Purpose:** Baseline end-to-end — create, rate, bind, and issue a standard PA auto policy.
**Unique step:** None — this is the happy path.
**Validates:** Policy is issued, premiums generated, documents produced.

### 4.2 SV PA Tort - Limited
**Purpose:** Verify Limited Tort option is selectable and affects the premium correctly.
**Unique step:** Step 8 — Select **Limited Tort** coverage, update coverage limit, save.
**Validates:** Limited tort premium is lower than full tort; policy issues successfully.

### 4.3 SV PA Tort - Full
**Purpose:** Verify Full Tort option is selectable and affects the premium correctly.
**Unique step:** Step 8 — Select **Full Tort** coverage, update coverage limit, save.
**Validates:** Full tort premium is higher than limited tort; policy issues successfully.

### 4.4 SV Validate rate factors - NBS
**Purpose:** Validate that the system calculates rate factors correctly for New Business (NBS).
**Unique step:** Step 10 — Check **rate factors in summary page** and verify **BTMP is calculated** per the rule set.
**Validates:** Each rate factor matches the master rate book; BTMP = product of all factors × base rate.

### 4.5 SV Validate rate factors - cancellations Flat rate
**Purpose:** Validate premium calculation when a policy is cancelled using flat rate method.
**Unique step:** Cancellation scenario with flat rate applied.
**Validates:** 🔲 Cancellation premium = flat rate amount (formula TBD on app access).

---

## 5. Pennsylvania-Specific Rules

Pennsylvania is a **"choice no-fault" state** — unique among US states in that the insured
must choose a tort option when purchasing a policy. This directly affects premium calculation.

### 5.1 Tort Options

| Tort Option | Description | Premium Impact |
|---|---|---|
| **Limited Tort** | Insured gives up the right to sue for pain & suffering (except in serious injury cases) | **Lower** premium |
| **Full Tort** | Insured retains unrestricted right to sue | **Higher** premium (~15–20% surcharge — 🔲 confirm exact multiplier) |

> **Why this matters for automation:** Tort selection is a mandatory PA policy field.
> Tests for Limited vs Full Tort are separate test cases because they produce
> different expected premiums. The rules engine must account for tort option in
> its PA premium calculation.

### 5.2 Minimum Coverage Requirements (PA)
| Coverage | Minimum |
|---|---|
| Bodily Injury Liability | $15,000 per person / $30,000 per accident |
| Property Damage Liability | $5,000 |
| First Party Benefits (Medical) | $5,000 |
| Uninsured Motorist | Optional (but offered) |

### 5.3 Coverages in scope
- **Liability** — required
- **Physical Damage** — added in Step 5
- **Tort** — selected in Step 8 (Limited or Full)
- 🔲 Additional coverages — to be confirmed on app access

---

## 6. Premium Calculation — BTMP

**BTMP = Base Term Monthly Premium**

This is the final monthly premium the system displays after rating.
It is the result of multiplying a base rate by a chain of rating factors:

```
Base Rate
  × Coverage level factor
  × Vehicle type factor
  × Driver age factor        (young / standard / senior)
  × Credit tier factor       🔲 confirm if used in PA
  × Tort option factor       (Limited < Full)
  × Prior claims surcharge
  × Deductible discount
  = BTMP
```

> 🔲 **Exact multiplier values are unknown** — they will be reverse-engineered
> from the rate factors screen once app access is granted. The rules engine
> (`rules/state_rules/pennsylvania.py`) will be updated with real values.

### Rate factors screen (Step 10)
- Summary page shows each factor individually
- Our test validates: each factor shown in UI matches the expected value from our rules engine
- BTMP shown in UI must equal our computed BTMP within rounding tolerance (±$0.05)

---

## 7. Cancellation Logic

### 🔲 Flat Rate Cancellation
- Used in test case 4.5
- Formula: TBD on app access
- Expected behavior: system applies flat rate regardless of time on risk

### 🔲 Pro-Rata Cancellation
- Not in current test scope but likely exists in the app
- Formula: premium refund proportional to unused policy period

---

## 8. Account Information Screen

From the app screenshot, the Account Information page contains:

| Field | Required | Notes |
|---|---|---|
| Account Number | — | Auto-generated on save (e.g. `85348046`) |
| Account Name | ✱ | Policyholder name |
| Account Name (cont.) | — | Continuation |
| Address Line 1 | ✱ | Street address |
| Address Line 2 | — | |
| City | ✱ | |
| State | ✱ | Dropdown — default: Pennsylvania |
| Zip Code | — | |
| Phone Number | — | |
| Email Address | — | |
| Alternate Billing Address | — | Checkbox |

**After save:** Success banner: `"Account saved successfully. new account number is XXXXXXXX"`
**Next action:** Link — `"Use account XXXXXXXX to create new policy"`
**Contact section:** `"Account has no contacts. Create new contact"` link

---

## 9. Open Questions (resolve on app access)

| # | Question | Where to look |
|---|---|---|
| 1 | What are the exact tort option multipliers for PA? | Rate factors summary screen |
| 2 | Are JSF element IDs stable or auto-generated (`j_idt123`)? | Browser DevTools on each page |
| 3 | What does the Coverage screen look like? What fields? | Step 5 in manual walkthrough |
| 4 | What vehicle questions are asked? | Step 7 in manual walkthrough |
| 5 | What policy questions are asked? | Step 4 in manual walkthrough |
| 6 | What does the rate factors summary page display? | Step 10 in manual walkthrough |
| 7 | What is the flat rate cancellation formula? | Step 10 in cancellation test |
| 8 | Is credit tier a rating factor in this system? | Rate factors screen |
| 9 | NBS = New Business? Any differences vs renewal flow? | Confirm with team |
| 10 | Are there login credentials / test users available? | Confirm with team |

---

---

## 10. State Grouping

States share rule **logic** within groups — only rate values differ between states in the same group.
Full detail in `data/datasets/state_groups.yaml`.

| Group | Base class (planned) | Key rule | States |
|---|---|---|---|
| **Tort choice** | `TortStateRule` | Tort option required (Limited/Full) | PA, NJ, KY, MT |
| **No-fault** | `NoFaultStateRule` | PIP mandatory, no tort field | NY, FL, MI, HI, MA, MN, UT, KS, ND |
| **Standard** | `StandardStateRule` | Liability only, simplest logic | TX, CA, IL, OH, GA… |

**Cross-cutting flag — `credit_banned: true`**
States where credit score is **legally banned** as a rating factor: `CA, MA, HI`
These inherit their group logic but always apply `credit_multiplier = 1.00`.

> Adding a new state = pick a group, add rate values to `state_groups.yaml`, register in `rule_registry.py`.


### What varies between test runs (pairwise dimensions)
```python
parameters = {
    "tort_option":    ["limited", "full"],
    "coverage_level": ["basic", "standard", "premium"],
    "vehicle_count":  [1, 2],
    "driver_age":     ["young (16-25)", "standard (26-65)", "senior (65+)"],
    "prior_claims":   [0, 1, 2],
    # 🔲 add more dimensions as discovered on app access
}
```

### Golden cases (always run)
Defined in `data/datasets/golden_cases.yaml`:
- Baseline PA full tort issue
- PA limited tort — verify lower premium
- PA full tort — verify higher premium
- PA rate factors NBS validation
- 🔲 Cancellation flat rate case (add when logic is confirmed)

---

## 11. Glossary

| Term | Meaning |
|---|---|
| **BTMP** | Base Term Monthly Premium — final computed monthly premium |
| **NBS** | New Business — a fresh policy (vs renewal) |
| **PAS** | Policy Administration System |
| **PHLY** | Philadelphia Insurance Companies |
| **Tort** | Legal right to sue for damages (Limited or Full in PA) |
| **Rate factors** | Individual multipliers applied to base rate to compute BTMP |
| **SV** | Scenario Verification (test case prefix) |
| **PA** | Pennsylvania |
| **Issue** | Finalizing and activating the policy |
| **Bind** | Committing the quoted premium — policy becomes active |
| **Quote** | Calculating the premium before binding |
