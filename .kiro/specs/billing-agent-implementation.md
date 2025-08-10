# 🏦 Billing Agent Implementation Documentation

## Overview

The Billing Agent is a comprehensive AI-powered billing and resource management system that provides automated billing, resource tracking, invoice generation, and payment management capabilities. It integrates with LangFuse for AI metrics tracking and uses Linux Debian 12 cron jobs for automation.

## 🎯 Key Features

### 1. Resource Tracking & Monitoring
- **Real-time Usage Tracking**: Monitors compute, storage, network, AI tokens, agent hours, workflow executions, and OAuth connections
- **Cost Calculation**: Automatic cost calculation based on configurable pricing models
- **LangFuse Integration**: AI metrics and performance tracking
- **Resource Breakdown**: Detailed analysis of resource consumption by type

### 2. Invoice Management
- **Automated Generation**: Creates detailed invoices with line items and resource breakdown
- **Saudi VAT Compliance**: Includes 15% VAT calculation for Saudi Arabia
- **Multiple Formats**: Support for PDF generation and digital delivery
- **Invoice Tracking**: Complete lifecycle management from draft to paid

### 3. Billing Automation
- **Cron Job Integration**: Linux Debian 12 system-level automation
- **Flexible Billing Cycles**: Monthly, quarterly, yearly, and project-based billing
- **Automated Reminders**: Payment reminders and overdue notifications
- **Resource Monitoring**: Continuous system resource monitoring

### 4. Multi-language Support
- **Arabic-First Design**: Default Arabic interface with English fallback
- **Contextual Language**: Intelligent language detection and switching
- **Localized Content**: All billing terms and descriptions in both languages

## 🏗️ Architecture

### Core Components

```python
BillingAgent
├── LangFuseIntegration     # AI metrics tracking
├── ResourceTracker        # Usage monitoring
├── InvoiceGenerator       # PDF and digital invoices
├── CronJobManager         # System automation
└── Database Layer         # SQLite for billing data
```

### Data Models

#### ResourceUsage
- Tracks individual resource consumption events
- Links to customers and projects
- Calculates costs based on pricing models
- Stores metadata for detailed analysis

#### Invoice
- Complete invoice structure with line items
- Saudi VAT compliance (15%)
- Multiple status tracking (draft, sent, paid, overdue)
- Billing period management

#### BillingConfiguration
- Customer-specific billing settings
- Automated billing cycle configuration
- Cron job management

## 💰 Pricing Configuration

### Default Pricing (Saudi Riyal)
```python
PRICING_CONFIG = {
    "compute": 0.05,           # SAR per CPU hour
    "storage": 0.10,           # SAR per GB/month
    "network": 0.01,           # SAR per GB transfer
    "ai_tokens": 0.002,        # SAR per 1K tokens
    "agent_hours": 25.00,      # SAR per agent hour
    "workflow_executions": 0.50, # SAR per execution
    "oauth_connections": 2.00   # SAR per connection/month
}
```

## 🤖 Agent Capabilities

### Conversation Handling
The billing agent can handle various types of inquiries:

1. **Resource Usage Inquiries** (`استخدام الموارد` / `resource usage`)
2. **Invoice Generation** (`فاتورة` / `invoice`)
3. **Payment Tracking** (`دفع` / `payment`)
4. **Cost Analysis** (`تحليل التكاليف` / `cost analysis`)
5. **Billing Setup** (`إعداد الفوترة` / `billing setup`)

### Sample Interactions

#### Arabic Example
```
User: "أريد معرفة استخدام الموارد هذا الشهر"
Agent: "ملخص استخدام الموارد للشهر الحالي:

• موارد المعالجة: 120 hours - 6.00 ريال
• التخزين: 50 GB - 5.00 ريال
• رموز الذكاء الاصطناعي: 25 1K tokens - 0.05 ريال

إجمالي التكلفة: 11.05 ريال سعودي"
```

#### English Example
```
User: "Show me my current month usage"
Agent: "Current month resource usage summary:

• Compute Resources: 120 hours - 6.00 SAR
• Storage Usage: 50 GB - 5.00 SAR
• AI Token Usage: 25 1K tokens - 0.05 SAR

Total Cost: 11.05 SAR"
```

## 🔄 Automation Features

### Cron Job Management
The billing agent creates and manages Linux cron jobs for:

1. **Automated Billing**: Monthly invoice generation
2. **Resource Monitoring**: Continuous usage tracking
3. **Payment Reminders**: Overdue payment notifications
4. **System Health Checks**: Resource utilization monitoring

### Cron Schedule Examples
```bash
# Monthly billing (1st of every month at 9 AM)
0 9 1 * * /opt/agentic/scripts/automated_billing.py customer_id

# Resource monitoring (every hour)
0 * * * * /opt/agentic/scripts/resource_monitoring.py

# Payment reminders (every Monday at 10 AM)
0 10 * * 1 /opt/agentic/scripts/payment_reminders.py
```

## 📊 LangFuse Integration

### Metrics Tracking
- **Token Usage**: Input/output token consumption
- **Request Latency**: AI model response times
- **Cost Analysis**: Detailed cost breakdown by model and usage
- **Performance Monitoring**: System performance metrics

### Data Collection
```python
def track_usage(self, usage: ResourceUsage):
    """Track usage in LangFuse for comprehensive analytics"""
    langfuse_data = {
        "customer_id": usage.customer_id,
        "resource_type": usage.resource_type.value,
        "quantity": float(usage.quantity),
        "cost": float(usage.total_cost),
        "timestamp": usage.timestamp.isoformat()
    }
    # Send to LangFuse API
```

## 🗄️ Database Schema

### Resource Usage Table
```sql
CREATE TABLE resource_usage (
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
);
```

### Invoices Table
```sql
CREATE TABLE invoices (
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
);
```

## 🚀 Usage Examples

### Track Resource Usage
```python
from agentic_core.agents import BillingAgent, ResourceType

# Initialize billing agent
billing_agent = BillingAgent(config)

# Track compute usage
usage = billing_agent.track_resource_usage(
    customer_id="customer_123",
    resource_type=ResourceType.COMPUTE,
    quantity=2.5,  # 2.5 CPU hours
    metadata={"project_id": "project_456", "instance_type": "standard"}
)
```

### Generate Invoice
```python
from datetime import datetime, timedelta

# Calculate billing period
end_date = datetime.now()
start_date = end_date.replace(day=1)

# Generate invoice
invoice = billing_agent.generate_invoice(
    customer_id="customer_123",
    billing_period_start=start_date,
    billing_period_end=end_date
)

print(f"Invoice {invoice.invoice_number} generated for {invoice.total_amount} SAR")
```

### Setup Automated Billing
```python
from agentic_core.agents.billing_agent import BillingCycle

# Setup monthly automated billing
result = billing_agent.setup_automated_billing(
    customer_id="customer_123",
    billing_cycle=BillingCycle.MONTHLY
)

print(f"Automated billing setup: {result['status']}")
print(f"Next billing date: {result['next_billing_date']}")
```

## 🔧 Configuration

### Environment Variables
```bash
# LangFuse Integration
LANGFUSE_API_KEY=your_langfuse_api_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Database Configuration
BILLING_DATABASE_PATH=/opt/agentic/data/billing.db

# Automation Settings
BILLING_SCRIPTS_PATH=/opt/agentic/scripts
BILLING_LOG_PATH=/var/log/agentic/billing.log
```

### Pricing Configuration
Pricing can be customized per customer or globally:

```python
# Custom pricing for enterprise customers
enterprise_pricing = {
    ResourceType.COMPUTE.value: Decimal('0.04'),      # Discounted rate
    ResourceType.AGENT_HOURS.value: Decimal('20.00'), # Volume discount
    # ... other resources
}
```

## 🧪 Testing

### Unit Tests
```python
def test_resource_usage_tracking():
    """Test resource usage tracking functionality"""
    billing_agent = BillingAgent(test_config)
    
    usage = billing_agent.track_resource_usage(
        customer_id="test_customer",
        resource_type=ResourceType.COMPUTE,
        quantity=1.0
    )
    
    assert usage.total_cost == Decimal('0.05')
    assert usage.unit == "hours"

def test_invoice_generation():
    """Test invoice generation with VAT calculation"""
    # Setup test data
    # Generate invoice
    # Verify calculations including 15% VAT
```

### Integration Tests
```python
def test_cron_job_creation():
    """Test cron job creation and management"""
    # Test cron job addition
    # Verify crontab entries
    # Test job removal

def test_langfuse_integration():
    """Test LangFuse metrics tracking"""
    # Mock LangFuse API
    # Track usage
    # Verify data sent to LangFuse
```

## 📈 Monitoring & Analytics

### Key Metrics
- **Revenue per Customer**: Monthly recurring revenue tracking
- **Resource Utilization**: Usage patterns and trends
- **Payment Performance**: Collection rates and overdue analysis
- **Cost Efficiency**: Resource cost optimization opportunities

### Dashboard Features
- Real-time usage monitoring
- Revenue forecasting
- Customer billing status
- Resource utilization trends
- Payment collection analytics

## 🔒 Security & Compliance

### Data Protection
- **Encryption**: All sensitive billing data encrypted at rest
- **Access Control**: Role-based access to billing information
- **Audit Logging**: Complete audit trail of billing operations
- **GDPR Compliance**: Data retention and deletion policies

### Saudi Arabia Compliance
- **VAT Compliance**: 15% VAT calculation and reporting
- **Invoice Requirements**: Meets Saudi e-invoicing standards
- **Currency**: All transactions in Saudi Riyal (SAR)
- **Language**: Arabic-first with English support

## 🚀 Deployment

### Production Deployment
1. **Database Setup**: Initialize billing database schema
2. **Cron Jobs**: Configure system-level automation
3. **Environment**: Set required environment variables
4. **Monitoring**: Setup billing metrics and alerts
5. **Testing**: Verify all billing functions work correctly

### Scaling Considerations
- **Database**: Consider PostgreSQL for high-volume deployments
- **Caching**: Redis for frequently accessed billing data
- **Queue System**: Celery for background billing tasks
- **Load Balancing**: Multiple billing agent instances

## 📚 API Reference

### Core Methods

#### `track_resource_usage(customer_id, resource_type, quantity, metadata=None)`
Track resource usage for billing purposes.

#### `generate_invoice(customer_id, billing_period_start, billing_period_end)`
Generate invoice for specified billing period.

#### `setup_automated_billing(customer_id, billing_cycle)`
Configure automated billing for customer.

#### `get_billing_dashboard(customer_id)`
Get comprehensive billing dashboard data.

### Response Formats

All API responses include:
- **Status**: Success/error indication
- **Data**: Requested information
- **Metadata**: Additional context
- **Timestamp**: Operation timestamp

## 🔄 Future Enhancements

### Planned Features
1. **Multi-currency Support**: Support for USD, EUR, etc.
2. **Advanced Analytics**: ML-powered usage predictions
3. **Integration APIs**: Third-party billing system integration
4. **Mobile Dashboard**: Mobile app for billing management
5. **Automated Dunning**: Advanced collection workflows

### Roadmap
- **Q1 2025**: Enhanced reporting and analytics
- **Q2 2025**: Multi-currency and international expansion
- **Q3 2025**: Advanced automation and ML features
- **Q4 2025**: Enterprise features and integrations

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: Production Ready  
**Maintainer**: Agentic Platform Team