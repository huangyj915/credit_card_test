from __future__ import annotations

import pytest
import requests

from reporting.classifier import redact_secrets
from reporting.excel_writer import sanitize_excel_text
from tests.test_official_rate_sync import is_approved_bank_url


@pytest.mark.security
def test_write_endpoints_protected_when_locked(base_url: str) -> None:
    """Verify all mutating/scraper endpoints reject unauthenticated requests when locked."""
    cfg = requests.get(f"{base_url}/api/config", timeout=15).json()
    if not cfg.get("admin_protected") and not cfg.get("public_readonly"):
        pytest.skip("Target instance is running without admin_protected or public_readonly lock")

    checks = [
        ("POST", "/api/scrape", {"bank_codes": ["cathay"], "mode": "demo_html"}),
        ("POST", "/api/scrape/custom", {"card_name": "CUBE 卡", "mode": "live"}),
        ("POST", "/api/banks/cathay/discover", None),
        ("POST", "/api/cards", {"bank_name": "Test", "card_name": "Test"}),
    ]
    for method, path, payload in checks:
        resp = requests.request(method, f"{base_url}{path}", json=payload, timeout=15)
        assert resp.status_code in {401, 403, 405}, (
            f"Endpoint {method} {path} returned {resp.status_code} without admin credentials"
        )


@pytest.mark.security
def test_scrape_logs_limit_boundary_rejected_or_clamped(base_url: str) -> None:
    """Verify extreme or negative limit query parameters on /api/scrape-logs are safely handled."""
    high_resp = requests.get(f"{base_url}/api/scrape-logs?limit=999999", timeout=15)
    assert high_resp.status_code in {200, 400, 422}
    if high_resp.status_code == 200:
        data = high_resp.json()
        assert isinstance(data, list)
        assert len(data) <= 200, f"Unbounded /api/scrape-logs response length: {len(data)}"

    neg_resp = requests.get(f"{base_url}/api/scrape-logs?limit=-1", timeout=15)
    assert neg_resp.status_code in {200, 400, 422}
    if neg_resp.status_code == 200:
        assert isinstance(neg_resp.json(), list)


@pytest.mark.security
def test_excel_formula_injection_and_secret_redaction() -> None:
    """Verify report writers neutralize Excel formula injection and redact sensitive tokens."""
    assert sanitize_excel_text("=CMD|' /C calc'!A0").startswith("'=")
    assert sanitize_excel_text("+1+1").startswith("'+")
    assert sanitize_excel_text("-2+3").startswith("'-")
    assert sanitize_excel_text("@SUM(1,2)").startswith("'@")
    assert sanitize_excel_text("\t=1+1").startswith("'\t")
    assert sanitize_excel_text("-") == "-"
    assert sanitize_excel_text("Normal text 3.5%") == "Normal text 3.5%"

    redacted = redact_secrets("Headers: X-Admin-Token: supersecret123, Authorization: Bearer eyJhbGciOi.abc.def")
    assert "supersecret123" not in redacted
    assert "eyJhbGciOi" not in redacted
    assert "[REDACTED]" in redacted


@pytest.mark.security
def test_official_url_allowlist_blocks_untrusted_schemes_and_hosts() -> None:
    """Verify official_url validator blocks non-HTTPS, localhost/SSRF, and untrusted domains."""
    assert is_approved_bank_url("https://www.cathaybk.com.tw/cathaybk/personal/product/credit-card/cards/cube/")
    assert is_approved_bank_url("https://www.esunbank.com/zh-tw/personal/credit-card/intro/bank-card/u-bear")
    assert not is_approved_bank_url("http://www.cathaybk.com.tw/insecure")
    assert not is_approved_bank_url("file:///etc/passwd")
    assert not is_approved_bank_url("https://127.0.0.1:8000/admin")
    assert not is_approved_bank_url("https://169.254.169.254/latest/meta-data/")
    assert not is_approved_bank_url("https://evil.example/cathaybk.com.tw")
