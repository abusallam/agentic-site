# 🚀 Professional Deployment Guide - consulting.sa

## Overview

This guide establishes the **correct professional workflow** using GitHub-based deployment with automated CI/CD, proper environment management, and comprehensive monitoring. No more manual file copying!

## The Right Architecture

```
Local Development
    ↓ (git push)
GitHub Repository (Private)
    ↓ (webhook)
VPS Deployment System
    ↓ (automated)
Production/Development Environments
```

## 🎯 What We Fixed

### ❌ Old (Wrong) Process
- Manual file copying from local to VPS
- No version control integration
- Manual container management
- Inconsistent environments
- No automated backups
- No proper monitoring

### ✅ New (Professional) Process
- GitHub-based deployment with webhooks
- Automated CI/CD pipeline
- Environment-specific configurations
- Automated backups before deployment
- Comprehensive health monitoring
- Professional logging and error handling

## 🚀 Quick Setup

### 1. Run the Setup Script
```bash
chmod +x infrastructure/scripts/setup-github-integration.sh
./infrastructure/scripts/setup-github-integration.sh
```

### 2. Update Configuration Files
After running the setup script, update these files on the VPS:

#### Repository URLs
```bash
# SSH to VPS
ssh root@217.79.255.54

# Update production deployment script
nano /opt/deployments/scripts/deploy-production.sh
# Change: REPO_URL="https://github.com/your-username/your-private-repo.git"

# Update development deployment script
nano /opt/deployments/scripts/deploy-development.sh
# Change: REPO_URL="https://github.com/your-username/your-private-repo.git"
```

#### Environment Variables
```bash
# Update production environment
nano /opt/deployments/configs/production.env
# Add your actual API keys, database URLs, etc.

# Update development environment
nano /opt/deployments/configs/development.env
# Add your actual API keys, database URLs, etc.
```

### 3. Configure GitHub Webhook
1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Payload URL: `https://www.consulting.sa/webhook`
4. Content type: `application/json`
5. Events: `Push events`
6. Secret: Use the webhook secret from your environment config

## 🔧 Professional Workflow

### Development Process
1. **Make changes locally**
2. **Test locally**: `npm run dev`
3. **Commit and push to `development` branch**
4. **Automatic deployment to https://dev.consulting.sa**
5. **Test on development environment**
6. **Merge to `main` branch when ready**
7. **Automatic deployment to https://www.consulting.sa**

### Branch Strategy
- `main`: Production-ready code (auto-deploys to production)
- `development`: Integration testing (auto-deploys to dev environment)
- `feature/*`: Feature development (no auto-deployment)
- `hotfix/*`: Emergency fixes (can be deployed directly to main)

## 📁 Directory Structure on VPS

```
/opt/deployments/
├── github-webhook/
│   └── webhook-handler.py          # GitHub webhook handler
├── scripts/
│   ├── deploy-production.sh        # Production deployment
│   ├── deploy-development.sh       # Development deployment
│   └── health-check.sh            # Health monitoring
├── configs/
│   ├── production.env             # Production environment
│   ├── development.env            # Development environment
│   ├── nginx-production.conf      # Production Nginx config
│   └── nginx-development.conf     # Development Nginx config
├── backups/                       # Automatic backups
└── logs/                          # Deployment logs

/opt/apps/
├── production/                    # Production application
└── development/                   # Development application
```

## 🌐 URLs and Services

### Production
- **Website**: https://www.consulting.sa
- **API**: https://www.consulting.sa/api
- **Webhook**: https://www.consulting.sa/webhook
- **Health**: https://www.consulting.sa/health

### Development
- **Website**: https://dev.consulting.sa
- **API**: https://dev.consulting.sa/api
- **N8N**: https://dev.consulting.sa/n8n
- **Health**: https://dev.consulting.sa/health

## 🔍 Monitoring and Maintenance

### Check System Status
```bash
# SSH to VPS
ssh root@217.79.255.54

# Check webhook service
systemctl status webhook.service

# Check Docker containers
docker ps

# Run health check
/opt/deployments/scripts/health-check.sh

# View deployment logs
tail -f /var/log/deployments/production-$(date +%Y%m%d).log
tail -f /var/log/deployments/development-$(date +%Y%m%d).log
```

### Manual Deployment (Emergency)
```bash
# SSH to VPS
ssh root@217.79.255.54

# Manual production deployment
/opt/deployments/scripts/deploy-production.sh

# Manual development deployment
/opt/deployments/scripts/deploy-development.sh
```

### Rollback Procedure
```bash
# SSH to VPS
ssh root@217.79.255.54

# List available backups
ls -la /opt/deployments/backups/

# Restore from backup (example)
BACKUP_DATE="20250108_143000"
cp -r /opt/deployments/backups/production_$BACKUP_DATE/production/* /opt/apps/production/
cd /opt/apps/production
docker compose -f docker-compose.production.yml up -d
```

## 🔒 Security Features

### SSL/TLS
- Let's Encrypt certificates for all domains
- Automatic renewal configured
- TLS 1.2 and 1.3 support
- Strong cipher suites

### Security Headers
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Content Security Policy
- Referrer Policy

### Access Control
- GitHub webhook signature verification
- Environment-based secrets management
- Service isolation with Docker networks
- Nginx rate limiting (can be configured)

## 🐛 Troubleshooting

### Common Issues

#### Webhook Not Triggering
1. Check GitHub webhook delivery logs
2. Verify webhook URL is accessible: `curl https://www.consulting.sa/webhook`
3. Check webhook service: `systemctl status webhook.service`
4. View webhook logs: `tail -f /var/log/deployments/webhook.log`

#### Deployment Fails
1. Check deployment logs: `tail -f /var/log/deployments/production-$(date +%Y%m%d).log`
2. Verify environment variables are set correctly
3. Check Docker container logs: `docker logs container_name`
4. Verify repository access and branch exists

#### SSL Issues
1. Check certificate status: `certbot certificates`
2. Renew certificates: `certbot renew`
3. Reload Nginx: `systemctl reload nginx`
4. Check Nginx configuration: `nginx -t`

#### Container Issues
1. Check container status: `docker ps -a`
2. View container logs: `docker logs container_name`
3. Restart containers: `docker compose -f docker-compose.production.yml restart`
4. Rebuild containers: `docker compose -f docker-compose.production.yml up -d --build`

### Log Locations
- **Webhook logs**: `/var/log/deployments/webhook.log`
- **Deployment logs**: `/var/log/deployments/production-YYYYMMDD.log`
- **Nginx logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **Container logs**: `docker logs container_name`

## 📊 Performance Optimization

### Frontend Optimization
- Next.js production build with optimization
- Gzip compression enabled in Nginx
- Static file caching with long expiry
- Image optimization
- Code splitting and lazy loading

### Backend Optimization
- Redis caching for session and data
- Database connection pooling
- API response caching
- Health check endpoints for monitoring

### Infrastructure Optimization
- Docker multi-stage builds
- Container health checks
- Nginx reverse proxy with caching
- Log rotation to prevent disk space issues

## 🔄 Backup Strategy

### Automated Backups
- **Before each deployment**: Automatic backup of current version
- **Retention**: 30 days of deployment backups
- **Location**: `/opt/deployments/backups/`

### Manual Backup
```bash
# Create manual backup
BACKUP_NAME="manual_$(date +%Y%m%d_%H%M%S)"
mkdir -p /opt/deployments/backups/$BACKUP_NAME
cp -r /opt/apps/production /opt/deployments/backups/$BACKUP_NAME/
cp -r /opt/apps/development /opt/deployments/backups/$BACKUP_NAME/
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Load balancer setup (Nginx or external)
- Multiple application instances
- Database clustering
- Redis clustering
- CDN integration

### Monitoring
- Application performance monitoring
- Error tracking and alerting
- Uptime monitoring
- Resource usage monitoring
- Custom metrics and dashboards

## 🎓 Team Training

### Developer Workflow
1. **Clone repository**: `git clone https://github.com/your-username/your-private-repo.git`
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Develop and test locally**: `npm run dev`
4. **Push to development**: `git push origin development`
5. **Test on dev environment**: https://dev.consulting.sa
6. **Create pull request to main**
7. **Merge triggers production deployment**

### Best Practices
- Always test on development environment first
- Use meaningful commit messages
- Keep feature branches small and focused
- Review deployment logs after each deployment
- Monitor application health after deployments

## 📚 Documentation Standards

### Code Documentation
- README files for each component
- API documentation
- Environment variable documentation
- Deployment procedure documentation

### Operational Documentation
- Troubleshooting guides
- Monitoring procedures
- Backup and recovery procedures
- Security incident response

## 🚨 Emergency Procedures

### Production Outage
1. **Check system status**: Run health check script
2. **Check logs**: Review recent deployment and error logs
3. **Rollback if needed**: Use backup restoration procedure
4. **Notify team**: Use established communication channels
5. **Document incident**: Create post-mortem documentation

### Security Incident
1. **Isolate affected systems**: Stop containers if necessary
2. **Review access logs**: Check for unauthorized access
3. **Update credentials**: Rotate API keys and passwords
4. **Apply security patches**: Update all components
5. **Document and review**: Improve security procedures

---

## 📞 Support Information

### System Administrator
- **Contact**: [Your contact information]
- **Availability**: [Your availability hours]
- **Emergency**: [Emergency contact method]

### Development Team
- **Lead Developer**: [Contact information]
- **Repository**: https://github.com/your-username/your-private-repo
- **Documentation**: This guide and repository README

### Infrastructure
- **VPS Provider**: [Provider information]
- **Domain Registrar**: [Registrar information]
- **SSL Provider**: Let's Encrypt (automated)

---

**Last Updated**: January 8, 2025  
**Version**: 1.0  
**Status**: Production Ready  
**Next Review**: Monthly system health review