# 🔄 Development Lifecycle - Agentic AI Platform

## 🎯 **Overview**

This document defines the complete development lifecycle for the Agentic AI Platform (consulting.sa), including branch strategies, environment management, and deployment processes. This ensures consistent development practices and smooth transitions between development and production.

---

## 🌳 **Branch Strategy**

### **Branch Structure**
```
main (production)     ← Live production system (https://consulting.sa)
├── develop           ← Development branch (https://dev.consulting.sa)
├── feature/*         ← Feature development branches
├── hotfix/*          ← Emergency production fixes
└── release/*         ← Release preparation branches
```

### **Branch Purposes**

#### **main (Production Branch)**
- **Purpose**: Live production system
- **URL**: https://consulting.sa
- **VPS**: 217.79.255.54 (production containers)
- **Deployment**: Automatic on merge to main
- **Protection**: Requires PR approval, all tests must pass
- **Database**: Production Supabase instance

#### **develop (Development Branch)**
- **Purpose**: Integration and testing environment
- **URL**: https://dev.consulting.sa
- **VPS**: 217.79.255.54 (development containers)
- **Deployment**: Automatic on push to develop
- **Database**: Development Supabase instance (dev_ prefixed tables)
- **Ports**: Different ports to avoid production conflicts

#### **feature/* (Feature Branches)**
- **Purpose**: Individual feature development
- **Naming**: `feature/feature-name` (e.g., `feature/user-authentication`)
- **Base**: Created from `develop`
- **Merge**: Back to `develop` via Pull Request
- **Testing**: Local development and testing

#### **hotfix/* (Hotfix Branches)**
- **Purpose**: Emergency production fixes
- **Naming**: `hotfix/issue-description` (e.g., `hotfix/payment-gateway-fix`)
- **Base**: Created from `main`
- **Merge**: To both `main` and `develop`
- **Deployment**: Immediate to production after testing

---

## 🏗️ **Environment Architecture**

### **Production Environment** ✅ LIVE
```
https://consulting.sa (main branch)
├── Frontend: Next.js (port 3000 → 443/80 via Nginx)
├── Backend: Python ADK Agent (port 8000)
├── Database: Supabase production instance
├── Monitoring: Prometheus (9090), Grafana (3001), N8N (5678)
├── SSL: Cloudflare certificates
└── Containers: agentic-frontend-prod, agentic-backend-prod, agentic-redis-prod
```

### **Development Environment** ✅ CONFIGURED
```
https://dev.consulting.sa (develop branch)
├── Frontend: Next.js (port 3001 → 443/80 via Nginx subdomain)
├── Backend: Python ADK Agent (port 8001)
├── Database: Supabase with dev_ prefixed tables
├── Monitoring: Shared with production (separate metrics)
├── SSL: Same wildcard certificate (*.consulting.sa)
└── Containers: agentic-frontend-dev, agentic-backend-dev, agentic-redis-dev
```

### **Local Development Environment**
```
http://localhost (feature branches)
├── Frontend: Next.js (port 3000)
├── Backend: Python ADK Agent (port 8000)
├── Database: Local Supabase or development instance
├── Environment: .env.development
└── Testing: Local testing and debugging
```

---

## 🚀 **Development Workflow**

### **1. Starting New Feature Development**
```bash
# 1. Switch to develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Set up local environment
cp .env.development .env
cd frontend && npm install && cd ..
cd backend && uv sync && cd agent && uv sync && cd ../..

# 4. Start local development
# Terminal 1 - Frontend
cd frontend && npm run dev

# Terminal 2 - Backend
cd backend/agent && uv run python main.py
```

### **2. Development Process**
```bash
# Make changes and test locally
npm run build          # Test frontend build
npm run type-check     # TypeScript validation
npm run lint           # Code quality

# Backend testing
cd backend/agent
uv run python main.py  # Test agent startup
uv run pytest tests/   # Run tests

# Commit changes
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

### **3. Integration Testing (Develop Branch)**
```bash
# Create Pull Request to develop branch
# After PR approval and merge:

# Automatic deployment to dev.consulting.sa
# Test integration with:
# - https://dev.consulting.sa (frontend)
# - https://dev.consulting.sa/api (backend)
# - Development database with dev_ tables
```

### **4. Production Deployment (Main Branch)**
```bash
# Create Pull Request from develop to main
# After thorough testing and approval:

# Automatic deployment to consulting.sa
# Production deployment includes:
# - Zero-downtime deployment
# - Health checks validation
# - Monitoring alerts
# - Backup creation
```

---

## 🔧 **Environment Configuration**

### **Environment Files**
- `.env.example` - Template with all variables
- `.env.development` - Development environment settings
- `.env.production` - Production environment settings (on VPS)
- `.env` - Local development (gitignored)

### **Key Environment Variables**
```env
# Environment Identification
NODE_ENV=development|production
ENVIRONMENT=development|production

# Database Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Development vs Production URLs
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa|https://consulting.sa
NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api|https://consulting.sa/api

# Service Ports (different for dev/prod)
FRONTEND_PORT=3001|3000
BACKEND_PORT=8001|8000

# AI Services (shared across environments)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Development Features
DEBUG_MODE=true|false
LOG_LEVEL=debug|info|error
```

---

## 🐳 **Docker Configuration**

### **Development Containers**
```yaml
# docker-compose.development.yml
services:
  frontend-dev:
    container_name: agentic-frontend-dev
    ports: ["3001:3000"]
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa

  backend-dev:
    container_name: agentic-backend-dev
    ports: ["8001:8000"]
    environment:
      - ENVIRONMENT=development
      - DEBUG_MODE=true
```

### **Production Containers**
```yaml
# docker-compose.production.yml
services:
  frontend-prod:
    container_name: agentic-frontend-prod
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://consulting.sa

  backend-prod:
    container_name: agentic-backend-prod
    ports: ["8000:8000"]
    environment:
      - ENVIRONMENT=production
      - DEBUG_MODE=false
```

---

## 🧪 **Testing Strategy**

### **Local Testing (Feature Branches)**
```bash
# Frontend testing
cd frontend
npm run build          # Production build test
npm run type-check     # TypeScript validation
npm run lint           # ESLint checks
npm run test           # Unit tests (when implemented)

# Backend testing
cd backend/agent
uv run python main.py  # Agent startup test
uv run pytest tests/   # Unit and integration tests
uv run python test_agent.py  # Agent-specific tests

# Full stack testing
./test-organized-structure.sh  # Complete project validation
```

### **Development Environment Testing (Develop Branch)**
```bash
# Automated testing on push to develop
# - Frontend build and deployment
# - Backend agent startup and health checks
# - Integration testing with development database
# - Service connectivity validation

# Manual testing
# - https://dev.consulting.sa functionality
# - API endpoints testing
# - Database operations with dev_ tables
```

### **Production Testing (Main Branch)**
```bash
# Pre-deployment testing
# - All development tests must pass
# - Performance testing
# - Security scanning
# - Database migration validation

# Post-deployment validation
# - Health check endpoints
# - Monitoring alerts
# - Performance metrics
# - User acceptance testing
```

---

## 📊 **Monitoring and Alerting**

### **Development Monitoring**
- **Health Checks**: https://dev.consulting.sa/api/health
- **Logs**: Docker container logs for debugging
- **Metrics**: Development-specific metrics in shared Prometheus
- **Alerts**: Development team notifications only

### **Production Monitoring**
- **Health Checks**: https://consulting.sa/api/health
- **Monitoring Stack**: Prometheus, Grafana, N8N workflows
- **Metrics**: Full performance and business metrics
- **Alerts**: Critical alerts to operations team
- **Uptime**: 99.9% availability target

---

## 🔄 **Deployment Automation**

### **Development Deployment**
```bash
# Triggered on push to develop branch
./infrastructure/scripts/deploy-dev-vps.sh

# Process:
# 1. Build development containers
# 2. Deploy to dev.consulting.sa
# 3. Run health checks
# 4. Update development database
# 5. Notify development team
```

### **Production Deployment**
```bash
# Triggered on merge to main branch
./infrastructure/scripts/deploy-main-vps.sh

# Process:
# 1. Create production backup
# 2. Build production containers
# 3. Zero-downtime deployment
# 4. Database migrations
# 5. Health check validation
# 6. Monitoring alert setup
# 7. Notify operations team
```

---

## 🚨 **Emergency Procedures**

### **Hotfix Process**
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue-fix

# 2. Make minimal fix and test locally
# 3. Deploy to development for validation
# 4. Create PR to main with emergency approval
# 5. Deploy to production immediately
# 6. Merge back to develop branch
```

### **Rollback Process**
```bash
# Production rollback
./infrastructure/scripts/rollback-production.sh

# Process:
# 1. Stop current containers
# 2. Restore previous container versions
# 3. Restore database backup if needed
# 4. Validate system health
# 5. Update monitoring
# 6. Notify team of rollback
```

---

## 📚 **Documentation Requirements**

### **Code Documentation**
- **Frontend**: JSDoc comments for complex functions
- **Backend**: Python docstrings for all classes and methods
- **API**: OpenAPI/Swagger documentation
- **Database**: Schema documentation and migration notes

### **Process Documentation**
- **Feature Development**: Document new features and their usage
- **Deployment Changes**: Update deployment procedures
- **Configuration Changes**: Document environment variable changes
- **Troubleshooting**: Add common issues and solutions

---

## 🎯 **Quality Gates**

### **Development Quality Gates**
- [ ] Code builds successfully
- [ ] All tests pass
- [ ] TypeScript compilation succeeds
- [ ] Linting passes without errors
- [ ] Security scans pass
- [ ] Documentation updated

### **Production Quality Gates**
- [ ] All development quality gates pass
- [ ] Integration tests pass in development environment
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Team approval obtained

---

## 🔗 **Quick Reference Commands**

### **Environment Setup**
```bash
# Development environment
git checkout develop
cp .env.development .env
npm install && cd backend && uv sync

# Production check
./scripts/validate-deployment.sh
```

### **Testing Commands**
```bash
# Local testing
./test-organized-structure.sh
cd frontend && npm run build
cd backend/agent && uv run python main.py

# Environment testing
curl https://dev.consulting.sa/api/health
curl https://consulting.sa/api/health
```

### **Deployment Commands**
```bash
# Development deployment
./infrastructure/scripts/deploy-dev-vps.sh

# Production deployment (automatic on merge)
# Manual: ./infrastructure/scripts/deploy-main-vps.sh
```

---

**Last Updated**: January 27, 2025  
**Status**: Development lifecycle fully documented and operational  
**Next**: Implement remaining CI/CD pipeline tasks with this workflow