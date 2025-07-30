# Deployment Lessons Learned - Development Environment

## 📋 **Overview**

This document captures all the errors encountered during development environment setup and the solutions that worked. This serves as a troubleshooting guide and best practices reference for future deployments.

---

## 🚨 **Major Issues Encountered & Solutions**

### **1. Container Name Conflicts**

**Problem:**
```bash
Error response from daemon: Conflict. The container name "/agentic-redis-dev" is already in use
```

**Root Cause:** Previous deployment attempts left containers running with the same names.

**Solution:**
- Created `cleanup-dev.sh` script to systematically remove all development containers
- Always run cleanup before fresh deployments
- Use `docker ps --filter name=agentic-*-dev` to check existing containers

**Best Practice:**
```bash
# Always clean up before deploying
./infrastructure/scripts/cleanup-dev.sh
# Then deploy services
./infrastructure/scripts/deploy-backend-dev.sh
```

### **2. File Structure Issues During SCP Transfer**

**Problem:**
```bash
scp: local "backend/agent/.venv/lib64" is not a regular file
scp: upload "backend/agent/.venv/lib64" to "/opt/agent-dev/agent/.venv/lib64" failed
```

**Root Cause:** 
- Virtual environment files contain symbolic links that can't be transferred via SCP
- Python cache files and compiled bytecode causing transfer issues
- Directory structure getting flattened during transfer

**Solutions Implemented:**
1. **Exclude problematic directories:**
   ```bash
   rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc'
   ```

2. **Copy files individually for critical components:**
   ```bash
   copy_to_vps "backend/agent/requirements.txt" "/opt/agent-dev/"
   copy_to_vps "backend/agent/api_server.py" "/opt/agent-dev/"
   copy_to_vps "backend/agent/my_adk_agent" "/opt/agent-dev/"
   ```

3. **Use temporary directories with cleanup:**
   ```bash
   TEMP_DIR=$(mktemp -d)
   # Process files
   rm -rf "$TEMP_DIR"
   ```

**Best Practice:** Never transfer virtual environments or cache directories to production servers.

### **3. Docker Build Context Issues**

**Problem:**
```bash
ERROR: failed to build: failed to solve: failed to compute cache key: 
failed to calculate checksum: "/requirements.txt": not found
```

**Root Cause:** 
- Files copied to wrong directory structure on VPS
- Docker build context not finding expected files
- Dockerfile expecting files in root but they were in subdirectories

**Solution:**
- Simplified file copying to maintain flat structure
- Updated Dockerfile to match actual file locations
- Added proper PYTHONPATH environment variable

**Working Dockerfile Pattern:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . .
# Set Python path
ENV PYTHONPATH=/app
```

### **4. Environment Variables Not Loading**

**Problem:**
```bash
time="2025-07-29T16:05:35Z" level=warning msg="The \"STRIPE_TEST_SECRET_KEY\" variable is not set. Defaulting to a blank string."
```

**Root Cause:** 
- Environment file not properly formatted
- Missing environment variables in .env.dev
- Docker compose not finding the environment file

**Solution:**
1. **Standardized .env.dev file with all required variables**
2. **Used `--env-file .env.dev` flag consistently**
3. **Added fallback values in deployment scripts**

**Best Practice:**
```bash
# Always specify env file explicitly
docker-compose --env-file .env.dev up -d
# Check environment variables are loaded
docker exec container_name env | grep API_KEY
```

### **5. Password Standardization Issues**

**Problem:** Multiple deployment scripts had different/outdated VPS passwords hardcoded.

**Root Cause:** Passwords scattered across multiple files without centralized management.

**Solution:**
- Updated all deployment scripts to use environment variables
- Standardized pattern: `VPS_PASSWORD=${VPS_PASSWORD:-"fallback_value"}`
- Updated all scripts with current password

**Best Practice:**
```bash
# In all deployment scripts
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}
```

---

## ✅ **Working Deployment Procedures**

### **Step-by-Step Development Deployment**

1. **Clean Environment:**
   ```bash
   ./infrastructure/scripts/cleanup-dev.sh
   ```

2. **Deploy Static Base:**
   ```bash
   ./infrastructure/scripts/deploy-dev-static.sh
   ```

3. **Deploy Backend Services:**
   ```bash
   ./infrastructure/scripts/deploy-backend-dev.sh
   ```

4. **Deploy Python Agent:**
   ```bash
   ./infrastructure/scripts/deploy-agent-dev.sh
   ```

5. **Deploy Frontend (Next.js):**
   ```bash
   ./infrastructure/scripts/deploy-frontend-dev.sh
   ```

6. **Update Documentation:**
   ```bash
   ./infrastructure/scripts/update-server-docs.sh
   ```

### **Health Check Procedures**

**Check All Services:**
```bash
# Development site
curl -k https://dev.consulting.sa/health

# Backend agent
curl -k https://dev.consulting.sa/backend/health

# Direct container access
curl http://217.79.255.54:8001/health  # Agent
curl http://217.79.255.54:5679/        # n8n
curl http://217.79.255.54:6380/        # Redis (use redis-cli)
```

**Check Container Status:**
```bash
# All development containers
docker ps --filter name=agentic-*-dev

# Container logs
docker logs --tail 20 agentic-agent-dev
docker logs --tail 20 agentic-redis-dev
docker logs --tail 20 agentic-n8n-dev
```

---

## 🛠️ **Best Practices Established**

### **1. Environment Management**
- ✅ Use separate .env files for different environments (.env, .env.dev)
- ✅ Always specify environment files explicitly in Docker commands
- ✅ Include fallback values in deployment scripts
- ✅ Never commit real credentials to version control

### **2. Container Management**
- ✅ Use consistent naming patterns (agentic-service-env)
- ✅ Always clean up before fresh deployments
- ✅ Use different ports for different environments (3000 vs 3001, 8000 vs 8001)
- ✅ Include health checks in all containers

### **3. File Transfer**
- ✅ Exclude virtual environments and cache directories
- ✅ Use rsync with exclusion patterns for complex transfers
- ✅ Copy critical files individually when needed
- ✅ Use temporary directories with proper cleanup

### **4. Docker Best Practices**
- ✅ Multi-stage builds for optimization
- ✅ Copy requirements.txt first for better caching
- ✅ Set proper PYTHONPATH and environment variables
- ✅ Include health checks in Dockerfiles
- ✅ Use specific base image versions

### **5. Deployment Scripts**
- ✅ Make all scripts executable with proper permissions
- ✅ Include comprehensive error handling
- ✅ Use consistent color coding for output
- ✅ Test VPS connection before proceeding
- ✅ Update documentation automatically after deployments

### **6. Documentation**
- ✅ Maintain real-time server status documentation
- ✅ Document all container ports and purposes
- ✅ Keep deployment history and lessons learned
- ✅ Include troubleshooting commands and procedures

---

## 🔧 **Troubleshooting Commands**

### **Common Issues**

**Container won't start:**
```bash
docker logs --tail 50 container_name
docker inspect container_name
```

**Port conflicts:**
```bash
netstat -tulpn | grep :8001
lsof -i :8001
```

**Environment variables not loading:**
```bash
docker exec container_name env
docker exec container_name cat /opt/path/.env
```

**File permission issues:**
```bash
ls -la /opt/agent-dev/
chown -R www-data:www-data /var/www/dev-consulting
```

**Nginx configuration issues:**
```bash
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
```

### **Quick Fixes**

**Reset development environment:**
```bash
./infrastructure/scripts/cleanup-dev.sh
./infrastructure/scripts/deploy-dev-static.sh
./infrastructure/scripts/deploy-backend-dev.sh
./infrastructure/scripts/deploy-agent-dev.sh
```

**Check all services:**
```bash
./infrastructure/scripts/update-server-docs.sh
cat docs/infrastructure/VPS_SERVER_STATUS.md
```

---

## 📊 **Success Metrics**

### **Working Development Environment Checklist**
- ✅ Static development site accessible: https://dev.consulting.sa
- ✅ Backend agent healthy: https://dev.consulting.sa/backend/health
- ✅ All containers running without restarts
- ✅ Environment variables properly loaded
- ✅ SSL certificates working
- ✅ Nginx proxy configuration correct
- ✅ Health checks passing
- ✅ Documentation automatically updated

### **Performance Indicators**
- **Container Build Time:** ~2-3 minutes for agent
- **Service Startup Time:** ~30 seconds for full stack
- **Health Check Response:** < 1 second
- **SSL Certificate:** Valid wildcard for *.consulting.sa

---

## 🎯 **Next Steps**

1. **Complete Frontend Deployment:** Deploy Next.js to complete full-stack environment
2. **Functionality Testing:** Compare development vs production features
3. **CI/CD Pipeline:** Implement remaining automation tasks
4. **Monitoring Setup:** Add comprehensive monitoring and alerting
5. **Security Hardening:** Implement additional security measures

---

**Document Version:** 1.0  
**Last Updated:** 2025-07-29  
**Status:** ✅ Development Environment Successfully Deployed  
**Next Review:** After frontend deployment completion