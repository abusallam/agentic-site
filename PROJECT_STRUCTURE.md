# 📁 Agentic AI Platform - Project Structure

This document outlines the organized project structure after cleanup and reorganization.

## 🏗️ Main Project Structure

```
agentic-platform/
├── 🌐 Frontend (Next.js)
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility libraries
│   ├── public/                 # Static assets
│   └── styles/                 # CSS styles
│
├── 🤖 Backend (Python ADK Agent)
│   └── agent/
│       ├── my_adk_agent/      # Main agent code
│       │   ├── services/      # Service integrations
│       │   └── tools/         # ADK tools
│       ├── tests/             # Backend tests
│       ├── api_server.py      # FastAPI server
│       └── requirements.txt   # Python dependencies
│
├── 🧪 Testing
│   └── tests/
│       ├── e2e/               # End-to-end tests
│       ├── integration/       # Integration tests
│       └── unit/              # Unit tests
│
├── 📊 Monitoring Stack (NEW)
│   ├── monitoring/            # Complete monitoring setup
│   │   ├── docker-compose.monitoring.yml  # Monitoring services
│   │   ├── prometheus/        # Metrics collection
│   │   │   ├── prometheus.yml # Prometheus config
│   │   │   └── rules/         # Alert rules
│   │   ├── grafana/          # Dashboards & visualization
│   │   │   └── dashboards/   # Pre-built dashboards
│   │   ├── alertmanager/     # Alert routing
│   │   ├── n8n/workflows/    # Automation workflows
│   │   └── blackbox/         # Endpoint monitoring
│   └── docs/monitoring/      # Monitoring documentation
│
├── 🔧 Infrastructure
│   ├── infrastructure/        # Ansible playbooks
│   ├── nginx/                 # Nginx configurations
│   ├── ssl/                   # SSL certificates
│   └── scripts/               # Deployment scripts
│       ├── deploy-monitoring-clean.sh  # Monitoring deployment
│       └── validate-deployment.sh      # System validation
│
├── 🚀 CI/CD
│   ├── .github/workflows/     # GitHub Actions
│   ├── docker-compose.*.yml   # Container orchestration
│   ├── Dockerfile.frontend    # Frontend container
│   └── Dockerfile.backend     # Backend container
│
├── 🛠️ Tools (Organized)
│   ├── tools/
│   │   ├── database/          # Database utilities
│   │   ├── security/          # Security tools
│   │   └── monitoring/        # Monitoring tools
│   └── archive/               # Archived/legacy files
│       ├── cleanup/           # Cleanup scripts
│       ├── deployment/        # Old deployment files
│       ├── testing/           # Test reports
│       ├── development/       # Development utilities
│       └── analysis/          # Project analysis
│
├── 📚 Documentation
│   ├── docs/                  # Project documentation
│   ├── README.md              # Main project README
│   ├── DEPLOYMENT_GUIDE.md    # Deployment instructions
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   └── PROJECT_STRUCTURE.md   # This file
│
└── 📝 Configuration
    ├── .env                   # Environment variables
    ├── .env.example          # Template
    ├── package.json          # Node.js dependencies
    ├── tsconfig.json         # TypeScript config
    ├── tailwind.config.ts    # Tailwind CSS config
    ├── next.config.mjs       # Next.js config
    ├── jest.config.js        # Jest testing config
    └── playwright.config.ts  # Playwright E2E config
```

## 🗂️ Organized Files

### ✅ **Moved to Archive**
- **Cleanup Scripts**: `archive/cleanup/`
- **Old Deployment Files**: `archive/deployment/`
- **Test Reports**: `archive/testing/`
- **Development Utilities**: `archive/development/`
- **Project Analysis**: `archive/analysis/`

### ✅ **Moved to Tools**
- **Database Tools**: `tools/database/`
- **Security Tools**: `tools/security/`
- **Monitoring Tools**: `tools/monitoring/`

### ❌ **Removed (Coolify)**
- `.coolify/` directory
- `coolify.json`
- `docker-compose.coolify.yml`
- `scripts/deploy-coolify.sh`
- `docs/deployment/COOLIFY_DEPLOYMENT.md`
- All Coolify labels from docker-compose files
- Coolify references from documentation

### ❌ **Removed (Duplicates)**
- `.env.production`, `.env.sample`, `.env.production.template`
- `Dockerfile`, `Dockerfile.production`, `Dockerfile.simple`
- Various duplicate Python scripts
- Old status and deployment scripts

## 🎯 **Current Active Files**

### **Core Application**
- `app/` - Next.js frontend application
- `agent/` - Python ADK backend agent
- `components/` - React UI components

### **Configuration**
- `.env` - Main environment configuration
- `package.json` - Node.js dependencies
- `docker-compose.production.yml` - Production deployment

### **Deployment**
- `deploy.sh` - Main deployment script
- `scripts/test-and-deploy.sh` - Comprehensive deployment
- `scripts/deploy-main-vps.sh` - VPS deployment
- `scripts/setup-monitoring.sh` - Monitoring setup

### **Infrastructure**
- `nginx/production.conf` - Nginx configuration
- `ssl/` - SSL certificates (Cloudflare)
- `monitoring/` - Prometheus & Grafana configs

## 🚀 **Ready for Deployment**

The project is now clean, organized, and ready for deployment with:

1. ✅ **Clean Structure** - All files properly organized
2. ✅ **No Coolify Dependencies** - Removed all Coolify references
3. ✅ **VPS Ready** - Configured for direct VPS deployment
4. ✅ **SSL Ready** - Cloudflare certificates configured
5. ✅ **Monitoring Ready** - Prometheus/Grafana setup included

## 📋 **Next Steps**

Run the deployment:
```bash
./deploy.sh
```

Choose option 2 for full deployment to your VPS at 217.79.255.54.