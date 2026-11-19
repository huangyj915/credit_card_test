from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reporting.catalog import TEST_CASE_CATALOG, lookup_test_meta
from reporting.classifier import classify_error_and_root_cause, enrich_results, extract_dev_issues
from reporting.excel_writer import update_history_summary_excel, write_excel_report
from reporting.html_writer import format_report_html
from reporting.markdown_writer import format_report_markdown

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


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
    html_text = format_report_html(
        started_at=started_at,
        finished_at=finished_at,
        base_url=base_url,
        require_en=require_en,
        results=results,
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
        (reports_dir / "index.html").write_text(html_text, encoding="utf-8")
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


__all__ = [
    "REPORTS_DIR",
    "TEST_CASE_CATALOG",
    "lookup_test_meta",
    "classify_error_and_root_cause",
    "enrich_results",
    "extract_dev_issues",
    "format_report_markdown",
    "format_report_html",
    "write_excel_report",
    "update_history_summary_excel",
    "write_all_run_reports",
]
