# Regression baseline

Branch: `codex/regression-test-hardening`

## Purpose

Create a reliable baseline before future Codex changes modify product logic.

## Safe automated candidates

- `python test_google_cloud.py`
- `python test_ai_operator_os.py`
- `python example_usage.py`

## Manual or interactive candidates

- `python policy_analyzer.py` prompts for company name and pasted policy text.
- `python quick_start.py` pauses for user input before sample analysis and later prompts for interactive analysis.
- `python batch_analyzer.py` opens an interactive menu.

## Required evidence report

Each future change should record:

- commands run
- pass, fail, blocked, or not run status
- files changed
- generated files avoided or ignored
- remaining test gaps
- manual verification steps

## Minimal test target

Add standard-library regression coverage for:

- `PolicyAnalyzer.analyze()` output shape
- URL and email extraction
- technology detection
- API reference detection
- data-sharing detection
- batch-analysis return shape
