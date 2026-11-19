from __future__ import annotations

import html
from datetime import datetime
from reporting.classifier import enrich_results, extract_dev_issues


def format_report_html(
    *,
    started_at: datetime,
    finished_at: datetime,
    base_url: str,
    require_en: bool,
    results: list[dict],
) -> str:
    """Generate a self-contained HTML dashboard suitable for GitHub Pages."""
    enriched = enrich_results(results)
    issues = extract_dev_issues(enriched)
    elapsed = max((finished_at - started_at).total_seconds(), 0.0)
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for r in enriched:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    total = len(enriched)
    err_count = counts["FAILED"] + counts["ERROR"]
    overall = "PASS" if err_count == 0 else "FAIL"
    badge_cls = "badge-pass" if overall == "PASS" else "badge-fail"

    e = html.escape

    prio_rows = []
    for prio in ("P0", "P1", "P2"):
        sub = [r for r in enriched if r["priority"] == prio]
        p_pass = sum(1 for r in sub if r["status"] == "PASSED")
        p_fail = sum(1 for r in sub if r["status"] == "FAILED")
        p_err = sum(1 for r in sub if r["status"] == "ERROR")
        p_skip = sum(1 for r in sub if r["status"] == "SKIPPED")
        prio_rows.append(
            f"<tr><td><span class='pill prio-{prio.lower()}'>{prio}</span></td>"
            f"<td>{len(sub)}</td><td>{p_pass}</td><td>{p_fail}</td><td>{p_err}</td><td>{p_skip}</td></tr>"
        )

    if not issues:
        issues_html = "<p class='ok-box'>✅ 本次測試無待修復 Issue！(0 Open Issues)</p>"
    else:
        iss_rows = "".join(
            f"<tr><td>{e(iss['issue_no'])}</td>"
            f"<td><span class='pill prio-{iss['priority'].lower()}'>{e(iss['priority'])}</span></td>"
            f"<td>{e(iss['owner'])}</td>"
            f"<td><span class='pill st-failed'>{e(iss['fail_rate'])}</span></td>"
            f"<td><strong>{e(iss['title'])}</strong><br><small>{e(iss['component'])}</small></td>"
            f"<td>{e(iss['root_cause'])}</td>"
            f"<td>{e(iss['fix_guide'])}</td>"
            f"<td><code>{e(iss['tc_ids_str'])}</code></td></tr>"
            for iss in issues
        )
        issues_html = (
            "<table><thead><tr><th>Issue ID</th><th>Priority</th><th>Owner</th><th>Fail Rate</th>"
            "<th>What to Fix</th><th>Root Cause</th><th>Fix Guide</th><th>TC IDs</th></tr></thead>"
            f"<tbody>{iss_rows}</tbody></table>"
        )

    tc_rows = "".join(
        f"<tr><td><code>{e(r['tc_id'])}</code></td>"
        f"<td><span class='pill prio-{r['priority'].lower()}'>{e(r['priority'])}</span></td>"
        f"<td>{e(r['category'])}</td>"
        f"<td>{e(r['title'])}</td>"
        f"<td><span class='pill st-{r['status'].lower()}'>{e(r['status'])}</span></td>"
        f"<td>{r['duration']:.2f}s</td>"
        f"<td>{e(r['error_reason'])}</td></tr>"
        for r in enriched
    )

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Credit Card E2E &amp; i18n Test Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }}
    .badge {{ padding: 6px 14px; border-radius: 999px; font-weight: 700; font-size: 14px; }}
    .badge-pass {{ background: #dcfce7; color: #166534; }}
    .badge-fail {{ background: #fee2e2; color: #991b1b; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 20px; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; }}
    .card .k {{ font-size: 12px; color: #64748b; }}
    .card .v {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
    .panel {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 20px; overflow-x: auto; }}
    .downloads a {{ display: inline-block; margin-right: 10px; padding: 6px 12px; background: #1e293b; color: #fff; text-decoration: none; border-radius: 6px; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; font-weight: 600; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; }}
    .prio-p0 {{ background: #fee2e2; color: #991b1b; }}
    .prio-p1 {{ background: #fef3c7; color: #92400e; }}
    .prio-p2 {{ background: #e0f2fe; color: #075985; }}
    .st-passed {{ background: #dcfce7; color: #166534; }}
    .st-failed {{ background: #fee2e2; color: #991b1b; }}
    .st-error {{ background: #fef3c7; color: #92400e; }}
    .st-skipped {{ background: #f1f5f9; color: #475569; }}
    .ok-box {{ background: #dcfce7; color: #166534; padding: 12px 14px; border-radius: 8px; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1 style="margin:0 0 6px;">Credit Card Recommender — Automated Test Report</h1>
        <div style="font-size:13px;color:#475569;">
          Target: <code>{e(base_url)}</code> | Executed: {started_at.strftime('%Y-%m-%d %H:%M:%S')} ({elapsed:.2f}s) | <code>--require-en={require_en}</code>
        </div>
      </div>
      <span class="badge {badge_cls}">{overall}</span>
    </header>

    <div class="downloads" style="margin-bottom:16px;">
      <a href="latest.xlsx">Download latest.xlsx</a>
      <a href="test-history-summary.xlsx">Download History Excel</a>
      <a href="latest.md">View latest.md</a>
    </div>

    <div class="cards">
      <div class="card"><div class="k">Total</div><div class="v">{total}</div></div>
      <div class="card"><div class="k">Passed</div><div class="v" style="color:#166534;">{counts['PASSED']}</div></div>
      <div class="card"><div class="k">Failed</div><div class="v" style="color:#991b1b;">{counts['FAILED']}</div></div>
      <div class="card"><div class="k">Error</div><div class="v" style="color:#92400e;">{counts['ERROR']}</div></div>
      <div class="card"><div class="k">Skipped</div><div class="v" style="color:#475569;">{counts['SKIPPED']}</div></div>
    </div>

    <div class="panel">
      <h2 style="margin-top:0;">Open Dev Issues</h2>
      {issues_html}
    </div>

    <div class="panel">
      <h2 style="margin-top:0;">Breakdown by Priority</h2>
      <table>
        <thead><tr><th>Priority</th><th>Total</th><th>Passed</th><th>Failed</th><th>Error</th><th>Skipped</th></tr></thead>
        <tbody>{"".join(prio_rows)}</tbody>
      </table>
    </div>

    <div class="panel">
      <h2 style="margin-top:0;">Test Cases ({total})</h2>
      <table>
        <thead><tr><th>TC ID</th><th>Priority</th><th>Category</th><th>Title</th><th>Status</th><th>Duration</th><th>Error Reason</th></tr></thead>
        <tbody>{tc_rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
