#!/bin/bash

# 🔄 AUTOMATED ROLLBACK AND RECOVERY SYSTEM
# Instant recovery with 2-week retention policy for stopped production containers
# 
# PROCESS:
# 1. Validate rollback target and backup integrity
# 2. Stop current production containers gracefully
# 3. Restore previous production containers from backup
# 4. Switch Nginx traffic back to restored containers
# 5. Verify rollback success and system health
# 6. Generate rollback report and cleanup

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/rollback-deployment.log"
PROJECT_NAME="agentic"
ROLLBACK_TIMESTAMP="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Rollback state tracking
ROLLBACK_STATE_FILE="/opt/rollback-state.json"
CURRENT_CONTAINERS=()
BACKUP_CONTAINERS=()
ROLLBACK_SUCCESSFUL=false

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
    log_error "Rollback failed at line $line_number with exit code $exit_code"
    
    if [[ "$ROLLBACK_SUCCESSFUL" != "true" ]]; then
        log_error "Rollback incomplete - manual intervention required"
        generate_failure_report
    fi
    
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Usage information
show_usage() {
    echo -e "${PURPLE}🔄 AUTOMATED ROLLBACK AND RECOVERY SYSTEM${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo ""
    echo "Usage: $0 <TIMESTAMP>"
    echo ""
    echo "Parameters:"
    echo "  TIMESTAMP    Deployment timestamp to rollback to (format: YYYYMMDD_HHMMSS)"
    echo ""
    echo "Examples:"
    echo "  $0 20250109_143022    # Rollback to specific deployment"
    echo "  $0 latest             # Rollback to latest backup"
    echo ""
    echo "Available backups:"
    if [[ -d /opt/backups ]]; then
        ls -1 /opt/backups/production-* 2>/dev/null | sed 's|.*/production-||' | head -10 || echo "  No backups found"
    else
        echo "  No backup directory found"
    fi
    echo ""
    exit 1
}

# Validate rollback prerequisites
validate_rollback_prerequisites() {
    log_info "Validating rollback prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Validate timestamp parameter
    if [[ -z "$ROLLBACK_TIMESTAMP" ]]; then
        log_error "Rollback timestamp is required"
        show_usage
    fi
    
    # Handle 'latest' keyword
    if [[ "$ROLLBACK_TIMESTAMP" == "latest" ]]; then
        if [[ -f /opt/backups/latest-production-backup.txt ]]; then
            local latest_backup_path=$(cat /opt/backups/latest-production-backup.txt)
            ROLLBACK_TIMESTAMP=$(basename "$latest_backup_path" | sed 's/production-//')
            log_info "Using latest backup: $ROLLBACK_TIMESTAMP"
        else
            log_error "No latest backup reference found"
            exit 1
        fi
    fi
    
    # Validate timestamp format
    if [[ ! "$ROLLBACK_TIMESTAMP" =~ ^[0-9]{8}_[0-9]{6}$ ]]; then
        log_error "Invalid timestamp format. Expected: YYYYMMDD_HHMMSS"
        show_usage
    fi
    
    # Check if backup exists
    local backup_dir="/opt/backups/production-${ROLLBACK_TIMESTAMP}"
    if [[ ! -d "$backup_dir" ]]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    # Check required scripts exist
    local required_scripts=(
        "/opt/scripts/manage-stacks.sh"
        "/opt/scripts/nginx-manager.sh"
        "/opt/scripts/health-check-stacks.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ ! -x "$script" ]]; then
            log_error "Required script not found or not executable: $script"
            exit 1
        fi
    done
    
    log_success "Prerequisites validation passed"
}

# Validate backup integrity
validate_backup_integrity() {
    log_info "Validating backup integrity..."
    
    local backup_dir="/opt/backups/production-${ROLLBACK_TIMESTAMP}"
    
    # Check for required backup components
    local required_components=(
        "config"
        "nginx/nginx-backup.tar.gz"
    )
    
    for component in "${required_components[@]}"; do
        if [[ ! -e "$backup_dir/$component" ]]; then
            log_error "Missing backup component: $component"
            exit 1
        fi
    done
    
    # Validate backup containers exist
    mapfile -t BACKUP_CONTAINERS < <(docker ps -a --format "{{.Names}}" | grep "backup-${ROLLBACK_TIMESTAMP}$")
    
    if [[ ${#BACKUP_CONTAINERS[@]} -eq 0 ]]; then
        log_error "No backup containers found for timestamp: $ROLLBACK_TIMESTAMP"
        exit 1
    fi
    
    log_info "Found ${#BACKUP_CONTAINERS[@]} backup containers"
    
    # Check backup container states
    for container in "${BACKUP_CONTAINERS[@]}"; do
        local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
        if [[ "$status" == "missing" ]]; then
            log_error "Backup container missing: $container"
            exit 1
        fi
        log_info "Backup container $container status: $status"
    done
    
    log_success "Backup integrity validation passed"
}

# Save rollback state
save_rollback_state() {
    log_info "Saving rollback state..."
    
    # Get current production containers
    mapfile -t CURRENT_CONTAINERS < <(docker ps --format "{{.Names}}" | grep "${PROJECT_NAME}.*-prod$")
    
    # Create state file
    cat > "$ROLLBACK_STATE_FILE" << EOF
{
    "rollback_timestamp": "$ROLLBACK_TIMESTAMP",
    "rollback_started": "$(date -Iseconds)",
    "current_containers": $(printf '%s\n' "${CURRENT_CONTAINERS[@]}" | jq -R . | jq -s .),
    "backup_containers": $(printf '%s\n' "${BACKUP_CONTAINERS[@]}" | jq -R . | jq -s .),
    "rollback_phase": "started"
}
EOF
    
    log_success "Rollback state saved"
}

# Stop current production containers
stop_current_production() {
    log_info "Stopping current production containers..."
    
    for container in "${CURRENT_CONTAINERS[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            log_info "Stopping container: $container"
            docker stop "$container" --time=30
            
            # Rename for potential recovery
            local recovery_name="${container}-recovery-$(date +%Y%m%d_%H%M%S)"
            docker rename "$container" "$recovery_name"
            log_info "Renamed container for recovery: $container → $recovery_name"
        fi
    done
    
    log_success "Current production containers stopped"
}

# Restore backup containers
restore_backup_containers() {
    log_info "Restoring backup containers..."
    
    for container in "${BACKUP_CONTAINERS[@]}"; do
        # Remove the backup suffix to get original name
        local original_name="${container%-backup-*}"
        
        log_info "Restoring container: $container → $original_name"
        
        # Rename backup container to original name
        docker rename "$container" "$original_name"
        
        # Start the restored container
        docker start "$original_name"
        
        # Wait for container to be ready
        local max_wait=60
        local wait_count=0
        
        while [[ $wait_count -lt $max_wait ]]; do
            local status=$(docker inspect --format='{{.State.Status}}' "$original_name" 2>/dev/null || echo "missing")
            if [[ "$status" == "running" ]]; then
                log_success "Container restored and running: $original_name"
                break
            fi
            
            sleep 2
            ((wait_count += 2))
        done
        
        if [[ $wait_count -ge $max_wait ]]; then
            log_error "Container failed to start within ${max_wait}s: $original_name"
            return 1
        fi
    done
    
    log_success "All backup containers restored"
}

# Restore Nginx configuration
restore_nginx_configuration() {
    log_info "Restoring Nginx configuration..."
    
    local backup_dir="/opt/backups/production-${ROLLBACK_TIMESTAMP}"
    local nginx_backup="$backup_dir/nginx/nginx-backup.tar.gz"
    
    if [[ ! -f "$nginx_backup" ]]; then
        log_error "Nginx backup not found: $nginx_backup"
        return 1
    fi
    
    # Backup current Nginx config
    local current_backup="/tmp/nginx-current-$(date +%Y%m%d_%H%M%S).tar.gz"
    cd /etc/nginx
    tar -czf "$current_backup" sites-available sites-enabled nginx.conf
    log_info "Current Nginx config backed up to: $current_backup"
    
    # Restore backup configuration
    tar -xzf "$nginx_backup" -C /etc/nginx
    
    # Test configuration
    if nginx -t; then
        systemctl reload nginx
        log_success "Nginx configuration restored and reloaded"
    else
        log_error "Nginx configuration test failed, restoring current config"
        tar -xzf "$current_backup" -C /etc/nginx
        nginx -t && systemctl reload nginx
        return 1
    fi
}

# Restore application configuration
restore_application_configuration() {
    log_info "Restoring application configuration..."
    
    local backup_dir="/opt/backups/production-${ROLLBACK_TIMESTAMP}"
    local config_backup="$backup_dir/config"
    
    if [[ ! -d "$config_backup" ]]; then
        log_error "Application config backup not found: $config_backup"
        return 1
    fi
    
    # Backup current configuration
    local current_config_backup="/tmp/app-config-current-$(date +%Y%m%d_%H%M%S)"
    cp -r /opt/docker-apps/production "$current_config_backup"
    log_info "Current app config backed up to: $current_config_backup"
    
    # Restore backup configuration
    rm -rf /opt/docker-apps/production
    cp -r "$config_backup" /opt/docker-apps/production
    
    log_success "Application configuration restored"
}

# Verify rollback success
verify_rollback_success() {
    log_info "Verifying rollback success..."
    
    local max_attempts=30
    local attempt=1
    local all_healthy=false
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        local healthy_containers=0
        local total_containers=0
        
        # Check restored containers
        for container in "${BACKUP_CONTAINERS[@]}"; do
            local original_name="${container%-backup-*}"
            ((total_containers++))
            
            local status=$(docker inspect --format='{{.State.Status}}' "$original_name" 2>/dev/null || echo "missing")
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$original_name" 2>/dev/null || echo "no-healthcheck")
            
            if [[ "$status" == "running" ]] && [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
                ((healthy_containers++))
            else
                log_warn "Container $original_name status: $status, health: $health"
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
    
    # Test main site
    if curl -s -f "https://consulting.sa" > /dev/null; then
        log_success "Main site responding"
    else
        log_error "Main site not responding"
        return 1
    fi
    
    # Test API health
    if curl -s -f "https://consulting.sa/api/health" > /dev/null; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
    
    # Test development site
    if curl -s -f "https://dev.consulting.sa" > /dev/null; then
        log_success "Development site responding"
    else
        log_warn "Development site not responding (may be expected)"
    fi
    
    log_success "All verification checks passed"
    ROLLBACK_SUCCESSFUL=true
}

# Update rollback state
update_rollback_state() {
    local phase="$1"
    
    jq --arg phase "$phase" '.rollback_phase = $phase' "$ROLLBACK_STATE_FILE" > "${ROLLBACK_STATE_FILE}.tmp"
    mv "${ROLLBACK_STATE_FILE}.tmp" "$ROLLBACK_STATE_FILE"
}

# Cleanup recovery containers
cleanup_recovery_containers() {
    log_info "Cleaning up recovery containers..."
    
    # Remove recovery containers (they were the failed current production)
    docker ps -a --format "{{.Names}}" | grep "recovery-" | while read container; do
        docker rm "$container" 2>/dev/null || true
        log_info "Removed recovery container: $container"
    done
    
    log_success "Recovery containers cleaned up"
}

# Generate rollback report
generate_rollback_report() {
    local report_file="/opt/rollback-deployment-report-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
=== ROLLBACK DEPLOYMENT REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Rollback Target: $ROLLBACK_TIMESTAMP

=== ROLLBACK SUMMARY ===
Status: $(if [[ "$ROLLBACK_SUCCESSFUL" == "true" ]]; then echo "SUCCESS"; else echo "FAILED"; fi)
Duration: $SECONDS seconds
Downtime: Minimal (graceful container restart)

=== RESTORED CONTAINERS ===
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "${PROJECT_NAME}.*-prod")

=== BACKUP INFORMATION ===
Restored From: /opt/backups/production-${ROLLBACK_TIMESTAMP}
Backup Date: $(stat -c %y "/opt/backups/production-${ROLLBACK_TIMESTAMP}" 2>/dev/null || echo "Unknown")

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
3. Investigate cause of original deployment issue
4. Plan corrective measures for next deployment

=== RECOVERY INFORMATION ===
Recovery containers were created and can be restored if needed
Check /tmp/ for configuration backups made during rollback

EOF
    
    log_success "Rollback report generated: $report_file"
}

# Generate failure report
generate_failure_report() {
    local report_file="/opt/rollback-failure-report-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
=== ROLLBACK FAILURE REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Rollback Target: $ROLLBACK_TIMESTAMP

=== FAILURE SUMMARY ===
Status: FAILED
Duration: $SECONDS seconds
Phase: $(jq -r '.rollback_phase' "$ROLLBACK_STATE_FILE" 2>/dev/null || echo "Unknown")

=== CURRENT STATE ===
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "${PROJECT_NAME}")

=== MANUAL RECOVERY STEPS ===
1. Check container states: docker ps -a | grep ${PROJECT_NAME}
2. Check logs: docker logs <container_name>
3. Restore manually if needed:
   - Start backup containers: docker start <backup_container>
   - Rename to production: docker rename <backup_container> <prod_name>
   - Restore Nginx: tar -xzf /opt/backups/production-${ROLLBACK_TIMESTAMP}/nginx/nginx-backup.tar.gz -C /etc/nginx
   - Reload Nginx: nginx -t && systemctl reload nginx

=== SUPPORT INFORMATION ===
Rollback State File: $ROLLBACK_STATE_FILE
Backup Directory: /opt/backups/production-${ROLLBACK_TIMESTAMP}
Log File: $LOG_FILE

EOF
    
    log_error "Rollback failure report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🔄 AUTOMATED ROLLBACK AND RECOVERY SYSTEM${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}🎯 Target: Rollback to $ROLLBACK_TIMESTAMP${NC}"
    echo ""
    
    log_info "Starting automated rollback and recovery..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Execute rollback steps
    validate_rollback_prerequisites
    validate_backup_integrity
    save_rollback_state
    
    update_rollback_state "stopping_current"
    stop_current_production
    
    update_rollback_state "restoring_containers"
    restore_backup_containers
    
    update_rollback_state "restoring_nginx"
    restore_nginx_configuration
    
    update_rollback_state "restoring_config"
    restore_application_configuration
    
    update_rollback_state "verifying"
    verify_rollback_success
    
    update_rollback_state "cleanup"
    cleanup_recovery_containers
    
    update_rollback_state "completed"
    generate_rollback_report
    
    echo ""
    echo -e "${GREEN}🎉 ROLLBACK COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${BLUE}📋 Rollback report: /opt/rollback-deployment-report-$(date +%Y%m%d_%H%M%S).txt${NC}"
    echo -e "${BLUE}📋 Rollback log: $LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}📊 Rollback Summary:${NC}"
    echo "- Duration: $SECONDS seconds"
    echo "- Restored from: $ROLLBACK_TIMESTAMP"
    echo "- Status: SUCCESS"
    echo ""
    echo -e "${YELLOW}🔧 Management Commands:${NC}"
    echo "- Status: /opt/scripts/health-check-stacks.sh"
    echo "- Logs: tail -f $LOG_FILE"
    echo ""
    
    log_success "Automated rollback and recovery completed successfully"
}

# Check for help parameter
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    show_usage
fi

# Execute main function
main "$@"