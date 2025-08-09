# 🤖 Kiro Configuration - Agentic AI Platform

## Overview

This `.kiro` folder contains the complete configuration and documentation for AI-powered development assistance on the **consulting.sa** agentic AI platform. It enables context-aware development, automated workflows, and production-ready standards enforcement.

## 📁 Directory Structure

```
.kiro/
├── README.md                    # This file - complete overview
├── PROJECT_STATUS.md            # Current system status and health
├── SERVER_ACCESS.md             # VPS credentials and connection info
├── SETUP_COMPLETE.md            # Setup summary and usage guide
├── specs/                       # Feature specifications
│   ├── README.md                # Specs overview and management
│   ├── PROJECT_ANALYSIS.md      # Complete project analysis
│   ├── agentic-cicd-pipeline/   # Active CI/CD enhancement spec
│   └── [other-specs]/           # Additional feature specifications
├── steering/                    # Project context and standards
│   ├── product.md               # Product vision and business context
│   ├── tech.md                  # Technology stack and standards
│   ├── structure.md             # Project structure conventions
│   └── project-architecture.md  # Architecture documentation
├── hooks/                       # Event-driven automation
│   ├── README.md                # Hooks documentation and examples
│   ├── react-test-generator.yml # Auto-generate React tests
│   ├── agent-docs-updater.yml   # Auto-update agent documentation
│   └── security-scanner.yml     # Security scanning automation
└── settings/                    # Kiro configuration
    ├── README.md                # Settings and configuration guide
    └── mcp.json                 # MCP server configurations
```

## 🎯 Key Components

### 1. Steering Files - Project Context
**Purpose**: Provide consistent project context across all Kiro sessions

- **`product.md`**: Business goals, target users, value propositions
- **`tech.md`**: Technology stack, dependencies, coding standards
- **`structure.md`**: File organization, naming conventions, patterns
- **`project-architecture.md`**: System architecture and design decisions

**How it works**: Kiro automatically reads these files to understand your project context, ensuring consistent development patterns and decision-making.

### 2. Specs - Feature Development
**Purpose**: Structured feature development through Requirements → Design → Tasks

- **Spec-driven development**: Transform ideas into actionable implementation plans
- **Three-phase process**: Requirements gathering, technical design, task breakdown
- **Progress tracking**: Checkbox-based task completion monitoring
- **Quality assurance**: Requirements mapping and acceptance criteria

**Current active spec**: `agentic-cicd-pipeline` - Comprehensive CI/CD pipeline enhancement

### 3. Hooks - Automated Workflows
**Purpose**: Event-driven AI automation for repetitive development tasks

- **`react-test-generator`**: Auto-generate tests when saving React components
- **`agent-docs-updater`**: Auto-update documentation when modifying agent services
- **`security-scanner`**: Manual security scanning and vulnerability assessment

**Triggers**: File saves, manual commands, scheduled execution

### 4. Settings - Configuration Management
**Purpose**: Customize Kiro behavior and integrate external tools

- **MCP Integration**: Model Context Protocol for external tool access
- **Project Settings**: Environment-specific configurations
- **Tool Definitions**: Custom automation tool configurations
- **Security Settings**: Access control and API key management

## 🚀 System Status

### Production Environment ✅ LIVE
- **Website**: https://consulting.sa (OPERATIONAL)
- **VPS**: 217.79.255.54 (SSH: gnqLG7FDd4)
- **Containers**: agentic-*-prod (DO NOT TOUCH)
- **Services**: Frontend (3000), Backend (8000), Redis (6379), N8N (5678)

### Development Environment ✅ READY
- **Containers**: agentic-*-dev (SAFE TO MODIFY)
- **Services**: Frontend (3001), Backend (8001), Redis (6380), N8N (5679)
- **Status**: Ready for enhancements and testing

## 🛠️ How to Use

### For New Sessions
1. **Automatic Context Loading**: Kiro reads steering files automatically
2. **Project Understanding**: Full architecture and standards awareness
3. **Consistent Development**: Established patterns enforced
4. **Automation Active**: Hooks trigger based on your work

### For Development Work
```bash
# Check system status
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker ps'

# Safe dev container management
sshpass -p 'gnqLG7FDd4' ssh root@217.79.255.54 'docker stop agentic-frontend-dev agentic-backend-dev'

# Trigger security scan
kiro hooks run security-scanner

# Work with specs
# 1. Review .kiro/specs/agentic-cicd-pipeline/
# 2. Execute tasks from the implementation plan
# 3. Update progress by checking off completed items
```

### For Feature Development
1. **Create New Spec**: Follow existing spec templates
2. **Requirements Phase**: Define user stories and acceptance criteria
3. **Design Phase**: Create technical architecture and data models
4. **Tasks Phase**: Break down into actionable implementation steps
5. **Execute**: Follow the task list systematically

## 🔧 Architecture Integration

### Dual-Agent System
- **CustomerJourneyAgent**: Main orchestration for customer interactions
- **N8nMCPAgent**: Specialized n8n workflow automation
- **Service Layer**: Supabase, MCP, Monitoring, CI/CD integrations

### Technology Stack
- **Frontend**: Next.js 15+ with TypeScript, Tailwind CSS, Shadcn/ui
- **Backend**: Python ADK Agent framework with Google Gemini
- **Database**: Supabase with real-time features
- **Infrastructure**: Docker containers, Nginx, SSL, monitoring stack

### Development Standards
- **Code Quality**: Type hints, linting, comprehensive testing
- **Security**: GDPR compliance, encryption, secure authentication
- **Performance**: <1.5s response times, <80% resource utilization
- **Deployment**: Zero-downtime, health checks, automated rollback

## 🛡️ Safety Protocols

### Production Protection
- **Never modify production containers** without explicit permission
- **Always check system status** before making changes
- **Use development containers** for all testing and development
- **Validate changes thoroughly** before considering production deployment

### Development Best Practices
- **Follow established patterns** defined in steering files
- **Use spec-driven development** for complex features
- **Leverage automation hooks** for quality and consistency
- **Document all changes** through automated systems

## 📊 Current Priorities

### Active Development
- **CI/CD Pipeline Enhancement**: Advanced testing, monitoring, automation
- **Container Registry Integration**: GitHub Container Registry setup
- **Database Migration Automation**: Supabase migration management
- **Security Hardening**: Compliance validation and vulnerability management

### Next Phase
- **Feature Expansion**: Multi-language support, analytics, API marketplace
- **Testing Framework**: E2E testing, performance regression testing
- **Configuration Management**: Infrastructure as code, secrets management
- **Rollback Systems**: Automated failure recovery and disaster recovery

## 🎊 Benefits

### For Developers
- **Context Awareness**: Kiro understands your complete project
- **Automated Quality**: Tests and documentation generated automatically
- **Consistent Standards**: Established patterns enforced across development
- **Reduced Boilerplate**: Hooks handle repetitive tasks

### For the Project
- **Production Stability**: Safe development practices with container separation
- **Quality Assurance**: Automated testing and security scanning
- **Documentation**: Always up-to-date API and service documentation
- **Scalability**: Structured approach to feature development

### For the Team
- **Knowledge Preservation**: Project context captured in steering files
- **Onboarding**: New team members get instant project understanding
- **Consistency**: Same development patterns across all contributors
- **Efficiency**: AI-powered assistance for common development tasks

---

**Configuration Version**: 2.1.0  
**Last Updated**: January 8, 2025  
**System Status**: ✅ Production Ready with Enhanced AI Assistance  
**Next Session**: Ready for development work with full context awareness

**🚀 The agentic AI platform is now equipped with comprehensive AI-powered development assistance. Focus on building features while Kiro handles automation, maintains consistency, and provides intelligent support throughout your development workflow.**