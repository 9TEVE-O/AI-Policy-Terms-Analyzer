#!/usr/bin/env python3
"""Controlled first-party policy discovery and analysis.

Bounded workflow:

homepage URL -> one-hop first-party policy discovery -> validated fetch ->
existing PolicyAnalyzer extraction -> provenance-bearing JSON.

This is not a general crawler, legal analyser, compliance checker, or safety
verdict system.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

from document_scanner import DocumentScanner
from policy_analyzer import PolicyAnalyzer


_POLICY_PATTERNS = {
    "privacy": (
        "privacy policy",
        "privacy notice",
        "privacy statement",
        "privacy",
    ),
    "terms": (
        "terms of service",
        "terms of use",
        "terms and conditions",
        "terms & conditions",
        "service terms",
        "terms",
    ),
    "cookies": (
        "cookie policy",
        "cookies policy",
        "cookie notice",
        "cookies",
        "cookie",
    ),
    "acceptable_use": (
        "acceptable use policy",
        "acceptable use",
        "usage policy",
        "aup",
    ),
    "ai_terms": (
        "ai terms",
        "ai policy",
        "artificial intelligence terms",
        "generative ai terms",
        "generative ai policy",
    ),
    "data_processing": (
        "data processing agreement",
        "data processing addendum",
        "data protection addendum",
        "data processing",
        "dpa",
    ),
    "subscription_billing": (
        "subscription terms",
        "billing terms",
        "payment terms",
        "refund policy",
        "cancellation policy",
    ),
}

_CATEGORY_ORDER = {
    "privacy": 0,
    "terms": 1,
    "cookies": 2,
    "acceptable_use": 3,
    "ai_terms": 4,
    "data_processing": 5,
    "subscription_billing": 6,
}

_NEGATIVE_PATH_MARKERS = (
    "/blog/",
    "/news/",
    "/press/",
    "/careers/",
    "/jobs/",
)

_STRONG_POLICY_PHRASES = (
    "privacy policy",
    "privacy notice",
    "terms of service",
    "terms of use",
    "terms and conditions",
    "cookie policy",
    "acceptable use policy",
    "data processing agreement",
    "data processing addendum",
    "subscription terms",
)


class _PolicyLinkParser(HTMLParser):
    """Collect href values and visible anchor text from a page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: List[Tuple[str, str]] = []
        self._href: Optional[str] = None
        self._text_parts: List[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: Iterable[Tuple[str, Optional[str]]],
    ) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href.strip()
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._href is None:
            return
        label = " ".join(" ".join(self._text_parts).split())
        self.links.append((self._href, label))
        self._href = None
        self._text_parts = []


def _normalise_http_url(base_url: str, href: str) -> Optional[str]:
    """Resolve and normalise an HTTP(S) link; reject unsupported forms."""
    if not href:
        return None

    absolute = urljoin(base_url, href.strip())
    absolute, _fragment = urldefrag(absolute)
    parsed = urlparse(absolute)

    if parsed.scheme.lower() not in {"http", "https"}:
        return None
    if not parsed.hostname or parsed.username or parsed.password:
        return None

    normalised = parsed._replace(scheme=parsed.scheme.lower(), fragment="")
    return urlunparse(normalised)


def _site_boundary_host(homepage_url: str) -> str:
    """Return the conservative host boundary used for first-party discovery."""
    host = (urlparse(homepage_url).hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        return host[4:]
    return host


def _is_first_party(homepage_url: str, candidate_url: str) -> bool:
    """Treat the site host and its subdomains as first party."""
    boundary = _site_boundary_host(homepage_url)
    candidate_host = (urlparse(candidate_url).hostname or "").lower().rstrip(".")
    if not boundary or not candidate_host:
        return False
    return candidate_host == boundary or candidate_host.endswith("." + boundary)


class _FirstPartyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Allow redirects only when the target remains inside the site boundary."""

    def __init__(self, boundary_url: str) -> None:
        super().__init__()
        self.boundary_url = boundary_url

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        resolved = _normalise_http_url(req.full_url, newurl)
        if not resolved or not _is_first_party(self.boundary_url, resolved):
            raise ValueError(
                f"Cross-host redirect blocked: {req.full_url!r} -> {newurl!r}"
            )
        return super().redirect_request(req, fp, code, msg, headers, resolved)


def _classify_policy_link(url: str, label: str) -> Tuple[List[str], List[str], int]:
    """Return categories, matched terms, and an evidence score for a link."""
    parsed = urlparse(url)
    path_text = parsed.path.lower().replace("-", " ").replace("_", " ")
    label_text = label.lower()

    categories: List[str] = []
    matches: List[str] = []
    score = 0

    for category, patterns in _POLICY_PATTERNS.items():
        category_matched = False
        for phrase in patterns:
            anchor_hit = phrase in label_text
            path_hit = phrase in path_text
            if anchor_hit or path_hit:
                category_matched = True
                matches.append(phrase)
                if anchor_hit:
                    score += 2
                if path_hit:
                    score += 2
        if category_matched:
            categories.append(category)

    combined = f"{label_text} {path_text}"
    if "/legal" in parsed.path.lower() or " policy" in combined:
        score += 1

    categories.sort(key=lambda item: _CATEGORY_ORDER[item])
    return categories, sorted(set(matches)), score


def discover_policy_links(homepage_url: str, homepage_html: str) -> Dict:
    """Discover policy-looking links from one homepage only."""
    normalised_homepage = _normalise_http_url(homepage_url, homepage_url)
    if not normalised_homepage:
        raise ValueError(
            f"A valid http/https homepage URL is required: {homepage_url!r}"
        )

    parser = _PolicyLinkParser()
    parser.feed(homepage_html or "")

    selected_by_url: Dict[str, Dict] = {}
    excluded_by_url: Dict[str, Dict] = {}

    for href, label in parser.links:
        candidate = _normalise_http_url(normalised_homepage, href)
        if not candidate:
            continue

        categories, matched_terms, score = _classify_policy_link(candidate, label)
        if not categories:
            continue

        path_lower = urlparse(candidate).path.lower()
        looks_like_content_page = any(
            marker in path_lower for marker in _NEGATIVE_PATH_MARKERS
        )
        strong_phrase = any(
            phrase in f"{label.lower()} {path_lower.replace('-', ' ')}"
            for phrase in _STRONG_POLICY_PHRASES
        )
        if looks_like_content_page and not strong_phrase:
            excluded_by_url[candidate] = {
                "url": candidate,
                "label": label,
                "categories": categories,
                "matched_terms": matched_terms,
                "score": score,
                "reason": "content_page_path",
            }
            continue

        if not _is_first_party(normalised_homepage, candidate):
            excluded_by_url[candidate] = {
                "url": candidate,
                "label": label,
                "categories": categories,
                "matched_terms": matched_terms,
                "score": score,
                "reason": "external_host",
            }
            continue

        existing = selected_by_url.get(candidate)
        if existing:
            existing["categories"] = sorted(
                set(existing["categories"]) | set(categories),
                key=lambda item: _CATEGORY_ORDER[item],
            )
            existing["matched_terms"] = sorted(
                set(existing["matched_terms"]) | set(matched_terms)
            )
            existing["score"] = max(existing["score"], score)
            if not existing["label"] and label:
                existing["label"] = label
            continue

        selected_by_url[candidate] = {
            "url": candidate,
            "label": label,
            "categories": categories,
            "matched_terms": matched_terms,
            "score": score,
            "discovered_from": normalised_homepage,
        }

    selected = list(selected_by_url.values())
    selected.sort(
        key=lambda item: (
            min(_CATEGORY_ORDER[category] for category in item["categories"]),
            -item["score"],
            item["url"],
        )
    )

    excluded = list(excluded_by_url.values())
    excluded.sort(key=lambda item: (item["reason"], item["url"]))

    found_categories = sorted(
        {category for item in selected for category in item["categories"]},
        key=lambda item: _CATEGORY_ORDER[item],
    )
    not_found = [
        category for category in _CATEGORY_ORDER if category not in found_categories
    ]

    return {
        "homepage_url": normalised_homepage,
        "scope": "homepage_links_one_hop",
        "selected": selected,
        "excluded_policy_candidates": excluded,
        "categories_found": found_categories,
        "categories_not_found": not_found,
    }


class ControlledPolicyAnalyzer:
    """Run bounded first-party policy discovery and existing extraction."""

    def __init__(
        self,
        scanner: Optional[DocumentScanner] = None,
        analyzer: Optional[PolicyAnalyzer] = None,
        resource_fetcher=None,
    ) -> None:
        self.scanner = scanner or DocumentScanner()
        self.analyzer = analyzer or PolicyAnalyzer()
        self.resource_fetcher = resource_fetcher or self._fetch_first_party_resource

    def _fetch_first_party_resource(self, url: str, boundary_url: str) -> Dict:
        """Fetch one resource while blocking redirects outside the site boundary."""
        opener = urllib.request.build_opener(_FirstPartyRedirectHandler(boundary_url))
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self.scanner._USER_AGENT},
        )

        with opener.open(request, timeout=self.scanner._URL_TIMEOUT) as response:
            final_url = _normalise_http_url(url, response.geturl())
            if not final_url or not _is_first_party(boundary_url, final_url):
                raise ValueError(
                    f"Final URL left first-party boundary: {response.geturl()!r}"
                )

            content_type = response.headers.get("Content-Type", "")
            if "application/pdf" in content_type.lower():
                return {
                    "requested_url": url,
                    "final_url": final_url,
                    "content_type": content_type,
                    "text": "",
                    "truncated": False,
                }

            raw = response.read(self.scanner._MAX_URL_BYTES + 1)
            truncated = len(raw) > self.scanner._MAX_URL_BYTES
            raw = raw[: self.scanner._MAX_URL_BYTES]
            charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")

        return {
            "requested_url": url,
            "final_url": final_url,
            "content_type": content_type,
            "text": text,
            "truncated": truncated,
        }

    def analyze_site(self, homepage_url: str, max_documents: int = 8) -> Dict:
        if max_documents < 1:
            raise ValueError("max_documents must be at least 1")

        requested_homepage = _normalise_http_url(homepage_url, homepage_url)
        if not requested_homepage:
            raise ValueError(
                f"A valid http/https homepage URL is required: {homepage_url!r}"
            )

        homepage_resource = self.resource_fetcher(
            requested_homepage,
            requested_homepage,
        )
        final_homepage = homepage_resource["final_url"]
        discovery = discover_policy_links(
            final_homepage,
            homepage_resource["text"],
        )

        selected = discovery["selected"][:max_documents]
        site_host = _site_boundary_host(final_homepage) or "Unknown"
        documents: List[Dict] = []

        for candidate in selected:
            document = {
                "url": candidate["url"],
                "label": candidate["label"],
                "categories": candidate["categories"],
                "matched_terms": candidate["matched_terms"],
                "discovered_from": candidate["discovered_from"],
            }

            try:
                resource = self.resource_fetcher(candidate["url"], final_homepage)
            except (ValueError, urllib.error.URLError, OSError) as exc:
                document.update(
                    {
                        "status": "fetch_failed",
                        "reason": f"{type(exc).__name__}: {exc}",
                        "final_url": None,
                        "analysis": None,
                    }
                )
                documents.append(document)
                continue

            document["final_url"] = resource["final_url"]
            document["content_type"] = resource["content_type"]
            document["truncated"] = resource["truncated"]

            path_is_pdf = urlparse(resource["final_url"]).path.lower().endswith(".pdf")
            type_is_pdf = "application/pdf" in resource["content_type"].lower()
            if path_is_pdf or type_is_pdf:
                document.update(
                    {
                        "status": "not_analysed",
                        "reason": "remote_pdf_not_supported_in_controlled_v0.1",
                        "analysis": None,
                    }
                )
                documents.append(document)
                continue

            text = self.scanner.scan_html_content(resource["text"])
            if not text.strip():
                document.update(
                    {
                        "status": "not_analysed",
                        "reason": "no_visible_text_extracted",
                        "analysis": None,
                    }
                )
                documents.append(document)
                continue

            document.update(
                {
                    "status": "analysed",
                    "reason": None,
                    "analysis": self.analyzer.analyze(text, site_host),
                }
            )
            documents.append(document)

        return {
            "input_url": homepage_url,
            "homepage_url": final_homepage,
            "requested_homepage_url": requested_homepage,
            "site_host": site_host,
            "homepage_truncated": homepage_resource["truncated"],
            "discovery_scope": discovery["scope"],
            "documents_discovered": len(discovery["selected"]),
            "documents_selected": len(selected),
            "documents": documents,
            "excluded_policy_candidates": discovery["excluded_policy_candidates"],
            "categories_found": discovery["categories_found"],
            "categories_not_found": discovery["categories_not_found"],
            "limitations": [
                "Discovery is limited to links present on the supplied homepage.",
                "Only first-party host links are selected automatically.",
                "Cross-host redirects are blocked before document analysis.",
                "Remote PDF policy documents are reported but not analysed in v0.1.",
                (
                    "Extraction identifies textual signals; it does not provide "
                    "legal advice, compliance validation, or a safe/unsafe verdict."
                ),
            ],
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Discover first-party policy documents from a homepage and run "
            "the existing structured extraction pipeline."
        )
    )
    parser.add_argument(
        "url",
        help="Homepage URL, for example https://example.com",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=8,
        help="Maximum number of policy documents to analyse (default: 8)",
    )
    args = parser.parse_args()

    result = ControlledPolicyAnalyzer().analyze_site(
        args.url,
        max_documents=args.limit,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
