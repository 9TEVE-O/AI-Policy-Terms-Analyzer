"""Tests for the bounded URL-only controlled policy-analysis workflow."""

from controlled_policy_analysis import ControlledPolicyAnalyzer, discover_policy_links


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


class FakeScanner:
    def __init__(self):
        self.pages = {
            "https://example.com": HOMEPAGE,
            "https://example.com/privacy": (
                "Privacy Policy\nWe use AWS and Stripe. "
                "We may share data with payment processors."
            ),
            "https://example.com/terms-of-service": (
                "Terms of Service\nAutomated scraping is prohibited."
            ),
            "https://legal.example.com/cookies": (
                "Cookie Policy\nWe use analytics providers."
            ),
        }
        self.scanned_urls = []

    def _fetch_url(self, url):
        return self.pages[url]

    def scan_url(self, url):
        self.scanned_urls.append(url)
        return self.pages[url]


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
    assert excluded["https://example.com/blog/privacy-engineering"] == "content_page_path"

    assert result["categories_found"][:3] == ["privacy", "terms", "cookies"]
    assert "acceptable_use" in result["categories_not_found"]


def test_analyze_site_runs_existing_analyzer_with_provenance():
    scanner = FakeScanner()
    result = ControlledPolicyAnalyzer(scanner=scanner).analyze_site("https://example.com")

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
    assert privacy["analysis"]["company_name"] == "example.com"
    assert "aws" in privacy["analysis"]["technologies_detected"].get("platforms", [])

    assert "https://vendor.example.net/privacy" not in scanner.scanned_urls


def test_document_limit_is_enforced_after_discovery():
    scanner = FakeScanner()
    result = ControlledPolicyAnalyzer(scanner=scanner).analyze_site(
        "https://example.com",
        max_documents=2,
    )

    assert result["documents_discovered"] == 3
    assert result["documents_selected"] == 2
    assert len(scanner.scanned_urls) == 2


def test_remote_pdf_is_reported_without_attempting_html_analysis():
    homepage = '<a href="/legal/privacy-policy.pdf">Privacy Policy</a>'

    class PdfScanner(FakeScanner):
        def __init__(self):
            self.pages = {"https://example.com": homepage}
            self.scanned_urls = []

    scanner = PdfScanner()
    result = ControlledPolicyAnalyzer(scanner=scanner).analyze_site("https://example.com")

    assert result["documents_selected"] == 1
    document = result["documents"][0]
    assert document["status"] == "not_analysed"
    assert document["reason"] == "remote_pdf_not_supported_in_controlled_v0.1"
    assert scanner.scanned_urls == []


def test_invalid_homepage_scheme_is_rejected():
    try:
        discover_policy_links("file:///etc/passwd", HOMEPAGE)
        assert False, "Expected ValueError for non-http homepage"
    except ValueError:
        pass
