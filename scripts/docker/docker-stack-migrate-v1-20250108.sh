#!/bin/bash
# Script: docker-stack-migrate-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: Migrate from individual containers to Docker stacks (consulting-prod-stack, consulting-dev-stack)
# Usage: ./docker-stack-migrate-v1-20250108.sh [plan|execute]
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version with stack migration planning

set -e

# Configuration
VPS_IP="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"

# Function to execute SSH commands
ssh_exec() {
    sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${VPS_IP}" "$1"
}

# Parse arguments
ACTION=${1:-"plan"}

echo "📦 Docker Stack Migration v1 - $(date)"
echo "📍 Server: ${VPS_IP}"
echo "🎯 Action: ${ACTION}"
echo "========================================"

if [ "$ACTION" = "plan" ]; then
    echo "📋 MIGRATION PLAN"
    echo "----------------------------------------"
    echo ""
    echo "🎯 OBJECTIVE:"
    echo "  Migrate from individual containers to Docker stacks for better organization"
    echo ""
    echo "📦 PROPOSED STACKS:"
    echo "  • consulting-prod-stack (production services)"
    echo "  • consulting-dev-stack (development services)"
    echo ""
    echo "🏭 PRODUCTION STACK (consulting-prod-stack):"
    echo "  Services:"
    echo "    - frontend-prod (port 3000)"
    echo "    - backend-prod (port 8000)"
    echo "    - redis-prod (port 6379)"
    echo "    - n8n-prod (port 5678)"
    echo ""
    echo "🔧 DEVELOPMENT STACK (consulting-dev-stack):"
    echo "  Services:"
    echo "    - frontend-dev (port 3001)"
    echo "    - backend-dev (port 8001)"
    echo "    - redis-dev (port 6380)"
    echo "    - n8n-dev (port 5679)"
    echo ""
    echo "📋 CURRENT CONTAINER STATUS:"
    ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'agentic'"
    echo ""
    echo "✅ BENEFITS:"
    echo "  • Better service organization"
    echo "  • Easier scaling and management"
    echo "  • Cleaner deployment process"
    echo "  • Better resource allocation"
    echo ""
    echo "⚠️  MIGRATION STEPS:"
    echo "  1. Create stack compose files"
    echo "  2. Test stack deployment in development"
    echo "  3. Migrate development environment first"
    echo "  4. Validate development stack"
    echo "  5. Migrate production environment (with downtime window)"
    echo "  6. Update all deployment scripts"
    echo ""
    echo "🚨 RISKS:"
    echo "  • Brief downtime during production migration"
    echo "  • Need to update all existing scripts"
    echo "  • Potential networking changes"
    echo ""
    echo "💡 RECOMMENDATION:"
    echo "  Execute migration during low-traffic period"
    echo "  Have rollback plan ready"
    echo "  Test thoroughly in development first"
    echo ""
    echo "To execute migration: $0 execute"
    
elif [ "$ACTION" = "execute" ]; then
    echo "🚨 STACK MIGRATION EXECUTION"
    echo "----------------------------------------"
    echo ""
    echo "⚠️  WARNING: This will modify the container architecture!"
    echo "🚨 PRODUCTION SERVICES WILL BE AFFECTED!"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ Migration cancelled by user"
        exit 0
    fi
    
    echo "🚧 This feature is not yet implemented"
    echo "📋 Next steps:"
    echo "  1. Create docker-compose.stack.yml files"
    echo "  2. Test stack deployment"
    echo "  3. Implement migration logic"
    echo ""
    echo "💡 For now, use individual container management"
    
else
    echo "❌ Invalid action: $ACTION"
    echo "Usage: $0 [plan|execute]"
    exit 1
fi

echo ""
echo "✅ Stack migration planning completed - $(date)"