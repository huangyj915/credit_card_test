from __future__ import annotations

from datetime import datetime
from reporting.classifier import enrich_results, extract_dev_issues


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
