#!/bin/bash
set -e

# Simple Development Static Deployment Script
# This script deploys a working static version first, then we can build up

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

echo -e "${BLUE}🚀 Deploying Static Development Environment to VPS: $VPS_HOST${NC}"

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

# Test VPS connection
echo -e "${BLUE}Testing VPS connection...${NC}"
if run_on_vps "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ VPS connection established${NC}"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

# Step 1: Create static web directory
echo -e "${BLUE}Step 1: Setting up static web directory...${NC}"
run_on_vps "mkdir -p /var/www/dev-consulting"

# Step 2: Copy static files
echo -e "${BLUE}Step 2: Copying static development files...${NC}"
copy_to_vps "frontend/public/dev-test.html" "/var/www/dev-consulting/"

# Step 3: Set proper permissions
echo -e "${BLUE}Step 3: Setting file permissions...${NC}"
run_on_vps "chown -R www-data:www-data /var/www/dev-consulting"
run_on_vps "chmod -R 755 /var/www/dev-consulting"

# Step 4: Update nginx configuration
echo -e "${BLUE}Step 4: Updating nginx configuration for static serving...${NC}"
copy_to_vps "infrastructure/nginx/development-static.conf" "/etc/nginx/sites-available/agentic-platform-dev-static"

# Enable the static development site
run_on_vps "ln -sf /etc/nginx/sites-available/agentic-platform-dev-static /etc/nginx/sites-enabled/agentic-platform-dev"

# Test nginx configuration and reload
echo -e "${BLUE}Step 5: Testing and reloading nginx...${NC}"
if run_on_vps "nginx -t"; then
    run_on_vps "systemctl reload nginx"
    echo -e "${GREEN}✓ Nginx configuration updated successfully${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi

# Step 6: Test the static site
echo -e "${BLUE}Step 6: Testing static development site...${NC}"
sleep 5

if run_on_vps "curl -f https://dev.consulting.sa/health"; then
    echo -e "${GREEN}✓ Development static site is accessible${NC}"
else
    echo -e "${YELLOW}⚠ Development site health check failed${NC}"
fi

# Step 7: Display access information
echo -e "${GREEN}🎉 Static development deployment completed!${NC}"
echo ""
echo -e "${BLUE}Development Access URLs:${NC}"
echo "- 🌐 Development Site: https://dev.consulting.sa"
echo "- 🏥 Health Check: https://dev.consulting.sa/health"
echo ""
echo -e "${YELLOW}Development Environment Notes:${NC}"
echo "1. This is a STATIC version for testing and comparison"
echo "2. Use this to compare with production and identify issues"
echo "3. Next step: Deploy backend services separately"
echo "4. Then: Deploy full Next.js frontend"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Visit https://dev.consulting.sa to see the development environment"
echo "2. Compare with https://consulting.sa (production)"
echo "3. Test the interface and identify missing functionality"
echo "4. Deploy backend services: ./infrastructure/scripts/deploy-backend-dev.sh"
echo "5. Deploy frontend: ./infrastructure/scripts/deploy-frontend-dev.sh"

echo -e "${GREEN}✅ Static development environment deployed successfully!${NC}"