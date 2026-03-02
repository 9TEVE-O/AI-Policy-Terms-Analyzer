# Subzteveø AI Operator OS — Architecture Guide

## Overview

The **Subzteveø AI Operator OS** is a three-tier AI orchestration framework that
transforms isolated AI experiments into a unified, secure, and scalable system.
It manages domain-specific agents and workflows through a layered architecture
borrowed from AIOS research and industry best practices, ensuring modularity,
security, and efficient resource use.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                            │
│  GovernmentCompliance │ MusicProduction │ Research │ Workflow │ PromptLib │
├─────────────────────────────────────────────────────────────────────┤
│                          KERNEL LAYER                               │
│  Scheduler │ ContextMgr │ MemoryMgr │ LLMCore │ AccessMgr │ Eval   │
├─────────────────────────────────────────────────────────────────────┤
│                      DATA / HARDWARE LAYER                          │
│    RelationalStore │ VectorStore │ FileStore │ Compute Resources    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tier 1 — Data / Hardware Layer

Integrates storage backends and compute resources to support all layers above.

| Component | Description |
|-----------|-------------|
| `RelationalStore` | Dict-of-dicts in-process store; compatible interface for SQL backends |
| `VectorStore` | Bag-of-words vector index with cosine similarity search; pluggable for FAISS/Pinecone |
| `FileStore` | In-memory file store; interface compatible with local filesystem or cloud object storage |
| `DataLayer` | Aggregates all stores; exposes compute resource metadata per deployment mode |

### Deployment Modes

| Mode | Primary Compute | Secondary Compute |
|------|----------------|------------------|
| `local` | Local CPU/GPU | — |
| `remote_kernel` | Local CPU/GPU | Remote kernel server |
| `personal_remote` | Personal cloud VM | Local CPU |
| `hybrid` | Local CPU/GPU | Cloud compute |

---

## Tier 2 — Kernel Layer

Modular services that coordinate agents, manage resources, enforce security,
and log everything for accountability.

### Scheduler

Manages task queuing and execution order. Three policies are supported:

- **`fifo`** (default) — first-in, first-out
- **`priority`** — highest numeric priority runs first
- **`round_robin`** — agents share the queue in rotation

```python
from ai_operator_os import Scheduler

s = Scheduler(policy='priority')
s.submit('task-1', 'research_agent', {'prompt': '...'}, priority=10)
s.submit('task-2', 'compliance_agent', {'prompt': '...'}, priority=5)
task = s.next_task()   # returns task-1 (higher priority)
s.mark_done(task, result={...})
```

### Context Manager

Maintains a sliding window of messages per session, enabling agents to
reference prior turns without unbounded memory growth.

```python
from ai_operator_os import ContextManager

cm = ContextManager(window_size=20)
cm.push('session-id', 'user', 'What are the GDPR obligations?')
cm.push('session-id', 'assistant', 'GDPR requires ...')
context = cm.get_context('session-id')
```

### Memory Manager

Provides two memory tiers:

- **Short-term** — scoped to a session, in-process, volatile
- **Long-term** — persisted in `RelationalStore`; semantically searchable via `VectorStore`

```python
from ai_operator_os import MemoryManager, DataLayer

mm = MemoryManager(DataLayer())
mm.remember_short('sess1', 'current_topic', 'privacy')
mm.remember_long('research', 'gdpr_doc', {'title': 'GDPR Overview', ...})
results = mm.search_long('data protection rights', top_k=5)
```

### LLM Core (Unified LLM-Core Abstraction)

Provider-agnostic router for language model calls. Ships with a built-in
`mock` provider for offline testing; real providers (OpenAI, Anthropic,
Gemini, local Ollama, etc.) can be registered as callables.

```python
from ai_operator_os import LLMCore

llm = LLMCore()

# Register a real provider
import openai
def openai_handler(prompt, **kwargs):
    r = openai.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return r.choices[0].message.content

llm.register_provider('openai', openai_handler, set_default=True)
result = llm.complete("Summarise this policy...")
```

### Tool & Access Manager (RBAC)

Role-based access control for tools and capabilities. Every agent is assigned
a role; access checks are logged for audit.

| Built-in Role | Permitted Tools |
|---------------|-----------------|
| `admin` | All tools |
| `researcher` | `policy_analyze`, `batch_analyze`, `vector_search`, `llm_complete` |
| `operator` | `policy_analyze`, `llm_complete`, `workflow_run` |
| `read_only` | `policy_analyze` |

```python
from ai_operator_os import ToolAccessManager

tam = ToolAccessManager()
tam.define_role('analyst', ['policy_analyze', 'vector_search'])
tam.assign_role('my_agent', 'analyst')
tam.check_access('my_agent', 'policy_analyze')  # True
tam.check_access('my_agent', 'file_write')       # False
print(tam.audit_log)
```

### Evaluation Engine

Continuously scores agent responses on three metrics:

| Metric | Description | Range |
|--------|-------------|-------|
| `hallucination_frequency` | Fraction of sentences with uncertain/speculative language | 0–1 (lower is better) |
| `context_relevance` | Jaccard token-overlap between prompt and response | 0–1 (higher is better) |
| `correctness` | User-confirmed correct fraction of responses | 0–1 (higher is better) |

```python
from ai_operator_os import EvaluationEngine

ee = EvaluationEngine()
ee.evaluate('my_agent', prompt='What is GDPR?',
            response='GDPR is ...', correct=True)
print(ee.aggregate('my_agent'))
print(ee.report())
```

---

## Tier 3 — Application Layer

Domain-specific agents that run on top of the kernel services.

### GovernmentComplianceAgent

Scans documents for regulatory obligations across five categories:
`data_protection`, `accessibility`, `security`, `procurement`, `ai_policy`.

Frameworks detected include GDPR, CCPA, HIPAA, ADA, WCAG, FISMA, NIST,
FedRAMP, FAR/DFARS, and Executive Order 14110.

```python
os = AIOperatorOS()
result = os.run('government_compliance_agent',
                'We comply with GDPR and have FedRAMP authorization.')
print(result['compliance_findings'])
# {'data_protection': ['gdpr'], 'security': ['fedramp']}
```

### MusicProductionAgent

Identifies music-production context (genres, DAW tools, production elements,
AI music tools) and generates workflow suggestions.

```python
result = os.run('music_production_agent',
                'Hip hop beat at 90 BPM in Ableton, heavy reverb.')
print(result['music_context'])
# {'genres': ['hip hop'], 'production_tools': ['ableton'],
#  'elements': ['bpm', 'reverb']}
```

### ResearchAgent

Wraps the `PolicyAnalyzer` to analyse policy documents, indexes the results
in the vector store for semantic recall, and persists structured findings in
long-term memory.

```python
result = os.run('research_agent',
                policy_text,
                company_name='Acme Corp')
print(result['analysis']['technologies_detected'])
```

### WorkflowDesigner

Lets users define named multi-step workflows as sequences of agent prompts.
Workflows are persisted in long-term memory and can be scheduled via the
kernel Scheduler.

```python
wd = os.application.workflow
wd.define_workflow('compliance_pipeline', steps=[
    {'agent': 'research_agent',    'prompt': 'Analyse policy for {company}'},
    {'agent': 'government_compliance_agent', 'prompt': 'Check compliance for {company}'},
])
tasks = wd.schedule_workflow('compliance_pipeline', variables={'company': 'Acme'})
```

### PromptLibrary

Stores, retrieves, fills, and semantically searches named prompt templates.
Ships with five built-in templates: `policy_summary`, `compliance_check`,
`tech_extraction`, `music_brief`, `research_query`.

```python
pl = os.application.prompts
filled = pl.fill('policy_summary', text='Our privacy policy states...')
results = pl.search('compliance regulatory', top_k=3)
```

---

## Quick Start

```python
from ai_operator_os import AIOperatorOS

# Initialise with local deployment
os_instance = AIOperatorOS(deployment_mode='local')

# Analyse a policy document
result = os_instance.run(
    'research_agent',
    'We use AWS and OpenAI. Contact privacy@example.com',
    company_name='Example Corp'
)
print(result['response'])

# Check compliance
result = os_instance.run(
    'government_compliance_agent',
    'Our platform is GDPR and HIPAA compliant with FedRAMP authorization.'
)
print(result['compliance_findings'])

# View evaluation metrics
print(os_instance.evaluation_report())

# View system status as JSON
print(os_instance.export_status_json())
```

---

## Implementation Roadmap

1. **Data Infrastructure** — swap in-memory stores for production backends
   (PostgreSQL, Pinecone/Weaviate, S3-compatible object storage)
2. **Agent Frameworks** — integrate LangChain, LlamaIndex, or AutoGen for
   richer agent orchestration
3. **LLM Providers** — register real providers (OpenAI, Anthropic, Gemini,
   local Ollama) via `register_llm_provider`
4. **Domain Agents** — extend `GovernmentComplianceAgent` keyword dictionaries
   and `MusicProductionAgent` tool lists as your use cases evolve
5. **Dashboard** — build a web UI on top of `export_status_json()` and the
   evaluation report
6. **Security Hardening** — replace in-process RBAC with a dedicated
   identity provider; add TLS for remote kernel connections
7. **Evaluation Loop** — feed `correct=True/False` labels from user feedback
   back into `EvaluationEngine.evaluate()` to improve `correctness` tracking

---

## Deployment Mode Details

### `local`
All layers run in-process on local hardware. Ideal for development and
single-user scenarios. No network dependencies.

### `remote_kernel`
Kernel services run on a remote server while agents execute locally. Enables
shared scheduling, memory, and evaluation across multiple clients. Requires
a network connection to the kernel server.

### `personal_remote`
All layers run on a personal cloud VM with a local CPU fallback. Suitable for
resource-intensive workloads that exceed local hardware capacity.

### `hybrid`
Agents execute locally; kernel services and data layer can use cloud compute
when available. Provides the best balance of responsiveness and scalability.

---

## Security Notes

- RBAC is enforced for every agent `run()` call via `ToolAccessManager`
- All access decisions are written to an immutable audit log
- The `EvaluationEngine` flags uncertain/speculative responses via
  `hallucination_frequency` to surface low-confidence outputs
- No external network requests are made by default (all LLM calls go through
  the mock provider unless a real provider is registered)
