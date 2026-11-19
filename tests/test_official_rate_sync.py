from __future__ import annotations

import re
import pytest
import requests
from playwright.sync_api import Page, expect

from pages import HomePage, MatrixTab

PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
DEAD_PAGE_PATTERNS = re.compile(
    r"(404\s*找不到頁面|找不到頁面|系統發生錯誤|Page\s*Not\s*Found|404\s*Not\s*Found)",
    re.IGNORECASE,
)


@pytest.mark.official_sync
def test_ui_displayed_rates_match_api_cards_source_of_truth(
    page: Page, base_url: str
) -> None:
    """Verify the comparison matrix UI displays the exact best rates from /api/cards."""
    cards = requests.get(f"{base_url}/api/cards", timeout=15).json()
    channels = requests.get(f"{base_url}/api/channels", timeout=15).json()

    home = HomePage(page)
    matrix = MatrixTab(page)
    home.goto_and_wait_ready(base_url)
    home.switch_tab("matrix")
    expect(matrix.rows).to_have_count(len(cards))

    for idx, card in enumerate(cards):
        row = matrix.rows.nth(idx)
        expect(row.locator("td").first).to_contain_text(card["card_name"])
        cells = row.locator("td")
        for ch_idx, ch in enumerate(channels, start=1):
            matching = [r for r in card["rules"] if r["channel_code"] == ch["code"]]
            expected_rate = (
                max(r["rate"] for r in matching)
                if matching
                else (
                    card["base_rate_foreign"]
                    if ch["code"] == "overseas"
                    else card["base_rate_domestic"]
                )
            )
            cell_text = cells.nth(ch_idx).inner_text()
            m = re.search(r"(\d+(?:\.\d+)?)%", cell_text)
            assert m is not None, f"Missing % in matrix cell ({card['card_slug']}, {ch['code']}): {cell_text!r}"
            assert float(m.group(1)) == pytest.approx(expected_rate, abs=0.01), (
                f"Matrix rate mismatch for {card['card_slug']}.{ch['code']}: "
                f"UI={m.group(1)}% vs API={expected_rate}%"
            )


def _extract_main_content_text(pg: Page) -> str:
    """Prefer main content containers over full body to reduce footer/legal boilerplate noise."""
    for sel in ("main", "article", '[role="main"]', "#main", ".main-content", ".card-detail"):
        loc = pg.locator(sel)
        if loc.count() > 0:
            try:
                text = " ".join(loc.first.inner_text(timeout=2000).split())
                if len(text) >= 200 and PCT_RE.search(text):
                    return text
            except Exception:
                continue
    return " ".join(pg.locator("body").inner_text().split())


@pytest.mark.official_sync
def test_displayed_card_rates_match_official_bank_websites(
    browser, base_url: str
) -> None:
    """Compare each card's displayed rule rates and official_url health against live bank websites."""
    cards = requests.get(f"{base_url}/api/cards", timeout=15).json()
    ctx = browser.new_context(locale="zh-TW", viewport={"width": 1280, "height": 800})

    dead_urls = []
    rate_mismatches = []
    unverified_blocked = []

    try:
        for card in cards:
            url = (card.get("official_url") or "").strip()
            slug = card["card_slug"]
            rule_rates = sorted({float(r["rate"]) for r in card.get("rules", []) if r.get("rate") is not None})
            if not url:
                continue

            pg = ctx.new_page()
            try:
                resp = pg.goto(url, wait_until="domcontentloaded", timeout=15000)
                try:
                    pg.wait_for_function(
                        "() => document.body && document.body.innerText.trim().length > 50",
                        timeout=6000,
                    )
                except Exception:
                    pass

                status = resp.status if resp else 0
                full_body = " ".join(pg.locator("body").inner_text().split())

                if status >= 400 or len(full_body) < 50 or DEAD_PAGE_PATTERNS.search(full_body):
                    dead_urls.append(
                        f"{slug} (HTTP={status}, len={len(full_body)}, snippet={full_body[:40]!r}, url={url})"
                    )
                    continue

                if not rule_rates:
                    continue

                scoped_text = _extract_main_content_text(pg)
                official_pcts = {round(float(m), 4) for m in PCT_RE.findall(scoped_text)}
                if not official_pcts:
                    official_pcts = {round(float(m), 4) for m in PCT_RE.findall(full_body)}
                if not official_pcts:
                    unverified_blocked.append(f"{slug} (no % extracted on {url})")
                    continue

                missing = [r for r in rule_rates if round(r, 4) not in official_pcts]
                if missing:
                    sample_official = sorted(official_pcts)[:12]
                    rate_mismatches.append(
                        f"{slug}: site_rules={missing}% not found on official page (official_pcts={sample_official}, url={url})"
                    )
            except Exception as exc:
                unverified_blocked.append(f"{slug}: fetch error {str(exc).splitlines()[0][:80]}")
            finally:
                pg.close()
    finally:
        ctx.close()

    problems = []
    if dead_urls:
        problems.append("Dead/broken official_url: " + "; ".join(dead_urls))
    if rate_mismatches:
        problems.append("Rate mismatch vs official bank page: " + "; ".join(rate_mismatches))
    if unverified_blocked:
        problems.append("Unreachable/no-rate official pages: " + "; ".join(unverified_blocked))

    assert not problems, " | ".join(problems)
