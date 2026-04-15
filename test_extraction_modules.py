#!/usr/bin/env python3
"""
Tests for extraction_modules.py

Covers all seven extraction modules and the top-level run_all_extractors()
helper.  Follows the project's function-based testing convention:
  - Plain functions named test_*
  - assert statements for assertions
  - Print "✓ <name> passed" on success
  - main() calls all tests in order
"""

from extraction_modules import (
    TechStackExtractor,
    WebsiteDomainExtractor,
    RepositoryExtractor,
    ThirdPartyServiceExtractor,
    APIIntegrationExtractor,
    BotAutomationExtractor,
    DataSharingExtractor,
    run_all_extractors,
    format_extraction_report,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TECH_HEAVY = """
Our platform is built on AWS (Amazon Web Services) and deploys containers
via Kubernetes and Docker. The backend is written in Python and Go, with a
React frontend served via Next.js. Data is stored in PostgreSQL and Redis.
We use TensorFlow and PyTorch for machine learning, and our CI/CD pipeline
runs on GitHub Actions. Static assets are served from AWS CloudFront.
"""

DOMAIN_HEAVY = """
Visit our website at https://www.example.com for details.
Our API documentation is at https://api.example.com/v2/docs.
We also operate https://status.example.com and partner with stripe.com,
sendgrid.com, and analytics.google.com.
Contact us at example.org or support.example.co.uk.
"""

REPO_HEAVY = """
Our source code is open-source and hosted at https://github.com/example/myapp.
We also mirror to https://gitlab.com/example/myapp.
Contributions are welcome — fork the repository on GitHub and submit a pull
request. We use Bitbucket for internal projects.
"""

SERVICE_HEAVY = """
Payments on our platform are processed by Stripe and PayPal.
We use Google Analytics and Mixpanel to understand usage patterns.
Transactional emails are sent via SendGrid; newsletters go through Mailchimp.
Customer support is handled in Zendesk and Intercom.
Our ads are managed through Google Ads and Facebook Ads.
Error tracking uses Sentry and performance monitoring uses Datadog.
"""

API_HEAVY = """
Our REST API follows the OpenAPI 3.0 specification.  All endpoints return
JSON and require OAuth 2.0 bearer tokens for authentication.  We also
provide a GraphQL endpoint at /graphql for complex queries.  Webhooks can
be configured to notify your system of events; the callback URL must be
HTTPS.  Native integrations include Zapier, Slack API, and Salesforce.
"""

BOT_HEAVY = """
Our AI assistant (chatbot) helps customers 24/7.  Automated scraping of our
content is prohibited; web crawlers that ignore robots.txt will be blocked.
We use Selenium and Puppeteer for automated testing.  RPA workflows are
supported via our API.  Our virtual assistant understands natural language.
"""

SHARING_HEAVY = """
We collect your name, email address, IP address, and browsing history.
We may share your personal data with our advertising partners with your
explicit consent.  Your payment information is processed by Stripe.
We disclose your usage data to third-party analytics providers for analytics
purposes.  We share information as required by law and in the event of a
merger or acquisition.  Location data may be shared for fraud detection.
"""

EMPTY_TEXT = "Nothing interesting here at all."


# ---------------------------------------------------------------------------
# 1. TechStackExtractor
# ---------------------------------------------------------------------------

def test_tech_stack_detects_cloud_platforms():
    result = TechStackExtractor().extract(TECH_HEAVY)
    assert 'by_category' in result
    assert 'all_technologies' in result
    cloud = result['by_category'].get('cloud_platforms', [])
    assert 'aws' in [c.lower() for c in cloud], f"Expected 'aws' in cloud_platforms, got {cloud}"
    print("✓ test_tech_stack_detects_cloud_platforms passed")


def test_tech_stack_detects_languages():
    result = TechStackExtractor().extract(TECH_HEAVY)
    langs = result['by_category'].get('languages', [])
    found = [l.lower() for l in langs]
    assert 'python' in found, f"Expected 'python' in languages, got {found}"
    assert 'go' in found, f"Expected 'go' in languages, got {found}"
    print("✓ test_tech_stack_detects_languages passed")


def test_tech_stack_detects_infrastructure():
    result = TechStackExtractor().extract(TECH_HEAVY)
    infra = result['by_category'].get('infrastructure', [])
    found_lower = [i.lower() for i in infra]
    assert 'kubernetes' in found_lower, f"Expected kubernetes, got {found_lower}"
    assert 'docker' in found_lower, f"Expected docker, got {found_lower}"
    print("✓ test_tech_stack_detects_infrastructure passed")


def test_tech_stack_all_technologies_is_flat_list():
    result = TechStackExtractor().extract(TECH_HEAVY)
    assert isinstance(result['all_technologies'], list)
    # all_technologies should be the union of by_category values
    all_from_cats = [item for items in result['by_category'].values() for item in items]
    assert set(result['all_technologies']) == set(all_from_cats)
    print("✓ test_tech_stack_all_technologies_is_flat_list passed")


def test_tech_stack_empty_text():
    result = TechStackExtractor().extract(EMPTY_TEXT)
    assert result['by_category'] == {}
    assert result['all_technologies'] == []
    print("✓ test_tech_stack_empty_text passed")


# ---------------------------------------------------------------------------
# 2. WebsiteDomainExtractor
# ---------------------------------------------------------------------------

def test_website_domain_extracts_urls():
    result = WebsiteDomainExtractor().extract(DOMAIN_HEAVY)
    assert 'urls' in result
    assert isinstance(result['urls'], list)
    found = ' '.join(result['urls'])
    assert 'example.com' in found, f"Expected example.com URL, got {result['urls']}"
    print("✓ test_website_domain_extracts_urls passed")


def test_website_domain_extracts_domains():
    result = WebsiteDomainExtractor().extract(DOMAIN_HEAVY)
    assert 'domains' in result
    assert isinstance(result['domains'], list)
    assert len(result['domains']) > 0
    print("✓ test_website_domain_extracts_domains passed")


def test_website_domain_deduplicates_urls():
    text = "https://example.com/a https://example.com/a https://example.com/b"
    result = WebsiteDomainExtractor().extract(text)
    urls = result['urls']
    assert len(urls) == len(set(urls)), "URLs should be deduplicated"
    print("✓ test_website_domain_deduplicates_urls passed")


def test_website_domain_empty_text():
    result = WebsiteDomainExtractor().extract(EMPTY_TEXT)
    assert isinstance(result['urls'], list)
    assert isinstance(result['domains'], list)
    print("✓ test_website_domain_empty_text passed")


# ---------------------------------------------------------------------------
# 3. RepositoryExtractor
# ---------------------------------------------------------------------------

def test_repository_detects_vcs_platforms():
    result = RepositoryExtractor().extract(REPO_HEAVY)
    platforms = result['vcs_platforms_mentioned']
    found = [p.lower() for p in platforms]
    assert 'github' in found, f"Expected github in platforms, got {found}"
    assert 'gitlab' in found, f"Expected gitlab in platforms, got {found}"
    print("✓ test_repository_detects_vcs_platforms passed")


def test_repository_extracts_repo_urls():
    result = RepositoryExtractor().extract(REPO_HEAVY)
    assert isinstance(result['repository_urls'], list)
    assert any('github.com' in u for u in result['repository_urls']), \
        f"Expected GitHub URL, got {result['repository_urls']}"
    print("✓ test_repository_extracts_repo_urls passed")


def test_repository_context_snippets():
    result = RepositoryExtractor().extract(REPO_HEAVY)
    assert isinstance(result['context_snippets'], list)
    print("✓ test_repository_context_snippets passed")


def test_repository_empty_text():
    result = RepositoryExtractor().extract(EMPTY_TEXT)
    assert result['vcs_platforms_mentioned'] == []
    assert result['repository_urls'] == []
    print("✓ test_repository_empty_text passed")


# ---------------------------------------------------------------------------
# 4. ThirdPartyServiceExtractor
# ---------------------------------------------------------------------------

def test_third_party_detects_payment_processors():
    result = ThirdPartyServiceExtractor().extract(SERVICE_HEAVY)
    by_cat = result['by_category']
    assert 'payment_processors' in by_cat, f"payment_processors not found in {list(by_cat.keys())}"
    names = [s.lower() for s in by_cat['payment_processors']]
    assert 'stripe' in names, f"Expected stripe, got {names}"
    print("✓ test_third_party_detects_payment_processors passed")


def test_third_party_detects_analytics():
    result = ThirdPartyServiceExtractor().extract(SERVICE_HEAVY)
    analytics = result['by_category'].get('analytics', [])
    names = [s.lower() for s in analytics]
    assert 'google analytics' in names, f"Expected google analytics, got {names}"
    assert 'mixpanel' in names, f"Expected mixpanel, got {names}"
    print("✓ test_third_party_detects_analytics passed")


def test_third_party_detects_email_marketing():
    result = ThirdPartyServiceExtractor().extract(SERVICE_HEAVY)
    email_svcs = result['by_category'].get('email_marketing', [])
    names = [s.lower() for s in email_svcs]
    assert 'sendgrid' in names, f"Expected sendgrid, got {names}"
    print("✓ test_third_party_detects_email_marketing passed")


def test_third_party_all_services_flat():
    result = ThirdPartyServiceExtractor().extract(SERVICE_HEAVY)
    assert isinstance(result['all_services'], list)
    assert len(result['all_services']) > 0
    print("✓ test_third_party_all_services_flat passed")


def test_third_party_empty_text():
    result = ThirdPartyServiceExtractor().extract(EMPTY_TEXT)
    assert result['by_category'] == {}
    assert result['all_services'] == []
    print("✓ test_third_party_empty_text passed")


# ---------------------------------------------------------------------------
# 5. APIIntegrationExtractor
# ---------------------------------------------------------------------------

def test_api_detects_rest():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    assert 'rest' in result['protocols'], f"Expected rest in protocols, got {list(result['protocols'].keys())}"
    print("✓ test_api_detects_rest passed")


def test_api_detects_graphql():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    assert 'graphql' in result['protocols'], f"Expected graphql, got {list(result['protocols'].keys())}"
    print("✓ test_api_detects_graphql passed")


def test_api_detects_webhook():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    assert 'webhook' in result['protocols'], f"Expected webhook, got {list(result['protocols'].keys())}"
    print("✓ test_api_detects_webhook passed")


def test_api_detects_oauth():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    assert 'oauth' in result['protocols'], f"Expected oauth, got {list(result['protocols'].keys())}"
    print("✓ test_api_detects_oauth passed")


def test_api_detects_named_integrations():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    names = [n.lower() for n in result['named_integrations']]
    assert 'zapier' in names, f"Expected zapier, got {names}"
    print("✓ test_api_detects_named_integrations passed")


def test_api_endpoint_patterns():
    result = APIIntegrationExtractor().extract(API_HEAVY)
    assert isinstance(result['endpoint_patterns'], list)
    print("✓ test_api_endpoint_patterns passed")


def test_api_empty_text():
    result = APIIntegrationExtractor().extract(EMPTY_TEXT)
    assert result['protocols'] == {}
    assert result['named_integrations'] == []
    print("✓ test_api_empty_text passed")


# ---------------------------------------------------------------------------
# 6. BotAutomationExtractor
# ---------------------------------------------------------------------------

def test_bot_detects_chatbots():
    result = BotAutomationExtractor().extract(BOT_HEAVY)
    by_type = result['by_type']
    assert 'chatbots' in by_type, f"Expected chatbots in by_type, got {list(by_type.keys())}"
    found = [k.lower() for k in by_type['chatbots']]
    assert 'chatbot' in found, f"Expected 'chatbot', got {found}"
    print("✓ test_bot_detects_chatbots passed")


def test_bot_detects_crawlers_scrapers():
    result = BotAutomationExtractor().extract(BOT_HEAVY)
    by_type = result['by_type']
    assert 'crawlers_scrapers' in by_type, f"Expected crawlers_scrapers, got {list(by_type.keys())}"
    print("✓ test_bot_detects_crawlers_scrapers passed")


def test_bot_detects_automated_systems():
    result = BotAutomationExtractor().extract(BOT_HEAVY)
    by_type = result['by_type']
    assert 'automated_systems' in by_type, f"Expected automated_systems, got {list(by_type.keys())}"
    systems = [s.lower() for s in by_type['automated_systems']]
    assert any(s in systems for s in ['selenium', 'puppeteer', 'rpa', 'robotic process automation']), \
        f"Expected automation tools, got {systems}"
    print("✓ test_bot_detects_automated_systems passed")


def test_bot_prohibition_snippets():
    result = BotAutomationExtractor().extract(BOT_HEAVY)
    assert isinstance(result['prohibition_snippets'], list)
    # The fixture text explicitly prohibits scraping
    combined = ' '.join(result['prohibition_snippets']).lower()
    assert 'prohibit' in combined or 'scraping' in combined or 'crawlers' in combined, \
        f"Expected prohibition mention, got: {result['prohibition_snippets']}"
    print("✓ test_bot_prohibition_snippets passed")


def test_bot_all_mentions_flat():
    result = BotAutomationExtractor().extract(BOT_HEAVY)
    assert isinstance(result['all_mentions'], list)
    assert len(result['all_mentions']) > 0
    print("✓ test_bot_all_mentions_flat passed")


def test_bot_empty_text():
    result = BotAutomationExtractor().extract(EMPTY_TEXT)
    assert result['by_type'] == {}
    assert result['all_mentions'] == []
    print("✓ test_bot_empty_text passed")


# ---------------------------------------------------------------------------
# 7. DataSharingExtractor
# ---------------------------------------------------------------------------

def test_data_sharing_detects_data_types():
    result = DataSharingExtractor().extract(SHARING_HEAVY)
    dt = result['data_types_mentioned']
    assert isinstance(dt, dict)
    # Should find at least personal identifiers
    assert 'personal_identifiers' in dt, f"Expected personal_identifiers, got {list(dt.keys())}"
    ids_lower = [i.lower() for i in dt['personal_identifiers']]
    assert 'email address' in ids_lower or 'name' in ids_lower, f"Got: {ids_lower}"
    print("✓ test_data_sharing_detects_data_types passed")


def test_data_sharing_detects_recipients():
    result = DataSharingExtractor().extract(SHARING_HEAVY)
    assert isinstance(result['recipients'], list)
    print("✓ test_data_sharing_detects_recipients passed")


def test_data_sharing_detects_purposes():
    result = DataSharingExtractor().extract(SHARING_HEAVY)
    purposes = result['purposes']
    assert isinstance(purposes, list)
    assert len(purposes) > 0, "Expected at least one purpose"
    print("✓ test_data_sharing_detects_purposes passed")


def test_data_sharing_detects_conditions():
    result = DataSharingExtractor().extract(SHARING_HEAVY)
    conditions = result['conditions']
    assert isinstance(conditions, list)
    combined = ' '.join(conditions).lower()
    assert 'consent' in combined or 'law' in combined or 'merger' in combined, \
        f"Expected legal conditions, got: {conditions}"
    print("✓ test_data_sharing_detects_conditions passed")


def test_data_sharing_empty_text():
    result = DataSharingExtractor().extract(EMPTY_TEXT)
    assert result['data_types_mentioned'] == {}
    assert result['recipients'] == []
    assert result['purposes'] == []
    print("✓ test_data_sharing_empty_text passed")


# ---------------------------------------------------------------------------
# run_all_extractors
# ---------------------------------------------------------------------------

def test_run_all_extractors_returns_all_keys():
    text = " ".join([TECH_HEAVY, DOMAIN_HEAVY, SERVICE_HEAVY, API_HEAVY, BOT_HEAVY, SHARING_HEAVY])
    result = run_all_extractors(text, "TestCorp")
    expected_keys = [
        'company_name', 'analysis_date', 'document_length', 'word_count',
        'tech_stack', 'websites_domains', 'repositories',
        'third_party_services', 'apis_integrations', 'bots_automation',
        'data_sharing',
    ]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
    print("✓ test_run_all_extractors_returns_all_keys passed")


def test_run_all_extractors_metadata():
    result = run_all_extractors("hello world", "AcmeCo")
    assert result['company_name'] == "AcmeCo"
    assert result['word_count'] == 2
    assert result['document_length'] == len("hello world")
    assert isinstance(result['analysis_date'], str)
    print("✓ test_run_all_extractors_metadata passed")


def test_run_all_extractors_default_company_name():
    result = run_all_extractors("some text")
    assert result['company_name'] == "Unknown"
    print("✓ test_run_all_extractors_default_company_name passed")


# ---------------------------------------------------------------------------
# format_extraction_report
# ---------------------------------------------------------------------------

def test_format_extraction_report_returns_string():
    result = run_all_extractors(TECH_HEAVY + SERVICE_HEAVY, "Demo Corp")
    report = format_extraction_report(result)
    assert isinstance(report, str)
    assert "EXTRACTION REPORT" in report
    assert "Demo Corp" in report
    print("✓ test_format_extraction_report_returns_string passed")


def test_format_extraction_report_contains_sections():
    text = " ".join([TECH_HEAVY, SERVICE_HEAVY, API_HEAVY])
    result = run_all_extractors(text, "Demo Corp")
    report = format_extraction_report(result)
    assert "TECH STACK" in report
    assert "THIRD-PARTY SERVICES" in report
    assert "APIs" in report
    print("✓ test_format_extraction_report_contains_sections passed")


# ---------------------------------------------------------------------------
# Integration: PolicyAnalyzer uses extraction modules
# ---------------------------------------------------------------------------

def test_policy_analyzer_includes_structured_fields():
    """PolicyAnalyzer.analyze() should include all 7 structured extraction keys."""
    from policy_analyzer import PolicyAnalyzer
    analyzer = PolicyAnalyzer()
    text = TECH_HEAVY + SERVICE_HEAVY + API_HEAVY
    result = analyzer.analyze(text, "IntegrationCorp")
    structured_keys = [
        'tech_stack', 'websites_domains', 'repositories',
        'third_party_services_structured', 'apis_integrations',
        'bots_automation', 'data_sharing_structured',
    ]
    for key in structured_keys:
        assert key in result, f"Missing structured key in PolicyAnalyzer output: {key}"
    print("✓ test_policy_analyzer_includes_structured_fields passed")


def test_policy_analyzer_format_report_includes_structured_sections():
    """format_report() should render the new structured sections."""
    from policy_analyzer import PolicyAnalyzer
    analyzer = PolicyAnalyzer()
    text = TECH_HEAVY + SERVICE_HEAVY + API_HEAVY
    result = analyzer.analyze(text, "IntegrationCorp")
    report = analyzer.format_report(result)
    assert "STRUCTURED EXTRACTION RESULTS" in report, "Structured section header missing from report"
    print("✓ test_policy_analyzer_format_report_includes_structured_sections passed")


# ---------------------------------------------------------------------------
# main runner
# ---------------------------------------------------------------------------

def main():
    print("Running extraction_modules tests...")
    print("=" * 80)

    # TechStackExtractor
    test_tech_stack_detects_cloud_platforms()
    test_tech_stack_detects_languages()
    test_tech_stack_detects_infrastructure()
    test_tech_stack_all_technologies_is_flat_list()
    test_tech_stack_empty_text()

    # WebsiteDomainExtractor
    test_website_domain_extracts_urls()
    test_website_domain_extracts_domains()
    test_website_domain_deduplicates_urls()
    test_website_domain_empty_text()

    # RepositoryExtractor
    test_repository_detects_vcs_platforms()
    test_repository_extracts_repo_urls()
    test_repository_context_snippets()
    test_repository_empty_text()

    # ThirdPartyServiceExtractor
    test_third_party_detects_payment_processors()
    test_third_party_detects_analytics()
    test_third_party_detects_email_marketing()
    test_third_party_all_services_flat()
    test_third_party_empty_text()

    # APIIntegrationExtractor
    test_api_detects_rest()
    test_api_detects_graphql()
    test_api_detects_webhook()
    test_api_detects_oauth()
    test_api_detects_named_integrations()
    test_api_endpoint_patterns()
    test_api_empty_text()

    # BotAutomationExtractor
    test_bot_detects_chatbots()
    test_bot_detects_crawlers_scrapers()
    test_bot_detects_automated_systems()
    test_bot_prohibition_snippets()
    test_bot_all_mentions_flat()
    test_bot_empty_text()

    # DataSharingExtractor
    test_data_sharing_detects_data_types()
    test_data_sharing_detects_recipients()
    test_data_sharing_detects_purposes()
    test_data_sharing_detects_conditions()
    test_data_sharing_empty_text()

    # run_all_extractors
    test_run_all_extractors_returns_all_keys()
    test_run_all_extractors_metadata()
    test_run_all_extractors_default_company_name()

    # format_extraction_report
    test_format_extraction_report_returns_string()
    test_format_extraction_report_contains_sections()

    # Integration
    test_policy_analyzer_includes_structured_fields()
    test_policy_analyzer_format_report_includes_structured_sections()

    print("=" * 80)
    print("All extraction_modules tests passed!")


if __name__ == "__main__":
    main()
