from __future__ import annotations

import re
from urllib.parse import urlparse
import pytest
from playwright.sync_api import Page, expect

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LEAKED_I18N_KEY_RE = re.compile(
    r"(\{\{[^}]+\}\}|\{(?:count|rate|reward|gain|rank|amount|annual|plan|date|time|value|bank|code|unit|fee)\}|__MISSING__|(?i:missing translation)|(?i:i18n\.[a-z0-9_.]+)|\bundefined\b|\bNaN\b)"
)


def _is_recommend_post(r) -> bool:
    return urlparse(r.url).path == "/api/recommend" and r.request.method == "POST"


def _find_and_switch_to_english(page: Page, base_url: str) -> tuple[bool, str]:
    """Attempt to activate English UI via switcher control or query param."""
    data_en = page.locator(
        '[data-lang^="en" i], [data-locale^="en" i], [data-testid="lang-en"], #langEnBtn'
    ).first
    if data_en.count() > 0 and data_en.is_visible():
        data_en.click()
        page.wait_for_timeout(400)
        return True, "clicked [data-lang='en'] button"

    selects = page.locator("select")
    for idx in range(selects.count()):
        sel = selects.nth(idx)
        en_opt = sel.locator('option[value^="en" i]')
        if en_opt.count() > 0:
            val = en_opt.first.get_attribute("value")
            if val:
                sel.select_option(val)
                page.wait_for_timeout(400)
                return True, f"selected option value={val}"

    btn_en = page.locator(
        "header button, header a, nav button, nav a, .hero-actions button, .hero-actions a"
    ).filter(has_text=re.compile(r"^(EN|ENG|English)$", re.I)).first
    if btn_en.count() > 0 and btn_en.is_visible():
        btn_en.click()
        page.wait_for_timeout(400)
        return True, "clicked header EN button/link"

    page.goto(f"{base_url}/?lang=en", wait_until="networkidle")
    html_lang = (page.locator("html").get_attribute("lang") or "").lower()
    h1_text = page.locator("h1").inner_text()
    if html_lang.startswith("en") or (h1_text and not CJK_RE.search(h1_text)):
        return True, "query param ?lang=en"

    return False, "no English switcher or ?lang=en response detected"


def _switch_back_to_zh(page: Page, base_url: str) -> bool:
    data_zh = page.locator(
        '[data-lang^="zh" i], [data-locale^="zh" i], [data-testid="lang-zh"], #langZhBtn'
    ).first
    if data_zh.count() > 0 and data_zh.is_visible():
        data_zh.click()
        page.wait_for_timeout(400)
        return True

    btn_zh = page.locator(
        "header button, header a, nav button, nav a, .hero-actions button, .hero-actions a"
    ).filter(has_text=re.compile(r"^(繁中|繁體中文|中文|ZH)$", re.I)).first
    if btn_zh.count() > 0 and btn_zh.is_visible():
        btn_zh.click()
        page.wait_for_timeout(400)
        return True

    page.goto(f"{base_url}/?lang=zh-TW", wait_until="networkidle")
    return True


@pytest.mark.i18n
def test_zh_hant_document_lang_charset_and_text_integrity(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    html_lang = page.locator("html").get_attribute("lang") or ""
    assert html_lang.lower().startswith("zh"), f"Expected zh* <html lang>, got {html_lang!r}"

    charset = page.evaluate("() => document.characterSet")
    assert charset.upper() == "UTF-8"

    title = page.title()
    assert CJK_RE.search(title), f"Expected Traditional Chinese title, got {title!r}"

    body_text = page.locator("body").inner_text()
    assert "\ufffd" not in body_text, "Found Unicode replacement character (mojibake)"
    match = LEAKED_I18N_KEY_RE.search(body_text)
    assert not match, f"Found leaked template/i18n placeholder in UI: {match.group(0)!r}"


@pytest.mark.i18n
def test_zh_tw_currency_percentage_and_taipei_timestamp_formatting(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="networkidle")

    total_text = page.locator("#totalSpendDisplay").inner_text()
    assert re.match(r"^NT\$\s[\d,]+$", total_text), f"Unexpected currency format: {total_text!r}"

    rate_text = page.locator("#recommendList .reward-rate").first.inner_text()
    assert re.search(r"\d+(?:\.\d+)?%", rate_text), f"Missing percentage format in {rate_text!r}"

    date_pill = page.locator("#recommendList .date-pill").first
    if date_pill.count() > 0:
        pill_text = date_pill.inner_text()
        pill_title = date_pill.get_attribute("title") or ""
        assert re.search(r"\d{4}-\d{2}-\d{2}|未標註", pill_text), f"Unexpected date pill: {pill_text!r}"
        if "最後更新：" in pill_title:
            assert re.search(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", pill_title)


@pytest.mark.i18n
@pytest.mark.parametrize(
    ("locale", "accept_language"),
    [
        ("zh-TW", "zh-TW,zh;q=0.9"),
        ("en-US", "en-US,en;q=0.9"),
        ("ja-JP", "ja-JP,ja;q=0.9,en;q=0.8"),
    ],
)
def test_app_functional_under_different_browser_locales(
    make_page,
    base_url: str,
    locale: str,
    accept_language: str,
) -> None:
    """Ensure Intl formatting, presets, recommendation, and tabs work under non-TW locales."""
    pg, errors = make_page(locale=locale, accept_language=accept_language)
    pg.goto(base_url, wait_until="networkidle")

    expect(pg.locator(".channel-input")).to_have_count(10)
    with pg.expect_response(_is_recommend_post) as resp_info:
        pg.locator('.chip[data-preset="travel"]').click()
    assert resp_info.value.status == 200

    total_text = pg.locator("#totalSpendDisplay").inner_text()
    assert "58,000" in total_text, f"Unexpected formatted total under {locale}: {total_text!r}"
    assert pg.locator("#recommendList .card-result").count() >= 1

    pg.locator('.tab-btn[data-tab="matrix"]').click()
    assert pg.locator("#matrixTable tbody tr").count() >= 1

    overflow = pg.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 1, f"Horizontal overflow under locale={locale}: {overflow}px"
    assert not errors["pageerrors"], f"Page errors under {locale}: {errors['pageerrors']}"
    assert not errors["server_errors"], f"Server 5xx under {locale}: {errors['server_errors']}"


@pytest.mark.i18n
@pytest.mark.en_i18n
def test_english_i18n_switch_and_translations(
    make_page,
    base_url: str,
    require_en: bool,
) -> None:
    """Verify English i18n mode: switcher, <html lang>, all UI regions, persistence, and round-trip to zh."""
    pg, errors = make_page(locale="zh-TW", accept_language="zh-TW,zh;q=0.9")
    pg.goto(base_url, wait_until="networkidle")

    activated, method = _find_and_switch_to_english(pg, base_url)
    if not activated:
        msg = (
            "English (en) i18n is not yet active on the target URL "
            f"({method}). Run with --require-en once English is deployed."
        )
        if require_en:
            pytest.fail(msg)
        pytest.skip(msg)

    # 1. Document <html lang>, <title>, and switcher button aria-pressed state
    expect(pg.locator("html")).to_have_attribute("lang", re.compile(r"^en", re.I))
    assert not CJK_RE.search(pg.title()), f"Document title not translated: {pg.title()!r}"

    en_btn = pg.locator('.lang-btn[data-lang="en"]')
    zh_btn = pg.locator('.lang-btn[data-lang="zh-TW"]')
    if en_btn.count() > 0:
        expect(en_btn).to_have_attribute("aria-pressed", "true")
        expect(zh_btn).to_have_attribute("aria-pressed", "false")

    # 2. Core UI chrome & preset chips should all be English (no residual CJK)
    chrome_selectors = {
        "hero_h1": "h1",
        "hero_subtitle": ".subtitle",
        "panel_heading": ".input-panel h2",
        "input_hint": ".input-panel .hint",
        "preset_office": '.chip[data-preset="office"]',
        "preset_travel": '.chip[data-preset="travel"]',
        "preset_commuter": '.chip[data-preset="commuter"]',
        "clear_btn": "#clearInputsBtn",
        "only_no_min_spend": ".checkbox-label span",
        "total_label": ".total-bar span",
        "submit_btn": '#spendingForm button[type="submit"]',
        "tab_recommend": '.tab-btn[data-tab="recommend"]',
        "tab_matrix": '.tab-btn[data-tab="matrix"]',
        "tab_scraper": '.tab-btn[data-tab="scraper"]',
        "footer": ".footer p",
    }
    untranslated = {}
    for name, selector in chrome_selectors.items():
        loc = pg.locator(selector)
        if loc.count() == 0:
            continue
        text = loc.first.inner_text().strip()
        assert text, f"Empty text for {name} ({selector}) in English mode"
        if CJK_RE.search(text):
            untranslated[name] = text

    assert not untranslated, f"Untranslated CJK text in English UI chrome: {untranslated}"

    # 3. Channel list labels & examples translated to English
    channel_texts = pg.locator("#channelsList .channel-meta").all_inner_texts()
    assert len(channel_texts) == 10
    cjk_channels = [t for t in channel_texts if CJK_RE.search(t)]
    assert not cjk_channels, f"Untranslated channels in English mode: {cjk_channels}"

    # 4. Trigger travel preset in English mode & check recommendations + breakdown + combo
    with pg.expect_response(_is_recommend_post):
        pg.locator('.chip[data-preset="travel"]').click()
    expect(pg.locator("#totalSpendDisplay")).to_have_text("NT$ 58,000")

    rec_text = pg.locator("#tab-recommend").inner_text()
    cjk_rec_lines = [line.strip() for line in rec_text.splitlines() if CJK_RE.search(line)]
    assert not cjk_rec_lines, f"Untranslated CJK lines in Recommend tab: {cjk_rec_lines[:5]}"

    # 5. Matrix tab translated
    pg.locator('.tab-btn[data-tab="matrix"]').click()
    matrix_text = pg.locator("#tab-matrix").inner_text()
    cjk_matrix_lines = [line.strip() for line in matrix_text.splitlines() if CJK_RE.search(line)]
    assert not cjk_matrix_lines, f"Untranslated CJK lines in Matrix tab: {cjk_matrix_lines[:5]}"

    # 6. Scraper tab translated
    pg.locator('.tab-btn[data-tab="scraper"]').click()
    scraper_text = pg.locator("#tab-scraper").inner_text()
    cjk_scraper_lines = [line.strip() for line in scraper_text.splitlines() if CJK_RE.search(line)]
    assert not cjk_scraper_lines, f"Untranslated CJK lines in Scraper tab: {cjk_scraper_lines[:5]}"

    # 7. No leaked i18n keys or replacement characters across entire body
    body_text = pg.locator("body").inner_text()
    assert "\ufffd" not in body_text
    leaked = LEAKED_I18N_KEY_RE.search(body_text)
    assert not leaked, f"Leaked i18n placeholder in English mode: {leaked.group(0)!r}"

    # 8. Language persistence in localStorage across page reload
    pg.reload(wait_until="networkidle")
    expect(pg.locator("html")).to_have_attribute("lang", re.compile(r"^en", re.I))
    assert not CJK_RE.search(pg.locator("h1").inner_text()), "English selection did not persist after reload"

    # 9. Layout overflow check in English on desktop & mobile
    pg.locator('.tab-btn[data-tab="recommend"]').click()
    for vp in ({"width": 1440, "height": 900}, {"width": 390, "height": 844}):
        pg.set_viewport_size(vp)
        pg.wait_for_timeout(150)
        overflow = pg.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        assert overflow <= 1, f"English UI horizontal overflow ({overflow}px) at {vp}"

    # 10. Round-trip switch back to Traditional Chinese
    _switch_back_to_zh(pg, base_url)
    expect(pg.locator("html")).to_have_attribute("lang", re.compile(r"^zh", re.I))
    assert CJK_RE.search(pg.locator("h1").inner_text())

    assert not errors["pageerrors"]
    assert not errors["server_errors"]


@pytest.mark.i18n
@pytest.mark.en_i18n
def test_english_query_param_direct_entry(
    make_page,
    base_url: str,
    require_en: bool,
) -> None:
    """Verify navigating directly to /?lang=en renders English UI on first paint."""
    pg, errors = make_page(locale="zh-TW")
    pg.goto(f"{base_url}/?lang=en", wait_until="networkidle")

    lang = (pg.locator("html").get_attribute("lang") or "").lower()
    if not lang.startswith("en"):
        msg = "/?lang=en did not activate English mode"
        if require_en:
            pytest.fail(msg)
        pytest.skip(msg)

    assert not CJK_RE.search(pg.locator("h1").inner_text())
    assert not errors["pageerrors"]
    assert not errors["server_errors"]
