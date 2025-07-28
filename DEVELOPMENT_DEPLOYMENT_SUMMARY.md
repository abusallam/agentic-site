# 🚀 Development Deployment Summary

## Overview

Your Agentic AI Platform now has a complete development environment setup that runs alongside production using the `dev.consulting.sa` subdomain with your wildcard SSL certificate.

## ✨ What's Been Created

### 📁 New Files Created

1. **`infrastructure/docker/docker-compose.development.yml`** - Development container orchestration
2. **`infrastructure/nginx/development.conf`** - Nginx config with SSL for dev subdomain
3. **`infrastructure/scripts/deploy-dev-vps.sh`** - Automated development deployment script
4. **`.env.development`** - Development environment template
5. **`docs/development/DEVELOPMENT_SETUP.md`** - Complete setup documentation

### 🌐 Subdomain Configuration

**Production:** `https://consulting.sa`
**Development:** `https://dev.consulting.sa` ✨

Both use your existing wildcard SSL certificate - no additional SSL setup needed!

## 🎯 Branch Strategy Recommendation

```bash
# 1. Create develop branch
git checkout -b develop
git push -u origin develop

# 2. For features
git checkout develop
git checkout -b feature/your-feature
# Make changes, commit, push
# Create PR to develop branch

# 3. For production releases
git checkout main
git merge develop  # After thorough testing
git push origin main
```

## 🚀 Quick Start Guide

### Step 1: Configure Environment
```bash
# Copy and edit development environment
cp .env.development .env.dev
# Edit .env.dev with your actual API keys and values
```

### Step 2: Deploy Development Environment
```bash
# Make script executable and deploy
chmod +x infrastructure/scripts/deploy-dev-vps.sh
./infrastructure/scripts/deploy-dev-vps.sh
```

### Step 3: Access Your Development Environment
- **🌐 Main Site:** https://dev.consulting.sa
- **🔧 API Endpoints:** https://dev.consulting.sa/api
- **📊 n8n Workflows:** https://dev.consulting.sa/n8n
- **🔍 Health Check:** https://dev.consulting.sa/api/health

## 🏗️ Architecture Overview

### Production vs Development

| Component | Production | Development |
|-----------|------------|-------------|
| **URL** | `https://consulting.sa` | `https://dev.consulting.sa` |
| **Directory** | `/opt/agentic-platform` | `/opt/agentic-platform-dev` |
| **Frontend** | Port 3000 | Port 3001 |
| **Backend** | Port 8000 | Port 8001 |
| **Redis** | Port 6379 | Port 6380 |
| **n8n** | Port 5678 | Port 5679 |
| **SSL** | Wildcard SSL | Same Wildcard SSL ✅ |
| **Environment** | Production | Development/Debug |
| **Stripe** | Live Keys | Test Keys |
| **Logging** | INFO | DEBUG |

### 🔒 Security Features

- ✅ **HTTPS Enabled** - Uses your wildcard SSL certificate
- ✅ **Isolated Environment** - Separate containers and databases
- ✅ **Test API Keys** - Safe testing with Stripe test mode
- ✅ **Debug Logging** - Enhanced logging for development
- ✅ **Port Isolation** - No conflicts with production

## 🛠️ Development Workflow

### Daily Development Process

1. **Make Changes Locally**
   ```bash
   git checkout develop
   # Make your changes
   git add .
   git commit -m "Your feature description"
   git push origin develop
   ```

2. **Deploy to Development**
   ```bash
   ./infrastructure/scripts/deploy-dev-vps.sh
   ```

3. **Test Online**
   - Visit https://dev.consulting.sa
   - Test all functionality
   - Check API endpoints
   - Verify integrations

4. **Monitor & Debug**
   ```bash
   # SSH to VPS and check status
   ssh root@YOUR_VPS_IP
   cd /opt/agentic-platform-dev
   ./dev-manage.sh status
   ./dev-manage.sh logs
   ```

### 📊 Management Commands

On your VPS, you can manage the development environment:

```bash
cd /opt/agentic-platform-dev

# Check status
./dev-manage.sh status

# View logs
./dev-manage.sh logs
./dev-manage.sh logs frontend-dev  # Specific service

# Restart services
./dev-manage.sh restart

# Rebuild containers (after code changes)
./dev-manage.sh rebuild

# Stop/Start development environment
./dev-manage.sh stop
./dev-manage.sh start
```

## 🎨 Benefits of This Setup

### ✅ Professional Development Environment
- **Clean URLs** - `https://dev.consulting.sa` instead of IP:port
- **SSL Security** - Full HTTPS with your wildcard certificate
- **Production Parity** - Same architecture as production
- **Easy Access** - Memorable subdomain for team testing

### ✅ Safe Testing
- **Isolated Environment** - Won't affect production
- **Test API Keys** - Safe Stripe testing
- **Debug Logging** - Enhanced troubleshooting
- **Separate Database** - Can use different Supabase project

### ✅ Efficient Workflow
- **One-Command Deployment** - Single script deploys everything
- **Hot Reloading** - Quick iteration cycles
- **Container Management** - Easy start/stop/rebuild
- **Comprehensive Logging** - Full visibility into issues

## 🔧 Environment Configuration

### Key Environment Variables for Development

```bash
# Core Development Settings
NODE_ENV=development
DEBUG=true
VERBOSE_LOGGING=true
ADK_LOG_LEVEL=DEBUG

# Development URLs (using wildcard SSL)
DEV_SITE_URL=https://dev.consulting.sa
DEV_ADMIN_URL=https://dev.consulting.sa/api
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://dev.consulting.sa/api

# SSL Configuration
FORCE_HTTPS=true

# Development Ports (to avoid production conflicts)
FRONTEND_DEV_PORT=3001
BACKEND_DEV_PORT=8001
REDIS_DEV_PORT=6380
N8N_DEV_PORT=5679

# Test API Keys (important for Stripe)
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_...
STRIPE_TEST_WEBHOOK_SECRET=whsec_test_...
```

## 🚦 Next Steps

### 1. Set Up Development Branch
```bash
git checkout -b develop
git push -u origin develop
```

### 2. Configure Environment
```bash
cp .env.development .env.dev
# Edit .env.dev with your actual values
```

### 3. Deploy Development Environment
```bash
./infrastructure/scripts/deploy-dev-vps.sh
```

### 4. Test Your Setup
- Visit https://dev.consulting.sa
- Test all major functionality
- Verify API endpoints work
- Check n8n workflows at https://dev.consulting.sa/n8n

### 5. Start Developing
- Make changes on `develop` branch
- Deploy to development for testing
- Merge to `main` only after thorough testing

## 🎉 Summary

You now have a **professional development environment** that:

- ✅ Uses your **wildcard SSL certificate** for `dev.consulting.sa`
- ✅ Runs **alongside production** without conflicts
- ✅ Provides **one-command deployment** to VPS
- ✅ Includes **comprehensive management tools**
- ✅ Supports **safe testing** with test API keys
- ✅ Enables **efficient development workflow**

This setup gives you the confidence to test changes online before deploying to production, while maintaining the same professional architecture and security standards as your production environment.

**Happy coding! 🚀**