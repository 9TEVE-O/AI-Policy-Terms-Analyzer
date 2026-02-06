# AI Policy & Terms Analyzer

This repository contains tools and resources for analyzing companies' policies, terms and conditions, and privacy policies to extract valuable technical information.

## 🎯 Purpose

Instead of manually reading through lengthy terms and conditions, this tool automatically analyzes policy documents to extract:

- **Tech Stack**: Technologies, frameworks, and platforms companies use
- **Websites & Domains**: All referenced URLs and domains
- **Repositories**: GitHub, GitLab, and other version control mentions
- **Third-Party Services**: Payment processors, analytics, email services, etc.
- **APIs & Integrations**: REST APIs, GraphQL, webhooks, and connections
- **Bots & Automation**: Chatbots, crawlers, and automated systems
- **Data Sharing**: What data is shared and with whom

## 🚀 Quick Start

### Basic Usage

```bash
# Run the interactive analyzer
python policy_analyzer.py

# Run examples to see what it can do
python example_usage.py
```

### Configuration

You can customize the analyzer's behavior using configuration files. See [Configuration Guide](docs/configuration.md) for detailed options.

```bash
# Create a config file in your directory
cp docs/examples/policyanalyzerrc.json .

# Or use a custom config
python policy_analyzer.py --config my_custom_config.json
```

### Using in Your Code

```python
from policy_analyzer import PolicyAnalyzer

# Create analyzer instance
analyzer = PolicyAnalyzer()

# Analyze a policy document
policy_text = """Your company's policy text here..."""
results = analyzer.analyze(policy_text, "Company Name")

# Get formatted report
print(analyzer.format_report(results))

# Or work with the raw data
print(f"URLs found: {results['urls_found']}")
print(f"Technologies: {results['technologies_detected']}")

# Access Google Cloud specific information
gcp_info = results['google_cloud_info']
print(f"GCP Services: {gcp_info['services']}")
print(f"GCP Programs: {gcp_info['programs']}")
print(f"GCP Certifications: {gcp_info['certifications']}")
```

### Testing Google Cloud Detection

```bash
# Run the Google Cloud detection test
python test_google_cloud.py
```

## 📋 Features

### 1. **URL & Domain Extraction**
Automatically finds all URLs and domain names mentioned in policies.

### 2. **Technology Detection**
Identifies mentions of:
- Cloud platforms (AWS, Azure, GCP, etc.)
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Django, Express, etc.)
- Databases (MongoDB, PostgreSQL, MySQL, etc.)
- AI/ML tools (OpenAI, ChatGPT, TensorFlow, etc.)

### 3. **Google Cloud Platform Analysis** ⭐ NEW
Comprehensive detection of Google Cloud usage:
- **GCP Services**: Cloud Functions, Cloud Run, BigQuery, Vertex AI, Cloud SQL, etc.
- **Developer Programs**: Google Cloud Developer and Innovator program references
- **Certifications**: Google Cloud Certified professionals and credentials
- **Complete Coverage**: 30+ Google Cloud services and programs tracked

### 4. **Service Integration Discovery**
Detects third-party services like:
- Payment processors (Stripe, PayPal)
- Communication tools (Twilio, SendGrid)
- Analytics platforms (Google Analytics, Mixpanel)
- Support systems (Zendesk, Intercom)

### 5. **Bot & Automation Detection**
Specifically identifies chatbots, automated systems, crawlers, and AI assistants.

### 6. **Data Sharing Analysis**
Extracts information about how and with whom companies share data.

### 7. **Multiple Output Formats**
- Human-readable formatted reports
- JSON for programmatic processing
- Batch analysis for multiple companies

## 💡 Use Cases

1. **Quick Research**: Analyze policies while browsing to understand tech stack
2. **Competitive Analysis**: Compare technologies used by different companies
3. **Security Research**: Identify third-party integrations and data sharing
4. **Tech Discovery**: Find new tools and services by analyzing successful companies
5. **Dating Site Analysis**: Discover bot usage and AI systems on dating platforms
6. **Data Collection**: Build a database of company tech stacks from public policies

## 📊 Example Output

```
================================================================================
POLICY ANALYSIS REPORT: TechCorp Inc.
================================================================================

Document Statistics:
  - Length: 1,234 characters
  - Word Count: 215 words

URLs Found (2):
  - https://techcorp.com/privacy
  - https://api.techcorp.com

Technologies Detected:
  Platforms:
    - aws
    - github
  Ai_Ml:
    - openai
    - chatgpt
  Services:
    - stripe
    - sendgrid
    - google analytics

Third-Party Services (5):
  - Zendesk for customer support
  - Intercom for live chat
  - Twilio for SMS notifications
  ...
```

## 🔧 Advanced Usage

### Batch Processing Multiple Policies

```python
from policy_analyzer import PolicyAnalyzer
import json

companies = {
    "Company A": "policy text...",
    "Company B": "policy text...",
    "Company C": "policy text..."
}

analyzer = PolicyAnalyzer()
results = {}

for company, policy in companies.items():
    results[company] = analyzer.analyze(policy, company)

# Save all results
with open('all_companies_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Custom Technology Keywords

```python
analyzer = PolicyAnalyzer()

# Add custom keywords to detect
analyzer.tech_keywords['custom_category'] = ['keyword1', 'keyword2']

results = analyzer.analyze(policy_text, "Company")
```

## 📁 Files in This Repository

- `policy_analyzer.py` - Main analyzer tool with PolicyAnalyzer class
- `example_usage.py` - Comprehensive examples showing different use cases
- `batch_analyzer.py` - Batch processing tool for multiple companies
- `quick_start.py` - Interactive beginner-friendly guide
- `requirements.txt` - Python dependencies (minimal - uses standard library)
- `README.md` - This documentation file
- `docs/configuration.md` - **Configuration guide** for customizing the analyzer
- `docs/examples/` - Example configuration files for different use cases
- AI workshop materials (PDFs) - Learning resources

## 📚 Documentation

- **[Configuration Guide](docs/configuration.md)** - Complete guide to configuring the analyzer
- **[User Guide](USER_GUIDE.md)** - Detailed guide for beginners
- **[Quick Reference](QUICK_REFERENCE.md)** - Quick command reference
- **[Project Summary](PROJECT_SUMMARY.md)** - Technical implementation details

## 🎓 Learning Resources

This repository also contains AI learning materials:
- AI Generalist Fellowship materials
- AI Income Workshop workbooks (1-3)
- Road Map and session guides
- YTA Playbook

## 🤝 Contributing

This tool was created to make policy analysis accessible and automated. Feel free to:
- Add more technology keywords
- Improve detection patterns
- Add new analysis features
- Share your use cases

## 📝 Tips for Best Results

1. **Copy the full policy**: Include complete terms/privacy policy for best results
2. **Multiple documents**: Analyze both terms AND privacy policy for complete picture
3. **Save results**: Use JSON output to build your own database
4. **Compare companies**: Run batch analysis to spot patterns and trends
5. **Dating sites**: Pay special attention to bot and AI mentions

## 🔍 What You Can Discover

From analyzing company policies, you can learn:
- What cloud infrastructure they use (cost and scale insights)
- Which third-party services they integrate (potential partnerships)
- Their tech stack (what technologies are popular/working)
- Bot and automation usage (especially on dating sites)
- Data sharing practices (privacy and security insights)
- API availability (integration opportunities)

## 🚦 Getting Started - No Coding Required

1. Open a company's Terms of Service or Privacy Policy webpage
2. Copy all the text (Ctrl+A, Ctrl+C)
3. Run: `python policy_analyzer.py`
4. Paste the text and press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows)
5. View the analysis results!

## 📧 Output

Analysis results show you everything the company uses to run their business - all extracted from public legal documents they're required to provide!

---

*Collect more data from your toilet than someone flipping through the Yellow Pages!* 📱
