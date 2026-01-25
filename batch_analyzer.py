#!/usr/bin/env python3
"""
Batch Policy Analyzer - Analyze Multiple Companies at Once

This script helps you analyze policies from multiple companies and 
compare them side-by-side. Great for competitive analysis!
"""

from policy_analyzer import PolicyAnalyzer
import json
import os
from datetime import datetime


def save_results(results, output_dir='analysis_results'):
    """Save all results to JSON files in a directory."""
    import re
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save individual company files
    for company, data in results.items():
        # Sanitize filename - remove unsafe characters
        safe_name = re.sub(r'[^\w\s-]', '', company).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        filename = f"{output_dir}/{safe_name}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Save combined summary
    summary_file = f"{output_dir}/summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Saved results to {output_dir}/")
    return output_dir


def create_comparison_report(results):
    """Create a side-by-side comparison of companies."""
    print("\n" + "=" * 100)
    print(" " * 35 + "COMPARISON REPORT")
    print("=" * 100)
    
    # Technology comparison
    print("\n📊 TECHNOLOGY COMPARISON")
    print("-" * 100)
    
    all_tech_categories = set()
    for company_data in results.values():
        all_tech_categories.update(company_data['technologies_detected'].keys())
    
    for category in sorted(all_tech_categories):
        print(f"\n{category.upper()}:")
        for company, data in results.items():
            techs = data['technologies_detected'].get(category, [])
            if techs:
                print(f"  {company:20s}: {', '.join(techs)}")
    
    # Service comparison
    print("\n\n🔗 THIRD-PARTY SERVICES")
    print("-" * 100)
    for company, data in results.items():
        services = data['third_party_services']
        print(f"{company:20s}: {len(services)} services")
        if services:
            print(f"{'':20s}  {', '.join(services[:5])}")
    
    # Data sharing
    print("\n\n🔒 DATA SHARING PRACTICES")
    print("-" * 100)
    for company, data in results.items():
        sharing = data['data_sharing_mentions']
        print(f"{company:20s}: {len(sharing)} mentions")
    
    # URLs and contacts
    print("\n\n🌐 ONLINE PRESENCE")
    print("-" * 100)
    for company, data in results.items():
        urls = len(data['urls_found'])
        emails = len(data['emails_found'])
        print(f"{company:20s}: {urls} URLs, {emails} emails")
    
    print("\n" + "=" * 100)


def analyze_batch_from_dict(companies_dict):
    """
    Analyze multiple companies from a dictionary.
    
    Args:
        companies_dict: Dict mapping company names to policy text
    
    Returns:
        Dict of analysis results
    """
    analyzer = PolicyAnalyzer()
    results = {}
    
    print(f"\n🔄 Analyzing {len(companies_dict)} companies...\n")
    
    for i, (company, policy) in enumerate(companies_dict.items(), 1):
        print(f"[{i}/{len(companies_dict)}] Analyzing {company}...", end=' ')
        results[company] = analyzer.analyze(policy, company)
        print("✓")
    
    print(f"\n✅ Analysis complete for {len(results)} companies!")
    return results


def example_batch_analysis():
    """Example showing batch analysis of multiple companies."""
    
    # Sample policies for demonstration
    sample_policies = {
        "TechStartup": """
            TechStartup Privacy Policy
            
            We use AWS for cloud infrastructure and GitHub for code hosting.
            Our application is built with React and Node.js, using MongoDB for data storage.
            Payment processing through Stripe, emails via SendGrid.
            
            We integrate with Google Analytics and Mixpanel for analytics.
            Our chatbot uses OpenAI GPT-4.
            
            Contact: privacy@techstartup.com
            Website: https://techstartup.com
        """,
        
        "FinanceApp": """
            FinanceApp Terms of Service
            
            Our platform runs on Microsoft Azure with PostgreSQL databases.
            We use Django for backend and Vue.js for frontend.
            
            Payment providers: PayPal, Stripe
            Security: We employ machine learning for fraud detection
            Communications: Twilio for SMS, SendGrid for email
            
            Third-party integrations with banking APIs and credit bureaus.
            Support: support@financeapp.com
            API: https://api.financeapp.com
        """,
        
        "SocialPlatform": """
            SocialPlatform Privacy Notice
            
            Infrastructure: Google Cloud Platform (GCP)
            Technology: React Native for mobile, Angular for web
            Storage: Firebase, Redis for caching
            
            We use AI and machine learning for content recommendations.
            Chatbot powered by Claude AI.
            
            Analytics: Google Analytics, Segment, Mixpanel
            CDN: Cloudflare
            
            We share data with advertising partners and analytics providers.
            
            Privacy contact: privacy@socialplatform.io
            Website: https://socialplatform.io
        """,
        
        "HealthTech": """
            HealthTech Privacy Policy
            
            HIPAA-compliant infrastructure on AWS
            Ruby on Rails backend with React frontend
            MySQL database with encryption
            
            We use automated systems and bots for:
            - Appointment reminders (Twilio)
            - Patient engagement (chatbot)
            - Data analysis (machine learning)
            
            Third-party services:
            - Stripe for payments
            - Zendesk for support
            - SendGrid for notifications
            
            Medical data shared only with authorized healthcare providers
            and insurance companies as required by law.
            
            Contact: hipaa@healthtech.com
            Portal: https://patient.healthtech.com
        """
    }
    
    # Perform batch analysis
    results = analyze_batch_from_dict(sample_policies)
    
    # Create comparison report
    create_comparison_report(results)
    
    # Save results
    output_dir = save_results(results)
    
    return results, output_dir


def interactive_batch_mode():
    """Interactive mode for batch analysis."""
    print("\n" + "=" * 100)
    print(" " * 30 + "BATCH POLICY ANALYZER")
    print("=" * 100)
    print("\nAnalyze multiple company policies at once!")
    print("\nHow to use:")
    print("  1. Enter number of companies to analyze")
    print("  2. For each company, provide name and paste policy text")
    print("  3. Get comprehensive comparison report")
    print("=" * 100)
    
    try:
        num_companies = int(input("\nHow many companies do you want to analyze? "))
    except ValueError:
        print("Invalid number. Exiting.")
        return
    
    if num_companies < 1 or num_companies > 20:
        print("Please enter a number between 1 and 20.")
        return
    
    companies = {}
    
    for i in range(num_companies):
        print(f"\n--- Company {i+1}/{num_companies} ---")
        company_name = input("Company name: ").strip()
        
        if not company_name:
            company_name = f"Company_{i+1}"
        
        print(f"\nPaste policy text for {company_name}")
        print("(Press Ctrl+D on Mac/Linux or Ctrl+Z then Enter on Windows when done)")
        print("-" * 80)
        
        policy_lines = []
        try:
            while True:
                policy_lines.append(input())
        except EOFError:
            pass
        
        policy_text = "\n".join(policy_lines)
        
        if not policy_text.strip():
            print(f"⚠️  No text entered for {company_name}. Skipping.")
            continue
        
        companies[company_name] = policy_text
        print(f"✓ Added {company_name} ({len(policy_text)} characters)")
    
    if not companies:
        print("\n❌ No companies to analyze. Exiting.")
        return
    
    # Analyze all companies
    results = analyze_batch_from_dict(companies)
    
    # Show comparison
    create_comparison_report(results)
    
    # Offer to save
    save = input("\n💾 Save results to files? (y/n): ").strip().lower()
    if save == 'y':
        save_results(results)
        print("\n✅ Results saved! Check the 'analysis_results' folder.")


def main():
    """Main function - choose between example or interactive mode."""
    print("\n" + "=" * 100)
    print(" " * 25 + "BATCH POLICY ANALYZER - MAIN MENU")
    print("=" * 100)
    print("\nOptions:")
    print("  1. Run example batch analysis (4 sample companies)")
    print("  2. Interactive batch analysis (analyze your own companies)")
    print("  3. Exit")
    print("=" * 100)
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🚀 Running example batch analysis...")
        example_batch_analysis()
        
    elif choice == '2':
        interactive_batch_mode()
        
    elif choice == '3':
        print("\n👋 Goodbye!")
        
    else:
        print("\n❌ Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled. Goodbye!")
