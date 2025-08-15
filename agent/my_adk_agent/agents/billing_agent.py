"""
Billing Agent - Google ADK Framework Integration
Handles resource tracking, invoice generation, and payment processing with Saudi VAT
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import logging
import uuid

# Import mock Google ADK for development
try:
    from google.adk import Agent, tool
    from google.generativeai import GenerativeModel
except ImportError:
    from ..mock_google_adk import Agent, tool, MockGenerativeModel as GenerativeModel

from ..services.supabase_service import SupabaseService
from ..services.stripe_service import StripeService
from ..models.billing import ResourceUsage, Invoice, BillingCycle

logger = logging.getLogger(__name__)

class BillingAgent(Agent):
    """
    Comprehensive billing agent using Google ADK
    - Tracks resource usage (compute, storage, AI tokens, agent hours)
    - Generates invoices with Saudi VAT (15%)
    - Manages automated billing cycles
    - Integrates with Stripe for payment processing
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="BillingAgent",
            description="Handles billing, resource tracking, and payment processing",
            model=GenerativeModel("gemini-2.0-flash-exp"),
            system_prompt=self._get_system_prompt()
        )
        
        self.config = config
        self.supabase = SupabaseService(config)
        self.stripe = StripeService(config)
        
        # Resource pricing in SAR
        self.pricing = {
            "compute_hours": Decimal("0.05"),      # SAR per CPU hour
            "storage_gb": Decimal("0.10"),         # SAR per GB/month
            "network_gb": Decimal("0.01"),         # SAR per GB transfer
            "ai_tokens": Decimal("0.002"),         # SAR per 1K tokens
            "agent_hours": Decimal("25.00"),       # SAR per agent hour
            "workflow_executions": Decimal("0.50"), # SAR per execution
            "live_sessions": Decimal("5.00"),      # SAR per session minute
            "file_processing": Decimal("0.10"),    # SAR per file processed
        }
        
        # Saudi VAT rate
        self.vat_rate = Decimal("0.15")  # 15%
        
    def _get_system_prompt(self) -> str:
        return """
        أنت وكيل الفوترة الذكي المتخصص في إدارة الموارد والفوترة الشاملة لشركة consulting.sa
        You are an intelligent Billing Agent specialized in comprehensive resource management and billing for consulting.sa
        
        قدراتك الأساسية / Your main capabilities:
        1. تتبع استخدام الموارد في الوقت الفعلي / Real-time resource usage tracking
        2. حساب التكاليف بدقة حسب الاستخدام / Accurate usage-based cost calculation
        3. إنشاء فواتير مفصلة مع ضريبة القيمة المضافة (15%) / Generate detailed invoices with VAT (15%)
        4. إدارة دورات الفوترة التلقائية / Manage automated billing cycles
        5. معالجة المدفوعات عبر Stripe / Process payments via Stripe
        6. تقديم تقارير مالية شاملة / Provide comprehensive financial reports
        
        أنواع الموارد المتتبعة / Tracked Resource Types:
        - ساعات المعالجة / Compute Hours: 0.05 ريال/ساعة
        - التخزين / Storage: 0.10 ريال/جيجابايت/شهر
        - نقل البيانات / Network Transfer: 0.01 ريال/جيجابايت
        - رموز الذكاء الاصطناعي / AI Tokens: 0.002 ريال/1000 رمز
        - ساعات الوكيل / Agent Hours: 25 ريال/ساعة
        - تنفيذ سير العمل / Workflow Executions: 0.50 ريال/تنفيذ
        - الجلسات المباشرة / Live Sessions: 5 ريال/دقيقة
        - معالجة الملفات / File Processing: 0.10 ريال/ملف
        
        قواعد الفوترة / Billing Rules:
        1. جميع الأسعار بالريال السعودي / All prices in Saudi Riyal (SAR)
        2. ضريبة القيمة المضافة 15% / VAT rate is 15%
        3. الفوترة الشهرية تلقائياً / Monthly billing automatically
        4. دعم الدفع عبر Stripe / Payment processing via Stripe
        5. تقارير مفصلة للاستخدام / Detailed usage reports
        
        عند التعامل مع العملاء / When dealing with customers:
        - قدم معلومات واضحة عن التكاليف / Provide clear cost information
        - اشرح تفاصيل الفاتورة / Explain invoice details
        - ساعد في إعداد طرق الدفع / Help setup payment methods
        - قدم تقارير الاستخدام / Provide usage reports
        - اعرض خيارات التوفير / Suggest cost-saving options
        """
    
    @tool
    async def track_resource_usage(self, customer_id: str, resource_type: str, quantity: float, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Track resource usage for billing
        
        Args:
            customer_id: Customer identifier
            resource_type: Type of resource (compute_hours, storage_gb, ai_tokens, etc.)
            quantity: Amount of resource used
            metadata: Additional metadata about the usage
        """
        try:
            # Get unit price for resource type
            unit_price = self.pricing.get(resource_type, Decimal("0"))
            total_cost = Decimal(str(quantity)) * unit_price
            
            # Create usage record
            usage_data = {
                "customer_id": customer_id,
                "resource_type": resource_type,
                "quantity": float(quantity),
                "unit_price": float(unit_price),
                "total_cost": float(total_cost),
                "currency": "SAR",
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store in database
            usage = await self.supabase.create_resource_usage(usage_data)
            
            logger.info(f"Tracked {resource_type} usage: {quantity} units for customer {customer_id}")
            
            return {
                "success": True,
                "usage_id": usage.id,
                "resource_type": resource_type,
                "quantity": quantity,
                "unit_price": float(unit_price),
                "total_cost": float(total_cost),
                "currency": "SAR"
            }
            
        except Exception as e:
            logger.error(f"Error tracking resource usage: {e}")
            return {
                "success": False,
                "error": "خطأ في تتبع استخدام الموارد" if metadata and metadata.get("language") == "ar" else "Error tracking resource usage"
            }
    
    @tool
    async def get_usage_summary(self, customer_id: str, period_days: int = 30, language: str = "ar") -> Dict[str, Any]:
        """
        Get resource usage summary for customer
        
        Args:
            customer_id: Customer identifier
            period_days: Number of days to include in summary
            language: Response language
        """
        try:
            # Get usage records for period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            usage_records = await self.supabase.get_usage_for_period(
                customer_id, start_date, end_date
            )
            
            # Calculate summary by resource type
            summary = {}
            total_cost = Decimal("0")
            
            for usage in usage_records:
                resource_type = usage.resource_type
                if resource_type not in summary:
                    summary[resource_type] = {
                        "quantity": 0,
                        "cost": Decimal("0"),
                        "unit": self._get_resource_unit(resource_type)
                    }
                
                summary[resource_type]["quantity"] += usage.quantity
                summary[resource_type]["cost"] += Decimal(str(usage.total_cost))
                total_cost += Decimal(str(usage.total_cost))
            
            # Format response
            if language == "ar":
                response = {
                    "success": True,
                    "period": f"{period_days} أيام",
                    "total_cost": float(total_cost),
                    "currency": "ريال سعودي",
                    "resources": {}
                }
                
                for resource_type, data in summary.items():
                    resource_name = self._get_arabic_resource_name(resource_type)
                    response["resources"][resource_name] = {
                        "quantity": data["quantity"],
                        "unit": data["unit"],
                        "cost": float(data["cost"])
                    }
            else:
                response = {
                    "success": True,
                    "period": f"{period_days} days",
                    "total_cost": float(total_cost),
                    "currency": "SAR",
                    "resources": {}
                }
                
                for resource_type, data in summary.items():
                    response["resources"][resource_type] = {
                        "quantity": data["quantity"],
                        "unit": data["unit"],
                        "cost": float(data["cost"])
                    }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting usage summary: {e}")
            return {
                "success": False,
                "error": "خطأ في جلب ملخص الاستخدام" if language == "ar" else "Error getting usage summary"
            }
    
    @tool
    async def generate_invoice(self, customer_id: str, billing_period_start: str, billing_period_end: str, language: str = "ar") -> Dict[str, Any]:
        """
        Generate invoice for customer billing period
        
        Args:
            customer_id: Customer identifier
            billing_period_start: Start date (ISO format)
            billing_period_end: End date (ISO format)
            language: Response language
        """
        try:
            # Parse dates
            start_date = datetime.fromisoformat(billing_period_start.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(billing_period_end.replace('Z', '+00:00'))
            
            # Get customer information
            customer = await self.supabase.get_customer(customer_id)
            if not customer:
                return {
                    "success": False,
                    "error": "العميل غير موجود" if language == "ar" else "Customer not found"
                }
            
            # Get usage records for period
            usage_records = await self.supabase.get_usage_for_period(
                customer_id, start_date, end_date
            )
            
            if not usage_records:
                return {
                    "success": False,
                    "error": "لا توجد بيانات استخدام للفترة المحددة" if language == "ar" else "No usage data for specified period"
                }
            
            # Calculate invoice totals
            line_items = []
            subtotal = Decimal("0")
            
            # Group usage by resource type
            usage_by_type = {}
            for usage in usage_records:
                resource_type = usage.resource_type
                if resource_type not in usage_by_type:
                    usage_by_type[resource_type] = {
                        "quantity": 0,
                        "total_cost": Decimal("0")
                    }
                usage_by_type[resource_type]["quantity"] += usage.quantity
                usage_by_type[resource_type]["total_cost"] += Decimal(str(usage.total_cost))
            
            # Create line items
            for resource_type, data in usage_by_type.items():
                unit_price = self.pricing.get(resource_type, Decimal("0"))
                line_item = {
                    "description": self._get_resource_description(resource_type, language),
                    "quantity": data["quantity"],
                    "unit": self._get_resource_unit(resource_type),
                    "unit_price": float(unit_price),
                    "total_price": float(data["total_cost"])
                }
                line_items.append(line_item)
                subtotal += data["total_cost"]
            
            # Calculate VAT and total
            vat_amount = subtotal * self.vat_rate
            total_amount = subtotal + vat_amount
            
            # Generate invoice number
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Create invoice record
            invoice_data = {
                "invoice_number": invoice_number,
                "customer_id": customer_id,
                "customer_name": customer.name,
                "customer_email": customer.email,
                "line_items": line_items,
                "subtotal": float(subtotal),
                "vat_rate": float(self.vat_rate),
                "vat_amount": float(vat_amount),
                "total_amount": float(total_amount),
                "currency": "SAR",
                "status": "draft",
                "billing_period_start": start_date.isoformat(),
                "billing_period_end": end_date.isoformat(),
                "issue_date": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            # Store invoice
            invoice = await self.supabase.create_invoice(invoice_data)
            
            logger.info(f"Generated invoice {invoice_number} for customer {customer_id}")
            
            return {
                "success": True,
                "invoice_id": invoice.id,
                "invoice_number": invoice_number,
                "subtotal": float(subtotal),
                "vat_amount": float(vat_amount),
                "total_amount": float(total_amount),
                "currency": "SAR",
                "line_items": line_items,
                "due_date": invoice_data["due_date"],
                "message": "تم إنشاء الفاتورة بنجاح" if language == "ar" else "Invoice generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return {
                "success": False,
                "error": "خطأ في إنشاء الفاتورة" if language == "ar" else "Error generating invoice"
            }
    
    @tool
    async def setup_payment_method(self, customer_id: str, payment_method_data: Dict[str, Any], language: str = "ar") -> Dict[str, Any]:
        """
        Setup payment method for customer using Stripe
        
        Args:
            customer_id: Customer identifier
            payment_method_data: Payment method information
            language: Response language
        """
        try:
            # Create or get Stripe customer
            stripe_customer = await self.stripe.get_or_create_customer(customer_id)
            
            # Setup payment method
            payment_method = await self.stripe.setup_payment_method(
                stripe_customer.id, payment_method_data
            )
            
            # Store payment method reference
            await self.supabase.store_payment_method(customer_id, {
                "stripe_customer_id": stripe_customer.id,
                "stripe_payment_method_id": payment_method.id,
                "type": payment_method.type,
                "last_four": payment_method.card.last4 if payment_method.card else None,
                "brand": payment_method.card.brand if payment_method.card else None
            })
            
            return {
                "success": True,
                "payment_method_id": payment_method.id,
                "type": payment_method.type,
                "message": "تم إعداد طريقة الدفع بنجاح" if language == "ar" else "Payment method setup successfully"
            }
            
        except Exception as e:
            logger.error(f"Error setting up payment method: {e}")
            return {
                "success": False,
                "error": "خطأ في إعداد طريقة الدفع" if language == "ar" else "Error setting up payment method"
            }
    
    @tool
    async def process_payment(self, invoice_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Process payment for invoice
        
        Args:
            invoice_id: Invoice identifier
            language: Response language
        """
        try:
            # Get invoice
            invoice = await self.supabase.get_invoice(invoice_id)
            if not invoice:
                return {
                    "success": False,
                    "error": "الفاتورة غير موجودة" if language == "ar" else "Invoice not found"
                }
            
            # Get customer payment method
            payment_method = await self.supabase.get_customer_payment_method(invoice.customer_id)
            if not payment_method:
                return {
                    "success": False,
                    "error": "لا توجد طريقة دفع مسجلة" if language == "ar" else "No payment method on file"
                }
            
            # Process payment via Stripe
            payment_result = await self.stripe.process_payment(
                amount=int(invoice.total_amount * 100),  # Convert to cents
                currency="sar",
                customer_id=payment_method.stripe_customer_id,
                payment_method_id=payment_method.stripe_payment_method_id,
                description=f"Invoice {invoice.invoice_number}"
            )
            
            if payment_result.status == "succeeded":
                # Update invoice status
                await self.supabase.update_invoice(invoice_id, {
                    "status": "paid",
                    "paid_date": datetime.now().isoformat(),
                    "payment_method": payment_method.type,
                    "stripe_payment_intent_id": payment_result.id
                })
                
                return {
                    "success": True,
                    "payment_id": payment_result.id,
                    "amount": invoice.total_amount,
                    "currency": "SAR",
                    "message": "تم الدفع بنجاح" if language == "ar" else "Payment processed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "فشل في معالجة الدفع" if language == "ar" else "Payment processing failed"
                }
                
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return {
                "success": False,
                "error": "خطأ في معالجة الدفع" if language == "ar" else "Error processing payment"
            }
    
    def _get_resource_unit(self, resource_type: str) -> str:
        """Get unit for resource type"""
        units = {
            "compute_hours": "hours",
            "storage_gb": "GB",
            "network_gb": "GB",
            "ai_tokens": "1K tokens",
            "agent_hours": "hours",
            "workflow_executions": "executions",
            "live_sessions": "minutes",
            "file_processing": "files"
        }
        return units.get(resource_type, "units")
    
    def _get_resource_description(self, resource_type: str, language: str = "ar") -> str:
        """Get description for resource type"""
        if language == "ar":
            descriptions = {
                "compute_hours": "ساعات المعالجة",
                "storage_gb": "التخزين",
                "network_gb": "نقل البيانات",
                "ai_tokens": "رموز الذكاء الاصطناعي",
                "agent_hours": "ساعات الوكيل",
                "workflow_executions": "تنفيذ سير العمل",
                "live_sessions": "الجلسات المباشرة",
                "file_processing": "معالجة الملفات"
            }
        else:
            descriptions = {
                "compute_hours": "Compute Hours",
                "storage_gb": "Storage Usage",
                "network_gb": "Network Transfer",
                "ai_tokens": "AI Token Usage",
                "agent_hours": "Agent Processing Hours",
                "workflow_executions": "Workflow Executions",
                "live_sessions": "Live Sessions",
                "file_processing": "File Processing"
            }
        
        return descriptions.get(resource_type, resource_type.replace('_', ' ').title())
    
    def _get_arabic_resource_name(self, resource_type: str) -> str:
        """Get Arabic name for resource type"""
        arabic_names = {
            "compute_hours": "ساعات المعالجة",
            "storage_gb": "التخزين",
            "network_gb": "نقل البيانات",
            "ai_tokens": "رموز الذكاء الاصطناعي",
            "agent_hours": "ساعات الوكيل",
            "workflow_executions": "تنفيذ سير العمل",
            "live_sessions": "الجلسات المباشرة",
            "file_processing": "معالجة الملفات"
        }
        return arabic_names.get(resource_type, resource_type)
    
    async def process_billing_message(self, message: str, customer_id: str, language: str = "ar") -> Dict[str, Any]:
        """
        Process billing-related customer messages
        
        Args:
            message: Customer message
            customer_id: Customer identifier
            language: Customer language
            
        Returns:
            Response dictionary
        """
        try:
            # Generate response using Gemini with billing context
            context = f"""
            Customer ID: {customer_id}
            Language: {language}
            Message: {message}
            Available Actions: track_usage, get_usage_summary, generate_invoice, setup_payment_method, process_payment
            """
            
            response = await self.model.generate_content_async(
                f"{self.system_prompt}\n\nContext: {context}\n\nRespond with billing assistance:"
            )
            
            # Determine if specific actions are needed
            actions = self._determine_billing_actions(message, language)
            
            return {
                "content": response.text,
                "language": language,
                "actions": actions,
                "agent_type": "billing"
            }
            
        except Exception as e:
            logger.error(f"Error processing billing message: {e}")
            return {
                "content": "عذراً، حدث خطأ في معالجة طلب الفوترة" if language == "ar" else "Sorry, an error occurred processing your billing request",
                "language": language,
                "actions": [],
                "agent_type": "billing"
            }
    
    def _determine_billing_actions(self, message: str, language: str) -> List[Dict[str, Any]]:
        """Determine billing-specific actions based on message"""
        actions = []
        message_lower = message.lower()
        
        # Check for usage inquiry
        usage_keywords_ar = ["استخدام", "موارد", "تكلفة", "فاتورة"]
        usage_keywords_en = ["usage", "resources", "cost", "bill", "invoice"]
        
        if any(keyword in message_lower for keyword in usage_keywords_ar + usage_keywords_en):
            actions.append({
                "type": "show_usage_summary",
                "priority": "high"
            })
        
        # Check for payment requests
        payment_keywords_ar = ["دفع", "سداد", "طريقة الدفع"]
        payment_keywords_en = ["payment", "pay", "payment method"]
        
        if any(keyword in message_lower for keyword in payment_keywords_ar + payment_keywords_en):
            actions.append({
                "type": "setup_payment",
                "priority": "high"
            })
        
        # Check for invoice requests
        invoice_keywords_ar = ["فاتورة", "كشف حساب"]
        invoice_keywords_en = ["invoice", "statement", "bill"]
        
        if any(keyword in message_lower for keyword in invoice_keywords_ar + invoice_keywords_en):
            actions.append({
                "type": "generate_invoice",
                "priority": "medium"
            })
        
        return actions