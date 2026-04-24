# AI Policy & Terms Analyzer

AI Policy & Terms Analyzer is a Python toolkit for extracting useful technical and operational signals from public policy documents, terms of service, and privacy pages. It helps turn dense legal text into structured findings: technologies mentioned, domains referenced, integrations disclosed, APIs named, automation language, and data-sharing patterns.

## What it demonstrates

- Python-first document analysis and text extraction workflows
- Structured parsing of long policy and terms documents
- Technology, service, domain, and integration detection
- Report formatting for both human review and JSON-based downstream use
- Companion utilities for key-point condensation and batch analysis

---

## Quick start

```bash
# Run the interactive analyzer
python policy_analyzer.py

# Run examples
python example_usage.py

# Run the quick start guide
python quick_start.py
```

---

## Basic usage

```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()

policy_text = """Paste policy text here..."""
results = analyzer.analyze(policy_text, "Company Name")

print(analyzer.format_report(results))
print(results["urls_found"])
print(results["technologies_detected"])
```

---

## Configuration

Use a local config file to customise detection behaviour.

```bash
cp docs/examples/policyanalyzerrc.json .
python policy_analyzer.py --config my_custom_config.json
```

See [docs/configuration.md](docs/configuration.md) for detailed options.

---

## Features

| Feature | Description |
|---|---|
| URL and domain extraction | Finds URLs and domain names mentioned in policy text |
| Technology detection | Identifies cloud platforms, languages, frameworks, databases, and AI tools |
| Service discovery | Detects payment, analytics, email, support, and communication services |
| API and integration detection | Finds references to APIs, webhooks, GraphQL, REST, and connected systems |
| Automation-language detection | Identifies references to bots, crawlers, chatbots, and automated systems |
| Data-sharing analysis | Extracts language about what data is shared and with whom |
| Key point condenser | Produces an abstract, extractive summary, and section outline |
| Batch analysis | Processes multiple company policies into structured output |

---

## Key point condenser

```python
from key_point_condenser import KeyPointCondenser

condenser = KeyPointCondenser()

result = condenser.condense(
    """Paste long policy text here...""",
    title="Company Policy"
)

print(condenser.format_report(result))
print(result["abstract"])
print(result["summary"])
print(result["outline"])
```

Run interactively:

```bash
python key_point_condenser.py
python test_key_point_condenser.py
```

---

## Batch processing

```python
from policy_analyzer import PolicyAnalyzer
import json

companies = {
    "Company A": "policy text...",
    "Company B": "policy text...",
    "Company C": "policy text..."
}

analyzer = PolicyAnalyzer()
results = {}

for company, policy in companies.items():
    results[company] = analyzer.analyze(policy, company)

with open("all_companies_analysis.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## Files

| File | Purpose |
|---|---|
| `policy_analyzer.py` | Main analyzer and `PolicyAnalyzer` class |
| `key_point_condenser.py` | Summary and outline utility for long documents |
| `example_usage.py` | Usage examples |
| `quick_start.py` | Interactive quick start flow |
| `batch_analyzer.py` | Batch processing utility |
| `test_google_cloud.py` | Detection tests for Google Cloud language |
| `test_ai_operator_os.py` | Tests for the AI Operator OS module |
| `requirements.txt` | Python dependencies |
| `docs/configuration.md` | Configuration documentation |
| `docs/examples/` | Example config files |

---

## AI Operator OS module

This repository also includes `ai_operator_os.py`, a three-tier orchestration experiment for routing specialised AI tasks through application, kernel, and data layers.

```text
Application Layer   -> Research | Workflow | MusicProduction | PromptLib
Kernel Layer        -> Scheduler | ContextMgr | MemoryMgr | LLMCore | Evaluation
Data/Hardware Layer -> RelationalStore | VectorStore | FileStore | Compute Resources
```

Run the demo and tests:

```bash
python ai_operator_os.py
python test_ai_operator_os.py
```

See [docs/ai_operator_os_architecture.md](docs/ai_operator_os_architecture.md) for details.

---

## Best-use workflow

1. Copy the full terms or privacy policy text.
2. Run `python policy_analyzer.py`.
3. Paste the text into the interactive prompt.
4. Review the formatted report.
5. Save JSON output for comparison, research, or later analysis.

---

## Output

The analyzer produces structured findings that can be read directly or used as data for further analysis. It is intended for research, technical discovery, platform comparison, and workflow experimentation.
