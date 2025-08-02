#!/bin/bash
set -e

# Fix Development Environment Script
# This script fixes the directory structure and starts containers properly

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}

echo -e "${BLUE}🔧 Fixing Development Environment${NC}"

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

# Step 1: Stop existing containers
echo -e "${BLUE}Step 1: Stopping existing development containers...${NC}"
run_on_vps "docker stop agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev 2>/dev/null || true"
run_on_vps "docker rm agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev 2>/dev/null || true"

# Step 2: Clean and recreate directory structure
echo -e "${BLUE}Step 2: Recreating proper directory structure...${NC}"
run_on_vps "rm -rf /opt/agentic-platform-dev"
run_on_vps "mkdir -p /opt/agentic-platform-dev/{frontend,backend,infrastructure}"

# Step 3: Copy files with proper structure
echo -e "${BLUE}Step 3: Copying files with correct structure...${NC}"
copy_to_vps "frontend/" "/opt/agentic-platform-dev/"

# Copy backend excluding .venv directory
echo -e "${YELLOW}Copying backend (excluding .venv)...${NC}"
sshpass -p "$VPS_PASSWORD" rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' -e "ssh -o StrictHostKeyChecking=no" backend/ "$VPS_USER@$VPS_HOST:/opt/agentic-platform-dev/backend/"

copy_to_vps "infrastructure/" "/opt/agentic-platform-dev/"
copy_to_vps ".env.dev" "/opt/agentic-platform-dev/"
copy_to_vps "package.json" "/opt/agentic-platform-dev/"

# Step 4: Verify directory structure
echo -e "${BLUE}Step 4: Verifying directory structure...${NC}"
run_on_vps "ls -la /opt/agentic-platform-dev/"
run_on_vps "ls -la /opt/agentic-platform-dev/infrastructure/docker/"

# Step 5: Start containers one by one
echo -e "${BLUE}Step 5: Starting development containers...${NC}"

# Start Redis first
echo -e "${YELLOW}Starting Redis...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d redis-dev"

# Start n8n
echo -e "${YELLOW}Starting n8n...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d n8n-dev"

# Build and start backend
echo -e "${YELLOW}Building and starting backend...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d --build backend-dev"

# Build and start frontend
echo -e "${YELLOW}Building and starting frontend...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d --build frontend-dev"

# Step 6: Wait for services to start
echo -e "${BLUE}Step 6: Waiting for services to start...${NC}"
sleep 30

# Step 7: Check container status
echo -e "${BLUE}Step 7: Checking container status...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml ps"

# Step 8: Run health checks
echo -e "${BLUE}Step 8: Running health checks...${NC}"

# Check frontend
if run_on_vps "curl -f http://localhost:3001/"; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
    run_on_vps "docker logs --tail 10 agentic-frontend-dev" || echo "Could not get frontend logs"
fi

# Check backend
if run_on_vps "curl -f http://localhost:8001/health"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed${NC}"
    run_on_vps "docker logs --tail 10 agentic-backend-dev" || echo "Could not get backend logs"
fi

# Step 9: Update nginx to use frontend container (FIXED)
echo -e "${BLUE}Step 9: Updating nginx configuration...${NC}"
copy_to_vps "infrastructure/nginx/development-fixed.conf" "/etc/nginx/sites-available/agentic-platform-dev-full"
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform-dev-full /etc/nginx/sites-enabled/agentic-platform-dev"
run_on_vps "nginx -t && systemctl reload nginx"

# Step 10: Final test
echo -e "${BLUE}Step 10: Final development site test...${NC}"
sleep 10

if run_on_vps "curl -f https://dev.consulting.sa/"; then
    echo -e "${GREEN}🎉 Development environment is working!${NC}"
    echo ""
    echo -e "${BLUE}=== DEVELOPMENT ENVIRONMENT READY ====${NC}"
    echo "🌐 Development Site: https://dev.consulting.sa"
    echo "🔧 Backend API: https://dev.consulting.sa/api/"
    echo "📊 n8n Workflows: https://dev.consulting.sa/n8n/"
    echo "🏥 Health Check: https://dev.consulting.sa/health"
    echo ""
    echo -e "${GREEN}✅ Ready for functionality testing and comparison with production!${NC}"
else
    echo -e "${YELLOW}⚠ Development site still not fully working${NC}"
    echo "Check container logs and nginx configuration"
fi

echo -e "${BLUE}🔧 Development environment fix completed!${NC}"