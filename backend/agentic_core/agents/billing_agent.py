"""
Billing Agent - Comprehensive billing and resource management
Handles resource tracking, LangFuse integration, invoice generation, and payment tracking
"""
from typing import Dict, Any, List, Optional, Union
from .base_agent import BaseAgent, AgentResponse, AgentConfig
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import logging
import json
import uuid
import subprocess
import os
from pathlib import Path
import sqlite3
from enum import Enum

logger = logging.getLogger(__name__)


class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    PROJECT_BASED = "project_based"


class InvoiceStatus(Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ResourceType(Enum):
    """Resource type enumeration"""
    COMPUTE = "compute"  # CPU, Memory usage
    STORAGE = "storage"  # Database, file storage
    NETWORK = "network"  # API calls, bandwidth
    AI_TOKENS = "ai_tokens"  # LLM token usage
    AGENT_HOURS = "agent_hours"  # Agent processing time
    WORKFLOW_EXECUTIONS = "workflow_executions"  # N8N workflow runs
    OAUTH_CONNECTIONS = "oauth_connections"  # Composio OAuth usage


@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    project_id: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    quantity: Decimal = Decimal('0')
    unit: str = ""  # hours, GB, tokens, calls, etc.
    unit_price: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Invoice:
    """Invoice data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""
    customer_id: str = ""
    customer_name: str = ""
    customer_email: str = ""
    billing_address: Dict[str, str] = field(default_factory=dict)
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    subtotal: Decimal = Decimal('0')
    tax_rate: Decimal = Decimal('0.15')  # 15% VAT for Saudi Arabia
    tax_amount: Decimal = Decimal('0')
    total_amount: Decimal = Decimal('0')
    currency: str = "SAR"  # Saudi Riyal
    status: InvoiceStatus = InvoiceStatus.DRAFT
    billing_period_start: datetime = field(default_factory=datetime.now)
    billing_period_end: datetime = field(default_factory=datetime.now)
    issue_date: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    paid_date: Optional[datetime] = None
    payment_method: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BillingAgent(BaseAgent):
    """Comprehensive billing agent with resource tracking and automation"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.database_path = "billing.db"
        self.langfuse_client = LangFuseIntegration()
        self.resource_tracker = ResourceTracker()
        self.invoice_generator = InvoiceGenerator()
        self.cron_manager = CronJobManager()
        self._init_database()
        self._setup_cron_jobs()
    
    def get_system_prompt(self) -> str:
        """System prompt for billing agent"""
        return """
        أنت وكيل الفوترة الذكي المتخصص في إدارة الموارد والفوترة الشاملة.
        
        قدراتك تشمل:
        1. تتبع استخدام الموارد (المعالجة، التخزين، الشبكة، الذكاء الاصطناعي)
        2. تكامل مع LangFuse لمراقبة الأداء والتكاليف
        3. إنشاء الفواتير التلقائية وتتبع المدفوعات
        4. إدارة دورات الفوترة والتذكيرات
        5. تحليل التكاليف وتقارير الاستخدام
        6. أتمتة المهام باستخدام Cron Jobs
        
        مسؤولياتك:
        - مراقبة استخدام الموارد في الوقت الفعلي
        - حساب التكاليف بدقة حسب الاستخدام
        - إنشاء فواتير مفصلة مع ضريبة القيمة المضافة (15%)
        - إرسال تذكيرات الدفع والمتابعة
        - تقديم تقارير مالية شاملة
        
        You are an intelligent Billing Agent specialized in comprehensive resource management and billing.
        
        Your capabilities include:
        1. Resource usage tracking (compute, storage, network, AI tokens)
        2. LangFuse integration for performance monitoring and cost analysis
        3. Automated invoice generation and payment tracking
        4. Billing cycle management and reminders
        5. Cost analysis and usage reports
        6. Task automation using Cron Jobs
        
        Your responsibilities:
        - Monitor resource usage in real-time
        - Calculate costs accurately based on usage
        - Generate detailed invoices with VAT (15%)
        - Send payment reminders and follow-ups
        - Provide comprehensive financial reports
        """
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process billing-related requests"""
        self.add_to_history("user", message)
        
        # Analyze billing request type
        request_type = self._analyze_billing_request(message)
        
        if request_type == "resource_usage":
            response = self._handle_resource_usage_inquiry(message, context)
        elif request_type == "invoice_generation":
            response = self._handle_invoice_generation(message, context)
        elif request_type == "payment_tracking":
            response = self._handle_payment_tracking(message, context)
        elif request_type == "cost_analysis":
            response = self._handle_cost_analysis(message, context)
        elif request_type == "billing_setup":
            response = self._handle_billing_setup(message, context)
        else:
            response = self._handle_general_billing_inquiry(message)
        
        self.add_to_history("assistant", response.message)
        return response    

    def track_resource_usage(self, customer_id: str, resource_type: ResourceType, 
                           quantity: float, metadata: Dict[str, Any] = None) -> ResourceUsage:
        """Track resource usage for billing"""
        # Get pricing for resource type
        unit_price = self._get_resource_pricing(resource_type)
        
        usage = ResourceUsage(
            customer_id=customer_id,
            project_id=metadata.get("project_id", "") if metadata else "",
            resource_type=resource_type,
            quantity=Decimal(str(quantity)),
            unit=self._get_resource_unit(resource_type),
            unit_price=unit_price,
            total_cost=Decimal(str(quantity)) * unit_price,
            metadata=metadata or {}
        )
        
        self._save_resource_usage(usage)
        
        # Update LangFuse metrics
        self.langfuse_client.track_usage(usage)
        
        logger.info(f"Tracked {resource_type.value} usage: {quantity} units for customer {customer_id}")
        return usage
    
    def generate_invoice(self, customer_id: str, billing_period_start: datetime, 
                        billing_period_end: datetime) -> Invoice:
        """Generate invoice for customer billing period"""
        # Get customer information
        customer_info = self._get_customer_info(customer_id)
        
        # Get resource usage for billing period
        usage_records = self._get_usage_for_period(customer_id, billing_period_start, billing_period_end)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=self._generate_invoice_number(),
            customer_id=customer_id,
            customer_name=customer_info.get("name", ""),
            customer_email=customer_info.get("email", ""),
            billing_address=customer_info.get("billing_address", {}),
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end
        )
        
        # Add line items from usage
        line_items = []
        subtotal = Decimal('0')
        
        # Group usage by resource type
        usage_by_type = {}
        for usage in usage_records:
            resource_type = usage.resource_type.value
            if resource_type not in usage_by_type:
                usage_by_type[resource_type] = {
                    "quantity": Decimal('0'),
                    "unit": usage.unit,
                    "unit_price": usage.unit_price,
                    "total_cost": Decimal('0')
                }
            usage_by_type[resource_type]["quantity"] += usage.quantity
            usage_by_type[resource_type]["total_cost"] += usage.total_cost
        
        # Create line items
        for resource_type, data in usage_by_type.items():
            line_item = {
                "description": self._get_resource_description(resource_type),
                "quantity": float(data["quantity"]),
                "unit": data["unit"],
                "unit_price": float(data["unit_price"]),
                "total_price": float(data["total_cost"])
            }
            line_items.append(line_item)
            subtotal += data["total_cost"]
        
        # Calculate tax and total
        invoice.line_items = line_items
        invoice.subtotal = subtotal
        invoice.tax_amount = subtotal * invoice.tax_rate
        invoice.total_amount = subtotal + invoice.tax_amount
        
        # Save invoice
        self._save_invoice(invoice)
        
        logger.info(f"Generated invoice {invoice.invoice_number} for customer {customer_id}")
        return invoice
    
    def setup_automated_billing(self, customer_id: str, billing_cycle: BillingCycle) -> Dict[str, Any]:
        """Setup automated billing for customer"""
        # Create cron job for automated billing
        cron_schedule = self._get_cron_schedule(billing_cycle)
        
        job_config = {
            "customer_id": customer_id,
            "billing_cycle": billing_cycle.value,
            "cron_schedule": cron_schedule,
            "script_path": "/opt/agentic/scripts/automated_billing.py",
            "enabled": True
        }
        
        # Add cron job to system
        cron_job_id = self.cron_manager.add_billing_job(job_config)
        
        # Save billing configuration
        self._save_billing_config(customer_id, job_config)
        
        return {
            "status": "success",
            "cron_job_id": cron_job_id,
            "billing_cycle": billing_cycle.value,
            "next_billing_date": self._calculate_next_billing_date(billing_cycle)
        }
    
    def get_billing_dashboard(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive billing dashboard for customer"""
        # Current month usage
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_usage = self._get_usage_for_period(customer_id, current_month_start, datetime.now())
        
        # Calculate current month cost
        current_month_cost = sum(usage.total_cost for usage in current_month_usage)
        
        # Get recent invoices
        recent_invoices = self._get_recent_invoices(customer_id, limit=5)
        
        # Get usage trends
        usage_trends = self._get_usage_trends(customer_id, days=30)
        
        # Outstanding balance
        outstanding_balance = self._get_outstanding_balance(customer_id)
        
        return {
            "customer_id": customer_id,
            "current_month_cost": float(current_month_cost),
            "outstanding_balance": float(outstanding_balance),
            "recent_invoices": [self._invoice_to_dict(inv) for inv in recent_invoices],
            "usage_trends": usage_trends,
            "resource_breakdown": self._get_resource_breakdown(current_month_usage),
            "billing_alerts": self._get_billing_alerts(customer_id),
            "payment_methods": self._get_payment_methods(customer_id)
        }
    
    def _init_database(self):
        """Initialize billing database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Resource usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_usage (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                project_id TEXT,
                resource_type TEXT NOT NULL,
                quantity DECIMAL NOT NULL,
                unit TEXT NOT NULL,
                unit_price DECIMAL NOT NULL,
                total_cost DECIMAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id TEXT NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                billing_address TEXT,
                line_items TEXT,
                subtotal DECIMAL NOT NULL,
                tax_rate DECIMAL NOT NULL,
                tax_amount DECIMAL NOT NULL,
                total_amount DECIMAL NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                billing_period_start TEXT NOT NULL,
                billing_period_end TEXT NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                paid_date TEXT,
                payment_method TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Billing configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_configs (
                customer_id TEXT PRIMARY KEY,
                billing_cycle TEXT NOT NULL,
                cron_schedule TEXT NOT NULL,
                cron_job_id TEXT,
                enabled BOOLEAN NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_customer_timestamp ON resource_usage (customer_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_customer_status ON invoices (customer_id, status)")
        
        conn.commit()
        conn.close()
    
    def _setup_cron_jobs(self):
        """Setup system cron jobs for billing automation"""
        # Create billing scripts directory
        scripts_dir = Path("/opt/agentic/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create automated billing script
        billing_script = scripts_dir / "automated_billing.py"
        billing_script.write_text(self._generate_billing_script())
        billing_script.chmod(0o755)
        
        # Create resource monitoring script
        monitoring_script = scripts_dir / "resource_monitoring.py"
        monitoring_script.write_text(self._generate_monitoring_script())
        monitoring_script.chmod(0o755)
        
        logger.info("Billing automation scripts created")


class LangFuseIntegration:
    """LangFuse integration for AI metrics and cost tracking"""
    
    def __init__(self):
        self.langfuse_api_key = os.getenv("LANGFUSE_API_KEY")
        self.langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    def track_usage(self, usage: ResourceUsage):
        """Track usage in LangFuse"""
        # Mock implementation - integrate with actual LangFuse API
        logger.info(f"LangFuse tracking: {usage.resource_type.value} - {usage.quantity} {usage.unit}")
    
    def get_ai_metrics(self, customer_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get AI usage metrics from LangFuse"""
        # Mock implementation
        return {
            "total_tokens": 150000,
            "total_requests": 1250,
            "average_latency": 1.2,
            "cost_breakdown": {
                "input_tokens": 45.50,
                "output_tokens": 67.25,
                "total_cost": 112.75
            }
        }


class ResourceTracker:
    """Resource usage tracking and monitoring"""
    
    def __init__(self):
        self.pricing_config = self._load_pricing_config()
    
    def _load_pricing_config(self) -> Dict[str, Decimal]:
        """Load resource pricing configuration"""
        return {
            ResourceType.COMPUTE.value: Decimal('0.05'),  # SAR per CPU hour
            ResourceType.STORAGE.value: Decimal('0.10'),  # SAR per GB/month
            ResourceType.NETWORK.value: Decimal('0.01'),  # SAR per GB transfer
            ResourceType.AI_TOKENS.value: Decimal('0.002'),  # SAR per 1K tokens
            ResourceType.AGENT_HOURS.value: Decimal('25.00'),  # SAR per agent hour
            ResourceType.WORKFLOW_EXECUTIONS.value: Decimal('0.50'),  # SAR per execution
            ResourceType.OAUTH_CONNECTIONS.value: Decimal('2.00')  # SAR per connection/month
        }


class InvoiceGenerator:
    """Invoice generation and management"""
    
    def generate_pdf_invoice(self, invoice: Invoice) -> str:
        """Generate PDF invoice"""
        # Mock implementation - use reportlab or similar for PDF generation
        pdf_path = f"/tmp/invoice_{invoice.invoice_number}.pdf"
        logger.info(f"Generated PDF invoice: {pdf_path}")
        return pdf_path


class CronJobManager:
    """Cron job management for Linux Debian 12"""
    
    def add_billing_job(self, job_config: Dict[str, Any]) -> str:
        """Add billing cron job to system"""
        customer_id = job_config["customer_id"]
        cron_schedule = job_config["cron_schedule"]
        script_path = job_config["script_path"]
        
        # Create cron job entry
        cron_entry = f"{cron_schedule} {script_path} {customer_id} >> /var/log/agentic/billing.log 2>&1"
        
        # Add to crontab
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Add new job
            new_crontab = current_crontab + "\n" + cron_entry + "\n"
            
            # Write back to crontab
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            job_id = f"billing_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Added cron job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add cron job: {e}")
            raise
    
    def remove_billing_job(self, customer_id: str) -> bool:
        """Remove billing cron job"""
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Filter out jobs for this customer
            lines = result.stdout.split("\n")
            filtered_lines = [line for line in lines if customer_id not in line]
            
            # Write back filtered crontab
            new_crontab = "\n".join(filtered_lines)
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)
            
            logger.info(f"Removed cron jobs for customer: {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove cron job: {e}")
            return False 
   
    # Helper methods for billing agent functionality
    
    def _analyze_billing_request(self, message: str) -> str:
        """Analyze billing request type"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["usage", "استخدام", "موارد", "resources"]):
            return "resource_usage"
        elif any(word in message_lower for word in ["invoice", "فاتورة", "bill", "فوترة"]):
            return "invoice_generation"
        elif any(word in message_lower for word in ["payment", "دفع", "paid", "مدفوع"]):
            return "payment_tracking"
        elif any(word in message_lower for word in ["cost", "تكلفة", "analysis", "تحليل"]):
            return "cost_analysis"
        elif any(word in message_lower for word in ["setup", "إعداد", "configure", "تكوين"]):
            return "billing_setup"
        else:
            return "general"
    
    def _handle_resource_usage_inquiry(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Handle resource usage inquiries"""
        customer_id = context.get("customer_id") if context else None
        
        if not customer_id:
            return AgentResponse(
                message="يرجى تسجيل الدخول لعرض استخدام الموارد" if self._is_arabic_context(context) else "Please log in to view resource usage",
                confidence=0.8,
                next_action="require_authentication"
            )
        
        # Get current month usage
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        usage_records = self._get_usage_for_period(customer_id, current_month_start, datetime.now())
        
        # Calculate totals by resource type
        usage_summary = {}
        total_cost = Decimal('0')
        
        for usage in usage_records:
            resource_type = usage.resource_type.value
            if resource_type not in usage_summary:
                usage_summary[resource_type] = {
                    "quantity": Decimal('0'),
                    "cost": Decimal('0'),
                    "unit": usage.unit
                }
            usage_summary[resource_type]["quantity"] += usage.quantity
            usage_summary[resource_type]["cost"] += usage.total_cost
            total_cost += usage.total_cost
        
        if self._is_arabic_context(context):
            response_message = f"ملخص استخدام الموارد للشهر الحالي:\n\n"
            for resource_type, data in usage_summary.items():
                resource_name = self._get_arabic_resource_name(resource_type)
                response_message += f"• {resource_name}: {data['quantity']} {data['unit']} - {data['cost']} ريال\n"
            response_message += f"\nإجمالي التكلفة: {total_cost} ريال سعودي"
        else:
            response_message = f"Current month resource usage summary:\n\n"
            for resource_type, data in usage_summary.items():
                response_message += f"• {resource_type.replace('_', ' ').title()}: {data['quantity']} {data['unit']} - {data['cost']} SAR\n"
            response_message += f"\nTotal Cost: {total_cost} SAR"
        
        return AgentResponse(
            message=response_message,
            confidence=0.9,
            next_action="show_detailed_usage",
            context={"usage_summary": usage_summary, "total_cost": float(total_cost)}
        )
    
    def _handle_general_billing_inquiry(self, message: str) -> AgentResponse:
        """Handle general billing inquiries"""
        return AgentResponse(
            message=(
                "مرحباً! أنا وكيل الفوترة الذكي. يمكنني مساعدتك في:\n\n"
                "💰 تتبع استخدام الموارد والتكاليف\n"
                "📄 إنشاء وإدارة الفواتير\n"
                "💳 تتبع المدفوعات والأرصدة\n"
                "📊 تحليل التكاليف والاستخدام\n"
                "⚙️ إعداد الفوترة التلقائية\n\n"
                "كيف يمكنني مساعدتك اليوم؟"
                if "عربي" in message.lower() or "arabic" in message.lower() else
                "Hello! I'm your intelligent Billing Agent. I can help you with:\n\n"
                "💰 Resource usage and cost tracking\n"
                "📄 Invoice generation and management\n"
                "💳 Payment tracking and balances\n"
                "📊 Cost analysis and usage reports\n"
                "⚙️ Automated billing setup\n\n"
                "How can I help you today?"
            ),
            confidence=0.8,
            next_action="await_billing_request"
        )
    
    def _get_resource_pricing(self, resource_type: ResourceType) -> Decimal:
        """Get pricing for resource type"""
        return self.resource_tracker.pricing_config.get(resource_type.value, Decimal('0'))
    
    def _get_resource_unit(self, resource_type: ResourceType) -> str:
        """Get unit for resource type"""
        units = {
            ResourceType.COMPUTE: "hours",
            ResourceType.STORAGE: "GB",
            ResourceType.NETWORK: "GB",
            ResourceType.AI_TOKENS: "1K tokens",
            ResourceType.AGENT_HOURS: "hours",
            ResourceType.WORKFLOW_EXECUTIONS: "executions",
            ResourceType.OAUTH_CONNECTIONS: "connections"
        }
        return units.get(resource_type, "units")
    
    def _get_resource_description(self, resource_type: str) -> str:
        """Get description for resource type"""
        descriptions = {
            "compute": "Compute Resources (CPU/Memory)",
            "storage": "Storage Usage",
            "network": "Network Transfer",
            "ai_tokens": "AI Token Usage",
            "agent_hours": "Agent Processing Hours",
            "workflow_executions": "Workflow Executions",
            "oauth_connections": "OAuth Connections"
        }
        return descriptions.get(resource_type, resource_type.replace('_', ' ').title())
    
    def _get_arabic_resource_name(self, resource_type: str) -> str:
        """Get Arabic name for resource type"""
        arabic_names = {
            "compute": "موارد المعالجة",
            "storage": "التخزين",
            "network": "نقل البيانات",
            "ai_tokens": "رموز الذكاء الاصطناعي",
            "agent_hours": "ساعات الوكيل",
            "workflow_executions": "تنفيذ سير العمل",
            "oauth_connections": "اتصالات OAuth"
        }
        return arabic_names.get(resource_type, resource_type)
    
    def _is_arabic_context(self, context: Dict[str, Any]) -> bool:
        """Check if context indicates Arabic language preference"""
        if not context:
            return True  # Default to Arabic
        return context.get("language", "ar") == "ar"
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        return f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    def _get_cron_schedule(self, billing_cycle: BillingCycle) -> str:
        """Get cron schedule for billing cycle"""
        schedules = {
            BillingCycle.MONTHLY: "0 9 1 * *",  # 9 AM on 1st of every month
            BillingCycle.QUARTERLY: "0 9 1 1,4,7,10 *",  # 9 AM on 1st of Jan, Apr, Jul, Oct
            BillingCycle.YEARLY: "0 9 1 1 *",  # 9 AM on January 1st
            BillingCycle.PROJECT_BASED: "0 9 * * 1"  # 9 AM every Monday (for project completion checks)
        }
        return schedules.get(billing_cycle, "0 9 1 * *")
    
    def _calculate_next_billing_date(self, billing_cycle: BillingCycle) -> datetime:
        """Calculate next billing date"""
        now = datetime.now()
        
        if billing_cycle == BillingCycle.MONTHLY:
            if now.day == 1:
                return now + timedelta(days=31)
            else:
                next_month = now.replace(day=1) + timedelta(days=32)
                return next_month.replace(day=1)
        elif billing_cycle == BillingCycle.QUARTERLY:
            # Next quarter start
            quarter_months = [1, 4, 7, 10]
            current_quarter = (now.month - 1) // 3
            next_quarter_month = quarter_months[(current_quarter + 1) % 4]
            if next_quarter_month <= now.month:
                year = now.year + 1
            else:
                year = now.year
            return datetime(year, next_quarter_month, 1)
        elif billing_cycle == BillingCycle.YEARLY:
            return datetime(now.year + 1, 1, 1)
        else:
            return now + timedelta(days=7)  # Weekly check for project-based
    
    def _generate_billing_script(self) -> str:
        """Generate automated billing script"""
        return '''#!/usr/bin/env python3
"""
Automated Billing Script
Executed by cron for automated invoice generation
"""
import sys
import os
sys.path.append('/opt/agentic/backend')

from agentic_core.agents.billing_agent import BillingAgent
from agentic_core.agents.base_agent import AgentConfig, AgentType
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: automated_billing.py <customer_id>")
        sys.exit(1)
    
    customer_id = sys.argv[1]
    
    # Initialize billing agent
    config = AgentConfig(
        agent_type=AgentType.BILLING,
        framework="ADK",
        model_name="gemini-pro"
    )
    
    billing_agent = BillingAgent(config)
    
    # Calculate billing period (previous month)
    today = datetime.now()
    billing_end = today.replace(day=1) - timedelta(days=1)
    billing_start = billing_end.replace(day=1)
    
    try:
        # Generate invoice
        invoice = billing_agent.generate_invoice(customer_id, billing_start, billing_end)
        logger.info(f"Generated invoice {invoice.invoice_number} for customer {customer_id}")
        
    except Exception as e:
        logger.error(f"Failed to generate invoice for customer {customer_id}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    def _generate_monitoring_script(self) -> str:
        """Generate resource monitoring script"""
        return '''#!/usr/bin/env python3
"""
Resource Monitoring Script
Executed by cron for resource usage tracking
"""
import sys
import os
sys.path.append('/opt/agentic/backend')

from agentic_core.agents.billing_agent import BillingAgent, ResourceType
from agentic_core.agents.base_agent import AgentConfig, AgentType
import psutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize billing agent
    config = AgentConfig(
        agent_type=AgentType.BILLING,
        framework="ADK",
        model_name="gemini-pro"
    )
    
    billing_agent = BillingAgent(config)
    
    try:
        # Monitor system resources
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        # Track usage for system monitoring
        logger.info(f"System resources - CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%")
        
    except Exception as e:
        logger.error(f"Failed to monitor resources: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Database helper methods
    def _save_resource_usage(self, usage: ResourceUsage):
        """Save resource usage to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resource_usage 
            (id, customer_id, project_id, resource_type, quantity, unit, unit_price, total_cost, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usage.id, usage.customer_id, usage.project_id, usage.resource_type.value,
            float(usage.quantity), usage.unit, float(usage.unit_price), float(usage.total_cost),
            usage.timestamp.isoformat(), json.dumps(usage.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_invoice(self, invoice: Invoice):
        """Save invoice to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO invoices 
            (id, invoice_number, customer_id, customer_name, customer_email, billing_address,
             line_items, subtotal, tax_rate, tax_amount, total_amount, currency, status,
             billing_period_start, billing_period_end, issue_date, due_date, paid_date,
             payment_method, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice.id, invoice.invoice_number, invoice.customer_id, invoice.customer_name,
            invoice.customer_email, json.dumps(invoice.billing_address), json.dumps(invoice.line_items),
            float(invoice.subtotal), float(invoice.tax_rate), float(invoice.tax_amount),
            float(invoice.total_amount), invoice.currency, invoice.status.value,
            invoice.billing_period_start.isoformat(), invoice.billing_period_end.isoformat(),
            invoice.issue_date.isoformat(), invoice.due_date.isoformat(),
            invoice.paid_date.isoformat() if invoice.paid_date else None,
            invoice.payment_method, invoice.notes, invoice.created_at.isoformat(),
            invoice.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information"""
        # Mock implementation - integrate with actual customer database
        return {
            "name": "Customer Name",
            "email": "customer@example.com",
            "billing_address": {
                "street": "123 Main St",
                "city": "Riyadh",
                "country": "Saudi Arabia",
                "postal_code": "12345"
            }
        }
    
    def _get_usage_for_period(self, customer_id: str, start_date: datetime, end_date: datetime) -> List[ResourceUsage]:
        """Get usage records for billing period"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM resource_usage 
            WHERE customer_id = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        """, (customer_id, start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        usage_records = []
        for row in rows:
            usage = ResourceUsage(
                id=row[0], customer_id=row[1], project_id=row[2],
                resource_type=ResourceType(row[3]), quantity=Decimal(str(row[4])),
                unit=row[5], unit_price=Decimal(str(row[6])), total_cost=Decimal(str(row[7])),
                timestamp=datetime.fromisoformat(row[8]),
                metadata=json.loads(row[9]) if row[9] else {}
            )
            usage_records.append(usage)
        
        return usage_records
    
    def _get_recent_invoices(self, customer_id: str, limit: int = 5) -> List[Invoice]:
        """Get recent invoices for customer"""
        # Mock implementation
        return []
    
    def _get_outstanding_balance(self, customer_id: str) -> Decimal:
        """Get outstanding balance for customer"""
        # Mock implementation
        return Decimal('0')
    
    def _get_usage_trends(self, customer_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage trends for customer"""
        # Mock implementation
        return {"total_cost": 0.0, "daily_average": 0.0}
    
    def _get_resource_breakdown(self, usage_records: List[ResourceUsage]) -> Dict[str, float]:
        """Get resource cost breakdown"""
        breakdown = {}
        for usage in usage_records:
            resource_type = usage.resource_type.value
            if resource_type not in breakdown:
                breakdown[resource_type] = 0.0
            breakdown[resource_type] += float(usage.total_cost)
        return breakdown
    
    def _get_billing_alerts(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get billing alerts for customer"""
        return []
    
    def _get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get payment methods for customer"""
        return []
    
    def _invoice_to_dict(self, invoice: Invoice) -> Dict[str, Any]:
        """Convert invoice to dictionary"""
        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "total_amount": float(invoice.total_amount),
            "status": invoice.status.value
        }
    
    def _save_billing_config(self, customer_id: str, config: Dict[str, Any]):
        """Save billing configuration"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO billing_configs 
            (customer_id, billing_cycle, cron_schedule, cron_job_id, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, config["billing_cycle"], config["cron_schedule"],
            config.get("cron_job_id"), config["enabled"],
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()