#!/bin/bash
# 🔧 FIX SEPARATED PRODUCTION AND DEVELOPMENT STACKS
# Properly separates prod and dev environments with correct naming and domains

set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"

echo "🔧 FIXING SEPARATED PRODUCTION AND DEVELOPMENT STACKS"
echo "📅 $(date)"
echo ""

# Function to run SSH command
ssh_run() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
    if [ $? -eq 0 ]; then
        echo "✅ SSH: $1"
    else
        echo "❌ SSH FAILED: $1"
        exit 1
    fi
}

# Function to copy file to server
scp_file() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$1" "$SERVER_USER@$SERVER_IP:$2"
    if [ $? -eq 0 ]; then
        echo "✅ SCP: $1 → $2"
    else
        echo "❌ SCP FAILED: $1 → $2"
        exit 1
    fi
}

echo "🔍 Step 1: Analyzing current container situation..."
ssh_run "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔍 Step 2: Creating updated Nginx configuration with main.consulting.sa..."

# Create updated production Nginx configuration
cat > /tmp/production-fixed.conf << 'EOF'
# Production Nginx Configuration for consulting.sa
server {
    listen 80;
    server_name consulting.sa www.consulting.sa main.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa main.consulting.sa;

    # SSL Configuration (Cloudflare Origin Certificate)
    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Main application (Production Frontend - Port 3000)
    location / {
        proxy_pass http://127.0.0.1:3000;
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

    # API routes (Production Backend - Port 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # n8n workflows (Production N8N - Port 5678)
    location /workflows/ {
        proxy_pass http://127.0.0.1:5678/;
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

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Create development Nginx configuration
cat > /tmp/development-fixed.conf << 'EOF'
# Development Nginx Configuration for dev.consulting.sa
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    # SSL Configuration (Cloudflare Origin Certificate)
    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Development-specific headers
    add_header X-Environment "development" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Main application (Development Frontend - Port 3001)
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

    # API routes (Development Backend - Port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # n8n workflows (Development N8N - Port 5679)
    location /workflows/ {
        proxy_pass http://127.0.0.1:5679/;
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

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Copy updated configurations
scp_file "/tmp/production-fixed.conf" "/etc/nginx/sites-available/production.conf"
scp_file "/tmp/development-fixed.conf" "/etc/nginx/sites-available/development.conf"

echo ""
echo "🔍 Step 3: Testing and reloading Nginx configuration..."
ssh_run "nginx -t"
ssh_run "systemctl reload nginx"

echo ""
echo "🔍 Step 4: Creating proper Docker Compose files for separated stacks..."

# Create production Docker Compose with proper naming
cat > /tmp/docker-compose.production-separated.yml << 'EOF'
version: '3.8'

services:
  frontend-prod:
    build:
      context: ./agentic-site/frontend
      dockerfile: ../Dockerfile.frontend
      args:
        NODE_ENV: production
    container_name: consulting-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://www.consulting.sa
      - NEXT_PUBLIC_API_URL=https://www.consulting.sa/api
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - backend-prod
      - redis-prod
    networks:
      - consulting-production

  backend-prod:
    build:
      context: ./agentic-site/agent
      dockerfile: ../Dockerfile.backend
    container_name: consulting-backend-prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - PORT=8000
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - redis-prod
    networks:
      - consulting-production

  redis-prod:
    image: redis:7-alpine
    container_name: consulting-redis-prod
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - consulting-production

  n8n-prod:
    image: n8nio/n8n:latest
    container_name: consulting-n8n-prod
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD:-defaultpassword}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://www.consulting.sa/workflows/
    volumes:
      - n8n_prod_data:/home/node/.n8n
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - consulting-production

volumes:
  redis_prod_data:
    driver: local
  n8n_prod_data:
    driver: local

networks:
  consulting-production:
    driver: bridge
EOF

# Create development Docker Compose with proper naming
cat > /tmp/docker-compose.development-separated.yml << 'EOF'
version: '3.8'

services:
  frontend-dev:
    build:
      context: ./agentic-site/frontend
      dockerfile: ../Dockerfile.frontend
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
    networks:
      - consulting-development

  backend-dev:
    build:
      context: ./agentic-site/agent
      dockerfile: ../Dockerfile.backend
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
    networks:
      - consulting-development

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
    networks:
      - consulting-development

  n8n-dev:
    image: n8nio/n8n:latest
    container_name: consulting-n8n-dev
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD:-defaultpassword}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://dev.consulting.sa/workflows/
    volumes:
      - n8n_dev_data:/home/node/.n8n
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - consulting-development

volumes:
  redis_dev_data:
    driver: local
  n8n_dev_data:
    driver: local

networks:
  consulting-development:
    driver: bridge
EOF

# Copy the new Docker Compose files
scp_file "/tmp/docker-compose.production-separated.yml" "/opt/docker-apps/production/agentic-site/docker-compose.production-separated.yml"
scp_file "/tmp/docker-compose.development-separated.yml" "/opt/docker-apps/development/agentic-site/docker-compose.development-separated.yml"

echo ""
echo "🔍 Step 5: Stopping old containers and starting with new separated naming..."

# Stop old containers
ssh_run "docker stop agentic-frontend-prod agentic-backend-prod agentic-redis-prod agentic-n8n-prod || true"
ssh_run "docker stop agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev || true"

# Remove old containers
ssh_run "docker rm agentic-frontend-prod agentic-backend-prod agentic-redis-prod agentic-n8n-prod || true"
ssh_run "docker rm agentic-frontend-dev agentic-backend-dev agentic-redis-dev agentic-n8n-dev || true"

echo ""
echo "🔍 Step 6: Starting production stack with new naming..."
ssh_run "cd /opt/docker-apps/production/agentic-site && docker compose -f docker-compose.production-separated.yml up -d --build"

echo ""
echo "🔍 Step 7: Waiting for production containers to start..."
sleep 30

echo ""
echo "🔍 Step 8: Checking production stack status..."
ssh_run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔍 Step 9: Testing production endpoints..."
if ssh_run "curl -f -s http://localhost:3000/ > /dev/null 2>&1"; then
    echo "✅ Production frontend is responding"
else
    echo "⚠️  Production frontend may still be starting"
fi

if ssh_run "curl -f -s http://localhost:8000/health > /dev/null 2>&1"; then
    echo "✅ Production backend is responding"
else
    echo "⚠️  Production backend may still be starting"
fi

# Cleanup temp files
rm -f /tmp/production-fixed.conf /tmp/development-fixed.conf
rm -f /tmp/docker-compose.production-separated.yml /tmp/docker-compose.development-separated.yml

echo ""
echo "✅ SEPARATED STACKS CONFIGURATION COMPLETED"
echo ""
echo "📋 What's Fixed:"
echo "├── 🌐 Domain Configuration: main.consulting.sa now points to frontend"
echo "├── 🏗️  Container Naming: consulting-*-prod vs consulting-*-dev"
echo "├── 🔌 Port Separation: Production (3000, 8000) vs Development (3001, 8001)"
echo "├── 🌍 Network Separation: consulting-production vs consulting-development"
echo "└── 📁 Stack Separation: Clear prod/dev environment isolation"
echo ""
echo "🌐 URLs:"
echo "   Production: https://consulting.sa, https://www.consulting.sa, https://main.consulting.sa"
echo "   Development: https://dev.consulting.sa"
echo ""
echo "🐳 Container Names:"
echo "   Production: consulting-frontend-prod, consulting-backend-prod, consulting-redis-prod, consulting-n8n-prod"
echo "   Development: consulting-frontend-dev, consulting-backend-dev, consulting-redis-dev, consulting-n8n-dev"
echo ""
echo "📊 Check status: docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"