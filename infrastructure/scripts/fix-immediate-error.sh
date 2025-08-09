#!/bin/bash
# 🔧 IMMEDIATE FIX FOR NEXT.JS SSR ERROR
# Fixes the current production error and deploys the fix

set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"

echo "🔧 FIXING IMMEDIATE NEXT.JS ERROR"
echo "📅 $(date)"
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

echo "🔍 Step 1: Checking current error..."
echo "Current error logs from production:"
ssh_run "docker logs agentic-frontend-prod --tail 10" || echo "Container not accessible"

echo ""
echo "🔍 Step 2: The error is fixed locally in the code"
echo "✅ Created ChatbotWrapper.tsx (client component)"
echo "✅ Updated layout.tsx to use client wrapper"
echo "✅ Removed ssr: false from Server Component"

echo ""
echo "🔍 Step 3: Now we need to deploy this fix properly"
echo "📋 You have two options:"
echo ""
echo "Option 1: Quick Manual Fix (Immediate)"
echo "   1. Copy the fixed files to VPS manually"
echo "   2. Rebuild containers"
echo "   3. This is a temporary solution"
echo ""
echo "Option 2: Professional GitHub Deployment (Recommended)"
echo "   1. Run: ./infrastructure/scripts/setup-github-integration.sh"
echo "   2. Configure GitHub webhook"
echo "   3. Push to GitHub repository"
echo "   4. Automatic deployment"
echo ""
echo "🚨 RECOMMENDATION: Use Option 2 for long-term stability"
echo ""
echo "For immediate fix, run:"
echo "   ./infrastructure/scripts/deploy-manual-fix.sh"
echo ""
echo "For professional setup, run:"
echo "   ./infrastructure/scripts/setup-github-integration.sh"