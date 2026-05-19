#!/usr/bin/env python3
"""Standard-library regression tests for PolicyAnalyzer."""

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from batch_analyzer import analyze_batch_from_dict
from policy_analyzer import PolicyAnalyzer

SAMPLE_POLICY = """
ExampleCo Privacy Policy
We use AWS and GitHub to operate our service.
Our chatbot is powered by OpenAI GPT models.
Our REST API supports webhooks for integrations.
We use Stripe for payment processing and SendGrid for email delivery.
We may share your data with payment processors and analytics providers.
Contact privacy@example.com or visit https://example.com/privacy.
"""


class PolicyAnalyzerRegressionTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = PolicyAnalyzer()
        self.results = self.analyzer.analyze(SAMPLE_POLICY, "ExampleCo")

    def test_analyze_core_output_shape(self):
        self.assertEqual(self.results["company_name"], "ExampleCo")
        self.assertGreater(self.results["document_length"], 0)
        self.assertGreater(self.results["word_count"], 0)
        for key in [
            "urls_found",
            "domains_found",
            "emails_found",
            "technologies_detected",
            "api_references",
            "third_party_services",
            "data_sharing_mentions",
            "tech_stack",
            "websites_domains",
            "apis_integrations",
            "data_sharing_structured",
        ]:
            self.assertIn(key, self.results)

    def test_url_domain_and_email_extraction(self):
        self.assertIn("https://example.com/privacy", self.results["urls_found"])
        self.assertIn("privacy@example.com", self.results["emails_found"])
        self.assertIn("example.com", self.results["websites_domains"].get("domains", []))

    def test_technology_and_api_detection(self):
        technologies = self.results["technologies_detected"]
        self.assertIn("aws", technologies.get("platforms", []))
        self.assertIn("github", technologies.get("platforms", []))
        self.assertIn("openai", technologies.get("ai_ml", []))
        self.assertIn("gpt", technologies.get("ai_ml", []))
        self.assertTrue(self.results["api_references"])
        api_types = self.results["apis_and_integrations"].get("api_types", [])
        self.assertIn("REST API", api_types)
        self.assertIn("Webhooks", api_types)

    def test_data_sharing_detection(self):
        sharing_mentions = self.results["data_sharing_mentions"]
        self.assertTrue(any("payment processors" in item for item in sharing_mentions))
        self.assertIn("shared_with", self.results["data_sharing_summary"])
        self.assertIn("purposes", self.results["data_sharing_summary"])

    def test_batch_analysis_output_shape(self):
        batch_results = analyze_batch_from_dict({"ExampleCo": SAMPLE_POLICY})
        self.assertIn("ExampleCo", batch_results)
        self.assertEqual(batch_results["ExampleCo"]["company_name"], "ExampleCo")
        self.assertIn("technologies_detected", batch_results["ExampleCo"])
        self.assertIn("urls_found", batch_results["ExampleCo"])


if __name__ == "__main__":
    unittest.main()
