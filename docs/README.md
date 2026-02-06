# Documentation

Welcome to the Policy Analyzer documentation!

## Available Documentation

### [Configuration Guide](configuration.md)
Complete guide to configuring the Policy Analyzer. Learn how to:
- Use configuration files (JSON, YAML, Python)
- Customize technology keywords
- Control output format and sections
- Use environment variables
- Set up batch processing

### Example Configurations

The [`examples/`](examples/) directory contains ready-to-use configuration files:

- **[policyanalyzerrc.json](examples/policyanalyzerrc.json)** - Complete default configuration in JSON format
- **[policyanalyzerrc.yml](examples/policyanalyzerrc.yml)** - Complete default configuration in YAML format
- **[dating-site-bot-detection.json](examples/dating-site-bot-detection.json)** - Focused config for dating site bot analysis
- **[fintech-analysis.json](examples/fintech-analysis.json)** - Config optimized for financial technology companies

## Quick Links

### Main Documentation (Root Directory)

- **[README.md](../README.md)** - Main project overview and quick start
- **[USER_GUIDE.md](../USER_GUIDE.md)** - Detailed beginner-friendly guide
- **[QUICK_REFERENCE.md](../QUICK_REFERENCE.md)** - Quick command reference
- **[PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md)** - Technical implementation details

## Getting Started

1. **New to the tool?** Start with [README.md](../README.md) and [USER_GUIDE.md](../USER_GUIDE.md)
2. **Want to customize?** See the [Configuration Guide](configuration.md)
3. **Need quick commands?** Check [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
4. **Technical details?** Read [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md)

## Using Example Configurations

To use an example configuration:

```bash
# Copy to your working directory
cp docs/examples/policyanalyzerrc.json .

# Or use directly
python policy_analyzer.py --config docs/examples/dating-site-bot-detection.json
```

## Configuration Format

The Policy Analyzer supports multiple configuration formats:

### JSON (Recommended)
```json
{
  "analyzer": {
    "tech_keywords": {
      "platforms": ["aws", "azure", "gcp"]
    }
  }
}
```

### YAML
```yaml
analyzer:
  tech_keywords:
    platforms:
      - aws
      - azure
      - gcp
```

### Python
```python
config = {
    'analyzer': {
        'tech_keywords': {
            'platforms': ['aws', 'azure', 'gcp']
        }
    }
}
```

## Contributing

Found an issue or want to improve the documentation?

1. Open an issue describing the problem
2. Submit a pull request with improvements
3. Share your custom configurations with the community

---

Happy analyzing! 🔍
