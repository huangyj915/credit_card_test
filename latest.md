# 自動化測試報告 (2026-11-19 16:25:30)

## 測試摘要

- **結果**：`FAIL`
- **目標網址**：`http://127.0.0.1:8000`
- **強制英語 i18n (`--require-en`)**：`False`
- **測試時間**：2026-11-19 16:25:30 ~ 16:25:52（總耗時 21.84s）
- **測試總數**：39 項｜✅ Passed: 35｜❌ Failed: 2｜⚠️ Error: 0｜⏭️ Skipped: 2

## 待修復 Issue 清單（開發端 Action Items）

| Issue ID | Priority | 負責端 | Fail Rate | 問題項目 (What to Fix) | 影響位置 | 根本原因 | 修復建議 | 關聯 TC |
|---|---|---|---|---|---|---|---|---|
| ISSUE-001 | P0 | 開發端 (Backend Recommender) | 1/39 (2.6%) | 推薦試算結果或最佳多卡組合計算與規則定義不符 | `POST /api/recommend 演算法引擎` | 推薦試算演算法邏輯缺陷 (Recommender Calculation Mismatch) | 檢查 recommender 計算溢額基本回饋、方案取優與 combo 分配邏輯。 | TC-MATH-001 |
| ISSUE-002 | P1 | 開發端 (待確認) | 1/39 (2.6%) | test_cap_overflow_and_min_spend_boundary_behavior 執行失敗 | `tests/test_recommendation_correctness.py` | 功能或資料預期不符 (Assertion / Runtime Failure) | 請開發端依錯誤訊息與測試步驟重現排查。 | TC-MATH-003 |

## Priority 分級統計

| Priority | 總數 | Passed | Failed | Error | Skipped |
|---|---:|---:|---:|---:|---:|
| P0 | 14 | 12 | 1 | 0 | 1 |
| P1 | 24 | 22 | 1 | 0 | 1 |
| P2 | 1 | 1 | 0 | 0 | 0 |

## Test Case 明細

| TC ID | Priority | 分類 | 測試案例名稱 | 結果 | 耗時 (s) | 錯誤原因 | 根本原因 |
|---|---|---|---|---|---:|---|---|
| TC-API-001 | P0 | API | 首頁 HTTP 200 與 UTF-8 編碼檢查 | ✅ PASSED | 0.01 | - | - |
| TC-API-002 | P0 | API | 系統設定 /api/config 欄位驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-003 | P0 | API | 消費通路目錄 /api/channels 完整性檢查 | ✅ PASSED | 0.00 | - | - |
| TC-API-004 | P0 | API | 信用卡清單與回饋規則 /api/cards 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-005 | P1 | API | 發卡銀行清單與級聯卡名查詢 API | ✅ PASSED | 0.01 | - | - |
| TC-API-006 | P1 | API | 爬蟲清單與紀錄查詢 /api/scrapers & /api/scrape-logs | ✅ PASSED | 0.00 | - | - |
| TC-API-007 | P0 | API | 信用卡回饋試算排序與多卡組合 /api/recommend | ✅ PASSED | 0.01 | - | - |
| TC-API-008 | P2 | API | 零消費邊界輸入 /api/recommend 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-009 | P1 | API | 無低消門檻過濾參數 only_no_min_spend 驗證 | ✅ PASSED | 0.01 | - | - |
| TC-API-010 | P1 | API | 爬蟲管理端點權限保護驗證 | ⏭️ SKIPPED | 0.00 | 目標站台未開啟管理員密碼或公開唯讀鎖定 | 環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN |
| TC-API-011 | P0 | i18n (EN) | 後端 API 英文語系 (?lang=en) 翻譯完整性 | ✅ PASSED | 0.01 | - | - |
| TC-UI-001 | P0 | Functional UI | 首頁初次載入預設套用 office 情境與推薦結果 | ✅ PASSED | 0.98 | - | - |
| TC-UI-002 | P1 | Functional UI | 情境範本切換：小資外食網購族 (office) | ✅ PASSED | 0.48 | - | - |
| TC-UI-003 | P1 | Functional UI | 情境範本切換：日本旅遊高消費族 (travel) | ✅ PASSED | 0.36 | - | - |
| TC-UI-004 | P1 | Functional UI | 情境範本切換：通勤超商日常族 (commuter) | ✅ PASSED | 0.39 | - | - |
| TC-UI-005 | P1 | Functional UI | 清空歸零按鈕重置消費金額與空白提示 | ✅ PASSED | 0.36 | - | - |
| TC-UI-006 | P0 | Functional UI | 手動輸入各通路金額並送出試算 | ✅ PASSED | 0.60 | - | - |
| TC-UI-007 | P1 | Functional UI | 勾選「僅顯示無低消門檻」即時重算 | ✅ PASSED | 0.38 | - | - |
| TC-UI-008 | P1 | Functional UI | 「各卡通路比較表」分頁渲染與高回饋標示 | ✅ PASSED | 0.35 | - | - |
| TC-UI-009 | P1 | Functional UI | 「Playwright 爬蟲中心」銀行與卡名連動下拉選單 | ✅ PASSED | 0.45 | - | - |
| TC-I18N-001 | P0 | Localization | 繁體中文 (zh-Hant) 語系標記與字串完整性檢查 | ✅ PASSED | 0.31 | - | - |
| TC-I18N-002 | P1 | Localization | 台幣格式 (NT$)、百分比與台北時區日期格式驗證 | ✅ PASSED | 0.33 | - | - |
| TC-I18N-003 | P1 | Localization | 瀏覽器語系 zh-TW 相容性與功能運作 | ✅ PASSED | 0.56 | - | - |
| TC-I18N-004 | P1 | Localization | 瀏覽器語系 en-US 相容性與功能運作 | ✅ PASSED | 0.53 | - | - |
| TC-I18N-005 | P1 | Localization | 瀏覽器語系 ja-JP 相容性與功能運作 | ✅ PASSED | 0.56 | - | - |
| TC-I18N-006 | P0 | i18n (EN) | 右上角繁中/EN 切換、全頁面英文翻譯、持久化與切回繁中 | ✅ PASSED | 1.52 | - | - |
| TC-I18N-007 | P1 | i18n (EN) | 網址參數 /?lang=en 直接進入英文介面驗證 | ✅ PASSED | 0.39 | - | - |
| TC-NEG-001 | P1 | Negative E2E | 負向測試：/api/recommend 回傳 500 後前端容錯與恢復 | ✅ PASSED | 0.58 | - | - |
| TC-NEG-002 | P1 | Negative E2E | 負向測試：public_readonly 模式下鎖定爬蟲與隱藏 /docs | ✅ PASSED | 0.48 | - | - |
| TC-NEG-003 | P1 | Negative E2E | 爬蟲中心 E2E 閉環：執行爬蟲後同步刷新結果區、日誌與比較表 | ✅ PASSED | 0.57 | - | - |
| TC-MATH-001 | P0 | Math & Logic | 獨立演算法對拍：單卡各通路回饋與有效回饋率精算驗證 | ❌ FAILED | 0.03 | 推薦演算法計算數值與規則獨立驗算結果不符 | 推薦試算演算法邏輯缺陷 (Recommender Calculation Mismatch) |
| TC-MATH-002 | P0 | Math & Logic | 多卡組合最佳化分配與多賺金額 (gain_over_best_single) 驗證 | ✅ PASSED | 0.01 | - | - |
| TC-MATH-003 | P1 | Math & Logic | 月回饋上限溢額計算與低消門檻過濾邊界驗證 | ❌ FAILED | 0.01 | E   assert 118.41999999999985 <= 0.05 | 功能或資料預期不符 (Assertion / Runtime Failure) |
| TC-MATH-004 | P1 | Math & Logic | 前端 UI 渲染金額與 /api/recommend API 回傳數值一致性驗證 | ✅ PASSED | 0.49 | - | - |
| TC-MATH-005 | P0 | Math & Logic | 黃金案例 (Golden Cases)：單調性、無負值與固定手工核算驗證 | ✅ PASSED | 0.02 | - | - |
| TC-SEC-001 | P0 | Security | 安全回歸：所有寫入端點於鎖定模式下皆拒絕未授權呼叫 | ⏭️ SKIPPED | 0.00 | 目標站台未開啟管理員密碼或公開唯讀鎖定 | 環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN |
| TC-SEC-002 | P1 | Security | 安全回歸：/api/scrape-logs limit 參數超大值與負值邊界防護 | ✅ PASSED | 0.00 | - | - |
| TC-SEC-003 | P1 | Security | 報表安全：Excel 公式注入防護與敏感憑證遮罩單元驗證 | ✅ PASSED | 0.00 | - | - |
| TC-SEC-004 | P1 | Security | 安全回歸：銀行官網白名單攔截非 HTTPS、內部位址與未核准網域 | ✅ PASSED | 0.00 | - | - |

## 失敗 / 錯誤 / 略過原始細節

### TC-API-010 (P1) `tests/test_api.py::test_admin_scrape_endpoint_protected_when_configured` — SKIPPED

- **錯誤原因**：目標站台未開啟管理員密碼或公開唯讀鎖定
- **根本原因**：環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN
- **建議處理**：屬正常跳過；若需驗證權限防護，請設定 ADMIN_TOKEN 後再測。

```text
Target instance is running without admin_protected or public_readonly lock
```

### TC-MATH-001 (P0) `tests/test_recommendation_correctness.py::test_recommend_oracle_matches_card_rules_and_caps` — FAILED

- **錯誤原因**：推薦演算法計算數值與規則獨立驗算結果不符
- **根本原因**：推薦試算演算法邏輯缺陷 (Recommender Calculation Mismatch)
- **建議處理**：核對推薦引擎中上限溢額、方案切換與多卡組合計算邏輯。

```text
tests/test_recommendation_correctness.py:125: in test_recommend_oracle_matches_card_rules_and_caps
    assert abs(rec["total_reward_ntd"] - oracle["total_reward_ntd"]) <= 0.1, (
E   AssertionError: sinopac-dawho total_reward_ntd mismatch: api=1679.99 vs oracle=2186.67
E   assert 506.68000000000006 <= 0.1
E    +  where 506.68000000000006 = abs((1679.99 - 2186.67))
```

### TC-MATH-003 (P1) `tests/test_recommendation_correctness.py::test_cap_overflow_and_min_spend_boundary_behavior` — FAILED

- **錯誤原因**：E   assert 118.41999999999985 <= 0.05
- **根本原因**：功能或資料預期不符 (Assertion / Runtime Failure)
- **建議處理**：檢視詳細錯誤堆疊並確認實際行為與規格。

```text
tests/test_recommendation_correctness.py:239: in test_cap_overflow_and_min_spend_boundary_behavior
    assert abs(above_card["total_reward_ntd"] - expected_above) <= 0.05
E   assert 118.41999999999985 <= 0.05
E    +  where 118.41999999999985 = abs((1736.84 - 1618.42))
```

### TC-SEC-001 (P0) `tests/test_security.py::test_write_endpoints_protected_when_locked` — SKIPPED

- **錯誤原因**：目標站台未開啟管理員密碼或公開唯讀鎖定
- **根本原因**：環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN
- **建議處理**：屬正常跳過；若需驗證權限防護，請設定 ADMIN_TOKEN 後再測。

```text
Target instance is running without admin_protected or public_readonly lock
```
