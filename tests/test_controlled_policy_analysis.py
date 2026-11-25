"""Tests for the bounded URL-only controlled policy-analysis workflow."""

import urllib.request
from email.message import Message
from unittest.mock import MagicMock, Mock, patch

import pytest

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


def test_www_homepage_uses_boundary_host_for_analysis_identity():
    homepage = '<a href="/privacy">Privacy Policy</a>'
    fetcher = FakeResourceFetcher(
        {
            "https://www.example.com": {
                "text": homepage,
                "content_type": "text/html",
            },
            "https://www.example.com/privacy": {
                "text": "Privacy Policy\nWe use AWS.",
                "content_type": "text/html",
            },
        }
    )

    result = ControlledPolicyAnalyzer(
        scanner=DocumentScanner(),
        resource_fetcher=fetcher,
    ).analyze_site("https://www.example.com")

    assert result["site_host"] == "example.com"
    assert result["documents"][0]["analysis"]["company_name"] == "example.com"


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


def test_truncated_policy_is_not_presented_as_completed_analysis():
    fetcher = FakeResourceFetcher(
        {
            "https://example.com": {
                "text": '<a href="/privacy">Privacy Policy</a>',
                "content_type": "text/html",
            },
            "https://example.com/privacy": {
                "text": "Privacy Policy. We use Stripe.",
                "content_type": "text/html",
                "truncated": True,
            },
        }
    )
    result = ControlledPolicyAnalyzer(resource_fetcher=fetcher).analyze_site(
        "https://example.com"
    )
    document = result["documents"][0]
    assert document["truncated"] is True
    assert document["status"] == "not_analysed"
    assert document["reason"] == "document_truncated"
    assert document["analysis"] is None


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


INELIGIBLE_MEDIA = [
    ("application/octet-stream", "unsupported_content_type"),
    ("image/png", "unsupported_content_type"),
    ("text/htmlx", "unsupported_content_type"),
    ("text/html, image/png", "unsupported_content_type"),
    ("", "missing_content_type"),
    ("application/pdf", "remote_pdf_not_supported_in_controlled_v0.1"),
]


def _mock_response(content_type):
    response = MagicMock()
    response.__enter__.return_value = response
    response.geturl.return_value = "https://example.com/privacy"
    response.headers = Message()
    if content_type:
        response.headers["Content-Type"] = content_type
    response.read.return_value = b"Privacy Policy. We use AWS."
    opener = Mock()
    opener.open.return_value = response
    return response, opener


@pytest.mark.parametrize("content_type,reason", INELIGIBLE_MEDIA)
def test_ineligible_controlled_fetch_does_not_read_body(content_type, reason):
    response, opener = _mock_response(content_type)
    controlled = ControlledPolicyAnalyzer()
    with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
        result = controlled._fetch_first_party_resource(
            "https://example.com/privacy", "https://example.com"
        )
    assert result["content_type"] == content_type
    assert result["text"] == ""
    response.read.assert_not_called()


@pytest.mark.parametrize("content_type,reason", INELIGIBLE_MEDIA)
def test_ineligible_policy_never_invokes_analyzer(content_type, reason):
    fetcher = FakeResourceFetcher({
        "https://example.com": {"text": '<a href="/privacy">Privacy Policy</a>'},
        "https://example.com/privacy": {
            "text": "Privacy Policy. We use AWS.",
            "content_type": content_type,
        },
    })
    analyzer = Mock()
    scanner = Mock(wraps=DocumentScanner())
    result = ControlledPolicyAnalyzer(
        scanner=scanner, analyzer=analyzer, resource_fetcher=fetcher
    ).analyze_site("https://example.com")
    document = result["documents"][0]
    assert document["status"] == "not_analysed"
    assert document["reason"] == reason
    assert document["analysis"] is None
    scanner.scan_html_content.assert_not_called()
    analyzer.analyze.assert_not_called()


@pytest.mark.parametrize("content_type,reason", INELIGIBLE_MEDIA)
def test_ineligible_homepage_stops_before_discovery(content_type, reason):
    fetcher = FakeResourceFetcher({
        "https://example.com": {
            "text": '<a href="/privacy">Privacy Policy</a>',
            "content_type": content_type,
        },
    })
    analyzer = Mock()
    controlled = ControlledPolicyAnalyzer(analyzer=analyzer, resource_fetcher=fetcher)
    with patch("controlled_policy_analysis.discover_policy_links") as discover:
        with pytest.raises(ValueError, match=reason):
            controlled.analyze_site("https://example.com")
    discover.assert_not_called()
    analyzer.analyze.assert_not_called()
    assert len(fetcher.calls) == 1


@pytest.mark.parametrize("content_type", [
    "text/html", "TEXT/PLAIN; charset=utf-8", "application/xhtml+xml",
])
def test_eligible_media_preserves_fetch_and_analysis(content_type):
    response, opener = _mock_response(content_type)
    controlled = ControlledPolicyAnalyzer()
    with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
        result = controlled._fetch_first_party_resource(
            "https://example.com/privacy", "https://example.com"
        )
    assert result["text"] == "Privacy Policy. We use AWS."
    response.read.assert_called_once_with(controlled.scanner._MAX_URL_BYTES + 1)

    fetcher = FakeResourceFetcher({
        "https://example.com": {"text": '<a href="/privacy">Privacy Policy</a>'},
        "https://example.com/privacy": {
            "text": result["text"], "content_type": content_type,
        },
    })
    analyzer = Mock()
    controlled = ControlledPolicyAnalyzer(analyzer=analyzer, resource_fetcher=fetcher)
    document = controlled.analyze_site("https://example.com")["documents"][0]
    assert document["status"] == "analysed"
    analyzer.analyze.assert_called_once()


@pytest.mark.parametrize("homepage", [
    '<a href="/privacy">Privacy Policy</a>',
    "<html><body>",
])
def test_truncated_homepage_stops_before_discovery(homepage):
    fetcher = FakeResourceFetcher({
        "https://example.com": {"text": homepage, "truncated": True},
        "https://example.com/privacy": {"text": "Privacy Policy. We use AWS."},
    })
    analyzer = Mock()
    controlled = ControlledPolicyAnalyzer(analyzer=analyzer, resource_fetcher=fetcher)
    with patch("controlled_policy_analysis.discover_policy_links") as discover:
        with pytest.raises(ValueError, match="homepage_truncated"):
            controlled.analyze_site("https://example.com")
    discover.assert_not_called()
    analyzer.analyze.assert_not_called()
    assert fetcher.calls == [("https://example.com", "https://example.com")]


@pytest.mark.parametrize("homepage,expected", [
    ('<a href="/privacy">Privacy Policy</a>', 1),
    ("<html></html>", 0),
])
def test_complete_homepage_preserves_bounded_discovery(homepage, expected):
    fetcher = FakeResourceFetcher({
        "https://example.com": {"text": homepage, "truncated": False},
        "https://example.com/privacy": {"text": "Privacy Policy. We use AWS."},
    })
    analyzer = Mock()
    result = ControlledPolicyAnalyzer(
        analyzer=analyzer, resource_fetcher=fetcher,
    ).analyze_site("https://example.com")
    assert result["homepage_truncated"] is False
    assert result["documents_discovered"] == expected
    assert len(result["documents"]) == expected
    assert ("privacy" in result["categories_found"]) == bool(expected)
    assert ("privacy" in result["categories_not_found"]) != bool(expected)
    assert analyzer.analyze.call_count == expected
    assert len(fetcher.calls) == expected + 1


def test_ineligible_truncated_homepage_preserves_media_rejection():
    fetcher = FakeResourceFetcher({
        "https://example.com": {
            "text": "", "content_type": "application/pdf", "truncated": True,
        },
    })
    with patch("controlled_policy_analysis.discover_policy_links") as discover:
        with pytest.raises(ValueError, match="remote_pdf_not_supported"):
            ControlledPolicyAnalyzer(resource_fetcher=fetcher).analyze_site(
                "https://example.com"
            )
    discover.assert_not_called()
    assert len(fetcher.calls) == 1
