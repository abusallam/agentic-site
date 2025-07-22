#!/bin/bash
# Deploy to VPS script
set -e

HOST="217.79.255.54"
USER="root"
PROJECT_PATH="/root/agentic-site"

echo "🚀 Deploying to VPS..."

# First, let's push our latest changes to GitHub
echo "📤 Pushing latest changes to GitHub..."
git add .
git commit -m "Deploy: $(date)" || echo "No changes to commit"
git push origin main

echo "📡 Connecting to VPS and deploying..."

# SSH to VPS and run deployment
ssh -o StrictHostKeyChecking=no $USER@$HOST << 'ENDSSH'
set -e

PROJECT_PATH="/root/agentic-site"
LOG_FILE="/var/log/agentic-site-deploy.log"

echo "$(date): Starting deployment..." | tee -a $LOG_FILE

# Navigate to project directory or create it
if [ ! -d "$PROJECT_PATH" ]; then
    echo "$(date): Creating project directory..." | tee -a $LOG_FILE
    mkdir -p $PROJECT_PATH
    cd $PROJECT_PATH
    git init
    git remote add origin https://github.com/abusallam/agentic-site.git
else
    cd $PROJECT_PATH
fi

# Fetch and pull latest changes
echo "$(date): Fetching from GitHub..." | tee -a $LOG_FILE
git fetch origin || echo "Fetch failed, continuing..."

echo "$(date): Pulling latest changes..." | tee -a $LOG_FILE
git pull origin main || echo "Pull failed, continuing..."

# Check Docker status
echo "$(date): Checking Docker..." | tee -a $LOG_FILE
docker --version | tee -a $LOG_FILE
docker-compose --version | tee -a $LOG_FILE

# Stop existing containers
echo "$(date): Stopping existing containers..." | tee -a $LOG_FILE
docker-compose down || echo "No containers to stop"

# Clean up
echo "$(date): Cleaning up..." | tee -a $LOG_FILE
docker system prune -f || echo "Cleanup failed"

# Build and start containers
echo "$(date): Building and starting containers..." | tee -a $LOG_FILE
docker-compose up -d --build

# Wait for containers to start
echo "$(date): Waiting for containers to start..." | tee -a $LOG_FILE
sleep 15

# Check container status
echo "$(date): Checking container status..." | tee -a $LOG_FILE
docker-compose ps | tee -a $LOG_FILE

# Test application health
echo "$(date): Testing application health..." | tee -a $LOG_FILE
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "$(date): ✅ Application is responding!" | tee -a $LOG_FILE
    echo "✅ Deployment successful!"
else
    echo "$(date): ⚠️  Application may not be responding on port 3000" | tee -a $LOG_FILE
    echo "⚠️  Application may not be responding, checking logs..."
    docker-compose logs --tail=10
fi

echo "$(date): Deployment completed" | tee -a $LOG_FILE

ENDSSH

echo "✅ Deployment completed!"
echo ""
echo "🎯 Your application should be running at:"
echo "   http://217.79.255.54:3000"
echo ""
echo "📋 To check status:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && docker-compose ps'"
echo ""
echo "📄 To view logs:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && docker-compose logs'"