from __future__ import annotations

import re
from reporting.catalog import lookup_test_meta

SECRET_PATTERNS = [
    re.compile(r"(?i)(Bearer)\s+[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(X-Admin-Token|Authorization|Cookie|ADMIN_TOKEN)\s*[:=]\s*(?:Bearer\s+)?[^\s,'\";\]]+"),
]


def redact_secrets(text: str) -> str:
    """Mask sensitive headers or tokens before persisting details into reports."""
    out = text or ""
    for pat in SECRET_PATTERNS:
        out = pat.sub(lambda m: f"{m.group(1)}=[REDACTED]", out)
    return out


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
        if "English (en) i18n is not yet active" in text or "尚未部署英語" in text or "lang=en" in text:
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
            "error_reason": "瀏覽器主控台出現靜態資源 404 錯誤",
            "root_cause": "站台靜態資源缺失 (Missing Static Asset)",
            "suggested_action": "檢查缺失之靜態資源路徑或補齊檔案。",
            "issue_key": "ISS-STATIC-404",
            "issue_owner": "開發端 (Frontend/FastAPI)",
            "issue_component": "靜態資源",
            "issue_title": "頁面載入時出現靜態資源 404 錯誤",
            "issue_actual_vs_expected": "實際：Console 印出 404 Failed to load resource；預期：所有預設請求皆為 2xx/3xx。",
            "issue_fix_guide": "檢查 Network 404 URL 並補上對應檔案或修正引用路徑。",
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
            "root_cause": "產品 i18n 缺漏 (Unlocalized DB Scrape Logs)",
            "suggested_action": "於 /api/scrape-logs?lang=en 依語系格式化或翻譯歷史紀錄訊息。",
            "issue_key": "ISS-I18N-SCRAPE-LOGS",
            "issue_owner": "開發端 (Backend API / SQLite)",
            "issue_component": "GET /api/scrape-logs?lang=en & #scrapeLogs",
            "issue_title": "英文模式 (?lang=en) 下「最近爬取紀錄」仍顯示中文歷史訊息",
            "issue_actual_vs_expected": "實際：#scrapeLogs 顯示中文日誌；預期：英文模式下顯示英文日誌。",
            "issue_fix_guide": "於 /api/scrape-logs?lang=en 針對既有中文日誌模板進行英文格式化與卡名替換。",
        }

    if "Untranslated CJK lines in Recommend tab" in text or "Untranslated card_name" in text:
        return {
            "error_reason": "英文模式下 /api/cards?lang=en 與推薦清單仍含未翻譯中文卡名或規則說明",
            "root_cause": "產品 i18n 缺漏 (Missing Backend/DB Card & Rule Translation)",
            "suggested_action": "補齊卡片名稱與爬蟲規則 note 之英文翻譯。",
            "issue_key": "ISS-I18N-CARD-RULES",
            "issue_owner": "開發端 (Backend API / i18n)",
            "issue_component": "GET /api/cards?lang=en & POST /api/recommend?lang=en",
            "issue_title": "英文語系 API 與推薦明細仍混有未翻譯中文卡名與規則 note",
            "issue_actual_vs_expected": "實際：lang=en 回傳資料含中文；預期：lang=en 下皆為英文。",
            "issue_fix_guide": "將未對照到的卡名與 scraped 規則 note 補入英文翻譯字典或 i18n 轉換邏輯。",
        }

    if "scraper-parsed rule anomalies" in text or "unrealistic rate=" in text or "monthly_cap_ntd=" in text:
        return {
            "error_reason": "卡片規則庫含爬蟲誤解析之異常利率 (>15%) 或月上限（如 3.0 / 1.0 / 年份 2024.0）",
            "root_cause": "資料與爬蟲解析缺陷 (Scraper Parsing Artifact)",
            "suggested_action": "修正爬蟲規則擷取正規式並清理 SQLite 既有異常規則。",
            "issue_key": "ISS-DATA-SCRAPER-RULES",
            "issue_owner": "開發端 (Scraper / DB Data)",
            "issue_component": "SQLite card_rules & Playwright 爬蟲解析器",
            "issue_title": "爬蟲解析出異常回饋率 (>15%) 或異常月上限導致推薦排名失真",
            "issue_actual_vs_expected": "實際：規則含異常高 % 或過低/年份上限；預期：利率與上限符合真實卡片權益。",
            "issue_fix_guide": "強化爬蟲對「最高 X%」與「上限 N 元」的邊界判斷並重爬異常規則。",
        }

    if "Dead/broken official_url" in text or "Rate mismatch vs official bank page" in text:
        return {
            "error_reason": "網站部分卡片顯示之回饋率或官網連結與實際銀行官網不符（含 404/錯誤頁與過時利率）",
            "root_cause": "資料同步與來源連結缺陷 (Outdated Seed Data / Broken Official URL)",
            "suggested_action": "更新失效之 official_url，並重爬或校正與官網不符之回饋率。",
            "issue_key": "ISS-DATA-OFFICIAL-SYNC",
            "issue_owner": "開發端 (Seed Data / Scraper)",
            "issue_component": "SQLite cards.official_url & card_rules.rate",
            "issue_title": "網站顯示回饋率或官網來源連結與銀行官網現況不吻合",
            "issue_actual_vs_expected": next((ln.strip() for ln in text.splitlines() if ln.strip().startswith("E ")), "官網連結失效或利率與官網不符"),
            "issue_fix_guide": "1) 修正 404/錯誤之 official_url；2) 依銀行官網最新公告更新過時回饋率並定期排程重爬。",
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
        safe_detail = redact_secrets(r.get("detail", ""))
        meta = lookup_test_meta(r["nodeid"])
        info = classify_error_and_root_cause(
            r["nodeid"], r["status"], safe_detail
        )
        enriched.append(
            {
                **r,
                "detail": safe_detail,
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
