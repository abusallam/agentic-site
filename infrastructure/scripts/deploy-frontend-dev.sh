#!/bin/bash
set -e

# Frontend Development Container Deployment Script
# This script specifically fixes and deploys the frontend container

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

echo -e "${BLUE}🚀 Deploying Frontend Development Container to VPS: $VPS_HOST${NC}"

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

# Step 1: Stop existing frontend container
echo -e "${BLUE}Step 1: Stopping existing frontend container...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml stop frontend-dev" || echo "No existing frontend container to stop"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml rm -f frontend-dev" || echo "No existing frontend container to remove"

# Step 2: Update project files with focus on frontend and Docker files
echo -e "${BLUE}Step 2: Updating project files...${NC}"
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Using temporary directory: $TEMP_DIR${NC}"

# Copy essential files for frontend build
cp -r frontend/ "$TEMP_DIR/"
cp -r infrastructure/ "$TEMP_DIR/"
cp .env.dev "$TEMP_DIR/" 2>/dev/null || cp .env "$TEMP_DIR/.env.dev"
cp package.json "$TEMP_DIR/" 2>/dev/null || echo "{}" > "$TEMP_DIR/package.json"

# Create archive for efficient transfer
echo -e "${YELLOW}Creating frontend deployment archive...${NC}"
cd "$TEMP_DIR"
tar -czf frontend-deployment.tar.gz .

# Step 3: Transfer files to VPS
echo -e "${BLUE}Step 3: Transferring updated files to VPS...${NC}"
copy_to_vps "$TEMP_DIR/frontend-deployment.tar.gz" "/opt/"

# Extract on VPS, overwriting existing files
run_on_vps "cd /opt && tar -xzf frontend-deployment.tar.gz -C agentic-platform-dev"
run_on_vps "rm -f /opt/frontend-deployment.tar.gz"

# Clean up local temp directory
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✓ Files updated successfully${NC}"

# Step 4: Verify file structure on VPS
echo -e "${BLUE}Step 4: Verifying file structure on VPS...${NC}"
echo -e "${YELLOW}Checking frontend directory structure:${NC}"
run_on_vps "ls -la /opt/agentic-platform-dev/frontend/" || echo "Frontend directory not found"
echo -e "${YELLOW}Checking Docker files:${NC}"
run_on_vps "ls -la /opt/agentic-platform-dev/infrastructure/docker/" || echo "Docker directory not found"

# Step 5: Build frontend container with verbose output
echo -e "${BLUE}Step 5: Building frontend container...${NC}"
echo -e "${YELLOW}This may take several minutes for the first build...${NC}"

# Build with no cache to ensure fresh build
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml build --no-cache frontend-dev"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend container built successfully${NC}"
else
    echo -e "${RED}❌ Frontend container build failed${NC}"
    echo -e "${YELLOW}Checking build logs...${NC}"
    run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml logs frontend-dev" || echo "Could not get build logs"
    exit 1
fi

# Step 6: Start frontend container
echo -e "${BLUE}Step 6: Starting frontend container...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml --env-file .env.dev up -d frontend-dev"

# Step 7: Wait for container to start
echo -e "${BLUE}Step 7: Waiting for frontend container to start...${NC}"
sleep 30

# Step 8: Check container status
echo -e "${BLUE}Step 8: Checking frontend container status...${NC}"
run_on_vps "cd /opt/agentic-platform-dev && docker-compose -f infrastructure/docker/docker-compose.development.yml ps frontend-dev"

# Step 9: Test frontend container health
echo -e "${BLUE}Step 9: Testing frontend container health...${NC}"
echo -e "${YELLOW}Checking if frontend is responding on port 3001...${NC}"

# Wait a bit more for the container to fully start
sleep 30

if run_on_vps "curl -f http://localhost:3001/"; then
    echo -e "${GREEN}✓ Frontend container is responding${NC}"
else
    echo -e "${YELLOW}⚠ Frontend container health check failed${NC}"
    echo -e "${YELLOW}Checking frontend logs...${NC}"
    run_on_vps "docker logs --tail 30 agentic-frontend-dev" || echo "Could not get frontend logs"
    
    echo -e "${YELLOW}Checking container status...${NC}"
    run_on_vps "docker ps -a | grep frontend-dev" || echo "Could not get container status"
fi

# Step 10: Update nginx configuration if needed (FIXED)
echo -e "${BLUE}Step 10: Ensuring nginx configuration is up to date...${NC}"
copy_to_vps "infrastructure/nginx/development-fixed.conf" "/etc/nginx/sites-available/agentic-platform-dev-full"

# Enable the development site
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform-dev-full /etc/nginx/sites-enabled/agentic-platform-dev"

# Test nginx configuration and reload
if run_on_vps "nginx -t"; then
    run_on_vps "systemctl reload nginx"
    echo -e "${GREEN}✓ Nginx configuration updated successfully${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
fi

# Step 11: Final comprehensive health check
echo -e "${BLUE}Step 11: Running final health checks...${NC}"

echo -e "${YELLOW}Checking frontend container logs:${NC}"
run_on_vps "docker logs --tail 10 agentic-frontend-dev" || echo "Could not get frontend logs"

echo -e "${YELLOW}Checking if frontend is accessible through nginx:${NC}"
if run_on_vps "curl -f https://dev.consulting.sa/"; then
    echo -e "${GREEN}✓ Frontend is accessible through nginx${NC}"
else
    echo -e "${YELLOW}⚠ Frontend not accessible through nginx${NC}"
fi

echo -e "${YELLOW}Checking container resource usage:${NC}"
run_on_vps "docker stats --no-stream agentic-frontend-dev" || echo "Could not get container stats"

# Step 12: Display access information
echo -e "${GREEN}🎉 Frontend Development Container Deployment Completed!${NC}"
echo ""
echo -e "${BLUE}=== FRONTEND ACCESS INFORMATION ====${NC}"
echo ""
echo -e "${GREEN}🌐 Development Site:${NC}"
echo "   https://dev.consulting.sa"
echo ""
echo -e "${GREEN}🔍 Direct Container Access:${NC}"
echo "   http://$VPS_HOST:3001"
echo ""
echo -e "${GREEN}🛠️ Container Management:${NC}"
echo "   - View logs: docker logs agentic-frontend-dev"
echo "   - Restart: docker restart agentic-frontend-dev"
echo "   - Shell access: docker exec -it agentic-frontend-dev sh"
echo ""
echo -e "${BLUE}=== TROUBLESHOOTING ====${NC}"
echo "If the frontend is not working:"
echo "1. Check container logs: docker logs agentic-frontend-dev"
echo "2. Check if port 3001 is accessible: curl http://localhost:3001"
echo "3. Verify nginx configuration: nginx -t"
echo "4. Check container status: docker ps | grep frontend-dev"
echo ""
echo -e "${GREEN}✅ Frontend Container Ready!${NC}"