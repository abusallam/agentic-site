#!/bin/bash

# Backup and Restore System
# This script handles automated backup and restore operations
# Usage: ./backup.sh [--create|--restore|--list|--cleanup]

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
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/backups"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/backup.log"
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

# Create comprehensive backup
create_backup() {
    local backup_name="${1:-full-backup-$(date +%Y%m%d-%H%M%S)}"
    local backup_path="${BACKUP_STORAGE_PATH:-/opt/backups}"
    
    log_info "Creating comprehensive backup: $backup_name"
    
    ssh_connect "
        echo 'Creating backup directory...'
        mkdir -p $backup_path
        
        echo 'Creating backup: $backup_name'
        backup_file=\"$backup_path/${backup_name}.tar.gz\"
        
        echo 'Backing up Docker containers and volumes...'
        mkdir -p /tmp/backup-$backup_name
        
        # Backup Docker compose files
        echo 'Backing up Docker Compose configurations...'
        find /opt -name 'docker-compose.yml' -exec cp --parents {} /tmp/backup-$backup_name/ \; 2>/dev/null || echo 'No compose files found'
        
        # Backup container data volumes
        echo 'Backing up Docker volumes...'
        for volume in \$(docker volume ls -q 2>/dev/null); do
            echo \"Backing up volume: \$volume\"
            docker run --rm -v \$volume:/data -v /tmp/backup-$backup_name:/backup alpine tar -czf /backup/volume-\$volume.tar.gz -C /data . 2>/dev/null || echo \"Failed to backup volume \$volume\"
        done
        
        # Backup Nginx configurations
        echo 'Backing up Nginx configurations...'
        cp -r /etc/nginx /tmp/backup-$backup_name/ 2>/dev/null || echo 'Nginx config backup failed'
        
        # Backup SSL certificates
        echo 'Backing up SSL certificates...'
        cp -r /etc/nginx/ssl /tmp/backup-$backup_name/ssl 2>/dev/null || echo 'SSL backup failed'
        
        # Backup deployment configurations
        echo 'Backing up deployment configurations...'
        cp -r /opt/deployments /tmp/backup-$backup_name/ 2>/dev/null || echo 'Deployment config backup failed'
        
        # Backup system configurations
        echo 'Backing up system configurations...'
        mkdir -p /tmp/backup-$backup_name/system
        cp /etc/ufw/ufw.conf /tmp/backup-$backup_name/system/ 2>/dev/null || echo 'UFW config not found'
        cp /etc/fail2ban/jail.local /tmp/backup-$backup_name/system/ 2>/dev/null || echo 'Fail2ban config not found'
        
        # Create backup metadata
        echo 'Creating backup metadata...'
        cat > /tmp/backup-$backup_name/backup-info.txt << EOF
Backup Name: $backup_name
Created: \$(date)
Hostname: \$(hostname)
VPS IP: $VPS_IP
Docker Version: \$(docker --version)
Running Containers: \$(docker ps --format '{{.Names}}' | tr '\n' ', ')
System Info: \$(uname -a)
Disk Usage: \$(df -h /)
EOF
        
        # Create compressed backup
        echo 'Compressing backup...'
        tar -czf \"\$backup_file\" -C /tmp backup-$backup_name
        
        # Cleanup temporary files
        rm -rf /tmp/backup-$backup_name
        
        # Verify backup
        if [[ -f \"\$backup_file\" ]]; then
            backup_size=\$(du -h \"\$backup_file\" | cut -f1)
            echo \"Backup created successfully: \$backup_file (\$backup_size)\"
            
            # Test backup integrity
            if tar -tzf \"\$backup_file\" >/dev/null 2>&1; then
                echo 'Backup integrity verified'
            else
                echo 'WARNING: Backup integrity check failed'
            fi
        else
            echo 'ERROR: Backup creation failed'
            exit 1
        fi
        
        # Cleanup old backups
        echo 'Cleaning up old backups...'
        find $backup_path -name '*.tar.gz' -type f -mtime +${BACKUP_RETENTION_DAYS:-30} -delete 2>/dev/null || echo 'Cleanup completed'
        
        echo 'Backup process completed'
    "
    
    log_success "Backup created: $backup_name"
}

# List available backups
list_backups() {
    log_info "Listing available backups..."
    
    ssh_connect "
        backup_path=\"${BACKUP_STORAGE_PATH:-/opt/backups}\"
        
        if [[ -d \"\$backup_path\" ]]; then
            echo '=== AVAILABLE BACKUPS ==='
            echo 'Location: '\$backup_path
            echo ''
            
            if ls \$backup_path/*.tar.gz >/dev/null 2>&1; then
                echo 'Backup Files:'
                for backup in \$backup_path/*.tar.gz; do
                    if [[ -f \"\$backup\" ]]; then
                        backup_name=\$(basename \"\$backup\")
                        backup_size=\$(du -h \"\$backup\" | cut -f1)
                        backup_date=\$(stat -c %y \"\$backup\" | cut -d' ' -f1,2 | cut -d'.' -f1)
                        echo \"  \$backup_name (\$backup_size) - Created: \$backup_date\"
                    fi
                done
            else
                echo 'No backup files found'
            fi
            
            echo ''
            echo 'Disk Usage:'
            du -sh \$backup_path 2>/dev/null || echo 'Cannot determine disk usage'
        else
            echo 'Backup directory does not exist: '\$backup_path
        fi
    "
}

# Restore from backup
restore_backup() {
    local backup_name="$1"
    
    if [[ -z "$backup_name" ]]; then
        log_error "Backup name is required for restore operation"
        return 1
    fi
    
    log_info "Restoring from backup: $backup_name"
    
    ssh_connect "
        backup_path=\"${BACKUP_STORAGE_PATH:-/opt/backups}\"
        backup_file=\"\$backup_path/$backup_name\"
        
        if [[ ! -f \"\$backup_file\" ]]; then
            echo 'ERROR: Backup file not found: '\$backup_file
            exit 1
        fi
        
        echo 'Verifying backup integrity...'
        if ! tar -tzf \"\$backup_file\" >/dev/null 2>&1; then
            echo 'ERROR: Backup file is corrupted'
            exit 1
        fi
        
        echo 'Creating restore point...'
        restore_point=\"restore-point-\$(date +%Y%m%d-%H%M%S)\"
        mkdir -p /tmp/\$restore_point
        
        # Backup current state before restore
        echo 'Backing up current state...'
        cp -r /etc/nginx /tmp/\$restore_point/ 2>/dev/null || echo 'Current nginx backup failed'
        cp -r /opt/deployments /tmp/\$restore_point/ 2>/dev/null || echo 'Current deployments backup failed'
        
        echo 'Extracting backup...'
        cd /tmp
        tar -xzf \"\$backup_file\"
        
        restore_dir=\$(find /tmp -name 'backup-*' -type d | head -1)
        if [[ -z \"\$restore_dir\" ]]; then
            echo 'ERROR: Cannot find backup data in archive'
            exit 1
        fi
        
        echo 'Stopping services before restore...'
        systemctl stop nginx 2>/dev/null || echo 'Nginx not running'
        docker-compose down 2>/dev/null || echo 'No compose services to stop'
        
        echo 'Restoring configurations...'
        
        # Restore Nginx configuration
        if [[ -d \"\$restore_dir/nginx\" ]]; then
            echo 'Restoring Nginx configuration...'
            cp -r \"\$restore_dir/nginx\"/* /etc/nginx/ 2>/dev/null || echo 'Nginx restore failed'
        fi
        
        # Restore SSL certificates
        if [[ -d \"\$restore_dir/ssl\" ]]; then
            echo 'Restoring SSL certificates...'
            mkdir -p /etc/nginx/ssl
            cp -r \"\$restore_dir/ssl\"/* /etc/nginx/ssl/ 2>/dev/null || echo 'SSL restore failed'
        fi
        
        # Restore deployment configurations
        if [[ -d \"\$restore_dir/deployments\" ]]; then
            echo 'Restoring deployment configurations...'
            cp -r \"\$restore_dir/deployments\"/* /opt/deployments/ 2>/dev/null || echo 'Deployment restore failed'
        fi
        
        # Restore Docker volumes
        echo 'Restoring Docker volumes...'
        for volume_backup in \"\$restore_dir\"/volume-*.tar.gz; do
            if [[ -f \"\$volume_backup\" ]]; then
                volume_name=\$(basename \"\$volume_backup\" .tar.gz | sed 's/volume-//')
                echo \"Restoring volume: \$volume_name\"
                docker volume create \$volume_name 2>/dev/null || echo \"Volume \$volume_name already exists\"
                docker run --rm -v \$volume_name:/data -v \"\$volume_backup\":/backup.tar.gz alpine sh -c 'cd /data && tar -xzf /backup.tar.gz' 2>/dev/null || echo \"Failed to restore volume \$volume_name\"
            fi
        done
        
        echo 'Testing configurations...'
        nginx -t 2>/dev/null || echo 'WARNING: Nginx configuration test failed'
        
        echo 'Starting services...'
        systemctl start nginx 2>/dev/null || echo 'Failed to start nginx'
        
        # Cleanup
        rm -rf \"\$restore_dir\"
        
        echo 'Restore completed'
        echo \"Restore point saved at: /tmp/\$restore_point\"
    "
    
    log_success "Restore completed from backup: $backup_name"
}

# Cleanup old backups
cleanup_backups() {
    local retention_days="${1:-${BACKUP_RETENTION_DAYS:-30}}"
    
    log_info "Cleaning up backups older than $retention_days days..."
    
    ssh_connect "
        backup_path=\"${BACKUP_STORAGE_PATH:-/opt/backups}\"
        
        if [[ -d \"\$backup_path\" ]]; then
            echo 'Cleaning up old backups...'
            
            # List files to be deleted
            echo 'Files to be deleted:'
            find \$backup_path -name '*.tar.gz' -type f -mtime +$retention_days -ls 2>/dev/null || echo 'No old backups found'
            
            # Delete old backups
            deleted_count=\$(find \$backup_path -name '*.tar.gz' -type f -mtime +$retention_days -delete -print 2>/dev/null | wc -l)
            echo \"Deleted \$deleted_count old backup files\"
            
            # Show remaining backups
            echo 'Remaining backups:'
            ls -lah \$backup_path/*.tar.gz 2>/dev/null || echo 'No backups remaining'
            
            echo 'Cleanup completed'
        else
            echo 'Backup directory does not exist'
        fi
    "
    
    log_success "Backup cleanup completed"
}

# Setup automated backups
setup_automated_backups() {
    log_info "Setting up automated backup schedule..."
    
    ssh_connect "
        echo 'Setting up automated backup cron job...'
        
        # Create backup script on VPS
        cat > /opt/scripts/automated-backup.sh << 'BACKUP_SCRIPT_EOF'
#!/bin/bash
# Automated Backup Script

BACKUP_PATH=\"${BACKUP_STORAGE_PATH:-/opt/backups}\"
RETENTION_DAYS=\"${BACKUP_RETENTION_DAYS:-30}\"
LOG_FILE=\"/var/log/automated-backup.log\"

log_message() {
    echo \"\$(date '+%Y-%m-%d %H:%M:%S') [\$1] \$2\" >> \"\$LOG_FILE\"
}

log_message \"INFO\" \"Starting automated backup\"

# Create backup
backup_name=\"auto-backup-\$(date +%Y%m%d-%H%M%S)\"
backup_file=\"\$BACKUP_PATH/\$backup_name.tar.gz\"

mkdir -p \"\$BACKUP_PATH\"
mkdir -p /tmp/backup-temp

# Backup Docker data
docker volume ls -q | while read volume; do
    docker run --rm -v \$volume:/data -v /tmp/backup-temp:/backup alpine tar -czf /backup/volume-\$volume.tar.gz -C /data . 2>/dev/null || log_message \"WARN\" \"Failed to backup volume \$volume\"
done

# Backup configurations
cp -r /etc/nginx /tmp/backup-temp/ 2>/dev/null || log_message \"WARN\" \"Nginx backup failed\"
cp -r /opt/deployments /tmp/backup-temp/ 2>/dev/null || log_message \"WARN\" \"Deployments backup failed\"

# Create backup archive
tar -czf \"\$backup_file\" -C /tmp backup-temp 2>/dev/null

if [[ -f \"\$backup_file\" ]]; then
    log_message \"SUCCESS\" \"Backup created: \$backup_file\"
    
    # Cleanup old backups
    find \"\$BACKUP_PATH\" -name 'auto-backup-*.tar.gz' -type f -mtime +\$RETENTION_DAYS -delete 2>/dev/null
    log_message \"INFO\" \"Old backups cleaned up\"
else
    log_message \"ERROR\" \"Backup creation failed\"
fi

# Cleanup temp files
rm -rf /tmp/backup-temp

log_message \"INFO\" \"Automated backup completed\"
BACKUP_SCRIPT_EOF

        chmod +x /opt/scripts/automated-backup.sh
        
        # Add to crontab (daily at 2 AM)
        (crontab -l 2>/dev/null | grep -v automated-backup; echo '0 2 * * * /opt/scripts/automated-backup.sh') | crontab -
        
        echo 'Automated backup schedule configured (daily at 2 AM)'
        echo 'Current crontab:'
        crontab -l | grep backup || echo 'No backup jobs found'
    "
    
    log_success "Automated backup schedule configured"
}

# Main backup function
main_backup() {
    echo -e "${PURPLE}💾 Backup and Restore System${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    case "${1:-}" in
        --create)
            backup_name="${2:-}"
            create_backup "$backup_name"
            ;;
        --restore)
            backup_name="${2:-}"
            if [[ -z "$backup_name" ]]; then
                echo -e "${RED}Error: Backup name required for restore${NC}"
                echo "Usage: $0 --restore BACKUP_NAME"
                exit 1
            fi
            restore_backup "$backup_name"
            ;;
        --list)
            list_backups
            ;;
        --cleanup)
            retention_days="${2:-}"
            cleanup_backups "$retention_days"
            ;;
        --setup-automated)
            setup_automated_backups
            ;;
        --help|-h)
            echo "Backup and Restore System - Usage:"
            echo ""
            echo "  --create [NAME]          Create a new backup (optional name)"
            echo "  --restore NAME           Restore from specified backup"
            echo "  --list                   List available backups"
            echo "  --cleanup [DAYS]         Clean up old backups (default: 30 days)"
            echo "  --setup-automated        Setup automated daily backups"
            echo "  --help, -h               Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./backup.sh --create"
            echo "  ./backup.sh --create my-backup"
            echo "  ./backup.sh --restore full-backup-20250813-120000.tar.gz"
            echo "  ./backup.sh --list"
            echo "  ./backup.sh --cleanup 7"
            ;;
        *)
            echo -e "${YELLOW}No option specified. Listing available backups...${NC}"
            echo -e "${YELLOW}Use --help for available options.${NC}"
            echo ""
            list_backups
            ;;
    esac
}

# Execute main function
main_backup "$@"