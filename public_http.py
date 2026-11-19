"""Public-network-only HTTP(S) transport for policy document retrieval.

This is a deliberately narrow egress boundary. It never uses HTTP proxies,
accepts only the default HTTP(S) ports, rejects non-global DNS answers, and
connects to the exact validated socket address (without a second DNS lookup).
TLS certificate and hostname verification use the original requested host.
Network controls outside this Python process remain the operator's responsibility.
"""

import http.client
import ipaddress
import socket
import ssl
import urllib.parse
import urllib.request


class UnsafeNetworkTarget(ValueError):
    """The requested destination cannot be used for public policy fetching."""


def validate_public_url(url):
    """Check URL syntax and static restrictions; DNS is checked on connect."""
    try:
        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise UnsafeNetworkTarget("Invalid HTTP(S) URL") from exc

    if (parsed.scheme not in ("http", "https") or not host
            or parsed.username is not None or parsed.password is not None):
        raise UnsafeNetworkTarget("Only credential-free HTTP(S) URLs are allowed")
    if any(char.isspace() for char in host) or "%" in host or "\\" in host:
        raise UnsafeNetworkTarget("Invalid destination hostname")
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise UnsafeNetworkTarget("Local and internal hostnames are prohibited")
    allowed_port = 443 if parsed.scheme == "https" else 80
    if port is not None and port != allowed_port:
        raise UnsafeNetworkTarget("Non-standard ports are prohibited")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            raise UnsafeNetworkTarget("Single-label hostnames are prohibited")
    else:
        if not _is_public(address):
            raise UnsafeNetworkTarget("Non-public IP destination is prohibited")
    return parsed


def _is_public(address):
    mapped = getattr(address, "ipv4_mapped", None)
    return bool(address.is_global and (mapped is None or mapped.is_global))


def _public_addresses(host, port):
    """Fail closed if any DNS result would permit an internal connection."""
    records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not records:
        raise UnsafeNetworkTarget("Destination has no usable addresses")
    for family, kind, proto, canonical, sockaddr in records:
        try:
            address = ipaddress.ip_address(sockaddr[0].split("%", 1)[0])
        except ValueError as exc:
            raise UnsafeNetworkTarget("Resolver returned invalid destination") from exc
        if not _is_public(address) or "%" in sockaddr[0]:
            raise UnsafeNetworkTarget("DNS returned a non-public address")
        if family not in (socket.AF_INET, socket.AF_INET6) or kind != socket.SOCK_STREAM:
            raise UnsafeNetworkTarget("Unsupported destination socket family")
    return records


def _connect_public(host, port, timeout, source_address):
    # Each request and redirect resolves afresh and pins the validated answer.
    # Connecting to the already-resolved sockaddr avoids a TOCTOU DNS re-query.
    addresses = _public_addresses(host, port)
    last_error = None
    for family, kind, proto, _canonical, sockaddr in addresses:
        sock = socket.socket(family, kind, proto)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    raise last_error or OSError("Unable to connect to public destination")


class _PublicConnectionMixin:
    def connect(self):
        if self._tunnel_host:
            raise UnsafeNetworkTarget("HTTP CONNECT tunnels are prohibited")
        validate_public_url(
            ("https" if isinstance(self, http.client.HTTPSConnection) else "http")
            + "://" + ("[" + self.host + "]" if ":" in self.host else self.host)
            + ":" + str(self.port)
        )
        sock = _connect_public(self.host, self.port, self.timeout, self.source_address)
        if isinstance(self, http.client.HTTPSConnection):
            try:
                self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
            except BaseException:
                sock.close()
                raise
        else:
            self.sock = sock


class _PublicHTTPConnection(_PublicConnectionMixin, http.client.HTTPConnection):
    pass


class _PublicHTTPSConnection(_PublicConnectionMixin, http.client.HTTPSConnection):
    pass


class _PublicHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, request):
        validate_public_url(request.full_url)
        return self.do_open(_PublicHTTPConnection, request)


class _PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, request):
        validate_public_url(request.full_url)
        return self.do_open(_PublicHTTPSConnection, request, context=self._context)


class _PublicRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        validate_public_url(urllib.parse.urljoin(request.full_url, newurl))
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def build_public_opener(redirect_handler=None):
    """No ambient proxies: neither requests nor urllib's default proxy path."""
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        _PublicHTTPHandler(),
        _PublicHTTPSHandler(context=ssl.create_default_context()),
        redirect_handler if redirect_handler is not None else _PublicRedirectHandler(),
    )
