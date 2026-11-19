from __future__ import annotations

import os
from datetime import datetime
from urllib.parse import urlparse
import pytest
from playwright.sync_api import sync_playwright

from reporting import write_all_run_reports

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
        help="Disable automatic Markdown and Excel test report generation under reports/.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config._report_state = {
        "started_at": datetime.now(),
        "results": [],
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()
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
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="chrome", headless=not headed)
        except Exception:
            b = p.chromium.launch(headless=not headed)
        yield b
        b.close()


@pytest.fixture
def make_page(browser, base_url: str):
    """Factory fixture creating isolated Playwright contexts/pages with error tracking."""
    created = []
    target_host = urlparse(base_url).netloc

    def _create(
        *,
        locale: str = "zh-TW",
        accept_language: str | None = None,
        viewport: dict[str, int] | None = None,
    ):
        headers = {}
        if accept_language:
            headers["Accept-Language"] = accept_language

        context = browser.new_context(
            locale=locale,
            viewport=viewport or {"width": 1440, "height": 900},
            extra_http_headers=headers,
        )
        page = context.new_page()
        page.set_default_timeout(15000)

        errors = {
            "pageerrors": [],
            "console_errors": [],
            "server_errors": [],
        }

        page.on("pageerror", lambda err: errors["pageerrors"].append(str(err)))
        page.on(
            "console",
            lambda msg: errors["console_errors"].append(msg.text)
            if msg.type == "error"
            and "status of 404" not in msg.text
            else None,
        )
        page.on(
            "response",
            lambda resp: errors["server_errors"].append(f"{resp.status} {resp.url}")
            if resp.status >= 500 and urlparse(resp.url).netloc == target_host
            else None,
        )

        created.append((context, errors))
        return page, errors

    yield _create

    for context, _ in created:
        context.close()


@pytest.fixture
def page(make_page):
    """Default zh-TW desktop page; asserts no uncaught JS or 5xx errors after test."""
    pg, errors = make_page(locale="zh-TW")
    yield pg
    assert not errors["pageerrors"], f"Uncaught page errors: {errors['pageerrors']}"
    assert not errors["server_errors"], f"Target 5xx responses: {errors['server_errors']}"
    assert not errors["console_errors"], f"Browser console errors: {errors['console_errors']}"
