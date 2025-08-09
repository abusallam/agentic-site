#!/bin/bash

# Deploy from GitHub Script
# This script pulls latest code from GitHub and deploys to VPS
# Usage: ./deploy-from-github.sh <SSH_ALIAS> <ENVIRONMENT> [BRANCH]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <SSH_ALIAS> <ENVIRONMENT> [BRANCH]${NC}"
    echo -e "${YELLOW}Example: $0 agentic-enterprise-217-79-255-54-development development${NC}"
    exit 1
fi

SSH_ALIAS="$1"
ENVIRONMENT="$2"
BRANCH="${3:-develop}"
DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

echo -e "${BLUE}🚀 Deploying from GitHub${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Environment: $ENVIRONMENT"
echo "Branch: $BRANCH"
echo "Deploy Path: $DEPLOY_PATH"
echo

# Function to run commands on VPS
run_on_vps() {
    ssh "$SSH_ALIAS" "$1"
}

echo -e "${YELLOW}Step 1: Pulling latest code from GitHub...${NC}"

# Pull latest code on VPS
run_on_vps "
    cd $DEPLOY_PATH
    
    # Ensure we're on the correct branch
    git checkout $BRANCH
    
    # Pull latest changes
    git pull origin $BRANCH
    
    echo '✓ Latest code pulled from GitHub'
"

echo -e "${YELLOW}Step 2: Rebuilding and redeploying application...${NC}"

# Rebuild and redeploy
run_on_vps "
    cd $DEPLOY_PATH
    
    # Stop current containers
    docker-compose down
    
    # Rebuild and start containers
    docker-compose up -d --build
    
    echo '✓ Application redeployed'
"

echo -e "${YELLOW}Step 3: Verifying deployment...${NC}"

# Wait for services to be ready
run_on_vps "
    cd $DEPLOY_PATH
    
    # Wait for containers to start
    sleep 15
    
    # Check container status
    echo 'Container Status:'
    docker-compose ps
    
    # Test endpoints
    if curl -s -f --max-time 10 http://localhost:3001/ > /dev/null; then
        echo '✓ Frontend is responding'
    else
        echo '❌ Frontend not responding'
    fi
    
    if curl -s -f --max-time 10 http://localhost:8001/health > /dev/null; then
        echo '✓ Backend is responding'
    else
        echo '❌ Backend not responding'
    fi
"

echo -e "${GREEN}✅ GitHub deployment completed!${NC}"
