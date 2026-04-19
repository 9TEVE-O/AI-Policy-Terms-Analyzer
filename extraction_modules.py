#!/usr/bin/env python3
"""
Extraction Modules for AI-Policy-Terms-Analyzer

Provides seven structured extraction modules, each targeting a distinct
category of technical information found in policy and terms documents:

  1. TechStackExtractor          — programming languages, frameworks, platforms
  2. WebsiteDomainExtractor      — URLs and domain names
  3. RepositoryExtractor         — VCS hosts and repository links
  4. ThirdPartyServiceExtractor  — payment, analytics, email, and other services
  5. APIIntegrationExtractor     — REST/GraphQL endpoints, webhooks, integrations
  6. BotAutomationExtractor      — chatbots, crawlers, scrapers, automated systems
  7. DataSharingExtractor        — what data is shared, with whom, and why

Each extractor exposes an ``extract(text)`` method that returns a structured
``dict``.  The top-level helper ``run_all_extractors(text, company_name)``
runs all seven and merges their output into a single dict suitable for
JSON serialisation.
"""

import re
from datetime import datetime
from typing import Dict, List

# ---------------------------------------------------------------------------
# 1. TechStackExtractor
# ---------------------------------------------------------------------------

class TechStackExtractor:
    """
    Identifies technologies, frameworks, and platforms mentioned in a document.

    Keyword lists are grouped into sub-categories so callers receive a
    categorised result rather than a flat list.
    """

    _KEYWORDS: Dict[str, List[str]] = {
        'cloud_platforms': [
            'aws', 'amazon web services', 'azure', 'microsoft azure',
            'google cloud', 'gcp', 'google cloud platform', 'heroku',
            'digitalocean', 'linode', 'vultr', 'cloudflare', 'fastly',
            'netlify', 'vercel', 'fly.io', 'render', 'railway',
        ],
        'languages': [
            'python', 'javascript', 'typescript', 'java', 'ruby', 'php',
            'go', 'golang', 'rust', 'c++', 'c#', 'swift', 'kotlin',
            'scala', 'elixir', 'haskell', 'r language', 'perl', 'lua',
        ],
        'frameworks': [
            'react', 'angular', 'vue', 'svelte', 'next.js', 'nextjs',
            'nuxt', 'remix', 'gatsby', 'django', 'flask', 'fastapi',
            'express', 'spring', 'rails', 'laravel', 'symfony',
            'asp.net', 'dotnet', '.net', 'gin', 'echo', 'fiber',
        ],
        'databases': [
            'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
            'elasticsearch', 'opensearch', 'dynamodb', 'cassandra',
            'sqlite', 'oracle', 'sql server', 'mssql', 'mariadb',
            'cockroachdb', 'supabase', 'firebase', 'neo4j', 'influxdb',
        ],
        'infrastructure': [
            'kubernetes', 'k8s', 'docker', 'terraform', 'ansible',
            'jenkins', 'github actions', 'circleci', 'travis ci',
            'gitlab ci', 'argocd', 'helm', 'istio', 'envoy', 'nginx',
            'apache', 'caddy', 'haproxy', 'prometheus', 'grafana',
            'datadog', 'new relic', 'splunk', 'elk stack',
        ],
        'ai_ml': [
            'openai', 'chatgpt', 'gpt-4', 'gpt-3', 'claude', 'gemini',
            'llama', 'mistral', 'hugging face', 'tensorflow', 'pytorch',
            'scikit-learn', 'keras', 'spark ml', 'vertex ai',
            'sagemaker', 'azure ml', 'machine learning', 'deep learning',
            'natural language processing', 'nlp', 'neural network',
            'large language model', 'llm', 'generative ai',
        ],
        'messaging_queues': [
            'kafka', 'rabbitmq', 'sqs', 'sns', 'pubsub', 'nats',
            'zeromq', 'celery', 'sidekiq', 'resque', 'bull',
        ],
        'cdn_storage': [
            's3', 'cloudfront', 'azure blob', 'google cloud storage',
            'gcs', 'backblaze', 'cloudinary', 'imgix', 'bunny.net',
        ],
    }

    def __init__(self) -> None:
        # Build a flattened lookup: lowercase keyword → (category, original_keyword)
        self._lookup: Dict[str, tuple] = {}
        for category, keywords in self._KEYWORDS.items():
            for kw in keywords:
                self._lookup[kw.lower()] = (category, kw)

    def extract(self, text: str) -> Dict[str, object]:
        """
        Extract technology mentions from *text*.

        Returns:
            {
              "by_category": {
                "cloud_platforms": ["aws", ...],
                "languages":       ["python", ...],
                ...
              },
              "all_technologies": ["aws", "python", ...]   # flat, deduped
            }
        """
        text_lower = text.lower()
        by_category: Dict[str, List[str]] = {}
        seen: set = set()

        # Iterate in stable definition order
        for category, keywords in self._KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower and kw.lower() not in seen:
                    by_category.setdefault(category, []).append(kw)
                    seen.add(kw.lower())

        return {
            'by_category': by_category,
            'all_technologies': [kw for kws in by_category.values() for kw in kws],
        }


# ---------------------------------------------------------------------------
# 2. WebsiteDomainExtractor
# ---------------------------------------------------------------------------

class WebsiteDomainExtractor:
    """
    Extracts URLs and domain names from a policy document.

    URLs are processed to also produce a deduplicated list of top-level
    domains so callers can quickly see which sites are referenced.
    """

    def __init__(self) -> None:
        self._url_re = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}'
            r'\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*',
            re.IGNORECASE,
        )
        # Bare domain pattern; deliberately conservative to reduce false positives
        self._domain_re = re.compile(
            r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'
            r'+(?:com|org|net|io|co|ai|dev|app|gov|edu|uk|de|fr|au|ca|jp)\b',
            re.IGNORECASE,
        )
        self._version_re = re.compile(r'^[v]?\d+\.\d+', re.IGNORECASE)

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "urls":    ["https://example.com/tos", ...],
              "domains": ["example.com", "stripe.com", ...]
            }
        """
        urls = list(dict.fromkeys(self._url_re.findall(text)))  # preserve first-seen order

        # Collect bare domains found in text, then add domains extracted from URLs
        bare = [
            d for d in self._domain_re.findall(text)
            if not self._version_re.match(d)
        ]
        # Extract host from each URL
        url_hosts: List[str] = []
        host_re = re.compile(r'https?://(?:www\.)?([^/?\s]+)', re.IGNORECASE)
        for url in urls:
            m = host_re.match(url)
            if m:
                url_hosts.append(m.group(1).lower())

        all_domains = list(dict.fromkeys(
            [d.lower() for d in bare] + url_hosts
        ))

        return {
            'urls': urls[:50],
            'domains': all_domains[:50],
        }


# ---------------------------------------------------------------------------
# 3. RepositoryExtractor
# ---------------------------------------------------------------------------

class RepositoryExtractor:
    """
    Detects mentions of version-control platforms and extracts repository URLs.
    """

    _VCS_HOSTS = [
        'github', 'github.com',
        'gitlab', 'gitlab.com',
        'bitbucket', 'bitbucket.org',
        'sourcehub', 'codeberg', 'codeberg.org',
        'gitea', 'sr.ht', 'azure devops', 'azure repos',
    ]

    def __init__(self) -> None:
        # Explicit repo URL patterns
        self._repo_url_re = re.compile(
            r'https?://(?:www\.)?(?:github|gitlab|bitbucket|codeberg)'
            r'\.[a-z]{2,}/[^\s"\'<>)]+',
            re.IGNORECASE,
        )
        # Contextual snippet patterns for implicit repo mentions
        self._context_patterns = [
            re.compile(
                r'(?:source\s+code|open[\s-]source|repository|repo)\s+'
                r'(?:is\s+)?(?:available|hosted|found)\s+(?:at|on|in)\s+([^\n.]+)',
                re.IGNORECASE,
            ),
            re.compile(
                r'(?:fork|clone|pull\s+request|commit|branch|release)\s+'
                r'(?:from|on|in|to)\s+([^\n.]+)',
                re.IGNORECASE,
            ),
        ]

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "vcs_platforms_mentioned": ["github", "gitlab"],
              "repository_urls":         ["https://github.com/org/repo"],
              "context_snippets":        ["source code available on GitHub..."]
            }
        """
        text_lower = text.lower()
        platforms = [h for h in self._VCS_HOSTS if h in text_lower]
        # Deduplicate while preserving order
        seen_p: set = set()
        deduped_platforms: List[str] = []
        for p in platforms:
            if p not in seen_p:
                deduped_platforms.append(p)
                seen_p.add(p)

        repo_urls = list(dict.fromkeys(self._repo_url_re.findall(text)))

        snippets: List[str] = []
        seen_s: set = set()
        for pattern in self._context_patterns:
            for m in pattern.finditer(text):
                snippet = m.group(0).strip()[:200]
                if snippet not in seen_s:
                    snippets.append(snippet)
                    seen_s.add(snippet)

        return {
            'vcs_platforms_mentioned': deduped_platforms,
            'repository_urls': repo_urls[:20],
            'context_snippets': snippets[:10],
        }


# ---------------------------------------------------------------------------
# 4. ThirdPartyServiceExtractor
# ---------------------------------------------------------------------------

class ThirdPartyServiceExtractor:
    """
    Identifies named third-party services categorised by function.
    """

    _SERVICES: Dict[str, List[str]] = {
        'payment_processors': [
            'stripe', 'paypal', 'braintree', 'square', 'adyen', 'klarna',
            'afterpay', 'zip pay', 'worldpay', 'checkout.com', 'mollie',
            'razorpay', 'paytm', 'apple pay', 'google pay', 'samsung pay',
        ],
        'analytics': [
            'google analytics', 'ga4', 'mixpanel', 'amplitude', 'heap',
            'segment', 'hotjar', 'fullstory', 'mouseflow', 'clarity',
            'chartbeat', 'comscore', 'nielsen', 'quantserve', 'piwik',
            'matomo', 'posthog', 'plausible', 'fathom', 'datadog rum',
        ],
        'email_marketing': [
            'sendgrid', 'mailchimp', 'mailgun', 'ses', 'amazon ses',
            'postmark', 'sparkpost', 'brevo', 'sendinblue', 'klaviyo',
            'constant contact', 'campaign monitor', 'activecampaign',
            'hubspot', 'marketo', 'pardot', 'iterable', 'sailthru',
        ],
        'customer_support': [
            'zendesk', 'intercom', 'freshdesk', 'helpscout', 'crisp',
            'drift', 'livechat', 'olark', 'tawk.to', 'uservoice',
            'salesforce service cloud', 'kustomer', 'front',
        ],
        'advertising': [
            'google ads', 'google adwords', 'doubleclick', 'facebook ads',
            'meta ads', 'twitter ads', 'linkedin ads', 'snapchat ads',
            'tiktok ads', 'criteo', 'the trade desk', 'appnexus',
            'taboola', 'outbrain', 'mediamath',
        ],
        'social_login_auth': [
            'auth0', 'okta', 'firebase auth', 'cognito', 'onelogin',
            'ping identity', 'google sign-in', 'sign in with apple',
            'facebook login', 'twitter login', 'github oauth',
        ],
        'cdn_performance': [
            'cloudflare', 'akamai', 'fastly', 'cloudfront', 'bunny.net',
            'stackpath', 'sucuri', 'imperva',
        ],
        'monitoring_logging': [
            'sentry', 'rollbar', 'bugsnag', 'datadog', 'new relic',
            'dynatrace', 'elastic apm', 'grafana', 'prometheus',
            'logdna', 'papertrail', 'loggly', 'sumo logic',
        ],
        'cloud_storage': [
            'aws s3', 'google cloud storage', 'azure blob', 'dropbox',
            'box', 'backblaze b2', 'wasabi', 'cloudinary', 'imgix',
        ],
    }

    def __init__(self) -> None:
        # Pre-compile case-insensitive patterns for each service name
        self._patterns: Dict[str, List[re.Pattern]] = {}
        for category, services in self._SERVICES.items():
            self._patterns[category] = [
                re.compile(r'\b' + re.escape(s) + r'\b', re.IGNORECASE)
                for s in services
            ]

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "by_category": {
                "payment_processors": ["Stripe", "PayPal"],
                "analytics":          ["Google Analytics"],
                ...
              },
              "all_services": ["Stripe", "PayPal", "Google Analytics", ...]
            }
        """
        by_category: Dict[str, List[str]] = {}
        seen: set = set()

        for category, patterns in self._patterns.items():
            for i, pattern in enumerate(patterns):
                service_name = self._SERVICES[category][i]
                if pattern.search(text) and service_name.lower() not in seen:
                    by_category.setdefault(category, []).append(service_name)
                    seen.add(service_name.lower())

        return {
            'by_category': by_category,
            'all_services': [s for svcs in by_category.values() for s in svcs],
        }


# ---------------------------------------------------------------------------
# 5. APIIntegrationExtractor
# ---------------------------------------------------------------------------

class APIIntegrationExtractor:
    """
    Detects API protocols, endpoint patterns, webhooks, and named integrations.
    """

    _PROTOCOL_KEYWORDS: Dict[str, List[str]] = {
        'rest': ['rest api', 'restful', 'rest endpoint', 'http api', 'http endpoint'],
        'graphql': ['graphql', 'graph ql', 'graphql endpoint', 'graphql api'],
        'grpc': ['grpc', 'gRPC', 'protocol buffers', 'protobuf'],
        'websocket': ['websocket', 'web socket', 'socket.io', 'ws://', 'wss://'],
        'webhook': ['webhook', 'web hook', 'outbound webhook', 'inbound webhook',
                    'callback url', 'event notification'],
        'sdk': ['sdk', 'client library', 'client sdk', 'mobile sdk', 'npm package',
                'pip package', 'composer package'],
        'oauth': ['oauth', 'oauth2', 'oauth 2.0', 'openid connect', 'oidc',
                  'bearer token', 'access token', 'refresh token', 'api key'],
    }

    _NAMED_INTEGRATIONS = [
        'zapier', 'make', 'integromat', 'n8n', 'workato', 'mulesoft',
        'boomi', 'tray.io', 'pipedream', 'ifttt', 'microsoft power automate',
        'salesforce', 'hubspot', 'shopify', 'woocommerce', 'magento',
        'slack api', 'discord api', 'telegram bot api', 'twilio api',
        'google maps api', 'mapbox api', 'openai api', 'anthropic api',
    ]

    _ENDPOINT_RE = re.compile(
        r'(?:api\.|/api/|/v\d+/|/graphql|/webhook|/callback)'
        r'[a-zA-Z0-9/_-]{2,60}',
        re.IGNORECASE,
    )
    _CONTEXT_RE = re.compile(
        r'(?:api|endpoint|webhook|integration)\s+[^\n.]{0,120}',
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self._named_patterns = [
            re.compile(r'\b' + re.escape(n) + r'\b', re.IGNORECASE)
            for n in self._NAMED_INTEGRATIONS
        ]

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "protocols": {
                "rest":      ["rest api", ...],
                "graphql":   ["graphql"],
                ...
              },
              "endpoint_patterns": ["/api/v1/users", ...],
              "named_integrations": ["Zapier", "Slack API", ...],
              "context_snippets":  ["our REST API allows ...", ...]
            }
        """
        text_lower = text.lower()

        # Protocol/paradigm detection
        protocols: Dict[str, List[str]] = {}
        for proto, keywords in self._PROTOCOL_KEYWORDS.items():
            matched = [kw for kw in keywords if kw.lower() in text_lower]
            if matched:
                protocols[proto] = matched

        # Endpoint path patterns
        endpoints = list(dict.fromkeys(self._ENDPOINT_RE.findall(text)))[:20]

        # Named third-party integrations
        named: List[str] = []
        seen: set = set()
        for i, pattern in enumerate(self._named_patterns):
            svc = self._NAMED_INTEGRATIONS[i]
            if pattern.search(text) and svc.lower() not in seen:
                named.append(svc)
                seen.add(svc.lower())

        # Short context snippets
        snippets: List[str] = []
        seen_s: set = set()
        for m in self._CONTEXT_RE.finditer(text):
            s = m.group(0).strip()[:150]
            if s not in seen_s:
                snippets.append(s)
                seen_s.add(s)
            if len(snippets) >= 10:
                break

        return {
            'protocols': protocols,
            'endpoint_patterns': endpoints,
            'named_integrations': named,
            'context_snippets': snippets,
        }


# ---------------------------------------------------------------------------
# 6. BotAutomationExtractor
# ---------------------------------------------------------------------------

class BotAutomationExtractor:
    """
    Extracts references to bots, automated systems, crawlers, and scrapers.
    """

    _BOT_TYPES: Dict[str, List[str]] = {
        'chatbots': [
            'chatbot', 'chat bot', 'virtual assistant', 'conversational ai',
            'ai assistant', 'ai agent', 'customer bot', 'support bot',
            'voice assistant', 'ivr',
        ],
        'crawlers_scrapers': [
            'web crawler', 'spider', 'scraper', 'web scraper',
            'data scraper', 'scraping', 'crawling', 'screen scraping',
            'content scraping', 'automated browsing',
        ],
        'automated_systems': [
            'automated system', 'automation', 'robotic process automation', 'rpa',
            'scheduled task', 'cron job', 'background job', 'batch processing',
            'automated testing', 'ci/cd', 'continuous integration',
            'headless browser', 'selenium', 'puppeteer', 'playwright',
        ],
        'ai_agents': [
            'ai agent', 'autonomous agent', 'llm agent', 'ai workflow',
            'agentic', 'multi-agent', 'tool use', 'function calling',
        ],
        'email_bots': [
            'email automation', 'auto-responder', 'autoresponder',
            'drip campaign', 'automated email', 'triggered email',
        ],
    }

    _PROHIBITION_PATTERNS = [
        re.compile(
            r'(?:prohibit|forbid|not\s+(?:allowed|permitted))\s+[^\n.]{0,80}'
            r'(?:bot|automat|crawl|scrape|spider)',
            re.IGNORECASE,
        ),
        re.compile(
            r'(?:bot|automat|crawl|scrape|spider)[^\n.]{0,80}'
            r'(?:prohibit|forbid|not\s+(?:allowed|permitted))',
            re.IGNORECASE,
        ),
    ]

    def __init__(self) -> None:
        self._keyword_map: Dict[str, List[str]] = self._BOT_TYPES

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "by_type": {
                "chatbots":          ["chatbot", "virtual assistant"],
                "crawlers_scrapers": ["web scraper"],
                ...
              },
              "all_mentions":    ["chatbot", "web scraper", ...],
              "prohibition_snippets": ["automated scraping is prohibited ..."]
            }
        """
        text_lower = text.lower()
        by_type: Dict[str, List[str]] = {}
        seen: set = set()

        for bot_type, keywords in self._keyword_map.items():
            for kw in keywords:
                if kw.lower() in text_lower and kw.lower() not in seen:
                    by_type.setdefault(bot_type, []).append(kw)
                    seen.add(kw.lower())

        prohibitions: List[str] = []
        seen_p: set = set()
        for pattern in self._PROHIBITION_PATTERNS:
            for m in pattern.finditer(text):
                snippet = m.group(0).strip()[:200]
                if snippet not in seen_p:
                    prohibitions.append(snippet)
                    seen_p.add(snippet)

        return {
            'by_type': by_type,
            'all_mentions': [kw for kws in by_type.values() for kw in kws],
            'prohibition_snippets': prohibitions[:10],
        }


# ---------------------------------------------------------------------------
# 7. DataSharingExtractor
# ---------------------------------------------------------------------------

class DataSharingExtractor:
    """
    Identifies what personal/user data is shared, with whom, and under what
    conditions — providing a structured view of data flows described in the
    document.
    """

    _DATA_TYPES: Dict[str, List[str]] = {
        'personal_identifiers': [
            'name', 'email address', 'phone number', 'date of birth',
            'address', 'postal code', 'social security number', 'ssn',
            'passport number', 'government id', 'ip address',
        ],
        'financial': [
            'payment information', 'credit card', 'bank account',
            'billing information', 'financial data', 'transaction history',
            'purchase history',
        ],
        'behavioural': [
            'browsing history', 'search history', 'click data',
            'usage data', 'interaction data', 'activity data',
            'engagement data', 'behavioural data',
        ],
        'location': [
            'location data', 'geolocation', 'gps data', 'precise location',
            'approximate location', 'location history',
        ],
        'biometric': [
            'biometric data', 'facial recognition', 'fingerprint',
            'voice recognition', 'retina scan', 'biometric identifier',
        ],
        'health': [
            'health data', 'medical information', 'fitness data',
            'mental health', 'health condition', 'medical record',
        ],
        'device': [
            'device identifier', 'device id', 'advertising id',
            'idfa', 'android id', 'device fingerprint', 'hardware id',
            'mac address', 'imei',
        ],
    }

    _RECIPIENT_PATTERNS = [
        re.compile(
            r'(?:share|disclose|transfer|provide|sell|send)\s+'
            r'(?:your\s+)?(?:personal\s+)?(?:data|information)\s+'
            r'(?:with|to)\s+([A-Z][^\n.]{3,80})',
            re.IGNORECASE,
        ),
        re.compile(
            r'third[\s-]party\s+(?:providers?|partners?|services?|vendors?):\s*([^\n.]+)',
            re.IGNORECASE,
        ),
        re.compile(
            r'(?:our\s+)?(?:partners?|affiliates?|subsidiaries|contractors?|processors?)'
            r'\s+(?:include|such\s+as|like)\s+([^\n.]+)',
            re.IGNORECASE,
        ),
    ]

    _CONDITION_PATTERNS = [
        re.compile(
            r'(?:only\s+)?(?:share|disclose)\s+(?:your\s+)?(?:data|information)\s+'
            r'(?:when|if|with\s+your\s+consent|for|to)\s+([^\n.]{5,120})',
            re.IGNORECASE,
        ),
        re.compile(r'with\s+your\s+(?:explicit\s+)?consent', re.IGNORECASE),
        re.compile(r'as\s+required\s+by\s+law', re.IGNORECASE),
        re.compile(r'for\s+legitimate\s+(?:business\s+)?(?:purposes?|interests?)', re.IGNORECASE),
        re.compile(r'to\s+fulfil(?:l)?\s+(?:our\s+)?(?:contract|agreement|obligations?)', re.IGNORECASE),
        re.compile(r'in\s+the\s+event\s+of\s+(?:a\s+)?(?:merger|acquisition|sale)', re.IGNORECASE),
    ]

    _PURPOSE_KEYWORDS: Dict[str, str] = {
        'advertising': 'Advertising and marketing',
        'analytics': 'Analytics and telemetry',
        'research': 'Research purposes',
        'fraud': 'Fraud detection/prevention',
        'payment': 'Payment processing',
        'support': 'Customer support',
        'legal': 'Legal compliance',
        'machine learning': 'AI/ML model training',
        'personalisation': 'Personalisation / recommendation',
        'personalization': 'Personalisation / recommendation',
    }

    def extract(self, text: str) -> Dict[str, object]:
        """
        Returns:
            {
              "data_types_mentioned": {
                "personal_identifiers": ["name", "email address", ...],
                "financial":            ["credit card"],
                ...
              },
              "recipients": ["our advertising partners", "Stripe", ...],
              "conditions": ["with your explicit consent", ...],
              "purposes":   ["Advertising and marketing", "Payment processing", ...]
            }
        """
        text_lower = text.lower()

        # Data types
        data_types: Dict[str, List[str]] = {}
        seen_dt: set = set()
        for category, keywords in self._DATA_TYPES.items():
            for kw in keywords:
                if kw.lower() in text_lower and kw.lower() not in seen_dt:
                    data_types.setdefault(category, []).append(kw)
                    seen_dt.add(kw.lower())

        # Recipients
        recipients: List[str] = []
        seen_r: set = set()
        for pattern in self._RECIPIENT_PATTERNS:
            for m in pattern.finditer(text):
                snippet = m.group(1).strip()[:100] if m.lastindex else ''
                if 3 < len(snippet) < 100 and snippet not in seen_r:
                    recipients.append(snippet)
                    seen_r.add(snippet)

        # Conditions
        conditions: List[str] = []
        seen_c: set = set()
        for pattern in self._CONDITION_PATTERNS:
            for m in pattern.finditer(text):
                snippet = m.group(0).strip()[:150]
                if snippet not in seen_c:
                    conditions.append(snippet)
                    seen_c.add(snippet)

        # Purposes
        purposes = list(dict.fromkeys(
            desc for kw, desc in self._PURPOSE_KEYWORDS.items()
            if kw in text_lower
        ))

        return {
            'data_types_mentioned': data_types,
            'recipients': recipients[:20],
            'conditions': conditions[:15],
            'purposes': purposes,
        }


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------

def run_all_extractors(text: str, company_name: str = "Unknown") -> Dict:
    """
    Run all seven extraction modules against *text* and return a single
    structured dict suitable for JSON serialisation.

    Args:
        text:         Full text of the policy / terms document.
        company_name: Human-readable company name for metadata.

    Returns:
        {
          "company_name":    "Acme Corp",
          "analysis_date":   "2024-01-15T10:30:00",
          "document_length": 12345,
          "word_count":      2000,
          "tech_stack":      { ... },
          "websites_domains":{ ... },
          "repositories":    { ... },
          "third_party_services": { ... },
          "apis_integrations":    { ... },
          "bots_automation":      { ... },
          "data_sharing":         { ... }
        }
    """
    return {
        'company_name': company_name,
        'analysis_date': datetime.now().isoformat(),
        'document_length': len(text),
        'word_count': len(text.split()),
        'tech_stack': TechStackExtractor().extract(text),
        'websites_domains': WebsiteDomainExtractor().extract(text),
        'repositories': RepositoryExtractor().extract(text),
        'third_party_services': ThirdPartyServiceExtractor().extract(text),
        'apis_integrations': APIIntegrationExtractor().extract(text),
        'bots_automation': BotAutomationExtractor().extract(text),
        'data_sharing': DataSharingExtractor().extract(text),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _format_section(title: str, data: object, indent: int = 2) -> List[str]:
    """Recursively format a dict/list section for CLI display."""
    pad = ' ' * indent
    lines: List[str] = [f"{pad}{title}:"]
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines += _format_section(k.replace('_', ' ').title(), v, indent + 2)
            elif v:
                lines.append(f"{pad}  {k.replace('_', ' ').title()}: {v}")
    elif isinstance(data, list):
        for item in data:
            lines.append(f"{pad}  - {item}")
    else:
        lines.append(f"{pad}  {data}")
    return lines


def format_extraction_report(result: Dict) -> str:
    """Return a human-readable extraction report from ``run_all_extractors``."""
    lines = [
        '=' * 80,
        f"EXTRACTION REPORT: {result['company_name']}",
        f"Analysed {result['word_count']:,} words  |  {result['document_length']:,} chars",
        '=' * 80,
        '',
    ]

    section_titles = {
        'tech_stack': '1. TECH STACK',
        'websites_domains': '2. WEBSITES & DOMAINS',
        'repositories': '3. REPOSITORIES',
        'third_party_services': '4. THIRD-PARTY SERVICES',
        'apis_integrations': '5. APIs & INTEGRATIONS',
        'bots_automation': '6. BOTS & AUTOMATION',
        'data_sharing': '7. DATA SHARING',
    }

    for key, title in section_titles.items():
        section = result.get(key, {})
        lines.append(title)
        lines.append('-' * 40)
        if not section:
            lines.append('  (none detected)')
        else:
            for sub_key, sub_val in section.items():
                if not sub_val:
                    continue
                label = sub_key.replace('_', ' ').title()
                if isinstance(sub_val, list):
                    lines.append(f"  {label} ({len(sub_val)}):")
                    for item in sub_val[:15]:
                        lines.append(f"    - {item}")
                    if len(sub_val) > 15:
                        lines.append(f"    ... and {len(sub_val) - 15} more")
                elif isinstance(sub_val, dict):
                    lines.append(f"  {label}:")
                    for cat, items in sub_val.items():
                        if items:
                            cat_label = cat.replace('_', ' ').title()
                            lines.append(f"    {cat_label}: {', '.join(str(i) for i in items[:8])}")
                else:
                    lines.append(f"  {label}: {sub_val}")
        lines.append('')

    lines.append('=' * 80)
    return '\n'.join(lines)


def main():
    """Interactive CLI for the extraction modules."""
    import json as _json
    import sys

    print("Extraction Modules — AI-Policy-Terms-Analyzer")
    print("=" * 80)

    company = input("Company name (optional): ").strip() or "Unknown Company"
    print("\nPaste policy text (Ctrl+D / Ctrl+Z when done):")
    print("-" * 80)

    lines_in = []
    try:
        while True:
            try:
                lines_in.append(input())
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)

    text = "\n".join(lines_in).strip()
    if not text:
        print("No text provided — using built-in example.")
        text = (
            "We use AWS and Kubernetes for our infrastructure. "
            "Our React frontend communicates with a REST API. "
            "Payments are handled by Stripe and PayPal. "
            "We use Google Analytics and Mixpanel for analytics. "
            "Email delivery is via SendGrid. "
            "Source code is hosted at https://github.com/example/repo. "
            "Our chatbot is powered by OpenAI GPT-4. "
            "We share your email address and usage data with our advertising partners "
            "with your consent. "
            "Webhooks are available at https://api.example.com/v1/webhook. "
            "Automated scraping of our site is prohibited. "
            "Visit https://example.com/privacy for details."
        )

    result = run_all_extractors(text, company)
    print("\n" + format_extraction_report(result))

    save = input("Save JSON? (y/n): ").strip().lower()
    if save == 'y':
        import re as _re
        safe = _re.sub(r'[^\w\s-]', '', company).strip()
        safe = _re.sub(r'[-\s]+', '_', safe)
        fname = f"{safe}_extraction.json"
        with open(fname, 'w') as fh:
            _json.dump(result, fh, indent=2)
        print(f"Saved to {fname}")


if __name__ == "__main__":
    main()
