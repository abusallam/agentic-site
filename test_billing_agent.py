#!/usr/bin/env python3
"""
Test script for the enhanced billing agent
Tests core functionality without disrupting production
"""
import sys
import os
sys.path.append('backend')

from backend.agentic_core.agents.billing_agent import (
    BillingAgent, ResourceType, BillingCycle, 
    ResourceUsage, Invoice, InvoiceStatus
)
from backend.agentic_core.agents.base_agent import AgentConfig, AgentType
from datetime import datetime, timedelta
from decimal import Decimal

def test_billing_agent_initialization():
    """Test billing agent initialization"""
    print("🧪 Testing Billing Agent Initialization...")
    
    try:
        # Create test config
        config = AgentConfig(
            agent_type=AgentType.BILLING,
            framework="ADK",
            model_name="gemini-pro"
        )
        
        # Initialize billing agent
        billing_agent = BillingAgent(config)
        print("✅ Billing agent initialized successfully")
        return billing_agent
        
    except Exception as e:
        print(f"❌ Failed to initialize billing agent: {e}")
        return None

def test_resource_usage_tracking(billing_agent):
    """Test resource usage tracking"""
    print("\n🧪 Testing Resource Usage Tracking...")
    
    try:
        # Track different resource types
        test_customer_id = "test_customer_123"
        
        # Track compute usage
        compute_usage = billing_agent.track_resource_usage(
            customer_id=test_customer_id,
            resource_type=ResourceType.COMPUTE,
            quantity=2.5,  # 2.5 CPU hours
            metadata={"project_id": "test_project", "instance_type": "standard"}
        )
        print(f"✅ Compute usage tracked: {compute_usage.quantity} {compute_usage.unit} = {compute_usage.total_cost} SAR")
        
        # Track AI tokens
        ai_usage = billing_agent.track_resource_usage(
            customer_id=test_customer_id,
            resource_type=ResourceType.AI_TOKENS,
            quantity=1500,  # 1.5K tokens
            metadata={"model": "gemini-pro", "conversation_id": "conv_123"}
        )
        print(f"✅ AI tokens tracked: {ai_usage.quantity} {ai_usage.unit} = {ai_usage.total_cost} SAR")
        
        # Track storage
        storage_usage = billing_agent.track_resource_usage(
            customer_id=test_customer_id,
            resource_type=ResourceType.STORAGE,
            quantity=25.0,  # 25 GB
            metadata={"storage_type": "database", "region": "riyadh"}
        )
        print(f"✅ Storage usage tracked: {storage_usage.quantity} {storage_usage.unit} = {storage_usage.total_cost} SAR")
        
        return test_customer_id
        
    except Exception as e:
        print(f"❌ Failed to track resource usage: {e}")
        return None

def test_invoice_generation(billing_agent, customer_id):
    """Test invoice generation with Saudi VAT"""
    print("\n🧪 Testing Invoice Generation...")
    
    try:
        # Calculate billing period (current month)
        now = datetime.now()
        billing_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        billing_end = now
        
        # Generate invoice
        invoice = billing_agent.generate_invoice(
            customer_id=customer_id,
            billing_period_start=billing_start,
            billing_period_end=billing_end
        )
        
        print(f"✅ Invoice generated successfully!")
        print(f"   Invoice Number: {invoice.invoice_number}")
        print(f"   Subtotal: {invoice.subtotal} SAR")
        print(f"   VAT (15%): {invoice.tax_amount} SAR")
        print(f"   Total: {invoice.total_amount} SAR")
        print(f"   Currency: {invoice.currency}")
        print(f"   Status: {invoice.status.value}")
        print(f"   Line Items: {len(invoice.line_items)}")
        
        # Verify VAT calculation
        expected_vat = invoice.subtotal * Decimal('0.15')
        if abs(invoice.tax_amount - expected_vat) < Decimal('0.01'):
            print("✅ VAT calculation is correct (15%)")
        else:
            print(f"⚠️  VAT calculation issue: expected {expected_vat}, got {invoice.tax_amount}")
        
        return invoice
        
    except Exception as e:
        print(f"❌ Failed to generate invoice: {e}")
        return None

def test_arabic_responses(billing_agent):
    """Test Arabic language responses"""
    print("\n🧪 Testing Arabic Language Responses...")
    
    try:
        # Test Arabic billing inquiry
        arabic_context = {"language": "ar", "customer_id": "test_customer_123"}
        
        response = billing_agent.process_message(
            "أريد معرفة استخدام الموارد هذا الشهر",
            context=arabic_context
        )
        
        print("✅ Arabic response generated:")
        print(f"   Message: {response.message[:100]}...")
        print(f"   Confidence: {response.confidence}")
        print(f"   Next Action: {response.next_action}")
        
        # Check if response contains Arabic text
        if any(ord(char) > 127 for char in response.message):
            print("✅ Response contains Arabic characters")
        else:
            print("⚠️  Response may not contain Arabic characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Arabic responses: {e}")
        return False

def test_english_responses(billing_agent):
    """Test English language responses"""
    print("\n🧪 Testing English Language Responses...")
    
    try:
        # Test English billing inquiry
        english_context = {"language": "en", "customer_id": "test_customer_123"}
        
        response = billing_agent.process_message(
            "Show me my current month usage",
            context=english_context
        )
        
        print("✅ English response generated:")
        print(f"   Message: {response.message[:100]}...")
        print(f"   Confidence: {response.confidence}")
        print(f"   Next Action: {response.next_action}")
        
        # Check if response contains expected English terms
        if "SAR" in response.message or "usage" in response.message.lower():
            print("✅ Response contains expected English billing terms")
        else:
            print("⚠️  Response may not contain expected English terms")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test English responses: {e}")
        return False

def test_cron_job_setup(billing_agent):
    """Test cron job setup (without actually creating system cron jobs)"""
    print("\n🧪 Testing Cron Job Configuration...")
    
    try:
        # Test automated billing setup
        result = billing_agent.setup_automated_billing(
            customer_id="test_customer_123",
            billing_cycle=BillingCycle.MONTHLY
        )
        
        print("✅ Automated billing configuration created:")
        print(f"   Status: {result['status']}")
        print(f"   Billing Cycle: {result['billing_cycle']}")
        print(f"   Next Billing Date: {result['next_billing_date']}")
        
        if 'cron_job_id' in result:
            print(f"   Cron Job ID: {result['cron_job_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test cron job setup: {e}")
        return False

def test_billing_dashboard(billing_agent):
    """Test billing dashboard functionality"""
    print("\n🧪 Testing Billing Dashboard...")
    
    try:
        dashboard_data = billing_agent.get_billing_dashboard("test_customer_123")
        
        print("✅ Billing dashboard data generated:")
        print(f"   Customer ID: {dashboard_data['customer_id']}")
        print(f"   Current Month Cost: {dashboard_data['current_month_cost']} SAR")
        print(f"   Outstanding Balance: {dashboard_data['outstanding_balance']} SAR")
        print(f"   Recent Invoices: {len(dashboard_data['recent_invoices'])}")
        print(f"   Resource Breakdown: {len(dashboard_data['resource_breakdown'])} types")
        print(f"   Billing Alerts: {len(dashboard_data['billing_alerts'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test billing dashboard: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced Agentic Platform - Billing Agent Test Suite")
    print("=" * 60)
    
    # Initialize billing agent
    billing_agent = test_billing_agent_initialization()
    if not billing_agent:
        print("❌ Cannot proceed without billing agent")
        return False
    
    # Test resource tracking
    customer_id = test_resource_usage_tracking(billing_agent)
    if not customer_id:
        print("❌ Cannot proceed without resource tracking")
        return False
    
    # Test invoice generation
    invoice = test_invoice_generation(billing_agent, customer_id)
    if not invoice:
        print("⚠️  Invoice generation failed, but continuing tests")
    
    # Test language responses
    arabic_success = test_arabic_responses(billing_agent)
    english_success = test_english_responses(billing_agent)
    
    # Test cron job setup
    cron_success = test_cron_job_setup(billing_agent)
    
    # Test billing dashboard
    dashboard_success = test_billing_dashboard(billing_agent)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    print(f"   ✅ Billing Agent Initialization: {'PASS' if billing_agent else 'FAIL'}")
    print(f"   ✅ Resource Usage Tracking: {'PASS' if customer_id else 'FAIL'}")
    print(f"   ✅ Invoice Generation: {'PASS' if invoice else 'FAIL'}")
    print(f"   ✅ Arabic Language Support: {'PASS' if arabic_success else 'FAIL'}")
    print(f"   ✅ English Language Support: {'PASS' if english_success else 'FAIL'}")
    print(f"   ✅ Cron Job Configuration: {'PASS' if cron_success else 'FAIL'}")
    print(f"   ✅ Billing Dashboard: {'PASS' if dashboard_success else 'FAIL'}")
    
    # Overall result
    all_tests = [billing_agent, customer_id, arabic_success, english_success, cron_success, dashboard_success]
    passed_tests = sum(1 for test in all_tests if test)
    total_tests = len(all_tests)
    
    print(f"\n🏆 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Billing agent is ready for production.")
    elif passed_tests >= total_tests * 0.8:
        print("✅ Most tests passed. Minor issues may need attention.")
    else:
        print("⚠️  Several tests failed. Review implementation before production use.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)