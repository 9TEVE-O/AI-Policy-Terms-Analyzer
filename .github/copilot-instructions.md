# Copilot Instructions for AI Policy & Terms Analyzer

## Project Overview

This repository contains a Python-based policy and terms analyzer that extracts technical information from companies' policy documents. The tool identifies technologies, services, URLs, APIs, bots, and data sharing practices mentioned in terms of service and privacy policies.

## Tech Stack

- **Language**: Python 3.x (uses standard library primarily)
- **Style**: Clean, readable Python with comprehensive docstrings
- **Dependencies**: Minimal - standard library only (optional: beautifulsoup4, requests, pdfplumber)
- **Structure**: Modular classes with clear separation of concerns

## Code Style Guidelines

### Python Conventions
- Follow PEP 8 style guidelines
- Use descriptive variable names (e.g., `policy_text`, `tech_keywords`, not `pt`, `tk`)
- Include docstrings for all classes and public methods
- Use type hints where appropriate (`from typing import Dict, List`)
- Prefer list comprehensions and dictionary comprehensions for simple transformations
- Use `#!/usr/bin/env python3` shebang for executable scripts

### Code Organization
- Main analyzer logic in `PolicyAnalyzer` class (`policy_analyzer.py`)
- Example/demo scripts separate from core functionality
- Test files use `test_` prefix
- Helper utilities and batch processing in separate files

### Documentation
- Keep README.md up-to-date with new features
- Include usage examples in docstrings
- Provide clear error messages and helpful output
- Document configuration options in `docs/configuration.md`

## Project Structure

```
.
├── policy_analyzer.py    # Core PolicyAnalyzer class
├── example_usage.py      # Usage examples and demos
├── batch_analyzer.py     # Batch processing utilities
├── quick_start.py        # Interactive beginner guide
├── test_google_cloud.py  # GCP detection tests
├── requirements.txt      # Python dependencies
├── docs/                 # Documentation files
│   ├── configuration.md  # Configuration guide
│   └── examples/         # Example configs
├── README.md             # Main documentation
├── USER_GUIDE.md         # User guide
└── QUICK_REFERENCE.md    # Quick command reference
```

## Key Features to Preserve

1. **URL & Domain Extraction**: Regex-based URL detection
2. **Technology Detection**: Keyword matching across multiple categories (platforms, languages, frameworks, databases, AI/ML, bots)
3. **Google Cloud Platform Analysis**: Comprehensive GCP service, program, and certification detection
4. **Service Integration Discovery**: Third-party service identification
5. **Multiple Output Formats**: JSON and formatted text reports

## Non-Negotiables

Copilot never merges "as-is" without verification:

- Run **tests + lint + typecheck** locally before accepting any change.
- No broad refactors unless explicitly requested.
- No new dependencies unless it is the smallest way to meet a requirement — state why.
- No secrets, PII, credentials, or sensitive data in prompts, comments, logs, or tests.

**Done = tests pass + lint clean + typecheck clean.**

## Control Loop

### Option A — TDD (default)

1. Write a failing test covering the requirement plus 2–3 edge cases.
2. Ask Copilot for the minimal implementation that satisfies the tests.
3. Run the tests.
4. Refactor in small steps.
5. Re-run tests + lint + typecheck.

### Option B — Spec-first (only when tests are hard to write upfront)

1. Write a mini-spec with acceptance criteria.
2. Ask Copilot for a skeleton with stubs.
3. Add tests.
4. Implement until tests pass.

> **Hard stop**: if no verifier (tests / types / lint) is running, Copilot is guessing.

## Context Discipline

Always open a Copilot Chat session or paste a **Context Pack** at the top of the relevant file:

```
# Goal: <one sentence>
# Inputs/outputs: <types + 1 example>
# Constraints: <perf, security, backwards compat>
# Must-use / must-not-use: <libs or patterns>
# Error policy: <throw vs Result; retry rules>
# Logging policy: <what must NOT be logged>
```

Providing this context reduces hallucinations and incorrect suggestions.

## Development Guidelines

### Adding New Features
- When adding new technology keywords, update the appropriate category in `tech_keywords` dictionary
- When adding new detection patterns, ensure they're case-insensitive
- Maintain backward compatibility with existing JSON output structure
- Add examples to `example_usage.py` for new features

### Testing
- Follow the TDD control loop above (write tests first)
- Include at least 2–3 edge cases per new test
- Verify detection is case-insensitive
- Test JSON output format remains consistent
- Run all test files to ensure no regression: `python -m pytest test_google_cloud.py test_ai_operator_os.py test_key_point_condenser.py -v`

### Security & Best Practices
- Validate and sanitize all user inputs
- Avoid executing arbitrary code from policy text
- Be mindful of potential ReDoS (Regular Expression Denial of Service) attacks with complex regex patterns
- Don't store sensitive company data in the repository
- Never include secrets, API keys, credentials, or PII in code, tests, logs, or comments
- Use safe JSON handling practices

### Code Quality
- Keep methods focused and single-purpose
- Extract magic numbers and repeated strings into constants
- Use meaningful variable names that describe the data
- Avoid deeply nested conditionals (max 3 levels)
- Comment complex regex patterns with examples

## Common Patterns

### Adding a New Technology Category
```python
self.tech_keywords = {
    # Existing categories...
    'new_category': ['keyword1', 'keyword2', 'keyword3']
}
```

### Adding a New Analysis Method
```python
def analyze_new_feature(self, text: str) -> Dict:
    """
    Analyze text for new feature.
    
    Args:
        text: The policy text to analyze
        
    Returns:
        Dict containing analysis results
    """
    results = {}
    # Implementation
    return results
```

### Output Format
- Always return structured data (dictionaries, lists)
- Include counts and statistics
- Provide both raw data and formatted output options
- Use consistent key names across different analysis functions

## Helpful Commands

```bash
# Run all tests
python -m pytest test_google_cloud.py test_ai_operator_os.py test_key_point_condenser.py -v

# Lint (errors only — fails build)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Lint (style warnings — informational)
flake8 . --count --max-line-length=120 --statistics --exit-zero

# Run the main analyzer interactively
python policy_analyzer.py

# Run examples
python example_usage.py

# Batch analyze multiple companies
python batch_analyzer.py
```

## When Making Changes

1. **Follow the TDD control loop** above before writing any implementation code.
2. **Provide a Context Pack** at the top of the Copilot Chat session or file being edited.
3. **Maintain consistency**: follow the established code style and structure.
4. **Update documentation**: update README.md and relevant docs when adding user-facing features.
5. **Keep it simple**: standard library only — no new dependencies without a stated reason.
6. **Think about users**: many users are non-technical — keep the interface simple and error messages clear.

## Remember

- This is primarily an educational and research tool
- Focus on accuracy of detection over speed
- Prioritize readability and maintainability
- The tool should work out-of-the-box with minimal setup
- Always handle edge cases gracefully (empty input, malformed text, etc.)
