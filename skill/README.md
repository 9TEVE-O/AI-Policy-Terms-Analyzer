# Analyzing Policy and Terms — Skill Package

This package was extracted from:

`https://github.com/9TEVE-O/AI-Policy-Terms-Analyzer`

Source baseline: main commit `01c4bedfb3a6016e73115535fae4ec1a83be9600` (29 August 2026).

Package contents:

- `SKILL.md` — operational skill contract;
- `references/extraction-schema.md` — stable extraction categories and fields;
- `references/responsible-use.md` — evidence, privacy, legal, and production-readiness boundaries;
- `tests/skill-cases.md` — positive and negative validation cases.

The skill deliberately does not embed or duplicate the full Python repository. When the repository is available, it can be used as the deterministic first-pass extractor. When it is not, the skill requires the analysis method to be labelled accurately rather than pretending the code ran.


## Capability upgrade (November 2026)

"Super skill" is an informal label, not a special permission tier. This package combines existing evidence-first instructions with two optional Python utilities: offline candidate extraction and a safe local skills installer. It does not create an agent runtime, upload confidential text, certify compliance, or silently enable this skill in any product.

### Run the actual analyzer without a network fetch

From the checked-out source repository:

    python skill/scripts/analyze_text.py --input /path/to/authorised-policy.txt --company "Example Company" --source-url "https://example.com/privacy" --output /path/to/new-findings.json

- Input: existing local UTF-8 text only, maximum 2 MiB. The input must be authorised.
- The URL flag is provenance metadata only. No URL is fetched.
- If output is omitted, JSON goes to stdout. Existing output paths are not overwritten.
- The report records SHA-256, source scope, raw candidate extraction and HUMAN_REVIEW_REQUIRED.
- No contextual review or legal/compliance evaluation is performed by this command.
- For a copied skill installed elsewhere, add --repo-root pointing to a trusted checkout of this repository.

### Install for local Codex or Claude Code

These commands preview the destination without writing anything:

    python skill/scripts/install_skill.py --agent codex --scope project --project-root .
    python skill/scripts/install_skill.py --agent claude --scope project --project-root .

To copy the skill into the relevant recognised project directory, explicitly add --install:

    python skill/scripts/install_skill.py --agent codex --scope project --project-root . --install
    python skill/scripts/install_skill.py --agent claude --scope project --project-root . --install

For a personal, cross-project local skill use --scope user without --project-root. The copied folder is named analyzing-policy-and-terms to satisfy the Agent Skills directory-name contract. The installer refuses to overwrite an existing target. These operations affect only the local execution environment where the script runs; committing these files on GitHub does not perform the installation.

### Validation boundary

Run:

    python -m pytest -q tests/test_policy_skill_cli.py
    python -m pytest -q

Do not promote passing software tests into a claim of semantic accuracy, safe legal advice, secure production operation or current company practice. Review the negative and positive cases in tests/skill-cases.md separately.
