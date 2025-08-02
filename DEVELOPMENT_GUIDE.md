# 🛠️ Development Guide - Agentic Platform

## 📋 **Quick Start**

### **Prerequisites**
- Git access to private repository: `abusallam/agentic-site`
- SSH access to VPS: `217.79.255.54`
- Docker and docker-compose installed locally (for local development)

### **Development Workflow**
```bash
# 1. Clone and setup
git clone https://github.com/abusallam/agentic-site.git
cd agentic-site
git checkout develop

# 2. Make your changes
# Edit files, add features, fix bugs

# 3. Deploy to development
git add .
git commit -m "feat: your feature description"
git push origin develop

# 4. Automatic deployment to https://dev.consulting.sa
# GitHub Actions will handle the deployment automatically
```

---

## 🏗️ **Project Structure**

```
agentic-site/
├── 📁 frontend/                    # Next.js Frontend Application
│   ├── app/                        # Next.js App Router
│   ├── components/                 # React Components
│   │   ├── ui/                     # shadcn/ui + Enhanced Components
│   │   ├── layout/                 # Layout Components
│   │   └── features/               # Feature-specific Components
│   ├── lib/                        # Utilities and Configurations
│   └── styles/                     # Global Styles and Animations
│
├── 📁 backend/                     # Python Backend (ADK Agent)
│   ├── agent/                      # Main Agent Code
│   │   ├── my_adk_agent/          # ADK Agent Implementation
│   │   ├── services/              # Service Integrations
│   │   ├── tools/                 # Agent Tools
│   │   └── tests/                 # Backend Tests
│   └── requirements.txt           # Python Dependencies
│
├── 📁 infrastructure/             # Infrastructure & Deployment
│   ├── docker/                    # Docker Configurations
│   ├── nginx/                     # Nginx Configurations
│   └── scripts/                   # Deployment Scripts
│
├── 📁 .github/workflows/          # CI/CD Pipelines
├── 📁 .kiro/                      # Kiro IDE Configurations
└── 📄 Documentation Files
```

---

## 🚀 **Deployment Process**

### **Automatic Deployment (Recommended)**
```bash
# Push to develop branch triggers automatic deployment
git push origin develop
```

**What happens automatically:**
1. 🔍 **Server Status Check**: Analyzes running containers and ports
2. 🧹 **Cleanup**: Removes conflicting containers and resources
3. 🏗️ **Build**: Creates Docker images for frontend and backend
4. 🚀 **Deploy**: Starts containers with correct configuration
5. ⚙️ **Configure**: Updates nginx with auto-detected ports
6. ✅ **Verify**: Tests all services and connections

### **Manual Deployment (For Debugging)**
```bash
# Comprehensive deployment with full status check
bash infrastructure/scripts/comprehensive-dev-deployment.sh

# Server cleanup only
bash infrastructure/scripts/check-and-cleanup-server.sh

# Test deployment without changes
bash infrastructure/scripts/test-dev-deployment.sh
```

---

## 🎨 **Frontend Development**

### **Technology Stack**
- **Framework**: Next.js 15.4.5 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Components**: Enhanced UI components available

### **Enhanced Components Usage**
```typescript
// Enhanced Button with loading state
import { Button } from "@/components/ui/enhanced-button"

<Button variant="gradient" loading={isLoading} icon={<Icon />}>
  Save Changes
</Button>

// Enhanced Card with animations
import { EnhancedCard } from "@/components/ui/enhanced-card"

<EnhancedCard 
  variant="glass" 
  animation="float"
  icon={<Icon />}
  title="Feature Title"
  description="Feature description"
>
  Card content
</EnhancedCard>

// Loading states
import { LoadingSpinner, PageLoading } from "@/components/ui/enhanced-loading"

<LoadingSpinner variant="ring" size="lg" />
<PageLoading message="Loading..." showProgress progress={75} />
```

### **Development Commands**
```bash
# Frontend development (local)
cd frontend
npm install
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run type-check   # TypeScript checking
```

---

## 🐍 **Backend Development**

### **Technology Stack**
- **Framework**: Google ADK (Agent Development Kit)
- **Language**: Python 3.11
- **API**: FastAPI with uvicorn
- **Database**: Supabase (PostgreSQL)
- **AI Services**: Google Gemini, OpenAI, Anthropic

### **Agent Architecture**
```python
# Main Agent Structure
backend/agent/my_adk_agent/
├── agent.py                    # Main agent class
├── services/                   # Service integrations
│   ├── auth_service.py        # Authentication
│   ├── supabase_service.py    # Database operations
│   ├── mcp_service.py         # MCP integration
│   └── livekit_service.py     # Real-time communication
├── tools/                     # Agent tools
└── tests/                     # Agent tests
```

### **Development Commands**
```bash
# Backend development (local)
cd backend
uv sync                    # Install dependencies
uv run python agent/main.py   # Start development server
uv run pytest tests/      # Run tests
```

### **Adding New Agent Features**
1. **Create Service**: Add new service in `backend/agent/my_adk_agent/services/`
2. **Create Tool**: Add agent tool in `backend/agent/my_adk_agent/tools/`
3. **Update Agent**: Integrate in `backend/agent/my_adk_agent/agent.py`
4. **Add Tests**: Create tests in `backend/agent/tests/`

---

## 🔧 **Infrastructure Management**

### **Container Management**
```bash
# Check container status
docker ps | grep agentic

# Development containers (should be running)
agentic-frontend-development    # Port 3002
agentic-agent-dev              # Port 8001  
agentic-redis-dev              # Port 6380
agentic-n8n-dev                # Port 5679

# Production containers (separate)
agentic-frontend-prod          # Port 3000
agentic-backend-prod           # Port 8000
agentic-redis-prod             # Port 6379
agentic-n8n-monitoring         # Port 5678
```

### **Nginx Configuration**
- **Development**: Auto-generated based on detected container ports
- **Location**: `/etc/nginx/sites-enabled/agentic-platform-dev`
- **SSL**: Wildcard certificate for `*.consulting.sa`

### **Environment Variables**
```bash
# Development environment
.env.dev                       # Development configuration
NEXT_PUBLIC_SUPABASE_URL      # Supabase URL
GEMINI_API_KEY                # AI service keys
N8N_URL                       # Workflow automation
# ... (see .env.example for full list)
```

---

## 🧪 **Testing & Quality Assurance**

### **Testing Strategy**
```bash
# Frontend testing
cd frontend
npm run test           # Jest tests
npm run test:e2e       # Playwright E2E tests
npm run lint           # Code linting

# Backend testing  
cd backend
uv run pytest tests/  # Python tests
uv run pytest tests/integration/  # Integration tests
```

### **Quality Checks**
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **Python**: Flake8 linting and type hints

---

## 📊 **Monitoring & Debugging**

### **Health Checks**
```bash
# Check service health
curl https://dev.consulting.sa/health        # Backend health
curl https://dev.consulting.sa/              # Frontend health
curl https://dev.consulting.sa/n8n/          # n8n health

# Direct container access (for debugging)
curl http://217.79.255.54:3002/              # Frontend direct
curl http://217.79.255.54:8001/health        # Backend direct
```

### **Log Access**
```bash
# Container logs
docker logs agentic-frontend-development
docker logs agentic-agent-dev
docker logs agentic-n8n-dev
docker logs agentic-redis-dev

# Nginx logs
tail -f /var/log/nginx/dev.consulting.sa.access.log
tail -f /var/log/nginx/dev.consulting.sa.error.log
```

### **Debugging Tools**
- **ADK Web UI**: Built-in agent debugging interface
- **Browser DevTools**: Frontend debugging
- **Docker Logs**: Container-level debugging
- **Nginx Logs**: Proxy and routing issues

---

## 🔄 **Dependency Management**

### **Frontend Dependencies**
```bash
cd frontend
npm update                    # Update all packages
npm audit                     # Security audit
npm audit fix                 # Fix security issues
```

### **Backend Dependencies**
```bash
cd backend
uv sync                       # Sync dependencies
uv add package-name          # Add new package
uv remove package-name       # Remove package
```

### **System Dependencies**
```bash
# Update deployment scripts
bash infrastructure/scripts/comprehensive-dev-deployment.sh

# Update Docker images
docker-compose pull          # Pull latest images
docker system prune -f       # Clean up unused resources
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"Port already in use"**
```bash
# Run comprehensive cleanup
bash infrastructure/scripts/check-and-cleanup-server.sh
```

#### **"Container won't start"**
```bash
# Check container logs
docker logs container-name

# Check system resources
docker system df
free -h
```

#### **"Nginx 502 Bad Gateway"**
```bash
# Check if containers are running
docker ps | grep agentic

# Test direct container access
curl http://localhost:3002/    # Frontend
curl http://localhost:8001/health  # Backend

# Check nginx configuration
nginx -t
```

#### **"GitHub Actions failing"**
1. Check GitHub Actions logs in repository
2. Verify GitHub Secrets are set correctly
3. Ensure VPS is accessible
4. Check container registry permissions

### **Emergency Procedures**
```bash
# Complete environment reset
bash infrastructure/scripts/check-and-cleanup-server.sh

# Rollback to last working state
git checkout last-working-commit
git push origin develop --force

# Manual container restart
docker-compose -f infrastructure/docker/docker-compose.development.yml restart
```

---

## 📝 **Development Best Practices**

### **Code Standards**
- **Commit Messages**: Use conventional commits (feat:, fix:, docs:, etc.)
- **Branch Strategy**: Use `develop` for development, `main` for production
- **Code Review**: Review changes before merging to main
- **Testing**: Write tests for new features

### **Security Practices**
- **Environment Variables**: Never commit secrets to repository
- **Dependencies**: Regularly update and audit dependencies
- **Access Control**: Use proper authentication and authorization
- **SSL/HTTPS**: Always use HTTPS in production and development

### **Performance Optimization**
- **Frontend**: Optimize images, use lazy loading, minimize bundle size
- **Backend**: Use caching, optimize database queries, monitor response times
- **Infrastructure**: Monitor resource usage, optimize container configurations

---

## 🎯 **Next Steps**

### **Immediate Tasks**
1. **UI Improvements**: Implement enhanced components across the application
2. **Backend Features**: Add new agent capabilities and integrations
3. **Documentation**: Complete API documentation and component library docs
4. **Testing**: Expand test coverage for both frontend and backend

### **Future Enhancements**
1. **Performance Monitoring**: Implement comprehensive monitoring
2. **Security Hardening**: Regular security audits and improvements
3. **Scalability**: Prepare for production scaling
4. **Feature Expansion**: Add new AI capabilities and integrations

---

**📞 Need Help?**
- Check the troubleshooting section above
- Review container logs for specific errors
- Run the comprehensive deployment script for automatic fixes
- Consult the project status document for current system state