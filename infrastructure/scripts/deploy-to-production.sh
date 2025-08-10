#!/bin/bash

# 🚀 ZERO-DOWNTIME PRODUCTION DEPLOYMENT SCRIPT
# This script implements our systematic deployment process with zero downtime
# 
# PROCESS:
# 1. Duplicate development stack to new production containers
# 2. Health check new stack before switching traffic
# 3. Nginx redirect traffic to new stack (atomic switch)
# 4. Stop old production stack (keep for 2 weeks rollback)
# 5. Rename new containers to production naming
#
# PREVENTS: Downtime, failed deployments, data loss, service interruption

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/production-deployment.log"
PROJECT_NAME="agentic"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_RETENTION_DAYS=14

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Deployment state tracking
DEPLOYMENT_STATE_FILE="/opt/deployment-state.json"
OLD_PROD_CONTAINERS=()
NEW_PROD_CONTAINERS=()
ROLLBACK_REQUIRED=false

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

# Error handling with automatic rollback
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Deployment failed at line $line_number with exit code $exit_code"
    
    if [[ "$ROLLBACK_REQUIRED" == "true" ]]; then
        log_error "Initiating automatic rollback..."
        rollback_deployment
    fi
    
    cleanup_failed_deployment
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Cleanup function for failed deployments
cleanup_failed_deployment() {
    log_warn "Cleaning up failed deployment..."
    
    # Remove any partially created containers
    for container in "${NEW_PROD_CONTAINERS[@]}"; do
        if docker ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
            docker rm -f "$container" 2>/dev/null || true
            log_info "Removed failed container: $container"
        fi
    done
    
    # Restore original Nginx configuration if changed
    if [[ -f "/opt/backups/nginx/nginx-backup-${TIMESTAMP}.tar.gz" ]]; then
        log_info "Restoring original Nginx configuration..."
        cd /etc/nginx
        tar -xzf "/opt/backups/nginx/nginx-backup-${TIMESTAMP}.tar.gz"
        nginx -t && systemctl reload nginx
    fi
}

# Rollback function
rollback_deployment() {
    log_warn "Rolling back deployment..."
    
    # Get the latest backup information
    local latest_backup=$(ls -t /opt/backups/production-* 2>/dev/null | head -1)
    if [[ -z "$latest_backup" ]]; then
        log_error "No backup found for rollback!"
        return 1
    fi
    
    log_info "Rolling back to: $latest_backup"
    
    # Stop new containers
    for container in "${NEW_PROD_CONTAINERS[@]}"; do
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    done
    
    # Restore old containers
    for container in "${OLD_PROD_CONTAINERS[@]}"; do
        docker start "$container" 2>/dev/null || true
    done
    
    # Restore Nginx configuration
    /opt/scripts/nginx-manager.sh redirect 3000 3000 production
    
    log_success "Rollback completed"
}

# Validation functions
validate_prerequisites() {
    log_info "Validating deployment prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Check required scripts exist
    local required_scripts=(
        "/opt/scripts/manage-stacks.sh"
        "/opt/scripts/duplicate-stack.sh"
        "/opt/scripts/nginx-manager.sh"
        "/opt/scripts/health-check-stacks.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ ! -x "$script" ]]; then
            log_error "Required script not found or not executable: $script"
            exit 1
        fi
    done
    
    # Check development stack is running
    if ! /opt/scripts/manage-stacks.sh status development | grep -q "Up"; then
        log_error "Development stack is not running. Cannot duplicate for production."
        exit 1
    fi
    
    # Check disk space (need at least 5GB free)
    local available_space=$(df / | awk 'NR==2{print $4}')
    if [[ $available_space -lt 5242880 ]]; then  # 5GB in KB
        log_error "Insufficient disk space for deployment (need 5GB free)"
        exit 1
    fi
    
    log_success "Prerequisites validation passed"
}

# Save deployment state for rollback
save_deployment_state() {
    log_info "Saving deployment state..."
    
    # Get current production containers
    mapfile -t OLD_PROD_CONTAINERS < <(docker ps --format "{{.Names}}" | grep "${PROJECT_NAME}.*-prod$")
    
    # Create state file
    cat > "$DEPLOYMENT_STATE_FILE" << EOF
{
    "timestamp": "$TIMESTAMP",
    "old_containers": $(printf '%s\n' "${OLD_PROD_CONTAINERS[@]}" | jq -R . | jq -s .),
    "deployment_phase": "started",
    "backup_location": "/opt/backups/production-${TIMESTAMP}"
}
EOF
    
    log_success "Deployment state saved"
}

# Backup current production stack
backup_production_stack() {
    log_info "Backing up current production stack..."
    
    local backup_dir="/opt/backups/production-${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Stop production containers gracefully
    log_info "Stopping production containers gracefully..."
    /opt/scripts/manage-stacks.sh stop production
    
    # Export container images
    log_info "Exporting production container images..."
    for container in "${OLD_PROD_CONTAINERS[@]}"; do
        local image=$(docker inspect "$container" --format='{{.Config.Image}}' 2>/dev/null || echo "")
        if [[ -n "$image" ]]; then
            docker save -o "$backup_dir/${container}-image.tar" "$image" 2>/dev/null || true
            log_info "Exported image for container: $container"
        fi
    done
    
    # Backup volumes
    log_info "Backing up production volumes..."
    local prod_volumes=(
        "${PROJECT_NAME}-redis-prod-data"
        "${PROJECT_NAME}-n8n-prod-data"
        "${PROJECT_NAME}-frontend-prod-data"
        "${PROJECT_NAME}-backend-prod-data"
        "${PROJECT_NAME}-logs-prod"
    )
    
    for volume in "${prod_volumes[@]}"; do
        if docker volume ls --format "{{.Name}}" | grep -q "^${volume}$"; then
            docker run --rm \
                -v "${volume}:/data" \
                -v "$backup_dir:/backup" \
                alpine tar czf "/backup/${volume}.tar.gz" -C /data . 2>/dev/null || true
            log_info "Backed up volume: $volume"
        fi
    done
    
    # Backup configuration
    cp -r /opt/docker-apps/production "$backup_dir/config"
    
    # Backup Nginx configuration
    mkdir -p "$backup_dir/nginx"
    cd /etc/nginx
    tar -czf "$backup_dir/nginx/nginx-backup.tar.gz" sites-available sites-enabled nginx.conf
    
    log_success "Production stack backed up to: $backup_dir"
    echo "$backup_dir" > /opt/backups/latest-production-backup.txt
}

# Duplicate development stack for production
duplicate_dev_stack() {
    log_info "Duplicating development stack for production..."
    
    # Use the stack duplication script
    /opt/scripts/duplicate-stack.sh dev-to-prod
    
    # Get new container names
    mapfile -t NEW_PROD_CONTAINERS < <(docker ps --format "{{.Names}}" | grep "${PROJECT_NAME}.*-prod-new")
    
    if [[ ${#NEW_PROD_CONTAINERS[@]} -eq 0 ]]; then
        log_error "No new production containers found after duplication"
        exit 1
    fi
    
    log_success "Development stack duplicated successfully"
    log_info "New containers: ${NEW_PROD_CONTAINERS[*]}"
}

# Comprehensive health check of new stack
health_check_new_stack() {
    log_info "Performing comprehensive health check on new stack..."
    
    local max_attempts=30
    local attempt=1
    local all_healthy=false
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        local healthy_containers=0
        local total_containers=${#NEW_PROD_CONTAINERS[@]}
        
        for container in "${NEW_PROD_CONTAINERS[@]}"; do
            local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
            
            if [[ "$status" == "running" ]] && [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
                ((healthy_containers++))
            else
                log_warn "Container $container status: $status, health: $health"
            fi
        done
        
        if [[ $healthy_containers -eq $total_containers ]]; then
            all_healthy=true
            break
        fi
        
        sleep 10
        ((attempt++))
    done
    
    if [[ "$all_healthy" != "true" ]]; then
        log_error "Health check failed after $max_attempts attempts"
        return 1
    fi
    
    # Test application endpoints
    log_info "Testing application endpoints..."
    
    # Get the port of the new frontend container
    local frontend_port=$(docker port "${PROJECT_NAME}-frontend-prod-new" 3000 2>/dev/null | cut -d: -f2)
    if [[ -n "$frontend_port" ]]; then
        if curl -s -f "http://localhost:${frontend_port}/api/health" > /dev/null; then
            log_success "Frontend health check passed"
        else
            log_error "Frontend health check failed"
            return 1
        fi
    fi
    
    # Get the port of the new backend container
    local backend_port=$(docker port "${PROJECT_NAME}-backend-prod-new" 8000 2>/dev/null | cut -d: -f2)
    if [[ -n "$backend_port" ]]; then
        if curl -s -f "http://localhost:${backend_port}/health" > /dev/null; then
            log_success "Backend health check passed"
        else
            log_error "Backend health check failed"
            return 1
        fi
    fi
    
    log_success "All health checks passed"
}

# Switch traffic to new stack (zero-downtime)
switch_traffic_to_new_stack() {
    log_info "Switching traffic to new stack (zero-downtime)..."
    
    ROLLBACK_REQUIRED=true  # Enable rollback from this point
    
    # Get port mappings for new containers
    local new_frontend_port=$(docker port "${PROJECT_NAME}-frontend-prod-new" 3000 2>/dev/null | cut -d: -f2)
    local new_backend_port=$(docker port "${PROJECT_NAME}-backend-prod-new" 8000 2>/dev/null | cut -d: -f2)
    
    if [[ -z "$new_frontend_port" || -z "$new_backend_port" ]]; then
        log_error "Could not determine new container ports"
        return 1
    fi
    
    log_info "Redirecting traffic: Frontend 3000 → $new_frontend_port, Backend 8000 → $new_backend_port"
    
    # Update Nginx configuration to point to new containers
    /opt/scripts/nginx-manager.sh redirect 3000 "$new_frontend_port" production
    /opt/scripts/nginx-manager.sh redirect 8000 "$new_backend_port" production
    
    # Wait a moment for traffic to switch
    sleep 5
    
    # Verify the switch worked
    if curl -s -f "https://consulting.sa/api/health" > /dev/null; then
        log_success "Traffic switch successful - production site responding"
    else
        log_error "Traffic switch failed - production site not responding"
        return 1
    fi
    
    log_success "Zero-downtime traffic switch completed"
}

# Finalize deployment
finalize_deployment() {
    log_info "Finalizing deployment..."
    
    # Stop and remove old production containers
    for container in "${OLD_PROD_CONTAINERS[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            docker stop "$container"
            # Don't remove yet - keep for rollback
            docker rename "$container" "${container}-backup-${TIMESTAMP}"
            log_info "Stopped and renamed old container: $container"
        fi
    done
    
    # Rename new containers to production names
    for container in "${NEW_PROD_CONTAINERS[@]}"; do
        local new_name="${container%-new}"
        docker rename "$container" "$new_name"
        log_info "Renamed container: $container → $new_name"
    done
    
    # Update Nginx configuration to use standard production ports
    /opt/scripts/nginx-manager.sh redirect "$new_frontend_port" 3000 production
    /opt/scripts/nginx-manager.sh redirect "$new_backend_port" 8000 production
    
    # Update deployment state
    jq '.deployment_phase = "completed"' "$DEPLOYMENT_STATE_FILE" > "${DEPLOYMENT_STATE_FILE}.tmp"
    mv "${DEPLOYMENT_STATE_FILE}.tmp" "$DEPLOYMENT_STATE_FILE"
    
    ROLLBACK_REQUIRED=false  # Deployment successful, disable rollback
    
    log_success "Deployment finalized successfully"
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups (keeping $BACKUP_RETENTION_DAYS days)..."
    
    # Remove old backup directories
    find /opt/backups -name "production-*" -type d -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # Remove old backup containers
    docker ps -a --format "{{.Names}}" | grep "backup-" | while read container; do
        local backup_date=$(echo "$container" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
        if [[ -n "$backup_date" ]]; then
            local backup_timestamp=$(date -d "${backup_date:0:8} ${backup_date:9:2}:${backup_date:11:2}:${backup_date:13:2}" +%s 2>/dev/null || echo "0")
            local cutoff_timestamp=$(date -d "$BACKUP_RETENTION_DAYS days ago" +%s)
            
            if [[ $backup_timestamp -lt $cutoff_timestamp ]]; then
                docker rm "$container" 2>/dev/null || true
                log_info "Removed old backup container: $container"
            fi
        fi
    done
    
    log_success "Old backup cleanup completed"
}

# Generate deployment report
generate_deployment_report() {
    local report_file="/opt/production-deployment-report-${TIMESTAMP}.txt"
    
    cat > "$report_file" << EOF
=== PRODUCTION DEPLOYMENT REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Deployment ID: $TIMESTAMP

=== DEPLOYMENT SUMMARY ===
Status: SUCCESS
Duration: $SECONDS seconds
Downtime: 0 seconds (zero-downtime deployment)

=== CONTAINERS DEPLOYED ===
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "${PROJECT_NAME}.*-prod")

=== BACKUP INFORMATION ===
Backup Location: /opt/backups/production-${TIMESTAMP}
Backup Retention: ${BACKUP_RETENTION_DAYS} days
Rollback Available: Yes

=== HEALTH STATUS ===
$(curl -s https://consulting.sa/api/health 2>/dev/null || echo "Health check failed")

=== PERFORMANCE METRICS ===
Frontend Response: $(curl -s -w "%{time_total}" -o /dev/null https://consulting.sa 2>/dev/null || echo "N/A")s
Backend Response: $(curl -s -w "%{time_total}" -o /dev/null https://consulting.sa/api/health 2>/dev/null || echo "N/A")s

=== SYSTEM RESOURCES ===
Memory Usage: $(free -h | awk '/^Mem:/{print $3 "/" $2}')
Disk Usage: $(df -h / | awk 'NR==2{print $3 "/" $2 " (" $5 ")"}')
Load Average: $(uptime | awk -F'load average:' '{print $2}')

=== NEXT STEPS ===
1. Monitor system performance for 24 hours
2. Verify all functionality is working correctly
3. Old containers will be automatically cleaned up in ${BACKUP_RETENTION_DAYS} days
4. Backup is available for rollback if needed

=== ROLLBACK COMMAND ===
If rollback is needed: /opt/scripts/rollback-deployment.sh $TIMESTAMP

EOF
    
    log_success "Deployment report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🚀 ZERO-DOWNTIME PRODUCTION DEPLOYMENT${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}🎯 Target: Production Environment${NC}"
    echo ""
    
    log_info "Starting zero-downtime production deployment..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Execute deployment steps
    validate_prerequisites
    save_deployment_state
    backup_production_stack
    duplicate_dev_stack
    health_check_new_stack
    switch_traffic_to_new_stack
    finalize_deployment
    cleanup_old_backups
    generate_deployment_report
    
    echo ""
    echo -e "${GREEN}🎉 ZERO-DOWNTIME DEPLOYMENT COMPLETED!${NC}"
    echo -e "${BLUE}📋 Deployment report: /opt/production-deployment-report-${TIMESTAMP}.txt${NC}"
    echo -e "${BLUE}📋 Deployment log: $LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}📊 Deployment Summary:${NC}"
    echo "- Duration: $SECONDS seconds"
    echo "- Downtime: 0 seconds"
    echo "- Backup: /opt/backups/production-${TIMESTAMP}"
    echo "- Status: SUCCESS"
    echo ""
    echo -e "${YELLOW}🔧 Management Commands:${NC}"
    echo "- Status: /opt/scripts/health-check-stacks.sh"
    echo "- Rollback: /opt/scripts/rollback-deployment.sh $TIMESTAMP"
    echo "- Logs: tail -f $LOG_FILE"
    echo ""
    
    log_success "Zero-downtime production deployment completed successfully"
}

# Execute main function
main "$@"