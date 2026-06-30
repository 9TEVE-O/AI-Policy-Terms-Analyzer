# Repository Audit — AI Policy Terms Analyzer

Status: audited with write limitation.
Classification: working Python toolkit / portfolio proof asset / needs cleanup before client-safe use.
Date: 2026-06-30

## Reframed question

Audit the repository as a working Python toolkit, fix concrete breakages where possible, and strengthen its research/product value without inflating claims beyond what the code demonstrates.

## Highest-leverage answer

The repo should not be expanded first. It should be made smaller, cleaner, more testable, and more obviously useful as a document-intelligence proof asset.

The strongest positioning is not legal analysis. It is structured policy-document extraction: finding URLs, domains, services, APIs, automation clauses, repositories, data-sharing language, and privacy-risk signals in long policy and terms documents.

## Assumptions

- The repo is intended as a public proof-of-work asset.
- The project should remain standard-library-first.
- The tool should avoid claiming legal/compliance advice.
- The priority is practical document intelligence, not a full SaaS product.

## Missing information

- No CI result was available during this audit.
- No package metadata is present, so the repo is not yet installable as a Python package.
- The repo contains unrelated PDFs/workbooks, which makes the canonical project boundary unclear.
- No benchmark corpus or labelled evaluation set is present.

## Failure conditions

This repo fails as a professional proof asset if it is presented as a legal analyser, compliance validator, or AI governance system. It also fails if duplicate legacy and structured extraction paths continue to drift without a documented compatibility policy.

## Findings

### 1. Repo scope is noisy

The codebase includes useful Python modules, but the root directory also contains unrelated PDFs, workbooks, certificates, and learning materials. That weakens the repository signal.

Fix direction:
- Move unrelated artefacts out of the repository or into `/docs/archive/learning-materials/` if they must remain.
- Keep the root focused on runnable code, tests, README, examples, and docs.

### 2. Strongest code path is `extraction_modules.py`

The structured extractor architecture is the clearest asset. It separates detection into seven categories:

- Tech stack
- Websites and domains
- Repositories
- Third-party services
- APIs and integrations
- Bots and automation
- Data sharing

This is the strongest foundation for the project.

### 3. `policy_analyzer.py` duplicates legacy and structured logic

`PolicyAnalyzer.analyze()` emits both legacy fields and structured fields. This is useful for backwards compatibility, but it creates a maintenance risk because the two extraction paths can disagree.

Fix direction:
- Treat `extraction_modules.py` as canonical.
- Keep legacy keys only as adapters.
- Add a compatibility note in README.

### 4. Matching logic risks false positives

Several extractors use substring matching. This can create false positives such as short technology terms appearing inside unrelated words.

Examples:
- `go` can match inside ordinary words.
- `r`-style short keywords are risky unless explicitly bounded.
- service names with generic meanings, such as `make`, `front`, `box`, or `segment`, need context or word-boundary checks.

Fix direction:
- Use word-boundary regex helpers for keyword matching.
- Treat short/generic tokens as high-risk and require contextual evidence.
- Add regression tests for false positives.

### 5. URL scanning needs hardening

`document_scanner.py` is generally useful, but URL handling should be hardened:

- Validate parsed URL schemes rather than case-sensitive string prefixes.
- Keep header access inside the urllib response context.
- Enforce max download size without exceeding the limit by a full chunk.
- Keep the no-dependency fallback behaviour.

Patch attempt note:
- A direct write attempt to harden `document_scanner.py` was blocked by the tool safety layer. Do not treat this audit file as a completed code patch.

### 6. Tests are useful but not enough

The test suite covers many positive extraction cases. It needs more negative tests.

Add tests for:
- No `go` detection in `governance`.
- No `java` detection in `javascript` unless Java is separately mentioned.
- No `bot` detection inside unrelated words.
- No service detection for generic English words unless context supports it.
- URL scanner accepts `HTTPS://example.com` and rejects `file:///etc/passwd`.

### 7. README should narrow claims

Current README positioning is close, but the safest public description is:

> A Python toolkit for extracting structured technical, operational, and data-sharing signals from public policy, privacy, and terms documents.

Avoid:
- legal analysis
- compliance validation
- privacy scoring as fact
- claims that the tool determines whether a policy is safe

## Recommended next commits

1. Harden `document_scanner.py` URL handling.
2. Add false-positive regression tests to `test_extraction_modules.py`.
3. Add a short `docs/claim_boundaries.md` file.
4. Move unrelated PDFs/workbooks out of root or into an archive folder.
5. Add GitHub Actions for `python -m pytest` or direct test script execution.

## Patch target: `document_scanner.py`

Concrete intended fixes:

- Import `urllib.parse`.
- In `scan_url()`, parse the URL and validate `parsed.scheme.lower()` against `{'http', 'https'}`.
- Require `parsed.netloc`.
- In `_fetch_url()`, read headers inside the urllib context manager.
- In the requests path, append only the remaining bytes needed to respect `_MAX_URL_BYTES`.

## Promotion status

Current status: audited / patch blocked.

Do not mark as fixed until the code patch lands and tests are run.

## Next concrete action

Apply the `document_scanner.py` hardening patch manually or in a trusted local dev environment, then run:

```bash
python test_document_scanner.py
python test_extraction_modules.py
python test_ai_policy_researcher.py
python test_ai_operator_os.py
```

Promotion condition:

- Tests pass.
- False-positive regression tests are added.
- README claims stay within extraction/toolkit boundaries.
