# Responsible-Use Documentation Controlled Run

**Run ID:** AIPTA-RU-2026-07-22-01  
**Repository:** `9TEVE-O/AI-Policy-Terms-Analyzer`  
**Branch:** `codex/responsible-use-evidence-run`  
**Base commit:** `10ccde0c5d825f24b1d19563f0f1fa59e1e4fee5`  
**README change commit:** `a6c9e05b2205215d6935dd5e0d6e39e0dffe1076`  
**Change type:** Documentation-only, bounded responsible-use clarification  
**Final human authority:** Steven Lees

## 1. Exact prompt

The following instruction initiated this controlled run:

> Next controlled build action  
> Run one bounded repository change through the full evidence chain:  
> Task: Add a limitations and responsible-use section addressing:  
> false positives and false negatives;  
> non-legal-advice boundaries;  
> private-document handling;  
> expected human review;  
> unsupported production-readiness claims.  
> For that change, preserve the exact prompt, generated patch, at least one rejected or revised suggestion, checks performed and Steven Lees’s final acceptance decision.

## 2. Scope and constraints

### Allowed change

- Add one limitations and responsible-use section to `README.md`.
- Link the section to this evidence record.
- Preserve the exact prompt, change provenance, rejection, checks and decision status.

### Excluded change

- No analyzer logic changes.
- No dependency or packaging changes.
- No new legal, compliance, security or production-readiness claims.
- No statement that tests prove semantic accuracy.
- No direct push or merge to `main` before explicit acceptance.
- No alteration of the separate `codex/regression-test-hardening` work.

## 3. Generated change

### Files changed

1. `README.md`
   - Added `## Limitations and responsible use`.
   - Added explicit false-positive and false-negative boundaries.
   - Added non-legal-advice and non-certification language.
   - Added controls for private, confidential, privileged, personal and regulated documents.
   - Added mandatory human-review expectations for consequential findings.
   - Added an explicit production-readiness boundary.
   - Linked to this controlled-run record.

2. `docs/RESPONSIBLE_USE_EVIDENCE_RUN_2026-07-22.md`
   - Preserves this evidence chain.

### Patch location

The generated README patch is preserved in Git history on branch `codex/responsible-use-evidence-run`, beginning with commit `a6c9e05b2205215d6935dd5e0d6e39e0dffe1076`.

## 4. Rejected or revised suggestion

### Rejected suggestion

> This analyzer provides reliable compliance insights and can be safely used to assess whether an organisation’s policies meet privacy obligations.

### Decision

**Rejected.**

### Reason

The repository does not contain evidence establishing legal reliability, compliance coverage, jurisdictional validity, independently measured semantic accuracy, or safe suitability for consequential privacy assessments.

### Risk avoided

- Unsupported legal and compliance claims.
- Confusing text-pattern detection with authoritative interpretation.
- Encouraging consequential decisions from incomplete automated output.
- Misrepresenting repository tests as proof of production or legal fitness.

### Accepted replacement

The README now states that the toolkit supports research and technical discovery, requires human review, does not provide legal or compliance advice, and has not established production readiness.

## 5. Checks performed

### Documentation checks

| Check | Result |
|---|---|
| False positives addressed | Pass |
| False negatives addressed | Pass |
| Absence-of-detection limitation stated | Pass |
| Detection-does-not-prove-applicability limitation stated | Pass |
| Non-legal-advice boundary stated | Pass |
| Compliance certification claim blocked | Pass |
| Private and sensitive document authority check stated | Pass |
| External AI and third-party transfer warning stated | Pass |
| Storage, retention and deletion limitations stated | Pass |
| Human source-document review required | Pass |
| Consequential decision boundary stated | Pass |
| Production-readiness claim blocked | Pass |
| Required pre-production controls named | Pass |
| Evidence-record link included | Pass |

### Code and test impact

- No Python source file changed.
- No dependency file changed.
- No runtime behaviour changed.
- Existing automated tests were not represented as validation of this documentation or of analyzer accuracy.
- A documentation-only change does not establish semantic correctness, security or production readiness.

### Known unverified areas

- Markdown rendering has not been independently reviewed in every GitHub client.
- Legal wording has not been reviewed by a qualified lawyer.
- The analyzer’s false-positive and false-negative rates remain unmeasured.
- Private-document processing controls remain operator responsibilities, not repository-enforced guarantees.

## 6. Acceptance decision

### Technical acceptance

**Decision:** Accepted for pull-request review.

**Reason:** The change is bounded, documentation-only, directly addresses all requested limitations, avoids unsupported claims, and does not interfere with analyzer logic or the existing regression-hardening branch.

### Human acceptance

**Decision authority:** Steven Lees  
**Decision:** Accepted.  
**Acceptance recorded:** 23 July 2026, Australia/Darwin.  
**Approved action:** Merge pull request #37 into `main`.

Steven Lees explicitly accepted the reviewed controlled change after the branch, pull request, evidence record, rejected suggestion, checks and pending approval boundary were presented.

## 7. Public-claim boundary after this change

Supported:

> The repository documents known limitations, requires human review, and explicitly blocks legal-advice, compliance-certification and unsupported production-readiness interpretations.

Not supported:

- The analyzer is legally reliable.
- The analyzer verifies compliance.
- The analyzer is secure for confidential material by default.
- The analyzer has measured accuracy across policy types.
- The analyzer is production-ready.
- Automated tests prove the correctness of policy interpretations.

## 8. Completion state

| Evidence-chain element | Status |
|---|---|
| Exact prompt | Preserved |
| Generated patch | Preserved in branch history |
| Rejected suggestion | Preserved with reason and risk |
| Checks performed | Preserved |
| Technical acceptance | Recorded |
| Steven Lees final acceptance | Accepted and recorded |
| Merge authority | Granted for PR #37 |
