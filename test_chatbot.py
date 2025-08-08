#!/usr/bin/env python3
"""
Test script for the AdTech Campaign Health Analyzer
This script tests the core functionality without requiring the Streamlit interface
"""

import os
import sys
from dataclasses import dataclass
from app import ClientInfo, CampaignEvaluator

def test_basic_functionality():
    """Test basic campaign analyzer functionality with sample data"""
    print("🧪 Testing AdTech Campaign Health Analyzer\n")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key: export OPENAI_API_KEY='your_key_here'")
        return False
    
    print("✅ API key found")
    
    # Create sample campaign data
    sample_campaign = ClientInfo(
        company_name="TechCorp Solutions",
        account_manager="Sarah Johnson",
        monthly_budget=50000.0,
        campaign_duration_months=6,
        campaign_objectives="Brand awareness and lead generation for new product launch",
        current_performance_metrics="CTR: 2.3%, CPA: $45, ROAS: 3.2x, 500K impressions/week",
        budget_utilization="85% spend rate, on track for monthly goals",
        client_reported_notes="Happy with performance, seeing good quality leads",
        recent_changes_or_concerns="No major concerns, interested in expanding to new markets"
    )
    
    print(f"📊 Testing with sample campaign: {sample_campaign.company_name}")
    print(f"   Budget: ${sample_campaign.monthly_budget:,.2f}/month")
    print(f"   Duration: {sample_campaign.campaign_duration_months} months")
    print()
    
    # Create evaluator and test
    try:
        evaluator = CampaignEvaluator()
        print("🔍 Running campaign evaluation...")
        
        evaluation = evaluator.evaluate_client(sample_campaign)
        
        print("✅ Evaluation completed successfully!")
        print("\n📊 Results:")
        print(f"   Category: {evaluation.get('category', 'Unknown')}")
        print(f"   Confidence: {evaluation.get('confidence', 'Unknown')}%")
        print(f"   Reasoning: {evaluation.get('reasoning', 'No reasoning provided')[:100]}...")
        
        recommendations = evaluation.get('recommendations', [])
        if recommendations:
            print(f"   Action Items: {len(recommendations)} provided")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during evaluation: {str(e)}")
        return False

def test_edge_cases():
    """Test edge cases and validation"""
    print("\n🧪 Testing edge cases...\n")
    
    # Test with minimal information
    minimal_campaign = ClientInfo(
        company_name="RetailPlus Inc",
        account_manager="Mike Chen",
        monthly_budget=25000.0,
        campaign_duration_months=3,
        campaign_objectives="Drive holiday sales",
        current_performance_metrics="",
        budget_utilization="95% spend, burning through budget quickly",
        client_reported_notes="Concerned about high costs",
        recent_changes_or_concerns=""
    )
    
    try:
        evaluator = CampaignEvaluator()
        evaluation = evaluator.evaluate_client(minimal_campaign)
        print("✅ Minimal information test passed")
        print(f"   Category: {evaluation.get('category', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Minimal information test failed: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("=" * 60)
    print("ADTECH CAMPAIGN HEALTH ANALYZER - TEST SUITE")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # Run tests
    if test_basic_functionality():
        success_count += 1
    
    if test_edge_cases():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The campaign analyzer is ready to use.")
        print("\nTo start the web interface, run:")
        print("   streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)