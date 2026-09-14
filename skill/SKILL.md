---
name: analyzing-policy-and-terms
description: Use when a user wants to inspect a privacy policy, terms of service, acceptable-use policy, AI policy, DPA, billing policy, or company homepage to extract technical and operational signals while preserving provenance and avoiding legal, compliance, or production-readiness overclaims.
---

# Analyzing Policy and Terms

## Overview

Turn dense policy, terms, privacy, acceptable-use, AI, data-processing, cookie, and subscription documents into structured, source-bound technical and operational findings.

This skill is extracted from `9TEVE-O/AI-Policy-Terms-Analyzer` and preserves its strongest reusable pattern:

source acquisition → bounded discovery → structured signal extraction → contextual review → provenance-preserving report → explicit limitations.

## Core Principle

A detected term is evidence that language appears in the analysed source. It is not automatically evidence that the organisation currently uses the technology, that the relationship applies to the user, that the document is governing, or that any legal or compliance conclusion follows.

Claim strength must not exceed source strength.

## When To Use

Use this skill when the user asks to:

- analyse a privacy policy, terms of service, acceptable-use policy, AI policy, DPA, cookie policy, or billing/subscription policy;
- identify technologies, platforms, services, APIs, repositories, bots, automation, or data-sharing language in those documents;
- inspect a company homepage for first-party policy documents and analyse the qualifying documents found;
- compare the same policy signals across several organisations or document versions;
- produce structured findings or JSON-like output from long policy text;
- investigate whether a document mentions a specific provider, technology, integration, automation mechanism, or data-sharing relationship.

## When Not To Use

Do not use this skill as the primary procedure when the user asks for:

- a legal opinion, compliance certification, regulatory determination, contractual approval, or enforceability conclusion;
- a security audit of source code or infrastructure;
- a production-readiness certification;
- a general website crawl unrelated to policy or terms discovery;
- a conclusion that a technology or practice is absent merely because it was not detected;
- a conclusion that a detected service is currently deployed merely because its name appears in a document.

For legal or compliance questions, this skill may extract and organise the relevant policy evidence, but it must stop short of making an authoritative legal determination.

## Inputs To Inspect

Accept one or more of:

1. supplied document text;
2. an uploaded policy/terms document;
3. an exact policy-document URL;
4. a company homepage URL for bounded discovery;
5. several documents or organisations for comparison;
6. an accessible local/connected copy of the source repository when deterministic extraction is requested or available.

Before analysis, record the input mode and the source actually inspected.

## Analysis Modes

### Mode A — Repository-backed extraction

Use when the repository code is locally available or accessible through an authorised tool.

Run the repository’s extraction path first, then context-review material detections against the source text.

Record the method as:

`repository extractor + contextual review`

Do not treat passing repository tests as proof of semantic accuracy, legal correctness, or production fitness.

### Mode B — Source-bound analysis

Use when the repository code is not available but the source text or document is available.

Reproduce the repository’s extraction categories using direct source inspection. Preserve supporting passages for material findings.

Record the method as:

`source-bound analysis; repository code not executed`

Never describe this mode as though the Python analyzer itself produced the result.

### Mode C — Homepage discovery

Use when the user provides a company homepage rather than a direct policy document.

Apply a bounded one-hop discovery path:

homepage → inspect visible links → classify policy-looking links → select qualifying first-party links → analyse selected documents.

Recognise these discovery categories:

- privacy;
- terms;
- cookies;
- acceptable use;
- AI terms or AI policy;
- data processing agreement/addendum;
- subscription or billing policy.

Default boundary:

- inspect links exposed from the supplied homepage;
- follow only qualifying first-party policy links;
- record policy-looking external links as excluded candidates rather than following them automatically;
- do not silently expand into a site-wide crawl, sitemap crawl, login flow, or unrelated external domain.

A category not found means only that the bounded discovery did not find a qualifying link. It does not establish organisational absence.

## Extraction Schema

Extract the seven core signal families:

1. technology stack;
2. websites and domains;
3. repositories and version-control references;
4. third-party services;
5. APIs and integrations;
6. bots and automation;
7. data sharing.

Use `references/extraction-schema.md` for the detailed subcategories and output fields.

## Workflow

### 1. Define scope

State what source or sources are being analysed, what period/version is visible if known, and whether the task is single-document, discovery, or comparison.

Do not invent missing version, effective date, jurisdiction, or applicability information.

### 2. Acquire and preserve provenance

For each source, preserve as available:

- source URL or file identity;
- page/document title;
- visible effective or updated date;
- organisation name;
- discovery parent page when applicable;
- discovery label/category when applicable;
- analysis method.

If the source is incomplete, truncated, scanned poorly, translated, or inaccessible, say so.

### 3. Extract candidate signals

Scan the complete available source for the seven signal families.

Treat keyword or pattern matches as candidate detections first.

### 4. Context-review material detections

For each material finding, inspect enough surrounding text to determine whether the source is:

- affirming use or operation;
- describing a third party;
- prohibiting or restricting conduct;
- describing a hypothetical or conditional case;
- referring to historical practice;
- referring to a user/customer capability rather than the organisation’s own stack;
- merely linking or naming something without establishing a relationship.

Preserve the smallest sufficient supporting passage for any material conclusion.

### 5. Calibrate the finding

Use these evidence states where useful:

- `EXPLICIT MENTION` — the source contains the named term or relationship language;
- `CONTEXT-SUPPORTED` — surrounding text supports the stated relationship or use;
- `NOT DETECTED` — no matching evidence was found in the analysed source; this is not proof of absence;
- `UNRESOLVED` — wording is ambiguous, incomplete, conflicting, or context is missing.

Do not promote an `EXPLICIT MENTION` into `CONTEXT-SUPPORTED` without source language that supports the stronger relationship.

### 6. Preserve contradictions and exclusions

If different documents, sections, dates, or clauses conflict, report the contradiction rather than selecting one silently.

If material linked/incorporated documents were not analysed, list them as exclusions or unknowns where relevant.

### 7. Report findings

Lead with the most material source-supported findings, then provide the structured categories.

Use the output contract below.

## Output Contract

Default report:

### Analysis scope
- organisation/document;
- source(s);
- method;
- visible version/effective date if present;
- bounded discovery coverage if homepage mode was used.

### Material findings
For each significant finding include:

- category;
- signal;
- relationship or context;
- evidence state;
- supporting passage or precise source reference;
- qualification/uncertainty.

### Structured extraction
Report the seven core categories using the schema in `references/extraction-schema.md`.

### Discovery coverage
When homepage discovery was used, report:

- selected first-party policy documents;
- excluded policy-looking external candidates;
- categories not found within the bounded discovery;
- fetch/extraction failures.

### Limitations and unknowns
State the material limitations that affect interpretation.

Optional on request:

- machine-readable JSON;
- cross-company comparison table;
- document outline or condensed summary.

## Safety and Evidence Rules

1. Detection does not prove deployment, applicability, legal significance, or current operation.
2. Non-detection does not prove absence.
3. A discovered policy does not prove that it is current, complete, applicable, governing, or legally controlling.
4. Do not provide legal advice, compliance certification, regulatory approval, or production-readiness certification from this analysis.
5. Do not claim that repository tests prove semantic accuracy of policy interpretation.
6. For consequential findings, preserve the supporting source passage and require human review against the complete source.
7. Consider definitions, exceptions, cross-references, dates, jurisdiction, incorporated documents, and versioning before strengthening a claim.
8. For private, confidential, privileged, personal, commercially sensitive, or regulated documents, minimise unnecessary transfer and retention; do not send content to additional external systems unless authorised and necessary.
9. Do not infer organisational ownership of unrelated external domains.
10. Do not turn historical, hypothetical, excluded, third-party, or prohibited language into a claim of current organisational practice.

See `references/responsible-use.md` for the full boundary.

## Batch and Comparison Rules

When comparing organisations or document versions:

- keep each source’s provenance separate;
- use the same extraction categories across sources;
- distinguish `not detected` from `not analysed`;
- do not merge contradictory findings into one synthetic position;
- compare like with like where possible (privacy vs privacy, terms vs terms, current vs current);
- flag materially different dates, jurisdictions, document scopes, or source completeness.

## Optional Condensation

For very long documents, an extractive summary or outline may be produced to aid navigation. It must not replace the source evidence used for findings.

## Common Failure Modes

| Failure | Correction |
|---|---|
| “Stripe detected, therefore Stripe is the payment processor.” | Report the mention first; strengthen only if surrounding text establishes that relationship. |
| “No DPA found, therefore the company has no DPA.” | State only that the bounded discovery found no qualifying DPA link. |
| “Bots are mentioned, therefore the service uses bots.” | Check whether the clause actually prohibits bots or describes customer behaviour. |
| “Tests pass, therefore results are accurate.” | Tests establish tested code behaviour, not general semantic or legal validity. |
| “External policy link probably belongs to them.” | Record it as an external candidate unless ownership is established. |
| “The policy says X, so the company is compliant.” | Extract the clause; do not issue the compliance determination. |

## Validation / Done Criteria

The analysis is complete only when:

- the analysed source set is explicit;
- the method is stated accurately;
- provenance is preserved for material sources;
- all seven core signal families were assessed unless intentionally scoped out;
- material findings are supported by source context;
- prohibitions, hypotheticals, historical statements, and third-party references were not misclassified as current practice;
- non-detection is not represented as absence;
- contradictions and material exclusions are preserved;
- legal/compliance/production-readiness boundaries are respected;
- homepage discovery, when used, reports selected, excluded, missing, and failed categories distinctly.

Use `tests/skill-cases.md` as the minimum positive/negative validation set when revising this skill.

## Source Basis

Extracted from `9TEVE-O/AI-Policy-Terms-Analyzer`, main branch commit `01c4bedfb3a6016e73115535fae4ec1a83be9600` (29 August 2026).

Primary source files used for this skill:

- `README.md`;
- `extraction_modules.py`;
- `controlled_policy_analysis.py` / `docs/controlled_policy_analysis.md`;
- `docs/RESPONSIBLE_USE_EVIDENCE_RUN_2026-07-22.md`;
- `QUICK_REFERENCE.md`.
