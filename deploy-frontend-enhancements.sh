#!/bin/bash

# Deploy Frontend Enhancements to Dev Container
echo "🚀 Deploying Frontend Enhancements to Development Environment"

# SSH connection details
SSH_HOST="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"

# Container and paths
DEV_CONTAINER="agentic-frontend-dev"
REMOTE_PATH="/opt/docker-apps/development/agentic-site/agentic-site"

echo "📋 Step 1: Stopping dev frontend container..."
sshpass -p "$SSH_PASS" ssh "$SSH_USER@$SSH_HOST" "docker stop $DEV_CONTAINER || true"

echo "📋 Step 2: Removing old dev frontend container..."
sshpass -p "$SSH_PASS" ssh "$SSH_USER@$SSH_HOST" "docker rm $DEV_CONTAINER || true"

echo "📋 Step 3: Creating enhanced components directory on VPS..."
sshpass -p "$SSH_PASS" ssh "$SSH_USER@$SSH_HOST" "mkdir -p $REMOTE_PATH/frontend/components/layout"

echo "📋 Step 4: Uploading enhanced logo component..."
sshpass -p "$SSH_PASS" scp frontend/components/layout/enhanced-logo.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/components/layout/"

echo "📋 Step 5: Uploading universal hero component..."
sshpass -p "$SSH_PASS" scp frontend/components/layout/universal-hero.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/components/layout/"

echo "📋 Step 6: Uploading updated navigation..."
sshpass -p "$SSH_PASS" scp frontend/components/layout/navigation-enhanced.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/components/layout/"

echo "📋 Step 7: Uploading updated pages..."
sshpass -p "$SSH_PASS" scp frontend/app/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/"
sshpass -p "$SSH_PASS" scp frontend/app/services/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/services/"
sshpass -p "$SSH_PASS" scp frontend/app/consulting/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/consulting/"
sshpass -p "$SSH_PASS" scp frontend/app/about/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/about/"
sshpass -p "$SSH_PASS" scp frontend/app/docs/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/docs/"
sshpass -p "$SSH_PASS" scp frontend/app/contact/page.tsx "$SSH_USER@$SSH_HOST:$REMOTE_PATH/frontend/app/contact/"

echo "📋 Step 8: Starting dev frontend container..."
sshpass -p "$SSH_PASS" ssh "$SSH_USER@$SSH_HOST" "cd $REMOTE_PATH && docker-compose up -d agentic-frontend-dev"

echo "📋 Step 9: Waiting for container to be ready..."
sleep 10

echo "📋 Step 10: Checking container status..."
sshpass -p "$SSH_PASS" ssh "$SSH_USER@$SSH_HOST" "docker ps | grep agentic-frontend-dev"

echo "📋 Step 11: Testing dev site..."
curl -I http://217.79.255.54:3001

echo "✅ Frontend enhancements deployed successfully!"
echo "🌐 Test the enhancements at: http://217.79.255.54:3001"
echo "🌐 Or via domain: https://dev.consulting.sa"

echo ""
echo "🎯 Enhancements Deployed:"
echo "  ✅ Enhanced Logo Component (vertical layout with consulting.sa text underneath)"
echo "  ✅ Universal Hero Component (consistent design across all pages)"
echo "  ✅ Updated Navigation (transparent with backdrop blur)"
echo "  ✅ All Pages Updated (home, services, consulting, about, docs, contact)"
echo "  ✅ Multi-language Support (Arabic translations preserved)"
echo ""
echo "🧪 Test the following:"
echo "  1. Logo displays vertically with text underneath"
echo "  2. Hero sections are consistent across all pages"
echo "  3. Navigation becomes transparent on scroll"
echo "  4. Arabic language switching works properly"
echo "  5. All pages load without errors"