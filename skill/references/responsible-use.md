# Responsible Use Boundary

This skill supports research and technical discovery from policy and terms documents. It does not establish authoritative legal, compliance, security, or production-readiness conclusions.

## False positives and false negatives

The underlying repository uses text patterns, configured terms, and document structure. Any equivalent skill run can also misclassify or miss material language.

Possible false positives include:

- a technology mentioned historically;
- a prohibited action mistaken for an active practice;
- a customer-selected integration mistaken for an organisation-controlled service;
- a third-party or hypothetical example mistaken for current operation.

Possible false negatives include:

- unfamiliar terminology;
- omitted or linked material;
- context not present in the supplied source;
- poor extraction, truncation, translation, or scanning;
- indirect language not captured by keyword-oriented detection.

Therefore:

- absence from output does not prove absence from the source or organisation;
- detection does not prove deployment, applicability, or legal significance.

## Legal and compliance boundary

Do not issue:

- legal advice;
- compliance certification;
- regulatory interpretation presented as authoritative;
- contractual approval;
- a determination that an organisation satisfies a legal standard.

A user may ask for evidence relevant to such a question. Extract and organise the evidence, identify uncertainties and missing sources, and keep the legal conclusion separate.

## Private and sensitive documents

When the source is private, confidential, privileged, personal, commercially sensitive, or regulated:

- use only the minimum necessary content;
- do not copy raw content into additional external services unless authorised and necessary;
- avoid reproducing credentials, secrets, or unnecessary personal information;
- preserve storage/retention/access limitations as unknown unless actually established;
- do not imply that the repository or this skill supplies secure storage, verified deletion, confidential computing, or access governance.

## Human review

For any consequential conclusion, a human reviewer should compare the finding against the complete source and consider:

- definitions;
- exceptions;
- cross-references;
- dates;
- jurisdiction;
- document version;
- applicability;
- linked or incorporated material.

## Production-readiness boundary

Code, documentation, tests, structured output, or an automated workflow do not establish production readiness.

Production use requires separately defined and tested requirements for, as applicable:

- accuracy;
- supported document types;
- failure handling;
- security;
- dependency management;
- monitoring;
- audit logging;
- review gates;
- rollback;
- ownership for errors and updates.

Repository tests should be represented only as evidence that tested implementation behaviour passed specified tests, not that policy interpretation is universally correct.
