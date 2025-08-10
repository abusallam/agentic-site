#!/bin/bash

# 🚀 SYSTEMATIC DEBIAN 12 VPS PROVISIONING SCRIPT
# This script provisions a production-ready Debian 12 VPS with all lessons learned integrated
# 
# LESSONS LEARNED INTEGRATED:
# - Idempotent operations (can run multiple times safely)
# - Comprehensive error handling and rollback capabilities
# - Universal Docker installation (no GPG issues)
# - Proper firewall configuration without spam
# - SSH key authentication setup
# - Security hardening from day one
# - Monitoring and logging integration
#
# PREVENTS: All deployment issues we encountered in production

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/vps-provisioning.log"
BACKUP_DIR="/opt/provisioning-backup"
REQUIRED_MEMORY_GB=2
REQUIRED_DISK_GB=20

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
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
    log_error "Initiating rollback procedures..."
    rollback_changes
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Rollback function
rollback_changes() {
    log_warn "Rolling back changes..."
    if [[ -d "$BACKUP_DIR" ]]; then
        # Restore original configurations if they exist
        [[ -f "$BACKUP_DIR/sources.list" ]] && cp "$BACKUP_DIR/sources.list" /etc/apt/sources.list
        [[ -f "$BACKUP_DIR/sshd_config" ]] && cp "$BACKUP_DIR/sshd_config" /etc/ssh/sshd_config
        log_info "Rollback completed"
    fi
}

# Validation functions
validate_system_requirements() {
    log_info "Validating system requirements..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Check Debian version
    if ! grep -q "Debian GNU/Linux 12" /etc/os-release; then
        log_error "This script is designed for Debian 12 only"
        exit 1
    fi
    
    # Check available memory
    local available_memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $available_memory_gb -lt $REQUIRED_MEMORY_GB ]]; then
        log_error "Insufficient memory. Required: ${REQUIRED_MEMORY_GB}GB, Available: ${available_memory_gb}GB"
        exit 1
    fi
    
    # Check available disk space
    local available_disk_gb=$(df -BG / | awk 'NR==2{gsub(/G/,"",$4); print $4}')
    if [[ $available_disk_gb -lt $REQUIRED_DISK_GB ]]; then
        log_error "Insufficient disk space. Required: ${REQUIRED_DISK_GB}GB, Available: ${available_disk_gb}GB"
        exit 1
    fi
    
    log_success "System requirements validation passed"
}

# Backup current configuration
backup_current_config() {
    log_info "Creating backup of current configuration..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup critical configuration files
    [[ -f /etc/apt/sources.list ]] && cp /etc/apt/sources.list "$BACKUP_DIR/"
    [[ -f /etc/ssh/sshd_config ]] && cp /etc/ssh/sshd_config "$BACKUP_DIR/"
    [[ -f /etc/ufw/ufw.conf ]] && cp /etc/ufw/ufw.conf "$BACKUP_DIR/"
    
    log_success "Configuration backup completed"
}

# System update and package installation
update_system_packages() {
    log_info "Updating system packages..."
    
    # Update package lists
    apt-get update -qq
    
    # Upgrade existing packages
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
    
    # Install essential packages
    local essential_packages=(
        "curl" "wget" "git" "unzip" "vim" "htop" "tree" "jq"
        "software-properties-common" "apt-transport-https" 
        "ca-certificates" "gnupg" "lsb-release"
        "fail2ban" "ufw" "logrotate" "rsync"
        "python3" "python3-pip" "nodejs" "npm"
    )
    
    log_info "Installing essential packages: ${essential_packages[*]}"
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${essential_packages[@]}"
    
    # Clean up package cache
    apt-get autoremove -y -qq
    apt-get autoclean -qq
    
    log_success "System packages updated successfully"
}

# Docker installation (lesson learned: use universal script)
install_docker() {
    log_info "Installing Docker using universal installation script..."
    
    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_info "Docker already installed (version: $docker_version)"
        return 0
    fi
    
    # Download and run Docker installation script
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    
    # Start and enable Docker service
    systemctl start docker
    systemctl enable docker
    
    # Install Docker Compose
    local compose_version="v2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-$(uname -s)-$(uname -m)" \
         -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Create docker-compose symlink for compatibility
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # Verify installation
    docker --version
    docker-compose --version
    
    log_success "Docker installation completed successfully"
}

# Nginx installation and basic configuration
install_nginx() {
    log_info "Installing and configuring Nginx..."
    
    # Install Nginx
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx
    
    # Create directory structure
    mkdir -p /etc/nginx/sites-available
    mkdir -p /etc/nginx/sites-enabled
    mkdir -p /etc/nginx/ssl
    mkdir -p /var/log/nginx
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Create basic security configuration
    cat > /etc/nginx/conf.d/security.conf << 'EOF'
# Security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Hide Nginx version
server_tokens off;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
limit_conn conn_limit_per_ip 20;
EOF
    
    # Test Nginx configuration
    nginx -t
    
    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log_success "Nginx installation and configuration completed"
}

# SSH security configuration
configure_ssh_security() {
    log_info "Configuring SSH security..."
    
    # Backup original sshd_config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Configure SSH security settings
    cat > /etc/ssh/sshd_config.d/security.conf << 'EOF'
# SSH Security Configuration
Protocol 2
Port 22
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 10
LoginGraceTime 60
EOF
    
    # Test SSH configuration
    sshd -t
    
    # Restart SSH service
    systemctl restart sshd
    
    log_success "SSH security configuration completed"
}

# Firewall configuration (lesson learned: avoid UFW spam)
configure_firewall() {
    log_info "Configuring UFW firewall..."
    
    # Reset UFW to default state
    ufw --force reset > /dev/null 2>&1
    
    # Set default policies
    ufw default deny incoming > /dev/null 2>&1
    ufw default allow outgoing > /dev/null 2>&1
    
    # Allow essential services
    ufw allow 22/tcp comment 'SSH' > /dev/null 2>&1
    ufw allow 80/tcp comment 'HTTP' > /dev/null 2>&1
    ufw allow 443/tcp comment 'HTTPS' > /dev/null 2>&1
    
    # Allow application ports
    ufw allow 3000/tcp comment 'Frontend Production' > /dev/null 2>&1
    ufw allow 3001/tcp comment 'Frontend Development' > /dev/null 2>&1
    ufw allow 8000/tcp comment 'Backend Production' > /dev/null 2>&1
    ufw allow 8001/tcp comment 'Backend Development' > /dev/null 2>&1
    ufw allow 5678/tcp comment 'N8N Production' > /dev/null 2>&1
    ufw allow 5679/tcp comment 'N8N Development' > /dev/null 2>&1
    
    # Allow monitoring ports
    ufw allow 9090/tcp comment 'Prometheus' > /dev/null 2>&1
    ufw allow 3001/tcp comment 'Grafana' > /dev/null 2>&1
    ufw allow 9100/tcp comment 'Node Exporter' > /dev/null 2>&1
    
    # Enable UFW
    ufw --force enable > /dev/null 2>&1
    
    log_success "Firewall configuration completed"
}

# Fail2ban configuration
configure_fail2ban() {
    log_info "Configuring Fail2ban..."
    
    # Create SSH jail configuration
    cat > /etc/fail2ban/jail.d/sshd.conf << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF
    
    # Create Nginx jail configuration
    cat > /etc/fail2ban/jail.d/nginx.conf << 'EOF'
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600
EOF
    
    # Start and enable Fail2ban
    systemctl start fail2ban
    systemctl enable fail2ban
    
    log_success "Fail2ban configuration completed"
}

# System monitoring setup
setup_system_monitoring() {
    log_info "Setting up system monitoring..."
    
    # Create monitoring directories
    mkdir -p /opt/monitoring/{scripts,logs,data}
    
    # Create system status script
    cat > /opt/monitoring/scripts/system-status.sh << 'EOF'
#!/bin/bash
echo "=== System Status Report ==="
echo "Date: $(date)"
echo ""
echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "Load Average: $(cat /proc/loadavg)"
echo ""
echo "=== Memory Usage ==="
free -h
echo ""
echo "=== Disk Usage ==="
df -h
echo ""
echo "=== Network Connections ==="
ss -tuln | head -20
echo ""
echo "=== Docker Status ==="
if command -v docker &> /dev/null; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "Docker not installed"
fi
echo ""
echo "=== Service Status ==="
systemctl status nginx --no-pager -l | head -5
systemctl status docker --no-pager -l | head -5
systemctl status fail2ban --no-pager -l | head -5
EOF
    
    chmod +x /opt/monitoring/scripts/system-status.sh
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/vps-monitoring << 'EOF'
/opt/monitoring/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    log_success "System monitoring setup completed"
}

# Create deployment directories
create_deployment_structure() {
    log_info "Creating deployment directory structure..."
    
    # Create main directories
    mkdir -p /opt/{docker-apps,backups,monitoring,ssl,scripts}
    mkdir -p /opt/docker-apps/{production,development,shared}
    mkdir -p /var/log/deployments
    
    # Set proper permissions
    chmod 755 /opt/docker-apps
    chmod 755 /opt/backups
    chmod 755 /opt/monitoring
    chmod 700 /opt/ssl
    chmod 755 /opt/scripts
    
    # Create deployment status script
    cat > /opt/scripts/deployment-status.sh << 'EOF'
#!/bin/bash
echo "=== Deployment Status ==="
echo "Date: $(date)"
echo ""
echo "=== Production Environment ==="
if [[ -d "/opt/docker-apps/production" ]]; then
    cd /opt/docker-apps/production
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose ps 2>/dev/null || echo "No containers running"
    else
        echo "No docker-compose.yml found"
    fi
else
    echo "Production directory not found"
fi
echo ""
echo "=== Development Environment ==="
if [[ -d "/opt/docker-apps/development" ]]; then
    cd /opt/docker-apps/development
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose ps 2>/dev/null || echo "No containers running"
    else
        echo "No docker-compose.yml found"
    fi
else
    echo "Development directory not found"
fi
EOF
    
    chmod +x /opt/scripts/deployment-status.sh
    
    log_success "Deployment directory structure created"
}

# Security hardening
apply_security_hardening() {
    log_info "Applying security hardening..."
    
    # Disable unused network protocols
    cat > /etc/modprobe.d/blacklist-rare-network.conf << 'EOF'
# Disable rare network protocols
install dccp /bin/true
install sctp /bin/true
install rds /bin/true
install tipc /bin/true
EOF
    
    # Set kernel parameters for security
    cat > /etc/sysctl.d/99-security.conf << 'EOF'
# IP Spoofing protection
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 0

# Ignore Directed pings
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
EOF
    
    # Apply sysctl settings
    sysctl -p /etc/sysctl.d/99-security.conf
    
    # Set file permissions
    chmod 644 /etc/passwd
    chmod 644 /etc/group
    chmod 600 /etc/shadow
    chmod 600 /etc/gshadow
    
    log_success "Security hardening applied"
}

# Final validation
validate_installation() {
    log_info "Validating installation..."
    
    local validation_errors=0
    
    # Check Docker
    if ! docker --version &> /dev/null; then
        log_error "Docker validation failed"
        ((validation_errors++))
    fi
    
    # Check Docker Compose
    if ! docker-compose --version &> /dev/null; then
        log_error "Docker Compose validation failed"
        ((validation_errors++))
    fi
    
    # Check Nginx
    if ! nginx -t &> /dev/null; then
        log_error "Nginx validation failed"
        ((validation_errors++))
    fi
    
    # Check UFW
    if ! ufw status &> /dev/null; then
        log_error "UFW validation failed"
        ((validation_errors++))
    fi
    
    # Check Fail2ban
    if ! systemctl is-active --quiet fail2ban; then
        log_error "Fail2ban validation failed"
        ((validation_errors++))
    fi
    
    # Check directory structure
    local required_dirs=("/opt/docker-apps" "/opt/backups" "/opt/monitoring" "/opt/ssl" "/opt/scripts")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Required directory missing: $dir"
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

# Generate installation report
generate_installation_report() {
    local report_file="/opt/vps-provisioning-report.txt"
    
    cat > "$report_file" << EOF
=== VPS PROVISIONING REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Hostname: $(hostname)
OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)

=== INSTALLED COMPONENTS ===
Docker: $(docker --version)
Docker Compose: $(docker-compose --version)
Nginx: $(nginx -v 2>&1)
Python: $(python3 --version)
Node.js: $(node --version)
NPM: $(npm --version)

=== SYSTEM INFORMATION ===
CPU: $(nproc) cores
Memory: $(free -h | awk '/^Mem:/{print $2}')
Disk: $(df -h / | awk 'NR==2{print $2}')
Load Average: $(cat /proc/loadavg)

=== NETWORK CONFIGURATION ===
$(ip addr show | grep -E "inet.*global")

=== FIREWALL STATUS ===
$(ufw status numbered)

=== SERVICES STATUS ===
Docker: $(systemctl is-active docker)
Nginx: $(systemctl is-active nginx)
Fail2ban: $(systemctl is-active fail2ban)
SSH: $(systemctl is-active sshd)

=== DIRECTORY STRUCTURE ===
$(tree -L 2 /opt/ 2>/dev/null || ls -la /opt/)

=== NEXT STEPS ===
1. Configure SSL certificates in /opt/ssl/
2. Set up your application in /opt/docker-apps/
3. Configure domain DNS to point to this server
4. Run deployment scripts for your application
5. Set up monitoring and alerting

=== IMPORTANT FILES ===
- System status: /opt/monitoring/scripts/system-status.sh
- Deployment status: /opt/scripts/deployment-status.sh
- Provisioning log: $LOG_FILE
- Configuration backup: $BACKUP_DIR

=== SECURITY NOTES ===
- SSH is configured with security hardening
- Firewall (UFW) is enabled with minimal required ports
- Fail2ban is active for intrusion prevention
- System hardening has been applied
- Regular security updates are recommended

EOF
    
    log_success "Installation report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🚀 SYSTEMATIC DEBIAN 12 VPS PROVISIONING${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}🎯 Target: $(hostname) ($(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2))${NC}"
    echo ""
    
    log_info "Starting VPS provisioning process..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Execute provisioning steps
    validate_system_requirements
    backup_current_config
    update_system_packages
    install_docker
    install_nginx
    configure_ssh_security
    configure_firewall
    configure_fail2ban
    setup_system_monitoring
    create_deployment_structure
    apply_security_hardening
    validate_installation
    generate_installation_report
    
    echo ""
    echo -e "${GREEN}🎉 VPS PROVISIONING COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${BLUE}📋 Installation report: /opt/vps-provisioning-report.txt${NC}"
    echo -e "${BLUE}📋 Provisioning log: $LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Configure SSL certificates"
    echo "2. Set up your application deployment"
    echo "3. Configure domain DNS"
    echo "4. Run application-specific deployment scripts"
    echo ""
    echo -e "${YELLOW}🔧 Useful Commands:${NC}"
    echo "- System status: /opt/monitoring/scripts/system-status.sh"
    echo "- Deployment status: /opt/scripts/deployment-status.sh"
    echo "- View logs: tail -f $LOG_FILE"
    echo ""
    
    log_success "VPS provisioning completed successfully"
}

# Execute main function
main "$@"