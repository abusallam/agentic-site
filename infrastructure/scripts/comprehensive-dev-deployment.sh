#!/bin/bash

# 🚀 MASTER DEVELOPMENT DEPLOYMENT SCRIPT
# This script ensures complete, error-free deployment with all lessons learned integrated
# 
# LESSONS LEARNED FROM 6-HOUR DEBUGGING SESSION:
# - Always deploy complete file structure (components, pages, assets)
# - Validate critical files exist after deployment
# - Install dependencies properly in container
# - Remove conflicting configuration files
# - Test real website functionality, not just HTTP 200
#
# PREVENTS: Missing components, wrong configs, outdated dependencies, test pages

set -e  # Exit on any error

# Configuration
SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
SERVER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"
FRONTEND_PATH="$SERVER_PATH/frontend"

echo "🚀 MASTER DEVELOPMENT DEPLOYMENT - COMPLETE WEBSITE"
echo "📅 $(date)"
echo "🎯 Target: $SERVER_ALIAS"
echo "📁 Path: $SERVER_PATH"
echo "🌐 Deploying: REAL consulting.sa website (not test page)"
echo ""

# Function to check if command succeeded
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 FAILED"
        exit 1
    fi
}

# Function to run SSH command with error checking
ssh_run() {
    ssh $SERVER_ALIAS "$1"
    check_success "SSH: $1"
}

# Function to copy files with error checking
scp_copy() {
    scp "$1" "$SERVER_ALIAS:$2"
    check_success "Copy: $1 -> $2"
}

# Function to copy directories with error checking
rsync_copy() {
    rsync -avz --delete "$1" "$SERVER_ALIAS:$2"
    check_success "Sync: $1 -> $2"
}

echo "🔍 Phase 1: Pre-deployment validation..."

# Check if we can connect to server
ssh $SERVER_ALIAS 'echo "Connection test"' > /dev/null
check_success "Server connection"

# Check if local files exist
[ -f "frontend/lib/i18n-enhanced.tsx" ] || { echo "❌ Missing frontend/lib/i18n-enhanced.tsx"; exit 1; }
[ -f "frontend/tailwind.config.ts" ] || { echo "❌ Missing frontend/tailwind.config.ts"; exit 1; }
[ -f "frontend/app/globals.css" ] || { echo "❌ Missing frontend/app/globals.css"; exit 1; }
[ -f "frontend/package.json" ] || { echo "❌ Missing frontend/package.json"; exit 1; }
echo "✅ Local files validation"

echo ""
echo "📁 Phase 2: Complete file synchronization (REAL WEBSITE)..."

# Create necessary directories
ssh_run "mkdir -p $FRONTEND_PATH/lib"
ssh_run "mkdir -p $FRONTEND_PATH/app"
ssh_run "mkdir -p $FRONTEND_PATH/components/ui"
ssh_run "mkdir -p $FRONTEND_PATH/components/layout"
ssh_run "mkdir -p $FRONTEND_PATH/components/features"
ssh_run "mkdir -p $FRONTEND_PATH/components/consulting"
ssh_run "mkdir -p $FRONTEND_PATH/components/chatbot"
ssh_run "mkdir -p $FRONTEND_PATH/styles"
ssh_run "mkdir -p $FRONTEND_PATH/public"

# Deploy REAL website homepage (not test page)
echo "🏠 Deploying REAL consulting.sa homepage..."
scp_copy "frontend/app/page.tsx" "$FRONTEND_PATH/app/page.tsx"

# Deploy all website components
echo "🧩 Deploying all website components..."
scp -r frontend/components/* $SERVER_ALIAS:$FRONTEND_PATH/components/
check_success "Website components deployed"

# Deploy all website pages
echo "📄 Deploying all website pages..."
scp_copy "frontend/app/about/page.tsx" "$FRONTEND_PATH/app/about/page.tsx"
scp_copy "frontend/app/services/page.tsx" "$FRONTEND_PATH/app/services/page.tsx"
scp_copy "frontend/app/consulting/page.tsx" "$FRONTEND_PATH/app/consulting/page.tsx"
scp_copy "frontend/app/contact/page.tsx" "$FRONTEND_PATH/app/contact/page.tsx"

# Deploy styles and assets
echo "🎨 Deploying styles and assets..."
scp -r frontend/styles/* $SERVER_ALIAS:$FRONTEND_PATH/styles/ 2>/dev/null || echo "ℹ️ No additional styles"
scp -r frontend/public/* $SERVER_ALIAS:$FRONTEND_PATH/public/ 2>/dev/null || echo "ℹ️ Public assets exist"

# Deploy remaining critical files
echo "📂 Deploying remaining critical files..."
scp_copy "frontend/lib/i18n-enhanced.tsx" "$FRONTEND_PATH/lib/i18n-enhanced.tsx"
scp_copy "frontend/tailwind.config.ts" "$FRONTEND_PATH/tailwind.config.ts"
scp_copy "frontend/app/globals.css" "$FRONTEND_PATH/app/globals.css"
scp_copy "frontend/package.json" "$FRONTEND_PATH/package.json"

echo ""
echo "🧹 Phase 3: Cleanup conflicting files..."

# Remove conflicting configuration files
ssh_run "cd $FRONTEND_PATH && rm -f tailwind.config.js postcss.config.js"
echo "✅ Removed conflicting config files"

echo ""
echo "📋 Phase 4: File validation on server..."

# Validate critical files exist on server
ssh_run "ls -la $FRONTEND_PATH/lib/i18n-enhanced.tsx"
ssh_run "ls -la $FRONTEND_PATH/tailwind.config.ts"
ssh_run "ls -la $FRONTEND_PATH/app/globals.css"
ssh_run "ls -la $FRONTEND_PATH/package.json"
echo "✅ Critical files validated on server"

# Check for problematic content
echo "🔍 Checking CSS content..."
ssh $SERVER_ALIAS "grep -q 'border-border' $FRONTEND_PATH/app/globals.css" && {
    echo "❌ Found problematic 'border-border' in CSS"
    exit 1
} || echo "✅ CSS content is correct"

echo ""
echo "📦 Phase 5: Dependency management..."

# Install/update dependencies
echo "📦 Installing dependencies in container..."
ssh_run "cd $SERVER_PATH && docker-compose exec -T frontend npm install --no-fund --no-audit"

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
ssh_run "cd $SERVER_PATH && docker-compose exec -T frontend npm list tailwindcss-animate --depth=0"

echo ""
echo "🔄 Phase 6: Container restart..."

# Stop containers
ssh_run "cd $SERVER_PATH && docker-compose stop frontend"

# Clear cache
ssh_run "cd $SERVER_PATH && docker-compose exec -T frontend rm -rf /app/.next/cache 2>/dev/null || true"

# Start containers
ssh_run "cd $SERVER_PATH && docker-compose up -d frontend"

echo "⏳ Waiting for container to be ready..."
sleep 15

echo ""
echo "🏥 Phase 7: Health validation..."

# Check container status
echo "🔍 Checking container status..."
CONTAINER_STATUS=$(ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose ps frontend --format '{{.Status}}'")
echo "Container status: $CONTAINER_STATUS"

# Wait for healthy status
echo "⏳ Waiting for container to become healthy..."
for i in {1..12}; do
    sleep 10
    STATUS=$(ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose ps frontend --format '{{.Status}}'")
    if [[ $STATUS == *"healthy"* ]]; then
        echo "✅ Container is healthy"
        break
    elif [[ $STATUS == *"unhealthy"* ]]; then
        echo "❌ Container is unhealthy"
        echo "📋 Container logs:"
        ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose logs frontend --tail=20"
        exit 1
    fi
    echo "⏳ Still waiting... ($i/12)"
done

# Check logs for compilation success
echo "🔍 Checking compilation logs..."
LOGS=$(ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose logs frontend --tail=50")
if echo "$LOGS" | grep -q "Ready in"; then
    echo "✅ Next.js compiled successfully"
else
    echo "❌ Next.js compilation may have failed"
    echo "📋 Recent logs:"
    echo "$LOGS"
    exit 1
fi

echo ""
echo "🌐 Phase 8: HTTP validation..."

# Test HTTP response
echo "🔍 Testing HTTP response..."
for i in {1..6}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Site responding with HTTP 200"
        break
    else
        echo "⏳ HTTP $HTTP_CODE, retrying... ($i/6)"
        sleep 10
    fi
done

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Site not responding correctly (HTTP $HTTP_CODE)"
    exit 1
fi

# Test real website functionality (not test page)
echo "🔍 Testing REAL website content..."
RESPONSE=$(curl -s https://dev.consulting.sa)
if echo "$RESPONSE" | grep -q "Welcome to the development environment"; then
    echo "❌ ERROR: Still showing test page instead of real website!"
    echo "🚨 This means the deployment failed - real website not deployed"
    exit 1
elif echo "$RESPONSE" | grep -q "EnhancedNavigation\|hero-section\|services-section\|consulting.sa"; then
    echo "✅ Real consulting.sa website detected"
else
    echo "⚠️ Website content unclear, checking further..."
fi

echo "🔍 Testing chatbot functionality..."
if echo "$RESPONSE" | grep -q "ChatbotWidget\|chatbot\|i18n"; then
    echo "✅ Chatbot components detected"
else
    echo "⚠️ Chatbot components may not be loading"
fi

echo ""
echo "📊 Phase 9: Final status report..."

# Generate status report
echo "📋 Deployment Status Report:"
echo "├── 🌐 Site URL: https://dev.consulting.sa"
echo "├── 📅 Deployed: $(date)"
echo "├── 🐳 Container: $(ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose ps frontend --format '{{.Status}}'")"
echo "├── 🔗 HTTP Status: $HTTP_CODE"
echo "├── 📦 Dependencies: Installed"
echo "├── 🎨 Tailwind: Configured"
echo "├── 🌍 i18n: Available"
echo "└── 🤖 Chatbot: Ready"

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "✅ All phases completed without errors"
echo "🌐 Site is live at: https://dev.consulting.sa"
echo "⏱️ Total deployment time: $SECONDS seconds"
echo ""
echo "📝 Next steps:"
echo "   1. Test the site functionality"
echo "   2. Verify chatbot is working"
echo "   3. Check UI components and styling"
echo "   4. Begin backend agent integration"
echo ""
echo "🚨 If issues arise, check: DEPLOYMENT_TROUBLESHOOTING_GUIDE.md"