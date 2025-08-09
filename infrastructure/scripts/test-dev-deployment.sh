#!/bin/bash

# 🔍 Quick Development Deployment Test Script
# Run this to quickly diagnose deployment issues

SERVER_ALIAS="agentic-fixed-217-79-255-54-development"
SERVER_PATH="/opt/docker-apps/development/agentic-site/agentic-site"

echo "🔍 Quick Deployment Diagnostic Test"
echo "📅 $(date)"
echo "🎯 Target: https://dev.consulting.sa"
echo ""

# Test 1: Server Connection
echo "1️⃣ Testing server connection..."
if ssh $SERVER_ALIAS 'echo "Connected"' > /dev/null 2>&1; then
    echo "✅ Server connection: OK"
else
    echo "❌ Server connection: FAILED"
    exit 1
fi

# Test 2: Container Status
echo ""
echo "2️⃣ Checking container status..."
CONTAINER_STATUS=$(ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose ps frontend --format '{{.Status}}'")
echo "📊 Container status: $CONTAINER_STATUS"

if [[ $CONTAINER_STATUS == *"healthy"* ]]; then
    echo "✅ Container: HEALTHY"
elif [[ $CONTAINER_STATUS == *"unhealthy"* ]]; then
    echo "❌ Container: UNHEALTHY"
    echo "📋 Recent logs:"
    ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose logs frontend --tail=10"
else
    echo "⚠️ Container: UNKNOWN STATUS"
fi

# Test 3: Critical Files
echo ""
echo "3️⃣ Checking critical files..."
FILES_TO_CHECK=(
    "lib/i18n-enhanced.tsx"
    "tailwind.config.ts"
    "app/globals.css"
    "package.json"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if ssh $SERVER_ALIAS "ls $SERVER_PATH/frontend/$file" > /dev/null 2>&1; then
        echo "✅ $file: EXISTS"
    else
        echo "❌ $file: MISSING"
    fi
done

# Test 4: HTTP Response
echo ""
echo "4️⃣ Testing HTTP response..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa)
echo "🌐 HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Site: RESPONDING"
else
    echo "❌ Site: NOT RESPONDING"
fi

# Test 5: Content Check
echo ""
echo "5️⃣ Testing site content..."
RESPONSE=$(curl -s https://dev.consulting.sa)
if echo "$RESPONSE" | grep -q "Next.js"; then
    echo "✅ Next.js: DETECTED"
else
    echo "❌ Next.js: NOT DETECTED"
fi

if echo "$RESPONSE" | grep -q "development environment"; then
    echo "✅ Development environment: DETECTED"
else
    echo "⚠️ Development environment: NOT DETECTED"
fi

# Test 6: Recent Logs
echo ""
echo "6️⃣ Recent container logs..."
echo "📋 Last 5 log entries:"
ssh $SERVER_ALIAS "cd $SERVER_PATH && docker-compose logs frontend --tail=5"

# Summary
echo ""
echo "📊 DIAGNOSTIC SUMMARY"
echo "===================="
echo "🌐 Site URL: https://dev.consulting.sa"
echo "🐳 Container: $CONTAINER_STATUS"
echo "🔗 HTTP: $HTTP_CODE"
echo "📅 Checked: $(date)"

if [ "$HTTP_CODE" = "200" ] && [[ $CONTAINER_STATUS == *"healthy"* ]]; then
    echo "🎉 STATUS: ALL GOOD!"
else
    echo "🚨 STATUS: ISSUES DETECTED"
    echo "📖 Check: DEPLOYMENT_TROUBLESHOOTING_GUIDE.md"
fi