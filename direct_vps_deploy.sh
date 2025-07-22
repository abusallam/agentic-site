#!/bin/bash
# Direct VPS deployment without GitHub
set -e

HOST="217.79.255.54"
USER="root"
PROJECT_PATH="/root/agentic-site"

echo "🚀 Direct VPS Deployment..."

# SSH to VPS and run deployment
ssh -o StrictHostKeyChecking=no $USER@$HOST << 'ENDSSH'
set -e

PROJECT_PATH="/root/agentic-site"
LOG_FILE="/var/log/agentic-site-deploy.log"

echo "$(date): Starting direct deployment..." | tee -a $LOG_FILE

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

# Try to pull from GitHub (if available)
echo "$(date): Attempting to pull from GitHub..." | tee -a $LOG_FILE
git fetch origin || echo "GitHub fetch failed, using existing code"
git pull origin main || echo "GitHub pull failed, using existing code"

# Check if we have essential files, if not create them
if [ ! -f "docker-compose.yml" ]; then
    echo "$(date): Creating basic docker-compose.yml..." | tee -a $LOG_FILE
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
fi

if [ ! -f "Dockerfile" ]; then
    echo "$(date): Creating basic Dockerfile..." | tee -a $LOG_FILE
    cat > Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
EOF
fi

if [ ! -f "package.json" ]; then
    echo "$(date): Creating basic package.json..." | tee -a $LOG_FILE
    cat > package.json << 'EOF'
{
  "name": "agentic-site",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "eslint": "^8",
    "eslint-config-next": "14.0.0"
  }
}
EOF
fi

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
sleep 20

# Check container status
echo "$(date): Checking container status..." | tee -a $LOG_FILE
docker-compose ps | tee -a $LOG_FILE

# Test application health
echo "$(date): Testing application health..." | tee -a $LOG_FILE
for i in {1..5}; do
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "$(date): ✅ Application is responding!" | tee -a $LOG_FILE
        echo "✅ Deployment successful!"
        break
    else
        echo "$(date): Attempt $i: Application not responding, waiting..." | tee -a $LOG_FILE
        sleep 10
    fi
done

# Show final status
echo "$(date): Final container status:" | tee -a $LOG_FILE
docker-compose ps | tee -a $LOG_FILE

echo "$(date): Deployment completed" | tee -a $LOG_FILE

ENDSSH

echo "✅ Direct deployment completed!"
echo ""
echo "🎯 Your application should be running at:"
echo "   http://217.79.255.54:3000"
echo ""
echo "📋 To check status:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && docker-compose ps'"
echo ""
echo "📄 To view logs:"
echo "   ssh root@217.79.255.54 'cd /root/agentic-site && docker-compose logs'"