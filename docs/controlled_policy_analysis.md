# Controlled Policy Analysis v0.1

## Purpose

Provide one bounded URL-only path from a public website homepage to structured
policy-document extraction while preserving source provenance and explicit
limits.

The workflow is:

```text
homepage URL
→ inspect homepage links
→ classify policy-looking links
→ select qualifying first-party links
→ fetch selected documents
→ run existing PolicyAnalyzer extraction
→ return provenance, exclusions, missing discovery categories, and limitations
```

## Usage

From the repository after installing dependencies:

```bash
pip install -e ".[all]"
python controlled_policy_analysis.py https://example.com
```

Optionally cap the number of selected documents analysed:

```bash
python controlled_policy_analysis.py https://example.com --limit 5
```

The command emits JSON. The runner is repository-local in v0.1 and is not
registered as an installed console script.

## Discovery categories

v0.1 recognises policy-looking links for:

- privacy;
- terms;
- cookies;
- acceptable use;
- AI terms/policies;
- data processing agreements/addenda; and
- subscription/billing policies.

A category listed as `categories_not_found` means only that the bounded
homepage-link discovery did not find a qualifying link. It does not establish
that the organisation has no such document.

## First-party selection rule

The supplied homepage host defines the automatic selection boundary. For a
homepage such as `https://www.example.com`, links to `example.com` and its
subdomains can qualify. External policy-looking links are recorded under
`excluded_policy_candidates` and are not followed automatically.

The implementation intentionally avoids guessing organisational ownership from
unrelated hostnames.

## Provenance

Each selected document retains:

- source URL;
- visible link label;
- policy categories assigned during discovery;
- matched discovery terms; and
- the homepage from which it was discovered.

The existing `PolicyAnalyzer` result is attached only after visible text has
been fetched successfully.

## Explicit v0.1 limits

- one-hop discovery from the supplied homepage only;
- no site-wide crawling or sitemap traversal;
- no external-host following;
- no login/session workflows;
- remote PDF policy links are reported but not analysed;
- no determination that a discovered document is current, applicable,
  complete, governing, or legally controlling;
- no safe/unsafe verdict;
- no legal advice or compliance certification.

## Acceptance gate

The v0.1 slice is acceptable only when:

1. existing PolicyAnalyzer regression tests remain green;
2. first-party policy discovery tests are green;
3. external policy-looking links are not fetched automatically;
4. missing categories are represented as bounded discovery results, not claims
   of organisational absence;
5. source provenance survives into the result;
6. the full repository pytest matrix passes on Python 3.9, 3.11, and 3.13; and
7. CodeQL completes successfully.
