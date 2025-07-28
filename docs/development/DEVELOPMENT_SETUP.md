# Development Environment Setup Guide

This guide explains how to set up a development environment for the Agentic AI Platform on your VPS alongside the production environment.

## Overview

The development setup allows you to:
- Test changes without affecting production
- Use different ports to avoid conflicts
- Enable debug logging and development features
- Use test API keys (especially for Stripe)
- Run alongside production environment

## Branch Strategy

### Recommended Git Workflow

1. **Create a develop branch:**
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

2. **For feature development:**
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   # Make changes
   git commit -m "Add your feature"
   git push -u origin feature/your-feature-name
   # Create PR to develop branch
   ```

3. **For production releases:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

## Development Environment Setup

### Step 1: Configure Development Environment

1. **Copy and configure development environment:**
   ```bash
   cp .env.development .env.dev
   # Edit .env.dev with your actual values
   ```

2. **Key differences from production:**
   - Different ports (3001, 8001, 6380, 5679, 8080)
   - Debug logging enabled
   - Test API keys for Stripe
   - Development URLs
   - Separate n8n instance

### Step 2: Deploy Development Environment

1. **Deploy to VPS:**
   ```bash
   ./infrastructure/scripts/deploy-dev-vps.sh
   ```

2. **The script will:**
   - Create `/opt/agentic-platform-dev` directory
   - Copy your code to VPS
   - Build development containers
   - Start services on different ports
   - Set up nginx proxy for easy access

### Step 3: Access Development Environment

After deployment, you can access:

- **🌐 Development Site:** `https://dev.consulting.sa`
- **🔧 Development API:** `https://dev.consulting.sa/api`
- **📊 Development n8n:** `https://dev.consulting.sa/n8n` (admin/devpassword)

**Direct Container Access (for debugging):**
- **Frontend Direct:** `http://YOUR_VPS_IP:3001`
- **Backend Direct:** `http://YOUR_VPS_IP:8001`
- **n8n Direct:** `http://YOUR_VPS_IP:5679`
- **Development Redis:** `YOUR_VPS_IP:6380`

## Development Workflow

### Making Changes

1. **Make changes locally:**
   ```bash
   git checkout develop
   # Make your changes
   git add .
   git commit -m "Your changes"
   git push origin develop
   ```

2. **Deploy changes to development:**
   ```bash
   ./infrastructure/scripts/deploy-dev-vps.sh
   ```

3. **Test your changes:**
   - Access development environment
   - Test functionality
   - Check logs if needed

### Managing Development Environment

**On VPS, you can use the management script:**

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Navigate to development directory
cd /opt/agentic-platform-dev

# Use management script
./dev-manage.sh status    # Check status
./dev-manage.sh restart   # Restart services
./dev-manage.sh rebuild   # Rebuild containers
./dev-manage.sh logs      # View logs
./dev-manage.sh stop      # Stop development
./dev-manage.sh start     # Start development
```

### Viewing Logs

```bash
# From your local machine
sshpass -p 'YOUR_PASSWORD' ssh root@YOUR_VPS_IP 'cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml logs -f'

# Or on VPS
cd /opt/agentic-platform-dev
./dev-manage.sh logs frontend-dev  # Specific service
./dev-manage.sh logs               # All services
```

## Environment Differences

### Production vs Development

| Aspect | Production | Development |
|--------|------------|-------------|
| **Directory** | `/opt/agentic-platform` | `/opt/agentic-platform-dev` |
| **URL** | `https://consulting.sa` | `https://dev.consulting.sa` |
| **Frontend Port** | 3000 | 3001 |
| **Backend Port** | 8000 | 8001 |
| **Redis Port** | 6379 | 6380 |
| **n8n Port** | 5678 | 5679 |
| **SSL** | Wildcard SSL | Wildcard SSL |
| **Logging** | INFO | DEBUG |
| **Stripe Keys** | Live | Test |

### Configuration Files

- **Production:** `docker-compose.production.yml`
- **Development:** `docker-compose.development.yml`
- **Environment:** `.env.dev` (development-specific)

## Testing Strategy

### Before Merging to Main

1. **Test in development environment:**
   - Deploy to development
   - Test all functionality
   - Check logs for errors
   - Verify integrations work

2. **Run automated tests:**
   ```bash
   # Run tests locally
   cd backend && python -m pytest
   cd frontend && npm test
   ```

3. **Performance check:**
   - Monitor resource usage
   - Check response times
   - Verify no memory leaks

### Integration Testing

1. **Test all integrations:**
   - Supabase database operations
   - AI service calls (Gemini)
   - Stripe payment flows (test mode)
   - n8n workflow automation
   - MCP server communication

2. **End-to-end testing:**
   - Customer journey flows
   - Agent interactions
   - Live chat handoff
   - Payment processing

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Check if ports are already in use
   - Modify ports in docker-compose.development.yml

2. **Container build failures:**
   ```bash
   # Rebuild without cache
   ./dev-manage.sh rebuild
   ```

3. **Database connection issues:**
   - Verify Supabase credentials
   - Check network connectivity
   - Review environment variables

4. **Service health check failures:**
   ```bash
   # Check individual service logs
   ./dev-manage.sh logs backend-dev
   ./dev-manage.sh logs frontend-dev
   ```

### Debugging

1. **Enable verbose logging:**
   - Set `DEBUG=true` in `.env.dev`
   - Set `ADK_LOG_LEVEL=DEBUG`
   - Set `VERBOSE_LOGGING=true`

2. **Access container shells:**
   ```bash
   docker exec -it agentic-backend-dev bash
   docker exec -it agentic-frontend-dev sh
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats
   ```

## Security Considerations

### Development Security

1. **Use test API keys:**
   - Never use production Stripe keys
   - Use separate Livekit instances if possible
   - Consider separate Supabase projects

2. **Network security:**
   - Development ports are exposed
   - Consider VPN access for sensitive testing
   - Don't expose development to public internet

3. **Data protection:**
   - Don't use real customer data in development
   - Use test data and mock services
   - Regular cleanup of development data

## Best Practices

### Development Workflow

1. **Always test in development first**
2. **Use feature branches for new features**
3. **Keep development environment updated**
4. **Regular cleanup of old containers and images**
5. **Monitor resource usage**

### Code Quality

1. **Follow existing code patterns**
2. **Add tests for new features**
3. **Update documentation**
4. **Use proper error handling**
5. **Follow security best practices**

## Maintenance

### Regular Tasks

1. **Update dependencies:**
   ```bash
   # Update Python packages
   cd backend && pip install -r requirements.txt --upgrade
   
   # Update Node packages
   cd frontend && npm update
   ```

2. **Clean up Docker:**
   ```bash
   docker system prune -f
   docker volume prune -f
   ```

3. **Monitor logs:**
   - Check for errors
   - Monitor performance
   - Review security events

4. **Backup development data:**
   - Export important test data
   - Backup configuration files
   - Document test scenarios

This development setup ensures you can safely test changes without affecting your production environment while maintaining the same architecture and functionality.