# Quick Reference Guide

## 🚀 Quick Start Commands

### For Beginners (No Coding Required)
```bash
python quick_start.py
```

### See Examples First
```bash
python example_usage.py
```

### Interactive Analysis
```bash
python policy_analyzer.py
```

### Batch Analysis (Multiple Companies)
```bash
python batch_analyzer.py
```

## 📝 Common Tasks

### Analyze a Single Company
1. Copy the company's Privacy Policy or Terms of Service
2. Run: `python policy_analyzer.py`
3. Enter company name
4. Paste the policy text
5. Press Ctrl+D (Mac/Linux) or Ctrl+Z+Enter (Windows)

### Analyze Multiple Companies
1. Run: `python batch_analyzer.py`
2. Choose option 2 (Interactive)
3. Enter number of companies
4. For each company:
   - Enter name
   - Paste policy text
   - Press Ctrl+D/Ctrl+Z

### Use in Your Own Code
```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
results = analyzer.analyze(policy_text, "Company Name")

# Get formatted report
print(analyzer.format_report(results))

# Or work with raw data
print(results['technologies_detected'])
print(results['urls_found'])
print(results['third_party_services'])
```

## 🎯 Use Case Examples

### Dating Site Bot Detection
```bash
# 1. Go to dating site
# 2. Copy Privacy Policy
# 3. Run analyzer
# 4. Look for "bots" section in results
```

### Tech Stack Research
```bash
# Analyze GitHub, Facebook, Twitter policies
# Compare their technologies
# Build competitive intelligence
```

### Privacy Analysis
```bash
# Check "data_sharing_mentions"
# Check "third_party_services"
# See who gets your data
```

## 💾 Saving Results

### Save Single Analysis
```python
import json
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
results = analyzer.analyze(policy_text, "Company")

with open('company_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Save Batch Results
The batch analyzer automatically offers to save results when you run it.
Files are saved to `analysis_results/` directory.

## 🔍 What the Tool Finds

| Category | Examples |
|----------|----------|
| **Platforms** | AWS, Azure, GCP, GitHub, Heroku |
| **Languages** | Python, JavaScript, Java, Go, Ruby |
| **Frameworks** | React, Django, Express, Angular |
| **Databases** | MongoDB, PostgreSQL, MySQL, Redis |
| **AI/ML** | OpenAI, ChatGPT, machine learning |
| **Bots** | chatbot, automated system, crawler |
| **Services** | Stripe, SendGrid, Twilio, Zendesk |
| **URLs** | All website links mentioned |
| **Emails** | Contact addresses |
| **APIs** | REST, GraphQL, webhook references |

## 📊 Output Formats

### Human-Readable Report
```bash
python policy_analyzer.py
# Automatically shows formatted report
```

### JSON Export
```bash
# Interactive mode asks if you want to save
# Or use programmatically:
import json
json.dump(results, open('output.json', 'w'), indent=2)
```

### Comparison Report (Batch)
```bash
python batch_analyzer.py
# Shows side-by-side comparison
```

## 🛠️ Customization

### Add Custom Technology Keywords
```python
from policy_analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer()
analyzer.tech_keywords['custom'] = ['keyword1', 'keyword2']

results = analyzer.analyze(text, "Company")
```

### Focus on Specific Categories
```python
results = analyzer.analyze(policy_text, "Company")

# Just get bots
bots = results['technologies_detected'].get('bots', [])

# Just get AI/ML
ai_tech = results['technologies_detected'].get('ai_ml', [])

# Just get third parties
services = results['third_party_services']
```

## 📁 File Structure

```
Ai-/
├── policy_analyzer.py      # Main tool
├── quick_start.py          # Beginner guide
├── example_usage.py        # Examples
├── batch_analyzer.py       # Batch analysis
├── README.md               # Main documentation
├── USER_GUIDE.md           # Detailed guide
├── PROJECT_SUMMARY.md      # Project overview
├── QUICK_REFERENCE.md      # This file
├── requirements.txt        # Dependencies (none!)
└── .gitignore             # Git configuration
```

## ⚡ Keyboard Shortcuts

| Action | Mac/Linux | Windows |
|--------|-----------|---------|
| Finish Input | Ctrl+D | Ctrl+Z then Enter |
| Cancel | Ctrl+C | Ctrl+C |
| Copy All | Cmd+A, Cmd+C | Ctrl+A, Ctrl+C |
| Paste | Cmd+V | Ctrl+V |

## 🐛 Troubleshooting

### "Python not found"
Install Python 3.8+ from python.org

### "No module named policy_analyzer"
Make sure you're in the correct directory:
```bash
cd /path/to/Ai-
ls policy_analyzer.py  # Should show the file
```

### "Nothing happens after pasting"
Press Ctrl+D (Mac/Linux) or Ctrl+Z then Enter (Windows)

### Results seem incomplete
Make sure you copied the ENTIRE policy, not just a section

## 📚 Documentation Files

- **README.md** - Overview and quick start
- **USER_GUIDE.md** - Detailed beginner guide with examples
- **PROJECT_SUMMARY.md** - Technical implementation details
- **QUICK_REFERENCE.md** - This file (command reference)

## 🎓 Learning Path

1. Start with `python quick_start.py` - Interactive introduction
2. Read `USER_GUIDE.md` - Understand all features
3. Run `python example_usage.py` - See real examples
4. Try `python policy_analyzer.py` - Analyze your first policy
5. Use `python batch_analyzer.py` - Compare companies
6. Import as module - Use in your own projects

## 🌟 Pro Tips

1. **Analyze both Privacy Policy AND Terms of Service** for complete picture
2. **Save results as JSON** to build your own database
3. **Use batch analyzer** to compare 5-10 competitors at once
4. **Focus on specific sections** like bots, AI, or data sharing
5. **Create folders** for different industries or use cases
6. **Export to spreadsheet** for easier comparison

## ✅ Checklist for Complete Analysis

- [ ] Copy full Privacy Policy
- [ ] Copy full Terms of Service
- [ ] Run analyzer on both
- [ ] Check technologies detected
- [ ] Review third-party services
- [ ] Note data sharing practices
- [ ] Check bot/AI usage
- [ ] Save results as JSON
- [ ] Add to your database/spreadsheet

## 🎯 Real-World Workflow

```bash
# Morning routine: Analyze 5 competitors

# 1. Make a list of companies
companies="Facebook Twitter Instagram TikTok Snapchat"

# 2. For each company:
#    - Visit site
#    - Find Privacy Policy
#    - Copy all text
#    - Paste into batch analyzer

# 3. Get comparison report

# 4. Save results

# 5. Update your competitive intelligence spreadsheet

# Time saved: Hours of manual reading!
```

## 📞 Getting Help

If you need help:
1. Read USER_GUIDE.md
2. Check PROJECT_SUMMARY.md for technical details
3. Run examples to see how it works
4. Check the code (it's well commented!)

---

**Remember**: This tool analyzes PUBLIC legal documents. Everything it finds is information companies are legally required to disclose!

Happy analyzing! 🔍✨
