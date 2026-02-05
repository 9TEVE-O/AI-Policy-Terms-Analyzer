# Configuration

## Overview

The AI Policy & Terms Analyzer provides flexible configuration through Python class instantiation and method parameters. This tool analyzes policy documents to extract technical information, and can be customized for various use cases.

## Basic Usage

### Creating an Analyzer Instance

```python
from policy_analyzer import PolicyAnalyzer

# Create analyzer with default configuration
analyzer = PolicyAnalyzer()
```

### Analyzing a Policy Document

The `analyze()` method is the main entry point for policy analysis:

```python
results = analyzer.analyze(policy_text, company_name)
```

**Parameters:**
- `policy_text` (str, required): The full text of the policy document to analyze
- `company_name` (str, optional): Name of the company. Defaults to "Unknown"

**Returns:**
A dictionary containing all extracted information with the following keys:
- `company_name`: Name of the company
- `analysis_date`: ISO 8601 timestamp of when the analysis was performed
- `urls_found`: List of URLs extracted from the document
- `domains_found`: List of domain names found in the text
- `emails_found`: List of email addresses discovered
- `technologies_detected`: Dictionary of detected technologies by category
- `google_cloud_info`: Detailed Google Cloud Platform information
- `api_references`: List of API-related references with context
- `third_party_services`: List of third-party services mentioned
- `data_sharing_mentions`: Data sharing and integration mentions
- `document_length`: Character count of the document
- `word_count`: Word count of the document

## Configuration Options

### Technology Keywords

The analyzer comes pre-configured with technology keywords organized by category. You can customize these by modifying the `tech_keywords` dictionary:

```python
analyzer = PolicyAnalyzer()

# Add custom keywords to existing categories
analyzer.tech_keywords['platforms'].append('digitalocean')
analyzer.tech_keywords['databases'].append('neo4j')

# Add entirely new categories
analyzer.tech_keywords['custom_category'] = ['keyword1', 'keyword2', 'keyword3']
```

**Default Categories:**

1. **platforms**: Cloud platforms and hosting services
   - Examples: github, gitlab, aws, azure, heroku, netlify, vercel
   
2. **languages**: Programming languages
   - Examples: python, javascript, java, ruby, php, go, rust, typescript
   
3. **frameworks**: Web and application frameworks
   - Examples: react, angular, vue, django, flask, express, spring
   
4. **databases**: Database systems
   - Examples: mysql, postgresql, mongodb, redis, elasticsearch
   
5. **services**: Third-party services and integrations
   - Examples: stripe, paypal, twilio, sendgrid, zendesk, intercom
   
6. **ai_ml**: AI and machine learning technologies
   - Examples: openai, chatgpt, claude, gemini, machine learning
   
7. **bots**: Bot and automation systems
   - Examples: chatbot, bot, automated system, crawler, spider

### Google Cloud Platform Configuration

The analyzer includes specialized detection for Google Cloud Platform services, programs, and certifications:

```python
analyzer = PolicyAnalyzer()

# Add custom GCP services
analyzer.gcp_services.append('cloud memorystore')
analyzer.gcp_services.append('cloud spanner')

# Add custom GCP programs
analyzer.gcp_programs.append('google cloud startup program')

# Add custom certification patterns (regex)
analyzer.gcp_cert_patterns.append(r'google cloud\s+specialist')
```

**Default GCP Detection:**

1. **Services**: 30+ Google Cloud services including:
   - Cloud Functions, Cloud Run, Cloud Storage
   - BigQuery, Cloud SQL, Cloud Firestore
   - Vertex AI, Cloud Vision, Cloud Speech
   - Kubernetes Engine (GKE), Compute Engine, App Engine
   
2. **Programs**: Developer and Innovator programs
   - Google Cloud Developer
   - Google Cloud Innovator
   - GCP Developer/Innovator programs
   
3. **Certifications**: Professional and Associate certifications
   - Cloud Architect, Cloud Developer, Cloud Engineer
   - Data Engineer certifications

### Output Formatting

The analyzer provides formatted reports through the `format_report()` method:

```python
# Get analysis results
results = analyzer.analyze(policy_text, "Company Name")

# Generate formatted text report
report = analyzer.format_report(results)
print(report)
```

**Customizing Output:**

You can also work directly with the results dictionary for custom output:

```python
import json

# Convert to JSON
json_output = json.dumps(results, indent=2)

# Save to file
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Access specific data
print(f"URLs found: {results['urls_found']}")
print(f"Technologies: {results['technologies_detected']}")
```

## Advanced Configuration

### Extraction Method Configuration

While the analyzer doesn't use configuration files, you can customize extraction behavior by modifying internal patterns:

#### URL Extraction Pattern

The default URL pattern can be customized if needed:

```python
import re

# Access the extraction methods to understand patterns
# URL pattern: r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&/=]*'

# For custom extraction, call methods directly
urls = analyzer.extract_urls(text)
domains = analyzer.extract_domains(text)
emails = analyzer.extract_emails(text)
```

#### API Reference Detection

API references are detected with context (50 characters before and after):

```python
# Get API references with surrounding context
api_refs = analyzer.extract_api_references(policy_text)

# Returns up to 10 API mentions with context
for ref in api_refs[:5]:
    print(ref)
```

### Batch Processing Configuration

For analyzing multiple policies, you can configure batch processing:

```python
analyzer = PolicyAnalyzer()

companies = {
    "Company A": "policy text A...",
    "Company B": "policy text B...",
    "Company C": "policy text C..."
}

# Batch analyze
results = {}
for company, policy in companies.items():
    results[company] = analyzer.analyze(policy, company)

# Aggregate results
all_technologies = set()
for result in results.values():
    for category, techs in result['technologies_detected'].items():
        all_technologies.update(techs)

print(f"Unique technologies across all companies: {len(all_technologies)}")
```

## Environment & Dependencies

### Python Version

- Python 3.6 or higher required
- Uses only standard library modules (no external dependencies)

### Required Imports

```python
import re          # Regular expression operations
import json        # JSON encoding/decoding
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
```

### Installation

No installation required beyond Python standard library:

```bash
# Clone the repository
git clone https://github.com/9TEVE-O/Ai-.git
cd Ai-

# Run directly
python policy_analyzer.py
```

## Usage Examples

### Example 1: Basic Analysis

```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
policy_text = """
Your company's privacy policy text here...
"""

results = analyzer.analyze(policy_text, "TechCorp")
print(analyzer.format_report(results))
```

### Example 2: Custom Technology Keywords

```python
analyzer = PolicyAnalyzer()

# Add industry-specific keywords
analyzer.tech_keywords['healthcare'] = ['hipaa', 'ehr', 'fhir', 'hl7']
analyzer.tech_keywords['fintech'] = ['pci-dss', 'sox', 'kyc', 'aml']

results = analyzer.analyze(policy_text, "HealthTech Inc.")
```

### Example 3: Focused Bot Detection

```python
analyzer = PolicyAnalyzer()
results = analyzer.analyze(dating_site_policy, "Dating Site")

# Extract bot-related information
bot_techs = results['technologies_detected'].get('bots', [])
ai_techs = results['technologies_detected'].get('ai_ml', [])

print(f"Bots detected: {len(bot_techs)}")
print(f"AI/ML technologies: {len(ai_techs)}")
```

### Example 4: Data Export Configuration

```python
import json
from datetime import datetime

analyzer = PolicyAnalyzer()
results = analyzer.analyze(policy_text, "Company")

# Export with timestamp
filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to {filename}")
```

## Command-Line Usage

### Interactive Mode

```bash
# Run interactive analyzer
python policy_analyzer.py
```

The interactive mode will:
1. Prompt for company name
2. Accept policy text input
3. Display formatted analysis results

### Quick Start Guide

```bash
# Run the guided quick start
python quick_start.py
```

This provides:
- Step-by-step instructions
- Sample analysis demonstration
- Interactive policy analysis
- Results export options

### Example Scripts

```bash
# Run comprehensive examples
python example_usage.py
```

This demonstrates:
- Basic usage
- JSON output
- Batch processing
- Custom analysis scenarios

## Troubleshooting

### Common Issues

**Issue: No technologies detected**
- Ensure policy text is properly formatted as a string
- Check that keywords match the text (case-insensitive matching is used)
- Verify the policy text contains technical information

**Issue: URLs not extracted**
- Ensure URLs include protocol (http:// or https://)
- Check URL format matches standard patterns
- Relative URLs (without protocol) may not be detected

**Issue: Too many false positives**
- Consider filtering results by category
- Implement custom post-processing logic
- Add domain-specific validation rules

### Performance Considerations

- **Large Documents**: The analyzer processes documents of any size, but very large documents (>1MB) may take longer
- **Batch Processing**: For analyzing many documents, consider processing in parallel using multiprocessing
- **Memory Usage**: Results are stored in memory; for very large batch jobs, consider streaming results to disk

## Best Practices

1. **Analyze Complete Documents**: For best results, analyze complete policy documents rather than excerpts
2. **Multiple Documents**: Analyze both Terms of Service and Privacy Policy for comprehensive coverage
3. **Customize Keywords**: Add industry-specific keywords before analysis for better detection
4. **Save Results**: Store analysis results in JSON format for future reference and comparison
5. **Batch Analysis**: When analyzing multiple companies, use consistent naming for easier comparison
6. **Version Control**: Keep track of when policies were analyzed, as companies update policies over time

## API Reference

### PolicyAnalyzer Class

#### Methods

**`__init__(self)`**
- Initializes the analyzer with default keyword configurations

**`analyze(self, policy_text: str, company_name: str = "Unknown") -> Dict`**
- Performs comprehensive analysis of a policy document
- Returns dictionary with all extracted information

**`format_report(self, analysis: Dict) -> str`**
- Formats analysis results as a human-readable report
- Returns formatted string

**`extract_urls(self, text: str) -> List[str]`**
- Extracts all URLs from text
- Returns list of unique URLs

**`extract_domains(self, text: str) -> List[str]`**
- Extracts domain names from text
- Returns list of unique domains

**`extract_emails(self, text: str) -> List[str]`**
- Extracts email addresses from text
- Returns list of unique emails

**`detect_technologies(self, text: str) -> Dict[str, List[str]]`**
- Detects technologies by category
- Returns dictionary mapping categories to detected technologies

**`extract_google_cloud_info(self, text: str) -> Dict[str, List[str]]`**
- Extracts detailed Google Cloud information
- Returns dictionary with services, programs, and certifications

**`extract_api_references(self, text: str) -> List[str]`**
- Extracts API-related references with context
- Returns list of up to 10 API mentions with surrounding text

**`extract_third_party_services(self, text: str) -> List[str]`**
- Extracts third-party service mentions
- Returns list of up to 20 services

**`detect_data_sharing(self, text: str) -> List[str]`**
- Detects data sharing and integration mentions
- Returns list of up to 15 data sharing references

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [USER_GUIDE.md](../USER_GUIDE.md) - Detailed user guide
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Quick reference for common tasks
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Project summary and goals
- [GOOGLE_CLOUD_DETECTION.md](../GOOGLE_CLOUD_DETECTION.md) - Google Cloud detection details

## Support

For issues, questions, or contributions:
- Review the documentation files in the repository
- Check the example scripts for usage patterns
- Examine the source code for implementation details
