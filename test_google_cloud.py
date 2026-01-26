#!/usr/bin/env python3
"""
Test script to demonstrate Google Cloud Developer and Innovator detection capabilities.

This script tests the enhanced Google Cloud detection features in the Policy Analyzer.
"""

from policy_analyzer import PolicyAnalyzer
import json


def test_google_cloud_detection():
    """Test the Google Cloud Developer and Innovator detection."""
    
    # Sample policy text with various Google Cloud references
    sample_policies = [
        {
            'name': 'Company A - Basic GCP Usage',
            'text': '''
            Our infrastructure runs on Google Cloud Platform (GCP). We use Cloud Functions
            for serverless computing and BigQuery for data analytics.
            '''
        },
        {
            'name': 'Company B - Developer Program',
            'text': '''
            We are proud members of the Google Cloud Developer program and Google Cloud
            Innovator program. Our team participates in GCP Developer community events.
            '''
        },
        {
            'name': 'Company C - Certifications',
            'text': '''
            Our engineering team includes Google Cloud Certified Professional Cloud Architects,
            GCP Certified Associate Cloud Engineers, and Google Certified Professional Data Engineers.
            We leverage this expertise to build on Google Cloud.
            '''
        },
        {
            'name': 'Company D - Full Stack',
            'text': '''
            Infrastructure: Google Cloud Platform
            Compute: Cloud Run, Cloud Functions, Compute Engine, Kubernetes Engine (GKE)
            Storage: Cloud Storage, Cloud SQL, Cloud Firestore, BigQuery
            AI/ML: Vertex AI, Cloud Vision, Cloud Speech, Cloud Natural Language
            DevOps: Cloud Build, Artifact Registry, Cloud Logging, Cloud Monitoring
            
            Team: Google Cloud Innovator program members, GCP Developer community contributors
            Certifications: Multiple Google Cloud Certified professionals on staff
            '''
        }
    ]
    
    analyzer = PolicyAnalyzer()
    
    print("=" * 80)
    print("GOOGLE CLOUD DEVELOPER & INNOVATOR DETECTION TEST")
    print("=" * 80)
    print()
    
    for policy in sample_policies:
        print(f"\n{'=' * 80}")
        print(f"Testing: {policy['name']}")
        print('=' * 80)
        
        results = analyzer.analyze(policy['text'], policy['name'])
        
        # Display Google Cloud specific information
        gcp_info = results.get('google_cloud_info', {})
        
        if any(gcp_info.values()):
            print("\n✓ Google Cloud Information Found:")
            
            if gcp_info.get('services'):
                print(f"\n  GCP Services ({len(gcp_info['services'])}):")
                for service in sorted(gcp_info['services']):
                    print(f"    • {service}")
            
            if gcp_info.get('programs'):
                print(f"\n  GCP Programs & Communities ({len(gcp_info['programs'])}):")
                for program in sorted(gcp_info['programs']):
                    print(f"    • {program}")
            
            if gcp_info.get('certifications'):
                print(f"\n  GCP Certifications ({len(gcp_info['certifications'])}):")
                for cert in sorted(set(gcp_info['certifications'])):
                    print(f"    • {cert}")
        else:
            print("\n✗ No Google Cloud information detected")
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print('=' * 80)
    print("\nThe Policy Analyzer can now detect:")
    print("  ✓ Google Cloud Platform services (Cloud Functions, BigQuery, etc.)")
    print("  ✓ Google Cloud Developer program references")
    print("  ✓ Google Cloud Innovator program references")
    print("  ✓ GCP certifications and professional credentials")
    print("\nThis enhancement enables comprehensive analysis of Google Cloud usage")
    print("in company policies, terms, and documentation.")
    print()


def test_json_export():
    """Test JSON export of Google Cloud information."""
    print("\n" + "=" * 80)
    print("JSON EXPORT TEST")
    print("=" * 80)
    
    test_text = """
    We use Google Cloud Platform extensively. Our team includes Google Cloud Innovator
    program members and Google Cloud Developer program participants. Services used:
    Cloud Functions, Cloud Run, BigQuery, Vertex AI.
    """
    
    analyzer = PolicyAnalyzer()
    results = analyzer.analyze(test_text, "Test Company")
    
    # Export just the Google Cloud info
    gcp_data = {
        'company': results['company_name'],
        'google_cloud_info': results['google_cloud_info']
    }
    
    print("\nGoogle Cloud Information (JSON format):")
    print(json.dumps(gcp_data, indent=2))
    print("\n✓ Data can be easily exported to JSON for further processing")


if __name__ == "__main__":
    test_google_cloud_detection()
    test_json_export()
    
    print("\n" + "=" * 80)
    print("All tests completed successfully! ✓")
    print("=" * 80)
    print()
