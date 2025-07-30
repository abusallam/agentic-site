# 🤖 AI Agent Prompt - Agentic AI Platform Development

## 🎯 **MANDATORY SESSION INITIALIZATION**

When starting ANY new session with this project, you MUST follow this protocol:

### **1. CRITICAL SAFETY CHECK** ⚠️
```
⚠️ PRODUCTION SYSTEM LIVE - DO NOT DISRUPT ⚠️

BEFORE ANY ACTIONS:
1. This is a LIVE PRODUCTION SYSTEM at https://consulting.sa
2. Real users may be accessing the system
3. NEVER restart, rebuild, or modify production without explicit permission
4. ALWAYS check system status first
5. Ask user which environment they want to work on: DEVELOPMENT or PRODUCTION
```

### **2. ENVIRONMENT IDENTIFICATION** 🌍
**ALWAYS ASK THE USER:**
```
🔄 Which environment do you want to work on?

A) 🚀 PRODUCTION (main branch) - https://consulting.sa
   - Live system with real users
   - Requires extreme caution
   - Only for critical fixes or approved deployments

B) 🛠️ DEVELOPMENT (develop branch) - https://dev.consulting.sa  
   - Safe development environment
   - Separate containers and database
   - Ideal for feature development and testing

C) 💻 LOCAL DEVELOPMENT (feature branch) - localhost
   - Local development setup
   - Complete isolation from production
   - Best for new feature development
```

### **3. PROJECT CONTEXT UNDERSTANDING** 📋
Read these documents in order:
1. `.kiro/specs/PROJECT_ANALYSIS.md` - Complete project overview
2. `.kiro/PROJECT_STATUS.md` - Current system status
3. `docs/development/DEVELOPMENT_LIFECYCLE.md` - Development workflow
4. `.kiro/specs/agentic-cicd-pipeline/tasks.md` - Current CI/CD progress

---

## 🏗️ **PROJECT ARCHITECTURE OVERVIEW**

### **What We're Building**
**consulting.sa** - Production-ready AI consulting SaaS platform with dual-agent architecture:

- **Frontend**: Next.js 15.4.1 + TypeScript + Tailwind CSS
- **Backend**: Python ADK Agent framework with Google Gemini AI
- **Database**: Supabase (PostgreSQL) with real-time features
- **Infrastructure**: Docker + Nginx + SSL on VPS (217.79.255.54)
- **Monitoring**: Prometheus + Grafana + N8N workflows
- **CI/CD**: GitHub Actions with automated deployment

### **Agent System Architecture**
```
CustomerJourneyAgent (Primary)
├── Customer inquiry processing with Google Gemini
├── Customer record management via Supabase
├── Workflow triggering via MCP/n8n
├── Requirements extraction from conversations
└── Health monitoring and metrics collection

N8nMCPAgent (Specialized)
├── Workflow execution and monitoring
├── MCP server communication
└── Automation pipeline management

Service Integration Layer
├── SupabaseService - Database operations
├── MCPService - n8n workflow integration
├── MonitoringService - Metrics and health monitoring
└── CICDService - Deployment automation
```

### **Current System Status**
- ✅ **PRODUCTION**: https://consulting.sa (LIVE)
- ✅ **DEVELOPMENT**: https://dev.consulting.sa (CONFIGURED)
- ✅ **MONITORING**: Full Prometheus/Grafana stack deployed
- ✅ **CI/CD**: GitHub Actions with automated deployment
- ✅ **SECURITY**: SSL, firewall, fail2ban active

---

## 🔄 **DEVELOPMENT WORKFLOW**

### **Branch Strategy**
```
main (production)     ← https://consulting.sa (LIVE SYSTEM)
├── develop           ← https://dev.consulting.sa (SAFE DEVELOPMENT)
├── feature/*         ← Local development branches
├── hotfix/*          ← Emergency production fixes
└── release/*         ← Release preparation
```

### **Environment Configuration**
```
PRODUCTION (main branch):
- URL: https://consulting.sa
- Containers: agentic-frontend-prod, agentic-backend-prod
- Database: Production Supabase instance
- Ports: Frontend (3000→443), Backend (8000)

DEVELOPMENT (develop branch):
- URL: https://dev.consulting.sa  
- Containers: agentic-frontend-dev, agentic-backend-dev
- Database: Development Supabase (dev_ prefixed tables)
- Ports: Frontend (3001→443), Backend (8001)

LOCAL (feature branches):
- URL: http://localhost:3000
- Local containers or direct execution
- Database: Local or development instance
- Environment: .env.development
```

---

## 🛠️ **DEVELOPMENT COMMANDS**

### **Environment Setup**
```bash
# Development Environment Setup
git checkout develop
cp .env.development .env
cd frontend && npm install && cd ..
cd backend && uv sync && cd agent && uv sync && cd ../..

# Start Development Servers
# Terminal 1 - Frontend
cd frontend && npm run dev

# Terminal 2 - Backend  
cd backend/agent && uv run python main.py
```

### **Testing Commands**
```bash
# Full Project Testing
./test-organized-structure.sh

# Frontend Testing
cd frontend
npm run build          # Production build test
npm run type-check     # TypeScript validation
npm run lint           # Code quality check

# Backend Testing
cd backend/agent
uv run python main.py  # Agent startup test
uv run pytest tests/   # Run test suite
```

### **Deployment Commands**
```bash
# Development Deployment (SAFE)
./infrastructure/scripts/deploy-dev-vps.sh

# Production Status Check (READ-ONLY)
./scripts/validate-deployment.sh

# Production Deployment (DANGEROUS - ASK FIRST)
./infrastructure/scripts/deploy-main-vps.sh
```

---

## 🚨 **SAFETY PROTOCOLS**

### **NEVER DO WITHOUT EXPLICIT PERMISSION**
- Restart production containers (`docker compose restart`)
- Rebuild production images (`docker compose build`)
- Modify production environment variables
- Run production deployment scripts
- Change Nginx configuration
- Update SSL certificates
- Modify database schema in production

### **ALWAYS DO FIRST**
- Check system status: `./scripts/validate-deployment.sh`
- Verify container health: `docker ps`
- Review logs: `docker compose logs`
- Understand user intent and environment preference
- Ask which branch/environment to work on

### **SAFE OPERATIONS**
- Read-only status checks and log viewing
- Local development and testing
- Development environment changes
- Documentation updates
- Code analysis and review

---

## 📊 **CURRENT CI/CD PIPELINE STATUS**

### **✅ COMPLETED TASKS** (Don't redo these)
- [x] 1. GitHub Actions CI/CD Infrastructure
- [x] 2.1 Frontend build and test pipeline
- [x] 2.2 Backend build and test pipeline  
- [x] 3.1 Docker configurations optimization
- [x] 4.1 Server provisioning automation
- [x] 4.2 Deployment automation scripts
- [x] 5.1 Static code analysis
- [x] 6.1 MCP deployment automation
- [x] 7.1 Application monitoring
- [x] 7.2 Alerting and notification system

### **🎯 AVAILABLE NEXT TASKS** (Safe to work on)
- [ ] 2.3 Integration test automation
- [ ] 3.2 Container registry integration
- [ ] 5.2 Compliance validation system
- [ ] 8.1 Database migration automation
- [ ] 8.2 Backup verification system
- [ ] 9.1 Automated test execution
- [ ] 9.2 End-to-end testing automation
- [ ] 10.1 Infrastructure as code
- [ ] 10.2 Secrets and environment management
- [ ] 11.1 Automated rollback mechanisms
- [ ] 11.2 Disaster recovery procedures
- [ ] 12.1 ADK framework integration
- [ ] 12.2 Final production deployment

---

## 🔧 **TECHNOLOGY STACK DETAILS**

### **Frontend (Next.js)**
```
Framework: Next.js 15.4.1 with App Router
Language: TypeScript 5.7.3
Styling: Tailwind CSS 3.4.17 + Shadcn/ui
Package Manager: npm
Build Tool: Webpack (Next.js built-in)
Testing: Jest (configured but not implemented)
Linting: ESLint + Prettier
```

### **Backend (Python ADK Agent)**
```
Framework: Google ADK (Agent Development Kit)
Language: Python 3.11+
Package Manager: uv (modern Python package manager)
API Framework: FastAPI
AI Integration: Google Gemini
Database Client: Supabase Python client
Testing: pytest
Linting: Black, isort, mypy, ruff
```

### **Infrastructure**
```
Containerization: Docker + Docker Compose
Web Server: Nginx with SSL termination
SSL Certificates: Cloudflare Origin certificates
Monitoring: Prometheus + Grafana + N8N
CI/CD: GitHub Actions workflows
VPS: Debian 12, 23GB RAM, 394GB storage
Domain: consulting.sa with wildcard SSL (*.consulting.sa)
```

---

## 📁 **PROJECT STRUCTURE**

### **Critical Directories**
```
frontend/                 # Next.js application (DO NOT MODIFY CORE FUNCTIONALITY)
├── app/                 # Next.js App Router pages
├── components/          # React components (40+ Shadcn/ui components)
├── lib/                 # Utilities and configurations
└── package.json         # npm dependencies

backend/                  # Python ADK agent system
├── agent/               # Main agent implementation
│   ├── my_adk_agent/    # CustomerJourneyAgent (ACTIVE DEVELOPMENT)
│   │   ├── agent.py     # Main agent class
│   │   └── services/    # Service integrations
│   └── pyproject.toml   # Python dependencies (uv)
└── tests/               # Test suite

infrastructure/           # Deployment and operations
├── docker/              # Docker configurations
├── scripts/             # Deployment scripts
├── nginx/               # Nginx configurations
└── monitoring/          # Monitoring stack

.kiro/                   # Kiro AI assistant configuration
├── specs/               # Feature specifications
└── PROJECT_STATUS.md    # Current system status

docs/                    # Documentation
├── development/         # Development guides
├── deployment/          # Deployment procedures
└── ai-agents/           # AI agent prompts (this file)
```

### **Key Configuration Files**
```
.env.example             # Environment template
.env.development         # Development environment
docker-compose.production.yml  # Production containers
docker-compose.development.yml # Development containers
package.json             # Root workspace management
workspace.json           # Workspace configuration
```

---

## 🎯 **DEVELOPMENT BEST PRACTICES**

### **Code Quality Standards**
- **TypeScript**: All new frontend code must use TypeScript
- **Python**: All backend code must have type hints and docstrings
- **Testing**: Write tests for new functionality
- **Documentation**: Update docs with any changes
- **Linting**: Code must pass all linting checks
- **Security**: Follow security best practices

### **Git Workflow**
```bash
# Feature Development
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
# ... make changes ...
git add .
git commit -m "feat: add feature description"
git push origin feature/your-feature-name
# Create PR to develop branch

# Hotfix Process
git checkout main
git checkout -b hotfix/critical-fix
# ... make minimal fix ...
git commit -m "fix: critical issue description"
# Create PR to main with emergency approval
```

### **Testing Strategy**
- **Local Testing**: Always test locally before pushing
- **Development Testing**: Test in dev.consulting.sa before production
- **Production Testing**: Comprehensive testing before main branch merge
- **Monitoring**: Watch metrics after deployment

---

## 🔗 **QUICK REFERENCE**

### **Health Check URLs**
- **Production**: https://consulting.sa/api/health
- **Development**: https://dev.consulting.sa/api/health
- **Prometheus**: http://217.79.255.54:9090
- **Grafana**: http://217.79.255.54:3001

### **VPS Access** (Use with extreme caution)
```bash
# SSH Access (PRODUCTION SERVER)
ssh root@217.79.255.54
Password: gt5qXy22aJ

# Container Management (READ-ONLY FIRST)
docker ps                    # Check container status
docker compose logs -f       # View logs
docker compose ps           # Service status
```

### **Emergency Contacts**
- **Technical Lead**: asim@consulting.sa
- **Production Issues**: Immediate notification required
- **Development Questions**: Use development environment first

---

## 🎯 **SESSION WORKFLOW TEMPLATE**

### **1. Session Initialization**
```
1. ⚠️ SAFETY CHECK: Acknowledge production system is live
2. 🌍 ENVIRONMENT: Ask user which environment (production/development/local)
3. 📋 CONTEXT: Read project analysis and current status
4. 🎯 INTENT: Understand what user wants to accomplish
5. 📋 PLAN: Create safe development approach
```

### **2. Development Process**
```
1. 🔍 ANALYZE: Understand current state and requirements
2. 🛠️ DEVELOP: Make changes in appropriate environment
3. 🧪 TEST: Comprehensive testing before deployment
4. 📚 DOCUMENT: Update documentation with changes
5. 🚀 DEPLOY: Safe deployment with monitoring
```

### **3. Session Completion**
```
1. ✅ VALIDATE: Ensure all changes work correctly
2. 📊 MONITOR: Check system health and metrics
3. 📚 UPDATE: Update project status and documentation
4. 🔄 HANDOFF: Prepare clear status for next session
```

---

## 🚀 **CURRENT DEVELOPMENT PRIORITIES**

### **Immediate Focus**
1. **Node.js & Next.js Upgrade**: Update to latest versions
2. **Frontend Development Environment**: Fix build issues
3. **Agentic Frontend Features**: Add AI capabilities to frontend
4. **User Subscriptions**: Implement subscription system
5. **CI/CD Pipeline Completion**: Finish remaining pipeline tasks

### **Long-term Goals**
- Complete CI/CD pipeline with all automation
- Implement comprehensive testing framework
- Add advanced monitoring and alerting
- Develop disaster recovery procedures
- Scale system for increased user load

---

**Remember**: This is a LIVE PRODUCTION SYSTEM. Safety, stability, and user experience are paramount. Always develop incrementally, test thoroughly, and maintain system reliability.

**Last Updated**: January 27, 2025  
**Status**: Production system operational, development environment configured  
**Next**: Node.js/Next.js upgrade and frontend agentic capabilities