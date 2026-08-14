"""Regression tests for schema and technology matching."""

from extraction_modules import TechStackExtractor
from policy_analyzer import PolicyAnalyzer


def test_tech_stack_avoids_embedded_short_name_matches():
    result = TechStackExtractor().extract(
        'Our governance model covers JavaScript application controls.'
    )
    languages = [item.lower() for item in result['by_category'].get('languages', [])]
    assert 'go' not in languages
    assert 'java' not in languages
    assert 'javascript' in languages


def test_repository_url_schema_alias_matches_canonical_key():
    result = PolicyAnalyzer().extract_repositories(
        'Source code is hosted at https://github.com/example/project.'
    )
    assert result['repo_urls'] == result['repository_urls']
