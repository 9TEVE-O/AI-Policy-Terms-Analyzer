"""Offline, adversarial tests for public-only policy HTTP(S) egress."""
import socket
import urllib.request
from email.message import Message
from unittest.mock import Mock, patch

import pytest

import public_http as safe
from controlled_policy_analysis import ControlledPolicyAnalyzer, _FirstPartyRedirectHandler
from document_scanner import DocumentScanner


@pytest.mark.parametrize("url", [
    "http://localhost/terms", "https://sub.localhost/privacy",
    "http://127.0.0.1/", "http://0.0.0.0/", "http://[::1]/",
    "https://192.168.1.2/", "http://10.0.0.8/",
    "http://169.254.169.254/latest/meta-data/",
    "http://metadata.google.internal/", "http://foo.local/",
    "http://100.64.0.1/", "http://example.com:8080",
    "ftp://example.com", "https://user:pass@example.com",
    "http://intranet/", "http://[::ffff:192.168.1.8]/",
])
def test_static_private_and_internal_destinations_denied(url):
    with pytest.raises(safe.UnsafeNetworkTarget):
        safe.validate_public_url(url)


@pytest.mark.parametrize("url", [
    "https://example.com/privacy", "http://example.com/terms",
    "https://8.8.8.8/", "https://[2606:4700:4700::1111]/",
])
def test_public_http_urls_allowed(url):
    assert safe.validate_public_url(url)


def test_mixed_dns_answers_denied_before_socket_creation():
    answers = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 443)),
    ]
    with patch.object(safe.socket, "getaddrinfo", return_value=answers), patch.object(
        safe.socket, "socket"
    ) as sock:
        with pytest.raises(safe.UnsafeNetworkTarget, match="non-public"):
            safe._connect_public("example.com", 443, 5, None)
    sock.assert_not_called()


def test_pinned_socket_address_prevents_second_dns_resolution():
    answer = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443))
    with patch.object(safe.socket, "getaddrinfo", return_value=[answer]) as resolver, patch.object(
        safe.socket, "socket"
    ) as sock:
        assert safe._connect_public("example.com", 443, 5, None) is sock.return_value
        sock.return_value.connect.assert_called_once_with(("1.1.1.1", 443))
        resolver.assert_called_once_with("example.com", 443, type=socket.SOCK_STREAM)


def test_https_uses_original_hostname_for_tls_validation():
    connection = safe._PublicHTTPSConnection("example.com", timeout=5)
    remote = Mock()
    with patch.object(safe, "_connect_public", return_value=remote):
        connection._context = Mock()
        connection.connect()
    connection._context.wrap_socket.assert_called_once_with(remote, server_hostname="example.com")


def test_ambient_proxy_bypass_disabled(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:3128")
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:3128")
    opener = safe.build_public_opener()
    assert not any(isinstance(item, urllib.request.ProxyHandler) for item in opener.handlers)
    assert any(isinstance(item, safe._PublicHTTPSHandler) for item in opener.handlers)


def test_public_redirect_to_metadata_address_denied_before_connection():
    handler = safe._PublicRedirectHandler()
    request = urllib.request.Request("https://example.com/privacy")
    with pytest.raises(safe.UnsafeNetworkTarget):
        handler.redirect_request(
            request, None, 302, "Found", {}, "http://169.254.169.254/"
        )


def test_first_party_redirect_handler_is_the_only_redirect_handler():
    handler = _FirstPartyRedirectHandler("https://example.com")
    opener = safe.build_public_opener(handler)
    redirect_handlers = [
        item for item in opener.handlers
        if isinstance(item, urllib.request.HTTPRedirectHandler)
    ]
    assert redirect_handlers == [handler]
    request = urllib.request.Request("https://example.com/privacy")
    with pytest.raises(ValueError, match="Cross-host"):
        handler.redirect_request(
            request, None, 302, "Found", {}, "https://vendor.example.net/"
        )
    with pytest.raises(safe.UnsafeNetworkTarget):
        handler.redirect_request(
            request, None, 302, "Found", {}, "https://10.0.0.5/"
        )


def test_http_tunnel_rejected():
    connection = safe._PublicHTTPSConnection("example.com")
    connection._tunnel_host = "internal.example"
    with pytest.raises(safe.UnsafeNetworkTarget, match="tunnels"):
        connection.connect()


def test_scanner_rejects_local_urls_without_dns():
    with patch.object(safe.socket, "getaddrinfo") as dns:
        with pytest.raises(safe.UnsafeNetworkTarget):
            DocumentScanner().scan_url("http://127.0.0.1/private")
    dns.assert_not_called()


class StubResponse:
    def __init__(self, data, content_type="text/html; charset=utf-8", url="https://example.com/privacy"):
        self.data = data
        self.url = url
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def read(self, limit):
        return self.data[:limit]

    def geturl(self):
        return self.url

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_scanner_uses_safe_opener_without_network():
    opener = Mock()
    opener.open.return_value = StubResponse(b"<p>Policy content</p>")
    with patch("document_scanner.build_public_opener", return_value=opener) as factory:
        text = DocumentScanner().scan_url("https://example.com/privacy")
    factory.assert_called_once()
    assert "Policy content" in text
    assert opener.open.call_args.args[0].full_url == "https://example.com/privacy"


@pytest.mark.parametrize("data,content_type,error", [
    (b"abcdef", "application/octet-stream", "Unsupported remote content type"),
    (b"x" * 6, "text/html", "exceeds the byte limit"),
])
def test_scanner_rejects_unusable_fetches(data, content_type, error):
    scanner = DocumentScanner()
    scanner._MAX_URL_BYTES = 5
    opener = Mock()
    opener.open.return_value = StubResponse(data, content_type)
    with patch("document_scanner.build_public_opener", return_value=opener):
        with pytest.raises(ValueError, match=error):
            scanner._fetch_url("https://example.com/privacy")


def test_controlled_fetch_rejects_external_before_network():
    analyser = ControlledPolicyAnalyzer()
    with patch("controlled_policy_analysis.build_public_opener") as factory:
        with pytest.raises(ValueError, match="first-party"):
            analyser._fetch_first_party_resource(
                "https://vendor.example.net/privacy", "https://example.com"
            )
    factory.assert_not_called()


def test_controlled_fetch_uses_safe_opener_with_first_party_handler():
    response = StubResponse(b"<p>Public policy</p>")
    opener = Mock()
    opener.open.return_value = response
    analyser = ControlledPolicyAnalyzer()
    with patch("controlled_policy_analysis.build_public_opener", return_value=opener) as factory:
        result = analyser._fetch_first_party_resource(
            "https://example.com/privacy", "https://example.com"
        )
    assert isinstance(factory.call_args.args[0], _FirstPartyRedirectHandler)
    assert result["text"] == "<p>Public policy</p>"
    assert result["truncated"] is False
