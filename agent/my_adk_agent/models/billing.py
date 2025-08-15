"""
Billing Data Models
Data structures for billing, invoices, and resource usage
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid

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
    COMPUTE_HOURS = "compute_hours"
    STORAGE_GB = "storage_gb"
    NETWORK_GB = "network_gb"
    AI_TOKENS = "ai_tokens"
    AGENT_HOURS = "agent_hours"
    WORKFLOW_EXECUTIONS = "workflow_executions"
    LIVE_SESSIONS = "live_sessions"
    FILE_PROCESSING = "file_processing"

@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    project_id: Optional[str] = None
    resource_type: str = ""
    quantity: float = 0.0
    unit: str = ""
    unit_price: float = 0.0
    total_cost: float = 0.0
    currency: str = "SAR"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

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
    subtotal: float = 0.0
    vat_rate: float = 0.15  # 15% VAT for Saudi Arabia
    vat_amount: float = 0.0
    total_amount: float = 0.0
    currency: str = "SAR"
    status: str = "draft"
    billing_period_start: datetime = field(default_factory=datetime.now)
    billing_period_end: datetime = field(default_factory=datetime.now)
    issue_date: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=datetime.now)
    paid_date: Optional[datetime] = None
    payment_method: str = ""
    stripe_payment_intent_id: Optional[str] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PaymentMethod:
    """Payment method data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    stripe_customer_id: str = ""
    stripe_payment_method_id: str = ""
    type: str = ""  # card, bank_account, etc.
    last_four: Optional[str] = None
    brand: Optional[str] = None
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class BillingConfiguration:
    """Billing configuration for customer"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    billing_cycle: str = "monthly"
    auto_billing_enabled: bool = False
    payment_method_id: Optional[str] = None
    billing_email: str = ""
    billing_address: Dict[str, str] = field(default_factory=dict)
    tax_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class UsageSummary:
    """Usage summary for reporting"""
    customer_id: str = ""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    total_cost: float = 0.0
    currency: str = "SAR"
    resource_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)