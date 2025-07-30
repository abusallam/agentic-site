# 🔄 Development Workflow Guide for AI Agents

## 🎯 Overview

This guide provides step-by-step instructions for AI agents working on the Agentic AI Platform. It covers the complete development lifecycle from initial setup to production deployment.

## 🚨 CRITICAL FIRST STEP: Environment Decision

**Before making ANY changes, you MUST ask the user:**

> **"Should I work on the development branch (safe testing at dev.consulting.sa) or production branch (live system at consulting.sa)?"**

### When to Use Each Environment

#### Development Branch (`develop`)
- ✅ **New features and enhancements**
- ✅ **Experimental changes**
- ✅ **Learning and exploration**
- ✅ **Testing integrations**
- ✅ **Safe to break and rebuild**

#### Production Branch (`main`)
- ⚠️ **Critical bug fixes only**
- ⚠️ **Emergency patches**
- ⚠️ **Hotfixes for live issues**
- ❌ **Never for experimental work**

## 🌟 Development Environment Workflow

### Step 1: Environment Setup

```bash
# Check current branch
git branch

# Switch to develop branch (if not already)
git checkout develop

# Pull latest changes
git pull origin develop

# Create feature branch (recommended)
git checkout -b feature/your-feature-name
```

### Step 2: Make Your Changes

#### Frontend Changes (Next.js)
```bash
# Navigate to frontend
cd frontend/

# Install dependencies (if needed)
npm install

# Start development server locally
npm run dev

# Make your changes in:
# - app/ (pages and layouts)
# - components/ (reusable components)
# - lib/ (utilities)
# - styles/ (CSS)
```

#### Backend Changes (Python ADK)
```bash
# Navigate to backend
cd backend/agent/

# Activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Make your changes in:
# - my_adk_agent/ (main agent code)
# - services/ (service integrations)
# - tools/ (ADK tools)
# - tests/ (test files)
```

### Step 3: Test Locally

#### Frontend Testing
```bash
cd frontend/

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test

# Build to check for errors
npm run build
```

#### Backend Testing
```bash
cd backend/agent/

# Run tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
pytest --cov=my_adk_agent
```

### Step 4: Deploy to Development Environment

```bash
# From project root
./infrastructure/scripts/deploy-dev-vps.sh
```

**This script will:**
1. Copy your code to VPS development directory
2. Build development containers
3. Start services on development ports
4. Configure nginx for dev.consulting.sa
5. Run health checks

### Step 5: Test in Development Environment

#### Access Points
- **🌐 Main Site**: https://dev.consulting.sa
- **🔧 API Endpoints**: https://dev.consulting.sa/api
- **📊 n8n Workflows**: https://dev.consulting.sa/n8n
- **🔍 Health Check**: https://dev.consulting.sa/api/health

#### Testing Checklist
- [ ] **Frontend loads correctly**
- [ ] **All pages render properly**
- [ ] **Chatbot functionality works**
- [ ] **API endpoints respond**
- [ ] **Database operations work**
- [ ] **Service integrations function**
- [ ] **No console errors**
- [ ] **Mobile responsiveness**

### Step 6: Monitor and Debug

#### Check Service Status
```bash
# SSH to VPS
ssh root@217.79.255.54

# Navigate to development directory
cd /opt/agentic-platform-dev

# Check status
./dev-manage.sh status

# View logs
./dev-manage.sh logs

# View specific service logs
./dev-manage.sh logs frontend-dev
./dev-manage.sh logs backend-dev
```

#### Common Debug Commands
```bash
# Restart services
./dev-manage.sh restart

# Rebuild containers (after code changes)
./dev-manage.sh rebuild

# Stop development environment
./dev-manage.sh stop

# Start development environment
./dev-manage.sh start
```

### Step 7: Commit and Push Changes

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add new chatbot feature

- Implement conversation memory
- Add user preference storage
- Update UI components
- Add comprehensive tests"

# Push to feature branch
git push origin feature/your-feature-name

# Or push to develop directly
git push origin develop
```

## 🚀 Production Deployment Workflow

### ⚠️ CRITICAL WARNING
**Only deploy to production after thorough testing in development!**

### Step 1: Validate Development Environment
- [ ] All tests pass
- [ ] No errors in logs
- [ ] All features work as expected
- [ ] Performance is acceptable
- [ ] Security checks pass

### Step 2: Merge to Main Branch
```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge develop branch
git merge develop

# Push to main
git push origin main
```

### Step 3: Deploy to Production
```bash
# Deploy to production
./infrastructure/scripts/deploy.sh
```

### Step 4: Post-Deployment Validation
- [ ] **Health checks pass**: https://consulting.sa/api/health
- [ ] **Frontend loads**: https://consulting.sa
- [ ] **API responds**: https://consulting.sa/api
- [ ] **No errors in logs**
- [ ] **All integrations work**

## 🛠️ Common Development Tasks

### Adding a New Frontend Component

1. **Create component file**
```typescript
// frontend/components/features/new-component.tsx
import React from 'react';

interface NewComponentProps {
  title: string;
  description?: string;
}

export function NewComponent({ title, description }: NewComponentProps) {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold">{title}</h3>
      {description && <p className="text-gray-600">{description}</p>}
    </div>
  );
}
```

2. **Add to page or layout**
```typescript
// frontend/app/page.tsx
import { NewComponent } from '@/components/features/new-component';

export default function HomePage() {
  return (
    <div>
      <NewComponent 
        title="Welcome" 
        description="This is a new component" 
      />
    </div>
  );
}
```

3. **Test and deploy to development**

### Adding a New Backend Service

1. **Create service file**
```python
# backend/agent/my_adk_agent/services/new_service.py
from typing import Dict, Any
import httpx
from .base_service import BaseService

class NewService(BaseService):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('NEW_SERVICE_API_KEY')
        self.base_url = config.get('NEW_SERVICE_URL')
    
    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/process",
                json=data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
```

2. **Register in agent**
```python
# backend/agent/my_adk_agent/agent.py
from .services.new_service import NewService

class MyAgent:
    def __init__(self):
        self.new_service = NewService(self.config)
    
    async def handle_request(self, request):
        result = await self.new_service.process_request(request.data)
        return result
```

3. **Add tests**
```python
# backend/agent/tests/test_new_service.py
import pytest
from my_adk_agent.services.new_service import NewService

@pytest.mark.asyncio
async def test_new_service_process_request():
    config = {"NEW_SERVICE_API_KEY": "test", "NEW_SERVICE_URL": "http://test"}
    service = NewService(config)
    
    # Mock the request
    result = await service.process_request({"test": "data"})
    
    assert result is not None
```

### Updating Environment Variables

1. **Add to .env file**
```bash
# New service configuration
NEW_SERVICE_API_KEY=your_api_key_here
NEW_SERVICE_URL=https://api.newservice.com
```

2. **Update Docker configuration**
```yaml
# infrastructure/docker/docker-compose.development.yml
environment:
  - NEW_SERVICE_API_KEY=${NEW_SERVICE_API_KEY}
  - NEW_SERVICE_URL=${NEW_SERVICE_URL}
```

3. **Redeploy to apply changes**

## 🔍 Troubleshooting Common Issues

### Frontend Build Errors

**Issue**: Next.js build fails
```bash
# Check for TypeScript errors
npm run type-check

# Check for linting errors
npm run lint

# Clear cache and rebuild
rm -rf .next
npm run build
```

### Backend Service Errors

**Issue**: Python service not starting
```bash
# Check Python environment
python --version
which python

# Check dependencies
uv pip list

# Check for import errors
python -c "import my_adk_agent"
```

### Docker Container Issues

**Issue**: Container won't start
```bash
# Check container logs
docker logs agentic-frontend-dev
docker logs agentic-backend-dev

# Rebuild containers
./dev-manage.sh rebuild

# Check resource usage
docker stats
```

### SSL/Network Issues

**Issue**: HTTPS not working
```bash
# Check nginx configuration
nginx -t

# Check SSL certificate
openssl x509 -in /path/to/cert.crt -text -noout

# Restart nginx
systemctl restart nginx
```

## 📊 Performance Monitoring

### Key Metrics to Monitor

#### Frontend Performance
- **Page Load Time**: < 3 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Cumulative Layout Shift**: < 0.1
- **Bundle Size**: Monitor with `npm run analyze`

#### Backend Performance
- **API Response Time**: < 100ms for simple requests
- **Memory Usage**: Monitor with `docker stats`
- **CPU Usage**: Should stay under 80%
- **Error Rate**: < 1% of requests

#### Infrastructure Performance
- **SSL Handshake**: < 100ms
- **DNS Resolution**: < 50ms
- **Database Queries**: < 50ms average
- **Cache Hit Rate**: > 90%

### Monitoring Commands
```bash
# Check system resources
htop
df -h
free -h

# Check service health
curl -f https://dev.consulting.sa/api/health
curl -f https://dev.consulting.sa:8001/health

# Monitor logs in real-time
./dev-manage.sh logs -f
```

## 🎯 Best Practices Summary

### Code Quality
- [ ] **Follow existing patterns** in the codebase
- [ ] **Add comprehensive tests** for new features
- [ ] **Use TypeScript** for type safety
- [ ] **Handle errors gracefully** with proper try-catch
- [ ] **Add meaningful comments** for complex logic

### Security
- [ ] **Never commit secrets** to version control
- [ ] **Validate all inputs** from users
- [ ] **Use environment variables** for configuration
- [ ] **Implement proper authentication** for protected routes
- [ ] **Follow HTTPS everywhere** principle

### Performance
- [ ] **Optimize images** and assets
- [ ] **Use caching** where appropriate
- [ ] **Minimize bundle sizes** for frontend
- [ ] **Use async/await** for backend operations
- [ ] **Monitor resource usage** regularly

### Documentation
- [ ] **Update documentation** when adding features
- [ ] **Add code comments** for complex logic
- [ ] **Document API changes** in appropriate files
- [ ] **Update README** files when needed
- [ ] **Keep changelog** updated

## 🎉 Success Checklist

Before considering any task complete:

- [ ] **Code works in development environment**
- [ ] **All tests pass**
- [ ] **No errors in logs**
- [ ] **Performance is acceptable**
- [ ] **Security best practices followed**
- [ ] **Documentation updated**
- [ ] **Changes committed and pushed**
- [ ] **Deployment successful**
- [ ] **Health checks pass**
- [ ] **User acceptance criteria met**

Remember: **Quality over speed, stability over features, security over convenience!**