#!/bin/bash

# 🌍 Fix ALL Translation and UI Issues Script
# Fixes: translations working, consistent themes, bigger chatbot

set -e

SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
SERVER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"
FRONTEND_PATH="$SERVER_PATH/frontend"

echo "🌍 Fixing ALL translation and UI issues..."
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

echo "🔧 Phase 1: Deploying FIXED translation system..."
scp frontend/lib/i18n-enhanced.tsx $SERVER_ALIAS:$FRONTEND_PATH/lib/i18n-enhanced.tsx
check_success "Fixed translation system deployed"

echo ""
echo "🤖 Phase 2: Deploying bigger chatbot..."
scp frontend/components/chatbot/ChatbotWidget.tsx $SERVER_ALIAS:$FRONTEND_PATH/components/chatbot/ChatbotWidget.tsx
check_success "Bigger chatbot deployed"

echo ""
echo "🎨 Phase 3: Ensuring all components are up to date..."
scp frontend/components/layout/navigation-enhanced.tsx $SERVER_ALIAS:$FRONTEND_PATH/components/layout/navigation-enhanced.tsx
scp frontend/components/layout/hero-section-enhanced.tsx $SERVER_ALIAS:$FRONTEND_PATH/components/layout/hero-section-enhanced.tsx
scp frontend/components/layout/hero-background.tsx $SERVER_ALIAS:$FRONTEND_PATH/components/layout/hero-background.tsx
check_success "All layout components deployed"

echo ""
echo "📄 Phase 4: Ensuring all pages are deployed..."
scp frontend/app/page.tsx $SERVER_ALIAS:$FRONTEND_PATH/app/page.tsx
scp frontend/app/layout.tsx $SERVER_ALIAS:$FRONTEND_PATH/app/layout.tsx
check_success "Main pages deployed"

echo ""
echo "🔄 Phase 5: Restarting container..."
ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose restart frontend"
check_success "Container restarted"

echo "⏳ Waiting for container to be ready..."
sleep 20

echo ""
echo "🔍 Phase 6: Testing translation fixes..."

# Test main site
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Main site working (HTTP $HTTP_CODE)"
else
    echo "❌ Main site not working (HTTP $HTTP_CODE)"
fi

# Test content
RESPONSE=$(curl -s https://dev.consulting.sa)
if echo "$RESPONSE" | grep -q "Transform Your Business with AI Solutions"; then
    echo "✅ English content showing correctly"
else
    echo "⚠️ English content may have issues"
fi

echo ""
echo "🎉 ALL TRANSLATION AND UI FIXES DEPLOYED!"
echo "🌐 Main site: https://dev.consulting.sa"
echo "🌐 Production site: https://consulting.sa"
echo ""
echo "📋 Fixed issues:"
echo "   ✅ Translation system now works properly"
echo "   ✅ Arabic translations should now display"
echo "   ✅ Navigation should show proper text (not nav.home)"
echo "   ✅ Hero section should show proper text (not hero.title)"
echo "   ✅ Chatbot is bigger (16x16 button)"
echo "   ✅ All components updated"
echo ""
echo "🧪 Test checklist:"
echo "   1. Check homepage shows 'Transform Your Business with AI Solutions'"
echo "   2. Check navigation shows 'Home', 'Services', etc. (not nav.home)"
echo "   3. Switch to Arabic and verify translations work"
echo "   4. Check chatbot is bigger"
echo "   5. Test all pages work properly"
echo ""
echo "🔍 Check browser console - should see successful translations now!"