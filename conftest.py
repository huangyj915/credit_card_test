from __future__ import annotations

import os
import re
from datetime import datetime
from urllib.parse import urlparse
import pytest
from playwright.sync_api import sync_playwright

from reporting import REPORTS_DIR, write_all_run_reports

DEFAULT_BASE_URL = "https://cards.zillurl.com"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=os.environ.get("BASE_URL", DEFAULT_BASE_URL),
        help=f"Target site base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.addoption(
        "--require-en",
        action="store_true",
        default=os.environ.get("REQUIRE_EN_I18N", "").lower() in {"1", "true", "yes"},
        help="Fail instead of skip if English (en) i18n is not yet available on the target site.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Google Chrome in headed (visible) mode.",
    )
    parser.addoption(
        "--no-report",
        action="store_true",
        default=False,
        help="Disable automatic Markdown, HTML, and Excel test report generation under reports/.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config._report_state = {
        "started_at": datetime.now(),
        "results": [],
    }


def _safe_artifact_stem(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid).strip("_")[:120]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        setattr(item, "_call_failed", rep.failed)

    state = getattr(item.config, "_report_state", None)
    if state is None:
        return

    should_record = (
        rep.when == "call"
        or (rep.when == "setup" and rep.outcome in {"failed", "skipped"})
        or (rep.when == "teardown" and rep.outcome == "failed")
    )
    if not should_record:
        return

    status = rep.outcome.upper()
    if rep.when in {"setup", "teardown"} and rep.outcome == "failed":
        status = "ERROR"

    detail = ""
    if rep.skipped:
        if isinstance(rep.longrepr, tuple) and len(rep.longrepr) >= 3:
            detail = str(rep.longrepr[2]).replace("Skipped: ", "", 1)
        else:
            detail = str(rep.longrepr or "")
    elif rep.failed:
        detail = str(rep.longreprtext or rep.longrepr or "")

    existing = next((r for r in state["results"] if r["nodeid"] == item.nodeid), None)
    entry = {
        "nodeid": item.nodeid,
        "when": rep.when,
        "status": status,
        "duration": round(rep.duration, 2),
        "detail": detail.strip(),
    }
    if existing and status == "ERROR":
        existing.update(entry)
    elif not existing:
        state["results"].append(entry)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if session.config.getoption("--no-report") or session.config.getoption("--collect-only"):
        return
    state = getattr(session.config, "_report_state", None)
    if not state or not state["results"]:
        return

    finished_at = datetime.now()
    base_url = str(session.config.getoption("--base-url")).rstrip("/")
    require_en = bool(session.config.getoption("--require-en"))

    md_path, xlsx_path, history_path = write_all_run_reports(
        started_at=state["started_at"],
        finished_at=finished_at,
        base_url=base_url,
        require_en=require_en,
        results=state["results"],
    )

    tw = session.config.pluginmanager.get_plugin("terminalreporter")
    if tw is not None:
        tw.write_sep("-", f"測試報告已產出: {xlsx_path} | {md_path} | 歷史彙總: {history_path}")


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("--base-url")).rstrip("/")


@pytest.fixture(scope="session")
def require_en(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--require-en"))


@pytest.fixture(scope="session")
def browser(request: pytest.FixtureRequest):
    headed = bool(request.config.getoption("--headed"))
    launch_args = ["--disable-dev-shm-usage"]
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="chrome", headless=not headed, args=launch_args)
        except Exception:
            b = p.chromium.launch(headless=not headed, args=launch_args)
        yield b
        b.close()


def assert_no_runtime_errors(errors: dict[str, list[str]], *, allow_server_errors: bool = False) -> None:
    assert not errors["pageerrors"], f"Uncaught page errors: {errors['pageerrors']}"
    if not allow_server_errors:
        assert not errors["server_errors"], f"Target 5xx responses: {errors['server_errors']}"
    assert not errors["console_errors"], f"Browser console errors: {errors['console_errors']}"


@pytest.fixture
def make_page(browser, base_url: str, request: pytest.FixtureRequest):
    """Factory fixture creating isolated Playwright contexts/pages with tracing & failure artifacts."""
    created = []
    target_host = urlparse(base_url).netloc
    artifacts_dir = REPORTS_DIR / "artifacts"

    def _create(
        *,
        locale: str = "zh-TW",
        accept_language: str | None = None,
        viewport: dict[str, int] | None = None,
        allow_server_errors: bool = False,
    ):
        headers = {}
        if accept_language:
            headers["Accept-Language"] = accept_language

        context = browser.new_context(
            locale=locale,
            viewport=viewport or {"width": 1440, "height": 900},
            extra_http_headers=headers,
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        page.set_default_timeout(15000)

        errors = {
            "pageerrors": [],
            "console_errors": [],
            "server_errors": [],
            "non_favicon_404s": [],
        }

        def _on_response(resp) -> None:
            parsed = urlparse(resp.url)
            if parsed.netloc != target_host:
                return
            if resp.status >= 500:
                errors["server_errors"].append(f"{resp.status} {resp.url}")
            elif resp.status == 404 and not parsed.path.endswith("/favicon.ico"):
                errors["non_favicon_404s"].append(f"404 {resp.url}")

        def _on_console(msg) -> None:
            if msg.type != "error":
                return
            # Only ignore benign browser /favicon.ico 404 noise; keep all other 404s
            if "status of 404" in msg.text and not errors["non_favicon_404s"]:
                loc_url = (msg.location or {}).get("url", "")
                if not loc_url or loc_url.endswith("/favicon.ico"):
                    return
            if allow_server_errors and "status of 500" in msg.text:
                return
            errors["console_errors"].append(msg.text)

        page.on("pageerror", lambda err: errors["pageerrors"].append(str(err)))
        page.on("response", _on_response)
        page.on("console", _on_console)

        created.append((context, page, errors, allow_server_errors))
        return page, errors

    yield _create

    failed = bool(getattr(request.node, "_call_failed", False))
    stem = _safe_artifact_stem(request.node.nodeid)

    for idx, (context, pg, _, _) in enumerate(created):
        suffix = f"-{idx}" if len(created) > 1 else ""
        try:
            if failed:
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                try:
                    pg.screenshot(path=str(artifacts_dir / f"{stem}{suffix}.png"), full_page=True)
                except Exception:
                    pass
                context.tracing.stop(path=str(artifacts_dir / f"{stem}{suffix}-trace.zip"))
            else:
                context.tracing.stop()
        finally:
            context.close()


@pytest.fixture
def page(make_page):
    """Default zh-TW desktop page with runtime error tracking."""
    pg, errors = make_page(locale="zh-TW")
    pg._runtime_errors = errors
    yield pg
    assert_no_runtime_errors(errors)
