# 自動化測試報告 (2026-11-20 08:11:12)

## 測試摘要

- **結果**：`FAIL`
- **目標網址**：`http://127.0.0.1:8000`
- **強制英語 i18n (`--require-en`)**：`False`
- **測試時間**：2026-11-20 08:11:12 ~ 08:11:46（總耗時 33.47s）
- **測試總數**：2 項｜✅ Passed: 1｜❌ Failed: 1｜⚠️ Error: 0｜⏭️ Skipped: 0

## 待修復 Issue 清單（開發端 Action Items）

| Issue ID | Priority | 負責端 | Fail Rate | 問題項目 (What to Fix) | 影響位置 | 根本原因 | 修復建議 | 關聯 TC |
|---|---|---|---|---|---|---|---|---|
| ISSUE-001 | P1 | 開發端 (待確認) | 1/2 (50.0%) | test_displayed_card_rates_match_official_bank_websites 執行失敗 | `tests/test_official_rate_sync.py` | 功能或資料預期不符 (Assertion / Runtime Failure) | 請開發端依錯誤訊息與測試步驟重現排查。 | TC-SYNC-002 |

## Priority 分級統計

| Priority | 總數 | Passed | Failed | Error | Skipped |
|---|---:|---:|---:|---:|---:|
| P0 | 1 | 1 | 0 | 0 | 0 |
| P1 | 1 | 0 | 1 | 0 | 0 |
| P2 | 0 | 0 | 0 | 0 | 0 |

## Test Case 明細

| TC ID | Priority | 分類 | 測試案例名稱 | 結果 | 耗時 (s) | 錯誤原因 | 根本原因 |
|---|---|---|---|---|---:|---|---|
| TC-SYNC-001 | P0 | Official Sync | 網站比較表顯示回饋率與後端 /api/cards 資料一致性檢查 | ✅ PASSED | 1.17 | - | - |
| TC-SYNC-002 | P1 | Official Sync | 網站卡片回饋率與銀行官網實際公告比對（含官網連結有效性） | ❌ FAILED | 30.66 | E   AssertionError: Unreachable/no-rate official pages: ubot-jihe (no % extracted on https://card.ubot.com.tw/CardDetail/cardDetail202) | 功能或資料預期不符 (Assertion / Runtime Failure) |

## 失敗 / 錯誤 / 略過原始細節

### TC-SYNC-002 (P1) `tests/test_official_rate_sync.py::test_displayed_card_rates_match_official_bank_websites` — FAILED

- **錯誤原因**：E   AssertionError: Unreachable/no-rate official pages: ubot-jihe (no % extracted on https://card.ubot.com.tw/CardDetail/cardDetail202)
- **根本原因**：功能或資料預期不符 (Assertion / Runtime Failure)
- **建議處理**：檢視詳細錯誤堆疊並確認實際行為與規格。

```text
tests/test_official_rate_sync.py:180: in test_displayed_card_rates_match_official_bank_websites
    assert not problems, " | ".join(problems)
E   AssertionError: Unreachable/no-rate official pages: ubot-jihe (no % extracted on https://card.ubot.com.tw/CardDetail/cardDetail202)
E   assert not ['Unreachable/no-rate official pages: ubot-jihe (no % extracted on https://card.ubot.com.tw/CardDetail/cardDetail202)']
```
