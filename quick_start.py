#!/usr/bin/env python3
"""
Quick Start Guide for Policy Analyzer

This script provides a simple walkthrough for new users.
"""

from policy_analyzer import PolicyAnalyzer


def print_header():
    """Print a nice header."""
    print("\n" + "=" * 80)
    print(" " * 20 + "🔍 POLICY ANALYZER - QUICK START GUIDE 🔍")
    print("=" * 80 + "\n")


def print_instructions():
    """Print usage instructions."""
    print("Welcome! This tool helps you extract technical information from company policies.")
    print("\n📋 WHAT IT FINDS:")
    print("   ✓ Technologies & platforms (AWS, GitHub, etc.)")
    print("   ✓ URLs and websites")
    print("   ✓ Third-party services")
    print("   ✓ APIs and integrations")
    print("   ✓ Bots and automation systems")
    print("   ✓ Data sharing practices")
    print("\n🚀 HOW TO USE:")
    print("   1. Visit any company's website")
    print("   2. Find their 'Terms of Service' or 'Privacy Policy'")
    print("   3. Copy ALL the text (Ctrl+A, Ctrl+C)")
    print("   4. Paste it below")
    print("\n💡 TIP: For best results, analyze both Terms AND Privacy Policy!")
    print("\n" + "=" * 80)


def analyze_sample():
    """Analyze a sample policy to show capabilities."""
    print("\n📊 SAMPLE ANALYSIS")
    print("-" * 80)
    print("Let's analyze a sample dating site policy to show what this tool can find:\n")
    
    sample = """
    Dating Website Terms of Service
    
    Welcome to LoveMatch! Our service connects people using advanced AI technology.
    
    Technology We Use:
    - AI-powered matching algorithms using machine learning
    - Chatbots for customer support (powered by OpenAI GPT-4)
    - Real-time messaging with WebSocket connections
    - Profile verification using neural networks
    - Photo analysis using computer vision
    
    Infrastructure:
    - Hosted on AWS (Amazon Web Services)
    - Code repositories on GitHub
    - Payment processing through Stripe
    - Email notifications via SendGrid
    - SMS verification through Twilio
    
    Third-Party Services:
    We integrate with Google Analytics for usage statistics,
    Mixpanel for behavioral analytics, and Zendesk for customer support.
    
    Automated Systems:
    We use automated bots and crawlers to:
    - Detect fake profiles and spam
    - Monitor for inappropriate content
    - Suggest potential matches
    
    Data Sharing:
    We may share your information with payment processors, 
    analytics providers, and verification services.
    
    For more information:
    Website: https://lovematch.com
    Support: support@lovematch.com
    Privacy: https://lovematch.com/privacy
    """
    
    analyzer = PolicyAnalyzer()
    results = analyzer.analyze(sample, "LoveMatch (Sample)")
    
    print(analyzer.format_report(results))
    
    print("\n" + "=" * 80)
    print("🎯 KEY INSIGHTS FROM THIS SAMPLE:")
    print("-" * 80)
    print("✓ Tech Stack: AWS, GitHub, AI/ML (OpenAI GPT-4)")
    print("✓ Payment: Stripe")
    print("✓ Communications: SendGrid (email), Twilio (SMS)")
    print("✓ Analytics: Google Analytics, Mixpanel")
    print("✓ Support: Zendesk, chatbots")
    print("✓ Bot Detection: Yes, they use automated systems for safety")
    print("✓ Data Sharing: Yes, with payment processors and analytics providers")
    print("=" * 80 + "\n")


def interactive_mode():
    """Run interactive analysis."""
    print("\n🎬 YOUR TURN!")
    print("-" * 80)
    
    choice = input("Would you like to analyze your own policy now? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\nNo problem! Run this script again when you're ready.")
        print("Or use: python policy_analyzer.py for the full interactive tool\n")
        return
    
    print("\n" + "=" * 80)
    company = input("Enter company name: ").strip()
    
    if not company:
        company = "Unknown Company"
    
    print("\nPaste the policy text below.")
    print("When finished, press:")
    print("  • Ctrl+D (Mac/Linux)")
    print("  • Ctrl+Z then Enter (Windows)")
    print("-" * 80)
    
    policy_lines = []
    try:
        while True:
            line = input()
            policy_lines.append(line)
    except EOFError:
        pass
    
    policy_text = "\n".join(policy_lines)
    
    if not policy_text.strip():
        print("\n❌ No text entered. Please try again with policy text.")
        return
    
    print("\n🔄 Analyzing...")
    analyzer = PolicyAnalyzer()
    results = analyzer.analyze(policy_text, company)
    
    print("\n" + "=" * 80)
    print(analyzer.format_report(results))
    
    # Offer to save
    save = input("\n💾 Save results to JSON file? (y/n): ").strip().lower()
    if save == 'y':
        import json
        import re
        # Sanitize filename - remove unsafe characters
        safe_name = re.sub(r'[^\w\s-]', '', company).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        filename = f"{safe_name}_analysis.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to: {filename}")
        except (PermissionError, OSError, IOError) as e:
            print(f"❌ Could not save results to '{filename}': {e}")


def show_next_steps():
    """Show what users can do next."""
    print("\n📚 NEXT STEPS:")
    print("-" * 80)
    print("1. Analyze more companies:")
    print("   python quick_start.py")
    print("\n2. Use the full interactive tool:")
    print("   python policy_analyzer.py")
    print("\n3. See more examples:")
    print("   python example_usage.py")
    print("\n4. Use in your own code:")
    print("   from policy_analyzer import PolicyAnalyzer")
    print("\n5. Batch analyze multiple companies and build your own database!")
    print("\n💡 PRO TIP: Create a folder, analyze 10-20 companies in your industry,")
    print("   and you'll have amazing competitive intelligence!")
    print("=" * 80 + "\n")


def main():
    """Run the quick start guide."""
    print_header()
    print_instructions()
    
    # Show sample
    input("\nPress Enter to see a sample analysis... ")
    analyze_sample()
    
    # Offer interactive mode
    interactive_mode()
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Run again anytime.\n")
