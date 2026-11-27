from __future__ import annotations

import json
import re
import pytest
from playwright.sync_api import Page, expect

from conftest import assert_no_runtime_errors
from pages import HomePage, MatrixTab, ScraperTab, is_bank_cards_get, is_recommend_post


@pytest.mark.functional
def test_initial_load_applies_default_office_preset(page: Page, base_url: str) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    expect(home.channel_inputs).to_have_count(10)
    expect(home.total_spend_display).to_have_text("NT$ 26,000")
    expect(home.recommend_cards.first).to_be_visible()
    expect(home.recommend_cards.first).to_have_class(re.compile(r"top-rank"))
    expect(home.recommend_cards.first.locator("details")).to_have_attribute("open", "")
    expect(home.combo_section).not_to_have_class(re.compile(r"\bhidden\b"))


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
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    resp = home.select_preset(preset_key)
    assert resp.status == 200
    expect(home.total_spend_display).to_have_text(expected_total)
    expect(home.recommend_cards.first).to_be_visible()


@pytest.mark.functional
def test_clear_inputs_resets_total_and_shows_empty_state(page: Page, base_url: str) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    home.clear_inputs()
    expect(home.combo_section).to_have_class(re.compile(r"\bhidden\b"))
    expect(home.empty_state).to_be_visible()

    values = home.channel_inputs.evaluate_all("els => els.map(e => Number(e.value))")
    assert all(v == 0 for v in values)


@pytest.mark.functional
def test_manual_spending_submission_and_breakdown(page: Page, base_url: str) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)
    home.clear_inputs()

    home.channel_input("dining").fill("8000")
    home.channel_input("overseas").fill("12000")
    expect(home.total_spend_display).to_have_text("NT$ 20,000")

    resp = home.submit_spending()
    req_body = json.loads(resp.request.post_data or "{}")
    assert req_body["monthly_spending"] == {"dining": 8000, "overseas": 12000}

    top_card = home.recommend_cards.first
    expect(top_card).to_be_visible()
    expect(top_card.locator(".breakdown-table tbody tr")).to_have_count(2)


@pytest.mark.functional
def test_only_no_min_spend_checkbox_sends_flag(page: Page, base_url: str) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    expect(home.only_no_min_spend).not_to_be_checked()

    with page.expect_response(is_recommend_post) as resp_info:
        home.only_no_min_spend.check()

    req_body = json.loads(resp_info.value.request.post_data or "{}")
    assert req_body["only_no_min_spend"] is True
    assert resp_info.value.status == 200
    expect(home.recommend_cards.first).to_be_visible()


@pytest.mark.functional
def test_matrix_tab_renders_cards_and_channels(page: Page, base_url: str) -> None:
    home = HomePage(page)
    matrix = MatrixTab(page)
    home.goto_and_wait_ready(base_url)

    home.switch_tab("matrix")
    expect(matrix.headers).to_have_count(11)
    expect(matrix.rows.first).to_be_visible()
    expect(matrix.high_rate_cells.first).to_be_visible()


@pytest.mark.functional
def test_scraper_tab_controls_and_cascading_bank_cards(page: Page, base_url: str) -> None:
    home = HomePage(page)
    scraper = ScraperTab(page)

    # Regular visitors on "/" must not see the admin scraper tab
    home.goto_and_wait_ready(base_url)
    expect(home.tab_btn("scraper")).to_be_hidden()

    # Admin entry "/?admin=1" unlocks the scraper console tab
    home.goto_and_wait_ready(f"{base_url.rstrip('/')}/?admin=1")
    home.switch_tab("scraper")
    expect(scraper.scraper_checks.first).to_be_visible()
    expect(scraper.mode_demo_radio).to_be_checked()
    expect(scraper.card_select).to_be_disabled()

    with page.expect_response(is_bank_cards_get):
        scraper.bank_select.select_option(index=1)

    expect(scraper.card_select).to_be_enabled()
    scraper.card_select.select_option(index=1)
    assert scraper.card_name_input.input_value().strip() != ""

    scraper.bank_select.select_option("__other__")
    expect(scraper.manual_bank_wrap).not_to_have_class(re.compile(r"\bhidden\b"))
    expect(scraper.card_select).to_be_disabled()


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
    home = HomePage(pg)
    home.goto_and_wait_ready(f"{base_url.rstrip('/')}/?admin=1")

    for tab in ("recommend", "matrix", "custom", "scraper"):
        home.switch_tab(tab)
        overflow = home.horizontal_overflow_px()
        assert overflow <= 1, f"Horizontal overflow of {overflow}px on tab={tab}, viewport={viewport}"

    assert_no_runtime_errors(errors)


@pytest.mark.functional
@pytest.mark.pending_app_push
def test_channel_input_enforces_digit_limit_and_blocks_non_numeric(
    page: Page, base_url: str
) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    expect(home.channel_inputs).to_have_count(10)
    for idx in range(10):
        expect(home.channel_inputs.nth(idx)).to_have_attribute("maxlength", "7")
        expect(home.channel_inputs.nth(idx)).to_have_attribute("max", "9999999")

    home.clear_inputs()

    dining = home.channel_input("dining")
    dining.click()
    dining.fill("")
    dining.press_sequentially("1234567890")
    expect(dining).to_have_value("1234567")
    expect(home.total_spend_display).to_have_text("NT$ 1,234,567")

    dining.fill("")
    dining.press_sequentially("50e+-1.2")
    expect(dining).to_have_value("5012")
    expect(home.total_spend_display).to_have_text("NT$ 5,012")


@pytest.mark.functional
@pytest.mark.pending_app_push
def test_truncated_condition_note_renders_more_link_to_source(
    page: Page, base_url: str
) -> None:
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    home.select_preset("travel")

    page.locator("#recommendList details:not([open]) summary").evaluate_all(
        "els => els.forEach(el => el.click())"
    )

    more_links = page.locator("#recommendList a.note-more-link")
    expect(more_links.first).to_be_visible()

    first_link = more_links.first
    expect(first_link).to_have_text("more")
    expect(first_link).to_have_attribute("target", "_blank")
    expect(first_link).to_have_attribute("rel", re.compile(r"noopener"))
    href = first_link.get_attribute("href") or ""
    assert href.startswith("http"), f"Expected valid source URL on more link, got {href!r}"

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

    en_btn = page.locator('.lang-btn[data-lang="en"]')
    if en_btn.count() > 0:
        with page.expect_response(is_recommend_post):
            en_btn.click()
        expect(home.html).to_have_attribute("lang", re.compile(r"^en", re.I))
        page.locator("#recommendList details:not([open]) summary").evaluate_all(
            "els => els.forEach(el => el.click())"
        )
        en_links = page.locator("#recommendList a.note-more-link")
        expect(en_links.first).to_be_visible()
        expect(en_links.first).to_have_text("more")
        assert (en_links.first.get_attribute("href") or "").startswith("http")


def test_wallet_custom_card_remove_even_with_null_id(page: Page, base_url: str) -> None:
    """Clicking '移除' must delete a custom wallet card even if its stored id was null."""
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)

    page.evaluate(
        """() => {
            window.localStorage.setItem("cc_custom_cards", JSON.stringify([
                {
                    id: null,
                    bank_name: "測試銀行",
                    card_name: "測試移除專用卡",
                    base_rate_domestic: 1.5,
                    base_rate_foreign: 2.0,
                    rules: [{ channel_code: "dining", rate: 3.0, monthly_cap_ntd: 300, cap_applies_to: "bonus" }]
                }
            ]));
        }"""
    )
    home.goto_and_wait_ready(base_url)

    page.locator('#customCardsTabBtn').click()
    item = page.locator("#userCustomCardsList .user-custom-card-item")
    expect(item).to_have_count(1)
    expect(item.first).to_contain_text("測試移除專用卡")

    with page.expect_response(is_recommend_post):
        item.first.locator(".btn-delete-custom").click()

    expect(page.locator("#userCustomCardsList .user-custom-card-item")).to_have_count(0)
    stored = page.evaluate('() => JSON.parse(window.localStorage.getItem("cc_custom_cards") || "[]")')
    assert stored == [], f"Expected cc_custom_cards to be empty after removal, got {stored}"
