# 🔍 Agentic AI Platform - Complete Project Analysis

## 🚨 **MANDATORY: READ THIS FIRST IN EVERY SESSION**

This document provides a comprehensive analysis of the project structure, architecture, and current status. **ALWAYS** reference this document when starting a new session to understand the full context of what we're building.

---

## 🎯 **Project Overview**

### **What We're Building**
**consulting.sa** - A production-ready AI consulting SaaS platform with dual-agent architecture for customer journey orchestration and workflow automation.

### **Current Status: LIVE PRODUCTION** ✅
- **Website**: https://consulting.sa (OPERATIONAL)
- **VPS**: 217.79.255.54 (RUNNING)
- **Phase**: CI/CD Pipeline Enhancement Ready
- **Last Updated**: July 23, 2025

---

## 🏗️ **Architecture Deep Dive**

### **Frontend Architecture (Next.js)**
```
app/                          # Next.js 15+ App Router
├── page.tsx                 # Landing page with hero section
├── about/                   # About page
├── services/                # Services showcase
├── consulting/              # Consulting services
├── documentation/           # API documentation
├── contact/                 # Contact forms
├── auth/                    # Authentication pages
├── admin/                   # Admin dashboard
├── customer/                # Customer portal
└── api/                     # API routes
    ├── health/              # Health check endpoints
    ├── agent/               # Agent API endpoints
    ├── chat/                # Chat functionality
    ├── customer/            # Customer management
    └── metrics/             # Metrics collection

components/                   # React components
├── ui/                      # Shadcn/ui components (40+ components)
├── consulting/              # Consulting-specific components
├── features/                # Feature components
├── layout/                  # Layout components
└── chatbot/                 # Chatbot widget

lib/                         # Utilities and configurations
├── supabase.ts             # Supabase client
├── brand.ts                # Brand configuration
├── i18n-enhanced.tsx       # Internationalization
└── utils.ts                # Utility functions
```

### **Backend Architecture (Python ADK Agent)**
```
agent/                       # Python ADK Agent framework
├── my_adk_agent/           # Main agent implementation
│   ├── agent.py            # CustomerJourneyAgent (main orchestrator)
│   ├── services/           # Service integrations
│   │   ├── supabase_service.py      # Database operations
│   │   ├── mcp_service.py           # n8n workflow integration
│   │   ├── monitoring_service.py    # Metrics and monitoring
│   │   └── cicd_service.py          # CI/CD automation
│   └── tools/              # ADK tools for agent capabilities
├── n8n_mcp_agent/         # N8nMCPAgent (workflow specialist)
├── specialized_agents/     # Domain-specific agents
│   ├── technical_agent.py
│   ├── sales_agent.py
│   ├── customer_support_agent.py
│   └── accountant_agent.py
├── tests/                  # Comprehensive test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── smoke/              # Smoke tests
├── api_server.py          # FastAPI server
└── requirements.txt       # Python dependencies
```

### **Infrastructure Architecture**
```
VPS (217.79.255.54)         # Production server
├── Docker Compose          # Container orchestration
│   ├── agentic-frontend-prod    # Next.js container (port 3000)
│   ├── agentic-backend-prod     # Python agent (port 8000)
│   └── agentic-redis-prod       # Redis cache (port 6379)
├── Nginx                   # Reverse proxy (ports 80/443)
├── SSL Certificates        # Cloudflare SSL
├── Monitoring Stack        # Prometheus, Grafana, N8N
│   ├── Prometheus (9090)   # Metrics collection
│   ├── Grafana (3001)      # Dashboards
│   ├── N8N (5678)          # Workflow automation
│   ├── Alertmanager        # Alert routing
│   └── Node Exporter       # System metrics
└── Security                # UFW Firewall + Fail2ban
```

---

## 🤖 **Agent System Deep Dive**

### **CustomerJourneyAgent (Primary)**
- **Purpose**: Main orchestration agent for customer interactions
- **Location**: `agent/my_adk_agent/agent.py`
- **Capabilities**:
  - Customer inquiry processing with Google Gemini
  - Customer record management via Supabase
  - Workflow triggering via MCP/n8n
  - Requirements extraction from conversations
  - Health monitoring and metrics collection

### **N8nMCPAgent (Specialized)**
- **Purpose**: Dedicated n8n workflow automation
- **Location**: `agent/n8n_mcp_agent/agent.py`
- **Capabilities**:
  - Workflow execution and monitoring
  - MCP server communication
  - Automation pipeline management

### **Service Integration Layer**
- **SupabaseService**: Database operations and customer management
- **MCPService**: n8n workflow integration via Model Context Protocol
- **MonitoringService**: Metrics collection and health monitoring
- **CICDService**: Deployment automation and pipeline management

---

## 🔧 **Technology Stack Analysis**

### **Frontend Stack**
- **Framework**: Next.js 15.4.1 with App Router
- **Language**: TypeScript 5.7.3
- **Styling**: Tailwind CSS 3.4.17 + Shadcn/ui
- **State Management**: React hooks + Supabase real-time
- **Icons**: Lucide React (1000+ icons)
- **Internationalization**: Custom i18n system (Arabic/English)

### **Backend Stack**
- **Framework**: Google ADK (Agent Development Kit)
- **Language**: Python 3.11+ with uv package manager
- **API**: FastAPI for additional endpoints
- **AI**: Google Gemini for conversational AI
- **Database**: Supabase (PostgreSQL-based)
- **Workflow**: n8n via MCP server integration

### **Infrastructure Stack**
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx with SSL termination
- **SSL**: Cloudflare Origin certificates
- **Monitoring**: Prometheus + Grafana + N8N
- **CI/CD**: GitHub Actions workflows
- **VPS**: Debian 12, 23GB RAM, 394GB storage

---

## 🚀 **Current CI/CD Pipeline Status**

### **✅ Implemented (DO NOT REDO)**
1. **GitHub Actions Infrastructure** - Complete workflow setup
2. **Frontend Build Pipeline** - Next.js testing and building
3. **Backend Build Pipeline** - Python ADK testing with pytest
4. **Docker Optimization** - Multi-stage builds configured
5. **VPS Infrastructure** - Ansible playbooks for server setup
6. **Deployment Automation** - Zero-downtime deployment scripts
7. **Security Scanning** - CodeQL, Dependabot, Trivy integration
8. **MCP Integration** - Workflow automation service
9. **Application Monitoring** - Health checks and metrics
10. **Alerting System** - Slack integration and notifications

### **🎯 Next Available Tasks**
- **Integration Testing** - Service connection test automation
- **Container Registry** - GitHub Container Registry integration
- **Compliance Validation** - GDPR and security policy enforcement
- **Database Automation** - Migration and backup management
- **Testing Framework** - E2E and performance testing
- **Configuration Management** - Infrastructure as code
- **Rollback Systems** - Automated failure recovery

---

## 📁 **File Structure Analysis**

### **Key Configuration Files**
- `.env` - Production environment variables (CRITICAL)
- `docker-compose.production.yml` - Container orchestration
- `nginx/production.conf` - Nginx reverse proxy config
- `ssl/consulting.sa.*` - SSL certificates
- `package.json` - Node.js dependencies and scripts
- `agent/pyproject.toml` - Python dependencies (uv)

### **Critical Directories**
- `app/` - Next.js application (DO NOT MODIFY CORE FUNCTIONALITY)
- `agent/my_adk_agent/` - Main agent code (ACTIVE DEVELOPMENT)
- `components/` - React UI components (STABLE)
- `monitoring/` - Complete monitoring stack (DEPLOYED)
- `.github/workflows/` - CI/CD pipelines (ACTIVE)
- `scripts/` - Deployment and management scripts

### **Archive Structure**
- `archive/` - Historical files and cleanup scripts
- `tools/` - Organized utilities (database, security, monitoring)
- `docs/` - Comprehensive documentation

---

## 🔑 **Environment & Secrets**

### **Production Environment**
- **VPS Access**: root@217.79.255.54 (password: gt5qXy22aJ)
- **Domain**: consulting.sa with Cloudflare SSL
- **Database**: Supabase production instance
- **AI Services**: Google Gemini API integrated
- **Monitoring**: Full Prometheus/Grafana stack

### **Service Integrations**
- **Supabase**: Database and real-time features
- **Google Gemini**: AI model for conversations
- **n8n**: Workflow automation platform
- **MCP Server**: Communication bridge
- **Livekit**: Real-time communication
- **Stripe**: Payment processing (configured)

---

## 🚨 **Critical Production Considerations**

### **NEVER DO WITHOUT EXPLICIT PERMISSION**
- Restart production containers
- Modify environment variables
- Change Nginx configuration
- Update SSL certificates
- Rebuild Docker images
- Run deployment scripts

### **ALWAYS DO FIRST**
- Check system status: `./scripts/validate-deployment.sh`
- Verify container health: `docker ps`
- Review logs before changes: `docker compose logs`
- Understand user intent before acting

### **SAFE OPERATIONS**
- Read-only status checks
- Log viewing and analysis
- Local development and testing
- Documentation updates
- Code analysis and review

---

## 📊 **Performance Metrics**

### **Current Performance**
- **Response Time**: < 1.5s average
- **Memory Usage**: < 80% utilization
- **Disk Usage**: < 70% utilization
- **SSL Certificate**: Valid until 2040
- **Health Checks**: 28/28 tests passing

### **Monitoring Endpoints**
- **Frontend Health**: https://consulting.sa/api/health
- **Backend Health**: http://217.79.255.54:8000/health
- **Prometheus**: http://217.79.255.54:9090
- **Grafana**: http://217.79.255.54:3001

---

## 🎯 **Development Workflow**

### **When Starting New Session**
1. **Read this document** - Understand full project context
2. **Check production status** - Verify system health
3. **Review task progress** - Check CI/CD pipeline status
4. **Understand user intent** - What are they trying to achieve?
5. **Plan safe approach** - Local dev → staging → production

### **Safe Development Practices**
- **Local First**: Develop and test locally
- **Incremental**: Small, focused changes
- **Documented**: Update docs with changes
- **Tested**: Comprehensive testing before deployment
- **Monitored**: Watch metrics after deployment

---

## 📚 **Key Documentation**

### **Essential Reading**
- `README.md` - Project overview and setup
- `PROJECT_STRUCTURE.md` - File organization
- `.kiro/PROJECT_STATUS.md` - Current system status
- `DEPLOYMENT_GUIDE.md` - Deployment procedures
- `docs/deployment/DEPLOYMENT_LESSONS_LEARNED.md` - Critical lessons

### **Spec Documents**
- `.kiro/specs/agentic-cicd-pipeline/` - Current CI/CD pipeline spec
- Requirements, design, and task documents
- Track progress and next steps

---

## 🔄 **Current Focus: CI/CD Pipeline Enhancement**

We are systematically building a comprehensive CI/CD pipeline while maintaining the live production system. The next phase involves implementing advanced testing, monitoring, and automation features to create a world-class deployment pipeline for the agentic AI platform.

**Remember**: This is a LIVE PRODUCTION SYSTEM serving real users. Stability and reliability are paramount while we enhance capabilities.

---

**Last Updated**: July 23, 2025  
**Status**: Production Ready with CI/CD Enhancement in Progress  
**Next Session**: Always start by reading this document and checking system status