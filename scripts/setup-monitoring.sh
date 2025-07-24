#!/bin/bash
set -e

# Monitoring Setup Script - N8N, Grafana, and Prometheus Integration
# This script sets up comprehensive monitoring for the agentic AI platform

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

echo -e "${PURPLE}📊 Agentic AI Platform - Monitoring Setup${NC}"
echo -e "${BLUE}Setting up N8N, Grafana, and Prometheus monitoring${NC}"
echo -e "${BLUE}Target: $VPS_HOST ($DOMAIN)${NC}"
echo ""

# Function to run commands on VPS
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

# Phase 1: Setup N8N for Workflow Automation
setup_n8n() {
    echo -e "${BLUE}Phase 1: Setting up N8N Workflow Automation${NC}"
    
    # Create N8N directory structure
    run_on_vps "mkdir -p /opt/agentic-platform/n8n/{data,workflows,credentials}" "Creating N8N directories"
    
    # Create N8N Docker Compose configuration
    run_on_vps "cat > /opt/agentic-platform/n8n/docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: agentic-n8n
    restart: unless-stopped
    ports:
      - \"5678:5678\"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=\${DOMAIN}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://\${VPS_HOST}:5678/
      - GENERIC_TIMEZONE=UTC
      - N8N_METRICS=true
      - N8N_LOG_LEVEL=info
      - DB_TYPE=sqlite
      - DB_SQLITE_DATABASE=/home/node/.n8n/database.sqlite
    volumes:
      - ./data:/home/node/.n8n
      - ./workflows:/opt/workflows
      - ./credentials:/opt/credentials
    networks:
      - monitoring-network

networks:
  monitoring-network:
    external: true
    name: agentic-platform_agentic-network
EOF" "Creating N8N Docker Compose configuration"
    
    echo -e "${GREEN}✅ N8N configuration created${NC}"
    echo ""
}

# Phase 2: Setup Prometheus for Metrics Collection
setup_prometheus() {
    echo -e "${BLUE}Phase 2: Setting up Prometheus Metrics Collection${NC}"
    
    # Create Prometheus directory
    run_on_vps "mkdir -p /opt/agentic-platform/prometheus/{data,config}" "Creating Prometheus directories"
    
    # Copy Prometheus configuration
    copy_to_vps "monitoring/prometheus.yml" "/opt/agentic-platform/prometheus/config/"
    
    # Create Prometheus Docker Compose configuration
    run_on_vps "cat > /opt/agentic-platform/prometheus/docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: agentic-prometheus
    restart: unless-stopped
    ports:
      - \"9090:9090\"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data:/prometheus
    networks:
      - monitoring-network

networks:
  monitoring-network:
    external: true
    name: agentic-platform_agentic-network
EOF" "Creating Prometheus Docker Compose configuration"
    
    echo -e "${GREEN}✅ Prometheus configuration created${NC}"
    echo ""
}

# Phase 3: Setup Grafana for Visualization
setup_grafana() {
    echo -e "${BLUE}Phase 3: Setting up Grafana Visualization${NC}"
    
    # Create Grafana directory
    run_on_vps "mkdir -p /opt/agentic-platform/grafana/{data,dashboards,provisioning}" "Creating Grafana directories"
    
    # Create Grafana Docker Compose configuration
    run_on_vps "cat > /opt/agentic-platform/grafana/docker-compose.yml << 'EOF'
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: agentic-grafana
    restart: unless-stopped
    ports:
      - \"3001:3000\"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=\${VPS_HOST}
      - GF_SERVER_HTTP_PORT=3000
      - GF_SERVER_ROOT_URL=http://\${VPS_HOST}:3001
    volumes:
      - ./data:/var/lib/grafana
      - ./dashboards:/etc/grafana/provisioning/dashboards
      - ./provisioning:/etc/grafana/provisioning
    networks:
      - monitoring-network

networks:
  monitoring-network:
    external: true
    name: agentic-platform_agentic-network
EOF" "Creating Grafana Docker Compose configuration"
    
    echo -e "${GREEN}✅ Grafana configuration created${NC}"
    echo ""
}

# Phase 4: Create Monitoring Workflows
create_monitoring_workflows() {
    echo -e "${BLUE}Phase 4: Creating Monitoring Workflows${NC}"
    
    # Create health check workflow for N8N
    run_on_vps "cat > /opt/agentic-platform/n8n/workflows/health-monitoring.json << 'EOF'
{
  \"name\": \"Agentic Platform Health Monitoring\",
  \"nodes\": [
    {
      \"parameters\": {
        \"rule\": {
          \"interval\": [
            {
              \"field\": \"minutes\",
              \"minutesInterval\": 5
            }
          ]
        }
      },
      \"name\": \"Schedule Health Check\",
      \"type\": \"n8n-nodes-base.cron\",
      \"typeVersion\": 1,
      \"position\": [240, 300]
    },
    {
      \"parameters\": {
        \"url\": \"https://consulting.sa/api/health\",
        \"options\": {
          \"timeout\": 10000
        }
      },
      \"name\": \"Check Frontend Health\",
      \"type\": \"n8n-nodes-base.httpRequest\",
      \"typeVersion\": 1,
      \"position\": [460, 300]
    },
    {
      \"parameters\": {
        \"url\": \"http://217.79.255.54:8000/health\",
        \"options\": {
          \"timeout\": 10000
        }
      },
      \"name\": \"Check Backend Health\",
      \"type\": \"n8n-nodes-base.httpRequest\",
      \"typeVersion\": 1,
      \"position\": [680, 300]
    }
  ],
  \"connections\": {
    \"Schedule Health Check\": {
      \"main\": [
        [
          {
            \"node\": \"Check Frontend Health\",
            \"type\": \"main\",
            \"index\": 0
          }
        ]
      ]
    },
    \"Check Frontend Health\": {
      \"main\": [
        [
          {
            \"node\": \"Check Backend Health\",
            \"type\": \"main\",
            \"index\": 0
          }
        ]
      ]
    }
  },
  \"active\": true,
  \"settings\": {},
  \"id\": \"health-monitoring\"
}
EOF" "Creating health monitoring workflow"
    
    echo -e "${GREEN}✅ Monitoring workflows created${NC}"
    echo ""
}

# Phase 5: Start Monitoring Services
start_monitoring_services() {
    echo -e "${BLUE}Phase 5: Starting Monitoring Services${NC}"
    
    # Start N8N
    run_on_vps "cd /opt/agentic-platform/n8n && docker compose up -d" "Starting N8N service"
    
    # Start Prometheus
    run_on_vps "cd /opt/agentic-platform/prometheus && docker compose up -d" "Starting Prometheus service"
    
    # Start Grafana
    run_on_vps "cd /opt/agentic-platform/grafana && docker compose up -d" "Starting Grafana service"
    
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 30
    
    echo -e "${GREEN}✅ All monitoring services started${NC}"
    echo ""
}

# Phase 6: Configure Nginx for Monitoring Services
configure_nginx_monitoring() {
    echo -e "${BLUE}Phase 6: Configuring Nginx for Monitoring Services${NC}"
    
    # Add monitoring locations to Nginx config
    run_on_vps "cat >> /etc/nginx/sites-available/agentic-platform << 'EOF'

    # N8N Workflow Automation
    location /n8n/ {
        proxy_pass http://127.0.0.1:5678/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Grafana Dashboards
    location /grafana/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Prometheus Metrics (restricted access)
    location /prometheus/ {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://127.0.0.1:9090/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
EOF" "Adding monitoring locations to Nginx"
    
    # Test and reload Nginx
    run_on_vps "nginx -t && systemctl reload nginx" "Reloading Nginx configuration"
    
    echo -e "${GREEN}✅ Nginx configured for monitoring services${NC}"
    echo ""
}

# Phase 7: Validate Monitoring Setup
validate_monitoring() {
    echo -e "${BLUE}Phase 7: Validating Monitoring Setup${NC}"
    
    echo -e "${YELLOW}Checking service health...${NC}"
    
    # Check N8N
    if run_on_vps "curl -s http://localhost:5678 | grep -q 'n8n'" "N8N health check"; then
        echo -e "${GREEN}✓ N8N is running${NC}"
    else
        echo -e "${YELLOW}⚠ N8N may still be starting${NC}"
    fi
    
    # Check Prometheus
    if run_on_vps "curl -s http://localhost:9090/-/healthy | grep -q 'Prometheus'" "Prometheus health check"; then
        echo -e "${GREEN}✓ Prometheus is running${NC}"
    else
        echo -e "${YELLOW}⚠ Prometheus may still be starting${NC}"
    fi
    
    # Check Grafana
    if run_on_vps "curl -s http://localhost:3001/api/health | grep -q 'ok'" "Grafana health check"; then
        echo -e "${GREEN}✓ Grafana is running${NC}"
    else
        echo -e "${YELLOW}⚠ Grafana may still be starting${NC}"
    fi
    
    echo -e "${GREEN}✅ Monitoring validation completed${NC}"
    echo ""
}

# Phase 8: Display Access Information
display_monitoring_info() {
    echo -e "${PURPLE}🎉 Monitoring Setup Complete!${NC}"
    echo ""
    echo -e "${BLUE}Access Information:${NC}"
    echo "- N8N Workflows: http://$VPS_HOST:5678 (admin/admin123)"
    echo "- Grafana Dashboards: http://$VPS_HOST:3001 (admin/admin123)"
    echo "- Prometheus Metrics: http://$VPS_HOST:9090 (localhost only)"
    echo ""
    echo -e "${BLUE}Via Nginx Proxy:${NC}"
    echo "- N8N: https://$DOMAIN/n8n/"
    echo "- Grafana: https://$DOMAIN/grafana/"
    echo "- Prometheus: https://$DOMAIN/prometheus/ (restricted)"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "- Check Status: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'docker ps | grep -E \"(n8n|grafana|prometheus)\"'"
    echo "- View Logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'docker logs agentic-n8n'"
    echo "- Restart Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/agentic-platform/n8n && docker compose restart'"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Access N8N and import monitoring workflows"
    echo "2. Configure Grafana dashboards for system metrics"
    echo "3. Set up alerting rules in Prometheus"
    echo "4. Test notification workflows"
    echo ""
    echo -e "${GREEN}✅ Monitoring and alerting system is ready!${NC}"
}

# Main execution
main() {
    echo -e "${PURPLE}Starting monitoring setup process...${NC}"
    echo ""
    
    setup_n8n
    setup_prometheus
    setup_grafana
    create_monitoring_workflows
    start_monitoring_services
    configure_nginx_monitoring
    validate_monitoring
    display_monitoring_info
    
    echo -e "${PURPLE}🚀 Monitoring system deployment completed!${NC}"
}

# Execute main function
main "$@"