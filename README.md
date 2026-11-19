# Credit Card Recommender — E2E, API & i18n Automated Test Suite

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.x-0A9EDC?logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Chromium%2FChrome-2EAD33?logo=playwright&logoColor=white)
![openpyxl](https://img.shields.io/badge/Reports-Excel%20%2B%20Markdown-217346?logo=microsoftexcel&logoColor=white)

針對 [台灣信用卡回饋比較 & 通路推薦系統 (`cards.zillurl.com`)](https://cards.zillurl.com/)（原始專案：[huangyj915/credit_card_recommend](https://github.com/huangyj915/credit_card_recommend)）建置的端對端自動化測試框架，涵蓋 **REST API 契約驗證、Chromium E2E 功能測試、手機/桌機響應式版面檢查、繁體中文在地化與雙語（`zh-TW` / `en`）i18n 驗證**，並內建 **Excel / Markdown 自動測試報告引擎**。

---

## 核心特色 (Key Highlights)

- **分層測試架構（38 支用例，分級 `P0` / `P1` / `P2`）**
  - **API 契約與基礎介面（11 項）**：驗證 `/api/config`、`/api/channels`、`/api/cards`、`/api/banks` 級聯查詢、`/api/recommend` 基本結構、邊界輸入、權限鎖定及 `?lang=en` 語系回傳。
  - **推薦演算法精算與規則資料品質（5 項）**：獨立實作規則重算 Oracle 逐卡核對上限溢額與方案取優、驗證多卡組合 (`combo`) 最佳分配與 `gain_over_best_single_ntd`、核對前後端數字一致，以及爬蟲規則合理性健檢。
  - **銀行官網回饋率即時比對（2 項）**：驗證前端比較表與 `/api/cards` 資料一致性，並以 Playwright 開啟各卡 `official_url` 比對實際銀行官網利率與連結有效性。
  - **E2E 功能與響應式版面（13 項）**：預設情境與多組花費試算、輸入字數上限與非數字攔截、截斷條件說明 `more` 來源超連結、清空歸零、手動送出與明細核對、無低消過濾、比較表與爬蟲中心級聯選單，以及桌機 (`1440x900`) / 手機 (`390x844`) 水平溢位檢查。
  - **在地化與雙語 i18n（7 項）**：`zh-Hant` UTF-8 編碼、新台幣與台北時區格式、跨語系（`zh-TW` / `en-US` / `ja-JP`）瀏覽器容錯、右上角 `繁中 / EN` 切換與 `localStorage` 持久化、`/?lang=en` 直連進入、CJK 殘留與佔位符洩漏掃描。
- **自動產出結構化 Excel 測試報告（[reporting.py](reporting.py)）**
  - 每次 `pytest` 執行完畢自動產出 `reports/test-report-YYYYMMDD-HHMMSS.xlsx`（與 `reports/latest.xlsx`、`latest.md`）及跨次趨勢表 `reports/test-history-summary.xlsx`。
  - 內含 **`Summary`**（KPI 與 Priority `P0`/`P1`/`P2` 分級統計）、**`Issues`**（自動去重歸納開發端待修清單，同列顯示 **Fail Rate**、影響元件、根本原因與修復建議）、**`Test Cases`**（完整 TC 明細與紅綠標色）。
- **環境彈性切換 & CI 就緒**
  - 透過 `--base-url` 與 `--require-en` 可同時驗證線上站台與本機開發站；內建 [GitHub Actions 工作流程](.github/workflows/test.yml)，於 CI Runner 內自動拉取 `credit_card_recommend` 啟動本地 Uvicorn 進行隔離測試（避開線上 Cloudflare 防爬蟲攔截），並上傳 `.xlsx` / `.md` 報告為 Artifact。

---

## 專案結構

```text
credit_card_test/
├── .github/workflows/
│   └── test.yml                # GitHub Actions CI（自動跑測試並上傳 Excel/MD 報告）
├── tests/
│   ├── test_api.py                       # API 契約、試算結構、權限與 ?lang=en 測試
│   ├── test_functional_ui.py             # Playwright E2E 功能流程與桌機/手機響應式測試
│   ├── test_i18n.py                      # 在地化、多語系瀏覽器容錯與 繁中/EN i18n 測試
│   ├── test_official_rate_sync.py        # 比較表一致性與銀行官網即時回饋率/連結比對
│   └── test_recommendation_correctness.py # 推薦演算法獨立對拍、上限邊界與規則資料健檢
├── reports/
│   ├── latest.xlsx / latest.md # 最新一次執行報告
│   ├── test-history-summary.xlsx # 歷次執行趨勢與 Fail Rate 彙總
│   └── test-report-*.xlsx/.md  # 各次歷史測試報告紀錄
├── conftest.py                 # CLI 選項、Chrome/Chromium fixture 與錯誤監聽、報告掛鉤
├── reporting.py                # Test Case 目錄、根因分類引擎、Excel & Markdown 產生器
├── pytest.ini                  # pytest markers 設定
└── requirements.txt            # 相依套件
```

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
# 執行全部測試（預設目標：https://cards.zillurl.com）
pytest

# 指定本機開發站台並強制驗收英語 i18n
pytest --base-url http://127.0.0.1:8000 --require-en

# 只執行特定類型測試
pytest -m api
pytest -m functional
pytest -m i18n

# 開啟瀏覽器畫面觀察執行過程 / 關閉自動產出報告
pytest --headed --no-report
```

---

## 實測抓出與驗證修復之缺陷紀錄

本測試套件於開發階段實際協助定位並追蹤修復以下問題（完整紀錄見 [`reports/test-history-summary.xlsx`](reports/test-history-summary.xlsx)）：

1. **手機版響應式溢位（`390x844`）**：偵測出 `recommend` 分頁產生 22px～43px 水平捲軸溢位，協助定位 `.input-panel` 寬度異常並驗證修復至 0 溢位。
2. **英語 API 與推薦明細漏翻**：檢出 `/api/cards?lang=en` 部分卡名（如 `福華聯名卡`、`星展everyday鈦金卡`）及爬蟲規則 `note` 殘留中文，追蹤修復至全數通過。
3. **歷史爬蟲日誌（`scrape_logs`）未依語系轉換**：檢出切換英文介面後 `#scrapeLogs` 仍顯示中文資料庫訊息，協助完成 `/api/scrape-logs?lang=en` 在地化並驗證全部 28 項執行測試 100% 通過。
