from __future__ import annotations

import json
import re
from urllib.parse import urlparse
import pytest
import requests
from playwright.sync_api import Page, expect


def _eval_rule_reward(
    spend: float,
    rate: float,
    cap: float | None,
    base_rate: float,
) -> float:
    """Reference reward formula: capped bonus + base rate on overflow spend."""
    if spend <= 0:
        return 0.0
    rate_dec = rate / 100.0
    base_dec = base_rate / 100.0
    raw = spend * rate_dec
    if cap is not None and cap > 0 and raw > cap and rate > base_rate:
        covered_spend = cap / rate_dec
        overflow_spend = max(spend - covered_spend, 0.0)
        return round(cap + overflow_spend * base_dec, 2)
    return round(raw, 2)


def _oracle_card_calc(card: dict, spending: dict[str, float]) -> dict:
    """Independently compute optimal plan, per-channel breakdown, and total reward from card rules."""
    total_spend = sum(v for v in spending.values() if v > 0)
    plans = sorted({r["plan_name"] for r in card["rules"] if r.get("plan_name")})
    candidate_plans = plans if plans else [None]

    best_result = None
    for plan in candidate_plans:
        breakdown = {}
        total_reward = 0.0
        for ch_code, spend in spending.items():
            if spend <= 0:
                continue
            base_rate = (
                card["base_rate_foreign"]
                if ch_code == "overseas"
                else card["base_rate_domestic"]
            )
            eligible = []
            for r in card["rules"]:
                if r["channel_code"] != ch_code:
                    continue
                if r.get("plan_name") not in (None, plan):
                    continue
                min_sp = r.get("min_spend_ntd") or 0.0
                if min_sp > 0 and total_spend < min_sp:
                    continue
                eligible.append(r)

            if eligible:
                # Choose rule yielding highest actual reward for this channel spend
                scored = [
                    (
                        _eval_rule_reward(
                            spend, r["rate"], r.get("monthly_cap_ntd"), base_rate
                        ),
                        r["rate"],
                        r,
                    )
                    for r in eligible
                ]
                reward, _, chosen = max(scored, key=lambda x: (x[0], x[1]))
                applied_rate = chosen["rate"]
                cap_ntd = chosen.get("monthly_cap_ntd")
            else:
                reward = round(spend * (base_rate / 100.0), 2)
                applied_rate = base_rate
                cap_ntd = None

            breakdown[ch_code] = {
                "applied_rate": applied_rate,
                "cap_ntd": cap_ntd,
                "actual_reward_ntd": reward,
            }
            total_reward += reward

        total_reward = round(total_reward, 2)
        if best_result is None or total_reward > best_result["total_reward_ntd"]:
            best_result = {
                "recommended_plan": plan,
                "total_reward_ntd": total_reward,
                "breakdown": breakdown,
            }

    return best_result


@pytest.mark.math
def test_recommend_oracle_matches_card_rules_and_caps(base_url: str) -> None:
    """Independently recompute every card's reward from /api/cards rules and compare with /api/recommend."""
    cards = requests.get(f"{base_url}/api/cards", timeout=15).json()
    card_by_slug = {c["card_slug"]: c for c in cards}

    spending = {
        "overseas": 20000,
        "travel": 10000,
        "dining": 6000,
        "ecommerce": 5000,
        "convenience_store": 2000,
        "general": 5000,
    }
    rec_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": spending, "only_no_min_spend": False},
        timeout=15,
    ).json()

    expected_total_spend = sum(spending.values())
    assert rec_resp["total_spend_ntd"] == expected_total_spend

    for rec in rec_resp["recommendations"]:
        card = card_by_slug[rec["card_slug"]]
        oracle = _oracle_card_calc(card, spending)

        assert abs(rec["total_reward_ntd"] - oracle["total_reward_ntd"]) <= 0.1, (
            f"{rec['card_slug']} total_reward_ntd mismatch: "
            f"api={rec['total_reward_ntd']} vs oracle={oracle['total_reward_ntd']}"
        )

        expected_eff = round(rec["total_reward_ntd"] / expected_total_spend * 100, 2)
        assert abs(rec["effective_rate_pct"] - expected_eff) <= 0.02, (
            f"{rec['card_slug']} effective_rate_pct mismatch: "
            f"api={rec['effective_rate_pct']} vs expected={expected_eff}"
        )

        for b in rec["breakdown"]:
            exp_b = oracle["breakdown"][b["channel_code"]]
            assert b["applied_rate"] == exp_b["applied_rate"], (
                f"{rec['card_slug']} {b['channel_code']} applied_rate mismatch: "
                f"api={b['applied_rate']} vs oracle={exp_b['applied_rate']}"
            )
            assert abs(b["actual_reward_ntd"] - exp_b["actual_reward_ntd"]) <= 0.05, (
                f"{rec['card_slug']} {b['channel_code']} reward mismatch: "
                f"api={b['actual_reward_ntd']} vs oracle={exp_b['actual_reward_ntd']}"
            )


@pytest.mark.math
def test_combo_allocation_maximizes_channel_rewards_and_gain(base_url: str) -> None:
    """Verify multi-card combo picks the highest-reward card per channel and computes gain accurately."""
    spending = {
        "overseas": 15000,
        "dining": 6000,
        "ecommerce": 5000,
        "transport": 3000,
    }
    rec_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": spending, "only_no_min_spend": False},
        timeout=15,
    ).json()

    recs = rec_resp["recommendations"]
    best_single = recs[0]
    combo = rec_resp["combo"]
    assert combo is not None, "Expected combo allocation for multi-channel spend"

    # Build lookup of each card's actual reward for each channel from single-card breakdowns
    reward_by_card_channel = {
        r["card_slug"]: {b["channel_code"]: b["actual_reward_ntd"] for b in r["breakdown"]}
        for r in recs
    }

    alloc_sum = 0.0
    for alloc in combo["allocations"]:
        ch = alloc["channel_code"]
        chosen_reward = alloc["reward_ntd"]
        max_possible = max(
            reward_by_card_channel[slug][ch] for slug in reward_by_card_channel
        )
        assert abs(chosen_reward - max_possible) <= 0.05, (
            f"Combo picked suboptimal card {alloc['card_slug']} ({chosen_reward}) "
            f"for {ch}; max single-card channel reward is {max_possible}"
        )
        alloc_sum += chosen_reward

    assert abs(combo["total_reward_ntd"] - round(alloc_sum, 2)) <= 0.1
    expected_gain = round(combo["total_reward_ntd"] - best_single["total_reward_ntd"], 2)
    assert abs(combo["gain_over_best_single_ntd"] - expected_gain) <= 0.1
    expected_eff = round(combo["total_reward_ntd"] / sum(spending.values()) * 100, 2)
    assert abs(combo["effective_rate_pct"] - expected_eff) <= 0.02


@pytest.mark.math
def test_cap_overflow_and_min_spend_boundary_behavior(base_url: str) -> None:
    """Verify cap saturation transitions excess spend to base rate and min_spend filter holds."""
    cards = requests.get(f"{base_url}/api/cards", timeout=15).json()

    # Find a card with a clean high cap (monthly_cap_ntd >= 200) and rate > base_rate
    target = None
    target_rule = None
    for c in cards:
        for r in c["rules"]:
            cap = r.get("monthly_cap_ntd") or 0
            base = c["base_rate_foreign"] if r["channel_code"] == "overseas" else c["base_rate_domestic"]
            if cap >= 200 and r["rate"] > base and not r.get("min_spend_ntd") and not r.get("plan_name"):
                target = c
                target_rule = r
                break
        if target:
            break

    assert target is not None and target_rule is not None

    ch = target_rule["channel_code"]
    cap = target_rule["monthly_cap_ntd"]
    rate = target_rule["rate"]
    base = target["base_rate_foreign"] if ch == "overseas" else target["base_rate_domestic"]

    cap_break_even = cap / (rate / 100.0)
    below_spend = round(cap_break_even * 0.5, 0)
    above_spend = round(cap_break_even * 2.0, 0)

    below_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": {ch: below_spend}, "only_no_min_spend": False},
        timeout=15,
    ).json()
    below_card = next(x for x in below_resp["recommendations"] if x["card_slug"] == target["card_slug"])
    assert abs(below_card["total_reward_ntd"] - round(below_spend * rate / 100.0, 2)) <= 0.05

    above_resp = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": {ch: above_spend}, "only_no_min_spend": False},
        timeout=15,
    ).json()
    above_card = next(x for x in above_resp["recommendations"] if x["card_slug"] == target["card_slug"])
    expected_above = _eval_rule_reward(above_spend, rate, cap, base)
    assert abs(above_card["total_reward_ntd"] - expected_above) <= 0.05

    # Verify only_no_min_spend=True excludes cards with min_spend_ntd > 0
    min_spend_slugs = {
        c["card_slug"]
        for c in cards
        if any((r.get("min_spend_ntd") or 0) > 0 for r in c["rules"])
    }
    if min_spend_slugs:
        filtered = requests.post(
            f"{base_url}/api/recommend",
            json={"monthly_spending": {ch: above_spend}, "only_no_min_spend": True},
            timeout=15,
        ).json()
        returned_slugs = {x["card_slug"] for x in filtered["recommendations"]}
        assert not (returned_slugs & min_spend_slugs), (
            f"only_no_min_spend=True still returned cards with min_spend: {returned_slugs & min_spend_slugs}"
        )


@pytest.mark.math
@pytest.mark.functional
def test_ui_displays_exact_api_recommendation_values(page: Page, base_url: str) -> None:
    """Verify the rendered UI cards, reward totals, and breakdown table match /api/recommend exactly."""
    page.goto(base_url, wait_until="networkidle")

    with page.expect_response(
        lambda r: urlparse(r.url).path == "/api/recommend" and r.request.method == "POST"
    ):
        page.locator("#clearInputsBtn").click()
    expect(page.locator("#recommendList .empty-state")).to_be_visible()

    page.locator('.channel-input[data-code="dining"]').fill("6000")
    page.locator('.channel-input[data-code="overseas"]').fill("15000")

    with page.expect_response(
        lambda r: urlparse(r.url).path == "/api/recommend" and r.request.method == "POST"
    ) as resp_info:
        page.locator('#spendingForm button[type="submit"]').click()

    api_data = json.loads(resp_info.value.text())
    top_api = api_data["recommendations"][0]

    top_ui = page.locator("#recommendList .card-result").first
    expect(top_ui.locator(".card-name")).to_contain_text(top_api["card_name"])

    expected_ntd = f"NT$ {round(top_api['total_reward_ntd']):,}"
    expect(top_ui.locator(".reward-amount")).to_contain_text(expected_ntd)
    expect(top_ui.locator(".reward-rate")).to_contain_text(f"{top_api['effective_rate_pct']}%")

    ui_rows = top_ui.locator(".breakdown-table tbody tr")
    expect(ui_rows).to_have_count(len(top_api["breakdown"]))

    if api_data.get("combo"):
        combo_ntd = f"NT$ {round(api_data['combo']['total_reward_ntd']):,}"
        expect(page.locator("#comboSection .combo-gain")).to_contain_text(combo_ntd)


@pytest.mark.data_quality
def test_card_rules_sanity_no_scraper_parse_artifacts(base_url: str) -> None:
    """Detect unrealistic scraper-parsed rates (>15%) or broken monthly caps (<50 NTD or year numbers)."""
    cards = requests.get(f"{base_url}/api/cards", timeout=15).json()
    anomalies = []

    for c in cards:
        slug = c["card_slug"]
        for r in c["rules"]:
            rate = r.get("rate") or 0.0
            cap = r.get("monthly_cap_ntd")
            cond = str(r.get("conditions") or "")
            ch = r["channel_code"]

            if rate > 15.0:
                anomalies.append(f"{slug}.{ch}: unrealistic rate={rate}%")
            if cap is not None and 0 < cap < 50.0:
                anomalies.append(f"{slug}.{ch}: suspicious low monthly_cap_ntd={cap}")
            if cap is not None and 2020 <= cap <= 2035 and re.search(rf"\b{int(cap)}/", cond):
                anomalies.append(f"{slug}.{ch}: monthly_cap_ntd={cap} likely parsed from calendar year")

    assert not anomalies, "Detected scraper-parsed rule anomalies distorting recommendations: " + "; ".join(anomalies)
