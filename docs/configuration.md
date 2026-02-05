# Configuration

## Overview

Policy Analyzer configuration can be managed through a config file, environment variables, and CLI flag overrides.

### Configuration File

Policy Analyzer will automatically look for a configuration file in the current working directory in the following priority order:

1. `.policyanalyzerrc.json`
2. `policyanalyzerrc.json`
3. `.policyanalyzerrc.yml`
4. `policyanalyzerrc.yml`
5. `.policyanalyzerrc.yaml`
6. `policyanalyzerrc.yaml`
7. `.policyanalyzerrc.py`
8. `policyanalyzerrc.py`

Note that upward traversal is not supported. If you'd like to keep your configuration in a different location, you can explicitly pass in a configuration file path to the analyzer using the `--config` option.

### Environment Variables

Any configuration option can also be set using environment variables prefixed with `POLICY_ANALYZER_`, using double underscores to separate nested properties.

```bash
POLICY_ANALYZER_TECH_KEYWORDS__PLATFORMS=aws,azure,gcp python policy_analyzer.py
# is equivalent to using a config file with custom platform keywords
```

### CLI Flags

CLI flags can set options as well when using the command-line interface!

```bash
python policy_analyzer.py --company "Example Corp" --output-format json --save-to results.json
```

## File Structure

The structure of the config file allows you to customize various aspects of the analyzer's behavior.

**`policyanalyzerrc.json`:**

```json
{
  "analyzer": {
    "tech_keywords": {
      "platforms": ["github", "gitlab", "aws", "azure"],
      "languages": ["python", "javascript", "java"],
      "custom_category": ["custom_keyword1", "custom_keyword2"]
    },
    "gcp_services": ["google cloud platform", "cloud functions"],
    "case_sensitive": false,
    "include_google_cloud_detection": true
  },
  "output": {
    "format": "text",
    "save_to": null,
    "include_statistics": true,
    "include_urls": true,
    "include_emails": true,
    "include_technologies": true,
    "include_third_party": true,
    "include_apis": true,
    "include_repositories": true,
    "include_bots": true,
    "include_data_sharing": true,
    "include_google_cloud": true
  },
  "batch": {
    "auto_save": false,
    "output_dir": "analysis_results",
    "comparison_report": true
  }
}
```

**`policyanalyzerrc.yml`:**

```yaml
analyzer:
  tech_keywords:
    platforms:
      - github
      - gitlab
      - aws
      - azure
    languages:
      - python
      - javascript
      - java
    custom_category:
      - custom_keyword1
      - custom_keyword2
  gcp_services:
    - google cloud platform
    - cloud functions
  case_sensitive: false
  include_google_cloud_detection: true

output:
  format: text  # Options: text, json, yaml
  save_to: null
  include_statistics: true
  include_urls: true
  include_emails: true
  include_technologies: true
  include_third_party: true
  include_apis: true
  include_repositories: true
  include_bots: true
  include_data_sharing: true
  include_google_cloud: true

batch:
  auto_save: false
  output_dir: analysis_results
  comparison_report: true
```

**`policyanalyzerrc.py`:**

```python
# Python configuration file
config = {
    'analyzer': {
        'tech_keywords': {
            'platforms': ['github', 'gitlab', 'aws', 'azure'],
            'languages': ['python', 'javascript', 'java'],
            'custom_category': ['custom_keyword1', 'custom_keyword2']
        },
        'gcp_services': ['google cloud platform', 'cloud functions'],
        'case_sensitive': False,
        'include_google_cloud_detection': True
    },
    'output': {
        'format': 'text',
        'save_to': None,
        'include_statistics': True,
        'include_urls': True,
        'include_emails': True,
        'include_technologies': True,
        'include_third_party': True,
        'include_apis': True,
        'include_repositories': True,
        'include_bots': True,
        'include_data_sharing': True,
        'include_google_cloud': True
    },
    'batch': {
        'auto_save': False,
        'output_dir': 'analysis_results',
        'comparison_report': True
    }
}
```

## Configuration Options

### Analyzer Options

#### `tech_keywords`

Customize the technology keywords the analyzer looks for. Each category can contain a list of keywords.

**Default categories:**
- `platforms`: Cloud platforms, hosting services, version control
- `languages`: Programming languages
- `frameworks`: Web frameworks and libraries
- `databases`: Database systems
- `services`: Third-party services and integrations
- `ai_ml`: AI and machine learning technologies
- `bots`: Bot and automation systems

**Type:** `object`

**Example:**

```json
{
  "tech_keywords": {
    "platforms": ["github", "gitlab", "bitbucket", "aws", "azure"],
    "custom_blockchain": ["ethereum", "bitcoin", "solana", "polygon"]
  }
}
```

#### `gcp_services`

List of Google Cloud Platform services to detect.

**Type:** `array`

**Default:** Includes 30+ GCP services like Cloud Functions, BigQuery, Cloud Run, etc.

**Example:**

```json
{
  "gcp_services": ["google cloud platform", "cloud functions", "bigquery"]
}
```

#### `case_sensitive`

Whether keyword matching should be case-sensitive.

**Type:** `boolean`

**Default:** `false`

#### `include_google_cloud_detection`

Enable or disable Google Cloud Platform specific detection and reporting.

**Type:** `boolean`

**Default:** `true`

### Output Options

#### `format`

Output format for analysis results.

**Type:** `string`

**Options:** `text`, `json`, `yaml`

**Default:** `text`

#### `save_to`

File path to automatically save results to. If `null`, results are only printed to console.

**Type:** `string` or `null`

**Default:** `null`

**Example:**

```json
{
  "save_to": "analysis_results/company_analysis.json"
}
```

#### Output Sections

Control which sections appear in the output:

- **`include_statistics`**: Show document statistics (length, word count)
- **`include_urls`**: Show URLs and domains found
- **`include_emails`**: Show email addresses found
- **`include_technologies`**: Show detected technologies
- **`include_third_party`**: Show third-party service mentions
- **`include_apis`**: Show API and integration references
- **`include_repositories`**: Show repository mentions
- **`include_bots`**: Show bot and automation mentions
- **`include_data_sharing`**: Show data sharing practices
- **`include_google_cloud`**: Show Google Cloud specific information

**Type:** `boolean` for each

**Default:** `true` for all

### Batch Processing Options

#### `auto_save`

Automatically save batch analysis results without prompting.

**Type:** `boolean`

**Default:** `false`

#### `output_dir`

Directory where batch analysis results are saved.

**Type:** `string`

**Default:** `analysis_results`

#### `comparison_report`

Generate a side-by-side comparison report when analyzing multiple companies.

**Type:** `boolean`

**Default:** `true`

## Usage Examples

### Basic Configuration File

Create a minimal configuration file to customize technology keywords:

**`policyanalyzerrc.json`:**

```json
{
  "analyzer": {
    "tech_keywords": {
      "platforms": ["github", "aws", "vercel"],
      "ai_ml": ["openai", "anthropic", "huggingface"]
    }
  }
}
```

### Focus on Specific Technologies

Create a configuration focused only on dating site bot detection:

```json
{
  "analyzer": {
    "tech_keywords": {
      "bots": [
        "chatbot", "bot", "automated system", "automation",
        "fake profile", "bot detection", "automated matching",
        "ai assistant", "virtual assistant"
      ]
    }
  },
  "output": {
    "include_statistics": false,
    "include_urls": false,
    "include_emails": false,
    "include_technologies": true,
    "include_third_party": false,
    "include_apis": false,
    "include_repositories": false,
    "include_bots": true,
    "include_data_sharing": false,
    "include_google_cloud": false
  }
}
```

### Batch Processing Configuration

Configuration for automated batch processing with auto-save:

```json
{
  "batch": {
    "auto_save": true,
    "output_dir": "competitive_analysis",
    "comparison_report": true
  },
  "output": {
    "format": "json"
  }
}
```

### Industry-Specific Configuration

Create custom configurations for different industries:

**`fintech_config.json`:**

```json
{
  "analyzer": {
    "tech_keywords": {
      "platforms": ["aws", "azure", "stripe", "plaid"],
      "services": ["dwolla", "twilio", "sendgrid", "braintree"],
      "compliance": ["pci dss", "gdpr", "soc 2", "iso 27001"],
      "security": ["encryption", "ssl", "tls", "two-factor", "mfa"]
    }
  }
}
```

**`social_media_config.json`:**

```json
{
  "analyzer": {
    "tech_keywords": {
      "platforms": ["aws", "cloudflare", "fastly"],
      "ai_ml": ["content moderation", "recommendation engine", "nlp"],
      "services": ["analytics", "cdn", "video streaming"]
    }
  }
}
```

### Using Configuration with Python API

```python
from policy_analyzer import PolicyAnalyzer
import json

# Load custom configuration
with open('policyanalyzerrc.json', 'r') as f:
    config = json.load(f)

# Create analyzer with custom config
analyzer = PolicyAnalyzer(config=config)

# Or manually customize
analyzer = PolicyAnalyzer()
analyzer.tech_keywords['blockchain'] = ['ethereum', 'bitcoin', 'web3']

# Analyze with custom configuration
results = analyzer.analyze(policy_text, "Company Name")
print(analyzer.format_report(results))
```

### Environment Variable Examples

```bash
# Set custom output directory
export POLICY_ANALYZER_BATCH__OUTPUT_DIR=my_results
python batch_analyzer.py

# Disable Google Cloud detection
export POLICY_ANALYZER_ANALYZER__INCLUDE_GOOGLE_CLOUD_DETECTION=false
python policy_analyzer.py

# Set output format to JSON
export POLICY_ANALYZER_OUTPUT__FORMAT=json
python policy_analyzer.py

# Add custom technology category
export POLICY_ANALYZER_TECH_KEYWORDS__BLOCKCHAIN=ethereum,bitcoin,solana
python policy_analyzer.py
```

## Configuration Priority

When the same option is configured in multiple places, the following priority order applies (highest to lowest):

1. **CLI flags** (highest priority)
2. **Environment variables**
3. **Configuration file**
4. **Default values** (lowest priority)

**Example:**

If you have a config file with `"format": "json"`, but run:
```bash
POLICY_ANALYZER_OUTPUT__FORMAT=yaml python policy_analyzer.py --output-format text
```

The output format will be `text` (CLI flag wins).

## Advanced Configuration

### Custom Keyword Patterns

For more advanced pattern matching, you can use regular expressions:

```python
analyzer = PolicyAnalyzer()
analyzer.custom_patterns = {
    'api_keys': r'api[_-]?key[s]?',
    'webhooks': r'webhook[s]?|callback[_-]?url',
    'oauth': r'oauth|openid|saml|sso'
}
```

### Pre-processing Configuration

Configure text pre-processing options:

```json
{
  "preprocessing": {
    "normalize_whitespace": true,
    "remove_html_tags": true,
    "lowercase": true,
    "min_word_length": 2
  }
}
```

### Output Customization

Customize report formatting:

```json
{
  "output": {
    "format": "text",
    "report_width": 80,
    "section_separator": "================================================================================",
    "indent_spaces": 2,
    "show_empty_sections": false
  }
}
```

### Filtering Options

Filter results based on criteria:

```json
{
  "filters": {
    "min_url_count": 1,
    "min_tech_mentions": 2,
    "exclude_common_urls": ["example.com", "localhost"],
    "exclude_email_domains": ["example.com"]
  }
}
```

## Configuration Validation

The analyzer will validate your configuration file when loaded. Common validation errors:

- **Invalid format**: Ensure JSON/YAML syntax is correct
- **Invalid option**: Unknown configuration keys will be ignored with a warning
- **Invalid value type**: E.g., providing a string where array is expected
- **Missing required fields**: Some advanced features may require specific fields

## Best Practices

### 1. Use Configuration Files for Projects

Keep a `policyanalyzerrc.json` in your project directory for consistent analysis.

### 2. Environment Variables for CI/CD

Use environment variables in continuous integration pipelines:

```yaml
# .github/workflows/analyze.yml
env:
  POLICY_ANALYZER_BATCH__AUTO_SAVE: true
  POLICY_ANALYZER_OUTPUT__FORMAT: json
```

### 3. Industry-Specific Configs

Maintain separate configuration files for different analysis types:

```
configs/
  ├── fintech.json
  ├── healthcare.json
  ├── social_media.json
  └── dating_apps.json
```

### 4. Version Control

Commit your configuration files to version control to maintain consistency across team members.

### 5. Document Custom Keywords

When adding custom keywords, document why they're important for your use case.

## Troubleshooting

### Configuration Not Loading

**Problem:** Configuration file is not being read

**Solutions:**
- Ensure the file is in the current working directory
- Check file name matches one of the expected patterns
- Verify JSON/YAML syntax is valid
- Try using `--config` flag with explicit path

### Environment Variables Not Working

**Problem:** Environment variables are ignored

**Solutions:**
- Use correct prefix: `POLICY_ANALYZER_`
- Use double underscores for nested properties
- Ensure environment variables are exported
- Check for typos in variable names

### Custom Keywords Not Detected

**Problem:** Added keywords are not being found

**Solutions:**
- Verify keywords are lowercase (unless case_sensitive is true)
- Check for typos in keyword spelling
- Ensure keywords appear in the policy text
- Try with simpler, more common variations

## Migration Guide

### From v1.x to v2.x (Future)

When new versions introduce configuration changes, this section will guide you through migration steps.

## Schema Reference

For a complete JSON schema of the configuration format, see [configuration-schema.json](./configuration-schema.json).

## See Also

- [README.md](../README.md) - Main documentation
- [USER_GUIDE.md](../USER_GUIDE.md) - User guide for beginners
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Command quick reference
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Technical details

## Contributing

To suggest new configuration options or improve existing ones, please:
1. Open an issue describing the use case
2. Provide example configuration
3. Explain expected behavior
4. Submit a pull request with implementation

---

**Note:** This configuration system is designed to be flexible and extensible. If you need configuration options not currently available, they can be easily added!
