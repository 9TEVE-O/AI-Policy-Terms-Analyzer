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

## Limitations and responsible use

This toolkit supports research and technical discovery. Its output is an aid to human analysis, not an authoritative interpretation of a policy, contract, privacy notice, law, regulation, or compliance obligation.

### False positives and false negatives

Detection is based on text patterns, configured terms, and document structure. The analyzer may:

- identify a technology, service, integration, or data-sharing relationship that the document does not actually establish;
- miss a relevant disclosure because it uses unfamiliar wording, appears only through context, or is contained in material not supplied to the analyzer;
- treat historical, hypothetical, excluded, or third-party language as a current operational statement;
- produce incomplete results from truncated, poorly extracted, scanned, translated, or malformed text.

Absence from the output does not prove absence from the source document. A detected item does not prove that the item is active, correctly described, legally significant, or applicable to a particular user.

### Not legal or compliance advice

The analyzer does not provide legal advice, compliance certification, regulatory interpretation, contractual approval, or a determination that an organisation meets any legal standard. Policy language must be reviewed against the complete source, applicable jurisdiction, current law, contractual context, and appropriate professional advice where required.

### Private and sensitive documents

The examples in this repository focus on public policy and terms documents. Before processing a private, confidential, privileged, personal, commercially sensitive, or regulated document:

- confirm that you have authority to use the document;
- understand where the text, configuration, logs, temporary files, and outputs will be stored;
- avoid sending raw content to external AI services or third-party systems unless that transfer is authorised and suitable safeguards are in place;
- minimise retained content and remove unnecessary personal or confidential information;
- apply the security, privacy, retention, access-control, and deletion requirements appropriate to the document.

This repository does not itself establish secure storage, confidential-computing guarantees, access governance, approved retention controls, or verified deletion.

### Human review is required

A human reviewer should compare material findings with the complete source document and preserve the supporting passage for any consequential conclusion. Review should consider context, definitions, exceptions, cross-references, dates, jurisdiction, document version, and whether linked or incorporated material was omitted.

Do not use analyzer output by itself to make legal, employment, financial, security, procurement, privacy, eligibility, enforcement, or other consequential decisions.

### Production-readiness boundary

The existence of code, tests, documentation, structured output, or automated workflows in this repository does not establish that the toolkit is production-ready, secure, accurate across document types, independently validated, continuously maintained, legally compliant, or suitable for unattended decision-making.

Before production use, the intended operator should define and test measurable accuracy requirements, supported document types, failure handling, security controls, dependency management, monitoring, audit logging, review gates, rollback procedures, and ownership for errors and updates.

See [docs/RESPONSIBLE_USE_EVIDENCE_RUN_2026-07-22.md](docs/RESPONSIBLE_USE_EVIDENCE_RUN_2026-07-22.md) for the controlled change record behind this section.

---

## Output

The analyzer produces structured findings that can be read directly or used as data for further analysis. It is intended for research, technical discovery, platform comparison, and workflow experimentation.