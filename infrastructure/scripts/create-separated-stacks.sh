#!/bin/bash

# 🔧 SEPARATED DOCKER STACKS CREATION SCRIPT
# Creates properly isolated production and development stacks
# 
# FIXES:
# - Separate Docker volumes for prod/dev
# - No shared filesystem between environments
# - Proper container isolation
# - Independent deployments

set -e

# Configuration
SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"
PROD_STACK_PATH="/opt/docker-stacks/production"
DEV_STACK_PATH="/opt/docker-stacks/development"

echo "🔧 CREATING SEPARATED DOCKER STACKS"
echo "📅 $(date)"
echo "🎯 Target: $SERVER_IP"
echo "📁 Production Stack: $PROD_STACK_PATH"
echo "📁 Development Stack: $DEV_STACK_PATH"
echo ""

# Function to run SSH command
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

echo "🔍 Phase 1: Stopping current containers safely..."

# Stop current containers
ssh_run "docker stop agentic-frontend-prod agentic-frontend-dev agentic-backend-prod agentic-backend-dev agentic-redis-prod agentic-redis-dev agentic-n8n-prod agentic-n8n-dev 2>/dev/null || true"

# Remove current containers
ssh_run "docker rm agentic-frontend-prod agentic-frontend-dev agentic-backend-prod agentic-backend-dev agentic-redis-prod agentic-redis-dev agentic-n8n-prod agentic-n8n-dev 2>/dev/null || true"

echo ""
echo "📁 Phase 2: Creating separated directory structure..."

# Create separated stack directories
ssh_run "mkdir -p $PROD_STACK_PATH/{frontend,backend,config,data,logs}"
ssh_run "mkdir -p $DEV_STACK_PATH/{frontend,backend,config,data,logs}"

# Create Docker volumes
ssh_run "docker volume create agentic-prod-frontend-data"
ssh_run "docker volume create agentic-prod-backend-data"
ssh_run "docker volume create agentic-prod-redis-data"
ssh_run "docker volume create agentic-prod-n8n-data"

ssh_run "docker volume create agentic-dev-frontend-data"
ssh_run "docker volume create agentic-dev-backend-data"
ssh_run "docker volume create agentic-dev-redis-data"
ssh_run "docker volume create agentic-dev-n8n-data"

echo ""
echo "📋 Phase 3: Creating production docker-compose..."

# Create production docker-compose
cat > /tmp/docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  # Production Frontend
  frontend-prod:
    image: node:20-alpine
    container_name: agentic-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://consulting.sa/api
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    working_dir: /app
    volumes:
      - agentic-prod-frontend-data:/app
      - ./frontend:/app-source:ro
    command: sh -c "cp -r /app-source/* /app/ && npm install && npm run build && npm start"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-prod

  # Production Backend
  backend-prod:
    image: python:3.11-slim
    container_name: agentic-backend-prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    working_dir: /app
    volumes:
      - agentic-prod-backend-data:/app
      - ./backend:/app-source:ro
    command: sh -c "cp -r /app-source/* /app/ && pip install -r requirements.txt && python main.py"
    restart: unless-stopped
    networks:
      - agentic-prod

  # Production Redis
  redis-prod:
    image: redis:7-alpine
    container_name: agentic-redis-prod
    ports:
      - "6379:6379"
    volumes:
      - agentic-prod-redis-data:/data
    restart: unless-stopped
    networks:
      - agentic-prod

  # Production n8n
  n8n-prod:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-prod
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=agentic2025
      - WEBHOOK_URL=https://consulting.sa/
      - GENERIC_TIMEZONE=Asia/Riyadh
    volumes:
      - agentic-prod-n8n-data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-prod

networks:
  agentic-prod:
    driver: bridge

volumes:
  agentic-prod-frontend-data:
    external: true
  agentic-prod-backend-data:
    external: true
  agentic-prod-redis-data:
    external: true
  agentic-prod-n8n-data:
    external: true
EOF

# Copy production compose to server
sshpass -p "$SERVER_PASS" scp /tmp/docker-compose.production.yml "$SERVER_USER@$SERVER_IP:$PROD_STACK_PATH/docker-compose.yml"
echo "✅ Production docker-compose created"

echo ""
echo "📋 Phase 4: Creating development docker-compose..."

# Create development docker-compose
cat > /tmp/docker-compose.development.yml << 'EOF'
version: '3.8'

services:
  # Development Frontend
  frontend-dev:
    image: node:20-alpine
    container_name: agentic-frontend-dev
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    working_dir: /app
    volumes:
      - agentic-dev-frontend-data:/app
      - ./frontend:/app-source:ro
    command: sh -c "cp -r /app-source/* /app/ && npm install && npm run dev"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-dev

  # Development Backend
  backend-dev:
    image: python:3.11-slim
    container_name: agentic-backend-dev
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=development
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    working_dir: /app
    volumes:
      - agentic-dev-backend-data:/app
      - ./backend:/app-source:ro
    command: sh -c "cp -r /app-source/* /app/ && pip install -r requirements.txt && python main.py"
    restart: unless-stopped
    networks:
      - agentic-dev

  # Development Redis
  redis-dev:
    image: redis:7-alpine
    container_name: agentic-redis-dev
    ports:
      - "6380:6379"
    volumes:
      - agentic-dev-redis-data:/data
    restart: unless-stopped
    networks:
      - agentic-dev

  # Development n8n
  n8n-dev:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-dev
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=agentic2025
      - WEBHOOK_URL=https://dev.consulting.sa/
      - GENERIC_TIMEZONE=Asia/Riyadh
    volumes:
      - agentic-dev-n8n-data:/home/node/.n8n
    restart: unless-stopped
    networks:
      - agentic-dev

networks:
  agentic-dev:
    driver: bridge

volumes:
  agentic-dev-frontend-data:
    external: true
  agentic-dev-backend-data:
    external: true
  agentic-dev-redis-data:
    external: true
  agentic-dev-n8n-data:
    external: true
EOF

# Copy development compose to server
sshpass -p "$SERVER_PASS" scp /tmp/docker-compose.development.yml "$SERVER_USER@$SERVER_IP:$DEV_STACK_PATH/docker-compose.yml"
echo "✅ Development docker-compose created"

echo ""
echo "📋 Phase 5: Creating deployment scripts..."

# Create production deployment script
cat > /tmp/deploy-production.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying Production Stack..."
cd /opt/docker-stacks/production

# Copy latest source code to production volume
docker run --rm -v $(pwd)/frontend:/source -v agentic-prod-frontend-data:/dest alpine sh -c "cp -r /source/* /dest/"

# Deploy production stack
docker-compose down
docker-compose pull
docker-compose up -d

echo "✅ Production Stack Deployed!"
docker-compose ps
EOF

# Create development deployment script
cat > /tmp/deploy-development.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying Development Stack..."
cd /opt/docker-stacks/development

# Copy latest source code to development volume
docker run --rm -v $(pwd)/frontend:/source -v agentic-dev-frontend-data:/dest alpine sh -c "cp -r /source/* /dest/"

# Deploy development stack
docker-compose down
docker-compose pull
docker-compose up -d

echo "✅ Development Stack Deployed!"
docker-compose ps
EOF

# Copy deployment scripts to server
sshpass -p "$SERVER_PASS" scp /tmp/deploy-production.sh "$SERVER_USER@$SERVER_IP:$PROD_STACK_PATH/deploy.sh"
sshpass -p "$SERVER_PASS" scp /tmp/deploy-development.sh "$SERVER_USER@$SERVER_IP:$DEV_STACK_PATH/deploy.sh"

ssh_run "chmod +x $PROD_STACK_PATH/deploy.sh"
ssh_run "chmod +x $DEV_STACK_PATH/deploy.sh"

echo "✅ Deployment scripts created"

echo ""
echo "📋 Phase 6: Copying current source code..."

# Copy current frontend source to both stacks
scp -r frontend "$SERVER_USER@$SERVER_IP:$PROD_STACK_PATH/"
scp -r frontend "$SERVER_USER@$SERVER_IP:$DEV_STACK_PATH/"

echo "✅ Source code copied to both stacks"

# Cleanup temp files
rm -f /tmp/docker-compose.production.yml /tmp/docker-compose.development.yml /tmp/deploy-production.sh /tmp/deploy-development.sh

echo ""
echo "🎉 SEPARATED STACKS CREATED SUCCESSFULLY!"
echo ""
echo "📋 What's Ready:"
echo "├── 🏭 Production Stack: $PROD_STACK_PATH"
echo "├── 🔧 Development Stack: $DEV_STACK_PATH"
echo "├── 💾 Isolated Docker Volumes: Prod/Dev completely separated"
echo "├── 🌐 Port Separation: Prod (3000,8000,6379,5678) | Dev (3001,8001,6380,5679)"
echo "├── 🚀 Deployment Scripts: Ready for independent deployments"
echo "└── 🔒 No Shared Filesystem: Changes in dev won't affect prod"
echo ""
echo "📝 Next Steps:"
echo "   1. Deploy production: ssh root@$SERVER_IP 'cd $PROD_STACK_PATH && ./deploy.sh'"
echo "   2. Deploy development: ssh root@$SERVER_IP 'cd $DEV_STACK_PATH && ./deploy.sh'"
echo "   3. Test both environments independently"
echo ""
echo "🚨 CRITICAL: This fixes the shared filesystem issue!"