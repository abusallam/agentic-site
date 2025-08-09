# 🚀 Quick Deployment Guide - Environment Variables

This guide shows you how to deploy to any VPS using environment variables for easy server switching.

## 🎯 Current VPS Configuration

**Active Development Server:**
- **IP**: 217.79.255.54
- **Username**: root
- **Password**: gnqLG7FDd4
- **Environment**: development
- **Domain**: dev.consulting.sa

## 🚀 Quick Start (Recommended Method)

### Option 1: One-Command Deployment with Environment Variables

```bash
# Load environment and deploy to development
source infrastructure/config/vps-environments.env
./infrastructure/scripts/deploy-with-env.sh dev
```

**What this does:**
- ✅ Loads VPS configurations from environment file
- ✅ Switches to development environment
- ✅ Sets up VPS if needed (first time)
- ✅ Deploys complete application stack
- ✅ Tests all endpoints and provides access URLs

### Option 2: Manual Step-by-Step

```bash
# 1. Test VPS connection first
./infrastructure/scripts/test-vps-connection.sh

# 2. Set up fresh VPS (first time only)
./infrastructure/scripts/setup-fresh-vps.sh 217.79.255.54 gnqLG7FDd4 development

# 3. Deploy application
./infrastructure/scripts/deploy-to-clean-vps.sh agentic-217-79-255-54-development development
```

## 🔄 Environment Switching

### Load Environment Configuration
```bash
# Load all VPS configurations
source infrastructure/config/vps-environments.env
```

### Switch Between Environments
```bash
# Switch to development
switch_to_dev

# Switch to production (when ready)
switch_to_prod

# Switch to staging (future)
switch_to_staging

# Show current environment
show_current_env
```

### Deploy to Current Environment
```bash
# Deploy using current environment variables
./infrastructure/scripts/deploy-with-env.sh

# Or specify environment directly
./infrastructure/scripts/deploy-with-env.sh dev      # Development
./infrastructure/scripts/deploy-with-env.sh prod     # Production
./infrastructure/scripts/deploy-with-env.sh staging  # Staging
```

## 🌐 Access Your Application

After successful deployment:

### Development Environment
- **Website**: https://dev.consulting.sa/
- **API Health**: https://dev.consulting.sa/health
- **Backend Admin**: https://dev.consulting.sa/backend/
- **n8n Workflow**: https://dev.consulting.sa/n8n/
- **API Docs**: https://dev.consulting.sa/backend/docs

### Direct Access (for debugging)
- **Frontend**: http://217.79.255.54:3001/
- **Backend**: http://217.79.255.54:8001/
- **n8n**: http://217.79.255.54:5679/
- **Redis**: 217.79.255.54:6380

## 🛠️ Management Commands

```bash
# Check system status
ssh agentic-217-79-255-54-development '/usr/local/bin/agentic-development-status.sh'

# View application logs
ssh agentic-217-79-255-54-development '/usr/local/bin/agentic-development-logs.sh'

# Restart all services
ssh agentic-217-79-255-54-development '/usr/local/bin/agentic-development-restart.sh'

# Create backup
ssh agentic-217-79-255-54-development '/usr/local/bin/agentic-development-backup.sh'

# Direct SSH access
ssh agentic-217-79-255-54-development
```

## 🔧 Adding New VPS Servers

To add a new VPS server, edit `infrastructure/config/vps-environments.env`:

```bash
# Add new server configuration
export NEW_VPS_IP="192.168.1.200"
export NEW_VPS_USER="root"
export NEW_VPS_PASSWORD="new_password"
export NEW_VPS_ENVIRONMENT="staging"
export NEW_VPS_DOMAIN="staging.consulting.sa"

# Add switching function
switch_to_new() {
    export VPS_IP="192.168.1.200"
    export VPS_USER="root"
    export VPS_PASSWORD="new_password"
    export VPS_ENVIRONMENT="staging"
    export VPS_DOMAIN="staging.consulting.sa"
    export SSH_ALIAS="agentic-new-staging"
    echo "✅ Switched to NEW STAGING environment"
}
```

Then deploy:
```bash
source infrastructure/config/vps-environments.env
switch_to_new
./infrastructure/scripts/deploy-with-env.sh
```

## 🚨 Troubleshooting

### Connection Issues
```bash
# Test VPS connection
./infrastructure/scripts/test-vps-connection.sh

# Check current environment
source infrastructure/config/vps-environments.env
show_current_env
```

### Deployment Issues
```bash
# Check container status
ssh $SSH_ALIAS 'cd /opt/docker-apps/$VPS_ENVIRONMENT/agentic-site && docker-compose ps'

# View logs
ssh $SSH_ALIAS '/usr/local/bin/agentic-$VPS_ENVIRONMENT-logs.sh'

# Restart services
ssh $SSH_ALIAS '/usr/local/bin/agentic-$VPS_ENVIRONMENT-restart.sh'
```

### Reset and Redeploy
```bash
# If something goes wrong, you can always reset and redeploy
source infrastructure/config/vps-environments.env
./infrastructure/scripts/setup-fresh-vps.sh $VPS_IP $VPS_PASSWORD $VPS_ENVIRONMENT
./infrastructure/scripts/deploy-to-clean-vps.sh $SSH_ALIAS $VPS_ENVIRONMENT
```

## 📊 What Gets Deployed

### Frontend (Next.js)
- ✅ All your UI fixes (logo size, navigation, pages)
- ✅ Services, consulting, about, contact pages
- ✅ Improved chatbot with better sizing
- ✅ Responsive design with proper CSS

### Backend (FastAPI)
- ✅ Health check endpoints
- ✅ Chat API for chatbot
- ✅ Admin interface
- ✅ API documentation

### Infrastructure
- ✅ Redis for caching
- ✅ n8n for workflow automation
- ✅ Nginx reverse proxy with security
- ✅ SSL-ready configuration
- ✅ Monitoring and health checks

### Security
- ✅ SSH key authentication
- ✅ Firewall configuration
- ✅ Fail2ban protection
- ✅ Security headers
- ✅ Rate limiting

## 🎯 Next Steps

1. **Test the deployment**: Visit https://dev.consulting.sa/
2. **Configure DNS**: Point your domain to 217.79.255.54
3. **Add SSL certificate**: Set up Let's Encrypt or upload certificates
4. **Configure API keys**: Update environment variables with real API keys
5. **Set up monitoring**: Configure additional monitoring if needed

---

**🔐 SECURITY NOTE**: All credentials are stored in the private repository. The environment variable system makes it easy to switch between servers while keeping everything secure and documented.