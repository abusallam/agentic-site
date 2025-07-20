# 🚀 Coolify Deployment Guide - AI SaaS Platform

This guide will help you deploy the AI SaaS Platform to Coolify with proper health checks and random port support.

## 📋 Prerequisites

- Coolify instance running
- Git repository with your code
- Domain name configured (e.g., consulting.sa)
- Required environment variables

## 🏗️ Deployment Files

The following files have been created for Coolify deployment:

### Docker Files
- `Dockerfile.simple` - Optimized single-container deployment
- `Dockerfile.production` - Multi-stage production build
- `docker-compose.coolify.yml` - Coolify-specific compose file

### Scripts
- `scripts/start-production.sh` - Production startup script
- `scripts/health-check.sh` - Comprehensive health check
- `scripts/deploy-coolify.sh` - Deployment preparation script

### Configuration
- `coolify.json` - Coolify application configuration
- Enhanced health check at `/api/health`

## 🚀 Quick Deployment Steps

### 1. Prepare for Deployment

```bash
# Run the deployment preparation script
./scripts/deploy-coolify.sh

# Optional: Test build locally
./scripts/deploy-coolify.sh --test-build
```

### 2. Push to Git Repository

```bash
git add .
git commit -m "Deploy to Coolify with enhanced health checks"
git push origin main
```

### 3. Create Application in Coolify

1. **Login to Coolify Dashboard**
2. **Create New Application**
   - Click "New Resource" → "Application"
   - Select "Public Repository" or connect your Git provider
   - Enter repository URL: `https://github.com/your-username/your-repo`

3. **Configure Build Settings**
   - **Branch**: `main`
   - **Dockerfile**: `Dockerfile.simple`
   - **Build Command**: `npm run build` (optional, handled in Dockerfile)
   - **Start Command**: `./start.sh` (handled in Dockerfile)

### 4. Set Environment Variables

Go to the **Environment** tab and add these variables:

#### Required Variables
```env
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
HOSTNAME=0.0.0.0

# Supabase (Required)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# AI Services (Required)
GEMINI_API_KEY=your_gemini_api_key

# Contact
NEXT_PUBLIC_CONTACT_EMAIL=asim@consulting.sa
```

#### Optional Variables
```env
# OpenAI (Optional)
OPENAI_API_KEY=your_openai_key

# Stripe (Optional)
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_public
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Livekit (Optional)
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret

# n8n (Optional)
N8N_URL=https://n8n.consulting.sa
N8N_API_KEY=your_n8n_api_key

# Backend Port (Coolify will set this)
BACKEND_PORT=8080
```

### 5. Configure Domains

1. Go to **Domains** tab
2. Add your domains:
   - `consulting.sa`
   - `www.consulting.sa`
3. Enable **SSL/TLS**
4. Enable **Redirect HTTP to HTTPS**

### 6. Configure Health Check

Coolify will automatically detect the health check from the Dockerfile, but you can verify:

- **Health Check Path**: `/api/health`
- **Port**: `3000` (frontend port)
- **Interval**: `30s`
- **Timeout**: `15s`
- **Retries**: `3`
- **Start Period**: `60s`

### 7. Deploy

1. Click **Deploy** button
2. Monitor the build logs
3. Wait for deployment to complete (usually 3-5 minutes)

## 🔍 Health Check Details

The enhanced health check endpoint (`/api/health`) provides:

```json
{
  "status": "healthy",
  "timestamp": "2025-07-20T13:00:00.000Z",
  "service": "ai-saas-platform",
  "version": "2.0.0",
  "environment": "production",
  "uptime": 3600,
  "memory": {
    "rss": 150000000,
    "heapTotal": 100000000,
    "heapUsed": 80000000,
    "external": 5000000
  },
  "services": {
    "frontend": {
      "status": "healthy",
      "port": 3000
    },
    "backend": {
      "status": "healthy",
      "port": 8080
    }
  }
}
```

### Status Codes
- `200` - All services healthy
- `503` - One or more services degraded

## 🎯 Port Configuration

Coolify automatically assigns random ports. The application handles this through:

- **Frontend Port**: `${PORT}` (default: 3000)
- **Backend Port**: `${BACKEND_PORT}` (default: 8080)
- **Health Check**: Adapts to assigned ports

## 📊 Monitoring & Access Points

After deployment, access your application:

### Public URLs
- **Main Website**: `https://consulting.sa`
- **Health Check**: `https://consulting.sa/api/health`
- **Admin Dashboard**: `https://consulting.sa/admin/dashboard`
- **Customer Portal**: `https://consulting.sa/customer/dashboard`

### Admin Access
- **Password**: `admin123`
- **Features**: Agent monitoring, customer sessions, analytics

### Customer Access
- **Login**: Any email address
- **Features**: Personal agents, usage analytics, controls

## 🔧 Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs in Coolify
# Common fixes:
- Ensure all environment variables are set
- Check Dockerfile.simple syntax
- Verify package.json dependencies
```

#### 2. Health Check Failures
```bash
# Test health check locally
curl https://consulting.sa/api/health

# Check both services
curl https://consulting.sa/api/health | jq '.services'
```

#### 3. Backend Not Starting
```bash
# Check environment variables
- BACKEND_PORT should be set by Coolify
- Python dependencies should install correctly
- Check startup logs for Python errors
```

#### 4. Frontend Issues
```bash
# Common fixes:
- Clear Next.js cache: rm -rf .next
- Check environment variables (NEXT_PUBLIC_*)
- Verify build output in logs
```

### Debug Commands

```bash
# Check container logs
docker logs <container_id>

# Test health endpoints
curl -v http://localhost:3000/api/health
curl -v http://localhost:8080/api/health

# Check processes
ps aux | grep -E "(node|python)"

# Check ports
netstat -tlnp | grep -E "(3000|8080)"
```

## 🔄 Updates & Redeployment

### Automatic Deployment
- Push to `main` branch triggers automatic deployment
- Coolify monitors Git repository for changes

### Manual Deployment
1. Go to Coolify dashboard
2. Click **Deploy** button
3. Monitor build progress

### Rolling Updates
- Coolify supports zero-downtime deployments
- Health checks ensure service availability

## 📈 Performance & Scaling

### Resource Limits
- **Memory**: 2GB (configurable)
- **CPU**: 1.0 core (configurable)
- **Auto-scaling**: Available in Coolify Pro

### Optimization Tips
1. **Enable caching** for static assets
2. **Use CDN** for global distribution
3. **Monitor metrics** through Coolify dashboard
4. **Scale horizontally** for high traffic

## 🔐 Security

### Environment Variables
- All secrets stored securely in Coolify
- No sensitive data in code repository
- Environment-specific configurations

### SSL/TLS
- Automatic SSL certificate generation
- HTTPS redirect enabled
- Security headers configured

### Access Control
- Admin dashboard password protected
- Customer portal with email authentication
- API endpoints secured

## 📞 Support

If you encounter issues:

1. **Check Coolify logs** first
2. **Review health check** status
3. **Verify environment variables**
4. **Test locally** with Docker

For additional support:
- **Email**: asim@consulting.sa
- **Documentation**: This guide
- **Health Check**: `https://consulting.sa/api/health`

---

## 🎉 Deployment Complete!

Your AI SaaS Platform is now running on Coolify with:

✅ **Automatic health checks**  
✅ **Random port support**  
✅ **SSL/TLS encryption**  
✅ **Auto-deployment**  
✅ **Monitoring & logging**  
✅ **Scalable architecture**  

**Main URL**: https://consulting.sa  
**Admin Panel**: https://consulting.sa/admin/dashboard  
**Customer Portal**: https://consulting.sa/customer/dashboard  

Enjoy your production-ready AI SaaS platform! 🚀