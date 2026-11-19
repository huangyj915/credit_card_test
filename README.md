# Credit Card Recommender — E2E, API & i18n Automated Test Suite

**繁體中文** | [English](README.en.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium%2FChrome-2EAD33?logo=playwright&logoColor=white)
![openpyxl](https://img.shields.io/badge/Reports-Excel%20%2B%20HTML%20%2B%20MD-217346?logo=microsoftexcel&logoColor=white)

針對 [台灣信用卡回饋比較 & 通路推薦系統 (`cards.zillurl.com`)](https://cards.zillurl.com/)（原始專案：[huangyj915/credit_card_recommend](https://github.com/huangyj915/credit_card_recommend)）建置的端對端自動化測試框架，採 **Page Object Model (POM)** 與模組化報表架構，涵蓋 **REST API 契約、推薦演算法精算與黃金案例、銀行官網回饋率即時比對、負向異常 E2E (`page.route` Mock)、響應式排版與雙語 (`zh-TW` / `en`) i18n 驗證**。

---

## 核心特色 (Key Highlights)

- **分層測試架構（46 支用例：`P0` 15 支、`P1` 28 支、`P2` 3 支）**
  - **API 契約與基礎介面（11 項）**：驗證 `/api/config`、`/api/channels`、`/api/cards`、`/api/banks` 級聯查詢、`/api/recommend` 基本結構、邊界輸入、權限鎖定及 `?lang=en` 語系回傳。
  - **推薦演算法精算、黃金案例與資料品質（6 項）**：獨立實作規則重算 Oracle 逐卡核對上限溢額與方案取優、驗證多卡組合 (`combo`) 最佳分配、非鏡像黃金業務不變量（單調性與上下界）、前後端數值一致與爬蟲規則健檢。
  - **銀行官網回饋率即時比對（2 項）**：驗證前端比較表與 `/api/cards` 一致性，並先驗證 HTTPS 與台灣銀行官網白名單，再以 Playwright 開啟主內容區比對利率與連結存活度。
  - **E2E 功能與響應式版面（13 項）**：預設情境試算、7 位數輸入上限與非數字過濾、截斷條件說明 `more` 來源超連結、清空歸零、手動送出、無低消過濾、比較表與爬蟲級聯選單，以及桌機 (`1440x900`) / 手機 (`390x844`) 水平溢位檢查。
  - **負向異常與 Mock E2E（3 項）**：使用 Playwright `page.route()` 模擬 `/api/recommend` 500 容錯恢復、`public_readonly` 唯讀鎖定與 `POST /api/scrape` 爬蟲閉環刷新。
  - **安全回歸與報表防護（4 項）**：驗證全部寫入端點未授權攔截、`/api/scrape-logs` `limit` 邊界保護、Excel 公式注入消毒（`sanitize_excel_text`）與憑證遮罩（`redact_secrets`），以及銀行官網白名單防 SSRF。
  - **在地化與雙語 i18n（7 項）**：`zh-Hant` UTF-8 編碼、新台幣與台北時區格式、跨語系（`zh-TW` / `en-US` / `ja-JP`）瀏覽器容錯、右上角 `繁中 / EN` 切換與 `localStorage` 持久化、`/?lang=en` 直連、CJK 殘留與佔位符洩漏掃描。
- **Playwright 穩定性與失敗證據留存（[conftest.py](conftest.py) / [pages/](pages/)）**
  - 採用 **Page Object Model (`HomePage`、`MatrixTab`、`ScraperTab`)** 集中管理定位器與共用操作；全面改用 Web-First Assertions 與條件等待，消除硬等待與棄用 API。
  - 測試失敗時自動留存 **Playwright Trace (`*-trace.zip`)** 與 **全頁截圖 (`.png`)** 供 [trace.playwright.dev](https://trace.playwright.dev/) 回放除錯，通過則自動丟棄不佔空間。
- **模組化報表引擎與 CI/CD（[reporting/](reporting/) / [.github/workflows/test.yml](.github/workflows/test.yml)）**
  - 自動產出 **Excel（含動態 `Fail Rate` 公式與歷次趨勢表）**、**Markdown（自動輸出至 GitHub Actions Step Summary）**、**JUnit XML** 與 **HTML 互動總覽頁 (`index.html`)**。
  - CI 採獨立雙虛擬環境啟動本地 `credit_card_recommend` 避開 Cloudflare 403，支援 **每日排程 (`schedule`) 監控銀行官網**，並將歷史趨勢與線上報告自動發佈至 **`gh-pages` 分支（GitHub Pages）**。

---

## 專案結構

```text
credit_card_test/
├── .github/workflows/
│   └── test.yml                           # GitHub Actions CI（隔離環境、Step Summary、每日排程、gh-pages）
├── pages/
│   └── home_page.py                       # Page Object Model (HomePage, MatrixTab, ScraperTab)
├── reporting/
│   ├── catalog.py                         # 42 支 Test Case 目錄與 Priority 分級定義
│   ├── classifier.py                      # 錯誤分類、根因歸納與 Issue 去重引擎
│   ├── excel_writer.py                    # Excel 報表與動態 Fail Rate 公式產生器
│   ├── markdown_writer.py                 # Markdown 報表產生器（同步至 Step Summary）
│   └── html_writer.py                     # 獨立 HTML 總覽儀表板（供 GitHub Pages 展示）
├── tests/
│   ├── test_api.py                        # API 契約、試算結構、權限與 ?lang=en 測試 (11)
│   ├── test_functional_ui.py              # Playwright E2E 功能流程與桌機/手機響應式測試 (13)
│   ├── test_negative_e2e.py               # page.route() 負向容錯、唯讀鎖定與爬蟲閉環測試 (3)
│   ├── test_i18n.py                       # 在地化、多語系瀏覽器容錯與 繁中/EN i18n 測試 (7)
│   ├── test_official_rate_sync.py         # 比較表一致性與銀行官網即時回饋率/連結比對 (2)
│   ├── test_recommendation_correctness.py # 演算法獨立對拍、黃金案例、上限邊界與資料健檢 (6)
│   └── test_security.py                   # 寫入端點權限、limit 邊界、公式注入與官網白名單 (4)
├── conftest.py                            # CLI 選項、Trace/截圖失敗證據、錯誤監聽與報告掛鉤
├── pytest.ini                             # pytest markers 設定
├── README.md / README.en.md               # 專案說明（繁中 / English）
└── requirements.txt                       # 相依套件
```

> 註：本機執行後會自動產出 `reports/` 目錄（已列入 `.gitignore` 不推上 `main`）；CI 報告保留於 GitHub Actions Artifacts 與 `gh-pages` 分支。

---

## 快速開始 (Quick Start)

### 1. 安裝相依套件

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 若本機尚未安裝 Google Chrome，請執行 `playwright install chromium` 安裝 Playwright Chromium。

### 2. 執行測試

```bash
# 執行全部 42 支測試（預設目標：https://cards.zillurl.com）
pytest

# 指定本機開發站台並強制驗收英語 i18n
pytest --base-url http://127.0.0.1:8000 --require-en

# 只執行特定類型測試
pytest -m api
pytest -m functional
pytest -m negative
pytest -m i18n
pytest -m math
pytest -m official_sync

# 開啟瀏覽器畫面觀察執行過程 / 關閉自動產出報告
pytest --headed --no-report
```
