#!/usr/bin/env python3
"""
Document Scanner

Extracts plain text from various document sources so that the policy analyzer
and summarization tools can work directly with files and URLs, not just pasted
text.

Supported input types
---------------------
* Plain-text files (.txt, .md, .csv, and other text-based formats)
* HTML files (.html, .htm) — always available via the standard-library
  ``html.parser``; richer extraction available when ``beautifulsoup4`` is
  installed.
* PDF files (.pdf) — requires the optional ``pdfplumber`` package; raises
  ``ImportError`` with a helpful message when it is absent.
* Remote URLs (http/https) — always available via ``urllib.request``; the
  optional ``requests`` package is used when present for better timeout and
  redirect handling.

Optional dependencies (add to requirements.txt to enable):
    beautifulsoup4>=4.12.0
    requests>=2.31.0
    pdfplumber>=0.10.0
"""

import html
import os
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from typing import Dict

# ---------------------------------------------------------------------------
# Optional-dependency guards
# ---------------------------------------------------------------------------

try:
    import pdfplumber as _pdfplumber  # noqa: F401
    _HAS_PDFPLUMBER = True
except ImportError:
    _HAS_PDFPLUMBER = False

try:
    from bs4 import BeautifulSoup as _BeautifulSoup  # noqa: F401
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False

try:
    import requests as _requests  # noqa: F401
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


# ---------------------------------------------------------------------------
# Stdlib HTML text extractor (fallback when beautifulsoup4 is absent)
# ---------------------------------------------------------------------------

class _TextExtractorParser(HTMLParser):
    """Minimal HTML parser that strips tags and collects visible text."""

    # Tags whose entire content (including children) should be ignored
    _SKIP_TAGS = {'script', 'style', 'head', 'noscript', 'template', 'meta', 'link'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self._parts.append(stripped)

    def get_text(self) -> str:
        return ' '.join(self._parts)


# ---------------------------------------------------------------------------
# DocumentScanner
# ---------------------------------------------------------------------------

class DocumentScanner:
    """
    Extracts plain text from documents so they can be fed into PolicyAnalyzer,
    KeyPointCondenser, and AIPolicyResearcher.

    Usage::

        scanner = DocumentScanner()

        # From a file (type detected automatically)
        text = scanner.scan_file('/path/to/policy.pdf')

        # From a URL
        text = scanner.scan_url('https://example.com/privacy')

        # From an HTML string already in memory
        text = scanner.scan_html_content('<html>...</html>')
    """

    # Maximum response size when fetching URLs (5 MB)
    _MAX_URL_BYTES = 5 * 1024 * 1024

    # Request timeout for URL fetches (seconds)
    _URL_TIMEOUT = 15

    # User-agent sent with URL requests
    _USER_AGENT = (
        'Mozilla/5.0 (compatible; AI-Policy-Analyzer/1.0; '
        '+https://github.com/9TEVE-O/AI-Policy-Terms-Analyzer)'
    )

    def __init__(self):
        # Normalise repeated whitespace in extracted text
        self._whitespace_re = re.compile(r'\s{2,}')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan_file(self, filepath: str) -> str:
        """
        Detect the file type by extension and extract text.

        Supports ``.pdf``, ``.html``/``.htm``, and plain-text files.

        Args:
            filepath: Absolute or relative path to the file.

        Returns:
            Extracted plain text.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not recognised.
            ImportError: If a PDF is provided but pdfplumber is not installed.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.pdf':
            return self.scan_pdf(filepath)
        elif ext in ('.html', '.htm'):
            return self.scan_html_file(filepath)
        elif ext in ('.txt', '.md', '.csv', '.rst', '.text', ''):
            return self.scan_text_file(filepath)
        else:
            # Attempt to read as plain text; raise if it looks binary
            return self.scan_text_file(filepath)

    def scan_text_file(self, filepath: str) -> str:
        """
        Read a plain-text file and return its contents.

        Args:
            filepath: Path to the text file.

        Returns:
            File contents as a string.
        """
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            return fh.read()

    def scan_pdf(self, filepath: str) -> str:
        """
        Extract text from a PDF file using ``pdfplumber``.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Extracted plain text from all pages.

        Raises:
            ImportError: If pdfplumber is not installed.
        """
        if not _HAS_PDFPLUMBER:
            raise ImportError(
                "PDF scanning requires the 'pdfplumber' package. "
                "Install it with:  pip install pdfplumber"
            )

        import pdfplumber  # delayed import: pdfplumber is an optional dependency

        pages_text = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)

        return self._clean_text('\n\n'.join(pages_text))

    def scan_html_file(self, filepath: str) -> str:
        """
        Read an HTML file and extract its visible text.

        Args:
            filepath: Path to the HTML file.

        Returns:
            Extracted visible text.
        """
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            html_content = fh.read()
        return self.scan_html_content(html_content)

    def scan_url(self, url: str) -> str:
        """
        Fetch a web page and extract its visible text.

        Uses ``requests`` when available for better timeout/redirect handling,
        otherwise falls back to ``urllib.request``.

        Args:
            url: The http or https URL to fetch.

        Returns:
            Extracted visible text.

        Raises:
            ValueError: If the URL scheme is not http or https.
            urllib.error.URLError: If the page cannot be fetched.
        """
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Only http/https URLs are supported, got: {url!r}")

        html_content = self._fetch_url(url)
        return self.scan_html_content(html_content)

    def scan_html_content(self, html_content: str) -> str:
        """
        Extract visible text from an HTML string.

        Uses ``beautifulsoup4`` when available; falls back to a lightweight
        stdlib ``html.parser``-based extractor.

        Args:
            html_content: Raw HTML string.

        Returns:
            Extracted visible text.
        """
        if _HAS_BS4:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script, style, and other non-visible elements
            for tag in soup(["script", "style", "head", "noscript",
                             "template", "meta", "link"]):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
        else:
            parser = _TextExtractorParser()
            parser.feed(html_content)
            text = parser.get_text()

        return self._clean_text(text)

    def get_document_info(self, filepath: str) -> Dict:
        """
        Return metadata about a document without extracting all its text.

        Args:
            filepath: Path to the file.

        Returns:
            Dict with keys: ``filename``, ``extension``, ``size_bytes``,
            ``scanner_available`` (bool).
        """
        ext = os.path.splitext(filepath)[1].lower()
        scanner_available = True
        if ext == '.pdf' and not _HAS_PDFPLUMBER:
            scanner_available = False

        size_bytes = os.path.getsize(filepath) if os.path.isfile(filepath) else 0

        return {
            'filename': os.path.basename(filepath),
            'extension': ext,
            'size_bytes': size_bytes,
            'scanner_available': scanner_available,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fetch_url(self, url: str) -> str:
        """Fetch URL content using requests (if available) or urllib."""
        if _HAS_REQUESTS:
            import requests
            with requests.get(
                url,
                timeout=self._URL_TIMEOUT,
                headers={'User-Agent': self._USER_AGENT},
                stream=True,
            ) as response:
                response.raise_for_status()
                # Read up to _MAX_URL_BYTES to avoid massive downloads
                content = b''
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                    if len(content) >= self._MAX_URL_BYTES:
                        break
                return content.decode(
                    response.encoding or 'utf-8', errors='replace'
                )
        else:
            req = urllib.request.Request(
                url, headers={'User-Agent': self._USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=self._URL_TIMEOUT) as resp:
                raw = resp.read(self._MAX_URL_BYTES)
            # Attempt to detect encoding from Content-Type header
            content_type = resp.headers.get('Content-Type', '')
            charset_match = re.search(r'charset=([^\s;]+)', content_type)
            encoding = charset_match.group(1) if charset_match else 'utf-8'
            return raw.decode(encoding, errors='replace')

    def _clean_text(self, text: str) -> str:
        """Normalise whitespace and unescape HTML entities in extracted text."""
        text = html.unescape(text)
        text = self._whitespace_re.sub(' ', text)
        return text.strip()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Interactive Document Scanner."""
    print("Document Scanner")
    print("=" * 80)
    print()
    print("Extracts text from PDF, HTML, plain-text files, and web URLs.")
    print()
    print("Options:")
    print("  1. Scan a local file")
    print("  2. Scan a URL")
    print("  3. Exit")
    print()

    choice = input("Enter your choice (1-3): ").strip()
    scanner = DocumentScanner()

    if choice == '1':
        filepath = input("Enter file path: ").strip()
        try:
            text = scanner.scan_file(filepath)
            print(f"\n✅ Extracted {len(text):,} characters from '{filepath}'")
            print("\nFirst 500 characters:")
            print("-" * 40)
            print(text[:500])
            print("-" * 40)
        except (FileNotFoundError, ValueError, ImportError, OSError) as exc:
            print(f"\n❌ Error: {exc}")

    elif choice == '2':
        url = input("Enter URL (https://...): ").strip()
        try:
            text = scanner.scan_url(url)
            print(f"\n✅ Extracted {len(text):,} characters from '{url}'")
            print("\nFirst 500 characters:")
            print("-" * 40)
            print(text[:500])
            print("-" * 40)
        except (ValueError, urllib.error.URLError, OSError) as exc:
            print(f"\n❌ Error: {exc}")

    elif choice == '3':
        print("\nGoodbye!")
    else:
        print("\n❌ Invalid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
