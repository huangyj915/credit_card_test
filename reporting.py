from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

REPORTS_DIR = Path(__file__).resolve().parent / "reports"

# Priority & Test Case Catalog keyed by nodeid prefix (supports parameterized suffixes)
TEST_CASE_CATALOG: list[tuple[str, dict[str, str]]] = [
    (
        "tests/test_api.py::test_homepage_utf8_and_status",
        {
            "tc_id": "TC-API-001",
            "priority": "P0",
            "category": "API",
            "title": "首頁 HTTP 200 與 UTF-8 編碼檢查",
            "expected": "GET / 回傳 HTTP 200，Content-Type 為 text/html 且編碼為 UTF-8。",
        },
    ),
    (
        "tests/test_api.py::test_get_config_shape",
        {
            "tc_id": "TC-API-002",
            "priority": "P0",
            "category": "API",
            "title": "系統設定 /api/config 欄位驗證",
            "expected": "GET /api/config 回傳布林型態之 admin_protected、public_readonly、docs_enabled。",
        },
    ),
    (
        "tests/test_api.py::test_get_channels_catalog",
        {
            "tc_id": "TC-API-003",
            "priority": "P0",
            "category": "API",
            "title": "消費通路目錄 /api/channels 完整性檢查",
            "expected": "至少包含 10 個標準通路代碼，且每個通路皆具 label、examples、icon。",
        },
    ),
    (
        "tests/test_api.py::test_get_cards_and_rules",
        {
            "tc_id": "TC-API-004",
            "priority": "P0",
            "category": "API",
            "title": "信用卡清單與回饋規則 /api/cards 驗證",
            "expected": "每張卡片皆含 bank_name、card_name、card_slug、國內/海外基本回饋率與 rules 清單。",
        },
    ),
    (
        "tests/test_api.py::test_get_banks_and_cascading_cards",
        {
            "tc_id": "TC-API-005",
            "priority": "P1",
            "category": "API",
            "title": "發卡銀行清單與級聯卡名查詢 API",
            "expected": "GET /api/banks 與 /api/banks/{code}/cards 皆正常回傳有效銀行與卡片資料。",
        },
    ),
    (
        "tests/test_api.py::test_get_scrapers_and_logs",
        {
            "tc_id": "TC-API-006",
            "priority": "P1",
            "category": "API",
            "title": "爬蟲清單與紀錄查詢 /api/scrapers & /api/scrape-logs",
            "expected": "GET /api/scrapers 回傳有效爬蟲；/api/scrape-logs?limit=5 回傳不超過 5 筆紀錄。",
        },
    ),
    (
        "tests/test_api.py::test_recommend_calculation_and_ranking",
        {
            "tc_id": "TC-API-007",
            "priority": "P0",
            "category": "API",
            "title": "信用卡回饋試算排序與多卡組合 /api/recommend",
            "expected": "依 total_reward_ntd 降冪排序，明細加總與總回饋一致，組合推薦總回饋不低於單卡。",
        },
    ),
    (
        "tests/test_api.py::test_recommend_zero_spending",
        {
            "tc_id": "TC-API-008",
            "priority": "P2",
            "category": "API",
            "title": "零消費邊界輸入 /api/recommend 驗證",
            "expected": "monthly_spending 為空時回傳 HTTP 200 且 total_spend_ntd == 0。",
        },
    ),
    (
        "tests/test_api.py::test_recommend_only_no_min_spend_filter",
        {
            "tc_id": "TC-API-009",
            "priority": "P1",
            "category": "API",
            "title": "無低消門檻過濾參數 only_no_min_spend 驗證",
            "expected": "only_no_min_spend=true 回傳卡片數不大於未過濾清單。",
        },
    ),
    (
        "tests/test_api.py::test_admin_scrape_endpoint_protected_when_configured",
        {
            "tc_id": "TC-API-010",
            "priority": "P1",
            "category": "API",
            "title": "爬蟲管理端點權限保護驗證",
            "expected": "若設定 admin_protected 或 public_readonly，未帶憑證呼叫 /api/scrape 應回傳 401/403。",
        },
    ),
    (
        "tests/test_api.py::test_api_endpoints_english_i18n",
        {
            "tc_id": "TC-API-011",
            "priority": "P0",
            "category": "i18n (EN)",
            "title": "後端 API 英文語系 (?lang=en) 翻譯完整性",
            "expected": "/api/channels、/api/cards、/api/banks、/api/recommend 在 lang=en 下不應殘留中文。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_initial_load_applies_default_office_preset",
        {
            "tc_id": "TC-UI-001",
            "priority": "P0",
            "category": "Functional UI",
            "title": "首頁初次載入預設套用 office 情境與推薦結果",
            "expected": "顯示 10 個通路輸入框、總消費 NT$ 26,000、第 1 名卡片明細預設展開且顯示多卡組合。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_presets_update_inputs_and_recommendations[office",
        {
            "tc_id": "TC-UI-002",
            "priority": "P1",
            "category": "Functional UI",
            "title": "情境範本切換：小資外食網購族 (office)",
            "expected": "點擊 office 範本後總金額更新為 NT$ 26,000 並觸發 /api/recommend 更新結果。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_presets_update_inputs_and_recommendations[travel",
        {
            "tc_id": "TC-UI-003",
            "priority": "P1",
            "category": "Functional UI",
            "title": "情境範本切換：日本旅遊高消費族 (travel)",
            "expected": "點擊 travel 範本後總金額更新為 NT$ 58,000 並觸發 /api/recommend 更新結果。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_presets_update_inputs_and_recommendations[commuter",
        {
            "tc_id": "TC-UI-004",
            "priority": "P1",
            "category": "Functional UI",
            "title": "情境範本切換：通勤超商日常族 (commuter)",
            "expected": "點擊 commuter 範本後總金額更新為 NT$ 27,000 並觸發 /api/recommend 更新結果。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_clear_inputs_resets_total_and_shows_empty_state",
        {
            "tc_id": "TC-UI-005",
            "priority": "P1",
            "category": "Functional UI",
            "title": "清空歸零按鈕重置消費金額與空白提示",
            "expected": "點擊清空歸零後所有輸入框歸 0、總消費顯示 NT$ 0、隱藏多卡組合並顯示空白提示。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_manual_spending_submission_and_breakdown",
        {
            "tc_id": "TC-UI-006",
            "priority": "P0",
            "category": "Functional UI",
            "title": "手動輸入各通路金額並送出試算",
            "expected": "手動輸入餐飲 8,000 + 海外 12,000 後送出表單，總消費 NT$ 20,000 且明細表為 2 列。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_only_no_min_spend_checkbox_sends_flag",
        {
            "tc_id": "TC-UI-007",
            "priority": "P1",
            "category": "Functional UI",
            "title": "勾選「僅顯示無低消門檻」即時重算",
            "expected": "勾選後發送 only_no_min_spend=true 並重新渲染推薦卡片。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_matrix_tab_renders_cards_and_channels",
        {
            "tc_id": "TC-UI-008",
            "priority": "P1",
            "category": "Functional UI",
            "title": "「各卡通路比較表」分頁渲染與高回饋標示",
            "expected": "切換至 matrix 分頁後顯示 11 欄（卡名 + 10 通路），且高回饋率標示 .rate-high。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_scraper_tab_controls_and_cascading_bank_cards",
        {
            "tc_id": "TC-UI-009",
            "priority": "P1",
            "category": "Functional UI",
            "title": "「Playwright 爬蟲中心」銀行與卡名連動下拉選單",
            "expected": "選取銀行後動態載入該行卡片、選取卡片自動帶入卡名，選其他銀行時顯示手動輸入欄。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_no_horizontal_overflow_across_tabs[viewport0",
        {
            "tc_id": "TC-UI-010",
            "priority": "P2",
            "category": "Responsive",
            "title": "桌機版 (1440x900) 全分頁無水平捲軸溢位",
            "expected": "recommend / matrix / scraper 三分頁之 scrollWidth <= clientWidth + 1px。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_no_horizontal_overflow_across_tabs[viewport1",
        {
            "tc_id": "TC-UI-011",
            "priority": "P2",
            "category": "Responsive",
            "title": "手機版 (390x844) 全分頁無水平捲軸溢位",
            "expected": "recommend / matrix / scraper 三分頁於手機視窗皆無水平溢位。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_channel_input_enforces_digit_limit_and_blocks_non_numeric",
        {
            "tc_id": "TC-UI-012",
            "priority": "P1",
            "category": "Functional UI",
            "title": "每月通路消費輸入框字數上限 (7 位數) 與非數字過濾",
            "expected": "輸入超過 7 位數截斷為 1234567，且攔截 e/+/-/. 等非數字字元。",
        },
    ),
    (
        "tests/test_functional_ui.py::test_truncated_condition_note_renders_more_link_to_source",
        {
            "tc_id": "TC-UI-013",
            "priority": "P1",
            "category": "Functional UI",
            "title": "條件說明截斷處顯示 more 超連結導向官網來源（含 EN 模式）",
            "expected": "過長條件說明結尾顯示省略號與 more 超連結（target=_blank、href 為有效來源網址），且 title 保留完整全文。",
        },
    ),
    (
        "tests/test_i18n.py::test_zh_hant_document_lang_charset_and_text_integrity",
        {
            "tc_id": "TC-I18N-001",
            "priority": "P0",
            "category": "Localization",
            "title": "繁體中文 (zh-Hant) 語系標記與字串完整性檢查",
            "expected": "<html lang='zh*'>、UTF-8、無亂碼 (U+FFFD) 且無未替換 i18n 佔位符。",
        },
    ),
    (
        "tests/test_i18n.py::test_zh_tw_currency_percentage_and_taipei_timestamp_formatting",
        {
            "tc_id": "TC-I18N-002",
            "priority": "P1",
            "category": "Localization",
            "title": "台幣格式 (NT$)、百分比與台北時區日期格式驗證",
            "expected": "金額符合 NT$ xx,xxx、回饋率含 %、資料更新徽章符合 YYYY-MM-DD 格式。",
        },
    ),
    (
        "tests/test_i18n.py::test_app_functional_under_different_browser_locales[zh-TW",
        {
            "tc_id": "TC-I18N-003",
            "priority": "P1",
            "category": "Localization",
            "title": "瀏覽器語系 zh-TW 相容性與功能運作",
            "expected": "zh-TW locale 下可正常切換 travel 範本、格式化 NT$ 58,000 且無 JS/5xx 錯誤。",
        },
    ),
    (
        "tests/test_i18n.py::test_app_functional_under_different_browser_locales[en-US",
        {
            "tc_id": "TC-I18N-004",
            "priority": "P1",
            "category": "Localization",
            "title": "瀏覽器語系 en-US 相容性與功能運作",
            "expected": "en-US locale 下可正常切換 travel 範本、Intl 格式化無異常且無 JS/5xx 錯誤。",
        },
    ),
    (
        "tests/test_i18n.py::test_app_functional_under_different_browser_locales[ja-JP",
        {
            "tc_id": "TC-I18N-005",
            "priority": "P1",
            "category": "Localization",
            "title": "瀏覽器語系 ja-JP 相容性與功能運作",
            "expected": "ja-JP locale 下可正常切換 travel 範本、Intl 格式化無異常且無 JS/5xx 錯誤。",
        },
    ),
    (
        "tests/test_i18n.py::test_english_i18n_switch_and_translations",
        {
            "tc_id": "TC-I18N-006",
            "priority": "P0",
            "category": "i18n (EN)",
            "title": "右上角繁中/EN 切換、全頁面英文翻譯、持久化與切回繁中",
            "expected": "切換 EN 後 lang=en、全分頁與通路無殘留中文、重整保留語系、桌機手機無溢位，切回繁中正常。",
        },
    ),
    (
        "tests/test_i18n.py::test_english_query_param_direct_entry",
        {
            "tc_id": "TC-I18N-007",
            "priority": "P1",
            "category": "i18n (EN)",
            "title": "網址參數 /?lang=en 直接進入英文介面驗證",
            "expected": "直接開啟 /?lang=en 首屏即套用英文介面 (<html lang='en'>) 且主標題為英文。",
        },
    ),
    (
        "tests/test_recommendation_correctness.py::test_recommend_oracle_matches_card_rules_and_caps",
        {
            "tc_id": "TC-MATH-001",
            "priority": "P0",
            "category": "Math & Logic",
            "title": "獨立演算法對拍：單卡各通路回饋與有效回饋率精算驗證",
            "expected": "依 /api/cards 規則獨立重算，每張卡之 applied_rate、actual_reward_ntd、total_reward_ntd 與 effective_rate_pct 完全吻合。",
        },
    ),
    (
        "tests/test_recommendation_correctness.py::test_combo_allocation_maximizes_channel_rewards_and_gain",
        {
            "tc_id": "TC-MATH-002",
            "priority": "P0",
            "category": "Math & Logic",
            "title": "多卡組合最佳化分配與多賺金額 (gain_over_best_single) 驗證",
            "expected": "combo 每個通路皆選取實際回饋最高之卡片，總回饋與 gain_over_best_single_ntd 精算無誤。",
        },
    ),
    (
        "tests/test_recommendation_correctness.py::test_cap_overflow_and_min_spend_boundary_behavior",
        {
            "tc_id": "TC-MATH-003",
            "priority": "P1",
            "category": "Math & Logic",
            "title": "月回饋上限溢額計算與低消門檻過濾邊界驗證",
            "expected": "未達上限依加碼率、超過上限之溢額退回基本回饋率，且 only_no_min_spend=true 正確排除有低消卡別。",
        },
    ),
    (
        "tests/test_recommendation_correctness.py::test_ui_displays_exact_api_recommendation_values",
        {
            "tc_id": "TC-MATH-004",
            "priority": "P1",
            "category": "Math & Logic",
            "title": "前端 UI 渲染金額與 /api/recommend API 回傳數值一致性驗證",
            "expected": "畫面呈現之最高卡名、月省金額、綜合回饋率、明細列數與多卡組合金額皆與 API 回應一致。",
        },
    ),
    (
        "tests/test_recommendation_correctness.py::test_card_rules_sanity_no_scraper_parse_artifacts",
        {
            "tc_id": "TC-DATA-001",
            "priority": "P1",
            "category": "Data Quality",
            "title": "卡片規則資料健檢：排除爬蟲誤解析異常利率或月上限",
            "expected": "規則中不應出現 >15% 異常利率、<50 元誤解析上限，或將年份(如 2024)誤當 monthly_cap_ntd。",
        },
    ),
    (
        "tests/test_official_rate_sync.py::test_ui_displayed_rates_match_api_cards_source_of_truth",
        {
            "tc_id": "TC-SYNC-001",
            "priority": "P0",
            "category": "Official Sync",
            "title": "網站比較表顯示回饋率與後端 /api/cards 資料一致性檢查",
            "expected": "各卡通路比較表 (#matrixTable) 每一格顯示的最高回饋率與 /api/cards 規則計算完全吻合。",
        },
    ),
    (
        "tests/test_official_rate_sync.py::test_displayed_card_rates_match_official_bank_websites",
        {
            "tc_id": "TC-SYNC-002",
            "priority": "P1",
            "category": "Official Sync",
            "title": "網站卡片回饋率與銀行官網實際公告比對（含官網連結有效性）",
            "expected": "所有卡片 official_url 皆可正常開啟且非 404/錯誤頁，且網站顯示的規則回饋率皆可於官網頁面吻合查證。",
        },
    ),
]


def lookup_test_meta(nodeid: str) -> dict[str, str]:
    for prefix, meta in TEST_CASE_CATALOG:
        if nodeid == prefix or nodeid.startswith(prefix):
            return meta
    return {
        "tc_id": "TC-MISC",
        "priority": "P2",
        "category": "General",
        "title": nodeid.split("::")[-1],
        "expected": "-",
    }


def classify_error_and_root_cause(
    nodeid: str, status: str, detail: str
) -> dict[str, str]:
    """Classify failure/error/skip into error_reason, root_cause, and dev issue metadata."""
    if status == "PASSED":
        return {
            "error_reason": "-",
            "root_cause": "-",
            "suggested_action": "-",
            "issue_key": "",
            "issue_owner": "",
            "issue_component": "",
            "issue_title": "",
            "issue_actual_vs_expected": "",
            "issue_fix_guide": "",
        }

    text = detail or ""

    if status == "SKIPPED":
        if "admin_protected" in text or "public_readonly" in text:
            return {
                "error_reason": "目標站台未開啟管理員密碼或公開唯讀鎖定",
                "root_cause": "環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN",
                "suggested_action": "屬正常跳過；若需驗證權限防護，請設定 ADMIN_TOKEN 後再測。",
                "issue_key": "",
                "issue_owner": "",
                "issue_component": "",
                "issue_title": "",
                "issue_actual_vs_expected": "",
                "issue_fix_guide": "",
            }
        if "English (en) i18n is not yet active" in text or "尚未部署英語" in text:
            return {
                "error_reason": "目標站台尚未提供英語切換按鈕或 ?lang=en",
                "root_cause": "功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文",
                "suggested_action": "待英語功能部署後，改以 --require-en 參數執行強制驗收。",
                "issue_key": "",
                "issue_owner": "",
                "issue_component": "",
                "issue_title": "",
                "issue_actual_vs_expected": "",
                "issue_fix_guide": "",
            }
        return {
            "error_reason": text.splitlines()[0] if text else "測試條件未滿足而跳過",
            "root_cause": "前置條件不適用 (Precondition Skipped)",
            "suggested_action": "確認執行參數與目標環境設定。",
            "issue_key": "",
            "issue_owner": "",
            "issue_component": "",
            "issue_title": "",
            "issue_actual_vs_expected": "",
            "issue_fix_guide": "",
        }

    if "status of 404" in text and "console_errors" in text:
        return {
            "error_reason": "瀏覽器主控台出現靜態資源 404 錯誤（如 /favicon.ico）",
            "root_cause": "站台靜態資源缺失 (Missing Static Asset)",
            "suggested_action": "於網站補上 favicon.ico 或 <link rel='icon'>，避免瀏覽器載入報 404。",
            "issue_key": "ISS-STATIC-404",
            "issue_owner": "開發端 (Frontend/FastAPI)",
            "issue_component": "靜態資源 /favicon.ico",
            "issue_title": "首頁載入時缺少 /favicon.ico 導致 Browser Console 報 404 錯誤",
            "issue_actual_vs_expected": "實際：Console 印出 404 Failed to load resource；預期：所有首頁預設請求皆為 2xx/3xx。",
            "issue_fix_guide": "在 static/ 加入 favicon.ico 或於 index.html 加上 <link rel='icon' href='...'>。",
        }

    if "Horizontal overflow" in text:
        m = re.search(r"overflow of (\d+)px on tab=(\w+)", text)
        px = m.group(1) if m else "?"
        tab = m.group(2) if m else "?"
        return {
            "error_reason": f"手機版 (390x844) 在 {tab} 分頁產生 {px}px 水平溢位",
            "root_cause": "產品版面缺陷 (Mobile CSS Layout Overflow) — .input-panel 寬度超出 390px 視窗",
            "suggested_action": "修正手機斷點 CSS（box-sizing: border-box、min-width: 0、調整 .channel-row / .input-wrap）。",
            "issue_key": "ISS-UI-MOBILE-OVERFLOW",
            "issue_owner": "開發端 (Frontend CSS)",
            "issue_component": "styles.css (手機版 390x844 / .input-panel)",
            "issue_title": f"手機版視窗 (390x844) 在 {tab} 分頁產生 {px}px 水平捲軸溢位",
            "issue_actual_vs_expected": f"實際：documentElement.scrollWidth 超出 clientWidth {px}px；預期：無水平溢位 (overflow <= 1px)。",
            "issue_fix_guide": "檢查 @media (max-width: 768px) 下 .main-grid、.panel.input-panel、.channel-row、.input-wrap 的寬度與 min-width: 0。",
        }

    if "Untranslated CJK lines in Scraper tab" in text or "scrapeLogs" in text or "成功透過 Playwright" in text:
        return {
            "error_reason": "英文模式下「Playwright 爬蟲中心」最近爬取紀錄 (#scrapeLogs) 仍顯示中文",
            "root_cause": "產品 i18n 缺漏 (Unlocalized DB Scrape Logs) — SQLite scrape_logs.message 以中文純文字儲存且未依語系轉換",
            "suggested_action": "於 /api/scrape-logs?lang=en 依語系格式化或翻譯歷史紀錄訊息（例如解析狀態與卡名）。",
            "issue_key": "ISS-I18N-SCRAPE-LOGS",
            "issue_owner": "開發端 (Backend API / SQLite)",
            "issue_component": "GET /api/scrape-logs?lang=en & #scrapeLogs",
            "issue_title": "英文模式 (?lang=en) 下「最近爬取紀錄」仍顯示中文歷史訊息",
            "issue_actual_vs_expected": "實際：#scrapeLogs 顯示「成功透過 Playwright 解析並更新『星展銀行 星展everyday鈦金卡』共 1 條通路規則」；預期：英文模式下顯示英文日誌。",
            "issue_fix_guide": "1) scrape_logs 改存結構化事件欄位（事件類型、規則數、card_slug）於 API 依 lang 渲染；或 2) 在 /api/scrape-logs?lang=en 針對既有中文日誌模板進行英文格式化與卡名替換。",
        }

    if "Untranslated CJK lines in Recommend tab" in text or "Untranslated card_name" in text or "福華聯名卡" in text:
        return {
            "error_reason": "英文模式下 /api/cards?lang=en 與推薦清單仍含未翻譯中文卡名或規則說明",
            "root_cause": "產品 i18n 缺漏 (Missing Backend/DB Card & Rule Translation)",
            "suggested_action": "補齊卡片名稱（如福華聯名卡、星展everyday鈦金卡）與爬蟲規則 note 之英文翻譯。",
            "issue_key": "ISS-I18N-CARD-RULES",
            "issue_owner": "開發端 (Backend API / i18n)",
            "issue_component": "GET /api/cards?lang=en & POST /api/recommend?lang=en",
            "issue_title": "英文語系 API 與推薦明細仍混有未翻譯中文卡名與規則 note",
            "issue_actual_vs_expected": "實際：card_name 含「福華聯名卡」且部分規則 note 為中文；預期：lang=en 下皆為英文。",
            "issue_fix_guide": "將未對照到的卡名與 scraped 規則 note 補入英文翻譯字典或 i18n 轉換邏輯。",
        }

    if "57,000" in text and "58,000" in text:
        return {
            "error_reason": "測試腳本預期 travel 範本總額 57,000，實際應為 58,000",
            "root_cause": "測試腳本缺陷 (Test Script Expected Value Typo)",
            "suggested_action": "已修正測試預期值為 NT$ 58,000（非產品 Bug）。",
            "issue_key": "ISS-TEST-PRESET-SUM",
            "issue_owner": "測試端 (Test Script)",
            "issue_component": "tests/test_functional_ui.py / tests/test_i18n.py",
            "issue_title": "[測試腳本問題] travel 情境加總預期值誤寫為 57,000（正確為 58,000）",
            "issue_actual_vs_expected": "實際頁面顯示 NT$ 58,000；舊版測試腳本誤設預期為 57,000。",
            "issue_fix_guide": "已將測試案例預期值修正為 58,000（無需開發端修改）。",
        }

    if "breakdown-table tbody tr" in text and "Actual value: 0" in text:
        return {
            "error_reason": "手動輸入測試抓到明細表為 0 列",
            "root_cause": "測試腳本缺陷 (Async Race Condition) — 未等待清空歸零 API 完成即送出新查詢",
            "suggested_action": "已於測試加上 expect_response 等待 clearInputsBtn 的 /api/recommend 完成（非產品 Bug）。",
            "issue_key": "ISS-TEST-ASYNC-RACE",
            "issue_owner": "測試端 (Test Script)",
            "issue_component": "tests/test_functional_ui.py",
            "issue_title": "[測試腳本問題] 清空按鈕後未等待非同步回應完成導致明細比對競態",
            "issue_actual_vs_expected": "舊版測試未等待 clearInputsBtn 之 POST /api/recommend 完成。",
            "issue_fix_guide": "已補上 page.expect_response 等待清空請求完成（無需開發端修改）。",
        }

    if "scraper-parsed rule anomalies" in text or "unrealistic rate=" in text or "monthly_cap_ntd=" in text:
        return {
            "error_reason": "卡片規則庫含爬蟲誤解析之異常利率 (>15%) 或月上限（如 3.0 / 1.0 / 年份 2024.0）",
            "root_cause": "資料與爬蟲解析缺陷 (Scraper Parsing Artifact) — 將活動滿額折抵/年份/利率數字誤存為 rate 或 monthly_cap_ntd",
            "suggested_action": "修正爬蟲規則擷取正規式並清理 SQLite 既有異常規則。",
            "issue_key": "ISS-DATA-SCRAPER-RULES",
            "issue_owner": "開發端 (Scraper / DB Data)",
            "issue_component": "SQLite card_rules & Playwright 爬蟲解析器",
            "issue_title": "爬蟲解析出異常回饋率 (>15%) 或異常月上限 (如 3.0 / 1.0 / 年份 2024.0) 導致推薦排名失真",
            "issue_actual_vs_expected": "實際：規則含 rate=19%/30% 或 monthly_cap_ntd=3.0/1.0/2024.0；預期：利率與上限應符合真實卡片權益格式。",
            "issue_fix_guide": "1) 強化爬蟲對「最高 X%」與「上限 N 元」的邊界判斷（過濾日期 YYYY/MM、排除小於 50 元的假上限與異常高 %）；2) 重爬或修正資料庫異常規則。",
        }

    if "Dead/broken official_url" in text or "Rate mismatch vs official bank page" in text:
        return {
            "error_reason": "網站部分卡片顯示之回饋率或官網連結與實際銀行官網不符（含 404/錯誤頁與過時利率）",
            "root_cause": "資料同步與來源連結缺陷 (Outdated Seed Data / Broken Official URL) — 銀行官網已改版或停售/調降利率，但站內規則與 URL 未同步更新",
            "suggested_action": "更新失效之 official_url（如 fubon-j、ubot-jihe），並重爬或校正與官網不符之回饋率（如 taishin-gogo、sinopac-dawho、custom-richart）。",
            "issue_key": "ISS-DATA-OFFICIAL-SYNC",
            "issue_owner": "開發端 (Seed Data / Scraper)",
            "issue_component": "SQLite cards.official_url & card_rules.rate",
            "issue_title": "網站顯示回饋率或官網來源連結與銀行官網現況不吻合",
            "issue_actual_vs_expected": next((ln.strip() for ln in text.splitlines() if ln.strip().startswith("E ")), "官網連結失效或利率與官網不符"),
            "issue_fix_guide": "1) 修正 404/錯誤之 official_url（fubon-j、ubot-jihe）；2) 依銀行官網最新公告更新過時回饋率（taishin-gogo 3%→3.8%、sinopac-dawho 7%→官網最新、richart 3.8%→3.88%）並定期排程重爬。",
        }

    if "mismatch:" in text or "suboptimal card" in text:
        return {
            "error_reason": "推薦演算法計算數值與規則獨立驗算結果不符",
            "root_cause": "推薦試算演算法邏輯缺陷 (Recommender Calculation Mismatch)",
            "suggested_action": "核對推薦引擎中上限溢額、方案切換與多卡組合計算邏輯。",
            "issue_key": "ISS-MATH-RECOMMEND",
            "issue_owner": "開發端 (Backend Recommender)",
            "issue_component": "POST /api/recommend 演算法引擎",
            "issue_title": "推薦試算結果或最佳多卡組合計算與規則定義不符",
            "issue_actual_vs_expected": next((ln.strip() for ln in text.splitlines() if ln.strip().startswith("E ")), "數值比對不一致"),
            "issue_fix_guide": "檢查 recommender 計算溢額基本回饋、方案取優與 combo 分配邏輯。",
        }

    first_err = next((ln.strip() for ln in text.splitlines() if ln.strip().startswith("E ")), "")
    return {
        "error_reason": first_err or (text.splitlines()[-1] if text else "斷言或執行失敗"),
        "root_cause": "功能或資料預期不符 (Assertion / Runtime Failure)",
        "suggested_action": "檢視詳細錯誤堆疊並確認實際行為與規格。",
        "issue_key": f"ISS-{nodeid.split('::')[-1][:24].upper()}",
        "issue_owner": "開發端 (待確認)",
        "issue_component": nodeid.split("::")[0],
        "issue_title": f"{nodeid.split('::')[-1]} 執行失敗",
        "issue_actual_vs_expected": first_err or "詳見 Raw Detail",
        "issue_fix_guide": "請開發端依錯誤訊息與測試步驟重現排查。",
    }


def enrich_results(results: list[dict]) -> list[dict]:
    enriched = []
    for r in results:
        meta = lookup_test_meta(r["nodeid"])
        info = classify_error_and_root_cause(
            r["nodeid"], r["status"], r.get("detail", "")
        )
        enriched.append(
            {
                **r,
                "tc_id": meta["tc_id"],
                "priority": meta["priority"],
                "category": meta["category"],
                "title": meta["title"],
                "expected": meta["expected"],
                **info,
            }
        )
    return enriched


def extract_dev_issues(enriched: list[dict]) -> list[dict]:
    """Group FAILED/ERROR tests into actionable deduplicated issues for developers."""
    grouped: dict[str, dict] = {}
    for r in enriched:
        if r["status"] not in {"FAILED", "ERROR"}:
            continue
        key = r["issue_key"] or r["tc_id"]
        if key not in grouped:
            grouped[key] = {
                "issue_key": key,
                "priority": r["priority"],
                "owner": r["issue_owner"],
                "component": r["issue_component"],
                "title": r["issue_title"],
                "actual_vs_expected": r["issue_actual_vs_expected"],
                "root_cause": r["root_cause"],
                "fix_guide": r["issue_fix_guide"],
                "tc_ids": [r["tc_id"]],
                "raw_detail": r.get("detail", ""),
            }
        else:
            if r["tc_id"] not in grouped[key]["tc_ids"]:
                grouped[key]["tc_ids"].append(r["tc_id"])
            # Escalate priority if a higher priority TC fails for same issue
            prio_order = {"P0": 0, "P1": 1, "P2": 2}
            if prio_order.get(r["priority"], 9) < prio_order.get(grouped[key]["priority"], 9):
                grouped[key]["priority"] = r["priority"]

    issues = []
    total_count = len(enriched)
    for idx, item in enumerate(grouped.values(), start=1):
        hit_count = len(item["tc_ids"])
        fail_rate_str = (
            f"{hit_count}/{total_count} ({(hit_count / total_count * 100):.1f}%)"
            if total_count
            else "0/0 (0.0%)"
        )
        issues.append(
            {
                "issue_no": f"ISSUE-{idx:03d}",
                **item,
                "fail_rate": fail_rate_str,
                "tc_ids_str": ", ".join(item["tc_ids"]),
            }
        )
    return issues


def _apply_header_style(cell, bg_hex: str = "1E293B") -> None:
    cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color=bg_hex, end_color=bg_hex, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _border_thin() -> Border:
    side = Side(border_style="thin", color="CBD5E1")
    return Border(left=side, right=side, top=side, bottom=side)


STATUS_FILLS = {
    "PASSED": PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid"),
    "FAILED": PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"),
    "ERROR": PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"),
    "SKIPPED": PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid"),
}

STATUS_FONTS = {
    "PASSED": Font(name="Calibri", size=10, bold=True, color="166534"),
    "FAILED": Font(name="Calibri", size=10, bold=True, color="991B1B"),
    "ERROR": Font(name="Calibri", size=10, bold=True, color="92400E"),
    "SKIPPED": Font(name="Calibri", size=10, bold=True, color="475569"),
}

PRIORITY_FILLS = {
    "P0": PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"),
    "P1": PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"),
    "P2": PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid"),
}


def format_report_markdown(
    *,
    started_at: datetime,
    finished_at: datetime,
    base_url: str,
    require_en: bool,
    results: list[dict],
    label: str = "",
) -> str:
    enriched = enrich_results(results)
    issues = extract_dev_issues(enriched)
    elapsed = max((finished_at - started_at).total_seconds(), 0.0)
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for r in enriched:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    total = len(enriched)
    err_count = counts["FAILED"] + counts["ERROR"]
    overall = "PASS" if err_count == 0 else "FAIL"
    suffix = f" - {label}" if label else ""

    lines = [
        f"# 自動化測試報告 ({started_at.strftime('%Y-%m-%d %H:%M:%S')}{suffix})",
        "",
        "## 測試摘要",
        "",
        f"- **結果**：`{overall}`",
        f"- **目標網址**：`{base_url}`",
        f"- **強制英語 i18n (`--require-en`)**：`{require_en}`",
        f"- **測試時間**：{started_at.strftime('%Y-%m-%d %H:%M:%S')} ~ {finished_at.strftime('%H:%M:%S')}（總耗時 {elapsed:.2f}s）",
        f"- **測試總數**：{total} 項｜✅ Passed: {counts['PASSED']}｜❌ Failed: {counts['FAILED']}｜⚠️ Error: {counts['ERROR']}｜⏭️ Skipped: {counts['SKIPPED']}",
        "",
        "## 待修復 Issue 清單（開發端 Action Items）",
        "",
    ]

    if not issues:
        lines.append("✅ 本次無待修復 Issue！")
    else:
        lines.extend(
            [
                "| Issue ID | Priority | 負責端 | Fail Rate | 問題項目 (What to Fix) | 影響位置 | 根本原因 | 修復建議 | 關聯 TC |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for iss in issues:
            lines.append(
                f"| {iss['issue_no']} | {iss['priority']} | {iss['owner']} | {iss['fail_rate']} | {iss['title']} | "
                f"`{iss['component']}` | {iss['root_cause']} | {iss['fix_guide']} | {iss['tc_ids_str']} |"
            )

    lines.extend(
        [
            "",
            "## Priority 分級統計",
            "",
            "| Priority | 總數 | Passed | Failed | Error | Skipped |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for prio in ("P0", "P1", "P2"):
        sub = [r for r in enriched if r["priority"] == prio]
        p_pass = sum(1 for r in sub if r["status"] == "PASSED")
        p_fail = sum(1 for r in sub if r["status"] == "FAILED")
        p_err = sum(1 for r in sub if r["status"] == "ERROR")
        p_skip = sum(1 for r in sub if r["status"] == "SKIPPED")
        lines.append(f"| {prio} | {len(sub)} | {p_pass} | {p_fail} | {p_err} | {p_skip} |")

    lines.extend(
        [
            "",
            "## Test Case 明細",
            "",
            "| TC ID | Priority | 分類 | 測試案例名稱 | 結果 | 耗時 (s) | 錯誤原因 | 根本原因 |",
            "|---|---|---|---|---|---:|---|---|",
        ]
    )
    icon_map = {
        "PASSED": "✅ PASSED",
        "FAILED": "❌ FAILED",
        "ERROR": "⚠️ ERROR",
        "SKIPPED": "⏭️ SKIPPED",
    }
    for r in enriched:
        lines.append(
            f"| {r['tc_id']} | {r['priority']} | {r['category']} | {r['title']} | "
            f"{icon_map.get(r['status'], r['status'])} | {r['duration']:.2f} | "
            f"{r['error_reason']} | {r['root_cause']} |"
        )

    non_pass = [r for r in enriched if r["status"] in {"FAILED", "ERROR", "SKIPPED"}]
    if non_pass:
        lines.extend(["", "## 失敗 / 錯誤 / 略過原始細節", ""])
        for r in non_pass:
            lines.extend(
                [
                    f"### {r['tc_id']} ({r['priority']}) `{r['nodeid']}` — {r['status']}",
                    "",
                    f"- **錯誤原因**：{r['error_reason']}",
                    f"- **根本原因**：{r['root_cause']}",
                    f"- **建議處理**：{r['suggested_action']}",
                    "",
                    "```text",
                    r["detail"] or "(無詳細訊息)",
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def write_excel_report(
    *,
    xlsx_path: Path,
    started_at: datetime,
    finished_at: datetime,
    base_url: str,
    require_en: bool,
    results: list[dict],
) -> None:
    enriched = enrich_results(results)
    issues = extract_dev_issues(enriched)
    elapsed = max((finished_at - started_at).total_seconds(), 0.0)
    thin = _border_thin()

    wb = Workbook()

    # --- Sheet 1: Summary ---
    ws_sum = wb.active
    ws_sum.title = "Summary"
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "信用卡比較網站自動化測試報告 (Test Summary & Dev Issues)"
    ws_sum["A1"].font = Font(name="Calibri", size=15, bold=True, color="0F172A")
    ws_sum.merge_cells("A1:H1")

    meta_rows = [
        ("目標網址 (Target URL)", base_url),
        ("測試時間 (Executed At)", f"{started_at.strftime('%Y-%m-%d %H:%M:%S')} ~ {finished_at.strftime('%H:%M:%S')}"),
        ("總耗時 (Duration)", f"{elapsed:.2f} s"),
        ("強制英語 i18n (--require-en)", str(require_en)),
    ]
    for idx, (k, v) in enumerate(meta_rows, start=3):
        ws_sum.cell(idx, 1, k).font = Font(name="Calibri", size=10, bold=True, color="334155")
        ws_sum.cell(idx, 2, v).font = Font(name="Calibri", size=10, color="0F172A")

    last_tc_row = 1 + len(enriched)

    # Overall KPI table (2 columns: drop 說明欄, no separate Fail Rate row here)
    ws_sum["A8"] = "整體測試指標 (Overall Metrics)"
    ws_sum["A8"].font = Font(name="Calibri", size=12, bold=True, color="0F172A")

    for col, h in enumerate(["指標 (Metric)", "數值 / 公式 (Value)"], start=1):
        c = ws_sum.cell(9, col, h)
        _apply_header_style(c, "1E293B")
        c.border = thin

    kpi_rows = [
        ("測試總數 (Total Test Cases)", f"=COUNTA('Test Cases'!A2:A{last_tc_row})"),
        ("通過數 (Passed)", f"=COUNTIF('Test Cases'!G2:G{last_tc_row},\"PASSED\")"),
        ("失敗數 (Failed)", f"=COUNTIF('Test Cases'!G2:G{last_tc_row},\"FAILED\")"),
        ("錯誤數 (Error)", f"=COUNTIF('Test Cases'!G2:G{last_tc_row},\"ERROR\")"),
        ("略過數 (Skipped)", f"=COUNTIF('Test Cases'!G2:G{last_tc_row},\"SKIPPED\")"),
    ]

    for offset, (label, formula) in enumerate(kpi_rows):
        row_num = 10 + offset
        c1 = ws_sum.cell(row_num, 1, label)
        c2 = ws_sum.cell(row_num, 2, formula)
        c1.font = Font(name="Calibri", size=10, bold=True)
        c2.font = Font(name="Calibri", size=10)
        for c in (c1, c2):
            c.border = thin
            c.alignment = Alignment(vertical="center")

    # Priority breakdown table (counts only)
    prio_title_row = 10 + len(kpi_rows) + 1
    ws_sum.cell(prio_title_row, 1, "依 Priority 分級統計 (Breakdown by Priority)").font = Font(
        name="Calibri", size=12, bold=True, color="0F172A"
    )

    prio_headers = ["Priority", "總數 (Total)", "Passed", "Failed", "Error", "Skipped"]
    prio_hdr_row = prio_title_row + 1
    for col, h in enumerate(prio_headers, start=1):
        c = ws_sum.cell(prio_hdr_row, col, h)
        _apply_header_style(c, "0F172A")
        c.border = thin

    for offset, prio in enumerate(("P0", "P1", "P2"), start=1):
        idx = prio_hdr_row + offset
        ws_sum.cell(idx, 1, prio).fill = PRIORITY_FILLS[prio]
        ws_sum.cell(idx, 1).font = Font(name="Calibri", size=10, bold=True)
        ws_sum.cell(idx, 2, f'=COUNTIF(\'Test Cases\'!B2:B{last_tc_row},"{prio}")')
        ws_sum.cell(idx, 3, f'=COUNTIFS(\'Test Cases\'!B2:B{last_tc_row},"{prio}",\'Test Cases\'!G2:G{last_tc_row},"PASSED")')
        ws_sum.cell(idx, 4, f'=COUNTIFS(\'Test Cases\'!B2:B{last_tc_row},"{prio}",\'Test Cases\'!G2:G{last_tc_row},"FAILED")')
        ws_sum.cell(idx, 5, f'=COUNTIFS(\'Test Cases\'!B2:B{last_tc_row},"{prio}",\'Test Cases\'!G2:G{last_tc_row},"ERROR")')
        ws_sum.cell(idx, 6, f'=COUNTIFS(\'Test Cases\'!B2:B{last_tc_row},"{prio}",\'Test Cases\'!G2:G{last_tc_row},"SKIPPED")')
        for col in range(1, 7):
            cell = ws_sum.cell(idx, col)
            cell.border = thin
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Open Dev Issues directly on Summary sheet with Fail Rate on the same row
    issue_title_row = prio_hdr_row + 5
    ws_sum.cell(issue_title_row, 1, "待修復 Issue 清單（給開發端 Action Items）").font = Font(
        name="Calibri", size=12, bold=True, color="991B1B"
    )
    sum_issue_headers = [
        "Issue ID",
        "Priority",
        "負責端",
        "Fail Rate",
        "待修復問題 (What to Fix)",
        "影響位置",
        "根本原因 (Root Cause)",
        "修復建議 (How to Fix)",
        "關聯 TC ID",
    ]
    issue_hdr_row = issue_title_row + 1
    for col, h in enumerate(sum_issue_headers, start=1):
        c = ws_sum.cell(issue_hdr_row, col, h)
        _apply_header_style(c, "991B1B")
        c.border = thin

    if not issues:
        c = ws_sum.cell(issue_hdr_row + 1, 1, "✅ 本次測試無待修復 Issue！")
        c.font = Font(name="Calibri", size=11, bold=True, color="166534")
    else:
        for offset, iss in enumerate(issues):
            r_num = issue_hdr_row + 1 + offset
            issue_key = iss["issue_key"]
            hit_expr = (
                f'(COUNTIFS(\'Test Cases\'!$I$2:$I${last_tc_row},"{issue_key}",\'Test Cases\'!$G$2:$G${last_tc_row},"FAILED")'
                f'+COUNTIFS(\'Test Cases\'!$I$2:$I${last_tc_row},"{issue_key}",\'Test Cases\'!$G$2:$G${last_tc_row},"ERROR"))'
            )
            fail_rate_formula = (
                f'={hit_expr}&"/"&$B$10&" ("&TEXT(IF($B$10>0,{hit_expr}/$B$10,0),"0.0%")&")"'
            )
            vals = [
                iss["issue_no"],
                iss["priority"],
                iss["owner"],
                fail_rate_formula,
                iss["title"],
                iss["component"],
                iss["root_cause"],
                iss["fix_guide"],
                iss["tc_ids_str"],
            ]
            for col, v in enumerate(vals, start=1):
                c = ws_sum.cell(r_num, col, v)
                c.border = thin
                c.font = Font(name="Calibri", size=10)
                c.alignment = Alignment(
                    horizontal="center" if col in {1, 2, 3, 4, 9} else "left",
                    vertical="top",
                    wrap_text=True,
                )
            p_cell = ws_sum.cell(r_num, 2)
            if iss["priority"] in PRIORITY_FILLS:
                p_cell.fill = PRIORITY_FILLS[iss["priority"]]
                p_cell.font = Font(name="Calibri", size=10, bold=True)
            fr_cell = ws_sum.cell(r_num, 4)
            fr_cell.fill = STATUS_FILLS["FAILED"]
            fr_cell.font = STATUS_FONTS["FAILED"]

    for col, w in enumerate([32, 18, 24, 16, 40, 28, 38, 44, 18], start=1):
        ws_sum.column_dimensions[get_column_letter(col)].width = w

    # --- Sheet 2: Issues (詳細開發待修單) ---
    ws_iss = wb.create_sheet("Issues")
    ws_iss.freeze_panes = "A2"
    iss_headers = [
        "Issue ID",
        "Issue Key",
        "Priority",
        "負責端 (Owner)",
        "Fail Rate",
        "影響位置 (Component)",
        "問題描述 (What to Fix)",
        "實際 vs 預期 (Actual vs Expected)",
        "根本原因 (Root Cause)",
        "開發修復建議 (How to Fix)",
        "關聯 TC ID",
        "詳細錯誤訊息 (Raw Detail)",
    ]
    for col, h in enumerate(iss_headers, start=1):
        c = ws_iss.cell(1, col, h)
        _apply_header_style(c, "991B1B")
        c.border = thin

    if not issues:
        ws_iss.cell(2, 1, "✅ 本次無待修復 Issue！").font = Font(name="Calibri", size=11, bold=True, color="166534")
    else:
        for row_idx, iss in enumerate(issues, start=2):
            issue_key = iss["issue_key"]
            hit_expr = (
                f'(COUNTIFS(\'Test Cases\'!$I$2:$I${last_tc_row},"{issue_key}",\'Test Cases\'!$G$2:$G${last_tc_row},"FAILED")'
                f'+COUNTIFS(\'Test Cases\'!$I$2:$I${last_tc_row},"{issue_key}",\'Test Cases\'!$G$2:$G${last_tc_row},"ERROR"))'
            )
            fail_rate_formula = (
                f'={hit_expr}&"/"&Summary!$B$10&" ("&TEXT(IF(Summary!$B$10>0,{hit_expr}/Summary!$B$10,0),"0.0%")&")"'
            )
            vals = [
                iss["issue_no"],
                iss["issue_key"],
                iss["priority"],
                iss["owner"],
                fail_rate_formula,
                iss["component"],
                iss["title"],
                iss["actual_vs_expected"],
                iss["root_cause"],
                iss["fix_guide"],
                iss["tc_ids_str"],
                (iss["raw_detail"] or "")[:3000],
            ]
            for col, v in enumerate(vals, start=1):
                c = ws_iss.cell(row_idx, col, v)
                c.border = thin
                c.font = Font(name="Calibri", size=10)
                c.alignment = Alignment(
                    horizontal="center" if col in {1, 2, 3, 4, 5, 11} else "left",
                    vertical="top",
                    wrap_text=True,
                )
            p_cell = ws_iss.cell(row_idx, 3)
            if iss["priority"] in PRIORITY_FILLS:
                p_cell.fill = PRIORITY_FILLS[iss["priority"]]
                p_cell.font = Font(name="Calibri", size=10, bold=True)
            fr_cell = ws_iss.cell(row_idx, 5)
            fr_cell.fill = STATUS_FILLS["FAILED"]
            fr_cell.font = STATUS_FONTS["FAILED"]

    for col, w in enumerate([12, 24, 10, 22, 16, 30, 38, 42, 42, 46, 18, 56], start=1):
        ws_iss.column_dimensions[get_column_letter(col)].width = w

    # --- Sheet 3: Test Cases ---
    ws_tc = wb.create_sheet("Test Cases")
    ws_tc.freeze_panes = "A2"
    tc_headers = [
        "TC ID",
        "Priority",
        "Category",
        "測試案例名稱 (Test Case Title)",
        "預期結果 (Expected Result)",
        "Pytest Node ID",
        "Status",
        "Duration (s)",
        "Issue Key",
        "錯誤原因 (Error Reason)",
        "根本原因 (Root Cause)",
        "詳細錯誤訊息 (Raw Detail)",
    ]
    for col, h in enumerate(tc_headers, start=1):
        c = ws_tc.cell(1, col, h)
        _apply_header_style(c, "1E293B")
        c.border = thin

    for row_idx, r in enumerate(enriched, start=2):
        vals = [
            r["tc_id"],
            r["priority"],
            r["category"],
            r["title"],
            r["expected"],
            r["nodeid"],
            r["status"],
            r["duration"],
            r["issue_key"] or "-",
            r["error_reason"],
            r["root_cause"],
            (r.get("detail") or "")[:2000],
        ]
        for col, v in enumerate(vals, start=1):
            c = ws_tc.cell(row_idx, col, v)
            c.border = thin
            c.font = Font(name="Calibri", size=10)
            c.alignment = Alignment(
                horizontal="center" if col in {1, 2, 3, 7, 8, 9} else "left",
                vertical="top",
                wrap_text=True,
            )
        prio_cell = ws_tc.cell(row_idx, 2)
        if r["priority"] in PRIORITY_FILLS:
            prio_cell.fill = PRIORITY_FILLS[r["priority"]]
            prio_cell.font = Font(name="Calibri", size=10, bold=True)

        st_cell = ws_tc.cell(row_idx, 7)
        if r["status"] in STATUS_FILLS:
            st_cell.fill = STATUS_FILLS[r["status"]]
            st_cell.font = STATUS_FONTS[r["status"]]

    tc_widths = [14, 10, 14, 34, 42, 46, 12, 12, 22, 36, 42, 52]
    for col, w in enumerate(tc_widths, start=1):
        ws_tc.column_dimensions[get_column_letter(col)].width = w

    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(xlsx_path)


def update_history_summary_excel(
    *,
    history_path: Path,
    run_id: str,
    started_at: datetime,
    finished_at: datetime,
    base_url: str,
    require_en: bool,
    results: list[dict],
    report_file: str,
) -> None:
    enriched = enrich_results(results)
    issues = extract_dev_issues(enriched)
    elapsed = max((finished_at - started_at).total_seconds(), 0.0)
    total = len(enriched)
    passed = sum(1 for r in enriched if r["status"] == "PASSED")
    failed = sum(1 for r in enriched if r["status"] == "FAILED")
    errored = sum(1 for r in enriched if r["status"] == "ERROR")
    skipped = sum(1 for r in enriched if r["status"] == "SKIPPED")
    err_count = failed + errored

    err_rate_str = (
        f"{err_count}/{total} ({(err_count / total * 100):.1f}%)"
        if (issues and total)
        else "-"
    )
    issues_summary = (
        "；".join(f"[{iss['priority']}] {iss['issue_key']}: {iss['title']}" for iss in issues)
        if issues
        else "無待修 Issue（全部通過）"
    )

    headers = [
        "Run ID",
        "執行時間 (Timestamp)",
        "目標網址 (Target URL)",
        "--require-en",
        "測試總數 (Total)",
        "Passed",
        "Failed",
        "Error",
        "Skipped",
        "Fail Rate",
        "待修 Issue 數",
        "耗時 (s)",
        "待修復 Issue 摘要 (Dev Action Items)",
        "報告檔名 (Report File)",
    ]

    thin = _border_thin()
    # Always recreate cleanly if column layout changed
    if history_path.exists():
        wb = load_workbook(history_path)
        ws = wb.active
        existing_headers = [ws.cell(1, c).value for c in range(1, len(headers) + 1)]
        if existing_headers != headers:
            wb = Workbook()
            ws = wb.active
            ws.title = "Run History"
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Run History"

    ws.freeze_panes = "A2"
    for col, h in enumerate(headers, start=1):
        c = ws.cell(1, col, h)
        _apply_header_style(c, "0F172A")
        c.border = thin

    target_row = None
    for row_idx in range(2, ws.max_row + 1):
        if ws.cell(row_idx, 1).value == run_id:
            target_row = row_idx
            break
    if target_row is None:
        target_row = ws.max_row + 1

    fail_rate_formula = (
        f'=IF((G{target_row}+H{target_row})>0,'
        f'(G{target_row}+H{target_row})&"/"&E{target_row}&" ("&TEXT(IF(E{target_row}>0,(G{target_row}+H{target_row})/E{target_row},0),"0.0%")&")",'
        f'"-")'
    )
    row_vals = [
        run_id,
        started_at.strftime("%Y-%m-%d %H:%M:%S"),
        base_url,
        str(require_en),
        total,
        passed,
        failed,
        errored,
        skipped,
        fail_rate_formula,
        len(issues),
        round(elapsed, 2),
        issues_summary,
        report_file,
    ]
    for col, val in enumerate(row_vals, start=1):
        c = ws.cell(target_row, col, val)
        c.border = thin
        c.font = Font(name="Calibri", size=10)
        c.alignment = Alignment(
            horizontal="center" if col not in {3, 13, 14} else "left",
            vertical="center",
            wrap_text=True,
        )

    widths = [18, 20, 26, 12, 12, 10, 10, 10, 10, 20, 12, 10, 56, 30]
    for col, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col)].width = w

    history_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(history_path)


def write_all_run_reports(
    *,
    started_at: datetime,
    finished_at: datetime,
    base_url: str,
    require_en: bool,
    results: list[dict],
    reports_dir: Path = REPORTS_DIR,
    update_latest: bool = True,
    label: str = "",
) -> tuple[Path, Path, Path]:
    ts = started_at.strftime("%Y%m%d-%H%M%S")
    md_path = reports_dir / f"test-report-{ts}.md"
    xlsx_path = reports_dir / f"test-report-{ts}.xlsx"
    history_path = reports_dir / "test-history-summary.xlsx"

    md_text = format_report_markdown(
        started_at=started_at,
        finished_at=finished_at,
        base_url=base_url,
        require_en=require_en,
        results=results,
        label=label,
    )
    reports_dir.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    write_excel_report(
        xlsx_path=xlsx_path,
        started_at=started_at,
        finished_at=finished_at,
        base_url=base_url,
        require_en=require_en,
        results=results,
    )

    if update_latest:
        (reports_dir / "latest.md").write_text(md_text, encoding="utf-8")
        write_excel_report(
            xlsx_path=reports_dir / "latest.xlsx",
            started_at=started_at,
            finished_at=finished_at,
            base_url=base_url,
            require_en=require_en,
            results=results,
        )

    update_history_summary_excel(
        history_path=history_path,
        run_id=ts,
        started_at=started_at,
        finished_at=finished_at,
        base_url=base_url,
        require_en=require_en,
        results=results,
        report_file=xlsx_path.name,
    )

    return md_path, xlsx_path, history_path
