from __future__ import annotations

import json
import re
from urllib.parse import urlparse
import pytest
from playwright.sync_api import Page, expect


def _is_recommend_post(r) -> bool:
    return urlparse(r.url).path == "/api/recommend" and r.request.method == "POST"


def _is_bank_cards_get(r) -> bool:
    path = urlparse(r.url).path
    return "/api/banks/" in path and path.endswith("/cards")


@pytest.mark.functional
def test_initial_load_applies_default_office_preset(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    expect(page.locator(".channel-input")).to_have_count(10)
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 26,000")

    cards = page.locator("#recommendList .card-result")
    assert cards.count() >= 1
    expect(cards.first).to_have_class(re.compile(r"top-rank"))

    # Rank 1 breakdown details should be expanded by default
    expect(cards.first.locator("details")).to_have_attribute("open", "")
    expect(page.locator("#comboSection")).not_to_have_class(re.compile(r"\bhidden\b"))


@pytest.mark.functional
@pytest.mark.parametrize(
    ("preset_key", "expected_total"),
    [
        ("office", "NT$ 26,000"),
        ("travel", "NT$ 58,000"),
        ("commuter", "NT$ 27,000"),
    ],
)
def test_presets_update_inputs_and_recommendations(
    page: Page,
    base_url: str,
    preset_key: str,
    expected_total: str,
) -> None:
    page.goto(base_url, wait_until="networkidle")

    with page.expect_response(_is_recommend_post) as resp_info:
        page.locator(f'.chip[data-preset="{preset_key}"]').click()

    assert resp_info.value.status == 200
    expect(page.locator("#totalSpendDisplay")).to_have_text(expected_total)
    assert page.locator("#recommendList .card-result").count() >= 1


@pytest.mark.functional
def test_clear_inputs_resets_total_and_shows_empty_state(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    with page.expect_response(_is_recommend_post):
        page.locator("#clearInputsBtn").click()

    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 0")
    expect(page.locator("#comboSection")).to_have_class(re.compile(r"\bhidden\b"))
    expect(page.locator("#recommendList .empty-state")).to_be_visible()

    values = page.locator(".channel-input").evaluate_all(
        "els => els.map(e => Number(e.value))"
    )
    assert all(v == 0 for v in values)


@pytest.mark.functional
def test_manual_spending_submission_and_breakdown(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    with page.expect_response(_is_recommend_post):
        page.locator("#clearInputsBtn").click()
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 0")
    expect(page.locator("#recommendList .empty-state")).to_be_visible()

    page.locator('.channel-input[data-code="dining"]').fill("8000")
    page.locator('.channel-input[data-code="overseas"]').fill("12000")
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 20,000")

    with page.expect_response(_is_recommend_post) as resp_info:
        page.locator('#spendingForm button[type="submit"]').click()

    req_body = json.loads(resp_info.value.request.post_data or "{}")
    assert req_body["monthly_spending"] == {"dining": 8000, "overseas": 12000}

    top_card = page.locator("#recommendList .card-result").first
    expect(top_card).to_be_visible()
    expect(top_card.locator(".breakdown-table tbody tr")).to_have_count(2)


@pytest.mark.functional
def test_only_no_min_spend_checkbox_sends_flag(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    checkbox = page.locator("#onlyNoMinSpend")
    expect(checkbox).not_to_be_checked()

    with page.expect_response(_is_recommend_post) as resp_info:
        checkbox.check()

    req_body = json.loads(resp_info.value.request.post_data or "{}")
    assert req_body["only_no_min_spend"] is True
    assert resp_info.value.status == 200
    assert page.locator("#recommendList .card-result").count() >= 1


@pytest.mark.functional
def test_matrix_tab_renders_cards_and_channels(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    page.locator('.tab-btn[data-tab="matrix"]').click()
    expect(page.locator("#tab-matrix")).to_have_class(re.compile(r"\bactive\b"))

    headers = page.locator("#matrixTable thead th")
    # 1 card column + 10 channel columns
    expect(headers).to_have_count(11)

    rows = page.locator("#matrixTable tbody tr")
    assert rows.count() >= 1
    assert page.locator("#matrixTable td.rate-high").count() >= 1


@pytest.mark.functional
def test_scraper_tab_controls_and_cascading_bank_cards(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    page.locator('.tab-btn[data-tab="scraper"]').click()
    expect(page.locator("#tab-scraper")).to_have_class(re.compile(r"\bactive\b"))

    # Scraper checkboxes and scrape mode radios
    assert page.locator("#scraperBanks .scraper-check").count() >= 1
    expect(page.locator('input[name="scrapeMode"][value="demo_html"]')).to_be_checked()

    # Cascading bank -> card dropdown populates card name & official URL
    bank_select = page.locator("#customBankSelect")
    card_select = page.locator("#customCardSelect")
    expect(card_select).to_be_disabled()

    with page.expect_response(_is_bank_cards_get):
        bank_select.select_option(index=1)

    expect(card_select).to_be_enabled()
    card_select.select_option(index=1)
    assert page.locator("#customCardName").input_value().strip() != ""

    # Selecting "__other__" reveals manual bank input
    bank_select.select_option("__other__")
    expect(page.locator("#customBankManualWrap")).not_to_have_class(re.compile(r"\bhidden\b"))
    expect(card_select).to_be_disabled()


@pytest.mark.functional
@pytest.mark.responsive
@pytest.mark.parametrize(
    "viewport",
    [
        {"width": 1440, "height": 900},
        {"width": 390, "height": 844},
    ],
)
def test_no_horizontal_overflow_across_tabs(
    make_page,
    base_url: str,
    viewport: dict[str, int],
) -> None:
    pg, errors = make_page(locale="zh-TW", viewport=viewport)
    pg.goto(base_url, wait_until="networkidle")

    for tab in ("recommend", "matrix", "scraper"):
        pg.locator(f'.tab-btn[data-tab="{tab}"]').click()
        pg.wait_for_timeout(150)
        overflow = pg.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        assert overflow <= 1, f"Horizontal overflow of {overflow}px on tab={tab}, viewport={viewport}"

    assert not errors["pageerrors"]
    assert not errors["server_errors"]


@pytest.mark.functional
@pytest.mark.pending_app_push
def test_channel_input_enforces_digit_limit_and_blocks_non_numeric(
    page: Page, base_url: str
) -> None:
    page.goto(base_url, wait_until="networkidle")

    inputs = page.locator(".channel-input")
    count = inputs.count()
    assert count == 10
    for idx in range(count):
        expect(inputs.nth(idx)).to_have_attribute("maxlength", "7")
        expect(inputs.nth(idx)).to_have_attribute("max", "9999999")

    with page.expect_response(_is_recommend_post):
        page.locator("#clearInputsBtn").click()
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 0")

    dining = page.locator('.channel-input[data-code="dining"]')
    dining.click()
    dining.fill("")
    dining.type("1234567890")
    expect(dining).to_have_value("1234567")
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 1,234,567")

    # Non-numeric keys like e, +, -, . should be blocked / sanitized
    dining.fill("")
    dining.type("50e+-1.2")
    expect(dining).to_have_value("5012")
    expect(page.locator("#totalSpendDisplay")).to_have_text("NT$ 5,012")


@pytest.mark.functional
@pytest.mark.pending_app_push
def test_truncated_condition_note_renders_more_link_to_source(
    page: Page, base_url: str
) -> None:
    page.goto(base_url, wait_until="networkidle")

    with page.expect_response(_is_recommend_post):
        page.locator('.chip[data-preset="travel"]').click()

    # Expand all card breakdown details so truncated notes across cards are visible
    page.locator("#recommendList details:not([open]) summary").evaluate_all(
        "els => els.forEach(el => el.click())"
    )

    more_links = page.locator("#recommendList a.note-more-link")
    assert more_links.count() >= 1, "Expected at least one truncated condition note with a 'more' link"

    first_link = more_links.first
    expect(first_link).to_be_visible()
    expect(first_link).to_have_text("more")
    expect(first_link).to_have_attribute("target", "_blank")
    expect(first_link).to_have_attribute("rel", re.compile(r"noopener"))
    href = first_link.get_attribute("href") or ""
    assert href.startswith("http"), f"Expected valid source URL on more link, got {href!r}"

    # Verify preceding span has truncated text ending with ellipsis and longer full title tooltip
    td_info = first_link.evaluate(
        """el => {
            const span = el.previousElementSibling;
            return {
                display: span ? span.textContent : '',
                title: span ? (span.getAttribute('title') || '') : ''
            };
        }"""
    )
    assert td_info["display"].endswith("…") or td_info["display"].endswith("..."), (
        f"Expected truncated note to end with ellipsis, got {td_info['display']!r}"
    )
    assert len(td_info["title"]) >= len(td_info["display"]), (
        f"Expected full tooltip title >= displayed truncated text: {td_info}"
    )

    # Also verify 'more' link still works properly after switching to English
    en_btn = page.locator('.lang-btn[data-lang="en"]')
    if en_btn.count() > 0:
        with page.expect_response(_is_recommend_post):
            en_btn.click()
        page.locator("#recommendList details:not([open]) summary").evaluate_all(
            "els => els.forEach(el => el.click())"
        )
        en_links = page.locator("#recommendList a.note-more-link")
        assert en_links.count() >= 1
        expect(en_links.first).to_have_text("more")
        assert (en_links.first.get_attribute("href") or "").startswith("http")
