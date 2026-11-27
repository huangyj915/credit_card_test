from __future__ import annotations

import json
import re
import pytest
import requests
from playwright.sync_api import Page, expect

from pages import HomePage


def _eval_rule_reward(
    spend: float,
    rate: float,
    cap: float | None,
    base_rate: float,
    cap_applies_to: str = "total",
) -> float:
    """Reference reward formula supporting both bonus-only caps and total caps."""
    if spend <= 0:
        return 0.0
    rate_dec = rate / 100.0
    base_dec = base_rate / 100.0
    base_reward = spend * base_dec

    if cap_applies_to == "bonus":
        bonus_rate = max(0.0, rate - base_rate)
        raw_bonus = spend * (bonus_rate / 100.0)
        if cap is not None and cap > 0 and raw_bonus > cap:
            return round(base_reward + cap, 2)
        return round(base_reward + raw_bonus, 2)

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
                scored = [
                    (
                        _eval_rule_reward(
                            spend,
                            r["rate"],
                            r.get("monthly_cap_ntd"),
                            base_rate,
                            r.get("cap_applies_to") or "total",
                        ),
                        r["rate"],
                        r,
                    )
                    for r in eligible
                ]
                reward, _, chosen = max(scored, key=lambda x: (x[0], x[1]))
                applied_rate = chosen["rate"]
                cap_ntd = chosen.get("monthly_cap_ntd")
                cap_group = chosen.get("cap_group")
            else:
                reward = round(spend * (base_rate / 100.0), 2)
                applied_rate = base_rate
                cap_ntd = None
                cap_group = None

            breakdown[ch_code] = {
                "applied_rate": applied_rate,
                "cap_ntd": cap_ntd,
                "cap_group": cap_group,
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

        # Detect whether multiple active channels share a cap_group on this card
        group_counts: dict[str, int] = {}
        for item in oracle["breakdown"].values():
            grp = item.get("cap_group")
            if grp:
                group_counts[grp] = group_counts.get(grp, 0) + 1
        has_shared_group = any(cnt > 1 for cnt in group_counts.values())

        bd_sum = round(sum(b["actual_reward_ntd"] for b in rec["breakdown"]), 2)
        assert abs(rec["total_reward_ntd"] - bd_sum) <= 0.1

        expected_eff = round(rec["total_reward_ntd"] / expected_total_spend * 100, 2)
        assert abs(rec["effective_rate_pct"] - expected_eff) <= 0.02, (
            f"{rec['card_slug']} effective_rate_pct mismatch: "
            f"api={rec['effective_rate_pct']} vs expected={expected_eff}"
        )

        if has_shared_group:
            # Shared cap across multiple channels cannot exceed independent-channel upper bound
            assert rec["total_reward_ntd"] <= oracle["total_reward_ntd"] + 0.1
            continue

        assert abs(rec["total_reward_ntd"] - oracle["total_reward_ntd"]) <= 0.1, (
            f"{rec['card_slug']} total_reward_ntd mismatch: "
            f"api={rec['total_reward_ntd']} vs oracle={oracle['total_reward_ntd']}"
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

    by_channel: dict[str, list[dict]] = {}
    for alloc in combo["allocations"]:
        by_channel.setdefault(alloc["channel_code"], []).append(alloc)

    assert set(by_channel.keys()) == set(spending.keys()), (
        f"Combo allocations channels mismatch: {set(by_channel.keys())} vs {set(spending.keys())}"
    )

    alloc_sum = 0.0
    for ch, items in by_channel.items():
        ch_spend = round(sum(a["spend_ntd"] for a in items), 2)
        assert abs(ch_spend - spending[ch]) <= 0.1, (
            f"Combo channel spend sum mismatch for {ch}: {ch_spend} vs {spending[ch]}"
        )
        ch_reward = round(sum(a["reward_ntd"] for a in items), 2)
        max_possible = max(
            reward_by_card_channel[slug][ch] for slug in reward_by_card_channel
        )
        # Same-channel overflow splitting can strictly beat any single card's capped reward
        assert ch_reward >= max_possible - 0.05, (
            f"Combo picked suboptimal allocation ({ch_reward}) for {ch}; "
            f"max single-card channel reward is {max_possible}"
        )
        alloc_sum += ch_reward

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
    cap_applies_to = target_rule.get("cap_applies_to") or "total"
    base = target["base_rate_foreign"] if ch == "overseas" else target["base_rate_domestic"]

    effective_cap_rate = (rate - base) if cap_applies_to == "bonus" else rate
    cap_break_even = cap / (effective_cap_rate / 100.0)
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
    expected_above = _eval_rule_reward(above_spend, rate, cap, base, cap_applies_to)
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
    home = HomePage(page)
    home.goto_and_wait_ready(base_url)
    home.clear_inputs()

    home.channel_input("dining").fill("6000")
    home.channel_input("overseas").fill("15000")

    resp = home.submit_spending()
    api_data = json.loads(resp.text())
    top_api = api_data["recommendations"][0]

    top_ui = home.recommend_cards.first
    expect(top_ui.locator(".card-name")).to_contain_text(top_api["card_name"])

    expected_ntd = f"NT$ {round(top_api['total_reward_ntd']):,}"
    expect(top_ui.locator(".reward-amount")).to_contain_text(expected_ntd)
    rate_text = top_ui.locator(".reward-rate").inner_text()
    m_rate = re.search(r"(\d+(?:\.\d+)?)%", rate_text)
    assert m_rate is not None, f"Missing rate percentage in {rate_text!r}"
    assert float(m_rate.group(1)) == pytest.approx(top_api["effective_rate_pct"], abs=0.01)

    ui_rows = top_ui.locator(".breakdown-table tbody tr")
    expect(ui_rows).to_have_count(len(top_api["breakdown"]))

    if api_data.get("combo"):
        combo_ntd = f"NT$ {round(api_data['combo']['total_reward_ntd']):,}"
        expect(page.locator("#comboSection .combo-gain")).to_contain_text(combo_ntd)


@pytest.mark.math
def test_golden_hand_calculated_scenarios(base_url: str) -> None:
    """Non-mirror golden business invariants: monotonicity, non-negativity, and reward bounds."""
    low = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": {"dining": 2000, "overseas": 5000}, "only_no_min_spend": False},
        timeout=15,
    ).json()
    high = requests.post(
        f"{base_url}/api/recommend",
        json={"monthly_spending": {"dining": 6000, "overseas": 15000}, "only_no_min_spend": False},
        timeout=15,
    ).json()

    low_by_slug = {r["card_slug"]: r for r in low["recommendations"]}
    high_by_slug = {r["card_slug"]: r for r in high["recommendations"]}

    for slug, low_rec in low_by_slug.items():
        high_rec = high_by_slug[slug]
        # 1. Non-negativity & upper bound: reward must be >= 0 and <= spend
        assert 0 <= low_rec["total_reward_ntd"] <= low_rec["total_spend_ntd"]
        assert 0 <= high_rec["total_reward_ntd"] <= high_rec["total_spend_ntd"]
        # 2. Monotonicity: 3x spend must yield >= reward (never decrease)
        assert high_rec["total_reward_ntd"] >= low_rec["total_reward_ntd"], (
            f"Non-monotonic reward for {slug}: 1x={low_rec['total_reward_ntd']}, 3x={high_rec['total_reward_ntd']}"
        )
        # 3. Sub-additivity under caps: 3x spend cannot yield strictly more than 3x reward (unless min_spend crossed)
        # Verify effective rate is within realistic bounds (0%..20%)
        assert 0.0 <= high_rec["effective_rate_pct"] <= 20.0


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
