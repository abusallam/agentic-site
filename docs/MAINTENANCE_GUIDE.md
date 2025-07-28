# 🛠️ Maintenance and Governance Guide

## Project Organization Principles

This document outlines the maintenance guidelines and governance principles for the organized Agentic AI Platform codebase.

## 📁 Directory Structure Rules

### **Frontend Directory (`frontend/`)**
- **Purpose**: Next.js application and React components
- **Rules**:
  - All React components go in `components/`
  - Utility functions in `lib/`
  - Custom hooks in `hooks/`
  - Styles in `styles/`
  - Static assets in `public/`
  - Tests in `tests/`

### **Backend Directory (`backend/`)**
- **Purpose**: Python ADK agent system
- **Rules**:
  - Preserve existing `agent/` structure
  - Service integrations in `services/`
  - Tests in `tests/`
  - Use `pyproject.toml` for dependencies

### **Infrastructure Directory (`infrastructure/`)**
- **Purpose**: Deployment and operations
- **Rules**:
  - Docker configs in `docker/`
  - Deployment scripts in `scripts/`
  - Nginx configs in `nginx/`
  - SSL certificates in `ssl/`
  - Monitoring setup in `monitoring/`

### **Root Level Files**
- **Allowed**: Configuration files, documentation, workspace files
- **Not Allowed**: Application code, temporary files, build artifacts

## 🔧 Development Workflow

### **Adding New Features**

1. **Frontend Features**:
   ```bash
   cd frontend/
   # Add components to components/
   # Add utilities to lib/
   # Add hooks to hooks/
   # Update package.json if new dependencies
   ```

2. **Backend Features**:
   ```bash
   cd backend/
   # Add to agent/ structure
   # Add services to services/
   # Update pyproject.toml if new dependencies
   ```

3. **Infrastructure Changes**:
   ```bash
   cd infrastructure/
   # Update Docker configs in docker/
   # Update scripts in scripts/
   # Update monitoring in monitoring/
   ```

### **Testing Requirements**

- **Frontend**: Jest + Playwright tests in `frontend/tests/`
- **Backend**: pytest tests in `backend/tests/`
- **Integration**: E2E tests in root `tests/`

### **Code Quality Standards**

- **Frontend**: ESLint + Prettier (configured in `frontend/`)
- **Backend**: Black + Flake8 + mypy (configured in `backend/`)
- **Pre-commit**: Husky hooks for quality enforcement

## 📦 Dependency Management

### **Frontend Dependencies**
- **File**: `frontend/package.json`
- **Manager**: npm
- **Rules**: 
  - Keep dependencies minimal
  - Use exact versions for critical packages
  - Regular security updates

### **Backend Dependencies**
- **File**: `backend/pyproject.toml`
- **Manager**: uv (preferred) or pip
- **Rules**:
  - Use version ranges for flexibility
  - Separate dev dependencies
  - Regular security updates

### **Workspace Management**
- **File**: `package.json` (root)
- **Purpose**: Workspace scripts and dev dependencies
- **Rules**: Only workspace-level tools here

## 🚀 Deployment Process

### **Local Development**
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && python agent/main.py

# Full stack
npm run dev  # Uses workspace scripts
```

### **Production Deployment**
```bash
# Use organized deployment script
./infrastructure/scripts/deploy-organized.sh

# Or use Docker
cd infrastructure/docker
docker-compose -f docker-compose.production.yml up -d
```

## 🔍 Monitoring and Maintenance

### **Health Checks**
- **Frontend**: `http://localhost:3000/api/health`
- **Backend**: `http://localhost:8000/health`
- **Monitoring**: Prometheus + Grafana in `infrastructure/monitoring/`

### **Log Management**
- **Frontend**: Next.js logs
- **Backend**: Python logging
- **Infrastructure**: Docker logs + monitoring stack

### **Backup Strategy**
- **Code**: Git repository
- **Database**: Supabase backups
- **Configuration**: Environment variables backup

## 🚫 Anti-Patterns to Avoid

### **Directory Structure Violations**
- ❌ Don't put frontend code in root
- ❌ Don't mix frontend and backend code
- ❌ Don't put temporary files in version control
- ❌ Don't duplicate configuration files

### **Dependency Management Issues**
- ❌ Don't install frontend deps in backend
- ❌ Don't use different package managers inconsistently
- ❌ Don't commit lock files for both root and workspace

### **Code Organization Problems**
- ❌ Don't create deep nested directories unnecessarily
- ❌ Don't put business logic in components
- ❌ Don't mix test files with source code

## 🔧 Troubleshooting Common Issues

### **Build Failures**
1. **Frontend build fails**:
   ```bash
   cd frontend
   rm -rf node_modules .next
   npm install
   npm run build
   ```

2. **Backend import errors**:
   ```bash
   cd backend
   export PYTHONPATH=/app/agent
   python -m pytest
   ```

3. **Docker build issues**:
   ```bash
   cd infrastructure/docker
   docker-compose build --no-cache
   ```

### **Import Path Issues**
- Use `@/` aliases in frontend
- Use relative imports in backend
- Update `tsconfig.json` paths if needed

### **Environment Configuration**
- Check `.env.example` for required variables
- Ensure environment variables are properly set
- Use different configs for dev/staging/production

## 📋 Maintenance Checklist

### **Weekly**
- [ ] Update dependencies (security patches)
- [ ] Review monitoring alerts
- [ ] Check disk space and performance
- [ ] Review error logs

### **Monthly**
- [ ] Update all dependencies
- [ ] Review and update documentation
- [ ] Performance optimization review
- [ ] Security audit

### **Quarterly**
- [ ] Major dependency updates
- [ ] Architecture review
- [ ] Backup and recovery testing
- [ ] Team training on new features

## 🤝 Contributing Guidelines

### **Code Review Process**
1. Create feature branch
2. Make changes following structure rules
3. Run tests and quality checks
4. Submit pull request
5. Code review and approval
6. Merge to main

### **Quality Gates**
- All tests must pass
- Code coverage > 80%
- No linting errors
- Documentation updated
- Security scan passed

## 📞 Support and Escalation

### **Issues and Questions**
- **Technical Issues**: Create GitHub issue
- **Architecture Questions**: Team lead review
- **Security Concerns**: Immediate escalation

### **Emergency Procedures**
- **Production Down**: Use rollback procedures
- **Security Incident**: Follow security playbook
- **Data Loss**: Restore from backups

---

**Last Updated**: $(date)
**Maintained By**: consulting.sa team
**Review Schedule**: Quarterly