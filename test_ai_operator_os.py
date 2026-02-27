#!/usr/bin/env python3
"""
Test script for the Subzteveø AI Operator OS.

Tests the three-tier architecture (application, kernel, data/hardware layers),
all domain agents, kernel services, deployment modes, and evaluation metrics.
"""

import json

from ai_operator_os import (
    AIOperatorOS,
    ApplicationLayer,
    DataLayer,
    EvaluationEngine,
    KernelLayer,
    PromptLibrary,
    RelationalStore,
    Scheduler,
    VectorStore,
    DEPLOYMENT_MODES,
    EVALUATION_METRICS,
)


# ---------------------------------------------------------------------------
# Data / Hardware Layer tests
# ---------------------------------------------------------------------------

def test_relational_store():
    """Test RelationalStore CRUD operations."""
    print("Testing RelationalStore...")
    store = RelationalStore()

    store.insert('users', 'u1', {'name': 'Alice', 'role': 'admin'})
    store.insert('users', 'u2', {'name': 'Bob', 'role': 'researcher'})

    assert store.get('users', 'u1') == {'name': 'Alice', 'role': 'admin'}
    assert store.get('users', 'u99') is None

    results = store.query('users', role='admin')
    assert len(results) == 1 and results[0]['name'] == 'Alice'

    assert store.delete('users', 'u1') is True
    assert store.get('users', 'u1') is None

    print("  ✓ RelationalStore CRUD works correctly")


def test_vector_store():
    """Test VectorStore upsert and semantic search."""
    print("Testing VectorStore...")
    store = VectorStore()

    store.upsert('doc1', 'privacy policy data protection GDPR',
                 metadata={'type': 'policy'})
    store.upsert('doc2', 'music production beat tempo BPM',
                 metadata={'type': 'music'})
    store.upsert('doc3', 'government compliance regulation law',
                 metadata={'type': 'compliance'})

    results = store.search('privacy data protection', top_k=2)
    assert len(results) == 2
    # The most relevant result should be doc1
    assert results[0]['id'] == 'doc1'

    assert store.delete('doc1') is True
    results_after = store.search('privacy data protection', top_k=2)
    assert all(r['id'] != 'doc1' for r in results_after)

    print("  ✓ VectorStore search ranks relevant documents first")


def test_data_layer_deployment_modes():
    """Test DataLayer initialises cleanly for each deployment mode."""
    print("Testing DataLayer deployment modes...")
    for mode in DEPLOYMENT_MODES:
        dl = DataLayer(deployment_mode=mode)
        assert dl.deployment_mode == mode
        resources = dl.compute_resources
        assert 'primary' in resources

    try:
        DataLayer(deployment_mode='invalid_mode')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print(f"  ✓ DataLayer supports all modes: {DEPLOYMENT_MODES}")


# ---------------------------------------------------------------------------
# Kernel Layer tests
# ---------------------------------------------------------------------------

def test_scheduler():
    """Test Scheduler with all three policies."""
    print("Testing Scheduler...")

    # FIFO policy
    s = Scheduler(policy='fifo')
    s.submit('t1', 'agent_a', 'payload1', priority=0)
    s.submit('t2', 'agent_b', 'payload2', priority=5)
    first = s.next_task()
    assert first['task_id'] == 't1', "FIFO should return first submitted task"

    # Priority policy
    s2 = Scheduler(policy='priority')
    s2.submit('t1', 'agent_a', 'payload1', priority=1)
    s2.submit('t2', 'agent_b', 'payload2', priority=10)
    s2.submit('t3', 'agent_c', 'payload3', priority=5)
    first = s2.next_task()
    assert first['task_id'] == 't2', "Priority should return highest-priority task"

    # mark_done
    task = s.next_task()
    s.mark_done(task, result={'ok': True})
    assert len(s.completed_tasks) == 1
    assert s.completed_tasks[0]['status'] == 'completed'

    print("  ✓ Scheduler FIFO and priority policies work correctly")


def test_context_manager():
    """Test ContextManager push, get, and clear."""
    print("Testing ContextManager...")
    from ai_operator_os import ContextManager

    cm = ContextManager(window_size=3)
    cm.push('sess1', 'user', 'hello')
    cm.push('sess1', 'assistant', 'hi there')
    cm.push('sess1', 'user', 'how are you?')
    cm.push('sess1', 'assistant', 'great')  # should push out first message

    ctx = cm.get_context('sess1')
    assert len(ctx) == 3, "Window should cap at window_size"
    assert ctx[0]['content'] == 'hi there'  # first msg should be evicted

    assert 'sess1' in cm.active_sessions()
    cm.clear('sess1')
    assert cm.get_context('sess1') == []

    print("  ✓ ContextManager window and clear work correctly")


def test_evaluation_engine():
    """Test EvaluationEngine metric scoring and aggregation."""
    print("Testing EvaluationEngine...")
    ee = EvaluationEngine()

    # Low hallucination: factual language
    rec1 = ee.evaluate('agent_x', 'What is GDPR?',
                       'GDPR is the General Data Protection Regulation.',
                       correct=True)
    assert rec1['scores']['hallucination_frequency'] == 0.0
    assert rec1['scores']['correctness'] == 1.0

    # High hallucination: uncertain language
    rec2 = ee.evaluate('agent_x',
                       'Explain the policy',
                       'I think maybe this possibly refers to something.',
                       correct=False)
    assert rec2['scores']['hallucination_frequency'] > 0.0
    assert rec2['scores']['correctness'] == 0.0

    # Relevance: identical prompt/response should score 1.0
    rec3 = ee.evaluate('agent_x', 'hello world', 'hello world')
    assert rec3['scores']['context_relevance'] == 1.0

    agg = ee.aggregate('agent_x')
    for metric in EVALUATION_METRICS:
        assert metric in agg

    report = ee.report()
    assert 'agent_x' in report

    print("  ✓ EvaluationEngine metrics and aggregation work correctly")


def test_tool_access_manager():
    """Test ToolAccessManager RBAC and audit log."""
    print("Testing ToolAccessManager...")
    from ai_operator_os import ToolAccessManager

    tam = ToolAccessManager()
    tam.define_role('analyst', ['policy_analyze', 'vector_search'])
    tam.assign_role('agent_a', 'analyst')

    assert tam.check_access('agent_a', 'policy_analyze') is True
    assert tam.check_access('agent_a', 'file_write') is False
    assert tam.check_access('unknown_agent', 'policy_analyze') is False

    permitted = tam.permitted_tools('agent_a')
    assert 'policy_analyze' in permitted

    assert len(tam.audit_log) == 3  # three check_access calls above

    print("  ✓ ToolAccessManager RBAC and audit log work correctly")


def test_memory_manager():
    """Test MemoryManager short-term and long-term storage."""
    print("Testing MemoryManager...")
    from ai_operator_os import MemoryManager

    dl = DataLayer()
    mm = MemoryManager(dl)

    mm.remember_short('sess1', 'topic', 'privacy')
    assert mm.recall_short('sess1', 'topic') == 'privacy'
    assert mm.recall_short('sess1', 'missing', default='default') == 'default'
    mm.forget_short('sess1')
    assert mm.recall_short('sess1', 'topic') is None

    mm.remember_long('research', 'doc1', {'title': 'GDPR Overview'})
    val = mm.recall_long('research', 'doc1')
    assert val == {'title': 'GDPR Overview'}
    assert mm.recall_long('research', 'missing') is None

    mm.index_memory('mem1', 'data protection privacy GDPR regulation')
    results = mm.search_long('GDPR data protection', top_k=1)
    assert results[0]['id'] == 'mem1'

    print("  ✓ MemoryManager short-term and long-term memory work correctly")


# ---------------------------------------------------------------------------
# Application Layer tests
# ---------------------------------------------------------------------------

def test_research_agent():
    """Test ResearchAgent policy analysis and memory indexing."""
    print("Testing ResearchAgent...")
    os_instance = AIOperatorOS()

    policy_text = """
    Privacy Policy - TechCorp
    We use GitHub for version control, AWS for hosting, and OpenAI's GPT for
    our chatbot. Payments via Stripe. Contact: privacy@techcorp.com
    Visit https://techcorp.com/privacy for details.
    """
    result = os_instance.run('research_agent', policy_text,
                             company_name='TechCorp')

    assert result.get('agent') == 'research_agent'
    assert 'response' in result
    assert 'analysis' in result
    assert 'doc_id' in result
    analysis = result['analysis']
    assert 'technologies_detected' in analysis
    assert 'urls_found' in analysis

    print("  ✓ ResearchAgent returns structured policy analysis")


def test_government_compliance_agent():
    """Test GovernmentComplianceAgent compliance keyword detection."""
    print("Testing GovernmentComplianceAgent...")
    os_instance = AIOperatorOS()

    doc = """
    Our platform complies with GDPR and HIPAA requirements. All data is
    encrypted following NIST guidelines and we have FedRAMP authorization.
    Our procurement follows FAR and DFARS regulations.
    """
    result = os_instance.run('government_compliance_agent', doc)

    assert result.get('agent') == 'government_compliance_agent'
    assert 'compliance_findings' in result
    findings = result['compliance_findings']

    # GDPR/HIPAA should be in data_protection; NIST/FedRAMP in security
    assert 'data_protection' in findings
    assert 'gdpr' in findings['data_protection']
    assert 'security' in findings

    print("  ✓ GovernmentComplianceAgent detects compliance categories")


def test_music_production_agent():
    """Test MusicProductionAgent genre and tool detection."""
    print("Testing MusicProductionAgent...")
    os_instance = AIOperatorOS()

    text = "I'm producing a hip hop track at 90 BPM in Ableton with heavy bass."
    result = os_instance.run('music_production_agent', text)

    assert result.get('agent') == 'music_production_agent'
    assert 'music_context' in result
    ctx = result['music_context']
    assert 'genres' in ctx and 'hip hop' in ctx['genres']
    assert 'production_tools' in ctx and 'ableton' in ctx['production_tools']
    assert 'elements' in ctx and 'bpm' in ctx['elements']

    print("  ✓ MusicProductionAgent detects genre, tools, and elements")


def test_workflow_designer():
    """Test WorkflowDesigner define, retrieve, and schedule workflows."""
    print("Testing WorkflowDesigner...")
    os_instance = AIOperatorOS()
    wd = os_instance.application.workflow

    steps = [
        {'agent': 'research_agent',
         'prompt': 'Analyse policy for {company}',
         'description': 'Policy analysis step'},
        {'agent': 'government_compliance_agent',
         'prompt': 'Check compliance for {company}',
         'description': 'Compliance check step'},
    ]
    workflow = wd.define_workflow('full_analysis', steps)
    assert workflow['name'] == 'full_analysis'
    assert len(workflow['steps']) == 2

    retrieved = wd.get_workflow('full_analysis')
    assert retrieved is not None
    assert retrieved['name'] == 'full_analysis'

    tasks = wd.schedule_workflow('full_analysis', variables={'company': 'Acme'})
    assert len(tasks) == 2
    # Verify prompt substitution
    first_payload = tasks[0]['payload']
    assert 'Acme' in first_payload['prompt']

    print("  ✓ WorkflowDesigner define/retrieve/schedule works correctly")


def test_prompt_library():
    """Test PromptLibrary save, retrieve, fill, and semantic search."""
    print("Testing PromptLibrary...")
    os_instance = AIOperatorOS()
    pl = os_instance.application.prompts

    # Built-in prompts should already be available
    template = pl.get_prompt('policy_summary')
    assert template is not None
    assert '{text}' in template

    filled = pl.fill('policy_summary', text='sample policy text')
    assert 'sample policy text' in filled

    # Save a custom prompt
    pl.save_prompt('custom_test',
                   'Analyse the following for {topic}: {content}',
                   tags=['test'])
    assert pl.get_prompt('custom_test') is not None

    # Semantic search
    results = pl.search('compliance regulatory', top_k=3)
    assert len(results) >= 1

    # List prompts
    names = pl.list_prompts()
    assert 'policy_summary' in names
    assert 'custom_test' in names

    print("  ✓ PromptLibrary save/fill/search works correctly")


# ---------------------------------------------------------------------------
# Integration and deployment mode tests
# ---------------------------------------------------------------------------

def test_all_deployment_modes():
    """Test AIOperatorOS initialises and returns status for all modes."""
    print("Testing all deployment modes...")
    for mode in DEPLOYMENT_MODES:
        os_instance = AIOperatorOS(deployment_mode=mode)
        assert os_instance.deployment_mode == mode
        status = os_instance.status()
        assert status['deployment_mode'] == mode
        assert set(status['agents']) == {
            'government_compliance_agent', 'music_production_agent',
            'research_agent', 'workflow_designer', 'prompt_library',
        }
    print(f"  ✓ All deployment modes initialise correctly: {DEPLOYMENT_MODES}")


def test_custom_llm_provider():
    """Test registering and using a custom LLM provider."""
    print("Testing custom LLM provider registration...")
    os_instance = AIOperatorOS()

    def echo_provider(prompt: str, **kwargs) -> str:
        return f"ECHO: {prompt[:50]}"

    os_instance.register_llm_provider('echo', echo_provider, set_default=True)
    assert 'echo' in os_instance.kernel.llm.available_providers

    result = os_instance.kernel.llm.complete("Hello, world!")
    assert result['response'].startswith('ECHO:')
    assert result['provider'] == 'echo'

    print("  ✓ Custom LLM provider registered and used correctly")


def test_evaluation_integration():
    """Test end-to-end evaluation after running multiple agents."""
    print("Testing evaluation integration...")
    os_instance = AIOperatorOS()

    os_instance.run('research_agent',
                    'We use AWS and Python. Visit https://example.com',
                    company_name='TestCo')
    os_instance.run('government_compliance_agent',
                    'We comply with GDPR and HIPAA.')

    report = os_instance.evaluation_report()
    assert 'research_agent' in report
    assert 'government_compliance_agent' in report

    for metrics in report.values():
        assert 'hallucination_frequency' in metrics
        assert 'context_relevance' in metrics

    print("  ✓ Evaluation metrics tracked across multiple agent runs")


def test_json_export():
    """Test AIOperatorOS.export_status_json produces valid JSON."""
    print("Testing JSON status export...")
    os_instance = AIOperatorOS(deployment_mode='hybrid')
    os_instance.run('music_production_agent',
                    'hip hop beat at 90 bpm in FL Studio')

    json_output = os_instance.export_status_json()
    parsed = json.loads(json_output)

    assert parsed['deployment_mode'] == 'hybrid'
    assert 'agents' in parsed
    assert 'scheduler' in parsed
    assert parsed['scheduler']['completed_tasks'] >= 1

    print("  ✓ JSON status export is valid and contains expected fields")


def test_scheduler_policies():
    """Test all three scheduler policies via the OS."""
    print("Testing all scheduler policies...")
    for policy in ('fifo', 'priority', 'round_robin'):
        os_instance = AIOperatorOS(scheduler_policy=policy)
        assert os_instance.kernel.scheduler.policy == policy
        # Run a task to exercise the scheduler
        os_instance.run('music_production_agent', 'test beat')
        assert os_instance.kernel.scheduler.queue_length == 0
        assert len(os_instance.kernel.scheduler.completed_tasks) == 1
    print("  ✓ All three scheduler policies initialise and run tasks")


def test_invalid_agent_dispatch():
    """Test that dispatching to an unknown agent returns an error dict."""
    print("Testing invalid agent dispatch...")
    os_instance = AIOperatorOS()
    result = os_instance.application.dispatch('nonexistent_agent', 'hello')
    assert 'error' in result
    assert 'nonexistent_agent' in result['error']
    print("  ✓ Invalid agent dispatch returns error dict")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 80)
    print("Subzteveø AI Operator OS — Test Suite")
    print("=" * 80)
    print()

    # Data / Hardware Layer
    print("--- Data / Hardware Layer ---")
    test_relational_store()
    test_vector_store()
    test_data_layer_deployment_modes()
    print()

    # Kernel Layer
    print("--- Kernel Layer ---")
    test_scheduler()
    test_context_manager()
    test_evaluation_engine()
    test_tool_access_manager()
    test_memory_manager()
    print()

    # Application Layer
    print("--- Application Layer ---")
    test_research_agent()
    test_government_compliance_agent()
    test_music_production_agent()
    test_workflow_designer()
    test_prompt_library()
    print()

    # Integration
    print("--- Integration ---")
    test_all_deployment_modes()
    test_custom_llm_provider()
    test_evaluation_integration()
    test_json_export()
    test_scheduler_policies()
    test_invalid_agent_dispatch()
    print()

    print("=" * 80)
    print("All tests completed successfully! ✓")
    print("=" * 80)
    print()
