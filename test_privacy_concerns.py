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
# Sample texts for new feature tests
# ---------------------------------------------------------------------------

POLICY_WITH_REPOS = """
Terms of Service - OpenSourceCo

Our SDK is hosted at https://github.com/opensourceco/sdk and documentation
lives at https://gitlab.com/opensourceco/docs. We also maintain a public
mirror on https://bitbucket.org/opensourceco/mirror.
Please refer to GitHub for all issue tracking.
"""

POLICY_WITH_APIS = """
Terms of Service - APIFirst Inc.

Our RESTful API is available at https://api.apifirst.com/v2/users.
We support GraphQL queries at https://api.apifirst.com/graphql.
Authentication uses OAuth 2.0 and API keys issued per account.
Webhooks notify your endpoint on account events.
We provide SDKs for popular languages.
"""

POLICY_WITH_BOTS = """
Terms of Service - AutoBot Ltd.

We deploy automated crawlers to index public web content.
Our chatbot is powered by GPT technology.
Web scraping of our content is prohibited without prior consent.
Scheduled jobs run nightly data exports.
RPA workflows process high-volume transactions.
"""

POLICY_WITH_THIRD_PARTY = """
Privacy Policy - MarketingPlatform Inc.

We use Stripe and PayPal for payment processing.
Analytics are provided by Google Analytics and Mixpanel.
Emails are sent via SendGrid and Mailchimp.
Our CDN infrastructure is handled by Cloudflare.
Customer support is powered by Zendesk.
We show advertisements via Google Ads and DoubleClick.
"""

POLICY_WITH_DATA_SHARING = """
Privacy Policy - DataSharing Corp.

We share personal data and browsing history with third parties.
We disclose contact information and device data to advertisers.
Business partners and service providers receive usage data.
Law enforcement may receive your financial data upon request.
Our affiliates and subsidiaries have access to location data.
"""


# ---------------------------------------------------------------------------
# Tests: extract_websites_and_domains
# ---------------------------------------------------------------------------

def test_websites_and_domains_extracts_urls():
    """Should extract full URLs into the 'urls' list."""
    analyzer = PolicyAnalyzer()
    text = "Visit https://example.com/privacy and http://test.org/terms for details."
    result = analyzer.extract_websites_and_domains(text)
    assert 'urls' in result, "Result should have 'urls' key"
    assert isinstance(result['urls'], list), "'urls' should be a list"
    assert len(result['urls']) >= 2, "Should find at least 2 URLs"
    assert any('example.com' in u for u in result['urls']), "Should find example.com URL"
    print("✓ test_websites_and_domains_extracts_urls passed")


def test_websites_and_domains_extracts_domains():
    """Should extract domain names into the 'domains' list."""
    analyzer = PolicyAnalyzer()
    text = "Our partner is partner.io and we use service.example.net regularly."
    result = analyzer.extract_websites_and_domains(text)
    assert 'domains' in result, "Result should have 'domains' key"
    assert isinstance(result['domains'], list), "'domains' should be a list"
    print("✓ test_websites_and_domains_extracts_domains passed")


def test_websites_and_domains_empty_input():
    """Empty text should return empty lists."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_websites_and_domains("")
    assert result['urls'] == [], "Empty text should yield empty urls"
    assert result['domains'] == [], "Empty text should yield empty domains"
    print("✓ test_websites_and_domains_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: extract_repositories
# ---------------------------------------------------------------------------

def test_repositories_detects_github_url():
    """Should detect a GitHub repository URL."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_repositories(POLICY_WITH_REPOS)
    assert 'repo_urls' in result, "Result should have 'repo_urls' key"
    assert any('github.com' in u for u in result['repo_urls']), \
        "Should detect GitHub URL"
    print("✓ test_repositories_detects_github_url passed")


def test_repositories_detects_gitlab_url():
    """Should detect a GitLab repository URL."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_repositories(POLICY_WITH_REPOS)
    assert any('gitlab.com' in u for u in result['repo_urls']), \
        "Should detect GitLab URL"
    print("✓ test_repositories_detects_gitlab_url passed")


def test_repositories_detects_keyword_mentions():
    """Should capture keyword mentions of GitHub/GitLab in repo_mentions."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_repositories(POLICY_WITH_REPOS)
    assert 'repo_mentions' in result, "Result should have 'repo_mentions' key"
    assert isinstance(result['repo_mentions'], list), "'repo_mentions' should be a list"
    print("✓ test_repositories_detects_keyword_mentions passed")


def test_repositories_empty_input():
    """Empty text should return empty repo lists."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_repositories("")
    assert result['repo_urls'] == [], "Empty text should yield empty repo_urls"
    assert result['repo_mentions'] == [], "Empty text should yield empty repo_mentions"
    print("✓ test_repositories_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: extract_third_party_services_categorised
# ---------------------------------------------------------------------------

def test_third_party_detects_payment_processors():
    """Should detect Stripe and PayPal as payment processors."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_third_party_services_categorised(POLICY_WITH_THIRD_PARTY)
    assert 'payment_processors' in result, "Should detect payment_processors category"
    assert 'stripe' in result['payment_processors'], "Should detect Stripe"
    assert 'paypal' in result['payment_processors'], "Should detect PayPal"
    print("✓ test_third_party_detects_payment_processors passed")


def test_third_party_detects_analytics_platforms():
    """Should detect Google Analytics and Mixpanel as analytics platforms."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_third_party_services_categorised(POLICY_WITH_THIRD_PARTY)
    assert 'analytics_platforms' in result, "Should detect analytics_platforms category"
    assert 'google analytics' in result['analytics_platforms'], "Should detect Google Analytics"
    assert 'mixpanel' in result['analytics_platforms'], "Should detect Mixpanel"
    print("✓ test_third_party_detects_analytics_platforms passed")


def test_third_party_detects_email_services():
    """Should detect SendGrid and Mailchimp as email services."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_third_party_services_categorised(POLICY_WITH_THIRD_PARTY)
    assert 'email_services' in result, "Should detect email_services category"
    assert 'sendgrid' in result['email_services'], "Should detect SendGrid"
    assert 'mailchimp' in result['email_services'], "Should detect Mailchimp"
    print("✓ test_third_party_detects_email_services passed")


def test_third_party_returns_dict_of_lists():
    """Return type should be a dict mapping strings to lists of strings."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_third_party_services_categorised(POLICY_WITH_THIRD_PARTY)
    assert isinstance(result, dict), "Should return a dict"
    for cat, services in result.items():
        assert isinstance(services, list), f"Category '{cat}' should map to a list"
        for svc in services:
            assert isinstance(svc, str), "Each service name should be a string"
    print("✓ test_third_party_returns_dict_of_lists passed")


def test_third_party_empty_input_returns_empty_dict():
    """Empty text should return an empty dict."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_third_party_services_categorised("")
    assert result == {}, f"Empty text should return empty dict, got {result}"
    print("✓ test_third_party_empty_input_returns_empty_dict passed")


# ---------------------------------------------------------------------------
# Tests: extract_apis_and_integrations
# ---------------------------------------------------------------------------

def test_apis_detects_rest():
    """Should detect REST API mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations(POLICY_WITH_APIS)
    assert 'api_types' in result, "Result should have 'api_types' key"
    assert 'REST API' in result['api_types'], "Should detect REST API"
    print("✓ test_apis_detects_rest passed")


def test_apis_detects_graphql():
    """Should detect GraphQL mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations(POLICY_WITH_APIS)
    assert 'GraphQL' in result['api_types'], "Should detect GraphQL"
    print("✓ test_apis_detects_graphql passed")


def test_apis_detects_webhooks():
    """Should detect webhook mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations(POLICY_WITH_APIS)
    assert 'Webhooks' in result['api_types'], "Should detect Webhooks"
    print("✓ test_apis_detects_webhooks passed")


def test_apis_detects_oauth():
    """Should detect OAuth mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations(POLICY_WITH_APIS)
    assert 'OAuth' in result['api_types'], "Should detect OAuth"
    print("✓ test_apis_detects_oauth passed")


def test_apis_extracts_endpoint_urls():
    """Should extract explicit API endpoint URLs."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations(POLICY_WITH_APIS)
    assert 'api_urls' in result, "Result should have 'api_urls' key"
    assert isinstance(result['api_urls'], list), "'api_urls' should be a list"
    assert len(result['api_urls']) > 0, "Should extract at least one API URL"
    print("✓ test_apis_extracts_endpoint_urls passed")


def test_apis_empty_input():
    """Empty text should return empty API detection."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_apis_and_integrations("")
    assert result['api_types'] == [], "Empty text should yield no api_types"
    assert result['api_urls'] == [], "Empty text should yield no api_urls"
    print("✓ test_apis_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: extract_bots_and_automation
# ---------------------------------------------------------------------------

def test_bots_detects_chatbot():
    """Should detect chatbot mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_bots_and_automation(POLICY_WITH_BOTS)
    assert 'Chatbot' in result, "Should detect 'Chatbot'"
    print("✓ test_bots_detects_chatbot passed")


def test_bots_detects_crawler():
    """Should detect web crawler mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_bots_and_automation(POLICY_WITH_BOTS)
    assert 'Web crawler / spider' in result, "Should detect 'Web crawler / spider'"
    print("✓ test_bots_detects_crawler passed")


def test_bots_detects_scraping():
    """Should detect data scraping mention."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_bots_and_automation(POLICY_WITH_BOTS)
    assert 'Data scraping' in result, "Should detect 'Data scraping'"
    print("✓ test_bots_detects_scraping passed")


def test_bots_returns_sorted_list():
    """Should return a sorted list of strings."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_bots_and_automation(POLICY_WITH_BOTS)
    assert isinstance(result, list), "Should return a list"
    for item in result:
        assert isinstance(item, str), "Each item should be a string"
    assert result == sorted(result), "List should be sorted alphabetically"
    print("✓ test_bots_returns_sorted_list passed")


def test_bots_empty_input():
    """Empty text should return an empty list."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_bots_and_automation("")
    assert result == [], f"Empty text should return empty list, got {result}"
    print("✓ test_bots_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: extract_data_sharing_summary
# ---------------------------------------------------------------------------

def test_data_sharing_detects_third_parties():
    """Should identify 'Third parties' as a data recipient."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary(POLICY_WITH_DATA_SHARING)
    assert 'shared_with' in result, "Result should have 'shared_with' key"
    assert 'Third parties' in result['shared_with'], "Should detect 'Third parties'"
    print("✓ test_data_sharing_detects_third_parties passed")


def test_data_sharing_detects_advertisers():
    """Should identify 'Advertisers' as a data recipient."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary(POLICY_WITH_DATA_SHARING)
    assert 'Advertisers' in result['shared_with'], "Should detect 'Advertisers'"
    print("✓ test_data_sharing_detects_advertisers passed")


def test_data_sharing_detects_data_types():
    """Should identify data types being shared."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary(POLICY_WITH_DATA_SHARING)
    assert 'data_types' in result, "Result should have 'data_types' key"
    assert len(result['data_types']) > 0, "Should detect at least one data type"
    print("✓ test_data_sharing_detects_data_types passed")


def test_data_sharing_detects_purposes():
    """Should identify purposes of data sharing."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary(POLICY_WITH_DATA_SHARING)
    assert 'purposes' in result, "Result should have 'purposes' key"
    assert isinstance(result['purposes'], list), "'purposes' should be a list"
    print("✓ test_data_sharing_detects_purposes passed")


def test_data_sharing_return_type():
    """extract_data_sharing_summary should return a dict with three list keys."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary(POLICY_WITH_DATA_SHARING)
    assert isinstance(result, dict), "Should return a dict"
    for key in ('shared_with', 'data_types', 'purposes'):
        assert key in result, f"Dict should contain key '{key}'"
        assert isinstance(result[key], list), f"'{key}' should be a list"
    print("✓ test_data_sharing_return_type passed")


def test_data_sharing_empty_input():
    """Empty text should return empty lists for all three keys."""
    analyzer = PolicyAnalyzer()
    result = analyzer.extract_data_sharing_summary("")
    for key in ('shared_with', 'data_types', 'purposes'):
        assert result[key] == [], f"Empty text: '{key}' should be empty"
    print("✓ test_data_sharing_empty_input passed")


# ---------------------------------------------------------------------------
# Tests: analyze() integration for new features
# ---------------------------------------------------------------------------

def test_analyze_includes_new_feature_keys():
    """analyze() should include all six new extraction keys."""
    analyzer = PolicyAnalyzer()
    text = "We use GitHub. Stripe processes payments. Our REST API uses webhooks."
    result = analyzer.analyze(text, "TestCo")
    for key in ('websites_and_domains', 'repositories', 'third_party_services_categorised',
                'apis_and_integrations', 'bots_and_automation', 'data_sharing_summary'):
        assert key in result, f"analyze() result should contain '{key}'"
    print("✓ test_analyze_includes_new_feature_keys passed")


def test_analyze_new_features_json_serializable():
    """New feature fields should be JSON-serializable."""
    import json as _json
    analyzer = PolicyAnalyzer()
    text = "GitHub repo. Stripe payments. REST API. Chatbot. Third-party data sharing."
    result = analyzer.analyze(text, "TestCo")
    new_keys = ('websites_and_domains', 'repositories', 'third_party_services_categorised',
                'apis_and_integrations', 'bots_and_automation', 'data_sharing_summary')
    for key in new_keys:
        try:
            _json.dumps(result[key])
        except TypeError as exc:
            raise AssertionError(f"Field '{key}' is not JSON-serializable: {exc}")
    print("✓ test_analyze_new_features_json_serializable passed")


# ---------------------------------------------------------------------------
# Tests: format_report() sections for new features
# ---------------------------------------------------------------------------

def test_format_report_includes_websites_section():
    """format_report should include a 'Websites & Domains' section when URLs present."""
    analyzer = PolicyAnalyzer()
    text = "Visit https://example.com for details."
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "Websites & Domains" in report, \
        "format_report should contain 'Websites & Domains' section"
    print("✓ test_format_report_includes_websites_section passed")


def test_format_report_includes_repositories_section():
    """format_report should include a 'Repositories' section when repos present."""
    analyzer = PolicyAnalyzer()
    text = "Our code is at https://github.com/myorg/myrepo"
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "Repositories" in report, \
        "format_report should contain 'Repositories' section"
    print("✓ test_format_report_includes_repositories_section passed")


def test_format_report_includes_third_party_categorised_section():
    """format_report should include categorised third-party section when services found."""
    analyzer = PolicyAnalyzer()
    text = "We use Stripe for payments and Mixpanel for analytics."
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "Third-Party Services (by category)" in report, \
        "format_report should contain 'Third-Party Services (by category)' section"
    print("✓ test_format_report_includes_third_party_categorised_section passed")


def test_format_report_includes_apis_section():
    """format_report should include 'APIs & Integrations' section when API types found."""
    analyzer = PolicyAnalyzer()
    text = "Our REST API and GraphQL endpoint support OAuth 2.0."
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "APIs & Integrations" in report, \
        "format_report should contain 'APIs & Integrations' section"
    print("✓ test_format_report_includes_apis_section passed")


def test_format_report_includes_bots_section():
    """format_report should include 'Bots & Automation' section when bots found."""
    analyzer = PolicyAnalyzer()
    text = "We use a chatbot and automated crawlers."
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "Bots & Automation" in report, \
        "format_report should contain 'Bots & Automation' section"
    print("✓ test_format_report_includes_bots_section passed")


def test_format_report_includes_data_sharing_summary_section():
    """format_report should include 'Data Sharing Summary' section when sharing detected."""
    analyzer = PolicyAnalyzer()
    text = "We share personal data with third parties and advertisers."
    result = analyzer.analyze(text, "TestCo")
    report = analyzer.format_report(result)
    assert "Data Sharing Summary" in report, \
        "format_report should contain 'Data Sharing Summary' section"
    print("✓ test_format_report_includes_data_sharing_summary_section passed")


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

    # ------------------------------------------------------------------ #
    # New feature tests
    # ------------------------------------------------------------------ #
    print()
    print("NEW EXTRACTION FEATURE TESTS")
    print("-" * 40)

    # extract_websites_and_domains
    test_websites_and_domains_extracts_urls()
    test_websites_and_domains_extracts_domains()
    test_websites_and_domains_empty_input()

    # extract_repositories
    test_repositories_detects_github_url()
    test_repositories_detects_gitlab_url()
    test_repositories_detects_keyword_mentions()
    test_repositories_empty_input()

    # extract_third_party_services_categorised
    test_third_party_detects_payment_processors()
    test_third_party_detects_analytics_platforms()
    test_third_party_detects_email_services()
    test_third_party_returns_dict_of_lists()
    test_third_party_empty_input_returns_empty_dict()

    # extract_apis_and_integrations
    test_apis_detects_rest()
    test_apis_detects_graphql()
    test_apis_detects_webhooks()
    test_apis_detects_oauth()
    test_apis_extracts_endpoint_urls()
    test_apis_empty_input()

    # extract_bots_and_automation
    test_bots_detects_chatbot()
    test_bots_detects_crawler()
    test_bots_detects_scraping()
    test_bots_returns_sorted_list()
    test_bots_empty_input()

    # extract_data_sharing_summary
    test_data_sharing_detects_third_parties()
    test_data_sharing_detects_advertisers()
    test_data_sharing_detects_data_types()
    test_data_sharing_detects_purposes()
    test_data_sharing_return_type()
    test_data_sharing_empty_input()

    # analyze() new feature integration
    test_analyze_includes_new_feature_keys()
    test_analyze_new_features_json_serializable()

    # format_report new feature sections
    test_format_report_includes_websites_section()
    test_format_report_includes_repositories_section()
    test_format_report_includes_third_party_categorised_section()
    test_format_report_includes_apis_section()
    test_format_report_includes_bots_section()
    test_format_report_includes_data_sharing_summary_section()

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
