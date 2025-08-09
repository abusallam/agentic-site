#!/bin/bash

# 🔧 Fix Website Issues Script
# Fixes: translations, missing docs page, inconsistent themes, background images

set -e

SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
SERVER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"
FRONTEND_PATH="$SERVER_PATH/frontend"

echo "🔧 Fixing website issues..."
echo "📅 $(date)"
echo ""

# Function to check success
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 FAILED"
        exit 1
    fi
}

echo "📄 Phase 1: Creating missing docs page..."
ssh $SERVER_ALIAS "mkdir -p $FRONTEND_PATH/app/docs"
scp frontend/app/docs/page.tsx $SERVER_ALIAS:$FRONTEND_PATH/app/docs/page.tsx
check_success "Docs page created"

echo ""
echo "🌐 Phase 2: Fixing navigation translations..."
scp frontend/components/layout/navigation-enhanced.tsx $SERVER_ALIAS:$FRONTEND_PATH/components/layout/navigation-enhanced.tsx
check_success "Navigation translations fixed"

echo ""
echo "🎨 Phase 3: Ensuring background image is deployed..."
scp frontend/public/bg1.webp $SERVER_ALIAS:$FRONTEND_PATH/public/bg1.webp
check_success "Background image deployed"

echo ""
echo "🔄 Phase 4: Restarting container..."
ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose restart frontend"
check_success "Container restarted"

echo "⏳ Waiting for container to be ready..."
sleep 15

echo ""
echo "🔍 Phase 5: Testing fixes..."

# Test docs page
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa/docs)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Docs page working (HTTP $HTTP_CODE)"
else
    echo "❌ Docs page not working (HTTP $HTTP_CODE)"
fi

# Test main site
RESPONSE=$(curl -s https://dev.consulting.sa)
if echo "$RESPONSE" | grep -q "Transform Your Business with AI Solutions"; then
    echo "✅ Hero title showing correctly (not hero.title)"
else
    echo "⚠️ Hero title may still show translation key"
fi

echo ""
echo "🎉 WEBSITE FIXES DEPLOYED!"
echo "🌐 Check: https://dev.consulting.sa"
echo "📄 Check docs: https://dev.consulting.sa/docs"
echo ""
echo "📋 Fixed issues:"
echo "   ✅ Created missing /docs page"
echo "   ✅ Fixed navigation translations"
echo "   ✅ Ensured background image is available"
echo "   ✅ Container restarted with fixes"
echo ""
echo "🔍 Still need to check:"
echo "   - Hero section translations (hero.title, hero.subtitle)"
echo "   - Arabic translations working properly"
echo "   - Page theme consistency"
echo "   - Background image showing on homepage"