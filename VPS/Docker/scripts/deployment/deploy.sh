#!/bin/bash

# Deployment Orchestrator - Standardized Container Deployment
# This script handles deployment of applications with intelligent conflict resolution
# Usage: ./deploy.sh --environment ENV --service SERVICE [--domain DOMAIN]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/config"
LOGS_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load environment variables
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    source "$PROJECT_ROOT/.env"
else
    echo -e "${RED}Error: .env file not found. Copy .env.template to .env and configure.${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/deployments"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/deployment.log"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# SSH connection function
ssh_connect() {
    local command="$1"
    local max_attempts="${MAX_RETRY_ATTEMPTS:-3}"
    local timeout="${CONNECTION_TIMEOUT:-30}"
    
    for attempt in $(seq 1 $max_attempts); do
        if [[ -n "${SSH_KEY_PATH:-}" && -f "$SSH_KEY_PATH" ]]; then
            if timeout "$timeout" ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout="$timeout" "$VPS_USERNAME@$VPS_IP" "$command" 2>/dev/null; then
                return 0
            fi
        fi
        
        if command -v sshpass >/dev/null 2>&1; then
            if timeout "$timeout" sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout="$timeout" "$VPS_USERNAME@$VPS_IP" "$command" 2>/dev/null; then
                return 0
            fi
        fi
        
        if [[ $attempt -lt $max_attempts ]]; then
            log_warn "Connection attempt $attempt failed, retrying..."
            sleep 2
        fi
    done
    
    return 1
}

# Generate deployment ID
generate_deployment_id() {
    echo "deploy-$(date +%Y%m%d-%H%M%S)-$(openssl rand -hex 4)"
}

# Check deployment prerequisites
check_prerequisites() {
    local environment="$1"
    local service="$2"
    
    log_info "Checking deployment prerequisites..."
    
    # Check VPS connection
    if ! ssh_connect "echo 'Connection test'"; then
        log_error "Cannot connect to VPS"
        return 1
    fi
    
    # Check Docker availability
    if ! ssh_connect "command -v docker >/dev/null 2>&1"; then
        log_error "Docker not available on VPS"
        return 1
    fi
    
    # Check available resources
    local resource_check
    resource_check=$(ssh_connect "
        echo 'CPU_USAGE:' \$(top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1)
        echo 'MEMORY_USAGE:' \$(free | awk '/^Mem:/ {printf \"%.1f\", \$3/\$2 * 100}')
        echo 'DISK_USAGE:' \$(df / | awk 'NR==2 {print \$5}' | cut -d'%' -f1)
    ")
    
    echo "$resource_check"
    
    # Parse resource usage
    local cpu_usage=$(echo "$resource_check" | grep CPU_USAGE | cut -d: -f2 | tr -d ' ')
    local memory_usage=$(echo "$resource_check" | grep MEMORY_USAGE | cut -d: -f2 | tr -d ' ')
    local disk_usage=$(echo "$resource_check" | grep DISK_USAGE | cut -d: -f2 | tr -d ' ')
    
    # Check resource thresholds
    if (( $(echo "$cpu_usage > ${MAX_CPU_USAGE_PERCENT:-80}" | bc -l) )); then
        log_warn "High CPU usage detected: ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage > ${MAX_MEMORY_USAGE_PERCENT:-85}" | bc -l) )); then
        log_warn "High memory usage detected: ${memory_usage}%"
    fi
    
    if (( disk_usage > ${MAX_DISK_USAGE_PERCENT:-90} )); then
        log_warn "High disk usage detected: ${disk_usage}%"
    fi
    
    log_success "Prerequisites check completed"
    return 0
}

# Find available port
find_available_port() {
    local base_port="$1"
    local environment="$2"
    
    log_info "Finding available port starting from $base_port..."
    
    local available_port
    available_port=$(ssh_connect "
        base_port=$base_port
        for port in \$(seq \$base_port \$((\$base_port + 100))); do
            if ! netstat -tln 2>/dev/null | grep -q \":\$port \" && ! ss -tln 2>/dev/null | grep -q \":\$port \"; then
                echo \$port
                break
            fi
        done
    ")
    
    if [[ -n "$available_port" ]]; then
        log_success "Available port found: $available_port"
        echo "$available_port"
    else
        log_error "No available port found starting from $base_port"
        return 1
    fi
}

# Create Docker Compose configuration
create_docker_compose() {
    local service="$1"
    local environment="$2"
    local domain="$3"
    local frontend_port="$4"
    local backend_port="$5"
    
    local compose_file="/tmp/docker-compose-${service}-${environment}.yml"
    
    cat > "$compose_file" << EOF
version: '3.8'

services:
  ${service}-frontend:
    image: ${service}/frontend:latest
    container_name: ${service}-frontend-${environment}
    ports:
      - "${frontend_port}:3000"
    environment:
      - NODE_ENV=${environment}
      - NEXT_PUBLIC_DOMAIN=${domain}
      - NEXT_PUBLIC_API_URL=https://${domain}/api
    networks:
      - ${service}-network
    restart: ${CONTAINER_RESTART_POLICY:-unless-stopped}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '${CONTAINER_CPU_LIMIT:-1.0}'
          memory: ${CONTAINER_MEMORY_LIMIT:-1g}
        reservations:
          cpus: '0.5'
          memory: 512m

  ${service}-backend:
    image: ${service}/backend:latest
    container_name: ${service}-backend-${environment}
    ports:
      - "${backend_port}:8000"
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=${environment}
    networks:
      - ${service}-network
    restart: ${CONTAINER_RESTART_POLICY:-unless-stopped}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '${CONTAINER_CPU_LIMIT:-1.0}'
          memory: ${CONTAINER_MEMORY_LIMIT:-1g}
        reservations:
          cpus: '0.5'
          memory: 512m

  ${service}-redis:
    image: redis:7-alpine
    container_name: ${service}-redis-${environment}
    ports:
      - "$((backend_port + 379)):6379"
    networks:
      - ${service}-network
    restart: ${CONTAINER_RESTART_POLICY:-unless-stopped}
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256m
        reservations:
          cpus: '0.1'
          memory: 128m

networks:
  ${service}-network:
    driver: bridge
    ipam:
      config:
        - subnet: ${DOCKER_NETWORK_SUBNET:-172.20.0.0/16}

volumes:
  ${service}-data:
    driver: local
EOF

    echo "$compose_file"
}

# Deploy application
deploy_application() {
    local service="$1"
    local environment="$2"
    local domain="$3"
    local deployment_id="$4"
    
    log_info "Deploying $service in $environment environment..."
    
    # Find available ports
    local base_frontend_port=3000
    local base_backend_port=8000
    
    if [[ "$environment" == "development" ]]; then
        base_frontend_port=3001
        base_backend_port=8001
    elif [[ "$environment" == "staging" ]]; then
        base_frontend_port=3002
        base_backend_port=8002
    fi
    
    local frontend_port
    local backend_port
    
    frontend_port=$(find_available_port "$base_frontend_port" "$environment")
    backend_port=$(find_available_port "$base_backend_port" "$environment")
    
    if [[ -z "$frontend_port" || -z "$backend_port" ]]; then
        log_error "Could not find available ports for deployment"
        return 1
    fi
    
    # Create Docker Compose configuration
    local compose_file
    compose_file=$(create_docker_compose "$service" "$environment" "$domain" "$frontend_port" "$backend_port")
    
    # Copy compose file to VPS
    if [[ -n "${SSH_KEY_PATH:-}" && -f "$SSH_KEY_PATH" ]]; then
        scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$compose_file" "$VPS_USERNAME@$VPS_IP:/tmp/"
    elif command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$compose_file" "$VPS_USERNAME@$VPS_IP:/tmp/"
    fi
    
    # Deploy on VPS
    local compose_filename=$(basename "$compose_file")
    ssh_connect "
        echo 'Setting up deployment directory...'
        mkdir -p /opt/deployments/${service}-${environment}
        cd /opt/deployments/${service}-${environment}
        
        echo 'Moving compose file...'
        mv /tmp/$compose_filename docker-compose.yml
        
        echo 'Creating deployment backup...'
        mkdir -p /opt/backups/deployments
        tar -czf /opt/backups/deployments/${deployment_id}.tar.gz . 2>/dev/null || echo 'Backup creation failed'
        
        echo 'Starting deployment...'
        docker-compose down 2>/dev/null || echo 'No existing containers to stop'
        docker-compose up -d
        
        echo 'Waiting for services to start...'
        sleep 30
        
        echo 'Checking deployment status...'
        docker-compose ps
        
        echo 'Testing service health...'
        for i in {1..10}; do
            if curl -f http://localhost:${frontend_port}/api/health 2>/dev/null; then
                echo 'Frontend health check passed'
                break
            fi
            echo \"Health check attempt \$i failed, retrying...\"
            sleep 10
        done
        
        if curl -f http://localhost:${backend_port}/health 2>/dev/null; then
            echo 'Backend health check passed'
        else
            echo 'Backend health check failed'
        fi
    "
    
    # Clean up local compose file
    rm -f "$compose_file"
    
    # Save deployment information
    cat > "$CONFIG_DIR/deployments/${deployment_id}.json" << EOF
{
  "deployment_id": "$deployment_id",
  "service": "$service",
  "environment": "$environment",
  "domain": "$domain",
  "frontend_port": $frontend_port,
  "backend_port": $backend_port,
  "redis_port": $((backend_port + 379)),
  "deployed_at": "$(date -Iseconds)",
  "status": "deployed"
}
EOF
    
    log_success "Deployment completed: $deployment_id"
    
    # Configure SSL if domain provided
    if [[ -n "$domain" && "$domain" != "localhost" ]]; then
        log_info "Configuring SSL for domain: $domain"
        "$PROJECT_ROOT/scripts/ssl/ssl-manager.sh" --setup-domain "$domain"
    fi
    
    return 0
}

# Main deployment function
main_deploy() {
    local environment=""
    local service=""
    local domain=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                environment="$2"
                shift 2
                ;;
            --service)
                service="$2"
                shift 2
                ;;
            --domain)
                domain="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    # Validate required arguments
    if [[ -z "$environment" || -z "$service" ]]; then
        echo -e "${RED}Error: --environment and --service are required${NC}"
        echo "Usage: $0 --environment ENV --service SERVICE [--domain DOMAIN]"
        exit 1
    fi
    
    # Set default domain if not provided
    if [[ -z "$domain" ]]; then
        if [[ "$environment" == "production" ]]; then
            domain="${service}.${DEFAULT_DOMAIN:-consulting.sa}"
        else
            domain="${service}-${environment}.${DEFAULT_DOMAIN:-consulting.sa}"
        fi
    fi
    
    local deployment_id
    deployment_id=$(generate_deployment_id)
    
    echo -e "${PURPLE}🚀 Deployment Orchestrator - Standardized Container Deployment${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo "Service: $service"
    echo "Environment: $environment"
    echo "Domain: $domain"
    echo "Deployment ID: $deployment_id"
    echo "VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    # Step 1: Check prerequisites
    echo -e "${CYAN}📋 Step 1: Checking prerequisites...${NC}"
    if ! check_prerequisites "$environment" "$service"; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    # Step 2: Deploy application
    echo ""
    echo -e "${CYAN}🐳 Step 2: Deploying application...${NC}"
    if ! deploy_application "$service" "$environment" "$domain" "$deployment_id"; then
        log_error "Deployment failed"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Deployment Completed Successfully!${NC}"
    echo ""
    echo -e "${BLUE}Deployment Information:${NC}"
    echo "- Deployment ID: $deployment_id"
    echo "- Service: $service"
    echo "- Environment: $environment"
    echo "- Domain: $domain"
    echo ""
    echo -e "${BLUE}Access Information:${NC}"
    echo "- Application: https://$domain"
    echo "- Health Check: https://$domain/api/health"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "- View logs: docker-compose -f /opt/deployments/${service}-${environment}/docker-compose.yml logs -f"
    echo "- Restart: docker-compose -f /opt/deployments/${service}-${environment}/docker-compose.yml restart"
    echo "- Stop: docker-compose -f /opt/deployments/${service}-${environment}/docker-compose.yml down"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update DNS to point $domain to $VPS_IP"
    echo "2. Test application functionality"
    echo "3. Monitor deployment health"
}

# Command line argument handling
case "${1:-}" in
    --environment)
        main_deploy "$@"
        ;;
    --help|-h)
        echo "Deployment Orchestrator - Usage:"
        echo ""
        echo "  --environment ENV        Deployment environment (production|staging|development)"
        echo "  --service SERVICE        Service name to deploy"
        echo "  --domain DOMAIN          Domain name (optional, auto-generated if not provided)"
        echo "  --help, -h               Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh --environment production --service myapp"
        echo "  ./deploy.sh --environment development --service myapp --domain dev.myapp.com"
        echo "  ./deploy.sh --environment staging --service api --domain staging-api.example.com"
        ;;
    *)
        echo -e "${RED}Error: Missing required arguments${NC}"
        echo "Usage: $0 --environment ENV --service SERVICE [--domain DOMAIN]"
        echo "Use --help for more information"
        exit 1
        ;;
esac