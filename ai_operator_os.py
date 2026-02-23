#!/usr/bin/env python3
"""
Subzteveø AI Operator OS

A three-tier AI orchestration framework that manages domain-specific agents
and workflows through a layered architecture:

  Application Layer:   Domain agents (government compliance, music production,
                       research, workflow designer, prompt library)
  Kernel Layer:        Core services (scheduling, context management, memory
                       and storage, unified LLM-core abstraction, tool and
                       access management, continuous evaluation)
  Data/Hardware Layer: Storage backends (relational DB, vector DB, file
                       storage) and compute resources (local, cloud)

Supported deployment modes: local, remote_kernel, personal_remote, hybrid

Reference: AIOS research and industry best practices for modular AI systems.
"""

import json
import re
import uuid
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEPLOYMENT_MODES = ('local', 'remote_kernel', 'personal_remote', 'hybrid')

EVALUATION_METRICS = ('hallucination_frequency', 'context_relevance', 'correctness')

# Words that may signal speculative or uncertain language (used by evaluation)
_UNCERTAINTY_TOKENS = {
    'maybe', 'perhaps', 'possibly', 'might', 'could', 'unsure', 'unclear',
    'probably', 'apparently', 'seemingly', 'i think', 'i believe', 'not sure',
    'hallucinate', 'fabricate', 'made up', 'uncertain'
}


# ---------------------------------------------------------------------------
# Data / Hardware Layer
# ---------------------------------------------------------------------------

class RelationalStore:
    """Lightweight in-process relational store (dict-of-dicts per table)."""

    def __init__(self):
        self._tables: Dict[str, Dict[str, Dict]] = defaultdict(dict)

    def insert(self, table: str, record_id: str, data: Dict) -> None:
        """Insert or replace a record."""
        self._tables[table][record_id] = dict(data)

    def get(self, table: str, record_id: str) -> Optional[Dict]:
        """Retrieve a record by id; returns None if not found."""
        return self._tables[table].get(record_id)

    def query(self, table: str, **filters) -> List[Dict]:
        """Return all records in a table matching all provided key=value filters."""
        results = []
        for record in self._tables[table].values():
            if all(record.get(k) == v for k, v in filters.items()):
                results.append(dict(record))
        return results

    def delete(self, table: str, record_id: str) -> bool:
        """Delete a record; returns True if it existed."""
        return self._tables[table].pop(record_id, None) is not None


class VectorStore:
    """Minimal vector store with cosine-similarity search over bag-of-words vectors."""

    def __init__(self):
        self._records: Dict[str, Tuple[str, Dict[str, float], Dict]] = {}

    @staticmethod
    def _vectorise(text: str) -> Dict[str, float]:
        """Convert text to a normalised bag-of-words vector."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        counts: Dict[str, float] = defaultdict(float)
        for t in tokens:
            counts[t] += 1.0
        norm = (sum(v * v for v in counts.values()) ** 0.5) or 1.0
        return {k: v / norm for k, v in counts.items()}

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        """Dot product of two pre-normalised vectors."""
        return sum(a.get(k, 0.0) * v for k, v in b.items())

    def upsert(self, doc_id: str, text: str, metadata: Optional[Dict] = None) -> None:
        """Index or replace a document."""
        self._records[doc_id] = (text, self._vectorise(text), metadata or {})

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Return the top-k most similar documents to the query."""
        q_vec = self._vectorise(query)
        scored = [
            {'id': doc_id, 'text': text, 'score': self._cosine(q_vec, vec),
             'metadata': meta}
            for doc_id, (text, vec, meta) in self._records.items()
        ]
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]

    def delete(self, doc_id: str) -> bool:
        """Remove a document; returns True if it existed."""
        return self._records.pop(doc_id, None) is not None


class FileStore:
    """In-memory file store; can be swapped for a real filesystem backend."""

    def __init__(self):
        self._files: Dict[str, bytes] = {}

    def write(self, path: str, content: bytes) -> None:
        """Write (or overwrite) a file at the given path."""
        self._files[path] = content

    def read(self, path: str) -> Optional[bytes]:
        """Read a file; returns None if path does not exist."""
        return self._files.get(path)

    def delete(self, path: str) -> bool:
        """Delete a file; returns True if it existed."""
        return self._files.pop(path, None) is not None

    def list_paths(self, prefix: str = '') -> List[str]:
        """List all stored paths that start with prefix."""
        return [p for p in self._files if p.startswith(prefix)]


class DataLayer:
    """
    Data / Hardware Layer.

    Aggregates the relational store, vector store, file store, and exposes
    basic compute-resource metadata for local and cloud targets.
    """

    def __init__(self, deployment_mode: str = 'local'):
        if deployment_mode not in DEPLOYMENT_MODES:
            raise ValueError(
                f"deployment_mode must be one of {DEPLOYMENT_MODES}, "
                f"got '{deployment_mode}'"
            )
        self.deployment_mode = deployment_mode
        self.relational = RelationalStore()
        self.vector = VectorStore()
        self.files = FileStore()

    @property
    def compute_resources(self) -> Dict[str, str]:
        """Describe the compute resources available for this deployment mode."""
        resources = {
            'local': {'primary': 'local CPU/GPU', 'secondary': None},
            'remote_kernel': {'primary': 'local CPU/GPU', 'secondary': 'remote kernel server'},
            'personal_remote': {'primary': 'personal cloud VM', 'secondary': 'local CPU'},
            'hybrid': {'primary': 'local CPU/GPU', 'secondary': 'cloud compute'},
        }
        return resources[self.deployment_mode]


# ---------------------------------------------------------------------------
# Kernel Layer — individual services
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Kernel service: task scheduling.

    Supports three scheduling policies:
      - 'fifo'     : first-in first-out (default)
      - 'priority' : highest numeric priority runs first
      - 'round_robin': agents share the queue in rotation
    """

    def __init__(self, policy: str = 'fifo'):
        if policy not in ('fifo', 'priority', 'round_robin'):
            raise ValueError(f"Unknown scheduling policy '{policy}'")
        self.policy = policy
        self._queue: deque = deque()
        self._completed: List[Dict] = []

    def submit(self, task_id: str, agent_name: str, payload: Any,
               priority: int = 0) -> Dict:
        """Enqueue a task for an agent."""
        task = {
            'task_id': task_id,
            'agent_name': agent_name,
            'payload': payload,
            'priority': priority,
            'submitted_at': datetime.now().isoformat(),
            'status': 'queued',
        }
        self._queue.append(task)
        return task

    def next_task(self) -> Optional[Dict]:
        """Return and remove the next task according to the scheduling policy."""
        if not self._queue:
            return None
        if self.policy == 'priority':
            self._queue = deque(
                sorted(self._queue, key=lambda t: t['priority'], reverse=True)
            )
        return self._queue.popleft()

    def mark_done(self, task: Dict, result: Any = None) -> None:
        """Record a completed task."""
        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        task['result'] = result
        self._completed.append(task)

    @property
    def queue_length(self) -> int:
        """Number of queued tasks."""
        return len(self._queue)

    @property
    def completed_tasks(self) -> List[Dict]:
        """Immutable view of completed tasks."""
        return list(self._completed)


class ContextManager:
    """
    Kernel service: per-session context management.

    Maintains a sliding window of messages per session so that agents can
    reference prior turns without unbounded memory growth.
    """

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._sessions: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.window_size)
        )

    def push(self, session_id: str, role: str, content: str) -> None:
        """Append a message to a session's context window."""
        self._sessions[session_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
        })

    def get_context(self, session_id: str) -> List[Dict]:
        """Return the current context window for a session."""
        return list(self._sessions[session_id])

    def clear(self, session_id: str) -> None:
        """Clear a session's context window."""
        self._sessions[session_id].clear()

    def active_sessions(self) -> List[str]:
        """List all session IDs that have at least one message."""
        return [sid for sid, ctx in self._sessions.items() if ctx]


class MemoryManager:
    """
    Kernel service: persistent memory and storage management.

    Provides two stores:
      - short-term: scoped to a session, volatile
      - long-term:  persisted across sessions via the DataLayer
    """

    def __init__(self, data_layer: DataLayer):
        self._data = data_layer
        self._short_term: Dict[str, Dict[str, Any]] = defaultdict(dict)

    # Short-term (in-process) memory
    def remember_short(self, session_id: str, key: str, value: Any) -> None:
        """Store a key/value pair in short-term memory for a session."""
        self._short_term[session_id][key] = value

    def recall_short(self, session_id: str, key: str,
                     default: Any = None) -> Any:
        """Retrieve a value from short-term memory."""
        return self._short_term[session_id].get(key, default)

    def forget_short(self, session_id: str) -> None:
        """Clear short-term memory for a session."""
        self._short_term.pop(session_id, None)

    # Long-term (data-layer) memory
    def remember_long(self, namespace: str, key: str, value: Any) -> None:
        """Persist a key/value pair in long-term relational storage."""
        self._data.relational.insert(
            'long_term_memory', f'{namespace}::{key}',
            {'namespace': namespace, 'key': key, 'value': value,
             'updated_at': datetime.now().isoformat()}
        )

    def recall_long(self, namespace: str, key: str,
                    default: Any = None) -> Any:
        """Retrieve a persisted value from long-term storage."""
        record = self._data.relational.get(
            'long_term_memory', f'{namespace}::{key}'
        )
        return record['value'] if record else default

    def search_long(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search over vector-indexed long-term memories."""
        return self._data.vector.search(query, top_k=top_k)

    def index_memory(self, doc_id: str, text: str,
                     metadata: Optional[Dict] = None) -> None:
        """Add a document to the vector index for semantic recall."""
        self._data.vector.upsert(doc_id, text, metadata)


class LLMCore:
    """
    Kernel service: unified LLM-core abstraction.

    Acts as a provider-agnostic router for language model calls. Concrete
    provider adapters can be registered at runtime; the core selects the
    best available provider for each request.

    Out-of-the-box it operates in 'mock' mode so the OS can run without
    any external dependencies — useful for testing, demos and offline use.
    """

    def __init__(self):
        self._providers: Dict[str, Callable] = {}
        self._default_provider: Optional[str] = None

    def register_provider(self, name: str, handler: Callable,
                          set_default: bool = False) -> None:
        """
        Register a provider handler.

        The handler must be callable with signature:
            handler(prompt: str, **kwargs) -> str
        """
        self._providers[name] = handler
        if set_default or self._default_provider is None:
            self._default_provider = name

    def complete(self, prompt: str, provider: Optional[str] = None,
                 **kwargs) -> Dict:
        """
        Send a completion request to a provider.

        Args:
            prompt:   The input prompt string.
            provider: Provider name; falls back to the default provider, then
                      to a built-in mock that returns a structured placeholder.
            **kwargs: Extra arguments forwarded to the provider handler.

        Returns:
            Dict with keys 'response', 'provider', 'prompt_tokens',
            'completion_tokens'.
        """
        chosen = provider or self._default_provider
        if chosen and chosen in self._providers:
            response_text = self._providers[chosen](prompt, **kwargs)
        else:
            # Built-in mock — no external dependency required
            response_text = (
                f"[mock response to: {prompt[:80]}{'...' if len(prompt) > 80 else ''}]"
            )
            chosen = 'mock'

        return {
            'response': response_text,
            'provider': chosen,
            'prompt_tokens': len(prompt.split()),
            'completion_tokens': len(response_text.split()),
        }

    @property
    def available_providers(self) -> List[str]:
        """Names of all registered providers."""
        return list(self._providers.keys())


class ToolAccessManager:
    """
    Kernel service: RBAC-based tool and access management.

    Roles are assigned to agents/users and each role grants access to a set
    of named tools or capabilities. Access checks are logged for audit.
    """

    def __init__(self):
        self._roles: Dict[str, set] = defaultdict(set)         # role -> tools
        self._principals: Dict[str, str] = {}                  # principal -> role
        self._audit_log: List[Dict] = []

    def define_role(self, role: str, tools: List[str]) -> None:
        """Create or extend a role with a list of permitted tools."""
        self._roles[role].update(tools)

    def assign_role(self, principal: str, role: str) -> None:
        """Assign a role to a principal (agent name or user id)."""
        self._principals[principal] = role

    def check_access(self, principal: str, tool: str) -> bool:
        """Return True if the principal's role grants access to the tool."""
        role = self._principals.get(principal)
        allowed = role is not None and tool in self._roles.get(role, set())
        self._audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'principal': principal,
            'tool': tool,
            'role': role,
            'allowed': allowed,
        })
        return allowed

    def permitted_tools(self, principal: str) -> List[str]:
        """List all tools the principal is permitted to use."""
        role = self._principals.get(principal)
        return sorted(self._roles.get(role, set()))

    @property
    def audit_log(self) -> List[Dict]:
        """Immutable view of the access audit log."""
        return list(self._audit_log)


class EvaluationEngine:
    """
    Kernel service: continuous agent evaluation.

    Tracks three metrics per agent:
      - hallucination_frequency : rate of uncertain/speculative language
      - context_relevance       : overlap between input and output tokens
      - correctness             : confirmed-correct fraction of responses
    """

    def __init__(self):
        self._records: Dict[str, List[Dict]] = defaultdict(list)

    def evaluate(self, agent_name: str, prompt: str,
                 response: str, correct: Optional[bool] = None) -> Dict:
        """
        Score a single agent response and record it.

        Args:
            agent_name: Identifier for the agent being evaluated.
            prompt:     The input given to the agent.
            response:   The agent's output.
            correct:    Optional ground-truth label (True/False/None).

        Returns:
            Dict with individual metric scores and a timestamp.
        """
        scores = {
            'hallucination_frequency': self._score_hallucination(response),
            'context_relevance': self._score_relevance(prompt, response),
            'correctness': 1.0 if correct else (0.0 if correct is False else None),
        }
        record = {
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'scores': scores,
        }
        self._records[agent_name].append(record)
        return record

    def aggregate(self, agent_name: str) -> Dict[str, Optional[float]]:
        """
        Return average metric values across all recorded evaluations for an agent.

        Returns None for a metric if no labelled data is available.
        """
        records = self._records.get(agent_name, [])
        if not records:
            return {m: None for m in EVALUATION_METRICS}

        agg: Dict[str, List[float]] = defaultdict(list)
        for r in records:
            for metric, val in r['scores'].items():
                if val is not None:
                    agg[metric].append(val)

        return {
            m: (sum(vals) / len(vals) if vals else None)
            for m, vals in agg.items()
        }

    def report(self) -> Dict[str, Dict]:
        """Return aggregated evaluation metrics for all agents."""
        return {name: self.aggregate(name) for name in self._records}

    # ------------------------------------------------------------------
    # Private scoring helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_hallucination(text: str) -> float:
        """
        Heuristic: fraction of sentences containing uncertainty tokens.

        Lower is better (0.0 = no uncertain language detected).
        """
        sentences = re.split(r'[.!?]+', text.lower())
        if not sentences:
            return 0.0
        uncertain = sum(
            1 for s in sentences
            if any(tok in s for tok in _UNCERTAINTY_TOKENS)
        )
        return uncertain / len(sentences)

    @staticmethod
    def _score_relevance(prompt: str, response: str) -> float:
        """
        Heuristic: token-overlap Jaccard similarity between prompt and response.

        Higher is better (1.0 = identical token sets).
        """
        p_tokens = set(re.findall(r'\b\w+\b', prompt.lower()))
        r_tokens = set(re.findall(r'\b\w+\b', response.lower()))
        if not p_tokens and not r_tokens:
            return 1.0
        if not p_tokens or not r_tokens:
            return 0.0
        return len(p_tokens & r_tokens) / len(p_tokens | r_tokens)


class KernelLayer:
    """
    Kernel Layer — aggregates all kernel services.

    Provides a single access point for the application layer and data layer
    to interact with core OS services.
    """

    def __init__(self, data_layer: DataLayer,
                 scheduler_policy: str = 'fifo',
                 context_window: int = 20):
        self.scheduler = Scheduler(policy=scheduler_policy)
        self.context = ContextManager(window_size=context_window)
        self.memory = MemoryManager(data_layer)
        self.llm = LLMCore()
        self.access = ToolAccessManager()
        self.evaluation = EvaluationEngine()

        # Seed default roles
        self.access.define_role('admin', [
            'policy_analyze', 'batch_analyze', 'vector_search',
            'file_read', 'file_write', 'llm_complete', 'workflow_run',
        ])
        self.access.define_role('researcher', [
            'policy_analyze', 'batch_analyze', 'vector_search', 'llm_complete',
        ])
        self.access.define_role('operator', [
            'policy_analyze', 'llm_complete', 'workflow_run',
        ])
        self.access.define_role('read_only', ['policy_analyze'])


# ---------------------------------------------------------------------------
# Application Layer — domain-specific agents
# ---------------------------------------------------------------------------

class Agent:
    """
    Base class for all application-layer agents.

    Every agent has:
      - a unique name
      - a reference to the KernelLayer
      - a session id used by context and memory services
    """

    def __init__(self, name: str, kernel: KernelLayer):
        self.name = name
        self.kernel = kernel
        self.session_id = str(uuid.uuid4())

    def run(self, prompt: str, **kwargs) -> Dict:
        """
        Execute the agent with a prompt.

        Subclasses should override `_handle` to provide domain logic.
        The base implementation checks access, calls `_handle`, evaluates
        the response, and stores the turn in context.
        """
        tool = self._required_tool()
        if not self.kernel.access.check_access(self.name, tool):
            return {
                'agent': self.name,
                'error': f"Access denied: '{self.name}' cannot use tool '{tool}'",
            }

        self.kernel.context.push(self.session_id, 'user', prompt)
        result = self._handle(prompt, **kwargs)
        response_text = result.get('response', '')
        self.kernel.context.push(self.session_id, 'assistant', response_text)
        self.kernel.evaluation.evaluate(self.name, prompt, response_text)
        return result

    def _required_tool(self) -> str:
        """Return the tool name required to run this agent."""
        return 'llm_complete'

    def _handle(self, prompt: str, **kwargs) -> Dict:
        """Domain-specific logic.  Subclasses must override this."""
        result = self.kernel.llm.complete(prompt, **kwargs)
        return {'agent': self.name, 'response': result['response'],
                'provider': result['provider']}

    @property
    def context_window(self) -> List[Dict]:
        """Current context window for this agent's session."""
        return self.kernel.context.get_context(self.session_id)


class GovernmentComplianceAgent(Agent):
    """
    Application-layer agent: Government Compliance.

    Specialises in analysing policy and regulatory documents for compliance
    requirements, flagging obligations, deadlines, and risk areas.
    """

    # Compliance-relevant keyword categories
    COMPLIANCE_KEYWORDS = {
        'data_protection': [
            'gdpr', 'ccpa', 'hipaa', 'ferpa', 'coppa', 'privacy',
            'data protection', 'personal data', 'sensitive data',
        ],
        'accessibility': [
            'ada', 'wcag', 'section 508', 'accessibility', 'disability',
        ],
        'security': [
            'fisma', 'nist', 'fedramp', 'security clearance', 'cybersecurity',
            'encryption', 'zero trust',
        ],
        'procurement': [
            'far', 'dfars', 'contract', 'solicitation', 'rfp', 'rfi',
            'procurement', 'acquisition', 'government contract',
        ],
        'ai_policy': [
            'executive order', 'eo 14110', 'ai governance', 'responsible ai',
            'algorithmic accountability', 'bias audit',
        ],
    }

    def __init__(self, kernel: KernelLayer):
        super().__init__('government_compliance_agent', kernel)
        kernel.access.assign_role(self.name, 'researcher')

    def _required_tool(self) -> str:
        return 'policy_analyze'

    def _handle(self, prompt: str, **kwargs) -> Dict:
        """Scan text for compliance obligations and return a structured report."""
        text_lower = prompt.lower()
        findings: Dict[str, List[str]] = {}
        for category, keywords in self.COMPLIANCE_KEYWORDS.items():
            hits = [kw for kw in keywords if kw in text_lower]
            if hits:
                findings[category] = hits

        llm_result = self.kernel.llm.complete(prompt, **kwargs)
        return {
            'agent': self.name,
            'response': llm_result['response'],
            'compliance_findings': findings,
            'categories_flagged': list(findings.keys()),
            'provider': llm_result['provider'],
        }


class MusicProductionAgent(Agent):
    """
    Application-layer agent: Music Production Assistant.

    Assists with music-production workflows: genre/style detection in text,
    task management, equipment and software mentions, and creative prompts.
    """

    MUSIC_KEYWORDS = {
        'genres': [
            'hip hop', 'rap', 'r&b', 'jazz', 'classical', 'electronic',
            'edm', 'house', 'techno', 'rock', 'pop', 'soul', 'gospel',
            'afrobeats', 'reggae', 'country',
        ],
        'production_tools': [
            'ableton', 'fl studio', 'logic pro', 'pro tools', 'reason',
            'studio one', 'cubase', 'reaper', 'daw',
        ],
        'elements': [
            'bpm', 'tempo', 'key', 'chord', 'melody', 'harmony',
            'rhythm', 'beat', 'sample', 'loop', 'mix', 'master',
            'eq', 'compression', 'reverb', 'delay', 'synth', 'drum',
        ],
        'ai_music': [
            'suno', 'udio', 'musiclm', 'jukebox', 'magenta', 'mubert',
            'aiva', 'soundraw',
        ],
    }

    def __init__(self, kernel: KernelLayer):
        super().__init__('music_production_agent', kernel)
        kernel.access.assign_role(self.name, 'operator')

    def _handle(self, prompt: str, **kwargs) -> Dict:
        """Identify music-production context and generate workflow suggestions."""
        text_lower = prompt.lower()
        detected: Dict[str, List[str]] = {}
        for category, keywords in self.MUSIC_KEYWORDS.items():
            hits = [kw for kw in keywords if kw in text_lower]
            if hits:
                detected[category] = hits

        llm_result = self.kernel.llm.complete(prompt, **kwargs)
        return {
            'agent': self.name,
            'response': llm_result['response'],
            'music_context': detected,
            'provider': llm_result['provider'],
        }


class ResearchAgent(Agent):
    """
    Application-layer agent: Research Assistant.

    Performs policy-document analysis using the existing PolicyAnalyzer,
    stores findings in the vector index for future semantic recall, and
    provides structured research summaries.
    """

    def __init__(self, kernel: KernelLayer):
        super().__init__('research_agent', kernel)
        kernel.access.assign_role(self.name, 'researcher')
        # Lazily import to avoid circular dependency at module level
        from policy_analyzer import PolicyAnalyzer
        self._policy_analyzer = PolicyAnalyzer()

    def _required_tool(self) -> str:
        return 'policy_analyze'

    def _handle(self, prompt: str, company_name: str = 'Unknown',
                **kwargs) -> Dict:
        """
        Analyse policy text, index it for semantic recall, and return findings.

        Args:
            prompt:       Policy or research text to analyse.
            company_name: Optional company name label.
        """
        analysis = self._policy_analyzer.analyze(prompt, company_name)
        report = self._policy_analyzer.format_report(analysis)

        # Index the document for future semantic search
        doc_id = f"research::{company_name}::{analysis['analysis_date']}"
        self.kernel.memory.index_memory(
            doc_id, prompt, metadata={'company': company_name,
                                      'type': 'policy_document'}
        )
        # Store structured results in long-term memory
        self.kernel.memory.remember_long(
            'research', doc_id, analysis
        )

        return {
            'agent': self.name,
            'response': report,
            'analysis': analysis,
            'doc_id': doc_id,
        }


class WorkflowDesigner(Agent):
    """
    Application-layer agent: Workflow Designer.

    Lets users define named multi-step workflows as sequences of (agent_name,
    prompt_template) pairs.  Workflows are persisted in long-term memory and
    can be retrieved and scheduled via the KernelLayer.
    """

    def __init__(self, kernel: KernelLayer):
        super().__init__('workflow_designer', kernel)
        kernel.access.assign_role(self.name, 'admin')

    def define_workflow(self, workflow_name: str,
                        steps: List[Dict]) -> Dict:
        """
        Persist a workflow definition.

        Args:
            workflow_name: Unique name for the workflow.
            steps: List of step dicts, each with keys:
                     - 'agent'  : name of the agent to invoke
                     - 'prompt' : prompt template string (may contain {variables})
                     - 'description' (optional): human-readable step description
        Returns:
            The stored workflow definition dict.
        """
        workflow = {
            'name': workflow_name,
            'steps': steps,
            'created_at': datetime.now().isoformat(),
        }
        self.kernel.memory.remember_long('workflows', workflow_name, workflow)
        return workflow

    def get_workflow(self, workflow_name: str) -> Optional[Dict]:
        """Retrieve a workflow definition by name."""
        return self.kernel.memory.recall_long('workflows', workflow_name)

    def schedule_workflow(self, workflow_name: str,
                          variables: Optional[Dict] = None) -> List[Dict]:
        """
        Expand a workflow's prompt templates and submit all steps to the scheduler.

        Args:
            workflow_name: Name of the workflow to schedule.
            variables:     Dict of variable substitutions for prompt templates.

        Returns:
            List of submitted task dicts.
        """
        workflow = self.get_workflow(workflow_name)
        if workflow is None:
            raise KeyError(f"Workflow '{workflow_name}' not found")

        variables = variables or {}
        tasks = []
        for i, step in enumerate(workflow['steps']):
            prompt = step['prompt'].format(**variables)
            task = self.kernel.scheduler.submit(
                task_id=f"{workflow_name}::step{i}::{uuid.uuid4().hex[:8]}",
                agent_name=step['agent'],
                payload={'prompt': prompt, 'step': i},
                priority=len(workflow['steps']) - i,  # earlier steps = higher priority
            )
            tasks.append(task)
        return tasks

    def _handle(self, prompt: str, **kwargs) -> Dict:
        """Parse a plain-text workflow description and register it."""
        lines = [ln.strip() for ln in prompt.strip().splitlines() if ln.strip()]
        name = lines[0] if lines else 'unnamed_workflow'
        steps = [
            {'agent': 'research_agent', 'prompt': ln, 'description': ln}
            for ln in lines[1:]
        ]
        workflow = self.define_workflow(name, steps)
        return {
            'agent': self.name,
            'response': (
                f"Workflow '{name}' registered with {len(steps)} step(s)."
            ),
            'workflow': workflow,
        }


class PromptLibrary(Agent):
    """
    Application-layer agent: Prompt Library.

    Stores, retrieves, and semantically searches named prompt templates.
    Templates may contain {placeholder} variables substituted at call time.
    """

    _BUILTIN_PROMPTS = {
        'policy_summary': (
            'Summarise the key data-sharing and technology provisions in the '
            'following policy document:\n\n{text}'
        ),
        'compliance_check': (
            'Identify all regulatory obligations and compliance requirements '
            'in the following text:\n\n{text}'
        ),
        'tech_extraction': (
            'List every technology, platform, and service mentioned in this '
            'policy document:\n\n{text}'
        ),
        'music_brief': (
            'Create a concise creative brief for the following music project: '
            '{project_description}'
        ),
        'research_query': (
            'Research and summarise information about: {topic}'
        ),
    }

    def __init__(self, kernel: KernelLayer):
        super().__init__('prompt_library', kernel)
        kernel.access.assign_role(self.name, 'admin')
        # Pre-load built-in prompts
        for name, template in self._BUILTIN_PROMPTS.items():
            self.save_prompt(name, template)

    def save_prompt(self, name: str, template: str,
                    tags: Optional[List[str]] = None) -> None:
        """Persist a prompt template and index it for semantic search."""
        self.kernel.memory.remember_long('prompts', name, {
            'name': name,
            'template': template,
            'tags': tags or [],
            'saved_at': datetime.now().isoformat(),
        })
        self.kernel.memory.index_memory(
            f'prompt::{name}', template,
            metadata={'type': 'prompt', 'name': name}
        )

    def get_prompt(self, name: str) -> Optional[str]:
        """Return the template string for a named prompt, or None."""
        record = self.kernel.memory.recall_long('prompts', name)
        return record['template'] if record else None

    def fill(self, name: str, **variables) -> Optional[str]:
        """
        Retrieve a named prompt template and substitute variables.

        Returns the filled prompt string, or None if the template is not found.
        """
        template = self.get_prompt(name)
        if template is None:
            return None
        return template.format(**variables)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Semantic search for prompt templates matching a query."""
        results = self.kernel.memory.search_long(query, top_k=top_k)
        return [r for r in results if r.get('metadata', {}).get('type') == 'prompt']

    def list_prompts(self) -> List[str]:
        """Return the names of all stored prompt templates."""
        records = self.kernel.memory._data.relational.query('long_term_memory',
                                                             namespace='prompts')
        return [r['key'] for r in records]

    def _handle(self, prompt: str, **kwargs) -> Dict:
        """Treat the prompt as a new template name + body (first line = name)."""
        lines = prompt.strip().splitlines()
        name = lines[0].strip() if lines else 'unnamed'
        template = '\n'.join(lines[1:]).strip() if len(lines) > 1 else prompt
        self.save_prompt(name, template)
        return {
            'agent': self.name,
            'response': f"Prompt '{name}' saved to library.",
            'template': template,
        }


class ApplicationLayer:
    """
    Application Layer — aggregates all domain-specific agents.

    Provides a unified `dispatch` method for routing a prompt to a named
    agent, and exposes each agent as a named attribute.
    """

    def __init__(self, kernel: KernelLayer):
        self.compliance = GovernmentComplianceAgent(kernel)
        self.music = MusicProductionAgent(kernel)
        self.research = ResearchAgent(kernel)
        self.workflow = WorkflowDesigner(kernel)
        self.prompts = PromptLibrary(kernel)
        self._registry: Dict[str, Agent] = {
            'government_compliance_agent': self.compliance,
            'music_production_agent': self.music,
            'research_agent': self.research,
            'workflow_designer': self.workflow,
            'prompt_library': self.prompts,
        }

    def dispatch(self, agent_name: str, prompt: str, **kwargs) -> Dict:
        """
        Route a prompt to a named agent.

        Args:
            agent_name: One of the registered agent names.
            prompt:     The input prompt.
            **kwargs:   Forwarded to the agent's `run` method.

        Returns:
            The agent's response dict; includes an 'error' key if the agent
            name is not found.
        """
        agent = self._registry.get(agent_name)
        if agent is None:
            return {
                'error': (
                    f"Unknown agent '{agent_name}'. "
                    f"Available: {list(self._registry.keys())}"
                )
            }
        return agent.run(prompt, **kwargs)

    @property
    def agent_names(self) -> List[str]:
        """Names of all registered agents."""
        return list(self._registry.keys())


# ---------------------------------------------------------------------------
# AI Operator OS — main orchestration class
# ---------------------------------------------------------------------------

class AIOperatorOS:
    """
    Subzteveø AI Operator OS.

    Orchestrates the three-tier architecture:
      1. Data Layer    — relational store, vector store, file store, compute
      2. Kernel Layer  — scheduler, context, memory, LLM-core, access, eval
      3. Application Layer — domain agents + workflow and prompt management

    Usage example::

        os_instance = AIOperatorOS(deployment_mode='local')
        result = os_instance.run('research_agent',
                                 'Analyse this privacy policy: ...',
                                 company_name='Acme Corp')
        print(result['response'])

    Deployment modes
    ----------------
    - ``local``          : all layers run in-process on local hardware
    - ``remote_kernel``  : kernel services run on a remote server; agents local
    - ``personal_remote``: everything on a personal cloud VM; local fallback
    - ``hybrid``         : local agents, kernel+data on cloud when available
    """

    def __init__(self, deployment_mode: str = 'local',
                 scheduler_policy: str = 'fifo',
                 context_window: int = 20):
        """
        Initialise the AI Operator OS.

        Args:
            deployment_mode:  One of the DEPLOYMENT_MODES constants.
            scheduler_policy: Scheduling policy for the kernel scheduler
                              ('fifo', 'priority', or 'round_robin').
            context_window:   Number of messages retained per session.
        """
        if deployment_mode not in DEPLOYMENT_MODES:
            raise ValueError(
                f"deployment_mode must be one of {DEPLOYMENT_MODES}, "
                f"got '{deployment_mode}'"
            )
        self.deployment_mode = deployment_mode

        # Instantiate layers bottom-up
        self.data = DataLayer(deployment_mode)
        self.kernel = KernelLayer(
            self.data,
            scheduler_policy=scheduler_policy,
            context_window=context_window,
        )
        self.application = ApplicationLayer(self.kernel)

    def run(self, agent_name: str, prompt: str, **kwargs) -> Dict:
        """
        Dispatch a prompt to an agent through the kernel.

        Wraps `application.dispatch` with scheduler integration: the task is
        submitted, immediately dequeued (eager execution), and the result is
        recorded in the scheduler's completed log.

        Args:
            agent_name: Name of the application-layer agent.
            prompt:     Input text / instruction.
            **kwargs:   Forwarded to the agent.

        Returns:
            The agent's response dict.
        """
        task = self.kernel.scheduler.submit(
            task_id=str(uuid.uuid4()),
            agent_name=agent_name,
            payload={'prompt': prompt, **kwargs},
        )
        # Eager execution: dequeue and run immediately
        self.kernel.scheduler.next_task()
        result = self.application.dispatch(agent_name, prompt, **kwargs)
        self.kernel.scheduler.mark_done(task, result)
        return result

    def register_llm_provider(self, name: str, handler: Callable,
                               set_default: bool = False) -> None:
        """Register a custom LLM provider with the kernel's LLM-core."""
        self.kernel.llm.register_provider(name, handler,
                                          set_default=set_default)

    def evaluation_report(self) -> Dict:
        """Return current aggregated evaluation metrics for all agents."""
        return self.kernel.evaluation.report()

    def status(self) -> Dict:
        """Return a high-level status snapshot of the OS."""
        return {
            'deployment_mode': self.deployment_mode,
            'compute_resources': self.data.compute_resources,
            'scheduler': {
                'policy': self.kernel.scheduler.policy,
                'queued_tasks': self.kernel.scheduler.queue_length,
                'completed_tasks': len(self.kernel.scheduler.completed_tasks),
            },
            'agents': self.application.agent_names,
            'llm_providers': self.kernel.llm.available_providers,
            'active_sessions': self.kernel.context.active_sessions(),
            'evaluation': self.evaluation_report(),
        }

    def export_status_json(self) -> str:
        """Serialise the current status snapshot as a JSON string."""
        return json.dumps(self.status(), indent=2, default=str)


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

def main():
    """Interactive demo of the Subzteveø AI Operator OS."""
    print("=" * 80)
    print("Subzteveø AI Operator OS — Interactive Demo")
    print("=" * 80)
    print()

    # Initialise in local mode
    os_instance = AIOperatorOS(deployment_mode='local', scheduler_policy='fifo')

    print(f"Deployment mode : {os_instance.deployment_mode}")
    print(f"Agents available: {', '.join(os_instance.application.agent_names)}")
    print()

    while True:
        print("Choose an option:")
        print("  1  Run research agent (policy analysis)")
        print("  2  Run government compliance agent")
        print("  3  Run music production agent")
        print("  4  Show evaluation report")
        print("  5  Show system status")
        print("  q  Quit")
        print()

        choice = input("Enter choice: ").strip().lower()

        if choice == 'q':
            print("Exiting AI Operator OS.")
            break

        elif choice == '1':
            text = input("Paste policy text (single line): ").strip()
            company = input("Company name (optional): ").strip() or "Unknown"
            result = os_instance.run('research_agent', text,
                                     company_name=company)
            print("\n" + result.get('response', str(result)))

        elif choice == '2':
            text = input("Paste document text (single line): ").strip()
            result = os_instance.run('government_compliance_agent', text)
            findings = result.get('compliance_findings', {})
            print(f"\nCompliance categories flagged: "
                  f"{result.get('categories_flagged', [])}")
            for cat, hits in findings.items():
                print(f"  {cat}: {hits}")

        elif choice == '3':
            text = input("Describe your music project: ").strip()
            result = os_instance.run('music_production_agent', text)
            context = result.get('music_context', {})
            print(f"\nMusic context detected: {context}")
            print(f"Response: {result.get('response', '')}")

        elif choice == '4':
            report = os_instance.evaluation_report()
            print("\nEvaluation Report:")
            print(json.dumps(report, indent=2, default=str))

        elif choice == '5':
            print("\nSystem Status:")
            print(os_instance.export_status_json())

        else:
            print("Unknown choice, please try again.")

        print()


if __name__ == "__main__":
    main()
