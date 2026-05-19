# Regression baseline

Branch: `codex/regression-test-hardening`

## Purpose

Create a reliable baseline before future Codex changes modify product logic.

## Safe automated candidates

- `python test_google_cloud.py`
- `python test_ai_operator_os.py`
- `python example_usage.py`
- `python -m unittest tests/test_policy_analyzer_regression.py`

## Manual or interactive candidates

These commands are valid smoke checks, but they are interactive when run raw. Do not place the raw commands in CI without controlled input or a timeout.

- `python policy_analyzer.py` prompts for company name and pasted policy text.
- `python quick_start.py` pauses for user input before sample analysis and later prompts for interactive analysis.
- `python batch_analyzer.py` opens an interactive menu.

## Manual smoke-check procedure

### `python policy_analyzer.py`

Expected interaction:

1. Run `python policy_analyzer.py`.
2. Enter a test company name, for example `ExampleCo`.
3. Paste a short sample policy that mentions at least one URL, email, technology, API, and data-sharing clause.
4. Send EOF:
   - macOS/Linux: `Ctrl+D`
   - Windows: `Ctrl+Z`, then Enter
5. Confirm the report prints without crashing.
6. Confirm URLs, emails, technologies, API references, and data-sharing mentions appear where expected.

### `python quick_start.py`

Expected interaction:

1. Run `python quick_start.py`.
2. Press Enter when prompted to see the sample analysis.
3. Choose `n` when asked whether to analyse your own policy, unless you are deliberately testing full input mode.
4. Confirm the sample report prints and the script exits cleanly.

### `python batch_analyzer.py`

Expected interaction:

1. Run `python batch_analyzer.py`.
2. Choose option `1` to run the example batch analysis.
3. Confirm the comparison report prints.
4. Confirm generated JSON output appears only in `analysis_results/` and is not committed.

## Optional controlled-input smoke checks

Use these only in a local shell or Codex terminal when you want quick non-blocking checks:

```bash
printf 'ExampleCo\nExampleCo Privacy Policy\nWe use AWS, GitHub, Stripe, and SendGrid. Our REST API supports webhooks. Contact privacy@example.com or visit https://example.com/privacy. We may share data with payment processors.\n' | python policy_analyzer.py

printf '\nn\n' | python quick_start.py

printf '1\n' | python batch_analyzer.py
```

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
