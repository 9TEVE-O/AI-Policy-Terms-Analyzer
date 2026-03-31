#!/usr/bin/env python3
"""
Tests for DocumentScanner.

Tests plain-text file scanning, HTML content extraction (stdlib fallback path),
URL validation, and metadata helpers — all using only the standard library so
that optional dependencies (pdfplumber, requests, beautifulsoup4) are not
required to run the test suite.
"""

import os
import tempfile

from document_scanner import DocumentScanner, _TextExtractorParser


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_TEXT = """
Privacy Policy — Example Corp

We use AWS for cloud infrastructure and GitHub for code hosting.
Our chatbot is powered by OpenAI GPT technology.
Contact: privacy@example.com
Website: https://example.com/privacy
"""

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Privacy Policy</title>
  <style>body { font-family: sans-serif; }</style>
  <script>console.log("analytics")</script>
</head>
<body>
  <h1>Privacy Policy</h1>
  <p>We use AWS for cloud infrastructure.</p>
  <p>Contact: privacy@example.com</p>
  <!-- comment that should be ignored -->
</body>
</html>"""


# ---------------------------------------------------------------------------
# _TextExtractorParser (stdlib fallback)
# ---------------------------------------------------------------------------

def test_text_extractor_parser_basic():
    """Stdlib HTML parser should strip tags and return visible text."""
    parser = _TextExtractorParser()
    parser.feed('<p>Hello <b>world</b>!</p>')
    text = parser.get_text()
    assert 'Hello' in text
    assert 'world' in text
    print("✓ test_text_extractor_parser_basic passed")


def test_text_extractor_parser_skips_script_and_style():
    """Script and style tag contents must be excluded from extracted text."""
    parser = _TextExtractorParser()
    parser.feed(
        '<html><head><style>body{margin:0}</style>'
        '<script>var x=1;</script></head>'
        '<body><p>Visible text.</p></body></html>'
    )
    text = parser.get_text()
    assert 'Visible text' in text
    assert 'margin' not in text
    assert 'var x' not in text
    print("✓ test_text_extractor_parser_skips_script_and_style passed")


def test_text_extractor_parser_empty_input():
    """Empty HTML should produce an empty string."""
    parser = _TextExtractorParser()
    parser.feed('')
    assert parser.get_text() == ''
    print("✓ test_text_extractor_parser_empty_input passed")


# ---------------------------------------------------------------------------
# DocumentScanner — text files
# ---------------------------------------------------------------------------

def test_scan_text_file():
    """scan_text_file should return the file contents unchanged."""
    scanner = DocumentScanner()
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False, encoding='utf-8'
    ) as fh:
        fh.write(SAMPLE_TEXT)
        path = fh.name

    try:
        result = scanner.scan_text_file(path)
        assert isinstance(result, str), "scan_text_file should return a string"
        assert 'AWS' in result
        assert 'privacy@example.com' in result
    finally:
        os.unlink(path)

    print("✓ test_scan_text_file passed")


def test_scan_file_txt_extension():
    """scan_file should detect .txt and delegate to scan_text_file."""
    scanner = DocumentScanner()
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False, encoding='utf-8'
    ) as fh:
        fh.write(SAMPLE_TEXT)
        path = fh.name

    try:
        result = scanner.scan_file(path)
        assert 'AWS' in result
        assert 'OpenAI' in result
    finally:
        os.unlink(path)

    print("✓ test_scan_file_txt_extension passed")


def test_scan_file_md_extension():
    """scan_file should handle .md files as plain text."""
    scanner = DocumentScanner()
    content = "# Terms\n\nWe use Python and GitHub.\n"
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.md', delete=False, encoding='utf-8'
    ) as fh:
        fh.write(content)
        path = fh.name

    try:
        result = scanner.scan_file(path)
        assert 'Python' in result
        assert 'GitHub' in result
    finally:
        os.unlink(path)

    print("✓ test_scan_file_md_extension passed")


def test_scan_file_not_found():
    """scan_file should raise FileNotFoundError for missing files."""
    scanner = DocumentScanner()
    try:
        scanner.scan_file('/tmp/definitely_does_not_exist_xyz.txt')
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass
    print("✓ test_scan_file_not_found passed")


# ---------------------------------------------------------------------------
# DocumentScanner — HTML
# ---------------------------------------------------------------------------

def test_scan_html_content_extracts_visible_text():
    """scan_html_content should return visible text, excluding scripts/styles."""
    scanner = DocumentScanner()
    result = scanner.scan_html_content(SAMPLE_HTML)

    assert isinstance(result, str), "scan_html_content should return a string"
    assert 'Privacy Policy' in result
    assert 'AWS' in result
    assert 'privacy@example.com' in result
    # Script and style contents should be absent
    assert 'console.log' not in result
    assert 'font-family' not in result

    print("✓ test_scan_html_content_extracts_visible_text passed")


def test_scan_html_content_empty():
    """scan_html_content with empty string should return an empty string."""
    scanner = DocumentScanner()
    result = scanner.scan_html_content('')
    assert result == ''
    print("✓ test_scan_html_content_empty passed")


def test_scan_html_file():
    """scan_html_file should read file and extract visible text."""
    scanner = DocumentScanner()
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8'
    ) as fh:
        fh.write(SAMPLE_HTML)
        path = fh.name

    try:
        result = scanner.scan_html_file(path)
        assert 'AWS' in result
        assert 'Privacy Policy' in result
    finally:
        os.unlink(path)

    print("✓ test_scan_html_file passed")


def test_scan_file_html_extension():
    """scan_file should detect .html and delegate to scan_html_file."""
    scanner = DocumentScanner()
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8'
    ) as fh:
        fh.write(SAMPLE_HTML)
        path = fh.name

    try:
        result = scanner.scan_file(path)
        assert 'Privacy Policy' in result
        assert 'AWS' in result
    finally:
        os.unlink(path)

    print("✓ test_scan_file_html_extension passed")


def test_scan_html_entities_decoded():
    """HTML entities in content should be decoded in extracted text."""
    scanner = DocumentScanner()
    html = '<p>Copyright &amp; Privacy &mdash; All Rights Reserved</p>'
    result = scanner.scan_html_content(html)
    assert '&amp;' not in result, "&amp; entity should have been decoded to &"
    print("✓ test_scan_html_entities_decoded passed")


# ---------------------------------------------------------------------------
# DocumentScanner — URL validation
# ---------------------------------------------------------------------------

def test_scan_url_rejects_non_http():
    """scan_url should raise ValueError for non-http(s) schemes."""
    scanner = DocumentScanner()
    try:
        scanner.scan_url('ftp://example.com/policy.txt')
        assert False, "Expected ValueError for ftp:// URL"
    except ValueError:
        pass
    print("✓ test_scan_url_rejects_non_http passed")


def test_scan_url_rejects_local_path():
    """scan_url should raise ValueError for bare local paths."""
    scanner = DocumentScanner()
    try:
        scanner.scan_url('/etc/passwd')
        assert False, "Expected ValueError for non-URL"
    except ValueError:
        pass
    print("✓ test_scan_url_rejects_local_path passed")


# ---------------------------------------------------------------------------
# DocumentScanner — PDF (graceful missing dependency)
# ---------------------------------------------------------------------------

def test_scan_pdf_raises_import_error_without_pdfplumber():
    """When pdfplumber is absent, scan_pdf should raise ImportError."""
    import document_scanner as ds_module
    original = ds_module._HAS_PDFPLUMBER
    ds_module._HAS_PDFPLUMBER = False
    scanner = DocumentScanner()
    try:
        scanner.scan_pdf('/tmp/fake.pdf')
        assert False, "Expected ImportError when pdfplumber absent"
    except ImportError as exc:
        assert 'pdfplumber' in str(exc).lower()
    finally:
        ds_module._HAS_PDFPLUMBER = original
    print("✓ test_scan_pdf_raises_import_error_without_pdfplumber passed")


# ---------------------------------------------------------------------------
# DocumentScanner — get_document_info
# ---------------------------------------------------------------------------

def test_get_document_info_text_file():
    """get_document_info should return correct metadata for a text file."""
    scanner = DocumentScanner()
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False, encoding='utf-8'
    ) as fh:
        fh.write("hello world")
        path = fh.name

    try:
        info = scanner.get_document_info(path)
        assert info['extension'] == '.txt'
        assert info['filename'] == os.path.basename(path)
        assert info['size_bytes'] > 0
        assert info['scanner_available'] is True
    finally:
        os.unlink(path)

    print("✓ test_get_document_info_text_file passed")


def test_get_document_info_pdf_no_pdfplumber():
    """get_document_info should mark scanner_available=False for PDFs when pdfplumber absent."""
    import document_scanner as ds_module
    original = ds_module._HAS_PDFPLUMBER

    ds_module._HAS_PDFPLUMBER = False
    try:
        scanner = DocumentScanner()
        # Use a non-existent path — get_document_info should not open the file
        info = scanner.get_document_info('/tmp/nonexistent_test.pdf')
        assert info['extension'] == '.pdf'
        assert info['scanner_available'] is False
        print("✓ test_get_document_info_pdf_no_pdfplumber passed")
    finally:
        ds_module._HAS_PDFPLUMBER = original
# ---------------------------------------------------------------------------
# DocumentScanner — _clean_text
# ---------------------------------------------------------------------------

def test_clean_text_collapses_whitespace():
    """_clean_text should collapse multiple spaces/newlines into one space."""
    scanner = DocumentScanner()
    result = scanner._clean_text("Hello    world\n\n\nfoo")
    assert '  ' not in result, "Should have no double spaces"
    assert 'Hello world' in result
    print("✓ test_clean_text_collapses_whitespace passed")


def test_clean_text_decodes_html_entities():
    """_clean_text should decode HTML entities."""
    scanner = DocumentScanner()
    result = scanner._clean_text("AT&amp;T and Marks &amp; Spencer")
    assert '&amp;' not in result
    assert 'AT&T' in result
    print("✓ test_clean_text_decodes_html_entities passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all DocumentScanner tests."""
    print("=" * 80)
    print("DOCUMENT SCANNER TESTS")
    print("=" * 80)
    print()

    test_text_extractor_parser_basic()
    test_text_extractor_parser_skips_script_and_style()
    test_text_extractor_parser_empty_input()

    test_scan_text_file()
    test_scan_file_txt_extension()
    test_scan_file_md_extension()
    test_scan_file_not_found()

    test_scan_html_content_extracts_visible_text()
    test_scan_html_content_empty()
    test_scan_html_file()
    test_scan_file_html_extension()
    test_scan_html_entities_decoded()

    test_scan_url_rejects_non_http()
    test_scan_url_rejects_local_path()

    test_scan_pdf_raises_import_error_without_pdfplumber()

    test_get_document_info_text_file()
    test_get_document_info_pdf_no_pdfplumber()

    test_clean_text_collapses_whitespace()
    test_clean_text_decodes_html_entities()

    print()
    print("=" * 80)
    print("All DocumentScanner tests passed! ✓")
    print("=" * 80)


if __name__ == "__main__":
    main()
