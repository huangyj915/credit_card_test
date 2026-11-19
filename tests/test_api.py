from __future__ import annotations

import re
import pytest
import requests

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


@pytest.mark.api
def test_homepage_utf8_and_status(base_url: str) -> None:
    resp = requests.get(f"{base_url}/", timeout=15)
    assert resp.status_code == 200
    content_type = resp.headers.get("content-type", "").lower()
    assert "text/html" in content_type
    assert "utf-8" in content_type or "<meta charset=\"UTF-8\"" in resp.text


@pytest.mark.api
def test_get_config_shape(base_url: str) -> None:
    resp = requests.get(f"{base_url}/api/config", timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("admin_protected"), bool)
    assert isinstance(data.get("public_readonly"), bool)
    assert isinstance(data.get("docs_enabled"), bool)


@pytest.mark.api
def test_get_channels_catalog(base_url: str) -> None:
    resp = requests.get(f"{base_url}/api/channels", timeout=15)
    assert resp.status_code == 200
    channels = resp.json()
    assert len(channels) >= 10
    codes = {c["code"] for c in channels}
    expected_codes = {
        "convenience_store",
        "dining",
        "delivery",
        "ecommerce",
        "mobile_pay",
        "supermarket",
        "transport",
        "travel",
        "overseas",
        "general",
    }
    assert expected_codes.issubset(codes)
    for ch in channels:
        assert ch["label"].strip()
        assert ch["examples"].strip()
        assert ch["icon"].strip()


@pytest.mark.api
def test_get_cards_and_rules(base_url: str) -> None:
    resp = requests.get(f"{base_url}/api/cards", timeout=15)
    assert resp.status_code == 200
    cards = resp.json()
    assert len(cards) >= 1
    for card in cards:
        assert card["bank_name"]
        assert card["card_name"]
        assert card["card_slug"]
        assert isinstance(card["base_rate_domestic"], (int, float))
        assert isinstance(card["base_rate_foreign"], (int, float))
        assert isinstance(card["rules"], list)


@pytest.mark.api
def test_get_banks_and_cascading_cards(base_url: str) -> None:
    resp = requests.get(f"{base_url}/api/banks", timeout=15)
    assert resp.status_code == 200
    banks = resp.json()
    assert len(banks) >= 5
    first_bank = banks[0]
    assert first_bank["bank_code"]
    assert first_bank["bank_name"]

    cards_resp = requests.get(
        f"{base_url}/api/banks/{first_bank['bank_code']}/cards",
        timeout=15,
    )
    assert cards_resp.status_code == 200
    bank_cards = cards_resp.json()
    assert isinstance(bank_cards, list)
    assert len(bank_cards) >= 1
    assert bank_cards[0]["card_name"]


@pytest.mark.api
def test_get_scrapers_and_logs(base_url: str) -> None:
    scrapers_resp = requests.get(f"{base_url}/api/scrapers", timeout=15)
    assert scrapers_resp.status_code == 200
    scrapers = scrapers_resp.json()
    assert len(scrapers) >= 1
    for s in scrapers:
        assert s["bank_code"]
        assert s["bank_name"]
        assert s["card_slug"]

    logs_resp = requests.get(f"{base_url}/api/scrape-logs?limit=5", timeout=15)
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    assert isinstance(logs, list)
    assert len(logs) <= 5


@pytest.mark.api
def test_recommend_calculation_and_ranking(base_url: str) -> None:
    payload = {
        "monthly_spending": {
            "dining": 6000,
            "ecommerce": 5000,
            "overseas": 10000,
        },
        "only_no_min_spend": False,
    }
    resp = requests.post(f"{base_url}/api/recommend", json=payload, timeout=15)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_spend_ntd"] == 21000.0
    recs = data["recommendations"]
    assert len(recs) >= 1

    rewards = [r["total_reward_ntd"] for r in recs]
    assert rewards == sorted(rewards, reverse=True), "Recommendations must be sorted descending by reward"

    top = recs[0]
    assert top["total_spend_ntd"] == 21000.0
    breakdown_spend = sum(item["spend_ntd"] for item in top["breakdown"])
    breakdown_reward = sum(item["actual_reward_ntd"] for item in top["breakdown"])
    assert breakdown_spend == 21000.0
    assert abs(breakdown_reward - top["total_reward_ntd"]) <= 1.0

    combo = data.get("combo")
    if combo:
        assert combo["total_spend_ntd"] == 21000.0
        assert combo["total_reward_ntd"] >= top["total_reward_ntd"]
        assert len(combo["allocations"]) >= 1


@pytest.mark.api
def test_recommend_zero_spending(base_url: str) -> None:
    resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": {}, "only_no_min_spend": False},
        timeout=15,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_spend_ntd"] == 0


@pytest.mark.api
def test_recommend_only_no_min_spend_filter(base_url: str) -> None:
    spending = {"dining": 5000, "ecommerce": 5000}
    all_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": spending, "only_no_min_spend": False},
        timeout=15,
    )
    filtered_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": spending, "only_no_min_spend": True},
        timeout=15,
    )
    assert all_resp.status_code == 200
    assert filtered_resp.status_code == 200
    all_recs = all_resp.json()["recommendations"]
    filtered_recs = filtered_resp.json()["recommendations"]
    assert len(filtered_recs) <= len(all_recs)


@pytest.mark.api
def test_admin_scrape_endpoint_protected_when_configured(base_url: str) -> None:
    cfg = requests.get(f"{base_url}/api/config", timeout=15).json()
    if not cfg.get("admin_protected") and not cfg.get("public_readonly"):
        pytest.skip("Target instance is running without admin_protected or public_readonly lock")

    resp = requests.post(
        f"{base_url}/api/scrape",
        json={"bank_codes": ["cathay"], "mode": "demo_html"},
        timeout=15,
    )
    assert resp.status_code in {401, 403}, f"Expected 401/403 without admin token, got {resp.status_code}"


@pytest.mark.api
@pytest.mark.en_i18n
def test_api_endpoints_english_i18n(base_url: str, require_en: bool) -> None:
    """Verify /api/channels, /api/cards, /api/banks, and /api/recommend return English when lang=en."""
    ch_en = requests.get(f"{base_url}/api/channels?lang=en", timeout=15).json()
    if CJK_RE.search(ch_en[0]["label"]):
        msg = "API ?lang=en still returning CJK channel labels"
        if require_en:
            pytest.fail(msg)
        pytest.skip(msg)

    for ch in ch_en:
        assert not CJK_RE.search(ch["label"]), f"Untranslated channel label: {ch}"
        assert not CJK_RE.search(ch["examples"]), f"Untranslated channel examples: {ch}"

    cards_en = requests.get(f"{base_url}/api/cards?lang=en", timeout=15).json()
    for card in cards_en:
        assert not CJK_RE.search(card["bank_name"]), f"Untranslated bank_name: {card['bank_name']}"
        assert not CJK_RE.search(card["card_name"]), f"Untranslated card_name: {card['card_name']}"
        assert not CJK_RE.search(card["reward_unit"]), f"Untranslated reward_unit: {card['reward_unit']}"
        assert not CJK_RE.search(card["annual_fee"]), f"Untranslated annual_fee: {card['annual_fee']}"

    banks_en = requests.get(f"{base_url}/api/banks?lang=en", timeout=15).json()
    for bank in banks_en:
        assert not CJK_RE.search(bank["bank_name"]), f"Untranslated bank: {bank}"

    rec_en = requests.post(
        f"{base_url}/api/recommend?lang=en",
        json={"monthly_spending": {"dining": 6000, "ecommerce": 5000}, "only_no_min_spend": False},
        timeout=15,
    ).json()
    top = rec_en["recommendations"][0]
    assert not CJK_RE.search(top["bank_name"])
    assert not CJK_RE.search(top["card_name"])
    for item in top["breakdown"]:
        assert not CJK_RE.search(item["channel_label"]), f"Untranslated breakdown label: {item}"
