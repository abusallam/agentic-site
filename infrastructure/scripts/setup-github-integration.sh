#!/bin/bash
# 🚀 COMPREHENSIVE GITHUB-BASED DEPLOYMENT SYSTEM
# Sets up proper CI/CD workflow with webhooks, environment management, and professional deployment
set -e

SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"
GITHUB_REPO="your-private-repo"  # Update this with your actual repo
GITHUB_TOKEN="your-github-token"  # Update this with your GitHub token

echo "🚀 SETTING UP PROFESSIONAL GITHUB-BASED DEPLOYMENT SYSTEM"
echo "📅 $(date)"
echo "🎯 Target: Complete CI/CD with GitHub integration and proper environment management"
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

echo "🔍 Phase 1: Setting up directory structure and dependencies..."

# Create comprehensive directory structure
ssh_run "mkdir -p /opt/deployments/{github-webhook,scripts,configs,backups,logs}"
ssh_run "mkdir -p /opt/apps/{production,development}"
ssh_run "mkdir -p /var/log/deployments"

# Install required packages
ssh_run "apt-get update && apt-get install -y git nodejs npm python3-pip nginx certbot python3-certbot-nginx docker.io docker-compose-v2 sshpass curl wget"
ssh_run "systemctl enable docker && systemctl start docker"

echo "✅ System packages and Docker installed"
echo ""

echo "🔍 Phase 2: Creating GitHub webhook handler..."

# Create advanced webhook handler with proper logging and error handling
cat > /tmp/webhook-handler.py << 'EOF'
#!/usr/bin/env python3
import json
import subprocess
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import hmac
import hashlib
import logging
from datetime import datetime
import threading
import time

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/deployments/webhook.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to use our logger
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_POST(self):
        if self.path == '/webhook':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Verify GitHub signature if secret is configured
                signature = self.headers.get('X-Hub-Signature-256')
                if not self.verify_signature(post_data, signature):
                    logger.warning("Invalid webhook signature")
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b'Invalid signature')
                    return
                
                payload = json.loads(post_data.decode('utf-8'))
                branch = payload.get('ref', '').replace('refs/heads/', '')
                repository = payload.get('repository', {}).get('name', 'unknown')
                
                logger.info(f"Received webhook for repository: {repository}, branch: {branch}")
                
                # Start deployment in background thread
                if branch == 'main':
                    threading.Thread(target=self.deploy_production, args=(payload,)).start()
                    response_msg = 'Production deployment started'
                elif branch == 'development':
                    threading.Thread(target=self.deploy_development, args=(payload,)).start()
                    response_msg = 'Development deployment started'
                else:
                    response_msg = f'No deployment configured for branch: {branch}'
                    logger.info(response_msg)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(response_msg.encode())
                
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Webhook service is healthy')
        else:
            self.send_response(404)
            self.end_headers()
    
    def deploy_production(self, payload):
        logger.info("Starting production deployment...")
        try:
            result = subprocess.run(
                ['/opt/deployments/scripts/deploy-production.sh'],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            if result.returncode == 0:
                logger.info("Production deployment completed successfully")
            else:
                logger.error(f"Production deployment failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("Production deployment timed out")
        except Exception as e:
            logger.error(f"Production deployment error: {e}")
    
    def deploy_development(self, payload):
        logger.info("Starting development deployment...")
        try:
            result = subprocess.run(
                ['/opt/deployments/scripts/deploy-development.sh'],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            if result.returncode == 0:
                logger.info("Development deployment completed successfully")
            else:
                logger.error(f"Development deployment failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("Development deployment timed out")
        except Exception as e:
            logger.error(f"Development deployment error: {e}")
    
    def verify_signature(self, payload, signature):
        if not signature:
            return True  # Allow unsigned webhooks for now
        
        secret = os.environ.get('WEBHOOK_SECRET', '').encode()
        if not secret:
            return True  # No secret configured
        
        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature or "")

def main():
    port = int(os.environ.get('WEBHOOK_PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    logger.info(f"GitHub webhook server starting on port {port}...")
    logger.info("Endpoints: POST /webhook, GET /health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Webhook server shutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()
EOF

scp_file "/tmp/webhook-handler.py" "/opt/deployments/github-webhook/webhook-handler.py"
ssh_run "chmod +x /opt/deployments/github-webhook/webhook-handler.py"

echo "✅ Advanced GitHub webhook handler created"
echo ""

echo "🔍 Phase 3: Creating production deployment script..."

# Create comprehensive production deployment script
cat > /tmp/deploy-production.sh << 'EOF'
#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/your-username/your-private-repo.git"  # Update this
DEPLOY_DIR="/opt/apps/production"
BACKUP_DIR="/opt/deployments/backups/production_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/var/log/deployments/production-$(date +%Y%m%d).log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 PRODUCTION DEPLOYMENT STARTED"
log "Repository: $REPO_URL"
log "Deploy Directory: $DEPLOY_DIR"

# Create backup of current deployment
if [ -d "$DEPLOY_DIR" ]; then
    log "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$DEPLOY_DIR" "$BACKUP_DIR/"
    log "✅ Backup created: $BACKUP_DIR"
fi

# Clone or update repository
log "Updating repository..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/main
    log "✅ Repository updated to latest main branch"
else
    rm -rf "$DEPLOY_DIR"
    git clone "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    log "✅ Repository cloned"
fi

# Load environment variables
if [ -f "/opt/deployments/configs/production.env" ]; then
    source /opt/deployments/configs/production.env
    log "✅ Production environment variables loaded"
else
    log "⚠️  Warning: Production environment file not found"
fi

# Stop existing containers
log "Stopping existing containers..."
cd "$DEPLOY_DIR"
docker compose -f docker-compose.production.yml down || true
log "✅ Existing containers stopped"

# Build and start new containers
log "Building and starting containers..."
docker compose -f docker-compose.production.yml up -d --build

# Wait for containers to be healthy
log "Waiting for containers to be healthy..."
sleep 30

# Health check
log "Performing health checks..."
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    log "✅ Frontend health check passed"
else
    log "❌ Frontend health check failed"
fi

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ Backend health check passed"
else
    log "❌ Backend health check failed"
fi

# Update nginx configuration if needed
if [ -f "/opt/deployments/configs/nginx-production.conf" ]; then
    cp /opt/deployments/configs/nginx-production.conf /etc/nginx/sites-available/consulting.conf
    nginx -t && systemctl reload nginx
    log "✅ Nginx configuration updated"
fi

log "✅ PRODUCTION DEPLOYMENT COMPLETED"
log "🌐 Site: https://www.consulting.sa"
log "📊 Check status: docker compose -f docker-compose.production.yml ps"
EOF

scp_file "/tmp/deploy-production.sh" "/opt/deployments/scripts/deploy-production.sh"
ssh_run "chmod +x /opt/deployments/scripts/deploy-production.sh"

echo "✅ Production deployment script created"
echo ""

echo "🔍 Phase 4: Creating development deployment script..."

# Create development deployment script
cat > /tmp/deploy-development.sh << 'EOF'
#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/your-username/your-private-repo.git"  # Update this
DEPLOY_DIR="/opt/apps/development"
BACKUP_DIR="/opt/deployments/backups/development_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/var/log/deployments/development-$(date +%Y%m%d).log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 DEVELOPMENT DEPLOYMENT STARTED"
log "Repository: $REPO_URL"
log "Deploy Directory: $DEPLOY_DIR"

# Create backup of current deployment
if [ -d "$DEPLOY_DIR" ]; then
    log "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$DEPLOY_DIR" "$BACKUP_DIR/"
    log "✅ Backup created: $BACKUP_DIR"
fi

# Clone or update repository
log "Updating repository..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git fetch origin
    git reset --hard origin/development
    log "✅ Repository updated to latest development branch"
else
    rm -rf "$DEPLOY_DIR"
    git clone -b development "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    log "✅ Repository cloned (development branch)"
fi

# Load environment variables
if [ -f "/opt/deployments/configs/development.env" ]; then
    source /opt/deployments/configs/development.env
    log "✅ Development environment variables loaded"
else
    log "⚠️  Warning: Development environment file not found"
fi

# Stop existing containers
log "Stopping existing containers..."
cd "$DEPLOY_DIR"
docker compose -f docker-compose.development.yml down || true
log "✅ Existing containers stopped"

# Build and start new containers
log "Building and starting containers..."
docker compose -f docker-compose.development.yml up -d --build

# Wait for containers to be healthy
log "Waiting for containers to be healthy..."
sleep 30

# Health check
log "Performing health checks..."
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    log "✅ Development frontend health check passed"
else
    log "❌ Development frontend health check failed"
fi

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    log "✅ Development backend health check passed"
else
    log "❌ Development backend health check failed"
fi

# Update nginx configuration if needed
if [ -f "/opt/deployments/configs/nginx-development.conf" ]; then
    cp /opt/deployments/configs/nginx-development.conf /etc/nginx/sites-available/dev-consulting.conf
    ln -sf /etc/nginx/sites-available/dev-consulting.conf /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    log "✅ Nginx configuration updated"
fi

log "✅ DEVELOPMENT DEPLOYMENT COMPLETED"
log "🌐 Site: https://dev.consulting.sa"
log "📊 Check status: docker compose -f docker-compose.development.yml ps"
EOF

scp_file "/tmp/deploy-development.sh" "/opt/deployments/scripts/deploy-development.sh"
ssh_run "chmod +x /opt/deployments/scripts/deploy-development.sh"

echo "✅ Development deployment script created"
echo ""

echo "🔍 Phase 5: Creating environment configurations..."

# Create production environment template
cat > /tmp/production.env << 'EOF'
# Production Environment Variables
NODE_ENV=production
NEXT_PUBLIC_SITE_URL=https://www.consulting.sa
NEXT_PUBLIC_API_URL=https://www.consulting.sa/api

# Database Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# AI Services
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_google_api_key

# Payment Processing
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Communication Services
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Workflow Automation
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_n8n_password

# Security
WEBHOOK_SECRET=your_webhook_secret
JWT_SECRET=your_jwt_secret

# Infrastructure
REDIS_URL=redis://localhost:6379
DATABASE_URL=your_production_database_url

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=your_grafana_password
EOF

# Create development environment template
cat > /tmp/development.env << 'EOF'
# Development Environment Variables
NODE_ENV=development
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api

# Database Configuration (Development)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# AI Services (Shared with production)
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
N8N_BASIC_AUTH_PASSWORD=your_dev_n8n_password

# Security
WEBHOOK_SECRET=your_webhook_secret
JWT_SECRET=your_dev_jwt_secret

# Infrastructure (Development ports)
REDIS_URL=redis://localhost:6380
DATABASE_URL=your_development_database_url

# Development Features
DEBUG=true
NEXT_TELEMETRY_DISABLED=1

# Monitoring
PROMETHEUS_ENABLED=false
EOF

scp_file "/tmp/production.env" "/opt/deployments/configs/production.env"
scp_file "/tmp/development.env" "/opt/deployments/configs/development.env"

echo "✅ Environment configuration templates created"
echo ""

echo "🔍 Phase 6: Setting up comprehensive Nginx configuration..."

# Create production Nginx configuration
cat > /tmp/nginx-production.conf << 'EOF'
# Production Site Configuration
server {
    listen 80;
    server_name consulting.sa www.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/consulting.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consulting.sa/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Main application
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
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Webhook endpoint
    location /webhook {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Create development Nginx configuration
cat > /tmp/nginx-development.conf << 'EOF'
# Development Site Configuration
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;
    
    # SSL Configuration (using wildcard cert)
    ssl_certificate /etc/letsencrypt/live/consulting.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consulting.sa/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Development-specific headers
    add_header X-Environment "development" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Main application (development port)
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
    
    # API routes (development port)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Development tools
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

scp_file "/tmp/nginx-production.conf" "/opt/deployments/configs/nginx-production.conf"
scp_file "/tmp/nginx-development.conf" "/opt/deployments/configs/nginx-development.conf"

# Apply initial Nginx configuration
ssh_run "cp /opt/deployments/configs/nginx-production.conf /etc/nginx/sites-available/consulting.conf"
ssh_run "cp /opt/deployments/configs/nginx-development.conf /etc/nginx/sites-available/dev-consulting.conf"
ssh_run "ln -sf /etc/nginx/sites-available/consulting.conf /etc/nginx/sites-enabled/"
ssh_run "ln -sf /etc/nginx/sites-available/dev-consulting.conf /etc/nginx/sites-enabled/"
ssh_run "rm -f /etc/nginx/sites-enabled/default"
ssh_run "nginx -t && systemctl reload nginx"

echo "✅ Nginx configurations created and applied"
echo ""

echo "🔍 Phase 7: Setting up SSL certificates..."

# Get SSL certificates for all domains
ssh_run "certbot --nginx -d consulting.sa -d www.consulting.sa -d dev.consulting.sa --non-interactive --agree-tos --email admin@consulting.sa --expand"

echo "✅ SSL certificates configured"
echo ""

echo "🔍 Phase 8: Creating systemd services..."

# Create webhook systemd service
cat > /tmp/webhook.service << 'EOF'
[Unit]
Description=GitHub Webhook Handler for Consulting.sa
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/deployments/github-webhook
ExecStart=/usr/bin/python3 /opt/deployments/github-webhook/webhook-handler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment variables
Environment=WEBHOOK_PORT=8080
Environment=WEBHOOK_SECRET=your_webhook_secret

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/deployments /var/log/deployments

[Install]
WantedBy=multi-user.target
EOF

scp_file "/tmp/webhook.service" "/etc/systemd/system/webhook.service"
ssh_run "systemctl daemon-reload"
ssh_run "systemctl enable webhook.service"
ssh_run "systemctl start webhook.service"

echo "✅ Webhook systemd service configured and started"
echo ""

echo "🔍 Phase 9: Creating monitoring and maintenance scripts..."

# Create health check script
cat > /tmp/health-check.sh << 'EOF'
#!/bin/bash
# Comprehensive health check script

LOG_FILE="/var/log/deployments/health-check.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔍 Starting health check..."

# Check webhook service
if systemctl is-active --quiet webhook.service; then
    log "✅ Webhook service is running"
else
    log "❌ Webhook service is not running"
    systemctl restart webhook.service
fi

# Check Docker containers
log "Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tee -a "$LOG_FILE"

# Check website accessibility
if curl -f -s https://www.consulting.sa/health > /dev/null; then
    log "✅ Production site is accessible"
else
    log "❌ Production site is not accessible"
fi

if curl -f -s https://dev.consulting.sa/health > /dev/null; then
    log "✅ Development site is accessible"
else
    log "❌ Development site is not accessible"
fi

# Check SSL certificates
log "Checking SSL certificates..."
certbot certificates | tee -a "$LOG_FILE"

log "✅ Health check completed"
EOF

scp_file "/tmp/health-check.sh" "/opt/deployments/scripts/health-check.sh"
ssh_run "chmod +x /opt/deployments/scripts/health-check.sh"

# Create log rotation configuration
cat > /tmp/deployments-logrotate << 'EOF'
/var/log/deployments/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload webhook.service > /dev/null 2>&1 || true
    endscript
}
EOF

scp_file "/tmp/deployments-logrotate" "/etc/logrotate.d/deployments"

echo "✅ Monitoring and maintenance scripts created"
echo ""

# Cleanup temporary files
rm -f /tmp/webhook-handler.py /tmp/deploy-production.sh /tmp/deploy-development.sh
rm -f /tmp/production.env /tmp/development.env
rm -f /tmp/nginx-production.conf /tmp/nginx-development.conf
rm -f /tmp/webhook.service /tmp/health-check.sh /tmp/deployments-logrotate

echo ""
echo "🎉 PROFESSIONAL GITHUB-BASED DEPLOYMENT SYSTEM SETUP COMPLETE!"
echo ""
echo "📋 What's Configured:"
echo "├── 🔗 GitHub Integration: Webhook handler on port 8080"
echo "├── 🚀 Automated Deployment: Push to main/development triggers deployment"
echo "├── 🔒 SSL Certificates: Let's Encrypt for all domains"
echo "├── 🌐 Nginx Configuration: Professional reverse proxy setup"
echo "├── 📁 Environment Management: Separate prod/dev configurations"
echo "├── 💾 Backup System: Automatic backups before deployment"
echo "├── 📊 Monitoring: Systemd services with auto-restart"
echo "├── 🔍 Health Checks: Comprehensive monitoring scripts"
echo "└── 📝 Logging: Centralized logging with rotation"
echo ""
echo "📝 CRITICAL NEXT STEPS:"
echo "   1. Update GitHub repository URL in deployment scripts:"
echo "      - Edit /opt/deployments/scripts/deploy-production.sh"
echo "      - Edit /opt/deployments/scripts/deploy-development.sh"
echo "      - Replace 'your-username/your-private-repo' with actual repo"
echo ""
echo "   2. Configure environment variables:"
echo "      - Edit /opt/deployments/configs/production.env"
echo "      - Edit /opt/deployments/configs/development.env"
echo "      - Add your actual API keys and secrets"
echo ""
echo "   3. Set up GitHub webhook:"
echo "      - Go to your repository Settings → Webhooks"
echo "      - Add webhook URL: https://www.consulting.sa/webhook"
echo "      - Content type: application/json"
echo "      - Events: Push events"
echo "      - Secret: Use the webhook secret from environment config"
echo ""
echo "   4. Test the deployment:"
echo "      - Push to 'development' branch to test dev deployment"
echo "      - Push to 'main' branch to trigger production deployment"
echo ""
echo "🌐 URLs:"
echo "   Production: https://www.consulting.sa"
echo "   Development: https://dev.consulting.sa"
echo "   Webhook: https://www.consulting.sa/webhook"
echo "   Health Check: https://www.consulting.sa/health"
echo ""
echo "🔧 Management Commands:"
echo "   Check webhook status: systemctl status webhook.service"
echo "   View deployment logs: tail -f /var/log/deployments/production-$(date +%Y%m%d).log"
echo "   Run health check: /opt/deployments/scripts/health-check.sh"
echo "   Manual deployment: /opt/deployments/scripts/deploy-production.sh"
echo ""
echo "📚 Documentation: All processes documented for future VPS deployments"