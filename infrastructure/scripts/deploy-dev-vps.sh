#!/bin/bash
set -e

# Development VPS Deployment Script
# This script deploys the development version of the agentic AI platform to VPS

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}
DOMAIN=${DOMAIN:-"consulting.sa"}
DEV_BRANCH=${DEV_BRANCH:-"develop"}

echo -e "${BLUE}🚀 Deploying Development Environment to VPS: $VPS_HOST${NC}"
echo -e "${BLUE}📋 Branch: $DEV_BRANCH${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    echo -e "${YELLOW}Running on VPS: $command${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    echo -e "${YELLOW}Copying $local_path to VPS:$remote_path${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}Installing sshpass...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        echo -e "${RED}Please install sshpass manually${NC}"
        exit 1
    fi
fi

# Test VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Step 1: Create development directory
echo -e "${BLUE}Step 1: Setting up development environment...${NC}"
run_on_vps "mkdir -p /opt/agentic-platform-dev"

# Step 2: Stop existing development containers (if any)
echo -e "${BLUE}Step 2: Stopping existing development containers...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml down" || echo "No existing containers to stop"

# Step 3: Copy application files
echo -e "${BLUE}Step 3: Copying application files...${NC}"
sshpass -p "$VPS_PASSWORD" rsync -avz --delete --exclude='.venv' --exclude='node_modules' --exclude='.git' --exclude='.next' --exclude='__pycache__' --exclude='*.pyc' -e "ssh -o StrictHostKeyChecking=no" . "$VPS_USER@$VPS_HOST:/opt/agentic-platform-dev/"

# Step 4: Setup development environment (inherits from production .env)
echo -e "${BLUE}Step 4: Setting up development environment variables...${NC}"
copy_to_vps ".env" "/opt/agentic-platform-dev/.env.dev"

# Add development-specific overrides to existing .env
run_on_vps "cat >> /opt/agentic-platform-dev/.env.dev << 'EOF'

# =============================================================================
# DEVELOPMENT ENVIRONMENT OVERRIDES
# =============================================================================
# These override the production values for development

# Development Environment
NODE_ENV=development
DEBUG=true
VERBOSE_LOGGING=true
ADK_LOG_LEVEL=DEBUG
FORCE_HTTPS=true

# Development URLs (using wildcard SSL subdomain)
DEV_SITE_URL=https://dev.consulting.sa
DEV_ADMIN_URL=https://dev.consulting.sa/api
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://dev.consulting.sa/api

# Development Database Settings (same Supabase, different tables)
DEV_TABLE_PREFIX=dev_
DEV_SCHEMA=development

# Development Ports (to avoid conflicts with production)
FRONTEND_DEV_PORT=3001
BACKEND_DEV_PORT=8001
REDIS_DEV_PORT=6380
N8N_DEV_PORT=5679
NGINX_DEV_PORT=8080

# Development-specific ADK configuration
ADK_AGENT_PORT=8001

# Development Contact Email
NEXT_PUBLIC_CONTACT_EMAIL=dev@consulting.sa

# Disable Analytics for Development
NEXT_PUBLIC_GA_ID=

# Development Docker Configuration
COMPOSE_PROJECT_NAME=agentic-dev
DOMAIN=dev.consulting.sa

# Development Debugging
NEXT_TELEMETRY_DISABLED=1
ANALYZE=false

# Development MCP Configuration
MCP_SERVER_URL=http://localhost:8001
MCP_SERVER_PORT=8001
N8N_MCP_PORT=8004

# Development n8n Configuration
N8N_DEV_URL=http://n8n-dev:5678

# Note: Most API keys (Supabase, Gemini, etc.) are inherited from production .env
# Only Stripe should use test keys - add them manually if different from production

EOF"

# Step 5: Build and start development containers
echo -e "${BLUE}Step 5: Building and starting development containers...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev build"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d"

# Step 6: Configure development subdomain with SSL
echo -e "${BLUE}Step 6: Setting up development subdomain (dev.consulting.sa)...${NC}"
run_on_vps "mkdir -p /etc/nginx/sites-available"
copy_to_vps "infrastructure/nginx/development-fixed.conf" "/etc/nginx/sites-available/agentic-platform-dev"

# Enable the development site
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform-dev /etc/nginx/sites-enabled/agentic-platform-dev"

# Test nginx configuration and reload
run_on_vps "nginx -t && systemctl reload nginx" || echo "Nginx configuration test failed, please check manually"

# Step 7: Wait for services to start and run health checks
echo -e "${BLUE}Step 7: Running health checks...${NC}"
sleep 45

# Check if development services are running
echo -e "${YELLOW}Checking development services...${NC}"
if run_on_vps "curl -f http://localhost:3001/api/health"; then
    echo -e "${GREEN}✓ Development Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Development Frontend health check failed${NC}"
fi

if run_on_vps "curl -f http://localhost:8001/health"; then
    echo -e "${GREEN}✓ Development Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Development Backend health check failed${NC}"
fi

# Step 8: Display access information
echo -e "${GREEN}🎉 Development deployment completed!${NC}"
echo ""
echo -e "${BLUE}Development Access URLs:${NC}"
echo "- 🌐 Development Site: https://dev.consulting.sa"
echo "- 🔧 Development API: https://dev.consulting.sa/api"
echo "- 📊 Development n8n: https://dev.consulting.sa/n8n (admin/devpassword)"
echo ""
echo -e "${BLUE}Direct Container Access (for debugging):${NC}"
echo "- Frontend Direct: http://$VPS_HOST:3001"
echo "- Backend Direct: http://$VPS_HOST:8001"
echo "- n8n Direct: http://$VPS_HOST:5679"
echo "- Redis: $VPS_HOST:6380"
echo ""
echo -e "${BLUE}Container Status:${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml ps"
echo ""
echo -e "${YELLOW}Development Environment Notes:${NC}"
echo "1. This runs alongside your production environment"
echo "2. Uses different ports to avoid conflicts"
echo "3. Has debug logging enabled"
echo "4. Uses development/test API keys where configured"
echo "5. Code changes require container rebuild"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "- View logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml logs -f'"
echo "- Restart services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml restart'"
echo "- Stop development: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml down'"

# Create development management script on VPS
run_on_vps "cat > /opt/agentic-platform-dev/dev-manage.sh << 'EOF'
#!/bin/bash

case \$1 in
    start)
        echo \"Starting development environment...\"
        docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d
        ;;
    stop)
        echo \"Stopping development environment...\"
        docker-compose -f infrastructure/docker/docker-compose.development.yml down
        ;;
    restart)
        echo \"Restarting development environment...\"
        docker-compose -f infrastructure/docker/docker-compose.development.yml restart
        ;;
    rebuild)
        echo \"Rebuilding development environment...\"
        docker-compose -f infrastructure/docker/docker-compose.development.yml down
        docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev build --no-cache
        docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d
        ;;
    logs)
        docker-compose -f infrastructure/docker/docker-compose.development.yml logs -f \$2
        ;;
    status)
        echo \"=== Development Environment Status ===\"
        docker-compose -f infrastructure/docker/docker-compose.development.yml ps
        echo \"\"
        echo \"=== Health Checks ===\"
        curl -f http://localhost:3001/api/health && echo \"Frontend: OK\" || echo \"Frontend: FAIL\"
        curl -f http://localhost:8001/health && echo \"Backend: OK\" || echo \"Backend: FAIL\"
        ;;
    *)
        echo \"Usage: \$0 {start|stop|restart|rebuild|logs [service]|status}\"
        exit 1
        ;;
esac
EOF"

run_on_vps "chmod +x /opt/agentic-platform-dev/dev-manage.sh"

echo -e "${GREEN}✅ Development VPS deployment completed!${NC}"
echo -e "${BLUE}Management: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST '/opt/agentic-platform-dev/dev-manage.sh status'${NC}"