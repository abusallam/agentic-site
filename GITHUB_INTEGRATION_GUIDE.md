# 🚀 GitHub Integration Guide - Development Branch Deployment

## 📋 Overview

This guide will help you set up complete GitHub integration for your development branch (`develop`) to automatically deploy to `dev.consulting.sa` when you push changes.

## 🎯 What We've Set Up

### ✅ **New Files Created:**
1. **`.github/workflows/cd-development.yml`** - Development deployment workflow
2. **`infrastructure/docker/docker-compose.development.yml`** - Development Docker Compose
3. **`infrastructure/nginx/development.conf`** - Development nginx configuration
4. **`frontend/public/index.html`** - Static frontend for development

### ✅ **Workflow Features:**
- **Automatic Deployment**: Triggers on push to `develop` branch
- **Alternative Frontend**: Uses nginx-based frontend to avoid Next.js build issues
- **Backend Deployment**: Full backend container deployment
- **Health Checks**: Comprehensive deployment validation
- **Slack Notifications**: Deployment status notifications

## 🔧 **Step 1: Configure GitHub Secrets**

You need to add these secrets to your GitHub repository:

### **Required Secrets:**
```bash
# Development VPS Access
DEV_HOST=217.79.255.54
DEV_USER=your_vps_username
DEV_SSH_KEY=your_private_ssh_key

# Development Environment Variables
DEV_SUPABASE_URL=your_dev_supabase_url
DEV_SUPABASE_ANON_KEY=your_dev_supabase_anon_key
DEV_DATABASE_URL=your_dev_database_url
DEV_N8N_URL=http://dev.consulting.sa/n8n/
DEV_MCP_SERVER_URL=http://dev.consulting.sa/api/

# Shared Secrets (can be same as production)
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_token
SLACK_WEBHOOK=your_slack_webhook_url
```

### **How to Add Secrets:**
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name above

## 🔧 **Step 2: Push Current Code to Develop Branch**

```bash
# Make sure you're on the develop branch
git checkout develop

# Add all the new files
git add .

# Commit the changes
git commit -m "feat: Add GitHub integration for development deployment

- Add development deployment workflow
- Create development Docker Compose configuration
- Add nginx configuration for development
- Create static frontend for development environment
- Fix frontend container build issues with nginx approach"

# Push to trigger the deployment
git push origin develop
```

## 🔧 **Step 3: Verify Deployment**

### **Check GitHub Actions:**
1. Go to your GitHub repository
2. Click **Actions** tab
3. Look for the "Deploy to Development" workflow
4. Monitor the deployment progress

### **Check VPS Deployment:**
```bash
# SSH into your VPS
ssh your_username@217.79.255.54

# Check if containers are running
docker ps

# Check development environment
cd /opt/agentic-development
docker-compose -f docker-compose.development.yml ps

# Check logs if needed
docker-compose -f docker-compose.development.yml logs frontend
docker-compose -f docker-compose.development.yml logs backend
```

### **Test the Development Environment:**
- **Frontend**: https://dev.consulting.sa
- **Backend API**: https://dev.consulting.sa/api/health
- **n8n Workflows**: https://dev.consulting.sa/n8n/

## 🔧 **Step 4: Development Workflow**

### **Daily Development Process:**
```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Test locally
cd frontend && npm run dev
cd backend/agent && uv run python main.py

# 4. Commit and push feature branch
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name

# 5. Create Pull Request to develop branch
# Go to GitHub and create PR: feature/your-feature-name → develop

# 6. After PR is merged, develop branch will auto-deploy
```

### **Production Deployment:**
```bash
# When ready for production
git checkout main
git merge develop
git push origin main
# This triggers production deployment
```

## 🔧 **Step 5: Troubleshooting**

### **Common Issues:**

#### **1. Frontend Build Fails**
- **Solution**: The new workflow uses nginx-based frontend to avoid Next.js build issues
- **Check**: Look at the workflow logs for the "Build frontend locally" step

#### **2. Backend Health Check Fails**
- **Solution**: Check backend logs and environment variables
- **Command**: `docker-compose -f docker-compose.development.yml logs backend`

#### **3. SSL Certificate Issues**
- **Solution**: Ensure SSL certificates are properly mounted
- **Check**: Verify `/etc/nginx/ssl/` directory exists on VPS

#### **4. GitHub Secrets Missing**
- **Solution**: Add all required secrets to GitHub repository
- **Check**: Go to Settings → Secrets and variables → Actions

### **Manual Deployment (if needed):**
```bash
# SSH into VPS
ssh your_username@217.79.255.54

# Navigate to development directory
cd /opt/agentic-development

# Pull latest images
docker-compose -f docker-compose.development.yml pull

# Restart services
docker-compose -f docker-compose.development.yml up -d --remove-orphans

# Check status
docker-compose -f docker-compose.development.yml ps
```

## 🔧 **Step 6: Monitoring and Maintenance**

### **Health Monitoring:**
```bash
# Check all services
curl https://dev.consulting.sa/api/health
curl https://dev.consulting.sa/n8n/

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### **Log Monitoring:**
```bash
# View real-time logs
docker-compose -f docker-compose.development.yml logs -f

# View specific service logs
docker-compose -f docker-compose.development.yml logs -f backend
docker-compose -f docker-compose.development.yml logs -f frontend
```

### **Resource Monitoring:**
```bash
# Check resource usage
docker stats

# Check disk space
df -h

# Check memory usage
free -h
```

## 🎉 **Success Indicators**

### **✅ Deployment Successful When:**
- GitHub Actions workflow completes without errors
- All containers are running: `docker ps` shows all services
- Health checks pass: `curl https://dev.consulting.sa/api/health` returns 200
- Frontend loads: https://dev.consulting.sa shows the development page
- n8n accessible: https://dev.consulting.sa/n8n/ loads properly

### **✅ Development Environment Ready When:**
- You can push to `develop` branch and see automatic deployment
- Backend APIs are fully functional
- Frontend serves static content (temporary solution)
- All services are healthy and monitored

## 🔄 **Next Steps**

### **Immediate:**
1. ✅ Configure GitHub secrets
2. ✅ Push current code to develop branch
3. ✅ Verify deployment works
4. ✅ Test development workflow

### **Future Improvements:**
1. **Fix Next.js Container**: Resolve the Next.js 15.4.4 container build issue
2. **Full Frontend**: Deploy the complete Next.js frontend when fixed
3. **Testing**: Add automated testing to the deployment pipeline
4. **Monitoring**: Enhance monitoring and alerting
5. **Backup**: Implement automated backups for development data

## 📞 **Support**

If you encounter any issues:
1. Check the GitHub Actions logs first
2. Review the troubleshooting section above
3. Check VPS logs and container status
4. Verify all secrets are properly configured

---

**Status**: 🟡 **Ready for Implementation**  
**Next Action**: Configure GitHub secrets and push to develop branch  
**Expected Result**: Automatic deployment to dev.consulting.sa 