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

## Development Guidelines

### Adding New Features
- When adding new technology keywords, update the appropriate category in `tech_keywords` dictionary
- When adding new detection patterns, ensure they're case-insensitive
- Maintain backward compatibility with existing JSON output structure
- Add examples to `example_usage.py` for new features

### Testing
- Test with sample policy texts that include edge cases
- Verify detection is case-insensitive
- Test JSON output format remains consistent
- Run existing test files to ensure no regression

### Security & Best Practices
- Validate and sanitize all user inputs
- Avoid executing arbitrary code from policy text
- Be mindful of potential ReDoS (Regular Expression Denial of Service) attacks with complex regex patterns
- Don't store sensitive company data in the repository
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
# Run the main analyzer interactively
python policy_analyzer.py

# Run examples
python example_usage.py

# Test Google Cloud detection
python test_google_cloud.py

# Batch analyze multiple companies
python batch_analyzer.py
```

## When Making Changes

1. **Understand the context**: Review existing code patterns before adding new features
2. **Maintain consistency**: Follow the established code style and structure
3. **Test thoroughly**: Run existing test scripts to ensure nothing breaks
4. **Update documentation**: Update README.md and relevant docs when adding features
5. **Keep it simple**: This tool uses standard library intentionally - avoid adding heavy dependencies unless absolutely necessary
6. **Think about users**: Many users are non-technical - keep the interface simple and error messages clear

## Remember

- This is primarily an educational and research tool
- Focus on accuracy of detection over speed
- Prioritize readability and maintainability
- The tool should work out-of-the-box with minimal setup
- Always handle edge cases gracefully (empty input, malformed text, etc.)
