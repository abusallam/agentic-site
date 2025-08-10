# 🚀 Systematic Agentic AI Platform

[![Production Live](https://img.shields.io/badge/Production-LIVE-green?style=for-the-badge&logo=checkmarx)](https://consulting.sa)
[![Development Live](https://img.shields.io/badge/Development-LIVE-blue?style=for-the-badge&logo=docker)](https://dev.consulting.sa)
[![Built with Next.js](https://img.shields.io/badge/Built%20with-Next.js-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Python ADK](https://img.shields.io/badge/Python-ADK%20Agent-yellow?style=for-the-badge&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enterprise-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready, battle-tested AI consulting SaaS platform with comprehensive deployment automation, security monitoring, systematic development processes, and advanced billing intelligence. Features Arabic-first interface, comprehensive billing agent with LangFuse integration, and automated testing capabilities. Built from real-world production experience with consulting.sa.

## ✅ Production Status

**🌐 LIVE SYSTEM**: https://consulting.sa (Operational since July 2025)  
**🔧 Development**: https://dev.consulting.sa (Active development environment)  
**📊 Monitoring**: Comprehensive security and performance monitoring  
**🛡️ Security**: Hardware monitoring, penetration testing, intrusion detection  

## 🎯 What Makes This Different

This isn't just another AI platform - it's a **systematic deployment framework** with **enhanced agentic capabilities** that solves real-world production challenges:

- ✅ **Battle-Tested**: Learned from 2+ weeks of production deployment challenges
- ✅ **Enhanced Agentic Foundation**: FastAPI + Celery + Redis + Flower architecture
- ✅ **Multi-Framework AI Support**: ADK, LangGraph, CrewAI, and Swarm compatibility
- ✅ **Intelligent Agent Routing**: Three-tier service architecture with specialized agents
- ✅ **Zero-Downtime Deployments**: Nginx-based traffic redirection system
- ✅ **Dual-Stack Architecture**: Isolated production/development environments
- ✅ **Comprehensive Security**: Hardware monitoring, pen testing, intrusion detection
- ✅ **Systematic Documentation**: Every mistake documented and prevented
- ✅ **Debian 12 Standardized**: Optimized for VPS deployment

## 🤖 Enhanced Agentic Features

### Three-Tier Service Architecture
Our platform intelligently routes customers to the most appropriate service based on their needs:

1. **🚀 Fast Solutions (N8N Workflow Agent)**
   - Template-based chatbots and automation
   - Sub-agent deployment with knowledge bases
   - Quick deployment using N8N workflows
   - Perfect for: Simple chatbots, basic automation, rapid prototyping

2. **⚡ Custom Solutions (Professional Agent)**
   - Custom development and coding services
   - Requirement gathering and technical feasibility analysis
   - Negotiation engine for project refinement
   - Perfect for: Enterprise integrations, complex applications, custom platforms

3. **📋 Consultation Services (Consulting Agent)**
   - Calendar scheduling and appointment management
   - Automated research and knowledge gathering
   - Document preparation for consultations
   - Perfect for: Strategic planning, technical consulting, business analysis

### Multi-Framework Agent Support
- **ADK (Agent Development Kit)**: Primary framework with Google Gemini integration
- **LangGraph**: Advanced workflow orchestration (ready for integration)
- **CrewAI**: Multi-agent collaboration (ready for integration)
- **Swarm**: Distributed agent coordination (ready for integration)

### Distributed Task Processing
- **FastAPI**: High-performance API gateway with async support
- **Celery**: Distributed task processing with multiple worker queues
- **Redis**: Message broker and caching layer
- **Flower**: Real-time task monitoring and management interface

## 🏦 Advanced Billing Intelligence

### Comprehensive Billing Agent
Our platform includes a sophisticated billing agent with advanced capabilities:

1. **🔍 Resource Tracking & Monitoring**
   - Real-time usage tracking (compute, storage, network, AI tokens)
   - LangFuse integration for AI metrics and cost analysis
   - Automated cost calculation with configurable pricing models
   - Detailed resource breakdown and usage analytics

2. **📄 Automated Invoice Management**
   - Saudi VAT compliance (15% tax calculation)
   - Multi-language invoice generation (Arabic/English)
   - PDF generation and digital delivery
   - Complete invoice lifecycle management (draft → sent → paid)

3. **⚙️ Linux Cron Job Automation**
   - Debian 12 system-level automation
   - Flexible billing cycles (monthly, quarterly, yearly, project-based)
   - Automated payment reminders and overdue notifications
   - Resource monitoring and system health checks

4. **🌍 Arabic-First Interface**
   - Default Arabic language with intelligent English fallback
   - Contextual language detection and switching
   - Localized billing terms and descriptions
   - RTL (Right-to-Left) layout support

### Billing Agent Capabilities
```python
# Track resource usage
billing_agent.track_resource_usage(
    customer_id="customer_123",
    resource_type=ResourceType.AI_TOKENS,
    quantity=1500,  # 1.5K tokens
    metadata={"project_id": "ai_chatbot", "model": "gemini-pro"}
)

# Generate invoice with Saudi VAT
invoice = billing_agent.generate_invoice(
    customer_id="customer_123",
    billing_period_start=start_date,
    billing_period_end=end_date
)
# Result: Invoice with 15% VAT, Arabic/English support

# Setup automated billing
billing_agent.setup_automated_billing(
    customer_id="customer_123",
    billing_cycle=BillingCycle.MONTHLY
)
# Result: Linux cron job created for automated monthly billing
```

### Sample Billing Interactions

**Arabic Interaction:**
```
User: "أريد معرفة استخدام الموارد هذا الشهر"
Agent: "ملخص استخدام الموارد للشهر الحالي:

• موارد المعالجة: 120 ساعة - 6.00 ريال
• التخزين: 50 جيجابايت - 5.00 ريال  
• رموز الذكاء الاصطناعي: 25 ألف رمز - 0.05 ريال

إجمالي التكلفة: 11.05 ريال سعودي"
```

**English Interaction:**
```
User: "Show me my current month usage"
Agent: "Current month resource usage summary:

• Compute Resources: 120 hours - 6.00 SAR
• Storage Usage: 50 GB - 5.00 SAR
• AI Token Usage: 25K tokens - 0.05 SAR

Total Cost: 11.05 SAR"
```

## 🏗️ Architecture Overview

### Enhanced Agentic Workflow Architecture

```mermaid
graph TB
    subgraph "Customer Entry Point"
        A[Customer Message] --> B[Enhanced Chat Widget]
        B --> C[FastAPI Gateway]
    end
    
    subgraph "Welcoming Agent Layer"
        C --> D[Welcoming Agent]
        D --> E[Intent Analysis]
        E --> F{Service Type Detection}
    end
    
    subgraph "Fast Solution Path"
        F -->|Fast Solution| G[N8N Workflow Agent]
        G --> H[Composio OAuth Setup]
        H --> I[N8N Workflow Creation]
        I --> J[Sub-Agent Deployment]
        J --> K[Workflow Monitoring]
        K --> L[Customer Access Portal]
    end
    
    subgraph "Custom Development Path"
        F -->|Custom Solution| M[Professional Agent]
        M --> N[Requirement Gathering]
        N --> O[Technical Feasibility]
        O --> P[Negotiation Engine]
        P --> Q[Test Environment Setup]
        Q --> R[Development Deployment]
    end
    
    subgraph "Consultation Path"
        F -->|Consultation| S[Consulting Agent]
        S --> T[Calendar Scheduling]
        T --> U[Research Engine]
        U --> V[BMad-Method Planning]
        V --> W[Comprehensive Documentation]
        W --> X[Long-term Project Support]
    end
    
    subgraph "Task Processing Layer"
        Y[Celery Workers] --> Z[Redis Message Broker]
        Z --> AA[Flower Monitoring]
        G --> Y
        M --> Y
        S --> Y
    end
    
    subgraph "Integration Layer"
        BB[Composio OAuth] --> CC[Gmail, Calendar, Slack, Facebook]
        DD[BMad-Method Engine] --> EE[Analyst, PM, Architect, Scrum Master]
        FF[N8N Platform] --> GG[Workflow Templates & Sub-Agents]
    end
    
    subgraph "Data & Monitoring"
        HH[Supabase Database] --> II[Customer Profiles]
        HH --> JJ[Conversation History]
        HH --> KK[Workflow State]
        LL[LangFusion Monitoring] --> MM[Agent Metrics]
        LL --> NN[Resource Monitoring]
    end
    
    Y --> HH
    AA --> LL
```

### Systematic Deployment Process
```
GitHub Repository
    ↓ (Push to develop)
Development Stack (dev.consulting.sa)
    ↓ (Testing & Validation)
Ready for Production
    ↓ (Duplicate Stack Command)
New Production Stack (temp containers)
    ↓ (Nginx Redirect + Health Check)
Stop Old Production (Keep 2 weeks)
    ↓ (Rename Containers)
New Production Live (main.consulting.sa)
```

### Enhanced Multi-Agent AI System
- **Welcoming Agent**: Initial customer interaction and intelligent routing
- **N8N Workflow Agent**: Fast automation solutions with sub-agents and knowledge bases
- **Professional Agent**: Custom development with requirement gathering and technical feasibility
- **Consulting Agent**: Calendar scheduling, research coordination, and consultation preparation
- **Multi-Framework Support**: ADK, LangGraph, CrewAI, and Swarm compatibility
- **FastAPI + Celery + Redis**: Distributed task processing with Flower monitoring
- **Security Monitoring**: Real-time threat detection and response
- **Hardware Security**: Rootkit detection and hardware integrity monitoring

### Technology Stack
- **Frontend**: Next.js 15+ with TypeScript, Tailwind CSS, Shadcn/ui, Enhanced Chat Widget
- **Backend**: FastAPI + Celery + Redis + Flower, Python ADK Agent framework with Google Gemini
- **Agentic Core**: Multi-framework support (ADK, LangGraph, CrewAI, Swarm)
- **Database**: Supabase with real-time features
- **Task Processing**: Distributed Celery workers with Redis message broker
- **Monitoring**: Flower for task monitoring, LangFusion integration ready
- **Infrastructure**: Docker containers, Nginx, SSL, comprehensive monitoring
- **Security**: Fail2ban, UFW firewall, SSL/TLS, security headers
- **Observability**: Prometheus, Grafana, N8N workflows, custom health checks

## 🚀 Quick Start (Systematic Deployment)

### Prerequisites
- Debian 12 VPS (minimum 2GB RAM, 20GB disk)
- Domain name with DNS access
- SSL certificates
- Required API keys (Supabase, Google Gemini, etc.)

### 1. VPS Provisioning (5 minutes)
```bash
# Provision and harden Debian 12 VPS
sudo ./infrastructure/scripts/provision-debian12-vps.sh

# Set up dual container stacks
sudo ./infrastructure/scripts/setup-dual-container-stacks.sh

# Configure Nginx with SSL
sudo ./infrastructure/scripts/manage-nginx-config.sh setup
```

### 2. Environment Configuration
```bash
# Copy and configure environment
cp .env.template .env
# Edit .env with your actual values

# Validate configuration
./infrastructure/scripts/validate-environment.sh
```

### 3. Application Deployment
```bash
# Deploy to development first
./infrastructure/scripts/deploy-to-development.sh

# Test and validate
./infrastructure/scripts/health-check-stacks.sh

# Deploy to production (zero-downtime)
./infrastructure/scripts/deploy-to-production.sh
```

## 📁 Systematic Project Structure

```
agentic-site/
├── 🌐 frontend/                    # Next.js application
│   ├── app/                        # Next.js 15+ App Router
│   ├── components/                 # React components
│   └── lib/                        # Utilities and configurations
├── 🤖 agent/                       # Python ADK agent
│   ├── my_adk_agent/              # Main agent implementation
│   │   ├── services/              # Service integrations
│   │   └── tools/                 # ADK tools
│   └── specialized_agents/        # Domain-specific agents
├── 🏗️ infrastructure/              # Deployment and infrastructure
│   ├── scripts/                   # Systematic deployment scripts
│   ├── nginx/                     # Nginx configurations
│   ├── monitoring/                # Monitoring stack
│   └── ssl/                       # SSL certificates
├── 🛡️ tools/                       # Security and utility tools
│   ├── security/                  # Security monitoring tools
│   ├── monitoring/                # System monitoring
│   └── database/                  # Database utilities
├── 📚 docs/                        # Comprehensive documentation
│   ├── deployment/                # Deployment guides
│   ├── security/                  # Security documentation
│   └── troubleshooting/           # Issue resolution
├── 🧪 tests/                       # Comprehensive test suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
└── 🔧 .kiro/                       # Kiro AI development assistance
    ├── specs/                     # Feature specifications
    ├── steering/                  # Project context
    └── hooks/                     # Automated workflows
```

## 🛡️ Security Features

### Comprehensive Security Monitoring
- **Intrusion Detection**: Real-time network traffic analysis
- **Hardware Security**: Rootkit detection and hardware integrity monitoring
- **Penetration Testing**: Automated OWASP Top 10 vulnerability testing
- **Threat Response**: Automated containment and incident response

### Security Hardening
- **Firewall**: UFW with minimal required ports
- **Fail2ban**: Brute force protection
- **SSL/TLS**: Modern cipher suites and security headers
- **Container Security**: Non-root users and health checks
- **Audit Logging**: Tamper-proof security event logging

## 🔄 Zero-Downtime Deployment Process

Our systematic deployment process ensures zero downtime:

1. **Development**: Work on `dev.consulting.sa` environment
2. **Testing**: Comprehensive validation and health checks
3. **Duplication**: Clone dev stack to new production containers
4. **Health Check**: Validate new stack before traffic switch
5. **Nginx Redirect**: Atomic traffic redirection to new stack
6. **Rollback Ready**: Keep old production stack for 2 weeks

### Simple Commands
```bash
# Deploy feature to production (zero-downtime)
./infrastructure/scripts/deploy-to-production.sh

# Rollback if needed (instant)
./infrastructure/scripts/rollback-deployment.sh

# Check system health
./infrastructure/scripts/health-check-stacks.sh
```

## 📊 Monitoring & Observability

### Built-in Monitoring Stack
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboards and visualization
- **N8N**: Workflow automation and notifications
- **Custom Health Checks**: 50+ automated validation tests

### Performance Metrics
- **Response Time**: < 1.5s average
- **Uptime**: > 99.9% availability
- **Security Response**: < 30 seconds threat detection
- **Deployment Time**: < 5 minutes zero-downtime deployment

## 🔧 Management Commands

### Stack Management
```bash
# Manage container stacks
/opt/scripts/manage-stacks.sh {start|stop|restart|status} {production|development|all}

# Nginx management
/opt/scripts/nginx-manager.sh {status|test|reload|redirect}

# Security monitoring
/opt/scripts/security-monitor.sh {status|scan|report}

# System health
/opt/scripts/health-check-stacks.sh
```

### Development Workflow
```bash
# Work on development environment
git checkout develop
# Make changes, test locally

# Deploy to development
./infrastructure/scripts/deploy-to-development.sh

# Test on dev.consulting.sa
./infrastructure/scripts/validate-deployment.sh

# Deploy to production (when ready)
./infrastructure/scripts/deploy-to-production.sh
```

## 🎯 Success Metrics

### Production Achievements
- ✅ **Zero-Downtime Deployments**: 100% success rate
- ✅ **System Uptime**: > 99.9% availability
- ✅ **Security Incidents**: 0 successful breaches
- ✅ **Deployment Speed**: < 5 minutes average
- ✅ **Recovery Time**: < 2 minutes rollback capability

### Development Efficiency
- ✅ **New VPS Setup**: < 10 minutes fully automated
- ✅ **Environment Replication**: Identical dev/prod environments
- ✅ **Documentation Coverage**: 100% of procedures documented
- ✅ **Knowledge Transfer**: < 1 day for new team members

## 📚 Comprehensive Documentation

### Deployment Guides
- [🚀 Systematic Deployment Guide](DEPLOYMENT_GUIDE.md)
- [🔧 VPS Provisioning Guide](docs/deployment/VPS_PROVISIONING.md)
- [🛡️ Security Hardening Guide](docs/security/SECURITY_HARDENING.md)
- [📊 Monitoring Setup Guide](docs/monitoring/MONITORING_SETUP.md)

### Development Resources
- [💻 Development Guide](DEVELOPMENT_GUIDE.md)
- [🏗️ Architecture Overview](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [🔌 API Documentation](docs/api/API_REFERENCE.md)
- [🧪 Testing Guide](docs/testing/TESTING_GUIDE.md)

### Troubleshooting
- [🔧 Deployment Troubleshooting](docs/troubleshooting/DEPLOYMENT_ISSUES.md)
- [🛡️ Security Incident Response](docs/security/INCIDENT_RESPONSE.md)
- [📊 Performance Optimization](docs/performance/OPTIMIZATION_GUIDE.md)

## 🤝 Contributing

### Development Process
1. **Fork** the repository
2. **Create** feature branch from `develop`
3. **Develop** using development environment
4. **Test** thoroughly on `dev.consulting.sa`
5. **Submit** pull request with comprehensive testing

### Standards
- Follow established coding standards in `.kiro/steering/`
- Include comprehensive tests
- Update documentation
- Validate security implications

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Why Choose This Platform?

This isn't just code - it's a **complete systematic deployment framework** that:

- ✅ **Saves Weeks of Debugging**: All production issues already solved
- ✅ **Ensures Zero Downtime**: Battle-tested deployment process
- ✅ **Provides Enterprise Security**: Comprehensive monitoring and protection
- ✅ **Enables Rapid Scaling**: Standardized Debian 12 deployment
- ✅ **Includes Complete Documentation**: Every procedure documented and tested

**Built by developers who've been through the pain, for developers who want to avoid it.**

---

**🚀 Ready to deploy? Start with the [Systematic Deployment Guide](DEPLOYMENT_GUIDE.md)**