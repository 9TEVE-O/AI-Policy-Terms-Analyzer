# AI-Assisted Engineering Portfolio Assessment

**Repository:** `9TEVE-O/AI-Policy-Terms-Analyzer`  
**Assessment date:** 22 July 2026  
**Owner and final decision authority:** Steven Lees  
**Assessment basis:** Coinbase's three durable engineering signals: repository-based coding and debugging, system design with AI, and leadership/behavioural judgment.  
**Evidence boundary:** This record assesses evidence currently visible in the repository. Missing evidence is recorded as a gap, not assumed to exist.

## Decision

**Current portfolio classification:** Credible working technical repository, but not yet a complete evidence-bound AI-assisted engineering case study.

**Overall score:** 61/100

**Decision:** Retain as a portfolio build and improve its evidence trail before presenting it as proof of advanced AI-assisted engineering practice.

The repository demonstrates useful implementation, testing, packaging and document-analysis capability. Its main weakness is not the code itself. The weakness is incomplete preservation of the human control trail: prompts, generated changes, rejected alternatives, verification reasoning and explicit acceptance decisions are not consistently linked.

---

## Scoring scale

| Score | Meaning |
|---:|---|
| 0 | No evidence |
| 1 | Claimed or implied only |
| 2 | Partial evidence |
| 3 | Adequate working evidence |
| 4 | Strong, repeatable evidence |
| 5 | Exceptional, independently reviewable evidence |

Weighted scores are converted to a 100-point total.

---

# Signal 1: Repository-based coding and debugging

**Weight:** 45%

| Criterion | Weight | Score /5 | Evidence and assessment |
|---|---:|---:|---|
| Repository comprehension | 7 | 4 | The README explains the main analyzer, key-point condenser, batch workflow, configuration, output forms and companion AI Operator OS experiment. The repository has identifiable components rather than an opaque single script. |
| Work within an existing codebase | 6 | 4 | Recent history includes packaging, CLI entry-point, test workflow and generated unit-test changes applied to an established repository. |
| Problem triage and debugging | 7 | 2 | Fix commits exist, including packaging backend correction, but the repository does not consistently preserve the original failure, diagnostic path, considered alternatives and why the accepted fix was correct. |
| AI-directed implementation | 6 | 2 | Branch and commit history indicate Claude and CodeRabbit involvement. Exact prompts, constraints and tool-selection reasoning are not preserved in a structured record. |
| Review of generated changes | 7 | 2 | AI-generated tests and pull requests are visible in history, but there is insufficient evidence showing which generated suggestions were challenged, modified or rejected by the human reviewer. |
| Verification and testing | 7 | 4 | The repository contains several tests and a test workflow. This is meaningful evidence of verification, although links between particular generated changes, targeted risks and test results remain incomplete. |
| Maintainability and rollback reasoning | 5 | 3 | Packaging, configuration documentation and modular files support maintainability. Explicit rollback criteria and compatibility decision records are limited. |

**Signal 1 subtotal:** 28/45

### Signal 1 judgment

The repository shows credible coding and maintenance activity in an existing codebase. The strongest evidence is the combination of structured functionality, tests, documentation and packaging changes. The main portfolio gap is that repository activity does not yet reveal enough of Steven Lees's judgment over the AI-produced work.

---

# Signal 2: System design with AI

**Weight:** 30%

| Criterion | Weight | Score /5 | Evidence and assessment |
|---|---:|---:|---|
| Problem and user definition | 5 | 3 | The README identifies the purpose: extracting technical and operational signals from policy, terms and privacy documents. Intended use is clear at a high level, but target users and decision contexts could be sharper. |
| Architecture and boundaries | 6 | 3 | The repository separates analysis, condensation, batch processing, configuration and reporting. The separate AI Operator OS experiment is described, but its relationship to the primary product is weak and may dilute the core architecture. |
| Data and output contracts | 5 | 3 | Structured JSON-compatible output and report formatting are documented. Formal schemas, validation constraints and versioned contracts are not strongly evidenced. |
| Failure-mode analysis | 5 | 2 | The analyzer's likely false positives, false negatives, ambiguous policy language and legal-interpretation boundaries are not fully modelled in the visible portfolio narrative. |
| Security, privacy and responsible use | 4 | 2 | The tool processes policy text and is presented as research/technical discovery rather than legal advice, but there is no prominent threat model or detailed handling boundary for private documents. |
| Trade-off and override judgment | 5 | 2 | Architectural choices are visible, but there is little preserved evidence showing alternatives proposed by AI, reasons for rejection, or explicit human overrides. |

**Signal 2 subtotal:** 15/30

### Signal 2 judgment

The repository has a coherent enough technical shape to demonstrate system-building capability. It is not yet a strong system-design case study because the decisions behind that shape are under-recorded. The AI Operator OS material should either be explicitly classified as an experiment or separated from the analyzer's main portfolio story.

---

# Signal 3: Leadership and behavioural judgment

**Weight:** 25%

| Criterion | Weight | Score /5 | Evidence and assessment |
|---|---:|---:|---|
| Task selection and value judgment | 5 | 3 | The repository addresses a genuine document-intelligence problem and has practical research and comparison uses. Evidence of user validation or a prioritised use case is limited. |
| Responsible AI delegation | 5 | 2 | AI-assisted commits are visible, but the delegation policy, constraints, data boundaries and approval rules are not captured in one reviewable location. |
| Handling disagreement and model error | 4 | 1 | There is little direct evidence of rejected AI output, contested recommendations or model-error correction beyond ordinary fix commits. |
| Evidence-based acceptance | 5 | 3 | Tests, documentation and workflow additions support acceptance decisions. However, explicit change-level acceptance records are absent. |
| Communication and transparency | 3 | 4 | The README is clear about features, usage and output. It does not appear to overclaim production readiness or legal authority. |
| Learning and iteration | 3 | 3 | The history shows iterative improvements across tests, packaging and repository hygiene. The lessons learned are not consolidated. |

**Signal 3 subtotal:** 18/25

### Signal 3 judgment

The repository communicates practical technical capability, but behavioural evidence is mostly inferred from artefacts. A stronger portfolio case study must make the human decisions visible rather than requiring a reviewer to reconstruct them from commit messages.

---

# Evidence preservation register

## 1. Prompts

**Current status:** Partial / not systematically preserved.

Known AI involvement is indicated by Claude-named branches and CodeRabbit-generated tests. The exact implementation prompts, constraints, supplied context and requested verification steps are not linked from the resulting changes.

**Required record for future changes:**

```text
Prompt ID:
Date:
Tool/model:
Task objective:
Repository context supplied:
Files AI was allowed to change:
Files AI was prohibited from changing:
Constraints:
Required tests:
Expected output:
Human approval authority:
```

## 2. Generated changes

**Current status:** Preserved through Git commits and pull requests, but not consistently labelled as AI-generated at file or decision-record level.

**Required record:**

```text
Change ID:
Prompt ID:
Branch/PR/commit:
Files changed:
AI-generated portions:
Human-authored portions:
Material assumptions introduced by AI:
```

## 3. Rejected outputs

**Current status:** Material gap.

The repository does not provide a reliable rejected-output register. This prevents a reviewer from seeing where human judgment corrected or constrained the model.

**Required record:**

```text
Rejection ID:
Prompt ID:
Rejected proposal or diff:
Reason rejected:
Risk avoided:
Replacement decision:
Supporting evidence:
```

## 4. Tests and verification

**Current status:** Working evidence exists.

Visible repository evidence includes dedicated tests and a recently added test workflow. Future records should link each material change to the exact tests run and their results.

**Required record:**

```text
Verification ID:
Change ID:
Commands run:
Automated test result:
Manual checks:
Failure modes targeted:
Known untested areas:
Reviewer:
```

## 5. Final decision record

**Current status:** Created by this assessment.

```text
Decision ID: AIPTA-PORTFOLIO-2026-07-22-01
Decision authority: Steven Lees
Decision: Retain and strengthen
Approved claim: The repository demonstrates Python-based document analysis, structured extraction, reporting, testing and iterative AI-assisted repository development.
Claims not yet approved:
- Production-ready legal or compliance analysis system
- Proven accuracy across varied policy documents
- Fully governed AI-development workflow
- Demonstrated end-user or commercial validation
Conditions before stronger public claims:
1. Preserve one complete prompt-to-decision development run.
2. Record at least one rejected AI-generated proposal.
3. Link generated changes to targeted tests and results.
4. Add an explicit limitations and responsible-use section.
5. Separate or classify the AI Operator OS experiment so it does not blur the main product architecture.
```

---

# Public portfolio claim

The following claim is supported by the current repository evidence:

> Built and iteratively improved a Python document-analysis toolkit that extracts structured technical and operational signals from policy and terms documents. The repository demonstrates modular analysis, configurable detection, human-readable and JSON output, batch processing, automated tests, packaging work and AI-assisted repository iteration. Current work is focused on strengthening the evidence trail around AI delegation, rejected outputs, verification and human acceptance decisions.

---

# Next controlled repository task

Run one bounded improvement through a complete evidence chain.

**Selected task:** Add a documented limitations and responsible-use section covering false positives, false negatives, non-legal-advice boundaries, private-document handling and expected human review.

For this task, preserve:

1. the exact prompt;
2. the generated patch;
3. at least one rejected or revised AI suggestion;
4. the tests or documentation checks performed;
5. Steven Lees's final acceptance decision.

Completion of that one run will turn this assessment from a retrospective scorecard into a reusable portfolio evidence pattern.
