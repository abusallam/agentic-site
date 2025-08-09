#!/bin/bash
# Script: docker-dev-restart-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: Safely restart development containers only (never touches production)
# Usage: ./docker-dev-restart-v1-20250108.sh [service-name]
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version with development-only restart capability

set -e

# Configuration
VPS_IP="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"
DEV_CONTAINERS=("agentic-frontend-dev" "agentic-backend-dev" "agentic-redis-dev" "agentic-n8n-dev")

# Function to execute SSH commands
ssh_exec() {
    sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${VPS_IP}" "$1"
}

# Parse arguments
SERVICE=${1:-"all"}

echo "🔄 Development Container Restart v1 - $(date)"
echo "📍 Server: ${VPS_IP}"
echo "🎯 Service: ${SERVICE}"
echo "⚠️  PRODUCTION CONTAINERS WILL NOT BE TOUCHED"
echo "----------------------------------------"

# Safety check - ensure we never touch production
echo "🔒 Safety Check: Verifying production containers are not affected..."
PROD_COUNT=$(ssh_exec "docker ps --format '{{.Names}}' | grep -c 'prod' || echo 0")
echo "✅ Found ${PROD_COUNT} production containers (will remain untouched)"

if [ "$SERVICE" = "all" ]; then
    echo "🔄 Restarting ALL development containers..."
    
    for container in "${DEV_CONTAINERS[@]}"; do
        echo "  🔄 Restarting ${container}..."
        ssh_exec "
            if docker ps --format '{{.Names}}' | grep -q '^${container}$'; then
                docker restart ${container}
                echo '    ✅ ${container} restarted successfully'
            else
                echo '    ⚠️  ${container} not found or not running'
            fi
        "
    done
    
elif [ "$SERVICE" != "all" ]; then
    # Validate it's a development container
    if [[ ! " ${DEV_CONTAINERS[@]} " =~ " ${SERVICE} " ]]; then
        echo "❌ Error: '${SERVICE}' is not a valid development container"
        echo "Valid development containers:"
        printf '  %s\n' "${DEV_CONTAINERS[@]}"
        exit 1
    fi
    
    echo "🔄 Restarting specific service: ${SERVICE}..."
    ssh_exec "
        if docker ps --format '{{.Names}}' | grep -q '^${SERVICE}$'; then
            docker restart ${SERVICE}
            echo '✅ ${SERVICE} restarted successfully'
        else
            echo '❌ ${SERVICE} not found or not running'
            exit 1
        fi
    "
fi

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 15

# Health check
echo "🏥 Performing health checks..."
ssh_exec "
    echo '🌐 Frontend (dev.consulting.sa):'
    curl -s -o /dev/null -w '  Status: %{http_code}\n' http://localhost:3001/api/health || echo '  ❌ Frontend health check failed'
    
    echo '🔧 Backend (development API):'
    curl -s -o /dev/null -w '  Status: %{http_code}\n' http://localhost:8001/health || echo '  ❌ Backend health check failed'
"

# Final status
echo ""
echo "📊 Final container status:"
ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'agentic.*dev'"

echo ""
echo "✅ Development container restart completed - $(date)"
echo "🌐 Access development site at: https://dev.consulting.sa"