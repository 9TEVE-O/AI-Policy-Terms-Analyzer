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
import itertools
from datetime import datetime
from typing import Dict, List

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


class PolicyAnalyzer:
    """Analyzes policy documents to extract technical and operational information."""
    
    def __init__(self):
        # Structured extraction modules (one per feature category)
        self._tech_stack_extractor = TechStackExtractor()
        self._website_domain_extractor = WebsiteDomainExtractor()
        self._repository_extractor = RepositoryExtractor()
        self._third_party_service_extractor = ThirdPartyServiceExtractor()
        self._api_integration_extractor = APIIntegrationExtractor()
        self._bot_automation_extractor = BotAutomationExtractor()
        self._data_sharing_extractor = DataSharingExtractor()

        # Common tech keywords and patterns
        self.tech_keywords = {
            'platforms': ['github', 'gitlab', 'bitbucket', 'aws', 'azure',
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
        
        # Google Cloud Platform specific keywords (organized by category)
        self.gcp_services = [
            'google cloud platform', 'gcp', 'google cloud',
            'cloud functions', 'cloud run', 'cloud storage', 'bigquery', 'cloud sql',
            'app engine', 'compute engine', 'kubernetes engine', 'gke', 'cloud vision',
            'cloud speech', 'cloud translation', 'cloud natural language', 'vertex ai',
            'cloud firestore', 'cloud pubsub', 'cloud dataflow', 'cloud composer',
            'cloud build', 'artifact registry', 'cloud cdn', 'cloud dns', 'cloud armor',
            'cloud load balancing', 'cloud iam', 'cloud logging', 'cloud monitoring',
            'cloud trace', 'cloud profiler', 'cloud debugger'
        ]
        
        self.gcp_programs = [
            'google cloud developer', 'google cloud innovator', 'gcp developer',
            'gcp innovator', 'cloud developer program', 'cloud innovator program',
            'google developer program', 'google innovator program'
        ]
        
        self.gcp_cert_patterns = [
            r'google cloud\s+(?:certified\s+)?(?:professional|associate)?\s*(?:cloud\s+)?(?:architect|developer|engineer|data\s+engineer)',
            r'gcp\s+(?:certified\s+)?(?:professional|associate)?\s*(?:architect|developer|engineer)',
            r'google\s+(?:certified\s+)?(?:professional|associate)?\s*cloud'
        ]

        # Pre-compile regex patterns for performance (avoids recompilation on every call)
        self._url_re = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&/=]*',
            re.IGNORECASE)
        self._domain_re = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')
        self._version_re = re.compile(r'^[v]?\d+\.\d+', re.IGNORECASE)
        self._email_re = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        self._api_re = re.compile(r'\b(?:API|api|REST|GraphQL|webhook|endpoint)s?\b', re.IGNORECASE)
        self._service_res = [
            re.compile(r'third[- ]party\s+(?:service|provider|platform)s?:?\s*([^\n.]+)', re.IGNORECASE),
            re.compile(r'we\s+(?:use|utilize|employ)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:for|to)', re.IGNORECASE),
            re.compile(r'powered\s+by\s+([A-Z][a-zA-Z]+)', re.IGNORECASE),
        ]
        self._sharing_res = [
            # re.DOTALL allows matching across newlines, preserving original [\s\S] behavior
            # for multi-line policy clauses
            re.compile(
                r'(?:share|transfer|disclose|provide).{0,200}?(?:data|information).{0,200}?(?:with|to)\s+([^\n.]+)',
                re.IGNORECASE | re.DOTALL),
            re.compile(r'(?:integrate|integration|connected|connection)\s+(?:with|to)\s+([^\n.]+)', re.IGNORECASE),
        ]
        self._gcp_cert_res = [re.compile(p, re.IGNORECASE) for p in self.gcp_cert_patterns]

        # Privacy concern patterns: (compiled_regex, description, severity)
        # Severity levels: 'high', 'medium', 'low'
        self._concern_patterns = [
            # HIGH severity
            (re.compile(r'\bsell\s+(?:your\s+)?(?:personal\s+)?(?:information|data)\b', re.IGNORECASE),
             'May sell your personal information to third parties', 'high'),
            (re.compile(r'\bsold\s+(?:to\s+)?(?:third\s+part|advertiser|partner)', re.IGNORECASE),
             'Data may be sold to third parties or advertisers', 'high'),
            (re.compile(
                r'(?:targeted|interest[\s-]based|behavioral)\s+(?:advertising|ads|marketing)',
                re.IGNORECASE),
             'Uses targeted behavioral advertising', 'high'),
            (re.compile(r'\bprecise\s+(?:geo)?location\b', re.IGNORECASE),
             'Collects your precise location data', 'high'),
            (re.compile(r'cross[\s-]site\s+(?:tracking|advertising)', re.IGNORECASE),
             'Performs cross-site tracking of your activity', 'high'),
            # MEDIUM severity
            (re.compile(
                r'(?:share|disclose|transfer)\s+(?:\w+\s+){0,5}?(?:data|information)\s+'
                r'(?:with|to)\s+(?:our\s+)?(?:affiliates?|subsidiaries|group\s+compan)',
                re.IGNORECASE),
             'Shares your data with corporate affiliates and subsidiaries', 'medium'),
            (re.compile(r'\badvertising\s+partners?\b', re.IGNORECASE),
             'Shares your data with advertising partners', 'medium'),
            (re.compile(
                r'for\s+(?:as\s+long\s+as|the\s+duration\s+of)\s+(?:we\s+)?(?:deem\s+)?necessary'
                r'|\bretain\s+(?:your\s+)?(?:data|information)\s+indefinitely\b',
                re.IGNORECASE),
             'May retain your data for an unspecified or indefinite period', 'medium'),
            (re.compile(
                r'\bbuild(?:ing)?\s+a\s+(?:profile|record)\s+(?:of|about)\s+(?:you|users?)\b',
                re.IGNORECASE),
             'Builds a detailed profile about you', 'medium'),
            (re.compile(r'\bcannot\s+opt[\s-]out\b|\bno\s+opt[\s-]out\b', re.IGNORECASE),
             'Limited or no opt-out options available', 'medium'),
            # LOW severity
            (re.compile(
                r'\b(?:law\s+enforcement|government\s+(?:agenc|official|request)|'
                r'court\s+order|legal\s+process|subpoena)\b',
                re.IGNORECASE),
             'May share your data with government or law enforcement', 'low'),
            (re.compile(
                r'\b(?:merger|acquisition|sale\s+of\s+(?:assets|business|company))\b',
                re.IGNORECASE),
             'Your data may be transferred in a merger or acquisition', 'low'),
            (re.compile(
                r'we\s+(?:may\s+)?(?:change|update|modify|revise)\s+(?:this|our|these)\s+'
                r'(?:policy|terms|agreement|notice)\s+(?:at\s+any\s+time|without\s+notice)',
                re.IGNORECASE),
             'Policy may be changed at any time without notice', 'low'),
        ]

        # Data sharing purpose patterns: (compiled_regex, purpose_description)
        self._purpose_res = [
            (re.compile(r'\b(?:analytics?|telemetry|usage\s+(?:data|statistics))\b', re.IGNORECASE),
             'Usage analytics and telemetry'),
            (re.compile(r'\badvertis(?:ing|ements?|ers?)\b', re.IGNORECASE),
             'Advertising and marketing'),
            (re.compile(
                r'\bpayment\s+(?:processing|providers?|services?)\b'
                r'|\bfinancial\s+(?:transactions?|services?)\b',
                re.IGNORECASE),
             'Payment processing'),
            (re.compile(
                r'\bcustomer\s+(?:support|service|care)\b|\bhelp\s+(?:desk|center)\b',
                re.IGNORECASE),
             'Customer support services'),
            (re.compile(r'\b(?:social\s+(?:media|network|platform))\b', re.IGNORECASE),
             'Social media platforms'),
            (re.compile(
                r'\bcloud\s+(?:storage|hosting|infrastructure|services?)\b'
                r'|\bhosting\s+(?:providers?|services?)\b',
                re.IGNORECASE),
             'Cloud hosting and infrastructure'),
            (re.compile(
                r'\bemail\s+(?:service|marketing|providers?|delivery)\b'
                r'|\bmarketing\s+(?:emails?|campaigns?|communications?)\b',
                re.IGNORECASE),
             'Email services and marketing'),
            (re.compile(
                r'\bfraud\s+(?:detection|prevention)\b|\bsecurity\s+(?:monitoring|services?)\b',
                re.IGNORECASE),
             'Security and fraud prevention'),
            (re.compile(
                r'\bresearch\s+(?:partners?|purposes?|projects?)\b|\bacademic\s+research\b',
                re.IGNORECASE),
             'Research and analytics purposes'),
            (re.compile(
                r'\b(?:artificial\s+intelligence|machine\s+learning)\s+'
                r'(?:processing|training|models?)\b',
                re.IGNORECASE),
             'AI and machine learning processing'),
        ]

    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from the text."""
        urls = self._url_re.findall(text)
        return list(set(urls))  # Remove duplicates
    
    def extract_domains(self, text: str) -> List[str]:
        """Extract domain names from text."""
        # Pattern for domain names - requires alphabetic TLD and minimum length
        domains = self._domain_re.findall(text)
        # Filter out likely version numbers (e.g., v1.2, 3.14)
        filtered_domains = [d for d in domains if not self._version_re.match(d)]
        # Return unique domains
        return list(set(filtered_domains))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        emails = self._email_re.findall(text)
        return list(set(emails))
    
    def detect_technologies(self, text: str) -> Dict[str, List[str]]:
        """Detect mentioned technologies by category."""
        text_lower = text.lower()
        # Preserve stable keyword order while deduplicating matches per category.
        results: Dict[str, List[str]] = {}
        for category, keywords in self.tech_keywords.items():
            seen = set()
            matched: List[str] = []
            for keyword in keywords:
                if keyword in text_lower and keyword not in seen:
                    matched.append(keyword)
                    seen.add(keyword)
            if matched:
                results[category] = matched
        return results
    
    def extract_api_references(self, text: str) -> List[str]:
        """Extract API-related references."""
        # Look for specific API mentions, stopping after the first 10
        api_contexts = []
        for match in itertools.islice(self._api_re.finditer(text), 10):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            api_contexts.append(context)
        
        return api_contexts
    
    def extract_third_party_services(self, text: str) -> List[str]:
        """Extract third-party service mentions."""
        services = []
        
        for pattern in self._service_res:
            matches = pattern.findall(text)
            services.extend(matches)
        
        return list(set(services))[:20]
    
    def detect_data_sharing(self, text: str) -> List[str]:
        """Detect data sharing and integration mentions."""
        sharing_info = []
        for pattern in self._sharing_res:
            matches = pattern.findall(text)
            sharing_info.extend(matches)
        
        return list(set(sharing_info))[:15]
    
    def detect_privacy_concerns(self, text: str) -> Dict[str, List[str]]:
        """
        Detect privacy concerns and red flags categorized by severity.

        Scans the policy text for patterns indicating potential privacy issues
        and returns them grouped by severity level.

        Args:
            text: The policy text to analyze.

        Returns:
            Dictionary with 'high', 'medium', 'low' severity keys, each
            mapping to a list of concern descriptions found in the text.
            Only non-empty severity categories are included.
        """
        concerns: Dict[str, List[str]] = {}
        for pattern, description, severity in self._concern_patterns:
            if pattern.search(text):
                bucket = concerns.setdefault(severity, [])
                if description not in bucket:
                    bucket.append(description)
        return concerns

    def detect_data_destinations(self, text: str) -> Dict[str, List[str]]:
        """
        Extract specific data destinations — where user data is shared or sent.

        Args:
            text: The policy text to analyze.

        Returns:
            Dictionary with:
              'recipients' — named entities/phrases that receive user data (up to 15).
              'purposes'   — functional categories describing why data is shared.
        """
        seen: set = set()
        recipients: List[str] = []
        for pattern in self._sharing_res:
            for m in pattern.finditer(text):
                snippet = m.group(1).strip() if m.lastindex else ""
                # Filter out too-short noise and overly-long run-on excerpts
                if 5 < len(snippet) < 80 and snippet not in seen:
                    seen.add(snippet)
                    recipients.append(snippet)

        purposes = [desc for p_re, desc in self._purpose_res if p_re.search(text)]

        return {
            'recipients': recipients[:15],
            'purposes': purposes,
        }

    # ------------------------------------------------------------------
    # Structured extraction methods (delegating to extraction_modules)
    # ------------------------------------------------------------------

    def extract_tech_stack(self, text: str) -> Dict:
        """
        Extract technologies, frameworks, and platforms mentioned in *text*.

        Delegates to :class:`extraction_modules.TechStackExtractor`.

        Returns:
            Structured dict with ``by_category`` and ``all_technologies`` keys.
        """
        return self._tech_stack_extractor.extract(text)

    def extract_websites_domains(self, text: str) -> Dict:
        """
        Extract all URLs and domain names referenced in *text*.

        Delegates to :class:`extraction_modules.WebsiteDomainExtractor`.

        Returns:
            Structured dict with ``urls`` and ``domains`` keys.
        """
        return self._website_domain_extractor.extract(text)

    def extract_repositories(self, text: str) -> Dict:
        """
        Detect VCS platform mentions and repository URLs in *text*.

        Delegates to :class:`extraction_modules.RepositoryExtractor`.

        Returns:
            Structured dict with ``vcs_platforms_mentioned``,
            ``repository_urls``, and ``context_snippets`` keys.
        """
        return self._repository_extractor.extract(text)

    def extract_third_party_services_structured(self, text: str) -> Dict:
        """
        Identify named third-party services categorised by function
        (payments, analytics, email, etc.).

        Delegates to :class:`extraction_modules.ThirdPartyServiceExtractor`.

        Returns:
            Structured dict with ``by_category`` and ``all_services`` keys.
        """
        return self._third_party_service_extractor.extract(text)

    def extract_apis_integrations(self, text: str) -> Dict:
        """
        Detect API protocols, endpoint patterns, webhooks, and named
        third-party integrations mentioned in *text*.

        Delegates to :class:`extraction_modules.APIIntegrationExtractor`.

        Returns:
            Structured dict with ``protocols``, ``endpoint_patterns``,
            ``named_integrations``, and ``context_snippets`` keys.
        """
        return self._api_integration_extractor.extract(text)

    def extract_bots_automation(self, text: str) -> Dict:
        """
        Extract references to chatbots, crawlers, scrapers, and automated
        systems from *text*.

        Delegates to :class:`extraction_modules.BotAutomationExtractor`.

        Returns:
            Structured dict with ``by_type``, ``all_mentions``, and
            ``prohibition_snippets`` keys.
        """
        return self._bot_automation_extractor.extract(text)

    def extract_data_sharing_structured(self, text: str) -> Dict:
        """
        Identify what personal data is shared, with whom, and under
        what conditions.

        Delegates to :class:`extraction_modules.DataSharingExtractor`.

        Returns:
            Structured dict with ``data_types_mentioned``, ``recipients``,
            ``conditions``, and ``purposes`` keys.
        """
        return self._data_sharing_extractor.extract(text)

    def generate_user_summary(self, analysis: Dict) -> str:
        """
        Generate a user-friendly privacy summary from the analysis.

        Presents the key findings in plain English, focusing on where user
        data goes and what to be cautious about.

        Args:
            analysis: The output from analyze().

        Returns:
            A formatted, easy-to-read summary string.
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"PRIVACY SUMMARY: {analysis['company_name']}")
        lines.append("=" * 80)
        lines.append("")

        # WHERE YOUR DATA GOES
        lines.append("WHERE YOUR DATA GOES:")
        lines.append("-" * 40)
        destinations = analysis.get('data_destinations', {})
        purposes = destinations.get('purposes', [])
        recipients = destinations.get('recipients', [])

        if purposes:
            for purpose in purposes:
                lines.append(f"  * {purpose}")
        if recipients:
            # Show up to 8 recipients to keep summary concise
            for r in recipients[:8]:
                lines.append(f"  * {r}")
        if not purposes and not recipients:
            sharing = analysis.get('data_sharing_mentions', [])
            if sharing:
                # Limit to 5 mentions for readability; truncate long mentions to fit
                for mention in sharing[:5]:
                    lines.append(f"  * {mention[:80]}")
            else:
                lines.append("  No specific data sharing destinations identified.")
        lines.append("")

        # WHAT TO BE WARY OF
        concerns = analysis.get('privacy_concerns', {})
        lines.append("WHAT TO BE WARY OF:")
        lines.append("-" * 40)
        if concerns:
            severity_labels = {
                'high': '[HIGH CONCERN]',
                'medium': '[MEDIUM CONCERN]',
                'low': '[LOW CONCERN]',
            }
            for severity in ['high', 'medium', 'low']:
                for concern in concerns.get(severity, []):
                    lines.append(f"  {severity_labels[severity]} {concern}")
        else:
            lines.append("  No major privacy concerns detected in this document.")
        lines.append("")

        # TECHNOLOGIES PROCESSING YOUR DATA
        techs = analysis.get('technologies_detected', {})
        notable: List[str] = []
        for cat in ['services', 'ai_ml', 'platforms']:
            notable.extend(techs.get(cat, []))

        if notable:
            lines.append("TECHNOLOGIES PROCESSING YOUR DATA:")
            lines.append("-" * 40)
            for tech in notable[:10]:
                lines.append(f"  * {tech}")
            lines.append("")

        lines.append(f"Document analyzed: {analysis['word_count']:,} words")
        lines.append("=" * 80)
        return "\n".join(lines)

    def extract_google_cloud_info(self, text: str) -> Dict[str, List[str]]:
        """
        Extract detailed Google Cloud information including services, programs, and certifications.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with categorized Google Cloud information
        """
        text_lower = text.lower()
        certifications = [
            m for cert_re in self._gcp_cert_res for m in cert_re.findall(text)
        ]
        return {
            # gcp_services and gcp_programs are defined without duplicates in __init__,
            # so no set() deduplication is needed here.
            'services': [s for s in self.gcp_services if s in text_lower],
            'programs': [p for p in self.gcp_programs if p in text_lower],
            'certifications': list(set(certifications))
        }
    
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
            'analysis_date': datetime.now().isoformat(),
            # Legacy / existing fields
            'urls_found': self.extract_urls(policy_text),
            'domains_found': self.extract_domains(policy_text),
            'emails_found': self.extract_emails(policy_text),
            'technologies_detected': self.detect_technologies(policy_text),
            'google_cloud_info': self.extract_google_cloud_info(policy_text),
            'api_references': self.extract_api_references(policy_text),
            'third_party_services': self.extract_third_party_services(policy_text),
            'data_sharing_mentions': self.detect_data_sharing(policy_text),
            'privacy_concerns': self.detect_privacy_concerns(policy_text),
            'data_destinations': self.detect_data_destinations(policy_text),
            # Structured extraction modules (7 feature categories)
            'tech_stack': self.extract_tech_stack(policy_text),
            'websites_domains': self.extract_websites_domains(policy_text),
            'repositories': self.extract_repositories(policy_text),
            'third_party_services_structured': self.extract_third_party_services_structured(policy_text),
            'apis_integrations': self.extract_apis_integrations(policy_text),
            'bots_automation': self.extract_bots_automation(policy_text),
            'data_sharing_structured': self.extract_data_sharing_structured(policy_text),
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

        # Privacy concerns (shown prominently before other details)
        concerns = analysis.get('privacy_concerns', {})
        if concerns:
            total = sum(len(v) for v in concerns.values())
            report.append(f"Privacy Concerns Detected ({total}):")
            severity_labels = {'high': '[HIGH]', 'medium': '[MEDIUM]', 'low': '[LOW]'}
            for severity in ['high', 'medium', 'low']:
                for concern in concerns.get(severity, []):
                    report.append(f"  {severity_labels[severity]} {concern}")
            report.append("")

        # Data destinations
        destinations = analysis.get('data_destinations', {})
        if destinations and (destinations.get('purposes') or destinations.get('recipients')):
            report.append("Data Destinations:")
            for purpose in destinations.get('purposes', []):
                report.append(f"  - {purpose}")
            for recipient in destinations.get('recipients', [])[:5]:
                report.append(f"  - {recipient}")
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
        
        # Google Cloud specific information
        if analysis.get('google_cloud_info'):
            gcp_info = analysis['google_cloud_info']
            has_gcp_content = any(gcp_info.values())
            
            if has_gcp_content:
                report.append("Google Cloud Platform Information:")
                
                if gcp_info.get('services'):
                    report.append(f"  GCP Services ({len(gcp_info['services'])}):")
                    for service in gcp_info['services']:
                        report.append(f"    - {service}")
                
                if gcp_info.get('programs'):
                    report.append(f"  GCP Programs ({len(gcp_info['programs'])}):")
                    for program in gcp_info['programs']:
                        report.append(f"    - {program}")
                
                if gcp_info.get('certifications'):
                    report.append(f"  GCP Certifications ({len(gcp_info['certifications'])}):")
                    for cert in gcp_info['certifications']:
                        report.append(f"    - {cert}")
                
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

        # ---------------------------------------------------------------
        # Structured extraction sections (7 feature categories)
        # ---------------------------------------------------------------
        report.append("─" * 80)
        report.append("STRUCTURED EXTRACTION RESULTS")
        report.append("─" * 80)
        report.append("")

        # 1. Tech Stack
        tech_stack = analysis.get('tech_stack', {})
        by_cat = tech_stack.get('by_category', {})
        if by_cat:
            total = sum(len(v) for v in by_cat.values())
            report.append(f"Tech Stack ({total} items):")
            for cat, items in by_cat.items():
                report.append(f"  {cat.replace('_', ' ').title()}: {', '.join(items)}")
            report.append("")

        # 2. Websites & Domains
        wd = analysis.get('websites_domains', {})
        if wd.get('urls') or wd.get('domains'):
            report.append("Websites & Domains:")
            if wd.get('urls'):
                report.append(f"  URLs ({len(wd['urls'])}):")
                for u in wd['urls'][:8]:
                    report.append(f"    - {u}")
                if len(wd['urls']) > 8:
                    report.append(f"    ... and {len(wd['urls']) - 8} more")
            if wd.get('domains'):
                report.append(f"  Domains ({len(wd['domains'])}): {', '.join(wd['domains'][:12])}")
            report.append("")

        # 3. Repositories
        repos = analysis.get('repositories', {})
        if repos.get('vcs_platforms_mentioned') or repos.get('repository_urls'):
            report.append("Repositories:")
            if repos.get('vcs_platforms_mentioned'):
                report.append(f"  VCS Platforms: {', '.join(repos['vcs_platforms_mentioned'])}")
            if repos.get('repository_urls'):
                report.append(f"  Repository URLs ({len(repos['repository_urls'])}):")
                for url in repos['repository_urls'][:5]:
                    report.append(f"    - {url}")
            if repos.get('context_snippets'):
                report.append(f"  Context snippets: {len(repos['context_snippets'])} found")
            report.append("")

        # 4. Third-Party Services (structured)
        tps = analysis.get('third_party_services_structured', {})
        tps_by_cat = tps.get('by_category', {})
        if tps_by_cat:
            total = sum(len(v) for v in tps_by_cat.values())
            report.append(f"Third-Party Services ({total}):")
            for cat, svcs in tps_by_cat.items():
                report.append(f"  {cat.replace('_', ' ').title()}: {', '.join(svcs)}")
            report.append("")

        # 5. APIs & Integrations
        apis = analysis.get('apis_integrations', {})
        if apis.get('protocols') or apis.get('named_integrations') or apis.get('endpoint_patterns'):
            report.append("APIs & Integrations:")
            if apis.get('protocols'):
                for proto, kws in apis['protocols'].items():
                    report.append(f"  {proto.upper()}: {', '.join(kws[:4])}")
            if apis.get('named_integrations'):
                report.append(f"  Named Integrations: {', '.join(apis['named_integrations'][:8])}")
            if apis.get('endpoint_patterns'):
                report.append(f"  Endpoint Patterns ({len(apis['endpoint_patterns'])}):")
                for ep in apis['endpoint_patterns'][:5]:
                    report.append(f"    - {ep}")
            report.append("")

        # 6. Bots & Automation
        bots = analysis.get('bots_automation', {})
        bots_by_type = bots.get('by_type', {})
        if bots_by_type:
            total = sum(len(v) for v in bots_by_type.values())
            report.append(f"Bots & Automation ({total} mentions):")
            for bot_type, items in bots_by_type.items():
                report.append(f"  {bot_type.replace('_', ' ').title()}: {', '.join(items)}")
            if bots.get('prohibition_snippets'):
                report.append(f"  Prohibition clauses: {len(bots['prohibition_snippets'])} found")
            report.append("")

        # 7. Data Sharing (structured)
        ds = analysis.get('data_sharing_structured', {})
        if ds.get('data_types_mentioned') or ds.get('recipients') or ds.get('purposes'):
            report.append("Data Sharing:")
            if ds.get('data_types_mentioned'):
                for cat, types in ds['data_types_mentioned'].items():
                    report.append(f"  {cat.replace('_', ' ').title()}: {', '.join(types[:5])}")
            if ds.get('recipients'):
                report.append(f"  Recipients ({len(ds['recipients'])}):")
                for r in ds['recipients'][:5]:
                    report.append(f"    - {r[:80]}")
            if ds.get('purposes'):
                report.append(f"  Purposes: {', '.join(ds['purposes'])}")
            if ds.get('conditions'):
                report.append(f"  Conditions: {len(ds['conditions'])} clause(s) found")
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
            # Sanitize filename - remove unsafe characters
            safe_name = re.sub(r'[^\w\s-]', '', company).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            filename = f"{safe_name}_analysis.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Results saved to {filename}")
            except (PermissionError, OSError, IOError) as e:
                print(f"Could not save results to '{filename}': {e}")
    
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")


if __name__ == "__main__":
    main()
