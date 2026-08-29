# Configuration

## PolicyAnalyzer configuration status

`PolicyAnalyzer` has **no configuration-file loader and no environment-variable
configuration system**. It also has no general-purpose CLI configuration
surface. Specifically, the following do not exist for `PolicyAnalyzer`:

- automatic discovery of `policyanalyzerrc.json` / `.yml` / `.yaml` / `.py`
  (or any other config file);
- `POLICY_ANALYZER_*` environment variables;
- `--config`, `--company`, `--output-format`, or `--save-to` configuration flags;
- a `config=` argument on `PolicyAnalyzer()`;
- output-format switching (`text` / `json` / `yaml`), batch auto-save options,
  or result filtering driven by configuration.

If older documentation or generated code suggests those features exist, treat
it as stale unless the implementation and tests establish otherwise.

## Controlled site-analysis command

The repository includes a separate bounded URL-only runner:

```bash
python controlled_policy_analysis.py https://example.com
python controlled_policy_analysis.py https://example.com --limit 5
```

The runner accepts:

- a required homepage URL; and
- optional `--limit`, which only caps the number of discovered policy documents
  sent through the analyser.

This narrow runner is not a general configuration system. It is repository-local
in v0.1 rather than registered as an installed console script. Its discovery
scope is intentionally constrained to one-hop links present on the supplied
homepage and qualifying first-party hosts. See `controlled_policy_analysis.py`
and `CLAUDE.md` for the current boundaries.

## What is supported for detection customisation

`PolicyAnalyzer` stores its keyword lists as plain public instance attributes.
`tech_keywords` is read each time `analyze()` runs, so it can be changed in
Python before analysis:

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
`docs/examples/fintech-analysis.json` are **not read by the application**.
There is no loader that consumes them. They are illustrative reference snippets
showing keyword groupings for particular use cases. If useful, copy the keyword
lists into your own Python setup. The `output` section in each file does not
correspond to supported automatic behaviour and should be ignored.

## See also

- [README.md](../README.md) - Main documentation
- [USER_GUIDE.md](../USER_GUIDE.md) - User guide for beginners
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Command quick reference
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Technical details
