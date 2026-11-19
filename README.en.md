# Credit Card Recommender — E2E, API & i18n Automated Test Suite

[繁體中文](README.md) | **English**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium%2FChrome-2EAD33?logo=playwright&logoColor=white)
![openpyxl](https://img.shields.io/badge/Reports-Excel%20%2B%20HTML%20%2B%20MD-217346?logo=microsoftexcel&logoColor=white)

## Purpose

This repository provides a Page-Object-Model (POM) automated test suite and modular reporting framework for the **Taiwan Credit Card Reward Comparison & Channel Recommendation System** ([`cards.zillurl.com`](https://cards.zillurl.com/), source app: [`huangyj915/credit_card_recommend`](https://github.com/huangyj915/credit_card_recommend)).

It continuously validates:
- REST API contracts, recommendation calculation accuracy (independent math oracle + golden business invariants), and card-rule data sanity.
- Playwright E2E user workflows, negative fault-tolerance scenarios (`page.route()` mocks), and desktop/mobile responsive layouts.
- Bilingual localization & i18n (`zh-Hant` / `en`) across both frontend UI and backend APIs.
- Live issuing-bank website URL liveness and reward-rate parity.

---

## Test Scope (46 Test Cases: 15 `P0`, 28 `P1`, 3 `P2`)

| Module | Cases | Coverage |
|---|---:|---|
| [`tests/test_api.py`](tests/test_api.py) | 11 | FastAPI endpoint contracts (`/api/config`, `/api/channels`, `/api/cards`, `/api/banks`, `/api/scrapers`, `/api/scrape-logs`), `/api/recommend` ranking & edge cases, admin lock protection, and `?lang=en` API parity |
| [`tests/test_functional_ui.py`](tests/test_functional_ui.py) | 13 | Scenario presets, 7-digit spend input cap & non-numeric sanitization, clear/reset, manual calculation, `only_no_min_spend` filter, comparison matrix, cascading bank/card dropdowns, truncated note `more` source links, and desktop (`1440x900`) / mobile (`390x844`) responsive overflow checks |
| [`tests/test_negative_e2e.py`](tests/test_negative_e2e.py) | 3 | `page.route()` negative & mocked E2E tests: `/api/recommend` HTTP 500 recovery, `public_readonly` UI locking, and scraper closed-loop UI refresh |
| [`tests/test_i18n.py`](tests/test_i18n.py) | 7 | `zh-Hant` UTF-8 & text integrity, `NT$` & `Asia/Taipei` formatting, multi-locale browser resilience (`zh-TW`, `en-US`, `ja-JP`), `繁中 / EN` toggle, `localStorage` persistence, `/?lang=en` deep link, residual-CJK & placeholder-leak checks |
| [`tests/test_recommendation_correctness.py`](tests/test_recommendation_correctness.py) | 6 | Independent rule-by-rule math oracle, multi-card `combo` optimality, cap-overflow & min-spend boundaries, UI-to-API value parity, non-mirror golden business invariants, and scraper-artifact data sanity checks |
| [`tests/test_official_rate_sync.py`](tests/test_official_rate_sync.py) | 2 | UI matrix vs `/api/cards` parity and allowlist-validated live Playwright cross-checks of each card's `official_url` liveness and main-content reward rates |
| [`tests/test_security.py`](tests/test_security.py) | 4 | Write-endpoint auth locks, `/api/scrape-logs` limit bounds, Excel formula injection & secret redaction unit tests, and HTTPS bank domain allowlist SSRF checks |

### Architecture, Failure Evidence & CI/CD
- **Page Object Model ([`pages/home_page.py`](pages/home_page.py))**: Encapsulates locators and flows (`HomePage`, `MatrixTab`, `ScraperTab`) with web-first assertions and condition-based waits (no hard sleeps or deprecated APIs).
- **Failure Artifacts ([`conftest.py`](conftest.py))**: Automatically captures Playwright **Trace (`*-trace.zip`)** and **full-page screenshots (`.png`)** under `reports/artifacts/` only when a test fails, with `--disable-dev-shm-usage` for Linux CI containers.
- **Modular Reporting ([`reporting/`](reporting/))**: Generates `latest.xlsx` (live Excel `Fail Rate` formulas `errors / total` + deduplicated dev `Issues`), `latest.md` (published to GitHub Actions Step Summary), `index.html` (deployed to `gh-pages` for GitHub Pages), `junit.xml`, and cumulative `test-history-summary.xlsx`.
- **GitHub Actions ([`.github/workflows/test.yml`](.github/workflows/test.yml))**: Uses isolated virtualenvs to boot `credit_card_recommend` locally inside the runner, runs core regression on `push`/`pull_request`, schedules daily `official_sync` monitoring (`cron`), restores/persists history via `gh-pages`, and uploads all reports & failure traces as Artifacts.

---

## How to Run

### 1. Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If Google Chrome is not installed locally, run `playwright install chromium` to install Playwright's Chromium binary.

### 2. Execute Tests

```bash
# Run all 42 tests against the default target (https://cards.zillurl.com)
pytest

# Run against a local dev/staging server and enforce English i18n checks
pytest --base-url http://127.0.0.1:8000 --require-en

# Filter by marker
pytest -m api
pytest -m functional
pytest -m negative
pytest -m i18n
pytest -m math
pytest -m official_sync

# Run with visible browser or skip report generation
pytest --headed --no-report
```
