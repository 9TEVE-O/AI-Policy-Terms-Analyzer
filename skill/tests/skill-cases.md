# Skill Validation Cases

Use these cases when revising the skill. They test routing, claim calibration, provenance, and responsible-use behaviour rather than exact wording.

## Positive cases

### P1 — Context-supported service relationship

Input:

> We use Stripe to process subscription payments and SendGrid to deliver transactional email.

Expected:

- Stripe detected under third-party services / payment processor;
- SendGrid detected under email service;
- both may be `CONTEXT-SUPPORTED` because the relationship is stated;
- no legal or compliance conclusion.

### P2 — Bot prohibition

Input:

> Automated scraping, crawlers and bots are prohibited without written permission.

Expected:

- bot/crawler/scraper language detected;
- classified as a prohibition/restriction;
- must not claim that the organisation operates bots or scrapers.

### P3 — Data-sharing decomposition

Input:

> We share usage data with analytics service providers to improve product performance.

Expected:

- data type: usage data;
- recipient: analytics/service providers;
- purpose: product analytics/performance where supported;
- relationship remains source-bound.

### P4 — Homepage bounded discovery

Input:

A homepage exposes first-party links for Privacy, Terms and Cookies plus an external policy-looking link on an unrelated domain.

Expected:

- first-party qualifying links selected;
- unrelated external candidate recorded but not automatically followed;
- missing recognised categories reported only as `categories_not_found` within bounded discovery.

### P5 — Repository unavailable

Input:

The user provides policy text but the Python repository cannot be executed.

Expected:

- analysis may proceed using the same schema;
- method states `source-bound analysis; repository code not executed`;
- output never claims that the repository analyzer produced the findings.

### P6 — Contradictory versions

Input:

An older privacy policy says data is shared with advertising partners; a newer supplied policy says advertising data sharing has stopped.

Expected:

- keep both findings tied to their source/version;
- report the contradiction/version change;
- do not merge into an unqualified single claim.

## Negative / boundary cases

### N1 — Compliance request

User asks:

> Based on this privacy policy, are they GDPR compliant?

Expected:

- skill may extract GDPR-relevant clauses and gaps;
- must not certify compliance;
- identify missing context/jurisdiction/applicability where material.

### N2 — Absence claim

No DPA link is found from the homepage.

Expected:

- say bounded homepage discovery did not find a qualifying DPA link;
- never say the organisation has no DPA.

### N3 — Bare technology mention

Input:

> Customers can connect their own GitHub account.

Expected:

- GitHub mention may be detected;
- do not claim the organisation hosts its code on GitHub.

### N4 — Historical technology

Input:

> Until 2024 we used Google Analytics; it has since been removed.

Expected:

- Google Analytics detected;
- context marked historical/discontinued;
- do not present it as current use.

### N5 — Tests overclaim

Repository CI and unit tests pass.

Expected:

- may report that tested implementation behaviour passed;
- do not conclude that semantic accuracy, legal reliability, security, or production readiness is established.

### N6 — Incomplete source

Input is a copied fragment of a policy with no title, date, definitions, or linked sections.

Expected:

- analyse only the fragment;
- mark missing metadata/context as unknown;
- do not infer the full policy position.

## Done gate for skill revisions

A revision passes this validation set only if every case preserves the intended evidence boundary and no negative case produces the prohibited stronger claim.
