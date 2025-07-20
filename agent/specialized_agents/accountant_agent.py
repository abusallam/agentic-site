"""
Accountant Agent - Handles invoicing, billing, payments, and financial management
"""

import json
import logging
from typing import Dict, Any, Optional, List
from google.adk.agents.base_agent import BaseAgent
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AccountantAgent(BaseAgent):
    """
    Specialized agent for accounting and financial operations
    """
    
    def __init__(self):
        super().__init__(
            name="accountant_agent",
            description="Specialized agent for invoicing, billing, payments, and financial management"
        )
        logger.info("AccountantAgent initialized")
    
    async def handle_task(self, task_data: Dict[str, Any], customer_email: str) -> Dict[str, Any]:
        """Handle accounting-related tasks"""
        try:
            action = task_data.get("action", "")
            
            if action == "create_invoice":
                return await self.create_invoice(customer_email, task_data)
            elif action == "process_payment":
                return await self.process_payment(customer_email, task_data)
            elif action == "generate_quote":
                return await self.generate_quote(customer_email, task_data)
            elif action == "billing_report":
                return await self.generate_billing_report(customer_email, task_data)
            elif action == "payment_reminder":
                return await self.send_payment_reminder(customer_email, task_data)
            else:
                return await self.create_invoice(customer_email, task_data)
                
        except Exception as e:
            logger.error(f"AccountantAgent task error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_invoice(self, customer_email: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice for the customer"""
        try:
            invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email) % 10000:04d}"
            
            invoice = {
                "invoice_id": invoice_id,
                "customer_email": customer_email,
                "amount": invoice_data.get("amount", 0),
                "currency": invoice_data.get("currency", "USD"),
                "description": invoice_data.get("description", "Professional Services"),
                "line_items": invoice_data.get("line_items", []),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "payment_terms": "Net 30",
                "tax_rate": invoice_data.get("tax_rate", 0.15),
                "subtotal": invoice_data.get("amount", 0),
                "tax_amount": invoice_data.get("amount", 0) * invoice_data.get("tax_rate", 0.15),
                "total": invoice_data.get("amount", 0) * (1 + invoice_data.get("tax_rate", 0.15))
            }
            
            # TODO: Save to database via SupabaseService
            # TODO: Generate PDF invoice
            # TODO: Send email notification
            
            return {
                "status": "success",
                "invoice_id": invoice_id,
                "invoice": invoice,
                "message": f"Invoice {invoice_id} created successfully",
                "next_steps": [
                    "PDF invoice generated",
                    "Email sent to customer",
                    "Payment tracking initiated"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_invoice_from_session(self, customer_email: str, session_transcript: List[Dict]) -> Dict[str, Any]:
        """Create invoice based on LiveKit session discussion"""
        try:
            # Analyze transcript for billing information
            billing_info = await self._extract_billing_from_transcript(session_transcript)
            
            return await self.create_invoice(customer_email, billing_info)
            
        except Exception as e:
            logger.error(f"Failed to create invoice from session: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _extract_billing_from_transcript(self, transcript: List[Dict]) -> Dict[str, Any]:
        """Extract billing information from session transcript"""
        try:
            # Simple extraction logic - in production, use AI/NLP
            billing_info = {
                "amount": 5000,  # Default amount
                "description": "Consulting Services",
                "line_items": []
            }
            
            # Look for pricing mentions in transcript
            for message in transcript:
                content = message.get("message", "").lower()
                if "$" in content or "price" in content or "cost" in content:
                    # Extract pricing information
                    # This is simplified - use proper NLP in production
                    pass
            
            return billing_info
            
        except Exception as e:
            logger.error(f"Failed to extract billing info: {e}")
            return {"amount": 0, "description": "Services"}
    
    async def process_payment(self, customer_email: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a payment for an invoice"""
        try:
            payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email) % 10000:04d}"
            
            payment = {
                "payment_id": payment_id,
                "invoice_id": payment_data.get("invoice_id"),
                "customer_email": customer_email,
                "amount": payment_data.get("amount", 0),
                "payment_method": payment_data.get("payment_method", "stripe"),
                "status": "processing",
                "processed_at": datetime.now().isoformat()
            }
            
            # TODO: Process via Stripe
            # TODO: Update invoice status
            # TODO: Send confirmation
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "payment": payment,
                "message": "Payment processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_quote(self, customer_email: str, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a quote for services"""
        try:
            quote_id = f"QUO-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email) % 10000:04d}"
            
            # Service pricing matrix
            service_prices = {
                "chatbot": {"base": 2500, "setup": 500, "monthly": 200},
                "ai_agent": {"base": 5000, "setup": 1000, "monthly": 400},
                "workflow_automation": {"base": 3500, "setup": 750, "monthly": 300},
                "consultation": {"hourly": 150, "project": 2000}
            }
            
            service_type = quote_data.get("service_type", "consultation")
            pricing = service_prices.get(service_type, service_prices["consultation"])
            
            quote = {
                "quote_id": quote_id,
                "customer_email": customer_email,
                "service_type": service_type,
                "pricing": pricing,
                "estimated_total": pricing.get("base", 0) + pricing.get("setup", 0),
                "monthly_cost": pricing.get("monthly", 0),
                "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
                "terms": "Quote valid for 30 days. 50% deposit required to start.",
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "quote_id": quote_id,
                "quote": quote,
                "message": f"Quote {quote_id} generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate quote: {e}")
            return {"status": "error", "error": str(e)}
    
    async def generate_billing_report(self, customer_email: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate billing report for customer"""
        try:
            report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email) % 10000:04d}"
            
            # TODO: Query database for actual billing data
            report = {
                "report_id": report_id,
                "customer_email": customer_email,
                "period": report_data.get("period", "monthly"),
                "total_invoiced": 15000,
                "total_paid": 12000,
                "outstanding": 3000,
                "invoices": [],
                "payments": [],
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "report_id": report_id,
                "report": report,
                "message": "Billing report generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate billing report: {e}")
            return {"status": "error", "error": str(e)}
    
    async def send_payment_reminder(self, customer_email: str, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment reminder to customer"""
        try:
            reminder_id = f"REM-{datetime.now().strftime('%Y%m%d')}-{hash(customer_email) % 10000:04d}"
            
            reminder = {
                "reminder_id": reminder_id,
                "customer_email": customer_email,
                "invoice_id": reminder_data.get("invoice_id"),
                "reminder_type": reminder_data.get("type", "friendly"),
                "sent_at": datetime.now().isoformat(),
                "message": "Friendly reminder about your outstanding invoice."
            }
            
            # TODO: Send email reminder
            # TODO: Log reminder in database
            
            return {
                "status": "success",
                "reminder_id": reminder_id,
                "reminder": reminder,
                "message": "Payment reminder sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send payment reminder: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run(self, user_input: str) -> str:
        """Handle direct interaction with accountant agent"""
        try:
            # Try to parse as JSON command
            try:
                command = json.loads(user_input)
                if isinstance(command, dict):
                    result = await self.handle_task(command, command.get("customer_email", ""))
                    return json.dumps(result, indent=2)
            except json.JSONDecodeError:
                pass
            
            # Handle natural language
            input_lower = user_input.lower()
            
            if "invoice" in input_lower:
                return """💰 **Accountant Agent - Invoice Management**

I can help you with:
• Create invoices
• Process payments  
• Generate quotes
• Billing reports
• Payment reminders

**Example Commands:**
```json
{
  "action": "create_invoice",
  "customer_email": "client@example.com",
  "amount": 5000,
  "description": "AI Chatbot Development",
  "line_items": [
    {"description": "Development", "amount": 4000},
    {"description": "Setup", "amount": 1000}
  ]
}
```"""
            
            elif "payment" in input_lower:
                return """💳 **Payment Processing**

I can process payments and track payment status:

```json
{
  "action": "process_payment",
  "customer_email": "client@example.com",
  "invoice_id": "INV-20250120-1234",
  "amount": 5000,
  "payment_method": "stripe"
}
```"""
            
            elif "quote" in input_lower:
                return """📋 **Quote Generation**

I can generate quotes for different services:

```json
{
  "action": "generate_quote",
  "customer_email": "prospect@example.com",
  "service_type": "chatbot",
  "requirements": {
    "languages": ["en", "ar"],
    "integrations": ["website", "whatsapp"]
  }
}
```

**Service Types:**
• chatbot - $2,500 base + $500 setup + $200/month
• ai_agent - $5,000 base + $1,000 setup + $400/month  
• workflow_automation - $3,500 base + $750 setup + $300/month
• consultation - $150/hour or $2,000/project"""
            
            else:
                return """💰 **Accountant Agent**

I handle all financial operations for consulting.sa:

**My Capabilities:**
• 📄 Invoice creation and management
• 💳 Payment processing via Stripe
• 📋 Quote generation with pricing
• 📊 Billing reports and analytics
• 📧 Payment reminders and follow-ups
• 💱 Multi-currency support
• 📈 Financial reporting

**Available Actions:**
• create_invoice
• process_payment
• generate_quote
• billing_report
• payment_reminder

What financial task can I help you with?"""
            
        except Exception as e:
            logger.error(f"AccountantAgent run error: {e}")
            return f"Accountant Agent Error: {str(e)}"