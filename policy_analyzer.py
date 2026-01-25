#!/usr/bin/env python3
"""
Policy and Terms Analyzer Assistant

This tool analyzes companies' policies, terms and conditions, and privacy policies
to extract technical information including:
- Websites and domains referenced
- Technologies and platforms mentioned
- Repository and API connections
- Third-party services and integrations
- Bot and automation systems
"""

import re
import json
from typing import Dict, List, Set
from collections import defaultdict


class PolicyAnalyzer:
    """Analyzes policy documents to extract technical and operational information."""
    
    def __init__(self):
        # Common tech keywords and patterns
        self.tech_keywords = {
            'platforms': ['github', 'gitlab', 'bitbucket', 'aws', 'azure', 'gcp', 'google cloud',
                         'heroku', 'netlify', 'vercel', 'cloudflare', 'firebase'],
            'languages': ['python', 'javascript', 'java', 'ruby', 'php', 'go', 'rust', 
                         'typescript', 'c++', 'c#', 'swift', 'kotlin'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'express', 'spring',
                          'rails', 'laravel', 'nextjs', 'nuxt', 'svelte'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                         'dynamodb', 'cassandra', 'sqlite', 'oracle', 'sql server'],
            'services': ['stripe', 'paypal', 'twilio', 'sendgrid', 'mailchimp', 'zendesk',
                        'intercom', 'segment', 'analytics', 'google analytics', 'mixpanel'],
            'ai_ml': ['openai', 'chatgpt', 'gpt', 'claude', 'gemini', 'machine learning',
                     'artificial intelligence', 'neural network', 'deep learning', 'nlp'],
            'bots': ['chatbot', 'bot', 'automated system', 'automation', 'crawler', 'spider']
        }
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from the text."""
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&/=]*'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return list(set(urls))  # Remove duplicates
    
    def extract_domains(self, text: str) -> List[str]:
        """Extract domain names from text."""
        # Pattern for domain names
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, text)
        # Filter out common words that might match
        filtered = [d for d in domains if not d.endswith('.com') or len(d) > 7]
        return list(set(filtered))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))
    
    def detect_technologies(self, text: str) -> Dict[str, List[str]]:
        """Detect mentioned technologies by category."""
        text_lower = text.lower()
        found_tech = defaultdict(list)
        
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_tech[category].append(keyword)
        
        return dict(found_tech)
    
    def extract_api_references(self, text: str) -> List[str]:
        """Extract API-related references."""
        api_pattern = r'\b(?:API|api|REST|GraphQL|webhook|endpoint)s?\b'
        api_mentions = re.findall(api_pattern, text)
        
        # Look for specific API mentions
        api_contexts = []
        for match in re.finditer(api_pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            api_contexts.append(context)
        
        return api_contexts[:10]  # Limit to first 10 mentions
    
    def extract_third_party_services(self, text: str) -> List[str]:
        """Extract third-party service mentions."""
        services = []
        text_lower = text.lower()
        
        # Common service patterns
        service_patterns = [
            r'third[- ]party\s+(?:service|provider|platform)s?:?\s*([^\n.]+)',
            r'we\s+(?:use|utilize|employ)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:for|to)',
            r'powered\s+by\s+([A-Z][a-zA-Z]+)',
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            services.extend(matches)
        
        return list(set(services))[:20]
    
    def detect_data_sharing(self, text: str) -> List[str]:
        """Detect data sharing and integration mentions."""
        sharing_patterns = [
            r'(?:share|transfer|disclose|provide).*?(?:data|information).*?(?:with|to)\s+([^\n.]+)',
            r'(?:integrate|integration|connected|connection)\s+(?:with|to)\s+([^\n.]+)'
        ]
        
        sharing_info = []
        for pattern in sharing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sharing_info.extend(matches)
        
        return list(set(sharing_info))[:15]
    
    def analyze(self, policy_text: str, company_name: str = "Unknown") -> Dict:
        """
        Perform comprehensive analysis of a policy document.
        
        Args:
            policy_text: The full text of the policy document
            company_name: Name of the company (optional)
        
        Returns:
            Dictionary containing all extracted information
        """
        analysis = {
            'company_name': company_name,
            'analysis_date': None,  # Could add timestamp
            'urls_found': self.extract_urls(policy_text),
            'domains_found': self.extract_domains(policy_text),
            'emails_found': self.extract_emails(policy_text),
            'technologies_detected': self.detect_technologies(policy_text),
            'api_references': self.extract_api_references(policy_text),
            'third_party_services': self.extract_third_party_services(policy_text),
            'data_sharing_mentions': self.detect_data_sharing(policy_text),
            'document_length': len(policy_text),
            'word_count': len(policy_text.split())
        }
        
        return analysis
    
    def format_report(self, analysis: Dict) -> str:
        """Format the analysis results as a readable report."""
        report = []
        report.append("=" * 80)
        report.append(f"POLICY ANALYSIS REPORT: {analysis['company_name']}")
        report.append("=" * 80)
        report.append("")
        
        # Document stats
        report.append(f"Document Statistics:")
        report.append(f"  - Length: {analysis['document_length']:,} characters")
        report.append(f"  - Word Count: {analysis['word_count']:,} words")
        report.append("")
        
        # URLs
        if analysis['urls_found']:
            report.append(f"URLs Found ({len(analysis['urls_found'])}):")
            for url in analysis['urls_found'][:10]:
                report.append(f"  - {url}")
            if len(analysis['urls_found']) > 10:
                report.append(f"  ... and {len(analysis['urls_found']) - 10} more")
            report.append("")
        
        # Technologies
        if analysis['technologies_detected']:
            report.append("Technologies Detected:")
            for category, techs in analysis['technologies_detected'].items():
                report.append(f"  {category.title()}:")
                for tech in techs:
                    report.append(f"    - {tech}")
            report.append("")
        
        # Third-party services
        if analysis['third_party_services']:
            report.append(f"Third-Party Services ({len(analysis['third_party_services'])}):")
            for service in analysis['third_party_services'][:10]:
                report.append(f"  - {service}")
            report.append("")
        
        # API references
        if analysis['api_references']:
            report.append(f"API References Found ({len(analysis['api_references'])}):")
            for ref in analysis['api_references'][:5]:
                report.append(f"  - ...{ref}...")
            report.append("")
        
        # Emails
        if analysis['emails_found']:
            report.append(f"Contact Emails ({len(analysis['emails_found'])}):")
            for email in analysis['emails_found']:
                report.append(f"  - {email}")
            report.append("")
        
        # Data sharing
        if analysis['data_sharing_mentions']:
            report.append(f"Data Sharing Mentions ({len(analysis['data_sharing_mentions'])}):")
            for mention in analysis['data_sharing_mentions'][:5]:
                report.append(f"  - {mention[:100]}...")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


def main():
    """Example usage of the PolicyAnalyzer."""
    print("Policy Analyzer Assistant")
    print("=" * 80)
    print()
    
    # Example usage
    print("Usage:")
    print("  1. Paste your policy text when prompted")
    print("  2. Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done")
    print()
    
    company = input("Enter company name (optional): ").strip() or "Unknown Company"
    print("\nPaste the policy text below (Ctrl+D or Ctrl+Z when finished):")
    print("-" * 80)
    
    try:
        # Read multi-line input
        policy_text = []
        while True:
            try:
                line = input()
                policy_text.append(line)
            except EOFError:
                break
        
        policy_text = "\n".join(policy_text)
        
        if not policy_text.strip():
            print("\nNo text provided. Using example...")
            policy_text = """
            Example Privacy Policy
            
            We use GitHub for code hosting and AWS for cloud infrastructure.
            Our chatbot is powered by OpenAI's GPT technology. 
            We integrate with Stripe for payments and SendGrid for emails.
            
            For more information, visit https://example.com or contact privacy@example.com
            
            Third-party services: We use Google Analytics, Mixpanel for analytics,
            and our REST API connects to various services.
            """
        
        # Analyze the policy
        analyzer = PolicyAnalyzer()
        results = analyzer.analyze(policy_text, company)
        
        # Print formatted report
        print("\n" + analyzer.format_report(results))
        
        # Optionally save as JSON
        save = input("\nSave results as JSON? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"{company.replace(' ', '_')}_analysis.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {filename}")
    
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")


if __name__ == "__main__":
    main()
