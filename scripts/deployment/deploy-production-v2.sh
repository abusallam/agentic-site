#!/bin/bash

# Production Deployment Script v2.0
# Enhanced deployment with comprehensive validation and rollback

set -e  # Exit on any error

# Configuration
DEPLOYMENT_ID=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/agentic/backups"
LOG_FILE="/var/log/agentic/deployment_${DEPLOYMENT_ID}.log"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
ROLLBACK_ENABLED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

log "🚀 Starting Production Deployment v2.0"
log "Deployment ID: $DEPLOYMENT_ID"

# Pre-deployment validation
validate_prerequisites() {
    log "🔍 Validating deployment prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root - this is acceptable for deployment"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df /opt/agentic | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5242880 ]]; then  # 5GB in KB
        log_error "Insufficient disk space. Need at least 5GB available"
        exit 1
    fi
    
    # Check if deployment directory exists
    if [[ ! -d "/opt/agentic" ]]; then
        log_error "Deployment directory /opt/agentic does not exist"
        exit 1
    fi
    
    log_success "Prerequisites validation completed"
}

# Create deployment backup
create_backup() {
    log "💾 Creating deployment backup..."
    
    mkdir -p "$BACKUP_DIR/$DEPLOYMENT_ID"
    
    # Backup current containers info
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "$BACKUP_DIR/$DEPLOYMENT_ID/containers.txt" 2>/dev/null || true
    
    # Backup docker-compose files
    cp /opt/agentic/docker-compose*.yml "$BACKUP_DIR/$DEPLOYMENT_ID/" 2>/dev/null || true
    
    # Backup environment files
    cp /opt/agentic/.env* "$BACKUP_DIR/$DEPLOYMENT_ID/" 2>/dev/null || true
    
    # Backup nginx configuration
    cp -r /opt/agentic/infrastructure/nginx "$BACKUP_DIR/$DEPLOYMENT_ID/" 2>/dev/null || true
    
    # Create backup metadata
    cat > "$BACKUP_DIR/$DEPLOYMENT_ID/backup_info.json" << EOF
{
    "deployment_id": "$DEPLOYMENT_ID",
    "backup_date": "$(date -Iseconds)",
    "git_commit": "$(cd /opt/agentic && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "containers_backed_up": $(docker ps -q | wc -l),
    "backup_size": "$(du -sh "$BACKUP_DIR/$DEPLOYMENT_ID" | cut -f1)"
}
EOF
    
    log_success "Backup created: $BACKUP_DIR/$DEPLOYMENT_ID"
}

# Update code from Git
update_code() {
    log "📥 Updating code from Git repository..."
    
    cd /opt/agentic
    
    # Fetch latest changes
    git fetch origin
    
    # Get current branch
    current_branch=$(git branch --show-current)
    log "Current branch: $current_branch"
    
    # Reset to latest commit
    git reset --hard origin/$current_branch
    
    # Get latest commit info
    latest_commit=$(git rev-parse HEAD)
    commit_message=$(git log -1 --pretty=format:"%s")
    
    log_success "Code updated to commit: $latest_commit"
    log "Commit message: $commit_message"
}

# Update environment configuration
update_environment() {
    log "⚙️  Updating environment configuration..."
    
    # Create production environment file
    cat > /opt/agentic/.env.production << 'EOF'
# Production Environment Configuration
NODE_ENV=production
ENVIRONMENT=production

# Database Configuration
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}

# AI Services
GOOGLE_API_KEY=${GOOGLE_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}

# Workflow Automation
N8N_URL=http://agentic-n8n-prod:5678
N8N_API_KEY=${N8N_API_KEY}

# Real-time Communication
LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
LIVEKIT_WS_URL=${LIVEKIT_WS_URL}

# Payment Processing
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}

# Security
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Backend Configuration
BACKEND_URL=http://agentic-backend-prod:8000
EOF

    # Update docker-compose for production
    cat > /opt/agentic/docker-compose.production.yml << 'EOF'
version: "3.8"

services:
  agentic-frontend-prod:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agentic-frontend-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_LIVEKIT_WS_URL=${LIVEKIT_WS_URL}
      - BACKEND_URL=http://agentic-backend-prod:8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network
    depends_on:
      - agentic-backend-prod

  agentic-backend-prod:
    build:
      context: ./agent
      dockerfile: Dockerfile
    container_name: agentic-backend-prod
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentic-network
    depends_on:
      - agentic-redis-prod

  agentic-redis-prod:
    image: redis:7-alpine
    container_name: agentic-redis-prod
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-network
    volumes:
      - redis_data:/data

  agentic-n8n-prod:
    image: n8nio/n8n:latest
    container_name: agentic-n8n-prod
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - WEBHOOK_URL=https://consulting.sa/
      - GENERIC_TIMEZONE=Asia/Riyadh
      - N8N_METRICS=true
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentic-network

volumes:
  redis_data:
  n8n_data:

networks:
  agentic-network:
    driver: bridge
EOF

    log_success "Environment configuration updated"
}

# Build and deploy containers
deploy_containers() {
    log "🏗️  Building and deploying containers..."
    
    cd /opt/agentic
    
    # Stop existing containers gracefully
    log "Stopping existing containers..."
    docker-compose -f docker-compose.production.yml down --timeout 30 || true
    
    # Remove old images to free space
    log "Cleaning up old images..."
    docker image prune -f || true
    
    # Build new images
    log "Building new container images..."
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Start services in order
    log "Starting Redis..."
    docker-compose -f docker-compose.production.yml up -d agentic-redis-prod
    
    log "Starting N8N..."
    docker-compose -f docker-compose.production.yml up -d agentic-n8n-prod
    
    log "Starting Backend..."
    docker-compose -f docker-compose.production.yml up -d agentic-backend-prod
    
    log "Starting Frontend..."
    docker-compose -f docker-compose.production.yml up -d agentic-frontend-prod
    
    log_success "Containers deployed"
}

# Health check function
check_container_health() {
    local container_name=$1
    local max_attempts=30
    local attempt=1
    
    log "🏥 Checking health of $container_name..."
    
    while [[ $attempt -le $max_attempts ]]; do
        # Check if container is running
        if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
            log_warning "Attempt $attempt/$max_attempts: $container_name is not running"
        else
            # Check health status
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-health-check")
            
            if [[ "$health_status" == "healthy" ]]; then
                log_success "$container_name is healthy"
                return 0
            elif [[ "$health_status" == "no-health-check" ]]; then
                # For containers without health checks, just verify they're running
                if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
                    log_success "$container_name is running (no health check configured)"
                    return 0
                fi
            else
                log_warning "Attempt $attempt/$max_attempts: $container_name health status: $health_status"
            fi
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "$container_name failed health check after $max_attempts attempts"
    return 1
}

# Comprehensive health validation
validate_deployment() {
    log "🔍 Validating deployment health..."
    
    local failed_containers=()
    
    # Check all production containers
    for container in "agentic-redis-prod" "agentic-n8n-prod" "agentic-backend-prod" "agentic-frontend-prod"; do
        if ! check_container_health "$container"; then
            failed_containers+=("$container")
        fi
    done
    
    # If any containers failed, report and potentially rollback
    if [[ ${#failed_containers[@]} -gt 0 ]]; then
        log_error "Health check failed for containers: ${failed_containers[*]}"
        return 1
    fi
    
    # Test API endpoints
    log "🌐 Testing API endpoints..."
    
    # Test frontend health
    if curl -f -s http://localhost:3000/api/health > /dev/null; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        return 1
    fi
    
    # Test backend health
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Test agent routing
    log "🤖 Testing agent routing..."
    response=$(curl -s -X POST http://localhost:3000/api/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello", "sessionId": "test_deployment"}' || echo "failed")
    
    if [[ "$response" != "failed" ]] && echo "$response" | grep -q "success"; then
        log_success "Agent routing test passed"
    else
        log_warning "Agent routing test failed, but continuing deployment"
    fi
    
    log_success "Deployment validation completed successfully"
    return 0
}

# Rollback function
rollback_deployment() {
    log_error "🔄 Initiating deployment rollback..."
    
    if [[ ! -d "$BACKUP_DIR/$DEPLOYMENT_ID" ]]; then
        log_error "No backup found for rollback"
        return 1
    fi
    
    cd /opt/agentic
    
    # Stop current containers
    docker-compose -f docker-compose.production.yml down --timeout 30 || true
    
    # Restore backup files
    cp "$BACKUP_DIR/$DEPLOYMENT_ID"/docker-compose*.yml /opt/agentic/ 2>/dev/null || true
    cp "$BACKUP_DIR/$DEPLOYMENT_ID"/.env* /opt/agentic/ 2>/dev/null || true
    
    # Start previous version
    if [[ -f "docker-compose.production.yml" ]]; then
        docker-compose -f docker-compose.production.yml up -d
        log_success "Rollback completed"
    else
        log_error "Could not find previous docker-compose configuration"
        return 1
    fi
}

# Cleanup function
cleanup_deployment() {
    log "🧹 Cleaning up deployment artifacts..."
    
    # Remove old backups (keep last 5)
    if [[ -d "$BACKUP_DIR" ]]; then
        cd "$BACKUP_DIR"
        ls -t | tail -n +6 | xargs -r rm -rf
        log_success "Old backups cleaned up"
    fi
    
    # Clean up Docker
    docker system prune -f > /dev/null 2>&1 || true
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    local deployment_failed=false
    
    # Trap to handle errors
    trap 'deployment_failed=true' ERR
    
    validate_prerequisites
    create_backup
    update_code
    update_environment
    deploy_containers
    
    if ! validate_deployment; then
        deployment_failed=true
    fi
    
    if [[ "$deployment_failed" == "true" ]]; then
        log_error "Deployment failed!"
        
        if [[ "$ROLLBACK_ENABLED" == "true" ]]; then
            rollback_deployment
        else
            log_warning "Rollback is disabled"
        fi
        
        exit 1
    else
        log_success "🎉 Deployment completed successfully!"
        log "Deployment ID: $DEPLOYMENT_ID"
        log "Frontend: https://consulting.sa"
        log "Backend API: http://localhost:8000"
        log "N8N: http://localhost:5678"
        
        cleanup_deployment
        
        # Send success notification (if configured)
        # notify_deployment_success "$DEPLOYMENT_ID"
    fi
}

# Run main function
main "$@"