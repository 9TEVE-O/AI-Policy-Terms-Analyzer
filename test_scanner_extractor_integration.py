"""Integration regression for scanner-to-extractor paragraph semantics."""

from document_scanner import DocumentScanner
from extraction_modules import BotAutomationExtractor


def test_scanner_preserves_blank_line_between_unrelated_clauses():
    html = (
        '<p>Account sharing is not permitted by policy</p>'
        '<p>Automated billing runs nightly.</p>'
    )
    scanned = DocumentScanner().scan_html_content(html)

    assert '\n\n' in scanned
    assert BotAutomationExtractor().extract(scanned)['prohibition_snippets'] == []
