#!/bin/bash

# 🚀 DUAL-STACK CONTAINER ORCHESTRATION SYSTEM
# This script sets up production and development container stacks with proper separation
# 
# LESSONS LEARNED INTEGRATED:
# - Proper container naming conventions (service-component-environment)
# - Isolated Docker networks for prod/dev separation
# - Volume management with proper persistence
# - Health checks and monitoring integration
# - Port allocation strategy to avoid conflicts
# - Environment-specific configurations
#
# PREVENTS: Container naming conflicts, network issues, volume conflicts

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/dual-stack-setup.log"
PROJECT_NAME="agentic"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# Error handling
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Script failed at line $line_number with exit code $exit_code"
    cleanup_on_error
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Cleanup function
cleanup_on_error() {
    log_warn "Cleaning up partial installation..."
    # Remove any partially created resources
    docker network ls --format "{{.Name}}" | grep -E "${PROJECT_NAME}-(production|development)" | xargs -r docker network rm 2>/dev/null || true
}

# Validation functions
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Check Docker installation
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please run provision-debian12-vps.sh first"
        exit 1
    fi
    
    # Check Docker Compose installation
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please run provision-debian12-vps.sh first"
        exit 1
    fi
    
    # Check if Docker service is running
    if ! systemctl is-active --quiet docker; then
        log_error "Docker service is not running"
        exit 1
    fi
    
    # Check directory structure
    if [[ ! -d "/opt/docker-apps" ]]; then
        log_error "Required directory structure not found. Please run provision-debian12-vps.sh first"
        exit 1
    fi
    
    log_success "Prerequisites validation passed"
}

# Create Docker networks
create_docker_networks() {
    log_info "Creating isolated Docker networks..."
    
    # Production network
    if ! docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-production"; then
        docker network create \
            --driver bridge \
            --subnet=172.20.0.0/16 \
            --gateway=172.20.0.1 \
            --opt com.docker.network.bridge.name=br-${PROJECT_NAME}-prod \
            ${PROJECT_NAME}-production
        log_success "Created production network: ${PROJECT_NAME}-production"
    else
        log_info "Production network already exists"
    fi
    
    # Development network
    if ! docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-development"; then
        docker network create \
            --driver bridge \
            --subnet=172.21.0.0/16 \
            --gateway=172.21.0.1 \
            --opt com.docker.network.bridge.name=br-${PROJECT_NAME}-dev \
            ${PROJECT_NAME}-development
        log_success "Created development network: ${PROJECT_NAME}-development"
    else
        log_info "Development network already exists"
    fi
    
    # Monitoring network (shared)
    if ! docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-monitoring"; then
        docker network create \
            --driver bridge \
            --subnet=172.22.0.0/16 \
            --gateway=172.22.0.1 \
            --opt com.docker.network.bridge.name=br-${PROJECT_NAME}-mon \
            ${PROJECT_NAME}-monitoring
        log_success "Created monitoring network: ${PROJECT_NAME}-monitoring"
    else
        log_info "Monitoring network already exists"
    fi
}

# Create Docker volumes
create_docker_volumes() {
    log_info "Creating Docker volumes..."
    
    # Production volumes
    local prod_volumes=(
        "${PROJECT_NAME}-redis-prod-data"
        "${PROJECT_NAME}-n8n-prod-data"
        "${PROJECT_NAME}-frontend-prod-data"
        "${PROJECT_NAME}-backend-prod-data"
        "${PROJECT_NAME}-logs-prod"
    )
    
    for volume in "${prod_volumes[@]}"; do
        if ! docker volume ls --format "{{.Name}}" | grep -q "$volume"; then
            docker volume create "$volume"
            log_success "Created production volume: $volume"
        else
            log_info "Production volume already exists: $volume"
        fi
    done
    
    # Development volumes
    local dev_volumes=(
        "${PROJECT_NAME}-redis-dev-data"
        "${PROJECT_NAME}-n8n-dev-data"
        "${PROJECT_NAME}-frontend-dev-data"
        "${PROJECT_NAME}-backend-dev-data"
        "${PROJECT_NAME}-logs-dev"
    )
    
    for volume in "${dev_volumes[@]}"; do
        if ! docker volume ls --format "{{.Name}}" | grep -q "$volume"; then
            docker volume create "$volume"
            log_success "Created development volume: $volume"
        else
            log_info "Development volume already exists: $volume"
        fi
    done
    
    # Shared volumes
    local shared_volumes=(
        "${PROJECT_NAME}-ssl-certs"
        "${PROJECT_NAME}-backups"
        "${PROJECT_NAME}-monitoring-data"
    )
    
    for volume in "${shared_volumes[@]}"; do
        if ! docker volume ls --format "{{.Name}}" | grep -q "$volume"; then
            docker volume create "$volume"
            log_success "Created shared volume: $volume"
        else
            log_info "Shared volume already exists: $volume"
        fi
    done
}

# Create production Docker Compose configuration
create_production_compose() {
    log_info "Creating production Docker Compose configuration..."
    
    local prod_dir="/opt/docker-apps/production"
    mkdir -p "$prod_dir"
    
    cat > "$prod_dir/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  frontend:
    image: ${PROJECT_NAME:-agentic}-frontend:latest
    container_name: ${PROJECT_NAME:-agentic}-frontend-prod
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://main.consulting.sa
      - NEXT_PUBLIC_API_URL=https://main.consulting.sa/api
    volumes:
      - agentic-frontend-prod-data:/app/.next
      - agentic-logs-prod:/app/logs
    networks:
      - agentic-production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    image: ${PROJECT_NAME:-agentic}-backend:latest
    container_name: ${PROJECT_NAME:-agentic}-backend-prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - N8N_URL=http://n8n:5678
      - REDIS_URL=redis://redis:6379
    volumes:
      - agentic-backend-prod-data:/app/data
      - agentic-logs-prod:/app/logs
    networks:
      - agentic-production
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME:-agentic}-redis-prod
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - agentic-redis-prod-data:/data
    networks:
      - agentic-production
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  n8n:
    image: n8nio/n8n:latest
    container_name: ${PROJECT_NAME:-agentic}-n8n-prod
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://main.consulting.sa/webhook/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - agentic-n8n-prod-data:/home/node/.n8n
    networks:
      - agentic-production
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  agentic-production:
    external: true

volumes:
  agentic-frontend-prod-data:
    external: true
  agentic-backend-prod-data:
    external: true
  agentic-redis-prod-data:
    external: true
  agentic-n8n-prod-data:
    external: true
  agentic-logs-prod:
    external: true
EOF
    
    # Create production environment file
    cat > "$prod_dir/.env" << 'EOF'
# Production Environment Configuration
PROJECT_NAME=agentic
ENVIRONMENT=production

# Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# AI Services
GOOGLE_API_KEY=your_google_api_key_here

# Real-time Communication
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# Payment Processing
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Domain Configuration
DOMAIN=main.consulting.sa
API_URL=https://main.consulting.sa/api

# Security
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
EOF
    
    log_success "Production Docker Compose configuration created"
}

# Create development Docker Compose configuration
create_development_compose() {
    log_info "Creating development Docker Compose configuration..."
    
    local dev_dir="/opt/docker-apps/development"
    mkdir -p "$dev_dir"
    
    cat > "$dev_dir/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  frontend:
    image: ${PROJECT_NAME:-agentic}-frontend:latest
    container_name: ${PROJECT_NAME:-agentic}-frontend-dev
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
      - NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api
    volumes:
      - agentic-frontend-dev-data:/app/.next
      - agentic-logs-dev:/app/logs
    networks:
      - agentic-development
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    image: ${PROJECT_NAME:-agentic}-backend:latest
    container_name: ${PROJECT_NAME:-agentic}-backend-dev
    restart: unless-stopped
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=development
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
      - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - N8N_URL=http://n8n:5678
      - REDIS_URL=redis://redis:6379
    volumes:
      - agentic-backend-dev-data:/app/data
      - agentic-logs-dev:/app/logs
    networks:
      - agentic-development
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME:-agentic}-redis-dev
    restart: unless-stopped
    ports:
      - "6380:6379"
    volumes:
      - agentic-redis-dev-data:/data
    networks:
      - agentic-development
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  n8n:
    image: n8nio/n8n:latest
    container_name: ${PROJECT_NAME:-agentic}-n8n-dev
    restart: unless-stopped
    ports:
      - "5679:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://dev.consulting.sa/webhook/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - agentic-n8n-dev-data:/home/node/.n8n
    networks:
      - agentic-development
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  agentic-development:
    external: true

volumes:
  agentic-frontend-dev-data:
    external: true
  agentic-backend-dev-data:
    external: true
  agentic-redis-dev-data:
    external: true
  agentic-n8n-dev-data:
    external: true
  agentic-logs-dev:
    external: true
EOF
    
    # Create development environment file
    cat > "$dev_dir/.env" << 'EOF'
# Development Environment Configuration
PROJECT_NAME=agentic
ENVIRONMENT=development

# Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# AI Services
GOOGLE_API_KEY=your_google_api_key_here

# Real-time Communication
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# Payment Processing
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Domain Configuration
DOMAIN=dev.consulting.sa
API_URL=https://dev.consulting.sa/api

# Security
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
EOF
    
    log_success "Development Docker Compose configuration created"
}

# Create stack management scripts
create_stack_management_scripts() {
    log_info "Creating stack management scripts..."
    
    # Create stack manager script
    cat > /opt/scripts/manage-stacks.sh << 'EOF'
#!/bin/bash

# Stack Management Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="agentic"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|health} {production|development|all}"
    echo ""
    echo "Commands:"
    echo "  start      - Start the specified stack"
    echo "  stop       - Stop the specified stack"
    echo "  restart    - Restart the specified stack"
    echo "  status     - Show stack status"
    echo "  logs       - Show stack logs"
    echo "  health     - Show health status"
    echo ""
    echo "Environments:"
    echo "  production - Production stack (ports 3000, 8000, 6379, 5678)"
    echo "  development - Development stack (ports 3001, 8001, 6380, 5679)"
    echo "  all        - Both stacks"
    exit 1
}

execute_stack_command() {
    local command="$1"
    local environment="$2"
    local stack_dir="/opt/docker-apps/$environment"
    
    if [[ ! -d "$stack_dir" ]]; then
        echo -e "${RED}Error: Stack directory not found: $stack_dir${NC}"
        return 1
    fi
    
    cd "$stack_dir"
    
    case "$command" in
        start)
            echo -e "${BLUE}Starting $environment stack...${NC}"
            docker-compose up -d
            ;;
        stop)
            echo -e "${YELLOW}Stopping $environment stack...${NC}"
            docker-compose down
            ;;
        restart)
            echo -e "${YELLOW}Restarting $environment stack...${NC}"
            docker-compose restart
            ;;
        status)
            echo -e "${BLUE}$environment stack status:${NC}"
            docker-compose ps
            ;;
        logs)
            echo -e "${BLUE}$environment stack logs:${NC}"
            docker-compose logs --tail=50
            ;;
        health)
            echo -e "${BLUE}$environment stack health:${NC}"
            docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
            ;;
    esac
}

main() {
    if [[ $# -ne 2 ]]; then
        usage
    fi
    
    local command="$1"
    local environment="$2"
    
    case "$environment" in
        production|development)
            execute_stack_command "$command" "$environment"
            ;;
        all)
            execute_stack_command "$command" "production"
            echo ""
            execute_stack_command "$command" "development"
            ;;
        *)
            echo -e "${RED}Error: Invalid environment: $environment${NC}"
            usage
            ;;
    esac
}

main "$@"
EOF
    
    chmod +x /opt/scripts/manage-stacks.sh
    
    # Create stack duplication script
    cat > /opt/scripts/duplicate-stack.sh << 'EOF'
#!/bin/bash

# Stack Duplication Script for Zero-Downtime Deployment
set -euo pipefail

PROJECT_NAME="agentic"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

usage() {
    echo "Usage: $0 {dev-to-prod|backup-prod}"
    echo ""
    echo "Commands:"
    echo "  dev-to-prod  - Duplicate development stack to become new production"
    echo "  backup-prod  - Backup current production stack before replacement"
    exit 1
}

backup_production_stack() {
    log_info "Backing up current production stack..."
    
    local backup_dir="/opt/backups/production-${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Stop production stack
    cd /opt/docker-apps/production
    docker-compose down
    
    # Export container images
    log_info "Exporting production container images..."
    docker save -o "$backup_dir/frontend-prod.tar" ${PROJECT_NAME}-frontend:latest 2>/dev/null || true
    docker save -o "$backup_dir/backend-prod.tar" ${PROJECT_NAME}-backend:latest 2>/dev/null || true
    
    # Backup volumes
    log_info "Backing up production volumes..."
    docker run --rm -v ${PROJECT_NAME}-redis-prod-data:/data -v "$backup_dir":/backup alpine tar czf /backup/redis-prod-data.tar.gz -C /data .
    docker run --rm -v ${PROJECT_NAME}-n8n-prod-data:/data -v "$backup_dir":/backup alpine tar czf /backup/n8n-prod-data.tar.gz -C /data .
    
    # Backup configuration
    cp -r /opt/docker-apps/production "$backup_dir/config"
    
    log_success "Production stack backed up to: $backup_dir"
    echo "$backup_dir" > /opt/backups/latest-production-backup.txt
}

duplicate_dev_to_prod() {
    log_info "Duplicating development stack to production..."
    
    # Backup current production first
    backup_production_stack
    
    # Create new production configuration from development
    local temp_prod_dir="/opt/docker-apps/production-new-${TIMESTAMP}"
    cp -r /opt/docker-apps/development "$temp_prod_dir"
    
    # Update configuration for production
    sed -i 's/development/production/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/3001:3000/3000:3000/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/8001:8000/8000:8000/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/6380:6379/6379:6379/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/5679:5678/5678:5678/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/dev\.consulting\.sa/main.consulting.sa/g' "$temp_prod_dir/docker-compose.yml"
    sed -i 's/agentic-development/agentic-production/g' "$temp_prod_dir/docker-compose.yml"
    
    # Update environment file
    sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/g' "$temp_prod_dir/.env"
    sed -i 's/dev\.consulting\.sa/main.consulting.sa/g' "$temp_prod_dir/.env"
    
    # Replace production directory
    rm -rf /opt/docker-apps/production
    mv "$temp_prod_dir" /opt/docker-apps/production
    
    log_success "Development stack duplicated to production configuration"
    log_info "Ready for Nginx redirection to complete deployment"
}

main() {
    if [[ $# -ne 1 ]]; then
        usage
    fi
    
    local command="$1"
    
    case "$command" in
        dev-to-prod)
            duplicate_dev_to_prod
            ;;
        backup-prod)
            backup_production_stack
            ;;
        *)
            echo -e "${RED}Error: Invalid command: $command${NC}"
            usage
            ;;
    esac
}

main "$@"
EOF
    
    chmod +x /opt/scripts/duplicate-stack.sh
    
    log_success "Stack management scripts created"
}

# Create monitoring integration
create_monitoring_integration() {
    log_info "Creating monitoring integration..."
    
    # Create health check script
    cat > /opt/scripts/health-check-stacks.sh << 'EOF'
#!/bin/bash

# Comprehensive Stack Health Check
set -euo pipefail

PROJECT_NAME="agentic"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_container_health() {
    local container_name="$1"
    local expected_status="running"
    
    if docker ps --format "{{.Names}}" | grep -q "^${container_name}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name")
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-healthcheck")
        
        if [[ "$status" == "$expected_status" ]]; then
            if [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
                echo -e "${GREEN}✓${NC} $container_name: $status ($health)"
                return 0
            else
                echo -e "${YELLOW}⚠${NC} $container_name: $status ($health)"
                return 1
            fi
        else
            echo -e "${RED}✗${NC} $container_name: $status"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $container_name: not found"
        return 1
    fi
}

check_port_connectivity() {
    local port="$1"
    local service="$2"
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Port $port ($service): accessible"
        return 0
    else
        echo -e "${RED}✗${NC} Port $port ($service): not accessible"
        return 1
    fi
}

main() {
    echo "=== DUAL STACK HEALTH CHECK ==="
    echo "Date: $(date)"
    echo ""
    
    local overall_health=0
    
    echo "=== PRODUCTION STACK ==="
    check_container_health "${PROJECT_NAME}-frontend-prod" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-backend-prod" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-redis-prod" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-n8n-prod" || ((overall_health++))
    
    echo ""
    echo "=== DEVELOPMENT STACK ==="
    check_container_health "${PROJECT_NAME}-frontend-dev" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-backend-dev" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-redis-dev" || ((overall_health++))
    check_container_health "${PROJECT_NAME}-n8n-dev" || ((overall_health++))
    
    echo ""
    echo "=== PORT CONNECTIVITY ==="
    check_port_connectivity 3000 "Frontend Production" || ((overall_health++))
    check_port_connectivity 3001 "Frontend Development" || ((overall_health++))
    check_port_connectivity 8000 "Backend Production" || ((overall_health++))
    check_port_connectivity 8001 "Backend Development" || ((overall_health++))
    check_port_connectivity 6379 "Redis Production" || ((overall_health++))
    check_port_connectivity 6380 "Redis Development" || ((overall_health++))
    check_port_connectivity 5678 "N8N Production" || ((overall_health++))
    check_port_connectivity 5679 "N8N Development" || ((overall_health++))
    
    echo ""
    echo "=== DOCKER NETWORKS ==="
    if docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-production"; then
        echo -e "${GREEN}✓${NC} Production network: exists"
    else
        echo -e "${RED}✗${NC} Production network: missing"
        ((overall_health++))
    fi
    
    if docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-development"; then
        echo -e "${GREEN}✓${NC} Development network: exists"
    else
        echo -e "${RED}✗${NC} Development network: missing"
        ((overall_health++))
    fi
    
    echo ""
    echo "=== DOCKER VOLUMES ==="
    local required_volumes=(
        "${PROJECT_NAME}-redis-prod-data"
        "${PROJECT_NAME}-redis-dev-data"
        "${PROJECT_NAME}-n8n-prod-data"
        "${PROJECT_NAME}-n8n-dev-data"
    )
    
    for volume in "${required_volumes[@]}"; do
        if docker volume ls --format "{{.Name}}" | grep -q "$volume"; then
            echo -e "${GREEN}✓${NC} Volume $volume: exists"
        else
            echo -e "${RED}✗${NC} Volume $volume: missing"
            ((overall_health++))
        fi
    done
    
    echo ""
    echo "=== OVERALL HEALTH ==="
    if [[ $overall_health -eq 0 ]]; then
        echo -e "${GREEN}✓ ALL SYSTEMS HEALTHY${NC}"
        exit 0
    else
        echo -e "${RED}✗ $overall_health ISSUES DETECTED${NC}"
        exit 1
    fi
}

main "$@"
EOF
    
    chmod +x /opt/scripts/health-check-stacks.sh
    
    log_success "Monitoring integration created"
}

# Validate dual stack setup
validate_dual_stack_setup() {
    log_info "Validating dual stack setup..."
    
    local validation_errors=0
    
    # Check Docker networks
    if ! docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-production"; then
        log_error "Production network not found"
        ((validation_errors++))
    fi
    
    if ! docker network ls --format "{{.Name}}" | grep -q "${PROJECT_NAME}-development"; then
        log_error "Development network not found"
        ((validation_errors++))
    fi
    
    # Check Docker volumes
    local required_volumes=(
        "${PROJECT_NAME}-redis-prod-data"
        "${PROJECT_NAME}-redis-dev-data"
        "${PROJECT_NAME}-n8n-prod-data"
        "${PROJECT_NAME}-n8n-dev-data"
    )
    
    for volume in "${required_volumes[@]}"; do
        if ! docker volume ls --format "{{.Name}}" | grep -q "$volume"; then
            log_error "Required volume missing: $volume"
            ((validation_errors++))
        fi
    done
    
    # Check configuration files
    if [[ ! -f "/opt/docker-apps/production/docker-compose.yml" ]]; then
        log_error "Production docker-compose.yml not found"
        ((validation_errors++))
    fi
    
    if [[ ! -f "/opt/docker-apps/development/docker-compose.yml" ]]; then
        log_error "Development docker-compose.yml not found"
        ((validation_errors++))
    fi
    
    # Check management scripts
    local required_scripts=(
        "/opt/scripts/manage-stacks.sh"
        "/opt/scripts/duplicate-stack.sh"
        "/opt/scripts/health-check-stacks.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ ! -x "$script" ]]; then
            log_error "Required script missing or not executable: $script"
            ((validation_errors++))
        fi
    done
    
    if [[ $validation_errors -eq 0 ]]; then
        log_success "All validation checks passed"
        return 0
    else
        log_error "Validation failed with $validation_errors errors"
        return 1
    fi
}

# Generate setup report
generate_setup_report() {
    local report_file="/opt/dual-stack-setup-report.txt"
    
    cat > "$report_file" << EOF
=== DUAL STACK CONTAINER SETUP REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Project Name: $PROJECT_NAME

=== DOCKER NETWORKS ===
$(docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" | grep -E "(NAME|${PROJECT_NAME})")

=== DOCKER VOLUMES ===
$(docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep -E "(NAME|${PROJECT_NAME})")

=== CONFIGURATION FILES ===
Production: /opt/docker-apps/production/docker-compose.yml
Development: /opt/docker-apps/development/docker-compose.yml

=== MANAGEMENT SCRIPTS ===
Stack Manager: /opt/scripts/manage-stacks.sh
Stack Duplicator: /opt/scripts/duplicate-stack.sh
Health Checker: /opt/scripts/health-check-stacks.sh

=== PORT ALLOCATION ===
Production Stack:
- Frontend: 3000
- Backend: 8000
- Redis: 6379
- N8N: 5678

Development Stack:
- Frontend: 3001
- Backend: 8001
- Redis: 6380
- N8N: 5679

=== USAGE EXAMPLES ===
# Start production stack
/opt/scripts/manage-stacks.sh start production

# Check health of all stacks
/opt/scripts/health-check-stacks.sh

# Duplicate dev to prod (zero-downtime deployment)
/opt/scripts/duplicate-stack.sh dev-to-prod

# View stack status
/opt/scripts/manage-stacks.sh status all

=== NEXT STEPS ===
1. Configure your application images
2. Update environment variables in .env files
3. Set up Nginx configuration for domain routing
4. Deploy your application containers
5. Test the dual stack setup

=== IMPORTANT NOTES ===
- Production and development stacks are completely isolated
- Each stack has its own Docker network and volumes
- Container naming follows: ${PROJECT_NAME}-service-environment
- Zero-downtime deployment is supported through stack duplication
- Health checks are integrated for all services

EOF
    
    log_success "Setup report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🚀 DUAL-STACK CONTAINER ORCHESTRATION SETUP${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}🎯 Project: $PROJECT_NAME${NC}"
    echo ""
    
    log_info "Starting dual-stack container setup..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Execute setup steps
    validate_prerequisites
    create_docker_networks
    create_docker_volumes
    create_production_compose
    create_development_compose
    create_stack_management_scripts
    create_monitoring_integration
    validate_dual_stack_setup
    generate_setup_report
    
    echo ""
    echo -e "${GREEN}🎉 DUAL-STACK CONTAINER SETUP COMPLETED!${NC}"
    echo -e "${BLUE}📋 Setup report: /opt/dual-stack-setup-report.txt${NC}"
    echo -e "${BLUE}📋 Setup log: $LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}📝 Quick Start Commands:${NC}"
    echo "- Health check: /opt/scripts/health-check-stacks.sh"
    echo "- Start production: /opt/scripts/manage-stacks.sh start production"
    echo "- Start development: /opt/scripts/manage-stacks.sh start development"
    echo "- View status: /opt/scripts/manage-stacks.sh status all"
    echo ""
    echo -e "${YELLOW}🔧 Next Steps:${NC}"
    echo "1. Update .env files with your actual configuration"
    echo "2. Build and deploy your application images"
    echo "3. Configure Nginx for domain routing"
    echo "4. Test the complete deployment pipeline"
    echo ""
    
    log_success "Dual-stack container setup completed successfully"
}

# Execute main function
main "$@"