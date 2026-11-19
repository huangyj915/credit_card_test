from __future__ import annotations

import re
from urllib.parse import urlparse
from playwright.sync_api import Locator, Page, expect


def is_recommend_post(resp) -> bool:
    return urlparse(resp.url).path == "/api/recommend" and resp.request.method == "POST"


def is_bank_cards_get(resp) -> bool:
    path = urlparse(resp.url).path
    return "/api/banks/" in path and path.endswith("/cards")


class HomePage:
    """Page Object for the Credit Card Recommender landing page & spending form."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def html(self) -> Locator:
        return self.page.locator("html")

    @property
    def h1(self) -> Locator:
        return self.page.locator("h1")

    @property
    def docs_link(self) -> Locator:
        return self.page.locator("#docsLink")

    @property
    def channel_inputs(self) -> Locator:
        return self.page.locator(".channel-input")

    @property
    def total_spend_display(self) -> Locator:
        return self.page.locator("#totalSpendDisplay")

    @property
    def clear_btn(self) -> Locator:
        return self.page.locator("#clearInputsBtn")

    @property
    def only_no_min_spend(self) -> Locator:
        return self.page.locator("#onlyNoMinSpend")

    @property
    def submit_btn(self) -> Locator:
        return self.page.locator('#spendingForm button[type="submit"]')

    @property
    def combo_section(self) -> Locator:
        return self.page.locator("#comboSection")

    @property
    def recommend_cards(self) -> Locator:
        return self.page.locator("#recommendList .card-result")

    @property
    def empty_state(self) -> Locator:
        return self.page.locator("#recommendList .empty-state")

    def channel_input(self, code: str) -> Locator:
        return self.page.locator(f'.channel-input[data-code="{code}"]')

    def preset_chip(self, preset_key: str) -> Locator:
        return self.page.locator(f'.chip[data-preset="{preset_key}"]')

    def tab_btn(self, tab_name: str) -> Locator:
        return self.page.locator(f'.tab-btn[data-tab="{tab_name}"]')

    def tab_panel(self, tab_name: str) -> Locator:
        return self.page.locator(f"#tab-{tab_name}")

    def goto_and_wait_ready(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
        expect(self.channel_inputs).to_have_count(10)
        expect(self.recommend_cards.first).to_be_visible()

    def select_preset(self, preset_key: str):
        with self.page.expect_response(is_recommend_post) as resp_info:
            self.preset_chip(preset_key).click()
        return resp_info.value

    def clear_inputs(self):
        with self.page.expect_response(is_recommend_post) as resp_info:
            self.clear_btn.click()
        expect(self.total_spend_display).to_have_text("NT$ 0")
        expect(self.empty_state).to_be_visible()
        return resp_info.value

    def submit_spending(self):
        with self.page.expect_response(is_recommend_post) as resp_info:
            self.submit_btn.click()
        return resp_info.value

    def switch_tab(self, tab_name: str) -> None:
        self.tab_btn(tab_name).click()
        expect(self.tab_panel(tab_name)).to_have_class(re.compile(r"\bactive\b"))

    def horizontal_overflow_px(self) -> int:
        return int(
            self.page.evaluate(
                "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
        )


class MatrixTab:
    """Page Object for the Comparison Matrix tab."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def table(self) -> Locator:
        return self.page.locator("#matrixTable")

    @property
    def headers(self) -> Locator:
        return self.page.locator("#matrixTable thead th")

    @property
    def rows(self) -> Locator:
        return self.page.locator("#matrixTable tbody tr")

    @property
    def high_rate_cells(self) -> Locator:
        return self.page.locator("#matrixTable td.rate-high")


class ScraperTab:
    """Page Object for the Playwright Scraper Center tab."""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def auth_bar(self) -> Locator:
        return self.page.locator("#scraperAuthBar")

    @property
    def scraper_checks(self) -> Locator:
        return self.page.locator("#scraperBanks .scraper-check")

    @property
    def mode_demo_radio(self) -> Locator:
        return self.page.locator('input[name="scrapeMode"][value="demo_html"]')

    @property
    def run_scrape_btn(self) -> Locator:
        return self.page.locator("#runScrapeBtn")

    @property
    def run_custom_scrape_btn(self) -> Locator:
        return self.page.locator("#runCustomScrapeBtn")

    @property
    def discover_cards_btn(self) -> Locator:
        return self.page.locator("#discoverBankCardsBtn")

    @property
    def bank_select(self) -> Locator:
        return self.page.locator("#customBankSelect")

    @property
    def card_select(self) -> Locator:
        return self.page.locator("#customCardSelect")

    @property
    def manual_bank_wrap(self) -> Locator:
        return self.page.locator("#customBankManualWrap")

    @property
    def card_name_input(self) -> Locator:
        return self.page.locator("#customCardName")

    @property
    def scrape_results(self) -> Locator:
        return self.page.locator("#scrapeResults")
