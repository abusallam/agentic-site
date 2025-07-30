# Agentic AI Platform Documentation

## 📚 Documentation Overview

Welcome to the comprehensive documentation for the Agentic AI Platform. This documentation is designed to help developers, AI agents, and system administrators understand, develop, and maintain the platform effectively.

## 🎯 Quick Start for AI Agents

**🚨 CRITICAL FIRST STEP**: Before making ANY changes, always ask:
> "Should I work on the **development branch** (safe testing at dev.consulting.sa) or **production branch** (live system at consulting.sa)?"

### Essential Reading
1. **[AI Agent Master Prompt](ai-agents/AI_AGENT_PROMPT.md)** - Start here for complete project understanding
2. **[Development Workflow](ai-agents/development-workflow.md)** - Step-by-step development process
3. **[Project Architecture](ai-agents/project-architecture.md)** - Technical system overview
4. **[Coding Standards](ai-agents/coding-standards.md)** - Code quality guidelines

## 📖 Documentation Structure

### 🤖 AI Agents Documentation
Essential guides for AI coding agents working on the project.

| Document | Purpose | Audience |
|----------|---------|----------|
| [AI Agent Master Prompt](ai-agents/AI_AGENT_PROMPT.md) | Complete project overview and guidelines | AI Agents |
| [Development Workflow](ai-agents/development-workflow.md) | Step-by-step development process | AI Agents, Developers |
| [Project Architecture](ai-agents/project-architecture.md) | Technical architecture overview | AI Agents, Architects |
| [Coding Standards](ai-agents/coding-standards.md) | Code quality and style guidelines | AI Agents, Developers |

### 🛠️ Development Documentation
Comprehensive guides for developers and development processes.

| Document | Purpose | Audience |
|----------|---------|----------|
| [Development Setup](development/DEVELOPMENT_SETUP.md) | Environment setup and configuration | Developers |
| [Branch Strategy](development/branch-strategy.md) | Git workflow and branch management | Developers, AI Agents |
| [Deployment Guide](development/deployment-guide.md) | Deployment processes and procedures | DevOps, Developers |
| [Testing Guide](development/testing-guide.md) | Testing strategies and procedures | Developers, QA |

### 📊 Project Status Documentation
Current state analysis and planning documents.

| Document | Purpose | Audience |
|----------|---------|----------|
| [Technology Stack](project-status/technology-stack.md) | Current technology analysis | Architects, Developers |
| [Upgrade Plan](project-status/upgrade-plan.md) | Technology upgrade strategy | Technical Leads |
| [Dependency Audit](project-status/dependency-audit.md) | Dependency status and security | Developers, Security |
| [Feature Roadmap](project-status/feature-roadmap.md) | Future development plans | Product, Management |

### 🔧 Troubleshooting Documentation
Problem-solving guides and maintenance procedures.

| Document | Purpose | Audience |
|----------|---------|----------|
| [Troubleshooting Guide](troubleshooting/TROUBLESHOOTING.md) | Common issues and solutions | All Users |

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    Agentic AI Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Frontend      │    │     Backend      │    │  External   │ │
│  │   (Next.js)     │◄──►│   (Python ADK)   │◄──►│  Services   │ │
│  │                 │    │                  │    │             │ │
│  │ • Website       │    │ • Agent System   │    │ • Supabase  │ │
│  │ • Chatbots      │    │ • Orchestration  │    │ • Gemini AI │ │
│  │ • User UI       │    │ • Integrations   │    │ • Stripe    │ │
│  │ • Admin Panel   │    │ • MCP Server     │    │ • Livekit   │ │
│  └─────────────────┘    └──────────────────┘    │ • n8n       │ │
│                                                 └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Environment Architecture
```
Production (main branch)
├── URL: https://consulting.sa
├── Directory: /opt/agentic-platform
├── Ports: 3000 (frontend), 8000 (backend)
└── SSL: Wildcard certificate

Development (develop branch)
├── URL: https://dev.consulting.sa
├── Directory: /opt/agentic-platform-dev
├── Ports: 3001 (frontend), 8001 (backend)
└── SSL: Same wildcard certificate
```

## 🚀 Technology Stack

### Frontend Stack
- **Next.js 15.4.1**: React framework with App Router ✅
- **React 19.1.0**: UI library with latest features ✅
- **TypeScript 5.7.3**: Type-safe JavaScript ✅
- **Tailwind CSS 3.4.17**: Utility-first CSS framework ✅
- **shadcn/ui**: Modern component library ✅

### Backend Stack
- **Python 3.12.9**: Modern Python runtime ✅
- **Google ADK**: Agent Development Kit ✅
- **FastAPI**: High-performance API framework ✅
- **Supabase**: PostgreSQL database with real-time features ✅

### Infrastructure
- **Docker**: Containerization ✅
- **Nginx**: Reverse proxy with SSL termination ✅
- **Ubuntu VPS**: Production server ✅
- **Wildcard SSL**: *.consulting.sa certificate ✅

## 🔄 Development Workflow

### Branch Strategy
```
main (production)
├── develop (development)
│   ├── feature/your-feature
│   └── hotfix/critical-fix
```

### Deployment Process
1. **Development**: Work on `develop` branch → Deploy to `dev.consulting.sa`
2. **Testing**: Validate functionality in development environment
3. **Production**: Merge to `main` → Deploy to `consulting.sa`

### Key Commands
```bash
# Development deployment
./infrastructure/scripts/deploy-dev-vps.sh

# Production deployment
./infrastructure/scripts/deploy.sh

# Health checks
curl -f https://dev.consulting.sa/api/health
curl -f https://consulting.sa/api/health
```

## 📋 Quick Reference

### Health Check URLs
- **Production Frontend**: https://consulting.sa/api/health
- **Production Backend**: https://consulting.sa:8000/health
- **Development Frontend**: https://dev.consulting.sa/api/health
- **Development Backend**: https://dev.consulting.sa:8001/health

### Management Commands
```bash
# Development environment management
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh status'
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh logs'
ssh root@217.79.255.54 'cd /opt/agentic-platform-dev && ./dev-manage.sh restart'

# Production environment management
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose ps'
ssh root@217.79.255.54 'cd /opt/agentic-platform && docker-compose logs -f'
```

### Testing Commands
```bash
# Frontend testing
cd frontend && npm test
cd frontend && npm run e2e

# Backend testing
cd backend/agent && pytest
cd backend/agent && pytest --cov=my_adk_agent
```

## 🎯 Best Practices

### For AI Agents
1. **Always ask about environment** (development vs production)
2. **Read the AI Agent Master Prompt** before starting work
3. **Follow the development workflow** step by step
4. **Test in development first** before production changes
5. **Use coding standards** for consistent code quality

### For Developers
1. **Work on feature branches** from develop
2. **Write tests** for all new functionality
3. **Update documentation** when making changes
4. **Use proper commit messages** following conventional commits
5. **Review code thoroughly** before merging

### For System Administrators
1. **Monitor health endpoints** regularly
2. **Keep SSL certificates** up to date
3. **Perform regular backups** of data and configurations
4. **Update dependencies** regularly for security
5. **Follow troubleshooting guides** for common issues

## 🆘 Getting Help

### Common Issues
1. **Check the [Troubleshooting Guide](troubleshooting/TROUBLESHOOTING.md)** first
2. **Verify health endpoints** are responding
3. **Check recent deployments** for potential causes
4. **Review logs** for error messages
5. **Test in development** environment first

### Emergency Contacts
- **System Issues**: Check troubleshooting guide
- **Security Issues**: Follow security incident procedures
- **Performance Issues**: Monitor resource usage and logs

## 📈 Current Status

### ✅ Production Ready
- **Frontend**: Next.js 15 with modern UI/UX
- **Backend**: Python ADK agent system
- **Database**: Supabase with real-time capabilities
- **AI Integration**: Google Gemini chatbot
- **Payment Processing**: Stripe integration
- **Deployment**: Docker containers with SSL
- **Development Environment**: Complete dev.consulting.sa setup

### 🔄 In Progress
- **Documentation**: Comprehensive guides (90% complete)
- **Testing**: Enhanced test coverage
- **Performance**: Optimization improvements

### 📅 Next Quarter (Q1 2025)
- **User Authentication**: Registration and login system
- **Subscription Management**: Tiered pricing and billing
- **Enhanced Chatbot**: Advanced conversation features
- **API Documentation**: Complete endpoint documentation

## 🎉 Success Metrics

### Technical Excellence
- **Uptime**: 99.9% availability ✅
- **Performance**: <100ms API response time ✅
- **Security**: Zero critical vulnerabilities ✅
- **Test Coverage**: >80% code coverage 🔄

### Documentation Quality
- **Completeness**: All major components documented ✅
- **Accuracy**: Documentation matches implementation ✅
- **Usability**: Easy to follow for new developers ✅
- **Maintenance**: Regular updates and improvements 🔄

## 📝 Contributing to Documentation

### Documentation Standards
1. **Use clear, concise language**
2. **Include practical examples**
3. **Keep information current**
4. **Follow markdown formatting standards**
5. **Test all code examples**

### Update Process
1. **Make changes** in appropriate documentation files
2. **Test examples** to ensure they work
3. **Update table of contents** if needed
4. **Commit with descriptive messages**
5. **Deploy to development** for review

---

## 📞 Support

For questions about this documentation or the platform:

1. **Check existing documentation** first
2. **Review troubleshooting guides** for common issues
3. **Test in development environment** before production
4. **Follow established workflows** and best practices

**Remember**: This is a production system serving real customers. Always prioritize stability, security, and thorough testing!