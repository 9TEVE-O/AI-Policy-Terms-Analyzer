# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Python toolkit for extracting structured technical, operational, and data-sharing signals from policy, privacy, and terms-of-service documents. It is explicitly **not** a legal/compliance tool. Read the "Limitations and responsible use" section of `README.md` before changing detection claims or report wording.

The project is standard-library-first. `beautifulsoup4`, `requests`, and `pdfplumber` are optional and feature-detected where needed by `document_scanner.py`.

## Canonical setup and verification

```bash
# Base editable install
pip install -e .

# Install all optional scanner dependencies used by CI
pip install -e ".[all]"

# Canonical full test gate
python -m pytest -q

# Lint exactly as CI does
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --max-line-length=120 --statistics --exit-zero
```

`.github/workflows/ci.yml` is the canonical automated test gate. It runs the complete pytest suite on Python 3.9, 3.11, and 3.13 with optional dependencies installed.

`.github/workflows/codeql.yml` runs Python CodeQL analysis separately.

The repository passed the portfolio hardening gate merged in PR #39 on 14 August 2026. Do not preserve or repeat older documentation that says some test files are excluded from CI or that `test_privacy_concerns.py::test_repositories_detects_github_url` is a known failing test. That state was superseded by the hardening work, including the `repo_urls` / `repository_urls` compatibility regression.

## Interactive tools

```bash
python policy_analyzer.py
python key_point_condenser.py
python batch_analyzer.py
python quick_start.py
python ai_policy_researcher.py
python document_scanner.py
python ai_operator_os.py
python extraction_modules.py
```

## Architecture

Several independently usable analysis engines share the repository but are **not** unified behind one entry point or configuration system:

- **`policy_analyzer.py` (`PolicyAnalyzer`)** — the main analyser. `analyze()` returns both legacy fields and structured fields for overlapping signals. Structured extraction is delegated to `extraction_modules.py`; legacy fields remain for backwards compatibility. When fixing a detection bug, check whether the same logic exists in both paths.
- **`extraction_modules.py`** — seven standalone extractor classes (`TechStackExtractor`, `WebsiteDomainExtractor`, `RepositoryExtractor`, `ThirdPartyServiceExtractor`, `APIIntegrationExtractor`, `BotAutomationExtractor`, `DataSharingExtractor`) plus `run_all_extractors()`.
- **`document_scanner.py` (`DocumentScanner`)** — turns files, URLs and HTML into plain text. It is not automatically wired into `PolicyAnalyzer`; callers pass extracted text to the analyser.
- **`ai_policy_researcher.py` (`AIPolicyResearcher`)** and **`key_point_condenser.py` (`KeyPointCondenser`)** — separate self-contained analysis utilities.
- **`batch_analyzer.py`** — orchestration over multiple documents using `PolicyAnalyzer`.
- **`ai_operator_os.py`** — a separate orchestration experiment that wraps `PolicyAnalyzer` through its research agent. Treat it as independent experimental scope unless a task explicitly targets it.

### Compatibility rule

The structured extractors are the preferred implementation for new extraction behaviour. Legacy fields should remain compatibility adapters unless a deliberate breaking change is approved and tested.

### No configuration system

There is **no config-file loader, environment-variable configuration system, or CLI flag parser** for `PolicyAnalyzer` in the current codebase. In particular:

- no automatic `policyanalyzerrc.*` loading;
- no `POLICY_ANALYZER_*` environment-variable system;
- no `--config`, `--company`, `--output-format`, or `--save-to` flags;
- no `config=` argument on `PolicyAnalyzer()`.

The supported customisation mechanism is direct mutation of public instance attributes before calling `analyze()`, for example:

```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
analyzer.tech_keywords['blockchain'] = ['ethereum', 'bitcoin', 'web3']
results = analyzer.analyze(policy_text, 'Company Name')
```

`docs/examples/*.json` are reference snippets only; the application does not load them.

## Evidence and claim discipline

- Tests demonstrate the behaviours they actually assert; they do not establish legal correctness, production readiness, general accuracy, or security completeness.
- A successful CodeQL workflow does not prove the absence of vulnerabilities.
- Detection output is evidence for human review, not an authoritative interpretation of a contract, privacy notice, law, regulation, or compliance obligation.
- Preserve supporting source text for consequential findings.
- Do not add public claims that exceed the evidence recorded in the repository.

## Repository hygiene

Keep the root limited to project code, tests, package/configuration files, current project documentation, and intentionally retained examples. Do not add personal certificates, course workbooks, training schedules, unrelated learning PDFs, or other non-project artefacts.