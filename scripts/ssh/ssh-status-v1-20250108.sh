#!/bin/bash
# Script: ssh-status-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: Check container status via SSH with clear production/development separation
# Usage: ./ssh-status-v1-20250108.sh [prod|dev|all]
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version with production/development separation

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
ENVIRONMENT=${1:-"all"}

echo "🔍 Container Status Check v1 - $(date)"
echo "📍 Server: ${VPS_IP}"
echo "🎯 Environment: ${ENVIRONMENT}"
echo "----------------------------------------"

case $ENVIRONMENT in
    "prod"|"production")
        echo "🏭 PRODUCTION CONTAINERS (DO NOT TOUCH)"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | head -1"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | grep -E 'agentic.*prod'"
        ;;
    "dev"|"development")
        echo "🔧 DEVELOPMENT CONTAINERS (SAFE TO MODIFY)"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | head -1"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | grep -E 'agentic.*dev'"
        ;;
    "all"|*)
        echo "🏭 PRODUCTION CONTAINERS (DO NOT TOUCH)"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | head -1"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | grep -E 'agentic.*prod' || echo 'No production containers found'"
        echo ""
        echo "🔧 DEVELOPMENT CONTAINERS (SAFE TO MODIFY)"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | head -1"
        ssh_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' | grep -E 'agentic.*dev' || echo 'No development containers found'"
        ;;
esac

echo ""
echo "📊 SYSTEM RESOURCES"
ssh_exec "df -h / | tail -1 | awk '{print \"💾 Disk Usage: \" \$3 \"/\" \$2 \" (\" \$5 \")\"}'"
ssh_exec "free -h | grep Mem | awk '{print \"🧠 Memory Usage: \" \$3 \"/\" \$2}'"
ssh_exec "uptime | awk '{print \"⏱️  Load Average: \" \$(NF-2) \" \" \$(NF-1) \" \" \$NF}'"

echo ""
echo "🌐 DOMAIN STATUS"
echo "Production: https://consulting.sa"
echo "Development: https://dev.consulting.sa"

echo ""
echo "✅ Status check completed - $(date)"