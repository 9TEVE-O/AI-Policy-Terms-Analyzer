"""Tests for the bounded URL-only controlled policy-analysis workflow."""

import json
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256
from http.client import HTTPResponse, IncompleteRead
from io import BytesIO
from email.message import Message
from unittest.mock import MagicMock, Mock, patch

import pytest

from controlled_policy_analysis import (
    ControlledPolicyAnalyzer,
    _FirstPartyRedirectHandler,
    _body_provenance,
    discover_policy_links,
    main,
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


def test_data_destination_passages_preserve_visible_text_and_source_identity():
    policy = (
        "<p>We do not share personal information with analytics providers.</p>"
        "<p>An older policy said we share personal information with analytics providers.</p>"
    )
    fetcher = FakeResourceFetcher({
        "https://example.com": {
            "text": '<a href="/privacy">Privacy Policy</a>',
            "content_type": "text/html",
        },
        "https://example.com/privacy": {
            "text": policy,
            "content_type": "text/html",
        },
    })
    document = ControlledPolicyAnalyzer(resource_fetcher=fetcher).analyze_site(
        "https://example.com"
    )["documents"][0]
    evidence = document["data_destination_passages"]
    visible = DocumentScanner().scan_html_content(policy)
    assert document["status"] == "analysed"
    assert evidence["source_url"] == "https://example.com/privacy"
    assert evidence["source_body_sha256"] is None
    assert evidence["text_basis"] == "visible_text_supplied_to_analyzer"
    assert evidence["coverage"] == "all_rule_matches"
    recipients = [p for p in evidence["passages"] if p["kind"] == "recipient"]
    assert len(recipients) == 2
    purposes = [p for p in evidence["passages"] if p["kind"] == "purpose"]
    assert len(purposes) == 2
    for passage in purposes:
        assert passage["label"] == "Usage analytics and telemetry"
        assert visible[passage["match_start"]:passage["match_end"]].lower() == "analytics"
        assert visible[passage["excerpt_start"]:passage["excerpt_end"]] == passage["excerpt"]
    for passage in recipients:
        assert passage["label"] == "analytics providers"
        assert visible[passage["excerpt_start"]:passage["excerpt_end"]] == passage["excerpt"]
        assert "share personal information with analytics providers" in (
            visible[passage["match_start"]:passage["match_end"]]
        )
        assert passage["review_status"] == "human_review_required"
    assert "do not share" in recipients[0]["excerpt"]
    assert "older policy" in recipients[1]["excerpt"]


def test_data_destination_passages_bound_occurrences_and_report_missing():
    from policy_analyzer import PolicyAnalyzer

    analyzer = PolicyAnalyzer()
    text = " ".join(["We share personal information with analytics providers."] * 4)
    destinations = analyzer.detect_data_destinations(text)
    evidence = analyzer.extract_data_destination_passages(text, destinations)
    recipients = [p for p in evidence["passages"] if p["kind"] == "recipient"]
    assert len(recipients) == 3
    assert evidence["omitted_occurrences"] >= 1
    assert evidence["coverage"] == "bounded"

    altered = analyzer.extract_data_destination_passages(
        text, {"recipients": ["fabricated recipient"], "purposes": []}
    )
    assert altered["passages"] == []
    assert altered["coverage"] == "incomplete"
    assert altered["unmatched_findings"] == [
        {"kind": "recipient", "label": "fabricated recipient"}
    ]


def test_data_destination_passages_unavailable_for_injected_analyzer():
    analyzer = Mock()
    analyzer.analyze.return_value = {"data_destinations": {"recipients": ["invented"]}}
    result = ControlledPolicyAnalyzer(
        analyzer=analyzer, resource_fetcher=FakeResourceFetcher()
    ).analyze_site("https://example.com")
    assert result["documents"][0]["data_destination_passages"]["coverage"] == (
        "unavailable_for_injected_analyzer"
    )
    assert result["documents"][0]["data_destination_passages"]["passages"] == []


def test_privacy_concern_passages_preserve_negation_history_and_offsets():
    policy = (
        "<p>We do not sell your personal information.</p>"
        "<p>An older policy said we sell your personal information.</p>"
        "<p>A third party may sell your personal information.</p>"
    )
    fetcher = FakeResourceFetcher({
        "https://example.com": {
            "text": '<a href="/privacy">Privacy Policy</a>',
            "content_type": "text/html",
        },
        "https://example.com/privacy": {
            "text": policy, "content_type": "text/html",
        },
    })
    document = ControlledPolicyAnalyzer(resource_fetcher=fetcher).analyze_site(
        "https://example.com"
    )["documents"][0]
    evidence = document["privacy_concern_passages"]
    assert document["analysis"]["privacy_concerns"]["high"]
    assert evidence["coverage"] == "all_rule_matches"
    assert evidence["other_analysis_fields"] == "not_mapped"
    assert evidence["source_url"] == "https://example.com/privacy"
    assert evidence["source_body_sha256"] is None
    assert len(evidence["passages"]) == 3
    visible = DocumentScanner().scan_html_content(policy)
    for passage in evidence["passages"]:
        assert visible[passage["excerpt_start"]:passage["excerpt_end"]] == passage["excerpt"]
        assert visible[passage["match_start"]:passage["match_end"]].lower().startswith("sell your")
        assert passage["review_status"] == "human_review_required"
    assert "do not sell" in evidence["passages"][0]["excerpt"]
    assert "older policy" in evidence["passages"][1]["excerpt"]
    assert "third party" in evidence["passages"][2]["excerpt"]


def test_privacy_passage_limit_is_explicit_and_not_complete_coverage():
    from policy_analyzer import PolicyAnalyzer

    analyzer = PolicyAnalyzer()
    text = " ".join(["We sell your personal information."] * 4)
    result = analyzer.extract_privacy_concern_passages(
        text, analyzer.detect_privacy_concerns(text)
    )
    assert len(result["passages"]) == 3
    assert result["omitted_occurrences"] == 1
    assert result["coverage"] == "bounded"


def test_injected_analyzer_marks_passage_coverage_unavailable():
    analyzer = Mock()
    analyzer.analyze.return_value = {"privacy_concerns": {"high": ["example"]}}
    document = ControlledPolicyAnalyzer(
        analyzer=analyzer, resource_fetcher=FakeResourceFetcher()
    ).analyze_site("https://example.com")["documents"][0]
    assert document["privacy_concern_passages"]["coverage"] == "unavailable_for_injected_analyzer"
    assert document["privacy_concern_passages"]["passages"] == []


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
    assert "privacy_concern_passages" not in document
    assert "data_destination_passages" not in document


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


class _WireSocket:
    def __init__(self, wire):
        self.wire = wire

    def makefile(self, *args, **kwargs):
        return BytesIO(self.wire)


def _wire_response(headers, body, status=200):
    wire = (
        b"HTTP/1.1 " + str(status).encode("ascii") + b" Test\r\n"
        + headers + b"\r\n" + body
    )
    response = HTTPResponse(_WireSocket(wire))
    response.begin()
    return response


_CHUNKED = b"3\r\nabc\r\n0\r\n\r\n"


@pytest.mark.parametrize(
    "headers,body,cap,status,eligible",
    [
        (b"Content-Length: 3\r\n", b"abc", 3, 200, True),
        (b"Content-Length: 0003\r\n", b"abc", 3, 200, True),
        (b"", b"abc", 3, 200, True),
        (b"Content-Length: 0\r\n", b"", 3, 200, True),
        (b"Content-Length: 4\r\n", b"abc", 8, 200, False),
        (b"Content-Length: 3\r\n", b"abc", 2, 200, False),
        (b"Transfer-Encoding: chunked\r\n", _CHUNKED, 3, 200, True),
        (b"Transfer-Encoding: Chunked\r\n", _CHUNKED, 3, 200, True),
        (b"Transfer-Encoding: chunked\r\nContent-Length: 3\r\n", _CHUNKED, 8, 200, False),
        (b"Transfer-Encoding: chunked\r\nTransfer-Encoding: chunked\r\n", _CHUNKED, 8, 200, False),
        (b"Transfer-Encoding: gzip, chunked\r\n", _CHUNKED, 30, 200, False),
        (b"Transfer-Encoding:\r\n", b"abc", 8, 200, False),
        (b"Content-Length: 3\r\nContent-Length: 3\r\n", b"abc", 8, 200, False),
        (b"Content-Length: +3\r\n", b"abc", 8, 200, False),
        (b"Content-Length: invalid\r\n", b"abc", 8, 200, False),
        (b"Content-Length: " + b"9" * 5000 + b"\r\n", b"abc", 8, 200, False),
        (b"Content-Range: bytes 0-2/5\r\nContent-Length: 3\r\n", b"abc", 8, 200, False),
        (b"Content-Length: 3\r\n", b"abc", 8, 206, False),
        (b"Content-Length: 3\r\n", b"abcd", 8, 200, True),
    ],
)
def test_body_provenance_real_reader(headers, body, cap, status, eligible):
    with _wire_response(headers, body, status) as response:
        raw = response.read(cap + 1)
        result = _body_provenance(response, raw, len(raw) > cap)
    assert bool(result) is eligible
    if eligible:
        provenance = result["source_provenance"]
        assert provenance["body_sha256"] == sha256(raw).hexdigest()
        assert provenance["body_bytes"] == len(raw)
        assert datetime.fromisoformat(provenance["retrieved_at_utc"]).utcoffset().total_seconds() == 0


@pytest.mark.parametrize("payload,charset", [
    (b"Privacy Policy. Cafe.", "utf-8"),
    (b"Privacy Policy. Caf\xc3\xa9.", "utf-8"),
    (b"Privacy Policy. Caf\xe9.", "iso-8859-1"),
    (b"Privacy Policy. Caf\xff.", "utf-8"),
])
def test_fingerprint_precedes_character_decoding(payload, charset):
    response, opener = _mock_response("text/plain; charset=" + charset)
    response.status = 200
    response.read.return_value = payload
    response.headers["Content-Length"] = str(len(payload))
    fixed = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
        with patch("controlled_policy_analysis.datetime") as clock:
            clock.now.return_value = fixed
            resource = ControlledPolicyAnalyzer()._fetch_first_party_resource(
                "https://example.com/privacy", "https://example.com"
            )
    assert resource["text"] == payload.decode(charset, errors="replace")
    assert resource["source_provenance"] == {
        "body_sha256": sha256(payload).hexdigest(),
        "body_bytes": len(payload),
        "retrieved_at_utc": fixed.isoformat(),
    }


@pytest.mark.parametrize("headers,body,cap,truncated,eligible", [
    (b"Content-Length: 3\r\n", b"abc", 3, False, True),
    (b"Content-Length: 0003\r\n", b"abc", 3, False, True),
    (b"Content-Length: 0\r\n", b"", 3, False, True),
    (b"Content-Length: 100\r\n", b"abc", 2, True, False),
    (b"Transfer-Encoding: chunked\r\n", _CHUNKED, 3, False, True),
    (b"Transfer-Encoding: chunked\r\nContent-Length: 100\r\n", _CHUNKED, 3, False, False),
    (b"Content-Length: 3\r\nContent-Length: 100\r\n", b"abc", 3, False, False),
    (b"Content-Length: invalid\r\n", b"abc", 3, False, False),
    (b"", b"abc", 3, False, True),
], ids=["exact-cap", "leading-zero", "empty", "capped", "chunked",
        "transfer-precedence", "ambiguous-length", "invalid-length", "eof"])
def test_fetch_preserves_complete_capped_and_ambiguous_reads(
    headers, body, cap, truncated, eligible,
):
    response, opener = _mock_response("text/plain")
    response.status = 200
    scanner = DocumentScanner()
    scanner._MAX_URL_BYTES = cap
    with _wire_response(headers, body) as wire:
        response.headers = wire.headers
        response.headers["Content-Type"] = "text/plain"
        response.chunked = wire.chunked
        response.read.side_effect = wire.read
        with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
            resource = ControlledPolicyAnalyzer(scanner=scanner)._fetch_first_party_resource(
                "https://example.com/privacy", "https://example.com"
            )
    assert resource["text"] == (b"abc" if body else b"")[:cap].decode()
    assert resource["truncated"] is truncated
    assert ("source_provenance" in resource) is eligible
    if eligible:
        assert resource["source_provenance"]["body_sha256"] == sha256(resource["text"].encode()).hexdigest()
    response.read.assert_called_once_with(cap + 1)


def test_default_fetcher_provenance_and_cli_json(capsys):
    homepage, opener = _mock_response("text/html")
    homepage.geturl.return_value = "https://example.com"
    homepage.status = 200
    homepage.read.return_value = b'<a href="/privacy">Privacy Policy</a>'
    policy, _ = _mock_response("text/plain; charset=iso-8859-1")
    policy.status = 200
    payload = b"Privacy Policy. We use AWS. Caf\xe9."
    policy.read.return_value = payload
    opener.open.side_effect = [homepage, policy]
    with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
        with patch("sys.argv", ["controlled_policy_analysis.py", "https://example.com"]):
            main()
    result = json.loads(capsys.readouterr().out)
    document = result["documents"][0]
    assert document["status"] == "analysed"
    assert document["source_provenance"]["body_sha256"] == sha256(payload).hexdigest()
    assert (
        document["privacy_concern_passages"]["source_body_sha256"]
        == document["source_provenance"]["body_sha256"]
    )
    assert "source_provenance" not in result
    assert document["analysis"]["company_name"] == "example.com"


class _EqualitySpoofingFetcher(FakeResourceFetcher):
    def __eq__(self, other):
        return True

    def __call__(self, url, boundary_url):
        resource = super().__call__(url, boundary_url)
        resource["source_provenance"] = {"body_sha256": "not trusted"}
        return resource


def test_injected_equal_fetcher_cannot_supply_provenance():
    fetcher = _EqualitySpoofingFetcher()
    controlled = ControlledPolicyAnalyzer(resource_fetcher=fetcher)
    assert fetcher == controlled._fetch_first_party_resource
    assert fetcher is not controlled._default_resource_fetcher
    for document in controlled.analyze_site("https://example.com")["documents"]:
        assert document["status"] == "analysed"
        assert "source_provenance" not in document
        assert document["privacy_concern_passages"]["source_body_sha256"] is None


@pytest.mark.parametrize("headers,body", [
    (b"Transfer-Encoding: chunked\r\n", b"3\r\nabc\r\n"),
    (b"Content-Length: 100\r\n", b"Privacy Policy. We use AWS."),
    (b"Content-Length: 000100\r\n", b"Privacy Policy. We use AWS."),
    (b"Content-Length: 1\r\n", b""),
    (b"Content-Length: " + b"9" * 5000 + b"\r\n", b"Privacy Policy."),
], ids=["chunked", "short", "leading-zero", "empty", "huge-length"])
def test_incomplete_policy_read_continues_to_next_candidate(headers, body):
    homepage, opener = _mock_response("text/html")
    homepage.geturl.return_value = "https://example.com"
    homepage.read.return_value = (
        b'<a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Service</a>'
    )
    bad, _ = _mock_response("text/plain")
    good, _ = _mock_response("text/plain")
    good.geturl.return_value = "https://example.com/terms"
    good.status = 200
    analyzer = Mock()
    analyzer.analyze.return_value = {"company_name": "example.com"}
    with _wire_response(headers, body) as wire:
        bad.headers = wire.headers
        bad.headers["Content-Type"] = "text/plain"
        bad.read.side_effect = wire.read
        opener.open.side_effect = [homepage, bad, good]
        with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
            documents = ControlledPolicyAnalyzer(analyzer=analyzer).analyze_site("https://example.com")["documents"]
    assert documents[0]["status"] == "fetch_failed"
    assert "Incomplete remote response body" in documents[0]["reason"]
    assert documents[0]["analysis"] is None
    assert "source_provenance" not in documents[0]
    assert documents[1]["status"] == "analysed"
    assert "source_provenance" in documents[1]
    analyzer.analyze.assert_called_once_with(good.read.return_value.decode(), "example.com")


@pytest.mark.parametrize("headers,body", [
    (b"Transfer-Encoding: chunked\r\n", b"3\r\nabc\r\n"),
    (b"Content-Length: 100\r\n", b'<a href="/privacy">Privacy Policy</a>'),
], ids=["chunked", "short"])
def test_incomplete_homepage_read_has_no_json_output(capsys, headers, body):
    homepage, opener = _mock_response("text/html")
    homepage.geturl.return_value = "https://example.com"
    homepage.status = 200
    with _wire_response(headers, body) as wire:
        homepage.headers = wire.headers
        homepage.headers["Content-Type"] = "text/html"
        homepage.read.side_effect = wire.read
        with patch("controlled_policy_analysis.build_public_opener", return_value=opener):
            with patch("sys.argv", ["controlled_policy_analysis.py", "https://example.com"]):
                with patch("controlled_policy_analysis.discover_policy_links", wraps=discover_policy_links) as discover:
                    with pytest.raises(ValueError, match="Incomplete remote response body") as exc:
                        main()
    if headers.startswith(b"Transfer-Encoding"):
        assert isinstance(exc.value.__cause__, IncompleteRead)
    discover.assert_not_called()
    assert opener.open.call_count == 1
    assert capsys.readouterr().out == ""
