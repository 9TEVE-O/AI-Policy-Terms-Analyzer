"""Tests for the bounded URL-only controlled policy-analysis workflow."""

import urllib.request

from controlled_policy_analysis import (
    ControlledPolicyAnalyzer,
    _FirstPartyRedirectHandler,
    discover_policy_links,
)
from document_scanner import DocumentScanner


HOMEPAGE = """
<html><body>
  <a href="/privacy">Privacy Policy</a>
  <a href="https://example.com/terms-of-service">Terms of Service</a>
  <a href="https://legal.example.com/cookies">Cookie Policy</a>
  <a href="https://vendor.example.net/privacy">Vendor Privacy Policy</a>
  <a href="/blog/privacy-engineering">Privacy engineering</a>
  <a href="mailto:privacy@example.com">Privacy contact</a>
</body></html>
"""


class FakeResourceFetcher:
    def __init__(self, pages=None):
        self.pages = pages or {
            "https://example.com": {
                "text": HOMEPAGE,
                "content_type": "text/html; charset=utf-8",
            },
            "https://example.com/privacy": {
                "text": (
                    "Privacy Policy\nWe use AWS and Stripe. "
                    "We may share data with payment processors."
                ),
                "content_type": "text/html; charset=utf-8",
            },
            "https://example.com/terms-of-service": {
                "text": "Terms of Service\nAutomated scraping is prohibited.",
                "content_type": "text/html; charset=utf-8",
            },
            "https://legal.example.com/cookies": {
                "text": "Cookie Policy\nWe use analytics providers.",
                "content_type": "text/html; charset=utf-8",
            },
        }
        self.calls = []

    def __call__(self, url, boundary_url):
        self.calls.append((url, boundary_url))
        page = self.pages[url]
        return {
            "requested_url": url,
            "final_url": page.get("final_url", url),
            "content_type": page.get("content_type", "text/html"),
            "text": page.get("text", ""),
            "truncated": page.get("truncated", False),
        }


def test_discovery_selects_first_party_and_records_exclusions():
    result = discover_policy_links("https://example.com", HOMEPAGE)

    selected_urls = {item["url"] for item in result["selected"]}
    assert "https://example.com/privacy" in selected_urls
    assert "https://example.com/terms-of-service" in selected_urls
    assert "https://legal.example.com/cookies" in selected_urls
    assert "https://vendor.example.net/privacy" not in selected_urls
    assert "https://example.com/blog/privacy-engineering" not in selected_urls

    excluded = {
        item["url"]: item["reason"]
        for item in result["excluded_policy_candidates"]
    }
    assert excluded["https://vendor.example.net/privacy"] == "external_host"
    assert (
        excluded["https://example.com/blog/privacy-engineering"]
        == "content_page_path"
    )

    assert result["categories_found"][:3] == ["privacy", "terms", "cookies"]
    assert "acceptable_use" in result["categories_not_found"]


def test_analyze_site_runs_existing_analyzer_with_provenance():
    fetcher = FakeResourceFetcher()
    analyzer = ControlledPolicyAnalyzer(
        scanner=DocumentScanner(),
        resource_fetcher=fetcher,
    )
    result = analyzer.analyze_site("https://example.com")

    assert result["discovery_scope"] == "homepage_links_one_hop"
    assert result["documents_discovered"] == 3
    assert result["documents_selected"] == 3
    assert len(result["documents"]) == 3
    assert all(item["status"] == "analysed" for item in result["documents"])

    privacy = next(
        item for item in result["documents"]
        if "privacy" in item["categories"]
    )
    assert privacy["discovered_from"] == "https://example.com"
    assert privacy["final_url"] == "https://example.com/privacy"
    assert privacy["analysis"]["company_name"] == "example.com"
    assert "aws" in privacy["analysis"]["technologies_detected"].get(
        "platforms",
        [],
    )

    fetched_urls = {url for url, _boundary in fetcher.calls}
    assert "https://vendor.example.net/privacy" not in fetched_urls


def test_document_limit_is_enforced_after_discovery():
    fetcher = FakeResourceFetcher()
    result = ControlledPolicyAnalyzer(
        scanner=DocumentScanner(),
        resource_fetcher=fetcher,
    ).analyze_site(
        "https://example.com",
        max_documents=2,
    )

    assert result["documents_discovered"] == 3
    assert result["documents_selected"] == 2
    assert len(fetcher.calls) == 3  # homepage plus two selected documents


def test_remote_pdf_is_reported_without_text_analysis():
    homepage = '<a href="/legal/privacy-policy.pdf">Privacy Policy</a>'
    fetcher = FakeResourceFetcher(
        {
            "https://example.com": {
                "text": homepage,
                "content_type": "text/html",
            },
            "https://example.com/legal/privacy-policy.pdf": {
                "text": "",
                "content_type": "application/pdf",
            },
        }
    )

    result = ControlledPolicyAnalyzer(
        scanner=DocumentScanner(),
        resource_fetcher=fetcher,
    ).analyze_site("https://example.com")

    assert result["documents_selected"] == 1
    document = result["documents"][0]
    assert document["status"] == "not_analysed"
    assert document["reason"] == "remote_pdf_not_supported_in_controlled_v0.1"
    assert document["analysis"] is None


def test_cross_host_redirect_is_blocked_by_transport_handler():
    handler = _FirstPartyRedirectHandler("https://example.com")
    request = urllib.request.Request("https://example.com/privacy")

    try:
        handler.redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://vendor.example.net/privacy",
        )
        assert False, "Expected cross-host redirect to be blocked"
    except ValueError as exc:
        assert "Cross-host redirect blocked" in str(exc)


def test_invalid_homepage_scheme_is_rejected():
    try:
        discover_policy_links("file:///etc/passwd", HOMEPAGE)
        assert False, "Expected ValueError for non-http homepage"
    except ValueError:
        pass
