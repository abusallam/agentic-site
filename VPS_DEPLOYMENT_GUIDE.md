# VPS Deployment Guide

This guide shows you how to deploy the Agentic Site to any VPS with just an IP address, username, and password.

## Quick Start

### Step 1: Set up a new VPS

```bash
./infrastructure/scripts/setup-new-vps.sh <IP> <USERNAME> <PASSWORD> [ENVIRONMENT]
```

**Examples:**
```bash
# Development environment
./infrastructure/scripts/setup-new-vps.sh 217.79.255.54 root mypassword development

# Production environment  
./infrastructure/scripts/setup-new-vps.sh 192.168.1.100 root mypassword production
```

**What this does:**
- ✅ Sets up SSH key authentication (no more passwords!)
- ✅ Installs Docker, Docker Compose, Nginx
- ✅ Configures firewall and security
- ✅ Creates deployment directories
- ✅ Sets up Nginx configuration
- ✅ Creates management scripts
- ✅ Optimizes system settings

### Step 2: Deploy the application

```bash
./infrastructure/scripts/deploy-to-vps.sh <SSH_ALIAS> <ENVIRONMENT>
```

**Examples:**
```bash
# Deploy to development
./infrastructure/scripts/deploy-to-vps.sh agentic-217-79-255-54 development

# Deploy to production
./infrastructure/scripts/deploy-to-vps.sh agentic-192-168-1-100 production
```

**What this does:**
- ✅ Builds frontend and backend containers locally
- ✅ Transfers containers to VPS
- ✅ Deploys complete application stack
- ✅ Sets up health checks and monitoring
- ✅ Tests all endpoints

## Complete Example

```bash
# 1. Set up VPS (one-time setup)
./infrastructure/scripts/setup-new-vps.sh 217.79.255.54 root gt5qXy22aJ development

# 2. Deploy application (can be run multiple times)
./infrastructure/scripts/deploy-to-vps.sh agentic-217-79-255-54 development
```

## What You Get

### Development Environment
- **Website**: https://dev.consulting.sa/
- **API**: https://dev.consulting.sa/health
- **n8n**: https://dev.consulting.sa/n8n/
- **Backend Admin**: https://dev.consulting.sa/backend/

### Production Environment
- **Website**: https://consulting.sa/
- **API**: https://consulting.sa/health
- **n8n**: https://consulting.sa/n8n/
- **Backend Admin**: https://consulting.sa/backend/

## Management Commands

After setup, you can manage your VPS with these commands:

```bash
# Connect to VPS
ssh agentic-217-79-255-54

# Check status
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-status.sh'

# View logs
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-logs.sh'

# Restart services
ssh agentic-217-79-255-54 '/usr/local/bin/agentic-development-restart.sh'
```

## Environment Configuration

After setup, you'll have a `.env.development` or `.env.production` file. Update it with your actual API keys:

```bash
# Edit environment file
nano .env.development

# Key variables to update:
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
GEMINI_API_KEY=your_gemini_key
```

Then redeploy:
```bash
./infrastructure/scripts/deploy-to-vps.sh agentic-217-79-255-54 development
```

## Multiple VPS Setup

You can set up multiple VPS instances for different purposes:

```bash
# Development server
./infrastructure/scripts/setup-new-vps.sh 10.0.0.1 root pass1 development

# Staging server  
./infrastructure/scripts/setup-new-vps.sh 10.0.0.2 root pass2 staging

# Production server
./infrastructure/scripts/setup-new-vps.sh 10.0.0.3 root pass3 production
```

Each will get its own SSH alias and configuration.

## Troubleshooting

### SSH Connection Issues
```bash
# Test SSH connection
ssh agentic-217-79-255-54 'echo "Connection working"'

# If connection fails, check SSH config
cat ~/.ssh/config | grep -A 10 "agentic-217-79-255-54"
```

### Container Issues
```bash
# Check container status
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose ps'

# View container logs
ssh agentic-217-79-255-54 'cd /opt/docker-apps/development/agentic-site && docker-compose logs -f'
```

### Port Issues
```bash
# Check what's listening on ports
ssh agentic-217-79-255-54 'netstat -tlnp | grep -E ":(3001|8001|5679|6380)"'
```

## Security Features

- ✅ SSH key authentication (no passwords)
- ✅ UFW firewall configured
- ✅ Security headers in Nginx
- ✅ Non-root containers where possible
- ✅ Log rotation configured
- ✅ System optimization applied

## File Structure Created

```
/opt/docker-apps/
├── development/
│   └── agentic-site/
│       ├── docker-compose.yml
│       └── .env
├── production/
│   └── agentic-site/
│       ├── docker-compose.yml
│       └── .env
└── shared/
    ├── ssl/
    └── backups/
```

## Next Steps

1. **Update DNS**: Point your domain to the VPS IP
2. **SSL Certificate**: Set up SSL/TLS certificates
3. **Monitoring**: Configure additional monitoring if needed
4. **Backups**: Set up automated backups
5. **CI/CD**: Integrate with your CI/CD pipeline

## Support

If you encounter issues:

1. Check the logs: `ssh <alias> '/usr/local/bin/agentic-<env>-logs.sh'`
2. Check status: `ssh <alias> '/usr/local/bin/agentic-<env>-status.sh'`
3. Restart services: `ssh <alias> '/usr/local/bin/agentic-<env>-restart.sh'`

The scripts are designed to be idempotent - you can run them multiple times safely.