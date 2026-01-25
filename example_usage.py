#!/usr/bin/env python3
"""
Example usage of the Policy Analyzer Assistant

This script demonstrates how to use the policy analyzer with sample policy text
and shows different ways to utilize the tool.
"""

from policy_analyzer import PolicyAnalyzer
import json


def example_basic_usage():
    """Basic usage example with sample policy text."""
    print("EXAMPLE 1: Basic Analysis")
    print("=" * 80)
    
    # Sample policy text
    sample_policy = """
    Privacy Policy - TechCorp Inc.
    
    Last Updated: January 2024
    
    At TechCorp, we value your privacy. This policy explains how we collect and use data.
    
    Technology Stack:
    - Our website is hosted on AWS (Amazon Web Services)
    - We use GitHub for version control and code repositories
    - Our chatbot is powered by OpenAI's ChatGPT API
    - Payment processing through Stripe
    - Email communications via SendGrid
    - Analytics through Google Analytics and Mixpanel
    
    Third-Party Integrations:
    We integrate with various third-party services including:
    - Zendesk for customer support
    - Intercom for live chat
    - Twilio for SMS notifications
    
    Our REST API connects to multiple services and we use webhooks for real-time updates.
    
    For questions, contact: privacy@techcorp.com or visit https://techcorp.com/privacy
    
    Data Sharing:
    We may share your data with trusted partners including payment processors,
    email service providers, and analytics platforms to improve our services.
    
    Bot Detection:
    We use automated systems and bots to detect fraud and ensure security.
    Our crawler systems index content for search functionality.
    """
    
    # Create analyzer instance
    analyzer = PolicyAnalyzer()
    
    # Perform analysis
    results = analyzer.analyze(sample_policy, "TechCorp Inc.")
    
    # Display formatted report
    print(analyzer.format_report(results))
    print("\n")
    
    return results


def example_json_output():
    """Example showing JSON output for programmatic use."""
    print("\nEXAMPLE 2: JSON Output for Data Processing")
    print("=" * 80)
    
    sample_policy = """
    Terms of Service - SocialApp
    
    We use Firebase for backend services, React for our frontend,
    and integrate with Facebook, Twitter, and Instagram APIs.
    Our machine learning models use TensorFlow and are hosted on Google Cloud Platform.
    
    Contact: support@socialapp.io
    Website: https://socialapp.io
    """
    
    analyzer = PolicyAnalyzer()
    results = analyzer.analyze(sample_policy, "SocialApp")
    
    # Convert to JSON
    json_output = json.dumps(results, indent=2)
    print(json_output)
    print("\n")


def example_batch_analysis():
    """Example analyzing multiple companies' policies."""
    print("\nEXAMPLE 3: Batch Analysis of Multiple Policies")
    print("=" * 80)
    
    policies = {
        "DataCo": """
            DataCo Privacy Policy
            We use MongoDB for databases, Express.js for backend, React for frontend,
            and Node.js runtime (MERN stack). Hosted on Heroku.
            API documentation: https://api.dataco.com/docs
        """,
        "AIStartup": """
            AIStartup Terms
            Our AI models use PyTorch and are trained on Azure ML.
            We integrate Claude AI and GPT-4 for natural language processing.
            Deep learning infrastructure on AWS. Contact: info@aistartup.ai
        """,
        "FinTech": """
            FinTech Privacy Notice
            Payment processing with PayPal and Stripe. PostgreSQL database.
            Django backend with Vue.js frontend. Deployed on Netlify and AWS.
            API: https://api.fintech.com
        """
    }
    
    analyzer = PolicyAnalyzer()
    
    # Analyze all policies
    all_results = {}
    for company, policy in policies.items():
        results = analyzer.analyze(policy, company)
        all_results[company] = results
        
        print(f"\n{company}:")
        print("-" * 40)
        
        # Show summary
        if results['technologies_detected']:
            print("Technologies:")
            for category, techs in results['technologies_detected'].items():
                print(f"  {category}: {', '.join(techs)}")
        
        if results['urls_found']:
            print(f"URLs: {', '.join(results['urls_found'])}")
        
        if results['emails_found']:
            print(f"Emails: {', '.join(results['emails_found'])}")
    
    print("\n" + "=" * 80)
    print(f"Total companies analyzed: {len(all_results)}")
    
    # Summary statistics
    total_urls = sum(len(r['urls_found']) for r in all_results.values())
    total_techs = sum(len(r['technologies_detected']) for r in all_results.values())
    
    print(f"Total URLs extracted: {total_urls}")
    print(f"Total technology categories detected: {total_techs}")
    print("\n")


def example_custom_analysis():
    """Example showing how to extend the analyzer for custom needs."""
    print("\nEXAMPLE 4: Custom Analysis - Dating Site Bot Detection")
    print("=" * 80)
    
    dating_site_policy = """
    Dating Site Terms of Service
    
    Bot Policy:
    We employ automated bots and chatbots to enhance user experience.
    Our AI-powered matching system uses machine learning algorithms.
    We use automated systems to detect fake profiles and spam.
    
    Technology:
    - Real-time chat powered by WebSocket connections
    - Profile verification using AI and neural networks
    - Recommendation engine built with Python and scikit-learn
    - Mobile apps built with React Native
    - Backend API using GraphQL
    
    Third Parties:
    We share data with verification services, payment processors (Stripe),
    and analytics platforms (Google Analytics).
    
    For more info: https://datingsite.com/safety
    Support: help@datingsite.com
    """
    
    analyzer = PolicyAnalyzer()
    results = analyzer.analyze(dating_site_policy, "Dating Site")
    
    # Custom analysis - focus on bot mentions
    bot_techs = results['technologies_detected'].get('bots', [])
    ai_techs = results['technologies_detected'].get('ai_ml', [])
    
    print(f"Bot/Automation Technologies: {len(bot_techs)}")
    for bot in bot_techs:
        print(f"  - {bot}")
    
    print(f"\nAI/ML Technologies: {len(ai_techs)}")
    for ai in ai_techs:
        print(f"  - {ai}")
    
    print(f"\nThird-Party Services: {len(results['third_party_services'])}")
    for service in results['third_party_services'][:5]:
        print(f"  - {service}")
    
    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "POLICY ANALYZER - USAGE EXAMPLES" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Run examples
    example_basic_usage()
    example_json_output()
    example_batch_analysis()
    example_custom_analysis()
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("\nTo use the interactive analyzer, run:")
    print("  python policy_analyzer.py")
    print("\nTo use in your own code:")
    print("  from policy_analyzer import PolicyAnalyzer")
    print("  analyzer = PolicyAnalyzer()")
    print("  results = analyzer.analyze(your_policy_text, 'Company Name')")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
