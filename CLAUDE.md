# CLAUDE.md

Guidance for automated coding work in this repository.

## Project scope

This repository is a Python toolkit for extracting technical, operational, automation, integration, and data-sharing signals from public policy, privacy, and terms documents. It is not a legal-advice or compliance-certification tool.

## Verification

```bash
pip install -e ".[all]"
python -m pytest -q
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --max-line-length=120 --statistics --exit-zero
```

`.github/workflows/ci.yml` runs the complete pytest suite on Python 3.9, 3.11, and 3.13. `.github/workflows/codeql.yml` runs Python CodeQL separately. PR #39 established the hardening baseline; PR #40 completed repository hygiene. Older notes describing excluded tests or a known `repo_urls` failure are stale.

## Main components

- `controlled_policy_analysis.py`: bounded URL-only workflow. It takes a homepage, inspects links on that homepage only, classifies policy-looking links, selects qualifying first-party links, fetches selected documents, and sends extracted text through the existing `PolicyAnalyzer`. It records source URLs, excluded policy candidates, and categories not found during the bounded discovery step.
- `policy_analyzer.py`: main analyser with legacy and structured output fields.
- `extraction_modules.py`: canonical structured extractor implementations.
- `document_scanner.py`: file, HTML, PDF, and URL text extraction.
- `batch_analyzer.py`: batch orchestration.
- `ai_policy_researcher.py` and `key_point_condenser.py`: separate analysis utilities.
- `ai_operator_os.py`: separate experimental orchestration scope.

## Controlled URL workflow

```bash
analyze-site https://example.com
analyze-site https://example.com --limit 5
```

The controlled workflow has these limits:

- one-hop discovery from the supplied homepage only;
- HTTP(S) links only;
- automatic selection limited to the supplied site host and qualifying subdomains;
- policy-looking external links are recorded but not followed;
- obvious blog, news, press, careers, and jobs paths are excluded unless they contain a strong policy phrase;
- document categories include privacy, terms, cookies, acceptable use, AI terms, data processing, and subscription/billing;
- a category reported as not found means not found in this bounded discovery step, not proven absent;
- remote PDF policy links are reported but not analysed in controlled v0.1;
- results are extraction evidence for human review, not legal interpretation or a safe/unsafe verdict.

Do not broaden crawl depth, automatic host selection, document types, or interpretation claims without a separate change and tests.

## Compatibility

Structured extractors are preferred for new extraction behaviour. Legacy fields remain compatibility adapters unless an intentional breaking change is approved and tested.

## Configuration

`PolicyAnalyzer` has no config-file loader, no environment-variable configuration system, no `config=` constructor argument, and no general CLI configuration flags. Detection customisation is done by changing public instance attributes before `analyze()`.

`analyze-site` is a separate narrow CLI. It accepts a homepage URL and optional `--limit`; that is not a general configuration system.

`docs/examples/*.json` are reference snippets only and are not loaded automatically.

## Evidence discipline

- Tests prove only the behaviours they assert.
- A successful CodeQL run does not prove absence of vulnerabilities.
- A discovered link does not prove a document is current, applicable, complete, or controlling.
- Failure to discover a document category does not prove absence.
- Preserve source provenance for consequential findings.
- Do not add claims of legal correctness, compliance, production readiness, general accuracy, or unattended decision suitability without evidence.

## Repository hygiene

Keep the repository limited to project code, tests, package/configuration files, project documentation, and intentional examples. Do not add personal certificates, course workbooks, training schedules, or unrelated learning files.
