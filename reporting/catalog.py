from __future__ import annotations

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
        "tests/test_recommendation_correctness.py::test_golden_hand_calculated_scenarios",
        {
            "tc_id": "TC-MATH-005",
            "priority": "P0",
            "category": "Math & Logic",
            "title": "黃金案例 (Golden Cases)：單調性、無負值與固定手工核算驗證",
            "expected": "消費倍增時總回饋單調不減、單通道回饋不超過消費額且無負值，不依賴鏡像實作。",
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
            "expected": "所有卡片 official_url 皆可正常開啟且非 404/錯誤頁，且網站顯示的規則回饋率皆可於官網主內容查證。",
        },
    ),
    (
        "tests/test_negative_e2e.py::test_recommend_api_500_error_recovery",
        {
            "tc_id": "TC-NEG-001",
            "priority": "P1",
            "category": "Negative E2E",
            "title": "負向測試：/api/recommend 回傳 500 後前端容錯與恢復",
            "expected": "模擬 API 500 失敗時頁面不崩潰、送出按鈕可再次點擊，且後續正常請求能恢復渲染。",
        },
    ),
    (
        "tests/test_negative_e2e.py::test_public_readonly_locks_scraper_controls",
        {
            "tc_id": "TC-NEG-002",
            "priority": "P1",
            "category": "Negative E2E",
            "title": "負向測試：public_readonly 模式下鎖定爬蟲與隱藏 /docs",
            "expected": "模擬 public_readonly=true 時顯示唯讀提示、隱藏 docsLink，且爬蟲按鈕皆為 disabled。",
        },
    ),
    (
        "tests/test_negative_e2e.py::test_scraper_demo_closed_loop_refreshes_ui",
        {
            "tc_id": "TC-NEG-003",
            "priority": "P1",
            "category": "Negative E2E",
            "title": "爬蟲中心 E2E 閉環：執行爬蟲後同步刷新結果區、日誌與比較表",
            "expected": "攔截 POST /api/scrape 回傳成功後，#scrapeResults 顯示結果、按鈕恢復可用並觸發卡片/日誌刷新。",
        },
    ),
    (
        "tests/test_security.py::test_write_endpoints_protected_when_locked",
        {
            "tc_id": "TC-SEC-001",
            "priority": "P0",
            "category": "Security",
            "title": "安全回歸：所有寫入端點於鎖定模式下皆拒絕未授權呼叫",
            "expected": "未帶憑證呼叫 /api/scrape、/api/scrape/custom、/api/banks/cathay/discover、/api/cards 皆回傳 401/403/405。",
        },
    ),
    (
        "tests/test_security.py::test_scrape_logs_limit_boundary_rejected_or_clamped",
        {
            "tc_id": "TC-SEC-002",
            "priority": "P1",
            "category": "Security",
            "title": "安全回歸：/api/scrape-logs limit 參數超大值與負值邊界防護",
            "expected": "limit=999999 與 limit=-1 應回傳 422 驗證錯誤或安全限制回傳筆數。",
        },
    ),
    (
        "tests/test_security.py::test_excel_formula_injection_and_secret_redaction",
        {
            "tc_id": "TC-SEC-003",
            "priority": "P1",
            "category": "Security",
            "title": "報表安全：Excel 公式注入防護與敏感憑證遮罩單元驗證",
            "expected": "sanitize_excel_text 中和 =/+/-/@ 開頭字串，redact_secrets 遮罩 X-Admin-Token / Bearer。",
        },
    ),
    (
        "tests/test_security.py::test_official_url_allowlist_blocks_untrusted_schemes_and_hosts",
        {
            "tc_id": "TC-SEC-004",
            "priority": "P1",
            "category": "Security",
            "title": "安全回歸：銀行官網白名單攔截非 HTTPS、內部位址與未核准網域",
            "expected": "http://、file://、127.0.0.1、evil.example 皆被白名單拒絕，僅核准台灣銀行 HTTPS 官網。",
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
