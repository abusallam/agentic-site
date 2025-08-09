#!/bin/bash
# Script: health-check-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: Comprehensive health check for both production and development environments
# Usage: ./health-check-v1-20250108.sh [prod|dev|all]
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version with comprehensive health monitoring

set -e

# Configuration
VPS_IP="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"

# Function to execute SSH commands
ssh_exec() {
    sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${VPS_IP}" "$1"
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo "  ✅ $name: HTTP $response"
        return 0
    else
        echo "  ❌ $name: HTTP $response (expected $expected_code)"
        return 1
    fi
}

# Parse arguments
ENVIRONMENT=${1:-"all"}

echo "🏥 Health Check v1 - $(date)"
echo "📍 Server: ${VPS_IP}"
echo "🎯 Environment: ${ENVIRONMENT}"
echo "========================================"

# System Health
echo ""
echo "🖥️  SYSTEM HEALTH"
echo "----------------------------------------"
ssh_exec "
    echo '💾 Disk Usage:'
    df -h / | tail -1 | awk '{print \"  Root: \" \$3 \"/\" \$2 \" (\" \$5 \")\"}'
    
    echo '🧠 Memory Usage:'
    free -h | grep Mem | awk '{print \"  RAM: \" \$3 \"/\" \$2 \" (\" int(\$3/\$2*100) \"%)\"}'
    
    echo '⚡ CPU Load:'
    uptime | awk '{print \"  Load: \" \$(NF-2) \" \" \$(NF-1) \" \" \$NF}'
    
    echo '🐳 Docker Status:'
    systemctl is-active docker | awk '{print \"  Docker: \" \$1}'
    
    echo '🌐 Nginx Status:'
    systemctl is-active nginx | awk '{print \"  Nginx: \" \$1}'
"

# Container Health
if [ "$ENVIRONMENT" = "all" ] || [ "$ENVIRONMENT" = "prod" ] || [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "🏭 PRODUCTION CONTAINERS"
    echo "----------------------------------------"
    ssh_exec "
        echo '📊 Container Status:'
        docker ps --format '  {{.Names}}: {{.Status}}' | grep -E 'agentic.*prod' || echo '  No production containers found'
        
        echo '💾 Container Resources:'
        docker stats --no-stream --format '  {{.Name}}: CPU {{.CPUPerc}} | MEM {{.MemUsage}}' | grep -E 'agentic.*prod' || echo '  No production containers found'
    "
    
    echo ""
    echo "🌐 Production Endpoints:"
    check_endpoint "https://consulting.sa" "Main Website"
    check_endpoint "https://consulting.sa/api/health" "Frontend API"
    check_endpoint "http://${VPS_IP}:8000/health" "Backend API"
fi

if [ "$ENVIRONMENT" = "all" ] || [ "$ENVIRONMENT" = "dev" ] || [ "$ENVIRONMENT" = "development" ]; then
    echo ""
    echo "🔧 DEVELOPMENT CONTAINERS"
    echo "----------------------------------------"
    ssh_exec "
        echo '📊 Container Status:'
        docker ps --format '  {{.Names}}: {{.Status}}' | grep -E 'agentic.*dev' || echo '  No development containers found'
        
        echo '💾 Container Resources:'
        docker stats --no-stream --format '  {{.Name}}: CPU {{.CPUPerc}} | MEM {{.MemUsage}}' | grep -E 'agentic.*dev' || echo '  No development containers found'
    "
    
    echo ""
    echo "🌐 Development Endpoints:"
    check_endpoint "https://dev.consulting.sa" "Dev Website"
    check_endpoint "https://dev.consulting.sa/api/health" "Dev Frontend API"
    check_endpoint "http://${VPS_IP}:8001/health" "Dev Backend API"
fi

# SSL Certificate Check
echo ""
echo "🔒 SSL CERTIFICATES"
echo "----------------------------------------"
echo "🏭 Production (consulting.sa):"
openssl s_client -connect consulting.sa:443 -servername consulting.sa </dev/null 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | sed 's/^/  /' || echo "  ❌ SSL check failed"

echo "🔧 Development (dev.consulting.sa):"
openssl s_client -connect dev.consulting.sa:443 -servername dev.consulting.sa </dev/null 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | sed 's/^/  /' || echo "  ❌ SSL check failed"

# Network Connectivity
echo ""
echo "🌐 NETWORK CONNECTIVITY"
echo "----------------------------------------"
ssh_exec "
    echo '📡 External Connectivity:'
    ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo '  ✅ Internet: Connected' || echo '  ❌ Internet: Failed'
    
    echo '🔍 DNS Resolution:'
    nslookup consulting.sa >/dev/null 2>&1 && echo '  ✅ DNS: Working' || echo '  ❌ DNS: Failed'
"

# Summary
echo ""
echo "📋 HEALTH CHECK SUMMARY"
echo "========================================"
echo "✅ Health check completed - $(date)"
echo "📊 For detailed monitoring, check Grafana dashboard"
echo "🚨 For alerts, check Prometheus alerts"
echo ""
echo "🌐 Access URLs:"
echo "  Production: https://consulting.sa"
echo "  Development: https://dev.consulting.sa"