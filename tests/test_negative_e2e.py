from __future__ import annotations

import json
import re
import pytest
from playwright.sync_api import expect

from conftest import assert_no_runtime_errors
from pages import HomePage, ScraperTab, is_recommend_post


@pytest.mark.negative
@pytest.mark.functional
def test_recommend_api_500_error_recovery(make_page, base_url: str) -> None:
    """Mock /api/recommend returning HTTP 500, verify graceful handling and recovery on retry."""
    pg, errors = make_page(locale="zh-TW", allow_server_errors=True)
    home = HomePage(pg)
    home.goto_and_wait_ready(base_url)

    fail_once = {"triggered": False}

    def _intercept_recommend(route):
        if not fail_once["triggered"]:
            fail_once["triggered"] = True
            route.fulfill(
                status=500,
                content_type="application/json",
                body=json.dumps({"detail": "Simulated server error"}),
            )
        else:
            route.continue_()

    pg.route("**/api/recommend*", _intercept_recommend)

    # First submit hits mocked 500; submit button must remain enabled and page must not crash
    with pg.expect_response(is_recommend_post) as err_resp:
        home.submit_btn.click()
    assert err_resp.value.status == 500
    expect(home.submit_btn).to_be_enabled()

    # Second submit recovers cleanly with HTTP 200
    ok_resp = home.submit_spending()
    assert ok_resp.status == 200
    expect(home.recommend_cards.first).to_be_visible()

    assert_no_runtime_errors(errors, allow_server_errors=True)


@pytest.mark.negative
@pytest.mark.functional
def test_public_readonly_locks_scraper_controls(make_page, base_url: str) -> None:
    """Mock /api/config with public_readonly=true, verify docs hidden and scraper buttons locked."""
    pg, errors = make_page(locale="zh-TW")

    pg.route(
        "**/api/config*",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "admin_protected": False,
                    "public_readonly": True,
                    "docs_enabled": False,
                }
            ),
        ),
    )

    home = HomePage(pg)
    scraper = ScraperTab(pg)
    home.goto_and_wait_ready(base_url)

    expect(home.docs_link).to_be_hidden()

    home.switch_tab("scraper")
    expect(scraper.auth_bar).not_to_have_class(re.compile(r"\bhidden\b"))
    expect(scraper.run_scrape_btn).to_be_disabled()
    expect(scraper.run_custom_scrape_btn).to_be_disabled()
    expect(scraper.discover_cards_btn).to_be_disabled()

    assert_no_runtime_errors(errors)


@pytest.mark.negative
@pytest.mark.functional
def test_scraper_demo_closed_loop_refreshes_ui(make_page, base_url: str) -> None:
    """Mock POST /api/scrape to verify closed-loop UI refresh without mutating backend DB."""
    pg, errors = make_page(locale="zh-TW")

    # Ensure scraper button is unlocked in this test regardless of server admin_protected setting
    pg.route(
        "**/api/config*",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "admin_protected": False,
                    "public_readonly": False,
                    "docs_enabled": True,
                }
            ),
        ),
    )

    pg.route(
        "**/api/scrape*",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "results": [
                        {
                            "bank_code": "cathay",
                            "card_slug": "cathay-cube",
                            "status": "success",
                            "message": "Mocked Playwright demo_html scrape succeeded",
                            "url": "https://www.cathaybk.com.tw/",
                        }
                    ]
                }
            ),
        )
        if route.request.method == "POST"
        else route.continue_(),
    )

    home = HomePage(pg)
    scraper = ScraperTab(pg)
    home.goto_and_wait_ready(base_url)
    home.switch_tab("scraper")

    with pg.expect_response(is_recommend_post):
        scraper.run_scrape_btn.click()

    expect(scraper.scrape_results).to_contain_text("Mocked Playwright demo_html scrape succeeded")
    expect(scraper.run_scrape_btn).to_be_enabled()

    assert_no_runtime_errors(errors)
