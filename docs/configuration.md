# Configuration

## Current status

`PolicyAnalyzer` has **no configuration-file loader, no environment-variable
configuration system, and no CLI flags**. Specifically, none of the
following exist in this codebase:

- Automatic discovery of `policyanalyzerrc.json` / `.yml` / `.yaml` / `.py`
  (or any other config file)
- `POLICY_ANALYZER_*` environment variables
- `--config`, `--company`, `--output-format`, or `--save-to` CLI flags
- A `config=` argument on `PolicyAnalyzer()`
- Output-format switching (`text` / `json` / `yaml`), batch auto-save
  options, or result filtering driven by configuration

If you have seen documentation, examples, or generated code suggesting
otherwise, they describe functionality that is not implemented here.

## What is actually supported: direct attribute customisation

`PolicyAnalyzer` stores its keyword lists as plain public instance
attributes, set in `__init__`. `tech_keywords` in particular is read fresh
every time `analyze()` runs, so you can edit it in Python before calling
`analyze()` and the change takes effect immediately — no config file or
re-instantiation required:

```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
analyzer.tech_keywords['blockchain'] = ['ethereum', 'bitcoin', 'web3']

results = analyzer.analyze(policy_text, "Company Name")
print(analyzer.format_report(results))
```

`tech_keywords` is a dict of category → list of keyword strings; add a new
category or extend an existing one the same way.

## Reference keyword lists (`docs/examples/`)

`docs/examples/dating-site-bot-detection.json` and
`docs/examples/fintech-analysis.json` are **not read by the application** —
there is no loader that consumes them. They are illustrative reference
snippets showing keyword groupings for particular use cases (dating-site
bot/AI detection, fintech-specific platforms and compliance terms). If one
is useful to you, copy the keyword lists under its `analyzer.tech_keywords`
key into your own script as shown above. The `output` section in each file
does not correspond to any supported behaviour and should be ignored.

## See also

- [README.md](../README.md) - Main documentation
- [USER_GUIDE.md](../USER_GUIDE.md) - User guide for beginners
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Command quick reference
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Technical details
