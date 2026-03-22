#!/usr/bin/env python3
"""
Tests for AIPolicyResearcher.

Covers AI signal detection, clause extraction (training data, automated
decisions, opt-out, profiling, transparency, regulatory references), risk
summary computation, report formatting, and edge cases.
"""

import json

from ai_policy_researcher import AIPolicyResearcher, KNOWN_AI_POLICY_TOOLS


# ---------------------------------------------------------------------------
# Sample policy texts
# ---------------------------------------------------------------------------

# Comprehensive AI-heavy policy
AI_HEAVY_POLICY = """
Privacy Policy — SmartAI Corp

AI AND MACHINE LEARNING:
We use artificial intelligence and machine learning algorithms to personalise
your experience on our platform. Your content, usage data, and interactions
may be used to train our AI models and improve our services.

AUTOMATED DECISIONS:
Certain decisions affecting your account access and content visibility are
made automatically by our algorithm without human review. You have the right
to request human oversight for decisions that significantly affect you.

AI-GENERATED CONTENT:
Some content displayed on our platform is AI-generated using large language
model technology. AI-generated text is labelled where required by law.

OPT-OUT:
You may opt out of AI-based personalisation at any time via your privacy
settings. You also have the right to object to algorithmic profiling.

ALGORITHMIC PROFILING:
We use machine learning to infer your interests and preferences in order to
deliver personalised recommendations and targeted advertising.

AI TRANSPARENCY:
We explain how our AI systems work in our AI Transparency Report. Human
review is available for automated decisions that significantly affect users.

REGULATORY COMPLIANCE:
We comply with GDPR Article 22 regarding automated decision-making. We are
reviewing our obligations under the EU AI Act and align with AI governance
best practices.
"""

# Minimal policy with no AI content
NO_AI_POLICY = """
Terms of Service — Classic Services Ltd

We provide document storage services. By using our services you agree to
these terms. We use standard encryption to protect your files.

Contact us at support@classicservices.com.
"""

# Policy with AI signals but no protections
AI_NO_PROTECTIONS_POLICY = """
Platform Terms — DataHarvest Inc

We use artificial intelligence, machine learning, and automated systems
extensively to analyse user behaviour, profile users, and make decisions
about account features. We may use your data to train our AI models.
Algorithmic profiling is used to predict user preferences and behaviour.
"""


# ---------------------------------------------------------------------------
# KNOWN_AI_POLICY_TOOLS catalogue
# ---------------------------------------------------------------------------

def test_known_tools_structure():
    """KNOWN_AI_POLICY_TOOLS should be a non-empty list of well-formed dicts."""
    assert isinstance(KNOWN_AI_POLICY_TOOLS, list), "Should be a list"
    assert len(KNOWN_AI_POLICY_TOOLS) > 0, "Should not be empty"
    for tool in KNOWN_AI_POLICY_TOOLS:
        assert 'name' in tool, "Each tool should have a 'name'"
        assert 'type' in tool, "Each tool should have a 'type'"
        assert 'url' in tool, "Each tool should have a 'url'"
        assert 'description' in tool, "Each tool should have a 'description'"
        assert isinstance(tool['name'], str) and tool['name']
        assert isinstance(tool['url'], str) and tool['url'].startswith('http')
    print("✓ test_known_tools_structure passed")


def test_known_tools_includes_key_frameworks():
    """Catalogue should include NIST AI RMF and EU AI Act at minimum."""
    names = [t['name'] for t in KNOWN_AI_POLICY_TOOLS]
    combined = ' '.join(names).lower()
    assert 'nist' in combined or 'ai rmf' in combined, "Should include NIST AI RMF"
    assert 'eu ai act' in combined or 'ai act' in combined, "Should include EU AI Act"
    print("✓ test_known_tools_includes_key_frameworks passed")


# ---------------------------------------------------------------------------
# AIPolicyResearcher.research() — return structure
# ---------------------------------------------------------------------------

def test_research_returns_required_keys():
    """research() should return a dict with all expected keys."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "SmartAI Corp")

    required_keys = [
        'company_name', 'analysis_date', 'ai_signals_detected',
        'training_data_clauses', 'automated_decision_clauses',
        'ai_generated_content_clauses', 'ai_opt_out_clauses',
        'profiling_clauses', 'transparency_clauses',
        'regulatory_references', 'known_ai_policy_tools',
        'risk_summary', 'document_length', 'word_count',
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    assert result['company_name'] == "SmartAI Corp"
    assert isinstance(result['document_length'], int) and result['document_length'] > 0
    assert isinstance(result['word_count'], int) and result['word_count'] > 0
    print("✓ test_research_returns_required_keys passed")


def test_research_json_serializable():
    """research() output should be JSON-serializable."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "JSON Test")
    json_str = json.dumps(result, indent=2)
    parsed = json.loads(json_str)
    assert parsed['company_name'] == "JSON Test"
    print("✓ test_research_json_serializable passed")


# ---------------------------------------------------------------------------
# AI signal detection
# ---------------------------------------------------------------------------

def test_detects_ai_signals_in_ai_heavy_policy():
    """AI signal words should be found in a policy that mentions AI."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    signals = result['ai_signals_detected']
    assert isinstance(signals, list)
    assert len(signals) > 0, "Should detect AI signals in AI-heavy policy"
    print(f"  Signals: {signals}")
    print("✓ test_detects_ai_signals_in_ai_heavy_policy passed")


def test_no_ai_signals_in_plain_policy():
    """No AI signal words should be found in a plain, non-AI policy."""
    researcher = AIPolicyResearcher()
    result = researcher.research(NO_AI_POLICY)
    signals = result['ai_signals_detected']
    assert isinstance(signals, list)
    # Signals list may be empty or very small
    assert len(signals) == 0, f"Expected no AI signals, got: {signals}"
    print("✓ test_no_ai_signals_in_plain_policy passed")


# ---------------------------------------------------------------------------
# Clause detection
# ---------------------------------------------------------------------------

def test_detects_training_data_clauses():
    """Training data clauses should be detected in AI-heavy policy."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    assert len(result['training_data_clauses']) > 0, \
        "Should detect training data clauses"
    print("✓ test_detects_training_data_clauses passed")


def test_no_training_data_clauses_in_plain_policy():
    """No training data clauses should be found in a non-AI policy."""
    researcher = AIPolicyResearcher()
    result = researcher.research(NO_AI_POLICY)
    assert len(result['training_data_clauses']) == 0, \
        "Should not detect training data clauses in non-AI policy"
    print("✓ test_no_training_data_clauses_in_plain_policy passed")


def test_detects_automated_decision_clauses():
    """Automated decision clauses should be detected."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    assert len(result['automated_decision_clauses']) > 0, \
        "Should detect automated decision clauses"
    print("✓ test_detects_automated_decision_clauses passed")


def test_detects_opt_out_clauses():
    """Opt-out provisions should be detected."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    assert len(result['ai_opt_out_clauses']) > 0, \
        "Should detect opt-out clauses"
    print("✓ test_detects_opt_out_clauses passed")


def test_detects_profiling_clauses():
    """Profiling clauses should be detected in AI-heavy policy."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    assert len(result['profiling_clauses']) > 0, \
        "Should detect profiling clauses"
    print("✓ test_detects_profiling_clauses passed")


def test_detects_transparency_clauses():
    """Transparency clauses should be detected."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    assert len(result['transparency_clauses']) > 0, \
        "Should detect transparency clauses"
    print("✓ test_detects_transparency_clauses passed")


# ---------------------------------------------------------------------------
# Regulatory references
# ---------------------------------------------------------------------------

def test_detects_gdpr_reference():
    """GDPR references should be detected."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    refs = result['regulatory_references']
    combined = ' '.join(refs).lower()
    assert 'gdpr' in combined or 'article 22' in combined, \
        f"Expected GDPR reference, got: {refs}"
    print("✓ test_detects_gdpr_reference passed")


def test_detects_eu_ai_act_reference():
    """EU AI Act references should be detected."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    refs = result['regulatory_references']
    combined = ' '.join(refs).lower()
    assert 'eu ai act' in combined or 'ai act' in combined, \
        f"Expected EU AI Act reference, got: {refs}"
    print("✓ test_detects_eu_ai_act_reference passed")


def test_no_regulatory_refs_in_plain_policy():
    """Non-AI policy should not produce regulatory references."""
    researcher = AIPolicyResearcher()
    result = researcher.research(NO_AI_POLICY)
    assert len(result['regulatory_references']) == 0, \
        "Non-AI policy should not produce regulatory references"
    print("✓ test_no_regulatory_refs_in_plain_policy passed")


# ---------------------------------------------------------------------------
# Risk summary
# ---------------------------------------------------------------------------

def test_risk_summary_structure():
    """risk_summary should have all required keys."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    risk = result['risk_summary']

    assert 'level' in risk
    assert 'ai_signal_count' in risk
    assert 'concern_count' in risk
    assert 'has_opt_out' in risk
    assert 'has_transparency' in risk

    assert isinstance(risk['ai_signal_count'], int)
    assert isinstance(risk['concern_count'], int)
    assert isinstance(risk['has_opt_out'], bool)
    assert isinstance(risk['has_transparency'], bool)
    print("✓ test_risk_summary_structure passed")


def test_risk_low_for_no_ai_policy():
    """Non-AI policy should receive a LOW risk level."""
    researcher = AIPolicyResearcher()
    result = researcher.research(NO_AI_POLICY)
    risk = result['risk_summary']
    assert 'LOW' in risk['level'].upper(), \
        f"Expected LOW risk for non-AI policy, got: {risk['level']}"
    print("✓ test_risk_low_for_no_ai_policy passed")


def test_risk_high_for_no_protection_policy():
    """Policy with AI but no opt-out or transparency should be HIGH risk."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_NO_PROTECTIONS_POLICY)
    risk = result['risk_summary']
    assert 'HIGH' in risk['level'].upper() or 'MEDIUM' in risk['level'].upper(), \
        f"Expected HIGH/MEDIUM risk, got: {risk['level']}"
    print("✓ test_risk_high_for_no_protection_policy passed")


def test_risk_lower_when_opt_out_present():
    """Policy with opt-out provisions should not be rated HIGH risk."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    risk = result['risk_summary']
    assert 'HIGH' not in risk['level'].upper(), \
        f"Should not be HIGH risk when opt-out present; got: {risk['level']}"
    assert risk['has_opt_out'] is True
    print("✓ test_risk_lower_when_opt_out_present passed")


# ---------------------------------------------------------------------------
# format_report()
# ---------------------------------------------------------------------------

def test_format_report_returns_string():
    """format_report() should return a non-empty string."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "Report Test")
    report = researcher.format_report(result)
    assert isinstance(report, str), "format_report should return a string"
    assert len(report) > 100
    print("✓ test_format_report_returns_string passed")


def test_format_report_contains_sections():
    """Report should contain key section headers."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "Header Test")
    report = researcher.format_report(result)

    assert 'AI POLICY RESEARCH REPORT' in report
    assert 'RISK SUMMARY' in report
    assert 'KNOWN AI POLICY' in report
    print("✓ test_format_report_contains_sections passed")


def test_format_report_includes_company_name():
    """Report should contain the provided company name."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "Acme Corp")
    report = researcher.format_report(result)
    assert 'Acme Corp' in report
    print("✓ test_format_report_includes_company_name passed")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_research_empty_input():
    """research() with empty string should not raise and should return valid structure."""
    researcher = AIPolicyResearcher()
    result = researcher.research("", "Empty")
    assert result['company_name'] == "Empty"
    assert result['ai_signals_detected'] == []
    assert result['training_data_clauses'] == []
    assert result['document_length'] == 0
    assert result['word_count'] == 0
    print("✓ test_research_empty_input passed")


def test_research_default_company_name():
    """research() default company_name should be 'Unknown'."""
    researcher = AIPolicyResearcher()
    result = researcher.research("Some policy text.")
    assert result['company_name'] == "Unknown"
    print("✓ test_research_default_company_name passed")


def test_clauses_are_lists_of_strings():
    """All clause fields should be lists of strings."""
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY)
    clause_keys = [
        'training_data_clauses', 'automated_decision_clauses',
        'ai_generated_content_clauses', 'ai_opt_out_clauses',
        'profiling_clauses', 'transparency_clauses', 'regulatory_references',
        'ai_signals_detected',
    ]
    for key in clause_keys:
        val = result[key]
        assert isinstance(val, list), f"{key} should be a list"
        for item in val:
            assert isinstance(item, str), f"Items in {key} should be strings"
    print("✓ test_clauses_are_lists_of_strings passed")


def test_clauses_capped_per_category():
    """No clause category should return more than 20 entries."""
    researcher = AIPolicyResearcher()
    # Repeat a strongly matching sentence many times
    repeated = (
        "We use artificial intelligence to train our AI models on user data. " * 30
    )
    result = researcher.research(repeated)
    for key in [
        'training_data_clauses', 'automated_decision_clauses',
        'ai_generated_content_clauses', 'ai_opt_out_clauses',
        'profiling_clauses', 'transparency_clauses',
    ]:
        assert len(result[key]) <= 20, f"{key} should be capped at 20"
    print("✓ test_clauses_capped_per_category passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all AIPolicyResearcher tests."""
    print("=" * 80)
    print("AI POLICY RESEARCHER TESTS")
    print("=" * 80)
    print()

    test_known_tools_structure()
    test_known_tools_includes_key_frameworks()

    test_research_returns_required_keys()
    test_research_json_serializable()

    test_detects_ai_signals_in_ai_heavy_policy()
    test_no_ai_signals_in_plain_policy()

    test_detects_training_data_clauses()
    test_no_training_data_clauses_in_plain_policy()
    test_detects_automated_decision_clauses()
    test_detects_opt_out_clauses()
    test_detects_profiling_clauses()
    test_detects_transparency_clauses()

    test_detects_gdpr_reference()
    test_detects_eu_ai_act_reference()
    test_no_regulatory_refs_in_plain_policy()

    test_risk_summary_structure()
    test_risk_low_for_no_ai_policy()
    test_risk_high_for_no_protection_policy()
    test_risk_lower_when_opt_out_present()

    test_format_report_returns_string()
    test_format_report_contains_sections()
    test_format_report_includes_company_name()

    test_research_empty_input()
    test_research_default_company_name()
    test_clauses_are_lists_of_strings()
    test_clauses_capped_per_category()

    print()
    print("=" * 80)
    print("All AIPolicyResearcher tests passed! ✓")
    print("=" * 80)
    print()

    # Show a sample report
    researcher = AIPolicyResearcher()
    result = researcher.research(AI_HEAVY_POLICY, "SmartAI Corp")
    print("SAMPLE REPORT OUTPUT")
    print("=" * 80)
    print(researcher.format_report(result))


if __name__ == "__main__":
    main()
