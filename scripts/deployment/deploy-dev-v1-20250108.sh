#!/bin/bash
# Script: deploy-dev-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: Deploy development environment with frontend UI enhancements
# Usage: ./deploy-dev-v1-20250108.sh
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version for development deployment with UI enhancements

set -e

# Configuration
VPS_IP="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"
DEV_PORTS="3001:3000,8001:8000,6380:6379,5679:5678"

echo "🚀 Starting Development Deployment v1 - $(date)"
echo "📍 Target: dev.consulting.sa (${VPS_IP})"
echo "🔧 Environment: Development containers only"

# Function to execute SSH commands
ssh_exec() {
    sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${VPS_IP}" "$1"
}

# Function to copy files to VPS
ssh_copy() {
    sshpass -p "${SSH_PASS}" scp -o StrictHostKeyChecking=no -r "$1" "${SSH_USER}@${VPS_IP}:$2"
}

# Step 1: Check current container status
echo "📊 Checking current container status..."
ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(agentic|consulting)'"

# Step 2: Build and copy frontend changes
echo "🏗️ Building frontend with UI enhancements..."
cd frontend
npm run build
cd ..

# Step 3: Create deployment package
echo "📦 Creating deployment package..."
tar -czf deployment-dev-$(date +%Y%m%d-%H%M%S).tar.gz \
    frontend/out \
    frontend/.next \
    frontend/package.json \
    docker-compose.yml \
    .env.development

# Step 4: Copy to VPS
echo "📤 Copying files to VPS..."
ssh_copy "deployment-dev-*.tar.gz" "/tmp/"

# Step 5: Deploy on VPS
echo "🚀 Deploying on VPS..."
ssh_exec "
    cd /opt/agentic-platform
    
    # Extract new files
    tar -xzf /tmp/deployment-dev-*.tar.gz
    
    # Stop development containers only
    docker stop agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev || true
    docker rm agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev || true
    
    # Start development containers
    docker-compose -f docker-compose.development.yml up -d
    
    # Wait for containers to be ready
    sleep 30
    
    # Check health
    curl -f http://localhost:3001/api/health || echo 'Frontend health check failed'
    curl -f http://localhost:8001/health || echo 'Backend health check failed'
"

# Step 6: Verify deployment
echo "✅ Verifying deployment..."
ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'agentic.*dev'"

echo "🎉 Development deployment completed successfully!"
echo "🌐 Access at: https://dev.consulting.sa"
echo "📊 Monitor at: http://${VPS_IP}:3001"

# Cleanup
rm -f deployment-dev-*.tar.gz

echo "📝 Deployment log saved to: /var/log/deploy-dev-$(date +%Y%m%d).log"