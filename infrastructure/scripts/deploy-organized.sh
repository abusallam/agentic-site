#!/bin/bash
# Deployment script for organized project structure
# Updated to work with frontend/ and backend/ directories

set -e

# Configuration
PROJECT_NAME="agentic-ai-platform"
VPS_HOST="217.79.255.54"
VPS_USER="root"
VPS_PASSWORD="xxXNCpx9Cz"
DEPLOY_PATH="/opt/agentic-platform"

echo "🚀 Deploying Organized Agentic AI Platform"
echo "=" * 50

# Function to run commands on VPS
run_on_vps() {
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$1"
}

# Function to copy files to VPS
copy_to_vps() {
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" "$VPS_USER@$VPS_HOST:$2"
}

# 1. Prepare deployment package
echo "📦 Preparing deployment package..."
rm -rf dist/
mkdir -p dist/

# Copy organized structure
cp -r frontend/ dist/
cp -r backend/ dist/
cp -r infrastructure/ dist/
cp -r docs/ dist/
cp -r tests/ dist/
cp -r tools/ dist/

# Copy root configuration files
cp .env.example dist/
cp package.json dist/
cp workspace.json dist/
cp README.md dist/
cp LICENSE dist/
cp .gitignore dist/

echo "✅ Deployment package prepared"

# 2. Create deployment archive
echo "📦 Creating deployment archive..."
tar -czf agentic-platform-organized.tar.gz -C dist .
echo "✅ Archive created: agentic-platform-organized.tar.gz"

# 3. Upload to VPS
echo "📤 Uploading to VPS..."
copy_to_vps "agentic-platform-organized.tar.gz" "/tmp/"

# 4. Deploy on VPS
echo "🚀 Deploying on VPS..."
run_on_vps "
    set -e
    
    # Create deployment directory
    mkdir -p $DEPLOY_PATH
    cd $DEPLOY_PATH
    
    # Backup current deployment
    if [ -d 'current' ]; then
        mv current backup-\$(date +%Y%m%d_%H%M%S)
    fi
    
    # Extract new deployment
    mkdir -p current
    cd current
    tar -xzf /tmp/agentic-platform-organized.tar.gz
    
    # Set up environment
    if [ ! -f .env ]; then
        cp .env.example .env
        echo '⚠️  Please configure .env file with your settings'
    fi
    
    # Install frontend dependencies
    cd frontend
    npm install
    npm run build
    cd ..
    
    # Set up backend
    cd backend
    python -m pip install -r agent/requirements.txt
    cd ..
    
    # Start services using Docker
    cd infrastructure/docker
    docker-compose -f docker-compose.production.yml up -d
    
    echo '✅ Deployment completed successfully!'
"

# 5. Verify deployment
echo "🔍 Verifying deployment..."
sleep 10

# Check frontend
if curl -f -s "http://$VPS_HOST:3000/api/health" > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend health check failed"
fi

# Check backend
if curl -f -s "http://$VPS_HOST:8000/health" > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend health check failed"
fi

# Cleanup
rm -f agentic-platform-organized.tar.gz
rm -rf dist/

echo ""
echo "🎉 Deployment completed!"
echo "Frontend: http://$VPS_HOST:3000"
echo "Backend: http://$VPS_HOST:8000"
echo "SSH: ssh $VPS_USER@$VPS_HOST"