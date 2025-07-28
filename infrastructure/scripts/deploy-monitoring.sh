#!/bin/bash
set -e

# Deploy Monitoring Script - N8N, Grafana, and Prometheus Integration
# This script deploys comprehensive monitoring for the agentic AI platform

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
VPS_HOST=${VPS_HOST:-"217.79.255.54"}
VPS_USER=${VPS_USER:-"root"}
VPS_PASSWORD=${VPS_PASSWORD:-"gt5qXy22aJ"}
DOMAIN=${DOMAIN:-"consulting.sa"}
N8N_PORT=5678
GRAFANA_PORT=3001
PROMETHEUS_PORT=9090

echo -e "${PURPLE}🔔 Agentic AI Platform - Monitoring Deployment${NC}"
echo -e "${BLUE}📊 Deploying N8N, Grafana, and Prometheus monitoring${NC}"
echo -e "${BLUE}🎯 Target: $VPS_HOST ($DOMAIN)${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: This will set up monitoring alongside your existing production system${NC}"
echo -e "${YELLOW}⚠️  The production system will NOT be disrupted${NC}"
echo ""

# Confirmation prompt
read -p "Continue with monitoring deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled by user${NC}"
    exit 0
fi

# Function to run commands on VPS using sshpass
run_on_vps() {
    local command="$1"
    local description="${2:-$command}"
    echo -e "${YELLOW}VPS: $description${NC}"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$command"
}

# Function to copy files to VPS
copy_to_vps() {
    local local_path="$1"
    local remote_path="$2"
    echo -e "${YELLOW}Copying $local_path to VPS:$remote_path${NC}"
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$VPS_USER@$VPS_HOST:$remote_path"
}

# Function to validate prerequisites
validate_prerequisites() {
    echo -e "${BLUE}Phase 1: Validating Prerequisites${NC}"
    
    # Check if sshpass is installed
    if ! command -v sshpass &> /dev/null; then
        echo -e "${YELLOW}Installing sshpass...${NC}"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y sshpass
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo -e "${RED}❌ Please install sshpass manually${NC}"
            exit 1
        fi
    fi
    
    # Test VPS connection
    echo -e "${YELLOW}Testing VPS connection...${NC}"
    if run_on_vps "echo 'Connection test successful'" "Testing connection"; then
        echo -e "${GREEN}✓ VPS connection established${NC}"
    else
        echo -e "${RED}❌ Failed to connect to VPS${NC}"
        exit 1
    fi
    
    # Check if production system is running
    echo -e "${YELLOW}Checking production system status...${NC}"
    if run_on_vps "docker ps | grep agentic-frontend-prod" "Checking frontend container"; then
        echo -e "${GREEN}✓ Production system is running${NC}"
    else
        echo -e "${RED}❌ Production system not found. Please ensure it's running first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites validation completed${NC}"
    echo ""
}

# Function to setup monitoring directories
setup_directories() {
    echo -e \"${BLUE}Phase 2: Setting up Monitoring Directories${NC}\"
    
    # Create monitoring directories
    run_on_vps \"mkdir -p /opt/monitoring/{n8n,grafana,prometheus,alertmanager,blackbox}\" \"Creating monitoring directories\"
    run_on_vps \"mkdir -p /opt/monitoring/{n8n/workflows,n8n/credentials,grafana/dashboards,grafana/datasources,prometheus/rules}\" \"Creating subdirectories\"
    
    echo -e \"${GREEN}✅ Monitoring directories created${NC}\"
    echo \"\"
}

# Function to deploy configuration files
deploy_configurations() {
    echo -e \"${BLUE}Phase 3: Deploying Configuration Files${NC}\"
    
    # Copy monitoring configurations
    copy_to_vps \"monitoring/docker-compose.monitoring.yml\" \"/opt/monitoring/docker-compose.yml\"
    copy_to_vps \"monitoring/prometheus/prometheus.yml\" \"/opt/monitoring/prometheus/prometheus.yml\"
    copy_to_vps \"monitoring/prometheus/rules/\" \"/opt/monitoring/prometheus/\"
    copy_to_vps \"monitoring/alertmanager/alertmanager.yml\" \"/opt/monitoring/alertmanager/alertmanager.yml\"
    copy_to_vps \"monitoring/blackbox/blackbox.yml\" \"/opt/monitoring/blackbox/blackbox.yml\"
    copy_to_vps \"monitoring/n8n/workflows/\" \"/opt/monitoring/n8n/\"
    copy_to_vps \"monitoring/grafana/dashboards/\" \"/opt/monitoring/grafana/\"
    
    echo -e \"${GREEN}✅ Configuration files deployed${NC}\"
    echo \"\"
}

# Function to setup Grafana datasources
setup_grafana_datasources() {
    echo -e \"${BLUE}Phase 4: Setting up Grafana Datasources${NC}\"
    
    # Create Prometheus datasource configuration
    run_on_vps \"cat > /opt/monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: '15s'
      queryTimeout: '60s'
      httpMethod: 'POST'
EOF\" \"Creating Prometheus datasource\"

    echo -e \"${GREEN}✅ Grafana datasources configured${NC}\"
    echo \"\"
}

# Function to setup Nginx configuration for monitoring
setup_nginx_config() {
    echo -e \"${BLUE}Phase 5: Setting up Nginx Configuration for Monitoring${NC}\"
    
    # Create Nginx configuration for monitoring subdomains
    run_on_vps \"cat > /etc/nginx/sites-available/monitoring << 'EOF'
# Monitoring services configuration

# N8N subdomain
server {
    listen 80;
    server_name n8n.${DOMAIN};
    return 301 https://\\$server_name\\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name n8n.${DOMAIN};
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/consulting.sa.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header Referrer-Policy \"no-referrer-when-downgrade\" always;
    
    # Proxy to N8N
    location / {
        proxy_pass http://localhost:${N8N_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_cache_bypass \\$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Grafana subdomain
server {
    listen 80;
    server_name monitoring.${DOMAIN};
    return 301 https://\\$server_name\\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitoring.${DOMAIN};
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/consulting.sa.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header Referrer-Policy \"no-referrer-when-downgrade\" always;
    
    # Proxy to Grafana
    location / {
        proxy_pass http://localhost:${GRAFANA_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_cache_bypass \\$http_upgrade;
    }
}

# Prometheus access (protected)
server {
    listen 80;
    server_name metrics.${DOMAIN};
    return 301 https://\\$server_name\\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name metrics.${DOMAIN};
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/consulting.sa.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozSSL:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header Referrer-Policy \"no-referrer-when-downgrade\" always;
    
    # Basic authentication
    auth_basic \"Prometheus Metrics\";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Proxy to Prometheus
    location / {
        proxy_pass http://localhost:${PROMETHEUS_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        proxy_cache_bypass \\$http_upgrade;
    }
}
EOF\" \"Creating Nginx configuration for monitoring\"

    # Create basic auth password file for Prometheus
    run_on_vps \"apt-get install -y apache2-utils\" \"Installing apache2-utils\"
    run_on_vps \"htpasswd -bc /etc/nginx/.htpasswd admin agentic-platform-admin-2025\" \"Creating basic auth for Prometheus\"

    # Enable the monitoring site
    run_on_vps \"ln -sf /etc/nginx/sites-available/monitoring /etc/nginx/sites-enabled/\" \"Enabling monitoring site\"

    # Test Nginx configuration
    echo -e \"${YELLOW}Testing Nginx configuration...${NC}\"
    if run_on_vps \"nginx -t\" \"Testing Nginx config\"; then
        echo -e \"${GREEN}✓ Nginx configuration valid${NC}\"
        run_on_vps \"systemctl reload nginx\" \"Reloading Nginx\"
    else
        echo -e \"${RED}❌ Nginx configuration test failed${NC}\"
        exit 1
    fi

    echo -e \"${GREEN}✅ Nginx configuration for monitoring created${NC}\"
    echo \"\"
}

# Function to deploy monitoring services
deploy_monitoring_services() {
    echo -e \"${BLUE}Phase 6: Deploying Monitoring Services${NC}\"
    
    # Start monitoring services
    run_on_vps \"cd /opt/monitoring && docker compose up -d\" \"Starting monitoring services\"
    
    # Wait for services to be ready
    echo -e \"${YELLOW}Waiting for services to be ready...${NC}\"
    sleep 30
    
    # Check service status
    run_on_vps \"cd /opt/monitoring && docker compose ps\" \"Checking service status\"
    
    echo -e \"${GREEN}✅ Monitoring services deployed${NC}\"
    echo \"\"
}

# Function to setup application metrics endpoints
setup_application_metrics() {
    echo -e \"${BLUE}Phase 7: Setting up Application Metrics Endpoints${NC}\"
    
    # Create metrics endpoint for Next.js frontend
    run_on_vps \"cat > /opt/agentic-platform/metrics-middleware.js << 'EOF'
// Metrics middleware for Next.js application
const promClient = require('prom-client');

// Create a Registry to register the metrics
const register = new promClient.Registry();

// Add a default label which is added to all metrics
register.setDefaultLabels({
  app: 'agentic-frontend',
  environment: 'production'
});

// Enable the collection of default metrics
promClient.collectDefaultMetrics({ register });

// Create custom metrics
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

const httpRequestCounter = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeUsers = new promClient.Gauge({
  name: 'active_users',
  help: 'Number of active users'
});

// Register the custom metrics
register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestCounter);
register.registerMetric(activeUsers);

module.exports = {
  register,
  httpRequestDurationMicroseconds,
  httpRequestCounter,
  activeUsers
};
EOF\" \"Creating metrics middleware\"

    echo -e \"${GREEN}✅ Application metrics endpoints configured${NC}\"
    echo \"\"
}

# Function to validate monitoring deployment
validate_monitoring_deployment() {
    echo -e \"${BLUE}Phase 8: Validating Monitoring Deployment${NC}\"
    
    # Check if services are responding
    echo -e \"${YELLOW}Checking service health...${NC}\"
    
    # Check N8N
    if run_on_vps \"curl -f http://localhost:${N8N_PORT}/healthz\" \"Checking N8N health\"; then
        echo -e \"${GREEN}✓ N8N is healthy${NC}\"
    else
        echo -e \"${YELLOW}⚠ N8N health check failed (may still be starting)${NC}\"
    fi
    
    # Check Grafana
    if run_on_vps \"curl -f http://localhost:${GRAFANA_PORT}/api/health\" \"Checking Grafana health\"; then
        echo -e \"${GREEN}✓ Grafana is healthy${NC}\"
    else
        echo -e \"${YELLOW}⚠ Grafana health check failed (may still be starting)${NC}\"
    fi
    
    # Check Prometheus
    if run_on_vps \"curl -f http://localhost:${PROMETHEUS_PORT}/-/healthy\" \"Checking Prometheus health\"; then
        echo -e \"${GREEN}✓ Prometheus is healthy${NC}\"
    else
        echo -e \"${YELLOW}⚠ Prometheus health check failed (may still be starting)${NC}\"
    fi
    
    echo -e \"${GREEN}✅ Monitoring deployment validation completed${NC}\"
    echo \"\"
}

# Function to display deployment summary
display_summary() {
    echo -e \"${PURPLE}🎉 Monitoring Deployment Summary${NC}\"
    echo \"\"
    echo -e \"${BLUE}Access Information:${NC}\"
    echo \"- N8N Workflows: https://n8n.$DOMAIN\"
    echo \"- Grafana Dashboards: https://monitoring.$DOMAIN\"
    echo \"- Prometheus Metrics: https://metrics.$DOMAIN (admin/agentic-platform-admin-2025)\"
    echo \"\"
    echo -e \"${BLUE}Default Credentials:${NC}\"
    echo \"- Grafana: admin / agentic-platform-admin-2025\"
    echo \"- Prometheus: admin / agentic-platform-admin-2025\"
    echo \"\"
    echo -e \"${BLUE}Management Commands:${NC}\"
    echo \"- Check Status: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose ps'\"
    echo \"- View Logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose logs -f'\"
    echo \"- Restart Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose restart'\"
    echo \"- Stop Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose down'\"
    echo \"\"
    echo -e \"${BLUE}Next Steps:${NC}\"
    echo \"1. Configure notification channels (Slack, Email, Telegram) in environment variables\"
    echo \"2. Import N8N workflows at https://n8n.$DOMAIN\"
    echo \"3. Set up custom Grafana dashboards at https://monitoring.$DOMAIN\"
    echo \"4. Configure alert rules in Prometheus\"
    echo \"5. Test alert notifications\"
    echo \"\"
    echo -e \"${BLUE}Environment Variables to Configure:${NC}\"
    echo \"- SLACK_WEBHOOK_URL: Your Slack webhook URL for notifications\"
    echo \"- ALERT_EMAIL: Email address for critical alerts\"
    echo \"- SMTP_HOST, SMTP_USER, SMTP_PASS: Email server configuration\"
    echo \"- TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID: Telegram bot configuration\"
    echo \"\"
    echo -e \"${GREEN}✅ Monitoring system deployed successfully!${NC}\"
    echo -e \"${YELLOW}📊 Your production system continues to run normally${NC}\"
}

# Main execution flow
main() {
    echo -e \"${PURPLE}Starting monitoring deployment process...${NC}\"
    echo \"\"
    
    validate_prerequisites
    setup_directories
    deploy_configurations
    setup_grafana_datasources
    setup_nginx_config
    deploy_monitoring_services
    setup_application_metrics
    validate_monitoring_deployment
    display_summary
    
    echo -e \"${PURPLE}🚀 Monitoring system deployment completed!${NC}\"
}

# Execute main function
main \"$@\"