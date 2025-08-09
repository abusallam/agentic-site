#!/bin/bash

# 🔍 MONITORING CONTAINERS PREPARATION SCRIPT
# Prepares VPS for additional monitoring and agentic tool containers
# 
# CONTAINERS TO BE DEPLOYED:
# - Prometheus (metrics collection)
# - Grafana (dashboards and visualization)
# - Portainer (container management)
# - n8n-monitoring (workflow monitoring)
# - Redis Insight (Redis monitoring)
# - Uptime Kuma (uptime monitoring)

set -e

# Configuration
SERVER_IP="217.79.255.54"
SERVER_USER="root"
SERVER_PASS="gnqLG7FDd4"
MONITORING_PATH="/opt/docker-apps/monitoring"

echo "🔍 MONITORING CONTAINERS PREPARATION"
echo "📅 $(date)"
echo "🎯 Target: $SERVER_IP"
echo "📁 Monitoring Path: $MONITORING_PATH"
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

echo "🔍 Phase 1: System preparation..."

# Create monitoring directory structure
ssh_run "mkdir -p $MONITORING_PATH/{prometheus,grafana,portainer,n8n-monitoring,redis-insight,uptime-kuma}"
ssh_run "mkdir -p $MONITORING_PATH/config/{prometheus,grafana,nginx}"
ssh_run "mkdir -p $MONITORING_PATH/data/{prometheus,grafana,portainer,uptime-kuma}"

# Set proper permissions
ssh_run "chmod -R 755 $MONITORING_PATH"

echo ""
echo "📋 Phase 2: Creating monitoring docker-compose..."

# Create monitoring docker-compose file
cat > /tmp/docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:latest
    container_name: agentic-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  # Grafana - Dashboards and Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: agentic-grafana
    ports:
      - "3030:3000"
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./config/grafana/grafana.ini:/etc/grafana/grafana.ini
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=agentic2025
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - monitoring

  # Portainer - Container Management
  portainer:
    image: portainer/portainer-ce:latest
    container_name: agentic-portainer
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data/portainer:/data
    restart: unless-stopped
    networks:
      - monitoring

  # Redis Insight - Redis Monitoring
  redis-insight:
    image: redislabs/redisinsight:latest
    container_name: agentic-redis-insight
    ports:
      - "8001:8001"
    volumes:
      - ./data/redis-insight:/db
    restart: unless-stopped
    networks:
      - monitoring

  # Uptime Kuma - Uptime Monitoring
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    container_name: agentic-uptime-kuma
    ports:
      - "3001:3001"
    volumes:
      - ./data/uptime-kuma:/app/data
    restart: unless-stopped
    networks:
      - monitoring

  # n8n Monitoring Instance
  n8n-monitoring:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-monitoring
    ports:
      - "5680:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=agentic2025
      - WEBHOOK_URL=https://monitoring.consulting.sa/
      - GENERIC_TIMEZONE=Asia/Riyadh
    volumes:
      - ./data/n8n-monitoring:/home/node/.n8n
    restart: unless-stopped
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  portainer_data:
  uptime_kuma_data:
  redis_insight_data:
  n8n_monitoring_data:
EOF

# Copy monitoring compose file to server
sshpass -p "$SERVER_PASS" scp /tmp/docker-compose.monitoring.yml "$SERVER_USER@$SERVER_IP:$MONITORING_PATH/docker-compose.yml"
echo "✅ Monitoring docker-compose created"

echo ""
echo "📋 Phase 3: Creating configuration files..."

# Create Prometheus configuration
cat > /tmp/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'agentic-frontend-prod'
    static_configs:
      - targets: ['host.docker.internal:3000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'agentic-frontend-dev'
    static_configs:
      - targets: ['host.docker.internal:3001']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'agentic-backend-prod'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'agentic-backend-dev'
    static_configs:
      - targets: ['host.docker.internal:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis-prod'
    static_configs:
      - targets: ['host.docker.internal:6379']

  - job_name: 'redis-dev'
    static_configs:
      - targets: ['host.docker.internal:6380']

  - job_name: 'n8n-prod'
    static_configs:
      - targets: ['host.docker.internal:5678']

  - job_name: 'n8n-dev'
    static_configs:
      - targets: ['host.docker.internal:5679']
EOF

# Copy Prometheus config to server
sshpass -p "$SERVER_PASS" scp /tmp/prometheus.yml "$SERVER_USER@$SERVER_IP:$MONITORING_PATH/config/prometheus/prometheus.yml"
echo "✅ Prometheus configuration created"

# Create Grafana configuration
cat > /tmp/grafana.ini << 'EOF'
[server]
http_port = 3000
domain = monitoring.consulting.sa
root_url = https://monitoring.consulting.sa/grafana/

[security]
admin_user = admin
admin_password = agentic2025

[users]
allow_sign_up = false
allow_org_create = false

[auth.anonymous]
enabled = false

[dashboards]
default_home_dashboard_path = /var/lib/grafana/dashboards/agentic-overview.json
EOF

# Copy Grafana config to server
sshpass -p "$SERVER_PASS" scp /tmp/grafana.ini "$SERVER_USER@$SERVER_IP:$MONITORING_PATH/config/grafana/grafana.ini"
echo "✅ Grafana configuration created"

echo ""
echo "📋 Phase 4: Creating nginx configuration for monitoring..."

# Create nginx config for monitoring subdomain
cat > /tmp/monitoring.conf << 'EOF'
server {
    listen 80;
    server_name monitoring.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitoring.consulting.sa;

    ssl_certificate /etc/ssl/certs/consulting.sa.crt;
    ssl_certificate_key /etc/ssl/private/consulting.sa.key;

    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3030/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Portainer
    location /portainer/ {
        proxy_pass http://localhost:9000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }

    # Uptime Kuma
    location /uptime/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Redis Insight
    location /redis/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # n8n Monitoring
    location /n8n-monitoring/ {
        proxy_pass http://localhost:5680/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Default monitoring dashboard
    location / {
        return 301 /grafana/;
    }
}
EOF

# Copy nginx config to server
sshpass -p "$SERVER_PASS" scp /tmp/monitoring.conf "$SERVER_USER@$SERVER_IP:$MONITORING_PATH/config/nginx/monitoring.conf"
echo "✅ Nginx monitoring configuration created"

echo ""
echo "📋 Phase 5: Creating deployment script..."

# Create monitoring deployment script
cat > /tmp/deploy-monitoring.sh << 'EOF'
#!/bin/bash

echo "🔍 Deploying Monitoring Stack..."

cd /opt/docker-apps/monitoring

# Stop any existing monitoring containers
docker-compose down 2>/dev/null || true

# Pull latest images
docker-compose pull

# Start monitoring stack
docker-compose up -d

# Wait for services to be ready
sleep 30

# Check status
docker-compose ps

echo ""
echo "🎉 Monitoring Stack Deployed!"
echo ""
echo "📊 Access URLs:"
echo "├── 🌐 Main Dashboard: https://monitoring.consulting.sa/"
echo "├── 📈 Grafana: https://monitoring.consulting.sa/grafana/"
echo "├── 📊 Prometheus: https://monitoring.consulting.sa/prometheus/"
echo "├── 🐳 Portainer: https://monitoring.consulting.sa/portainer/"
echo "├── ⏰ Uptime Kuma: https://monitoring.consulting.sa/uptime/"
echo "├── 🔴 Redis Insight: https://monitoring.consulting.sa/redis/"
echo "└── 🔄 n8n Monitoring: https://monitoring.consulting.sa/n8n-monitoring/"
echo ""
echo "🔐 Default Credentials:"
echo "├── Grafana: admin / agentic2025"
echo "├── n8n: admin / agentic2025"
echo "└── Portainer: Set on first access"
EOF

# Copy deployment script to server
sshpass -p "$SERVER_PASS" scp /tmp/deploy-monitoring.sh "$SERVER_USER@$SERVER_IP:$MONITORING_PATH/deploy-monitoring.sh"
ssh_run "chmod +x $MONITORING_PATH/deploy-monitoring.sh"
echo "✅ Monitoring deployment script created"

# Cleanup temp files
rm -f /tmp/docker-compose.monitoring.yml /tmp/prometheus.yml /tmp/grafana.ini /tmp/monitoring.conf /tmp/deploy-monitoring.sh

echo ""
echo "🎉 MONITORING PREPARATION COMPLETE!"
echo ""
echo "📋 What's Ready:"
echo "├── 🐳 Docker Compose: Prometheus, Grafana, Portainer, Uptime Kuma, Redis Insight, n8n"
echo "├── ⚙️ Configurations: All services pre-configured"
echo "├── 🌐 Nginx: monitoring.consulting.sa subdomain ready"
echo "├── 🚀 Deployment: Ready to deploy with single command"
echo "└── 📊 Monitoring: Full stack monitoring prepared"
echo ""
echo "📝 To deploy monitoring stack:"
echo "   ssh root@$SERVER_IP"
echo "   cd $MONITORING_PATH"
echo "   ./deploy-monitoring.sh"
echo ""
echo "⚠️ Note: Add monitoring.consulting.sa to DNS before deployment"