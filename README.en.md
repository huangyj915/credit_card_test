# Credit Card Recommender — E2E, API & i18n Automated Test Suite

[繁體中文](README.md) | **English**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium%2FChrome-2EAD33?logo=playwright&logoColor=white)
![openpyxl](https://img.shields.io/badge/Reports-Excel%20%2B%20Markdown-217346?logo=microsoftexcel&logoColor=white)

## Purpose

This repository provides a comprehensive automated test suite and executive reporting framework for the **Taiwan Credit Card Reward Comparison & Channel Recommendation System** ([`cards.zillurl.com`](https://cards.zillurl.com/), source app: [`huangyj915/credit_card_recommend`](https://github.com/huangyj915/credit_card_recommend)).

It is designed to continuously verify:
- Functional correctness of all API contracts and Playwright E2E user workflows.
- Mathematical accuracy of reward calculations, monthly cap overflow rules, and multi-card combo optimization.
- Bilingual localization & i18n (`zh-Hant` / `en`) across both frontend UI and backend APIs.
- Data accuracy against live issuing-bank websites, generating actionable Excel and Markdown test reports with automated root-cause classification and per-issue fail rates.

---

## Test Scope (38 Test Cases: 13 `P0`, 22 `P1`, 3 `P2`)

| Module | Cases | Coverage |
|---|---:|---|
| [`tests/test_api.py`](tests/test_api.py) | 11 | FastAPI endpoint contracts (`/api/config`, `/api/channels`, `/api/cards`, `/api/banks`, `/api/scrapers`, `/api/scrape-logs`), `/api/recommend` ranking & edge cases, admin lock protection, and `?lang=en` API parity |
| [`tests/test_functional_ui.py`](tests/test_functional_ui.py) | 13 | Default & scenario presets, 7-digit spend input cap & non-numeric sanitization, clear/reset, manual calculation, `only_no_min_spend` filter, comparison matrix, cascading bank/card dropdowns, truncated note `more` source links, and desktop (`1440x900`) / mobile (`390x844`) responsive overflow checks |
| [`tests/test_i18n.py`](tests/test_i18n.py) | 7 | `zh-Hant` UTF-8 & text integrity, `NT$` & `Asia/Taipei` formatting, multi-locale browser resilience (`zh-TW`, `en-US`, `ja-JP`), `繁中 / EN` toggle, `localStorage` persistence, `/?lang=en` deep link, residual-CJK & placeholder-leak checks |
| [`tests/test_recommendation_correctness.py`](tests/test_recommendation_correctness.py) | 5 | Independent rule-by-rule math oracle verifying `applied_rate`, cap-overflow fallback to base rate, `effective_rate_pct`, multi-card `combo` optimality, UI-to-API value parity, and card-rule data sanity checks |
| [`tests/test_official_rate_sync.py`](tests/test_official_rate_sync.py) | 2 | UI matrix vs `/api/cards` parity and live Playwright cross-checks of each card's `official_url` liveness and displayed reward rates against issuing-bank websites |

### Automated Reporting & CI/CD
- **Excel & Markdown Reports ([`reporting.py`](reporting.py))**: Every `pytest` run locally generates `reports/test-report-YYYYMMDD-HHMMSS.xlsx`, `reports/latest.xlsx`, `reports/latest.md`, and updates `reports/test-history-summary.xlsx` (`reports/` is gitignored and kept local; CI reports are uploaded as GitHub Actions Artifacts).
  - Workbooks include `Summary` (KPI metrics, `P0`/`P1`/`P2` breakdown, open dev issues), `Issues` (deduplicated action items with live Excel `Fail Rate` formulas `errors / total`, root cause, and fix guidance), and `Test Cases`.
- **GitHub Actions ([`.github/workflows/test.yml`](.github/workflows/test.yml))**: Boots `credit_card_recommend` locally inside the CI runner (`127.0.0.1:8000`) to avoid Cloudflare bot-protection `403` blocks on cloud IPs, runs the core CI suite on `push`/`pull_request` (and full 38-case suite on `workflow_dispatch`), and uploads `.xlsx`/`.md` artifacts.

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
# Run all 38 tests against the default target (https://cards.zillurl.com)
pytest

# Run against a local dev/staging server and enforce English i18n checks
pytest --base-url http://127.0.0.1:8000 --require-en

# Filter by marker
pytest -m api
pytest -m functional
pytest -m i18n
pytest -m math
pytest -m official_sync

# Run with visible browser or skip report generation
pytest --headed --no-report
```

---

## Latest Verification Snapshot

- **Latest Full Run (`2026-11-19 23:27:17` against `http://127.0.0.1:8000 --require-en`)**: **38 collected — 37 passed, 1 skipped (`ADMIN_TOKEN` not set locally), 0 failed (100% pass rate across all 37 executed cases, 0 open issues)**.
- Previously caught and verified fixed: mobile `390x844` horizontal overflow (22px–43px), untranslated card names/notes & SQLite `scrape_logs` under `?lang=en`, scraper-parsed abnormal caps/rates, and 2 dead bank URLs + 3 outdated card rates against live bank pages.
