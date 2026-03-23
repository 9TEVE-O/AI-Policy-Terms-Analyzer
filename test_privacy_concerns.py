#!/usr/bin/env python3
"""
Tests for privacy concern detection, data destination extraction,
and user-friendly summary generation added to PolicyAnalyzer.
"""

import json
from policy_analyzer import PolicyAnalyzer


# ---------------------------------------------------------------------------
# Sample policy texts
# ---------------------------------------------------------------------------

POLICY_WITH_HIGH_CONCERNS = """
Privacy Policy - DataBroker Corp.

We collect your personal information and may sell your personal data to third
parties for marketing and monetization purposes. We use targeted advertising
and interest-based ads across our platform. We collect your precise location
data to deliver location-based services.
"""

POLICY_WITH_MEDIUM_CONCERNS = """
Privacy Policy - AffiliateHub Ltd.

We share your data with our advertising partners for campaign management.
We may disclose your information with our affiliates and subsidiaries for
internal business purposes. We retain your data for as long as we deem
necessary to fulfil our business obligations.
You cannot opt-out of certain core data collection activities.
"""

POLICY_WITH_LOW_CONCERNS = """
Privacy Policy - CloudApp Inc.

In the event of a merger or acquisition, your data may be transferred to the
acquiring entity. We may share information with law enforcement or government
agencies when required by court order or legal process.
We may change this policy at any time without notice to users.
"""

POLICY_WITHOUT_CONCERNS = """
Privacy Policy - PrivacyFirst Corp.

We collect only the minimum data needed to provide our services.
We do not sell, rent, or trade your personal information to any third parties.
All data is encrypted in transit and at rest using industry-standard protocols.
We delete your data within 30 days of account closure upon request.
You can opt out of all non-essential communications at any time.
"""

POLICY_WITH_DESTINATIONS = """
Privacy Policy - MultiService Inc.

We share your information with payment processing providers for financial
transactions. We use analytics services for usage statistics and telemetry.
Our platform integrates with advertising and marketing tools.
We use cloud hosting infrastructure to store and serve your data.
Customer support services help us respond to your inquiries.
We employ fraud detection services to protect your account security.
We work with email marketing providers to send communications.
"""

POLICY_COMBINED = """
Privacy Policy - BigTech Ltd.

DATA COLLECTION:
We collect personal information including your name, email address, and
precise location data when you interact with our services.

DATA SHARING:
We may sell your personal information to third parties for business purposes.
We share your data with our advertising partners for targeted advertising.
We disclose information with our affiliates and subsidiaries.
We integrate with payment processing and analytics providers.
Your data may be transferred in a merger or acquisition.
We may share information with law enforcement when required by court order.

RETENTION:
We retain your data for as long as we deem necessary.

We may change this policy at any time without notice.
"""


# ---------------------------------------------------------------------------
# Tests: detect_privacy_concerns
# ---------------------------------------------------------------------------

def test_high_concern_data_selling():
    """Should detect data-selling language as a HIGH concern."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITH_HIGH_CONCERNS)
    assert 'high' in concerns, "Expected 'high' severity key"
    assert len(concerns['high']) > 0, "Expected at least one HIGH concern"
    high_texts = " ".join(concerns['high'])
    assert 'sell' in high_texts.lower() or 'sold' in high_texts.lower(), \
        "HIGH concern should mention selling data"
    print("✓ test_high_concern_data_selling passed")


def test_high_concern_targeted_advertising():
    """Should detect targeted/behavioral advertising as a HIGH concern."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITH_HIGH_CONCERNS)
    assert 'high' in concerns, "Expected 'high' severity key"
    assert len(concerns['high']) > 0, "Expected at least one HIGH concern"
    high_texts = " ".join(concerns['high'])
    assert 'advertising' in high_texts.lower() or 'behavioral' in high_texts.lower(), \
        "HIGH concern should mention targeted advertising"
    print("✓ test_high_concern_targeted_advertising passed")


def test_high_concern_precise_location():
    """Should detect precise location collection as a HIGH concern."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITH_HIGH_CONCERNS)
    assert 'high' in concerns, "Expected 'high' severity key"
    assert len(concerns['high']) > 0, "Expected at least one HIGH concern"
    high_texts = " ".join(concerns['high'])
    assert 'location' in high_texts.lower(), \
        "HIGH concern should mention location data"
    print("✓ test_high_concern_precise_location passed")


def test_medium_concerns_detected():
    """Should detect advertising partners and data retention as MEDIUM concerns."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITH_MEDIUM_CONCERNS)
    assert 'medium' in concerns, "Expected 'medium' severity key"
    assert len(concerns['medium']) > 0, "Expected at least one MEDIUM concern"
    medium_texts = " ".join(concerns['medium'])
    assert 'advertising' in medium_texts.lower() or 'retain' in medium_texts.lower(), \
        "MEDIUM concerns should mention advertising partners or data retention"
    print("✓ test_medium_concerns_detected passed")


def test_low_concerns_detected():
    """Should detect merger/govt sharing and policy-change-without-notice as LOW concerns."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITH_LOW_CONCERNS)
    assert 'low' in concerns, "Expected 'low' severity key"
    assert len(concerns['low']) > 0, "Expected at least one LOW concern"
    low_texts = " ".join(concerns['low'])
    assert ('merger' in low_texts.lower() or 'law enforcement' in low_texts.lower()
            or 'policy' in low_texts.lower()), \
        "LOW concerns should mention merger, law enforcement, or policy changes"
    print("✓ test_low_concerns_detected passed")


def test_no_false_positives_for_clean_policy():
    """A clearly clean policy should produce no HIGH or MEDIUM concerns."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns(POLICY_WITHOUT_CONCERNS)
    assert 'high' not in concerns, \
        f"Clean policy should produce no HIGH concerns, got: {concerns.get('high')}"
    assert 'medium' not in concerns, \
        f"Clean policy should produce no MEDIUM concerns, got: {concerns.get('medium')}"
    print("✓ test_no_false_positives_for_clean_policy passed")


def test_concerns_return_type():
    """detect_privacy_concerns should always return a dict of lists."""
    analyzer = PolicyAnalyzer()
    result = analyzer.detect_privacy_concerns(POLICY_COMBINED)
    assert isinstance(result, dict), "Should return a dict"
    for severity, items in result.items():
        assert isinstance(items, list), f"Severity '{severity}' should map to a list"
        for item in items:
            assert isinstance(item, str), "Each concern should be a string"
    print("✓ test_concerns_return_type passed")


def test_empty_text_returns_no_concerns():
    """Empty input should produce an empty dict (no concerns)."""
    analyzer = PolicyAnalyzer()
    concerns = analyzer.detect_privacy_concerns("")
    assert concerns == {}, f"Empty text should return empty dict, got {concerns}"
    print("✓ test_empty_text_returns_no_concerns passed")


# ---------------------------------------------------------------------------
# Tests: detect_data_destinations
# ---------------------------------------------------------------------------

def test_data_destinations_purposes():
    """Should detect functional sharing purposes from policy text."""
    analyzer = PolicyAnalyzer()
    result = analyzer.detect_data_destinations(POLICY_WITH_DESTINATIONS)
    assert 'purposes' in result, "Result should contain 'purposes' key"
    assert isinstance(result['purposes'], list), "'purposes' should be a list"
    assert len(result['purposes']) > 0, \
        "Should detect at least one purpose from the destination policy"
    purposes_text = " ".join(result['purposes']).lower()
    assert any(kw in purposes_text for kw in ['analytics', 'payment', 'advertising',
                                               'hosting', 'email', 'fraud', 'support']), \
        "Should detect recognizable sharing purposes"
    print("✓ test_data_destinations_purposes passed")


def test_data_destinations_recipients():
    """Should extract recipient phrases from sharing patterns."""
    analyzer = PolicyAnalyzer()
    text = ("We share your personal data with Google Analytics for reporting. "
            "We integrate with Stripe for payment processing services.")
    result = analyzer.detect_data_destinations(text)
    assert 'recipients' in result, "Result should contain 'recipients' key"
    assert isinstance(result['recipients'], list), "'recipients' should be a list"
    print("✓ test_data_destinations_recipients passed")


def test_data_destinations_return_type():
    """detect_data_destinations should always return the expected dict structure."""
    analyzer = PolicyAnalyzer()
    result = analyzer.detect_data_destinations(POLICY_COMBINED)
    assert isinstance(result, dict), "Should return a dict"
    assert 'recipients' in result and 'purposes' in result, \
        "Dict should contain 'recipients' and 'purposes' keys"
    assert isinstance(result['recipients'], list), "'recipients' should be a list"
    assert isinstance(result['purposes'], list), "'purposes' should be a list"
    print("✓ test_data_destinations_return_type passed")


def test_data_destinations_empty_input():
    """Empty text should return empty recipients and purposes."""
    analyzer = PolicyAnalyzer()
    result = analyzer.detect_data_destinations("")
    assert result['recipients'] == [], "Empty text should produce no recipients"
    assert result['purposes'] == [], "Empty text should produce no purposes"
    print("✓ test_data_destinations_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: analyze() includes new fields
# ---------------------------------------------------------------------------

def test_analyze_includes_privacy_concerns():
    """analyze() output should include 'privacy_concerns' key."""
    analyzer = PolicyAnalyzer()
    result = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    assert 'privacy_concerns' in result, "analyze() should include 'privacy_concerns'"
    assert isinstance(result['privacy_concerns'], dict)
    print("✓ test_analyze_includes_privacy_concerns passed")


def test_analyze_includes_data_destinations():
    """analyze() output should include 'data_destinations' key."""
    analyzer = PolicyAnalyzer()
    result = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    assert 'data_destinations' in result, "analyze() should include 'data_destinations'"
    assert isinstance(result['data_destinations'], dict)
    assert 'recipients' in result['data_destinations']
    assert 'purposes' in result['data_destinations']
    print("✓ test_analyze_includes_data_destinations passed")


def test_analyze_output_is_json_serializable():
    """The full analyze() output including new fields should be JSON-serializable."""
    analyzer = PolicyAnalyzer()
    result = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    json_str = json.dumps(result, indent=2)
    parsed = json.loads(json_str)
    assert parsed['company_name'] == "BigTech Ltd."
    assert 'privacy_concerns' in parsed
    assert 'data_destinations' in parsed
    print("✓ test_analyze_output_is_json_serializable passed")


# ---------------------------------------------------------------------------
# Tests: generate_user_summary
# ---------------------------------------------------------------------------

def test_generate_user_summary_returns_string():
    """generate_user_summary() should return a non-empty string."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    summary = analyzer.generate_user_summary(analysis)
    assert isinstance(summary, str), "Should return a string"
    assert len(summary) > 0, "Summary should not be empty"
    print("✓ test_generate_user_summary_returns_string passed")


def test_generate_user_summary_sections():
    """User summary should contain required section headers."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    summary = analyzer.generate_user_summary(analysis)
    assert "WHERE YOUR DATA GOES" in summary, "Summary should contain data destinations section"
    assert "WHAT TO BE WARY OF" in summary, "Summary should contain concerns section"
    assert "BigTech Ltd." in summary, "Summary should include company name"
    print("✓ test_generate_user_summary_sections passed")


def test_generate_user_summary_shows_concerns():
    """User summary should list HIGH concerns for a problematic policy."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_WITH_HIGH_CONCERNS, "DataBroker Corp.")
    summary = analyzer.generate_user_summary(analysis)
    assert "[HIGH CONCERN]" in summary, \
        "Summary should surface HIGH concerns for problematic policy"
    print("✓ test_generate_user_summary_shows_concerns passed")


def test_generate_user_summary_no_concerns_message():
    """User summary should show a no-concerns message for a clean policy."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_WITHOUT_CONCERNS, "PrivacyFirst Corp.")
    summary = analyzer.generate_user_summary(analysis)
    assert "No major privacy concerns detected" in summary, \
        "Should indicate no major concerns for a clean policy"
    print("✓ test_generate_user_summary_no_concerns_message passed")


def test_generate_user_summary_word_count():
    """User summary should include the word count of the analyzed document."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    summary = analyzer.generate_user_summary(analysis)
    assert "words" in summary.lower(), "Summary should reference document word count"
    print("✓ test_generate_user_summary_word_count passed")


# ---------------------------------------------------------------------------
# Tests: format_report includes new sections
# ---------------------------------------------------------------------------

def test_format_report_includes_privacy_concerns():
    """format_report() should include a Privacy Concerns section when present."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    report = analyzer.format_report(analysis)
    assert "Privacy Concerns Detected" in report, \
        "format_report() should include 'Privacy Concerns Detected' section"
    print("✓ test_format_report_includes_privacy_concerns passed")


def test_format_report_includes_data_destinations():
    """format_report() should include a Data Destinations section when present."""
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_WITH_DESTINATIONS, "MultiService Inc.")
    report = analyzer.format_report(analysis)
    assert "Data Destinations" in report, \
        "format_report() should include 'Data Destinations' section"
    print("✓ test_format_report_includes_data_destinations passed")


def test_format_report_omits_empty_sections():
    """format_report() should not include concerns section if none found."""
    analyzer = PolicyAnalyzer()
    # Minimal text with no concerns triggers
    analysis = analyzer.analyze("We provide a service.", "Minimal Co.")
    report = analyzer.format_report(analysis)
    assert "Privacy Concerns Detected" not in report, \
        "Should omit concerns section when no concerns detected"
    print("✓ test_format_report_omits_empty_sections passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all privacy concern and destination tests."""
    print("=" * 80)
    print("PRIVACY CONCERNS & DATA DESTINATIONS TESTS")
    print("=" * 80)
    print()

    # detect_privacy_concerns tests
    test_high_concern_data_selling()
    test_high_concern_targeted_advertising()
    test_high_concern_precise_location()
    test_medium_concerns_detected()
    test_low_concerns_detected()
    test_no_false_positives_for_clean_policy()
    test_concerns_return_type()
    test_empty_text_returns_no_concerns()

    # detect_data_destinations tests
    test_data_destinations_purposes()
    test_data_destinations_recipients()
    test_data_destinations_return_type()
    test_data_destinations_empty_input()

    # analyze() integration tests
    test_analyze_includes_privacy_concerns()
    test_analyze_includes_data_destinations()
    test_analyze_output_is_json_serializable()

    # generate_user_summary tests
    test_generate_user_summary_returns_string()
    test_generate_user_summary_sections()
    test_generate_user_summary_shows_concerns()
    test_generate_user_summary_no_concerns_message()
    test_generate_user_summary_word_count()

    # format_report tests
    test_format_report_includes_privacy_concerns()
    test_format_report_includes_data_destinations()
    test_format_report_omits_empty_sections()

    print()
    print("=" * 80)

    # Show a sample user summary
    print("\nSAMPLE USER SUMMARY OUTPUT")
    print("=" * 80)
    analyzer = PolicyAnalyzer()
    analysis = analyzer.analyze(POLICY_COMBINED, "BigTech Ltd.")
    print(analyzer.generate_user_summary(analysis))

    print("All tests completed successfully! ✓")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
