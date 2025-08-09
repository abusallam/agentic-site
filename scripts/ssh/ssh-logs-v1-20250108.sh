#!/bin/bash
# Script: ssh-logs-v1-20250108.sh
# Version: v1
# Date: 2025-01-08
# Purpose: View container logs via SSH with environment filtering
# Usage: ./ssh-logs-v1-20250108.sh [container-name] [lines]
# Author: AI Assistant
# Last Modified: 2025-01-08
#
# Changelog:
# v1 - Initial version with container log viewing

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
CONTAINER=${1:-""}
LINES=${2:-"50"}

echo "📋 Container Logs Viewer v1 - $(date)"
echo "📍 Server: ${VPS_IP}"
echo "----------------------------------------"

if [ -z "$CONTAINER" ]; then
    echo "Available containers:"
    echo ""
    echo "🏭 PRODUCTION (DO NOT MODIFY):"
    ssh_exec "docker ps --format '  {{.Names}}' | grep -E 'agentic.*prod' || echo '  No production containers found'"
    echo ""
    echo "🔧 DEVELOPMENT (SAFE TO VIEW):"
    ssh_exec "docker ps --format '  {{.Names}}' | grep -E 'agentic.*dev' || echo '  No development containers found'"
    echo ""
    echo "Usage: $0 [container-name] [lines]"
    echo "Example: $0 agentic-frontend-dev 100"
    exit 0
fi

# Validate container exists
if ! ssh_exec "docker ps --format '{{.Names}}' | grep -q '^${CONTAINER}$'"; then
    echo "❌ Container '${CONTAINER}' not found or not running"
    exit 1
fi

# Check if it's a production container
if echo "$CONTAINER" | grep -q "prod"; then
    echo "⚠️  WARNING: This is a PRODUCTION container!"
    echo "🚨 Viewing logs only - DO NOT RESTART OR MODIFY"
    echo ""
fi

echo "📋 Showing last ${LINES} lines from ${CONTAINER}:"
echo "----------------------------------------"

ssh_exec "docker logs --tail=${LINES} --timestamps ${CONTAINER}"

echo ""
echo "✅ Log viewing completed - $(date)"
echo "💡 To follow logs in real-time, use: docker logs -f ${CONTAINER}"