# 自動化測試報告 (2026-11-19 16:21:34)

## 測試摘要

- **結果**：`PASS`
- **目標網址**：`http://127.0.0.1:8000`
- **強制英語 i18n (`--require-en`)**：`False`
- **測試時間**：2026-11-19 16:21:34 ~ 16:21:57（總耗時 23.03s）
- **測試總數**：35 項｜✅ Passed: 31｜❌ Failed: 0｜⚠️ Error: 0｜⏭️ Skipped: 4

## 待修復 Issue 清單（開發端 Action Items）

✅ 本次無待修復 Issue！

## Priority 分級統計

| Priority | 總數 | Passed | Failed | Error | Skipped |
|---|---:|---:|---:|---:|---:|
| P0 | 13 | 11 | 0 | 0 | 2 |
| P1 | 21 | 19 | 0 | 0 | 2 |
| P2 | 1 | 1 | 0 | 0 | 0 |

## Test Case 明細

| TC ID | Priority | 分類 | 測試案例名稱 | 結果 | 耗時 (s) | 錯誤原因 | 根本原因 |
|---|---|---|---|---|---:|---|---|
| TC-API-001 | P0 | API | 首頁 HTTP 200 與 UTF-8 編碼檢查 | ✅ PASSED | 0.01 | - | - |
| TC-API-002 | P0 | API | 系統設定 /api/config 欄位驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-003 | P0 | API | 消費通路目錄 /api/channels 完整性檢查 | ✅ PASSED | 0.00 | - | - |
| TC-API-004 | P0 | API | 信用卡清單與回饋規則 /api/cards 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-005 | P1 | API | 發卡銀行清單與級聯卡名查詢 API | ✅ PASSED | 0.03 | - | - |
| TC-API-006 | P1 | API | 爬蟲清單與紀錄查詢 /api/scrapers & /api/scrape-logs | ✅ PASSED | 0.01 | - | - |
| TC-API-007 | P0 | API | 信用卡回饋試算排序與多卡組合 /api/recommend | ✅ PASSED | 0.00 | - | - |
| TC-API-008 | P2 | API | 零消費邊界輸入 /api/recommend 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-009 | P1 | API | 無低消門檻過濾參數 only_no_min_spend 驗證 | ✅ PASSED | 0.01 | - | - |
| TC-API-010 | P1 | API | 爬蟲管理端點權限保護驗證 | ⏭️ SKIPPED | 0.00 | 目標站台未開啟管理員密碼或公開唯讀鎖定 | 環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN |
| TC-API-011 | P0 | i18n (EN) | 後端 API 英文語系 (?lang=en) 翻譯完整性 | ⏭️ SKIPPED | 0.00 | 目標站台尚未提供英語切換按鈕或 ?lang=en | 功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文 |
| TC-UI-001 | P0 | Functional UI | 首頁初次載入預設套用 office 情境與推薦結果 | ✅ PASSED | 1.12 | - | - |
| TC-UI-002 | P1 | Functional UI | 情境範本切換：小資外食網購族 (office) | ✅ PASSED | 0.58 | - | - |
| TC-UI-003 | P1 | Functional UI | 情境範本切換：日本旅遊高消費族 (travel) | ✅ PASSED | 0.45 | - | - |
| TC-UI-004 | P1 | Functional UI | 情境範本切換：通勤超商日常族 (commuter) | ✅ PASSED | 0.43 | - | - |
| TC-UI-005 | P1 | Functional UI | 清空歸零按鈕重置消費金額與空白提示 | ✅ PASSED | 0.41 | - | - |
| TC-UI-006 | P0 | Functional UI | 手動輸入各通路金額並送出試算 | ✅ PASSED | 0.64 | - | - |
| TC-UI-007 | P1 | Functional UI | 勾選「僅顯示無低消門檻」即時重算 | ✅ PASSED | 0.45 | - | - |
| TC-UI-008 | P1 | Functional UI | 「各卡通路比較表」分頁渲染與高回饋標示 | ✅ PASSED | 0.51 | - | - |
| TC-UI-009 | P1 | Functional UI | 「Playwright 爬蟲中心」銀行與卡名連動下拉選單 | ✅ PASSED | 0.67 | - | - |
| TC-I18N-001 | P0 | Localization | 繁體中文 (zh-Hant) 語系標記與字串完整性檢查 | ✅ PASSED | 0.45 | - | - |
| TC-I18N-002 | P1 | Localization | 台幣格式 (NT$)、百分比與台北時區日期格式驗證 | ✅ PASSED | 0.39 | - | - |
| TC-I18N-003 | P1 | Localization | 瀏覽器語系 zh-TW 相容性與功能運作 | ✅ PASSED | 0.66 | - | - |
| TC-I18N-004 | P1 | Localization | 瀏覽器語系 en-US 相容性與功能運作 | ✅ PASSED | 0.66 | - | - |
| TC-I18N-005 | P1 | Localization | 瀏覽器語系 ja-JP 相容性與功能運作 | ✅ PASSED | 0.64 | - | - |
| TC-I18N-006 | P0 | i18n (EN) | 右上角繁中/EN 切換、全頁面英文翻譯、持久化與切回繁中 | ⏭️ SKIPPED | 0.66 | 目標站台尚未提供英語切換按鈕或 ?lang=en | 功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文 |
| TC-I18N-007 | P1 | i18n (EN) | 網址參數 /?lang=en 直接進入英文介面驗證 | ⏭️ SKIPPED | 0.47 | 目標站台尚未提供英語切換按鈕或 ?lang=en | 功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文 |
| TC-NEG-001 | P1 | Negative E2E | 負向測試：/api/recommend 回傳 500 後前端容錯與恢復 | ✅ PASSED | 0.58 | - | - |
| TC-NEG-002 | P1 | Negative E2E | 負向測試：public_readonly 模式下鎖定爬蟲與隱藏 /docs | ✅ PASSED | 0.58 | - | - |
| TC-NEG-003 | P1 | Negative E2E | 爬蟲中心 E2E 閉環：執行爬蟲後同步刷新結果區、日誌與比較表 | ✅ PASSED | 0.61 | - | - |
| TC-MATH-001 | P0 | Math & Logic | 獨立演算法對拍：單卡各通路回饋與有效回饋率精算驗證 | ✅ PASSED | 0.02 | - | - |
| TC-MATH-002 | P0 | Math & Logic | 多卡組合最佳化分配與多賺金額 (gain_over_best_single) 驗證 | ✅ PASSED | 0.01 | - | - |
| TC-MATH-003 | P1 | Math & Logic | 月回饋上限溢額計算與低消門檻過濾邊界驗證 | ✅ PASSED | 0.01 | - | - |
| TC-MATH-004 | P1 | Math & Logic | 前端 UI 渲染金額與 /api/recommend API 回傳數值一致性驗證 | ✅ PASSED | 0.59 | - | - |
| TC-MATH-005 | P0 | Math & Logic | 黃金案例 (Golden Cases)：單調性、無負值與固定手工核算驗證 | ✅ PASSED | 0.01 | - | - |

## 失敗 / 錯誤 / 略過原始細節

### TC-API-010 (P1) `tests/test_api.py::test_admin_scrape_endpoint_protected_when_configured` — SKIPPED

- **錯誤原因**：目標站台未開啟管理員密碼或公開唯讀鎖定
- **根本原因**：環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN
- **建議處理**：屬正常跳過；若需驗證權限防護，請設定 ADMIN_TOKEN 後再測。

```text
Target instance is running without admin_protected or public_readonly lock
```

### TC-API-011 (P0) `tests/test_api.py::test_api_endpoints_english_i18n` — SKIPPED

- **錯誤原因**：目標站台尚未提供英語切換按鈕或 ?lang=en
- **根本原因**：功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文
- **建議處理**：待英語功能部署後，改以 --require-en 參數執行強制驗收。

```text
API ?lang=en still returning CJK channel labels
```

### TC-I18N-006 (P0) `tests/test_i18n.py::test_english_i18n_switch_and_translations` — SKIPPED

- **錯誤原因**：目標站台尚未提供英語切換按鈕或 ?lang=en
- **根本原因**：功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文
- **建議處理**：待英語功能部署後，改以 --require-en 參數執行強制驗收。

```text
English (en) i18n is not yet active on the target URL (no English switcher or ?lang=en response detected). Run with --require-en once English is deployed.
```

### TC-I18N-007 (P1) `tests/test_i18n.py::test_english_query_param_direct_entry` — SKIPPED

- **錯誤原因**：目標站台尚未提供英語切換按鈕或 ?lang=en
- **根本原因**：功能尚未上線 (Feature Not Deployed) — 線上版僅提供繁體中文
- **建議處理**：待英語功能部署後，改以 --require-en 參數執行強制驗收。

```text
/?lang=en did not activate English mode
```
