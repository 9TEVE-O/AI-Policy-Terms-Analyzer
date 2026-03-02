#!/usr/bin/env python3
"""
Test script for the Key Point Condenser.

Tests summarization, abstract generation, and outline creation.
"""

from key_point_condenser import KeyPointCondenser
import json


SAMPLE_POLICY = """
PRIVACY POLICY

DATA COLLECTION:
We collect personal information including your name, email address, and usage
data when you interact with our services. This information is essential for
providing personalized experiences and improving our platform functionality.

DATA SHARING:
We may share your personal data with trusted third-party service providers who
assist us in operating our website and conducting our business. All third parties
are contractually required to keep your information confidential and secure.
We never sell your personal information to advertisers or data brokers.

SECURITY:
We implement industry-standard security measures to protect your data from
unauthorized access, alteration, disclosure, or destruction. Our security
team regularly audits our systems to identify and address potential vulnerabilities.

COOKIES:
Our website uses cookies to enhance your browsing experience and collect
analytics data about site usage. You may disable cookies in your browser
settings, though some features may not function correctly without them.
"""

UNSTRUCTURED_TEXT = """
Our platform leverages machine learning algorithms to analyze user behavior and
deliver personalized content recommendations. We use advanced natural language
processing techniques to understand user queries and provide accurate results.
The system continuously learns from user interactions to improve its performance
and accuracy over time. Data privacy and security are paramount concerns in our
design philosophy, and we employ end-to-end encryption for all communications.
"""


def test_summarize():
    """Test the summarize method."""
    condenser = KeyPointCondenser()

    summary = condenser.summarize(SAMPLE_POLICY, num_sentences=3)
    assert isinstance(summary, str), "summarize() should return a string"
    assert len(summary) > 0, "summarize() should not return empty string for non-empty input"

    # Should contain no more than 3 sentences
    sentences = [s for s in summary.split('.') if s.strip()]
    assert len(sentences) <= 3, "Summary should be concise"

    print("✓ test_summarize passed")


def test_generate_abstract():
    """Test the generate_abstract method."""
    condenser = KeyPointCondenser()

    abstract = condenser.generate_abstract(SAMPLE_POLICY)
    assert isinstance(abstract, str), "generate_abstract() should return a string"
    assert len(abstract) > 0, "generate_abstract() should produce content"

    full_summary = condenser.summarize(SAMPLE_POLICY, num_sentences=5)
    # Abstract (3 sentences) should be shorter than or equal to the 5-sentence summary
    assert len(abstract) <= len(full_summary) + 50, "Abstract should be shorter than full summary"

    print("✓ test_generate_abstract passed")


def test_generate_outline_with_headings():
    """Test outline generation on text that contains headings."""
    condenser = KeyPointCondenser()

    outline = condenser.generate_outline(SAMPLE_POLICY)
    assert isinstance(outline, list), "generate_outline() should return a list"
    assert len(outline) > 0, "Outline should contain at least one section"

    for section in outline:
        assert 'heading' in section, "Each section should have a 'heading' key"
        assert 'key_points' in section, "Each section should have a 'key_points' key"
        assert isinstance(section['heading'], str), "Heading should be a string"
        assert isinstance(section['key_points'], list), "Key points should be a list"

    headings = [s['heading'] for s in outline]
    print(f"  Detected headings: {headings}")

    print("✓ test_generate_outline_with_headings passed")


def test_generate_outline_without_headings():
    """Test outline generation on plain text without headings."""
    condenser = KeyPointCondenser()

    outline = condenser.generate_outline(UNSTRUCTURED_TEXT)
    assert isinstance(outline, list), "generate_outline() should return a list"
    assert len(outline) == 1, "Unstructured text should produce a single 'Main Points' section"
    assert outline[0]['heading'] == 'Main Points', "Section heading should be 'Main Points'"
    assert isinstance(outline[0]['key_points'], list), "Key points should be a list"

    print("✓ test_generate_outline_without_headings passed")


def test_condense():
    """Test the full condense() method."""
    condenser = KeyPointCondenser()

    result = condenser.condense(SAMPLE_POLICY, title="Test Policy")
    assert result['title'] == "Test Policy", "Title should match input"
    assert isinstance(result['word_count'], int), "word_count should be an integer"
    assert result['word_count'] > 0, "word_count should be positive"
    assert isinstance(result['abstract'], str), "abstract should be a string"
    assert isinstance(result['summary'], str), "summary should be a string"
    assert isinstance(result['outline'], list), "outline should be a list"

    print(f"  Word count: {result['word_count']}")
    print("✓ test_condense passed")


def test_condense_empty_input():
    """Test condense() with empty input."""
    condenser = KeyPointCondenser()

    result = condenser.condense("", title="Empty")
    assert result['abstract'] == "", "Abstract of empty text should be empty string"
    assert result['summary'] == "", "Summary of empty text should be empty string"
    assert isinstance(result['outline'], list), "Outline should still be a list"

    print("✓ test_condense_empty_input passed")


def test_format_report():
    """Test that format_report() produces a readable string."""
    condenser = KeyPointCondenser()

    result = condenser.condense(SAMPLE_POLICY, title="Format Test")
    report = condenser.format_report(result)

    assert isinstance(report, str), "format_report() should return a string"
    assert "KEY POINT CONDENSER REPORT" in report, "Report should contain header"
    assert "ABSTRACT" in report, "Report should contain ABSTRACT section"
    assert "SUMMARY" in report, "Report should contain SUMMARY section"
    assert "OUTLINE" in report, "Report should contain OUTLINE section"

    print("✓ test_format_report passed")


def test_json_serializable():
    """Test that condense() output is JSON-serializable."""
    condenser = KeyPointCondenser()

    result = condenser.condense(SAMPLE_POLICY, title="JSON Test")
    json_output = json.dumps(result, indent=2)
    assert isinstance(json_output, str), "JSON output should be a string"
    parsed = json.loads(json_output)
    assert parsed['title'] == "JSON Test", "Roundtrip JSON should preserve title"

    print("✓ test_json_serializable passed")


def test_summarize_num_sentences_clamped():
    """Test that requesting more sentences than available works gracefully."""
    condenser = KeyPointCondenser()

    # Request far more sentences than the text contains
    summary = condenser.summarize("This is one sentence. Here is another.", num_sentences=100)
    assert isinstance(summary, str), "Should return a string even for large num_sentences"

    print("✓ test_summarize_num_sentences_clamped passed")


def main():
    """Run all Key Point Condenser tests."""
    print("=" * 80)
    print("KEY POINT CONDENSER TESTS")
    print("=" * 80)
    print()

    test_summarize()
    test_generate_abstract()
    test_generate_outline_with_headings()
    test_generate_outline_without_headings()
    test_condense()
    test_condense_empty_input()
    test_format_report()
    test_json_serializable()
    test_summarize_num_sentences_clamped()

    print()
    print("=" * 80)

    # Show a sample report
    print("\nSAMPLE OUTPUT")
    print("=" * 80)
    condenser = KeyPointCondenser()
    result = condenser.condense(SAMPLE_POLICY, title="Privacy Policy")
    print(condenser.format_report(result))

    print("All tests completed successfully! ✓")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
