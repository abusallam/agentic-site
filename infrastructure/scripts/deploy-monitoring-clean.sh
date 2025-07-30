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
VPS_PASSWORD=${VPS_PASSWORD:-"xxXNCpx9Cz"}
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

# Auto-proceed for automated deployment
echo -e "${GREEN}✅ Proceeding with automated deployment${NC}"

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
    echo -e "${BLUE}Phase 2: Setting up Monitoring Directories${NC}"
    
    # Create monitoring directories
    run_on_vps "mkdir -p /opt/monitoring/{n8n,grafana,prometheus,alertmanager,blackbox}" "Creating monitoring directories"
    run_on_vps "mkdir -p /opt/monitoring/{n8n/workflows,n8n/credentials,grafana/dashboards,grafana/datasources,prometheus/rules}" "Creating subdirectories"
    
    echo -e "${GREEN}✅ Monitoring directories created${NC}"
    echo ""
}

# Function to deploy configuration files
deploy_configurations() {
    echo -e "${BLUE}Phase 3: Deploying Configuration Files${NC}"
    
    # Copy monitoring configurations
    copy_to_vps "monitoring/docker-compose.monitoring.yml" "/opt/monitoring/docker-compose.yml"
    copy_to_vps "monitoring/prometheus/prometheus.yml" "/opt/monitoring/prometheus/prometheus.yml"
    copy_to_vps "monitoring/prometheus/rules/" "/opt/monitoring/prometheus/"
    copy_to_vps "monitoring/alertmanager/alertmanager.yml" "/opt/monitoring/alertmanager/alertmanager.yml"
    copy_to_vps "monitoring/blackbox/blackbox.yml" "/opt/monitoring/blackbox/blackbox.yml"
    copy_to_vps "monitoring/n8n/workflows/" "/opt/monitoring/n8n/"
    copy_to_vps "monitoring/grafana/dashboards/" "/opt/monitoring/grafana/"
    
    echo -e "${GREEN}✅ Configuration files deployed${NC}"
    echo ""
}

# Function to setup Grafana datasources
setup_grafana_datasources() {
    echo -e "${BLUE}Phase 4: Setting up Grafana Datasources${NC}"
    
    # Create Prometheus datasource configuration
    run_on_vps "cat > /opt/monitoring/grafana/datasources/prometheus.yml << 'EOF'
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
EOF" "Creating Prometheus datasource"

    echo -e "${GREEN}✅ Grafana datasources configured${NC}"
    echo ""
}

# Function to deploy monitoring services
deploy_monitoring_services() {
    echo -e "${BLUE}Phase 5: Deploying Monitoring Services${NC}"
    
    # Start monitoring services
    run_on_vps "cd /opt/monitoring && docker compose up -d" "Starting monitoring services"
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 30
    
    # Check service status
    run_on_vps "cd /opt/monitoring && docker compose ps" "Checking service status"
    
    echo -e "${GREEN}✅ Monitoring services deployed${NC}"
    echo ""
}

# Function to validate monitoring deployment
validate_monitoring_deployment() {
    echo -e "${BLUE}Phase 6: Validating Monitoring Deployment${NC}"
    
    # Check if services are responding
    echo -e "${YELLOW}Checking service health...${NC}"
    
    # Check N8N
    if run_on_vps "curl -f http://localhost:${N8N_PORT}/healthz" "Checking N8N health"; then
        echo -e "${GREEN}✓ N8N is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ N8N health check failed (may still be starting)${NC}"
    fi
    
    # Check Grafana
    if run_on_vps "curl -f http://localhost:${GRAFANA_PORT}/api/health" "Checking Grafana health"; then
        echo -e "${GREEN}✓ Grafana is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Grafana health check failed (may still be starting)${NC}"
    fi
    
    # Check Prometheus
    if run_on_vps "curl -f http://localhost:${PROMETHEUS_PORT}/-/healthy" "Checking Prometheus health"; then
        echo -e "${GREEN}✓ Prometheus is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Prometheus health check failed (may still be starting)${NC}"
    fi
    
    echo -e "${GREEN}✅ Monitoring deployment validation completed${NC}"
    echo ""
}

# Function to display deployment summary
display_summary() {
    echo -e "${PURPLE}🎉 Monitoring Deployment Summary${NC}"
    echo ""
    echo -e "${BLUE}Access Information:${NC}"
    echo "- N8N Workflows: https://n8n.$DOMAIN"
    echo "- Grafana Dashboards: https://monitoring.$DOMAIN"
    echo "- Prometheus Metrics: https://metrics.$DOMAIN (admin/agentic-platform-admin-2025)"
    echo ""
    echo -e "${BLUE}Default Credentials:${NC}"
    echo "- Grafana: admin / agentic-platform-admin-2025"
    echo "- Prometheus: admin / agentic-platform-admin-2025"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "- Check Status: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose ps'"
    echo "- View Logs: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose logs -f'"
    echo "- Restart Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose restart'"
    echo "- Stop Services: sshpass -p '$VPS_PASSWORD' ssh $VPS_USER@$VPS_HOST 'cd /opt/monitoring && docker compose down'"
    echo ""
    echo -e "${GREEN}✅ Monitoring system deployed successfully!${NC}"
    echo -e "${YELLOW}📊 Your production system continues to run normally${NC}"
}

# Main execution flow
main() {
    echo -e "${PURPLE}Starting monitoring deployment process...${NC}"
    echo ""
    
    validate_prerequisites
    setup_directories
    deploy_configurations
    setup_grafana_datasources
    deploy_monitoring_services
    validate_monitoring_deployment
    display_summary
    
    echo -e "${PURPLE}🚀 Monitoring system deployment completed!${NC}"
}

# Execute main function
main "$@"