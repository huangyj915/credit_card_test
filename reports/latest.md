# 自動化測試報告 (2026-11-19 23:06:53)

## 測試摘要

- **結果**：`FAIL`
- **目標網址**：`http://127.0.0.1:8000`
- **強制英語 i18n (`--require-en`)**：`True`
- **測試時間**：2026-11-19 23:06:53 ~ 23:08:16（總耗時 83.02s）
- **測試總數**：38 項｜✅ Passed: 36｜❌ Failed: 1｜⚠️ Error: 0｜⏭️ Skipped: 1

## 待修復 Issue 清單（開發端 Action Items）

| Issue ID | Priority | 負責端 | Fail Rate | 問題項目 (What to Fix) | 影響位置 | 根本原因 | 修復建議 | 關聯 TC |
|---|---|---|---|---|---|---|---|---|
| ISSUE-001 | P1 | 開發端 (Seed Data / Scraper) | 1/38 (2.6%) | 網站顯示回饋率或官網來源連結與銀行官網現況不吻合 | `SQLite cards.official_url & card_rules.rate` | 資料同步與來源連結缺陷 (Outdated Seed Data / Broken Official URL) — 銀行官網已改版或停售/調降利率，但站內規則與 URL 未同步更新 | 1) 修正 404/錯誤之 official_url（fubon-j、ubot-jihe）；2) 依銀行官網最新公告更新過時回饋率（taishin-gogo 3%→3.8%、sinopac-dawho 7%→官網最新、richart 3.8%→3.88%）並定期排程重爬。 | TC-SYNC-002 |

## Priority 分級統計

| Priority | 總數 | Passed | Failed | Error | Skipped |
|---|---:|---:|---:|---:|---:|
| P0 | 13 | 13 | 0 | 0 | 0 |
| P1 | 22 | 20 | 1 | 0 | 1 |
| P2 | 3 | 3 | 0 | 0 | 0 |

## Test Case 明細

| TC ID | Priority | 分類 | 測試案例名稱 | 結果 | 耗時 (s) | 錯誤原因 | 根本原因 |
|---|---|---|---|---|---:|---|---|
| TC-API-001 | P0 | API | 首頁 HTTP 200 與 UTF-8 編碼檢查 | ✅ PASSED | 0.01 | - | - |
| TC-API-002 | P0 | API | 系統設定 /api/config 欄位驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-003 | P0 | API | 消費通路目錄 /api/channels 完整性檢查 | ✅ PASSED | 0.00 | - | - |
| TC-API-004 | P0 | API | 信用卡清單與回饋規則 /api/cards 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-005 | P1 | API | 發卡銀行清單與級聯卡名查詢 API | ✅ PASSED | 0.02 | - | - |
| TC-API-006 | P1 | API | 爬蟲清單與紀錄查詢 /api/scrapers & /api/scrape-logs | ✅ PASSED | 0.00 | - | - |
| TC-API-007 | P0 | API | 信用卡回饋試算排序與多卡組合 /api/recommend | ✅ PASSED | 0.00 | - | - |
| TC-API-008 | P2 | API | 零消費邊界輸入 /api/recommend 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-009 | P1 | API | 無低消門檻過濾參數 only_no_min_spend 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-API-010 | P1 | API | 爬蟲管理端點權限保護驗證 | ⏭️ SKIPPED | 0.00 | 目標站台未開啟管理員密碼或公開唯讀鎖定 | 環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN |
| TC-API-011 | P0 | i18n (EN) | 後端 API 英文語系 (?lang=en) 翻譯完整性 | ✅ PASSED | 0.02 | - | - |
| TC-UI-001 | P0 | Functional UI | 首頁初次載入預設套用 office 情境與推薦結果 | ✅ PASSED | 0.60 | - | - |
| TC-UI-002 | P1 | Functional UI | 情境範本切換：小資外食網購族 (office) | ✅ PASSED | 0.63 | - | - |
| TC-UI-003 | P1 | Functional UI | 情境範本切換：日本旅遊高消費族 (travel) | ✅ PASSED | 0.63 | - | - |
| TC-UI-004 | P1 | Functional UI | 情境範本切換：通勤超商日常族 (commuter) | ✅ PASSED | 0.62 | - | - |
| TC-UI-005 | P1 | Functional UI | 清空歸零按鈕重置消費金額與空白提示 | ✅ PASSED | 0.63 | - | - |
| TC-UI-006 | P0 | Functional UI | 手動輸入各通路金額並送出試算 | ✅ PASSED | 0.68 | - | - |
| TC-UI-007 | P1 | Functional UI | 勾選「僅顯示無低消門檻」即時重算 | ✅ PASSED | 0.61 | - | - |
| TC-UI-008 | P1 | Functional UI | 「各卡通路比較表」分頁渲染與高回饋標示 | ✅ PASSED | 0.63 | - | - |
| TC-UI-009 | P1 | Functional UI | 「Playwright 爬蟲中心」銀行與卡名連動下拉選單 | ✅ PASSED | 0.65 | - | - |
| TC-UI-010 | P2 | Responsive | 桌機版 (1440x900) 全分頁無水平捲軸溢位 | ✅ PASSED | 1.14 | - | - |
| TC-UI-011 | P2 | Responsive | 手機版 (390x844) 全分頁無水平捲軸溢位 | ✅ PASSED | 1.17 | - | - |
| TC-UI-012 | P1 | Functional UI | 每月通路消費輸入框字數上限 (7 位數) 與非數字過濾 | ✅ PASSED | 0.69 | - | - |
| TC-UI-013 | P1 | Functional UI | 條件說明截斷處顯示 more 超連結導向官網來源（含 EN 模式） | ✅ PASSED | 0.73 | - | - |
| TC-I18N-001 | P0 | Localization | 繁體中文 (zh-Hant) 語系標記與字串完整性檢查 | ✅ PASSED | 0.58 | - | - |
| TC-I18N-002 | P1 | Localization | 台幣格式 (NT$)、百分比與台北時區日期格式驗證 | ✅ PASSED | 0.58 | - | - |
| TC-I18N-003 | P1 | Localization | 瀏覽器語系 zh-TW 相容性與功能運作 | ✅ PASSED | 0.74 | - | - |
| TC-I18N-004 | P1 | Localization | 瀏覽器語系 en-US 相容性與功能運作 | ✅ PASSED | 0.72 | - | - |
| TC-I18N-005 | P1 | Localization | 瀏覽器語系 ja-JP 相容性與功能運作 | ✅ PASSED | 0.71 | - | - |
| TC-I18N-006 | P0 | i18n (EN) | 右上角繁中/EN 切換、全頁面英文翻譯、持久化與切回繁中 | ✅ PASSED | 2.56 | - | - |
| TC-I18N-007 | P1 | i18n (EN) | 網址參數 /?lang=en 直接進入英文介面驗證 | ✅ PASSED | 0.64 | - | - |
| TC-SYNC-001 | P0 | Official Sync | 網站比較表顯示回饋率與後端 /api/cards 資料一致性檢查 | ✅ PASSED | 0.78 | - | - |
| TC-SYNC-002 | P1 | Official Sync | 網站卡片回饋率與銀行官網實際公告比對（含官網連結有效性） | ❌ FAILED | 63.91 | 網站部分卡片顯示之回饋率或官網連結與實際銀行官網不符（含 404/錯誤頁與過時利率） | 資料同步與來源連結缺陷 (Outdated Seed Data / Broken Official URL) — 銀行官網已改版或停售/調降利率，但站內規則與 URL 未同步更新 |
| TC-MATH-001 | P0 | Math & Logic | 獨立演算法對拍：單卡各通路回饋與有效回饋率精算驗證 | ✅ PASSED | 0.01 | - | - |
| TC-MATH-002 | P0 | Math & Logic | 多卡組合最佳化分配與多賺金額 (gain_over_best_single) 驗證 | ✅ PASSED | 0.00 | - | - |
| TC-MATH-003 | P1 | Math & Logic | 月回饋上限溢額計算與低消門檻過濾邊界驗證 | ✅ PASSED | 0.01 | - | - |
| TC-MATH-004 | P1 | Math & Logic | 前端 UI 渲染金額與 /api/recommend API 回傳數值一致性驗證 | ✅ PASSED | 0.70 | - | - |
| TC-DATA-001 | P1 | Data Quality | 卡片規則資料健檢：排除爬蟲誤解析異常利率或月上限 | ✅ PASSED | 0.00 | - | - |

## 失敗 / 錯誤 / 略過原始細節

### TC-API-010 (P1) `tests/test_api.py::test_admin_scrape_endpoint_protected_when_configured` — SKIPPED

- **錯誤原因**：目標站台未開啟管理員密碼或公開唯讀鎖定
- **根本原因**：環境設定差異 (Environment Config) — 本機測試未設定 ADMIN_TOKEN
- **建議處理**：屬正常跳過；若需驗證權限防護，請設定 ADMIN_TOKEN 後再測。

```text
Target instance is running without admin_protected or public_readonly lock
```

### TC-SYNC-002 (P1) `tests/test_official_rate_sync.py::test_displayed_card_rates_match_official_bank_websites` — FAILED

- **錯誤原因**：網站部分卡片顯示之回饋率或官網連結與實際銀行官網不符（含 404/錯誤頁與過時利率）
- **根本原因**：資料同步與來源連結缺陷 (Outdated Seed Data / Broken Official URL) — 銀行官網已改版或停售/調降利率，但站內規則與 URL 未同步更新
- **建議處理**：更新失效之 official_url（如 fubon-j、ubot-jihe），並重爬或校正與官網不符之回饋率（如 taishin-gogo、sinopac-dawho、custom-richart）。

```text
tests/test_official_rate_sync.py:119: in test_displayed_card_rates_match_official_bank_websites
    assert not problems, " | ".join(problems)
E   AssertionError: Dead/broken official_url: fubon-j (HTTP=200, len=64, snippet='富邦金控 富邦金控 404 找不到頁面 找不到頁面 網址錯誤或頁面出現問題 富邦', url=https://www.fubon.com/banking/personal/credit_card/all_card/jcard/jcard.htm); ubot-jihe (HTTP=200, len=12, snippet='系統發生錯誤，請稍候再試', url=https://card.ubot.com.tw/eCard/Activity/jihe/) | Rate mismatch vs official bank page: taishin-gogo: site_rules=[3.0]% not found on official page (official_pcts=[0.0, 2.88, 3.5, 3.8, 15.0], url=https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/cg021/); sinopac-dawho: site_rules=[7.0]% not found on official page (official_pcts=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 15.0, 20.0], url=https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction/bankcard/DAWHO.html); custom-richart-73287a9a: site_rules=[3.8]% not found on official page (official_pcts=[0.0, 1.3, 2.88, 3.5, 3.88, 8.0, 10.0, 13.3, 15.0, 19.0], url=https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/cg047/card001/)
E   assert not ["Dead/broken official_url: fubon-j (HTTP=200, len=64, snippet='富邦金控 富邦金控 404 找不到頁面 找不到頁面 網址錯誤或頁面出現問題 富邦', url=https://www.fubon.com/banking/personal/credit_card/all_card/jcard/jcard.htm); ubot-jihe (HTTP=200, len=12, snippet='系統發生錯誤，請稍候再試', url=https://card.ubot.com.tw/eCard/Activity/jihe/)", 'Rate mismatch vs official bank page: taishin-gogo: site_rules=[3.0]% not found on official page (official_pcts=[0.0, 2.88, 3.5, 3.8, 15.0], url=https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/cg021/); sinopac-dawho: site_rules=[7.0]% not found on official page (official_pcts=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 15.0, 20.0], url=https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction/bankcard/DAWHO.html); custom-richart-73287a9a: site_rules=[3.8]% not found on official page (official_pcts=[0.0, 1.3, 2.88, 3.5, 3.88, 8.0, 10.0, 13.3, 15.0, 19.0], url=https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/cg047/card001/)']
```
