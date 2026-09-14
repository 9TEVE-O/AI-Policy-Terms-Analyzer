# Extraction Schema

Use this reference to keep analysis categories stable across runs.

## 1. Technology stack

Candidate subcategories:

- cloud platforms;
- programming languages;
- frameworks;
- databases;
- infrastructure and observability;
- AI/ML platforms and concepts;
- messaging/queues;
- CDN/storage.

Recommended fields:

```text
signal
subcategory
raw mention
context
state
source reference
qualification
```

A technology name alone is normally `EXPLICIT MENTION`. Strengthen only when the clause establishes use, provision, integration, hosting, processing, or another specific relationship.

## 2. Websites and domains

Extract:

- explicit URLs;
- domains referenced in the document;
- policy/document links when relevant.

Do not infer ownership merely from mention.

## 3. Repositories and version control

Extract:

- repository URLs;
- version-control hosts (for example GitHub, GitLab, Bitbucket, Codeberg);
- source-code or repository context snippets.

Distinguish a direct repository link from a generic platform mention.

## 4. Third-party services

Candidate subcategories:

- payment processors;
- analytics;
- email/marketing;
- customer support;
- advertising;
- authentication/social login;
- CDN/performance;
- monitoring/logging;
- cloud/storage.

For each named service, determine whether the source establishes a relationship, merely mentions it, or refers to a user-selected integration.

## 5. APIs and integrations

Extract:

- REST;
- GraphQL;
- gRPC;
- WebSocket;
- webhooks;
- SDK/client libraries;
- OAuth/OIDC/access-token/API-key language;
- named integrations;
- endpoint patterns;
- relevant context snippets.

Do not expose secrets or credentials if they appear in a private source. Minimise them in output.

## 6. Bots and automation

Candidate subcategories:

- chatbots/virtual assistants;
- crawlers/scrapers;
- automated systems/workflows;
- AI agents;
- email automation;
- scheduled jobs or CI/CD language;
- prohibitions/restrictions on bots, scraping, crawling, or automated access.

Always test for negation/prohibition before stating that the organisation operates the detected automation.

## 7. Data sharing

Extract separately:

### Data types
Examples include:

- personal identifiers;
- financial data;
- behavioural/usage data;
- location data;
- biometric data;
- health data;
- device identifiers.

### Recipients
Examples include:

- service providers;
- advertisers;
- affiliates/subsidiaries;
- business partners;
- government/law enforcement;
- research partners;
- acquirers in an M&A context.

### Conditions
Examples include:

- consent;
- legal requirement;
- legitimate business purpose;
- contractual performance;
- merger/acquisition/sale.

### Purposes
Examples include:

- advertising/marketing;
- analytics/telemetry;
- research;
- fraud prevention;
- payments;
- support;
- legal compliance;
- AI/ML training;
- personalisation/recommendation.

Do not collapse data type, recipient, condition, and purpose into one generic “shares data” finding.

## Homepage Discovery Schema

When starting from a homepage, maintain:

```text
homepage_url
selected_documents[]
  - url
  - visible_label
  - category/categories
  - matched discovery terms
  - discovery parent
excluded_policy_candidates[]
categories_not_found[]
fetch_failures[]
```

Recognised categories:

- privacy;
- terms;
- cookies;
- acceptable use;
- AI terms/policy;
- DPA/data processing addendum/agreement;
- subscription/billing.

`categories_not_found` is a bounded discovery result only.

## Recommended Machine-Readable Finding

```json
{
  "category": "third_party_services",
  "subcategory": "payment_processors",
  "signal": "Stripe",
  "state": "CONTEXT-SUPPORTED",
  "relationship": "payment processing",
  "evidence": "Payments are processed by Stripe...",
  "source": {
    "title": "Privacy Policy",
    "url": "https://example.com/privacy",
    "effective_date": null
  },
  "qualification": "Current applicability not independently established."
}
```

Use null/unknown values rather than inventing missing metadata.
