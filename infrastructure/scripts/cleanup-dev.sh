#!/bin/bash
set -e

# Development Environment Cleanup Script
# This script removes all development containers and cleans up

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

echo -e "${BLUE}🧹 Cleaning up Development Environment${NC}"

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    echo -e "${YELLOW}Running on VPS: $command${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Test VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Step 1: Stop all development containers
echo -e "${BLUE}Step 1: Stopping all development containers...${NC}"
run_on_vps "docker stop \$(docker ps -q --filter name=agentic-*-dev) 2>/dev/null || true"

# Step 2: Remove all development containers
echo -e "${BLUE}Step 2: Removing all development containers...${NC}"
run_on_vps "docker rm \$(docker ps -aq --filter name=agentic-*-dev) 2>/dev/null || true"

# Step 3: Remove development images
echo -e "${BLUE}Step 3: Removing development images...${NC}"
run_on_vps "docker rmi \$(docker images -q --filter reference=agentic-*-dev) 2>/dev/null || true"

# Step 4: Clean up directories
echo -e "${BLUE}Step 4: Cleaning up directories...${NC}"
run_on_vps "rm -rf /opt/agentic-platform-dev /opt/agent-dev /opt/frontend-dev"

# Step 5: Show current status
echo -e "${BLUE}Step 5: Current container status...${NC}"
run_on_vps "docker ps --filter name=agentic"

echo -e "${GREEN}🧹 Development environment cleanup completed!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Deploy static environment: ./infrastructure/scripts/deploy-dev-static.sh"
echo "2. Deploy backend services: ./infrastructure/scripts/deploy-backend-dev.sh"
echo "3. Deploy agent: ./infrastructure/scripts/deploy-agent-dev.sh"
echo "4. Deploy frontend: ./infrastructure/scripts/deploy-frontend-dev.sh"

echo -e "${GREEN}✅ Ready for clean deployment!${NC}"