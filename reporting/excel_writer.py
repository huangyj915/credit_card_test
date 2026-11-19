from __future__ import annotations

from datetime import datetime
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from reporting.classifier import enrich_results, extract_dev_issues


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

    # --- Sheet 2: Issues ---
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
