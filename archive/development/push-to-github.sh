#!/bin/bash
# Quick push to GitHub and deploy script
set -e

echo "🚀 Pushing to GitHub and deploying..."

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  You have uncommitted changes. Please commit them first."
    git status
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin $CURRENT_BRANCH

echo "✅ Pushed to GitHub successfully!"
echo ""
echo "🎯 To deploy on VPS, run:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && ./deploy.sh'"
echo ""
echo "Or use the deploy script:"
echo "   ./deploy-to-vps.sh"
