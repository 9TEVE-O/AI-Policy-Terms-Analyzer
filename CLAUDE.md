# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Python toolkit for extracting structured technical, operational, and data-sharing signals from policy, privacy, and terms-of-service documents. It is explicitly **not** a legal/compliance tool — see the "Limitations and responsible use" section of `README.md` before changing anything that touches detection claims or report wording.

Standard-library only by default; `beautifulsoup4`, `requests`, and `pdfplumber` are optional and feature-detected at import time (see `document_scanner.py`).

## Commands

```bash
pip install -e .              # or: pip install -e ".[all]" for HTML/PDF/URL scanning support

# Run tools interactively
python policy_analyzer.py
python key_point_condenser.py
python batch_analyzer.py
python quick_start.py
python ai_policy_researcher.py
python document_scanner.py
python ai_operator_os.py
python extraction_modules.py

# Lint (matches CI in .github/workflows/ci.yml)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics   # errors only, fails build
flake8 . --count --max-line-length=120 --statistics --exit-zero      # style warnings, informational
```

### Running tests

There is no single test command — two conventions coexist:

- Most `test_*.py` files are **dual-mode**: plain `assert`-based functions named `test_*`, called manually from an `if __name__ == "__main__":` block. Run them directly (`python test_extraction_modules.py`) or under pytest (`pytest test_extraction_modules.py`, or `pytest test_extraction_modules.py::test_api_detects_rest` for a single case) — both work.
- `test_pyproject_toml.py` is pytest-only (uses a `@pytest.fixture`, has no `__main__` block): `pytest test_pyproject_toml.py`.

CI does not run everything the same way or run all files:
- `.github/workflows/ci.yml` runs `pytest test_google_cloud.py test_ai_operator_os.py test_key_point_condenser.py -v`.
- `.github/workflows/tests.yml` runs `python test_document_scanner.py`, `test_extraction_modules.py`, `test_ai_policy_researcher.py`, and `test_ai_operator_os.py` as direct scripts.
- `test_privacy_concerns.py` and `test_pyproject_toml.py` are not wired into either workflow.

**Known pre-existing failure**: `test_extraction_modules.py::test_bot_prohibition_snippets` fails on `main` as of the current HEAD (`AssertionError: Expected prohibition mention, got: []`) — a regex/test mismatch in `BotAutomationExtractor`'s prohibition-snippet detection, unrelated to unrelated changes. Don't assume you broke something if you see only this failure.

## Architecture

Several independently-usable analysis engines share the repo but are **not** unified behind one entry point or config system:

- **`policy_analyzer.py` (`PolicyAnalyzer`)** — the main analyzer. `analyze()` returns a dict with two parallel sets of fields for the same underlying signals: legacy fields computed by methods defined directly on `PolicyAnalyzer` (`extract_urls`, `detect_technologies`, `extract_third_party_services`, ...), and structured fields computed by delegating to `extraction_modules.py`'s seven `*Extractor` classes (`tech_stack`, `websites_domains`, `repositories`, `third_party_services_structured`, `apis_integrations`, `bots_automation`, `data_sharing_structured`). The structured extractors are the newer, canonical implementation (see `REPO_AUDIT_2026-06-30.md` finding #2–3); the legacy fields exist for backward compatibility with older report/JSON consumers. When fixing a detection bug, check whether the same logic is duplicated in both a `PolicyAnalyzer` method and the corresponding `extraction_modules.py` extractor.
- **`extraction_modules.py`** — seven standalone `Extractor` classes (`TechStackExtractor`, `WebsiteDomainExtractor`, `RepositoryExtractor`, `ThirdPartyServiceExtractor`, `APIIntegrationExtractor`, `BotAutomationExtractor`, `DataSharingExtractor`), each with an `extract(text) -> dict` method, plus `run_all_extractors()` as a standalone orchestrator independent of `PolicyAnalyzer`.
- **`document_scanner.py` (`DocumentScanner`)** — turns files/URLs/HTML into plain text for the analyzers above; not wired into `PolicyAnalyzer` automatically, callers pass its output in manually.
- **`ai_policy_researcher.py` (`AIPolicyResearcher`)** and **`key_point_condenser.py` (`KeyPointCondenser`)** — separate, self-contained analyzers (AI-clause detection; extractive summarization) that don't share code with `PolicyAnalyzer` or each other.
- **`batch_analyzer.py`** — thin orchestration layer that runs `PolicyAnalyzer` over multiple companies and builds a comparison report.
- **`ai_operator_os.py`** — a separate three-tier orchestration experiment (Data / Kernel / Application layers: `RelationalStore`/`VectorStore`/`FileStore`, `Scheduler`/`ContextManager`/`MemoryManager`/`LLMCore`/`ToolAccessManager`/`EvaluationEngine`, and domain `Agent`s) that wraps `PolicyAnalyzer` via its `ResearchAgent`. `LLMCore` runs in a documented no-dependency "mock" mode unless a real provider is registered with `register_provider()`. Largely independent of the rest of the codebase — read `docs/ai_operator_os_architecture.md` before touching it.

### No configuration system

Despite what `docs/configuration.md`'s "See also" links and `docs/README.md` may suggest, **there is no config-file loader, `POLICY_ANALYZER_*` environment-variable system, or CLI flag parsing anywhere in this codebase** (verified: no `argparse`/`sys.argv` usage in any `.py` file, `PolicyAnalyzer.__init__` takes no `config` argument). The only real customization mechanism is mutating public instance attributes in Python before calling `analyze()`, e.g. `analyzer.tech_keywords['blockchain'] = [...]` — `tech_keywords`, `gcp_services`, and `gcp_programs` are read fresh on every call. `docs/examples/*.json` are illustrative keyword-list snippets to copy from by hand, not files the tool loads. Don't propagate the config-file/CLI-flag claims into new code or docs — see `docs/configuration.md` for the corrected version.

### Root-directory noise

The repo root also contains unrelated personal/learning materials (PDFs, an `.xlsx` workbook, a `memory assessment` file) that are not part of the project — ignore them unless a task specifically references them.
