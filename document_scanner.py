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
* Remote HTTP(S) URLs use a public-only, DNS-pinned stdlib transport.
  Proxies, internal network destinations and non-standard ports are rejected.
"""

import html
import os
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Dict

from public_http import build_public_opener, validate_public_url

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

class _TextExtractorParser(HTMLParser):
    """Minimal HTML parser that strips tags while preserving block boundaries."""

    _SKIP_TAGS = {'script', 'style', 'head', 'noscript', 'template', 'meta', 'link'}
    _BLOCK_TAGS = {
        'address', 'article', 'aside', 'blockquote', 'br', 'dd', 'div', 'dl',
        'dt', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2',
        'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'li', 'main', 'nav', 'ol',
        'p', 'pre', 'section', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
        'tr', 'ul',
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth == 0 and tag in self._BLOCK_TAGS:
            self._parts.append('\n\n')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if self._skip_depth == 0 and tag in self._BLOCK_TAGS:
            self._parts.append('\n\n')

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        return ''.join(self._parts)


class DocumentScanner:
    """Extract plain text from local documents, HTML, PDFs, and web pages."""

    _MAX_URL_BYTES = 5 * 1024 * 1024
    _URL_TIMEOUT = 15
    _USER_AGENT = (
        'Mozilla/5.0 (compatible; AI-Policy-Analyzer/1.0; '
        '+https://github.com/9TEVE-O/AI-Policy-Terms-Analyzer)'
    )
    _BLOCK_TAGS = _TextExtractorParser._BLOCK_TAGS

    def __init__(self):
        # Horizontal whitespace is normalised separately from newlines so
        # paragraph boundaries remain available to downstream extractors.
        self._horizontal_whitespace_re = re.compile(r'[\t\f\v ]{2,}')
        self._spaces_around_newline_re = re.compile(r'[\t ]*\n[\t ]*')
        self._excess_newlines_re = re.compile(r'\n{3,}')

    def scan_file(self, filepath: str) -> str:
        """Detect the file type by extension and extract text."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            return self.scan_pdf(filepath)
        if ext in ('.html', '.htm'):
            return self.scan_html_file(filepath)
        return self.scan_text_file(filepath)

    def scan_text_file(self, filepath: str) -> str:
        """Read a plain-text file and return its contents unchanged."""
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            return fh.read()

    def scan_pdf(self, filepath: str) -> str:
        """Extract text from a PDF while preserving page boundaries."""
        if not _HAS_PDFPLUMBER:
            raise ImportError(
                "PDF scanning requires the 'pdfplumber' package. "
                "Install it with:  pip install pdfplumber"
            )

        import pdfplumber

        pages_text = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)

        return self._clean_text('\n\n'.join(pages_text))

    def scan_html_file(self, filepath: str) -> str:
        """Read an HTML file and extract its visible text."""
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            html_content = fh.read()
        return self.scan_html_content(html_content)

    def scan_url(self, url: str) -> str:
        """Fetch an HTTP(S) page and extract its visible text."""
        validate_public_url(url)

        html_content = self._fetch_url(url)
        return self.scan_html_content(html_content)

    def scan_html_content(self, html_content: str) -> str:
        """Extract visible text from HTML while retaining block boundaries."""
        if _HAS_BS4:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup([
                'script', 'style', 'head', 'noscript', 'template', 'meta', 'link'
            ]):
                tag.decompose()

            # Mark block-level boundaries before flattening the DOM. The
            # cleaner below retains at most one blank line between blocks.
            for tag in soup.find_all(list(self._BLOCK_TAGS)):
                tag.append('\n\n')
            text = soup.get_text(separator=' ', strip=False)
        else:
            parser = _TextExtractorParser()
            parser.feed(html_content)
            text = parser.get_text()

        return self._clean_text(text)

    def get_document_info(self, filepath: str) -> Dict:
        """Return document metadata without extracting the full document."""
        ext = os.path.splitext(filepath)[1].lower()
        scanner_available = not (ext == '.pdf' and not _HAS_PDFPLUMBER)
        size_bytes = os.path.getsize(filepath) if os.path.isfile(filepath) else 0

        return {
            'filename': os.path.basename(filepath),
            'extension': ext,
            'size_bytes': size_bytes,
            'scanner_available': scanner_available,
        }

    def _fetch_url(self, url: str) -> str:
        """Fetch public HTML through a pinned, proxy-free connection."""
        validate_public_url(url)
        req = urllib.request.Request(
            url, headers={'User-Agent': self._USER_AGENT}
        )
        with build_public_opener().open(req, timeout=self._URL_TIMEOUT) as resp:
            content_type = resp.headers.get('Content-Type', '')
            if content_type and not content_type.lower().startswith(
                ('text/html', 'text/plain', 'application/xhtml+xml')
            ):
                raise ValueError("Unsupported remote content type")
            raw = resp.read(self._MAX_URL_BYTES + 1)
            if len(raw) > self._MAX_URL_BYTES:
                raise ValueError("Remote document exceeds the byte limit")
            encoding = resp.headers.get_content_charset() or 'utf-8'
        return raw.decode(encoding, errors='replace')

    def _clean_text(self, text: str) -> str:
        """Normalise whitespace without destroying paragraph boundaries."""
        text = html.unescape(text)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = self._horizontal_whitespace_re.sub(' ', text)
        text = self._spaces_around_newline_re.sub('\n', text)
        text = self._excess_newlines_re.sub('\n\n', text)
        return text.strip()


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
