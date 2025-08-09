#!/bin/bash
# 🚀 MANUAL DEPLOYMENT OF IMMEDIATE FIX
# Deploys the Next.js error fix manually (temporary solution)

set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"

echo "🚀 MANUAL DEPLOYMENT OF NEXT.JS FIX"
echo "📅 $(date)"
echo "⚠️  This is a temporary solution. Use GitHub deployment for production."
echo ""

# Function to run SSH command
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

# Function to copy file to server
scp_file() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$1" "$SERVER_USER@$SERVER_IP:$2"
    if [ $? -eq 0 ]; then
        echo "✅ SCP: $1 → $2"
    else
        echo "❌ SCP FAILED: $1 → $2"
        exit 1
    fi
}

echo "🔍 Step 1: Backing up current deployment..."
ssh_run "mkdir -p /opt/backups/manual_fix_$(date +%Y%m%d_%H%M%S)"
ssh_run "cp -r /opt/docker-apps/production/agentic-site /opt/backups/manual_fix_$(date +%Y%m%d_%H%M%S)/" || echo "Backup completed"

echo ""
echo "🔍 Step 2: Copying fixed files to the correct locations..."

# Copy the fixed frontend files to the nested structure
scp_file "frontend/app/layout.tsx" "/opt/docker-apps/production/agentic-site/agentic-site/frontend/app/layout.tsx"
scp_file "frontend/components/chatbot/ChatbotWrapper.tsx" "/opt/docker-apps/production/agentic-site/agentic-site/frontend/components/chatbot/ChatbotWrapper.tsx"

# Copy environment and docker-compose files to the root level
scp_file ".env.production" "/opt/docker-apps/production/agentic-site/.env.production"
scp_file "docker-compose.production-fixed.yml" "/opt/docker-apps/production/agentic-site/docker-compose.production-fixed.yml"

echo ""
echo "🔍 Step 3: Checking current containers..."
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔍 Step 4: Stopping existing containers..."
ssh_run "cd /opt/docker-apps/production/agentic-site && docker compose -f docker-compose.production.yml down" || echo "No containers to stop"

echo ""
echo "🔍 Step 5: Building and starting containers with fixed configuration..."
ssh_run "cd /opt/docker-apps/production/agentic-site && docker compose -f docker-compose.production-fixed.yml up -d --build"

echo ""
echo "🔍 Step 6: Waiting for containers to start..."
sleep 45

echo ""
echo "🔍 Step 7: Health check..."
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔍 Step 8: Testing the fix..."

# Test frontend
echo "Testing frontend..."
if ssh_run "curl -f -s http://localhost:3000/ > /dev/null 2>&1"; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting - checking logs..."
    ssh_run "docker logs agentic-frontend-prod --tail 20" || echo "Container may still be starting"
fi

# Test backend
echo "Testing backend..."
if ssh_run "curl -f -s http://localhost:8000/health > /dev/null 2>&1"; then
    echo "✅ Backend is responding"
else
    echo "⚠️  Backend may still be starting - checking logs..."
    ssh_run "docker logs agentic-backend-prod --tail 20" || echo "Container may still be starting"
fi

echo ""
echo "✅ MANUAL FIX DEPLOYMENT COMPLETED"
echo ""
echo "🌐 Test the site: https://www.consulting.sa"
echo ""
echo "📋 Container Status:"
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "📋 Next Steps:"
echo "   1. Test the website to ensure the error is fixed"
echo "   2. If there are still issues, check the logs:"
echo "      ssh root@217.79.255.54 'docker logs agentic-frontend-prod --tail 50'"
echo "   3. Set up proper GitHub deployment for future updates:"
echo "      ./infrastructure/scripts/setup-github-integration.sh"
echo "   4. This manual fix is temporary - use GitHub workflow going forward"