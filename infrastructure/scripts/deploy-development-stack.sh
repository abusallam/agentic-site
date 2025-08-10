#!/bin/bash
# 🚀 DEVELOPMENT STACK DEPLOYMENT
# Deploys development environment connected to GitHub for continuous deployment
set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"
REPO_URL="git@github.com:abusallam/agentic-site.git"
BRANCH="develop"

echo "🚀 DEPLOYING DEVELOPMENT STACK"
echo "📅 $(date)"
echo "🎯 Target: Development environment at dev.consulting.sa"
echo "📦 Repository: $REPO_URL"
echo "🌿 Branch: $BRANCH"
echo ""

# Function to run SSH command with error handling
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

echo "🔍 Step 1: Setting up development directory..."

# Create development directory structure
ssh_run "mkdir -p /opt/apps/development"
ssh_run "mkdir -p /var/log/deployments"

echo ""
echo "🔍 Step 2: Cloning repository to development environment..."

# Clone repository to development directory
ssh_run "cd /opt/apps && rm -rf development/agentic-site"
ssh_run "cd /opt/apps/development && git clone -b $BRANCH $REPO_URL agentic-site || git clone $REPO_URL agentic-site"
ssh_run "cd /opt/apps/development/agentic-site && git checkout -b $BRANCH origin/$BRANCH 2>/dev/null || git checkout $BRANCH || echo 'Using main branch'"

echo ""
echo "🔍 Step 3: Creating development Docker Compose configuration..."

# Update the existing docker-compose.development.yml to use consulting naming
cat > /tmp/docker-compose.development.yml << 'EOF'
version: '3.8'

services:
  frontend-dev:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.frontend
      args:
        NODE_ENV: development
    container_name: consulting-frontend-dev
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
    env_file:
      - .env.development
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - backend-dev
      - redis-dev

  backend-dev:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.backend
    container_name: consulting-backend-dev
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=development
      - PORT=8000
    env_file:
      - .env.development
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - redis-dev

  redis-dev:
    image: redis:7-alpine
    container_name: consulting-redis-dev
    ports:
      - "6380:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_dev_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  n8n-dev:
    image: n8nio/n8n:latest
    container_name: consulting-n8n-dev
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD:-dev_n8n_password}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://dev.consulting.sa/n8n/
    volumes:
      - n8n_dev_data:/home/node/.n8n
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_dev_data:
    driver: local
  n8n_dev_data:
    driver: local

networks:
  default:
    name: consulting-development
    driver: bridge
EOF

# Copy updated development docker-compose to server
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no /tmp/docker-compose.development.yml "$SERVER_USER@$SERVER_IP:/opt/apps/development/agentic-site/"

echo ""
echo "🔍 Step 4: Creating development environment file..."

# Create development environment file
cat > /tmp/.env.development << 'EOF'
# Development Environment Variables
NODE_ENV=development
ENVIRONMENT=development
DEBUG=true

# Site URLs
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api

# Database Configuration (Development)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# AI Services
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_google_api_key

# Payment Processing (Test keys)
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
STRIPE_SECRET_KEY=sk_test_your_test_key

# Communication Services (Development)
LIVEKIT_API_KEY=your_dev_livekit_api_key
LIVEKIT_API_SECRET=your_dev_livekit_api_secret

# Workflow Automation (Development)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=dev_n8n_password

# Infrastructure (Development ports)
REDIS_URL=redis://consulting-redis-dev:6379
DATABASE_URL=your_development_database_url

# Development Features
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_DEBUG=true
EOF

# Copy development environment file to server
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no /tmp/.env.development "$SERVER_USER@$SERVER_IP:/opt/apps/development/agentic-site/.env"

echo ""
echo "🔍 Step 5: Deploying development containers..."

# Stop any existing development containers
ssh_run "cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml down || true"

# Build and start development containers
ssh_run "cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml up -d --build"

echo ""
echo "🔍 Step 6: Waiting for containers to be healthy..."

# Wait for containers to start
sleep 30

# Check container status
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep dev"

echo ""
echo "🔍 Step 7: Testing development endpoints..."

# Test development endpoints
ssh_run "curl -I http://localhost:3001/ || echo 'Frontend not ready yet'"
ssh_run "curl -I http://localhost:8001/health || echo 'Backend not ready yet'"

echo ""
echo "🔍 Step 8: Setting up Nginx configuration for development..."

# Create development Nginx configuration
cat > /tmp/nginx-dev.conf << 'EOF'
# Development Site Configuration
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    # SSL Configuration (using existing wildcard cert)
    ssl_certificate /etc/letsencrypt/live/consulting.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consulting.sa/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Development-specific headers
    add_header X-Environment "development" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Main application (development port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # API routes (development port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Development tools - N8N
    location /n8n/ {
        proxy_pass http://127.0.0.1:5679/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "development healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Copy and apply Nginx configuration
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no /tmp/nginx-dev.conf "$SERVER_USER@$SERVER_IP:/etc/nginx/sites-available/dev-consulting.conf"
ssh_run "ln -sf /etc/nginx/sites-available/dev-consulting.conf /etc/nginx/sites-enabled/"
ssh_run "nginx -t && systemctl reload nginx"

echo ""
echo "🔍 Step 9: Final health check..."

# Final status check
echo "Container Status:"
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(dev|NAMES)'"

echo ""
echo "Testing URLs:"
ssh_run "curl -I https://dev.consulting.sa/health || echo 'Development site not accessible yet'"

# Cleanup temporary files
rm -f /tmp/docker-compose.development.yml /tmp/.env.development /tmp/nginx-dev.conf

echo ""
echo "🎉 DEVELOPMENT STACK DEPLOYMENT COMPLETED!"
echo ""
echo "📋 What's Deployed:"
echo "├── 🌐 Development Site: https://dev.consulting.sa"
echo "├── 🔧 Frontend Container: consulting-frontend-dev (port 3001)"
echo "├── 🔧 Backend Container: consulting-backend-dev (port 8001)"
echo "├── 🔧 Redis Container: consulting-redis-dev (port 6380)"
echo "├── 🔧 N8N Container: consulting-n8n-dev (port 5679)"
echo "└── 🔗 GitHub Repository: Connected to '$BRANCH' branch"
echo ""
echo "🚀 Next Steps:"
echo "1. **Test Development Site**: Visit https://dev.consulting.sa"
echo "2. **Set up GitHub Webhook**: For automatic deployments on push"
echo "3. **Configure Environment Variables**: Update .env file with real API keys"
echo "4. **Test Deployment Pipeline**: Push to '$BRANCH' branch to trigger deployment"
echo ""
echo "🔧 Management Commands:"
echo "   View dev containers: docker ps | grep dev"
echo "   View dev logs: docker logs consulting-frontend-dev"
echo "   Restart dev stack: cd /opt/apps/development/agentic-site && docker compose -f docker-compose.development.yml restart"
echo "   Update from GitHub: cd /opt/apps/development/agentic-site && git pull origin $BRANCH"
echo ""
echo "📝 Your deployment strategy is now ready:"
echo "   Dev Stack (dev.consulting.sa) ← GitHub '$BRANCH' branch"
echo "   Test & Validate ← Development environment"
echo "   Promote via Nginx ← Switch domains when ready"
echo "   Production Promotion ← Dev becomes prod, new dev created"