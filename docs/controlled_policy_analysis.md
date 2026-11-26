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

Analysed documents may include optional `source_provenance`: `body_sha256`
hashes the exact body bytes returned by the built-in HTTP reader before
character decoding or HTML cleanup; `body_bytes` counts those bytes;
`retrieved_at_utc` is the local UTC clock reading after the body was read.
These are observed bytes, not wire framing or extracted text.

The field is omitted for injected fetchers, non-200 or ranged responses,
reads over the byte cap, invalid/duplicate/mismatched Content-Length,
conflicting Transfer-Encoding and Content-Length, and unsupported or
duplicate Transfer-Encoding. A single chunked transfer is eligible only
when the HTTP reader recognised and decoded it. A response without length
or transfer encoding can be fingerprinted at EOF. IncompleteRead becomes
an explicit fetch error (homepage stops; policy fetch_failed continues).

The standard HTTP reader may tolerate malformed chunk framing or return
only the declared length when extra bytes follow. Neither a successful
read nor EOF proves strict wire integrity or publisher completeness.
Omitting provenance does not change existing analysis eligibility; this
metadata does not attest authenticity, decoding fidelity or legal
completeness. Supporting passages are outside this slice.

## Explicit v0.1 limits

- one-hop discovery from the supplied homepage only;
- no site-wide crawling or sitemap traversal;
- no external-host following;
- public-only HTTP(S) transport with DNS answers validated and pinned to the
  socket destination, HTTPS hostname verification, and ambient proxy bypass disabled;
- loopback, private, link-local and non-global addresses, internal hostnames and
  non-standard ports are rejected; separate network-level egress controls remain necessary;
- no login/session workflows;
- remote PDF policy links are reported but not analysed;
- controlled retrieval requires an explicit media type of `text/html`, `text/plain`,
  or `application/xhtml+xml` (case-insensitive base media type, parameters ignored
  for eligibility). Missing and unsupported/malformed base media types are rejected
  without reading the body. Ineligible policy documents retain their source URL and
  reported content type with `not_analysed` and an explicit reason; ineligible
  homepages stop before discovery with a `ValueError`;
- media eligibility does not establish content authenticity or semantic accuracy;
- unknown or non-text declared character encodings raise `ValueError` with an
  explicit unsupported-encoding reason in both remote fetch paths. A controlled
  homepage encoding failure stops the run; a policy encoding failure is recorded
  as `fetch_failed` and the remaining candidates can proceed. No alternate charset
  is guessed. The existing UTF-8 default for an absent charset and replacement
  of malformed byte sequences for recognized codecs are unchanged;
- a homepage exceeding the configured byte cap stops before link discovery with
  a `ValueError` containing `homepage_truncated`; no partial discovery result or
  missing-category list is emitted. This matches the ineligible-homepage error
  contract. A non-truncated homepage still supports only bounded one-hop discovery;
- fetched policy documents exceeding the byte cap are marked `not_analysed`
  with reason `document_truncated`, rather than treated as completed analyses;
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
