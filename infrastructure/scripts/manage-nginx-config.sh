#!/bin/bash

# 🚀 NGINX CONFIGURATION MANAGEMENT SYSTEM
# This script manages Nginx configurations for zero-downtime deployments
# 
# LESSONS LEARNED INTEGRATED:
# - Proper SSL certificate management
# - Security headers and hardening
# - Zero-downtime deployment through port redirection
# - Configuration validation before applying
# - Automatic rollback on failure
# - Domain-based routing for prod/dev separation
#
# PREVENTS: Nginx configuration errors, SSL issues, downtime during deployments

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/nginx-management.log"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
SSL_CERT_DIR="/opt/ssl"
BACKUP_DIR="/opt/backups/nginx"

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
    rollback_nginx_config
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Rollback function
rollback_nginx_config() {
    log_warn "Rolling back Nginx configuration..."
    if [[ -f "$BACKUP_DIR/nginx.conf.backup" ]]; then
        cp "$BACKUP_DIR/nginx.conf.backup" /etc/nginx/nginx.conf
        log_info "Restored main nginx.conf"
    fi
    
    if [[ -d "$BACKUP_DIR/sites-enabled" ]]; then
        rm -rf "$NGINX_SITES_ENABLED"/*
        cp -r "$BACKUP_DIR/sites-enabled"/* "$NGINX_SITES_ENABLED"/ 2>/dev/null || true
        log_info "Restored sites-enabled configurations"
    fi
    
    if nginx -t 2>/dev/null; then
        systemctl reload nginx
        log_success "Nginx configuration rolled back successfully"
    else
        log_error "Rollback configuration is also invalid!"
    fi
}

# Validation functions
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Check Nginx installation
    if ! command -v nginx &> /dev/null; then
        log_error "Nginx is not installed"
        exit 1
    fi
    
    # Check if Nginx service is running
    if ! systemctl is-active --quiet nginx; then
        log_warn "Nginx service is not running, starting it..."
        systemctl start nginx
    fi
    
    # Create required directories
    mkdir -p "$NGINX_SITES_AVAILABLE" "$NGINX_SITES_ENABLED" "$SSL_CERT_DIR" "$BACKUP_DIR"
    
    log_success "Prerequisites validation passed"
}

# Backup current configuration
backup_current_config() {
    log_info "Backing up current Nginx configuration..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_subdir="$BACKUP_DIR/$timestamp"
    mkdir -p "$backup_subdir/sites-enabled"
    
    # Backup main nginx.conf
    cp /etc/nginx/nginx.conf "$backup_subdir/nginx.conf"
    cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf.backup"
    
    # Backup sites-enabled
    if [[ -n "$(ls -A $NGINX_SITES_ENABLED 2>/dev/null)" ]]; then
        cp -r "$NGINX_SITES_ENABLED"/* "$backup_subdir/sites-enabled/"
        cp -r "$NGINX_SITES_ENABLED"/* "$BACKUP_DIR/sites-enabled/" 2>/dev/null || mkdir -p "$BACKUP_DIR/sites-enabled"
    fi
    
    log_success "Configuration backed up to: $backup_subdir"
}

# Create production site configuration
create_production_config() {
    log_info "Creating production site configuration..."
    
    cat > "$NGINX_SITES_AVAILABLE/production.conf" << 'EOF'
# Production Configuration - main.consulting.sa
server {
    listen 80;
    server_name main.consulting.sa consulting.sa www.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name main.consulting.sa consulting.sa www.consulting.sa;

    # SSL Configuration
    ssl_certificate /opt/ssl/consulting.sa.crt;
    ssl_certificate_key /opt/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';" always;

    # Rate Limiting
    limit_req zone=api burst=20 nodelay;
    limit_conn conn_limit_per_ip 20;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Frontend (Production - Port 3000)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API (Production - Port 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # N8N Workflows (Production - Port 5678)
    location /workflows/ {
        proxy_pass http://127.0.0.1:5678/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Health Check Endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Security.txt
    location /.well-known/security.txt {
        return 200 "Contact: security@consulting.sa\nExpires: 2025-12-31T23:59:59.000Z\n";
        add_header Content-Type text/plain;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ \.(env|log|ini)$ {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/production.access.log;
    error_log /var/log/nginx/production.error.log;
}
EOF
    
    log_success "Production configuration created"
}

# Create development site configuration
create_development_config() {
    log_info "Creating development site configuration..."
    
    cat > "$NGINX_SITES_AVAILABLE/development.conf" << 'EOF'
# Development Configuration - dev.consulting.sa
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    # SSL Configuration
    ssl_certificate /opt/ssl/consulting.sa.crt;
    ssl_certificate_key /opt/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers (Less strict for development)
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate Limiting (More lenient for development)
    limit_req zone=api burst=50 nodelay;
    limit_conn conn_limit_per_ip 50;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Frontend (Development - Port 3001)
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API (Development - Port 8001)
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # N8N Workflows (Development - Port 5679)
    location /workflows/ {
        proxy_pass http://127.0.0.1:5679/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Health Check Endpoint
    location /health {
        access_log off;
        return 200 "healthy-dev\n";
        add_header Content-Type text/plain;
    }

    # Development Tools Access
    location /dev-tools/ {
        proxy_pass http://127.0.0.1:3001/dev-tools/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/development.access.log;
    error_log /var/log/nginx/development.error.log;
}
EOF
    
    log_success "Development configuration created"
}

# Create monitoring configuration
create_monitoring_config() {
    log_info "Creating monitoring site configuration..."
    
    cat > "$NGINX_SITES_AVAILABLE/monitoring.conf" << 'EOF'
# Monitoring Configuration - Internal Access Only
server {
    listen 80;
    server_name monitoring.consulting.sa;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monitoring.consulting.sa;

    # SSL Configuration
    ssl_certificate /opt/ssl/consulting.sa.crt;
    ssl_certificate_key /opt/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # IP Restriction (Uncomment and configure for production)
    # allow 192.168.1.0/24;
    # allow 10.0.0.0/8;
    # deny all;

    # Grafana (Port 3001)
    location /grafana/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Prometheus (Port 9090)
    location /prometheus/ {
        proxy_pass http://127.0.0.1:9090/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Node Exporter (Port 9100)
    location /node-exporter/ {
        proxy_pass http://127.0.0.1:9100/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Default monitoring dashboard
    location / {
        return 200 "Monitoring Dashboard\nGrafana: /grafana/\nPrometheus: /prometheus/\nNode Exporter: /node-exporter/\n";
        add_header Content-Type text/plain;
    }

    # Logging
    access_log /var/log/nginx/monitoring.access.log;
    error_log /var/log/nginx/monitoring.error.log;
}
EOF
    
    log_success "Monitoring configuration created"
}

# Update main nginx.conf with optimizations
update_main_nginx_config() {
    log_info "Updating main Nginx configuration..."
    
    cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 100M;

    # MIME Types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Rate Limiting Zones
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;

    # Logging Settings
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;

    # Security Headers (Global)
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Virtual Host Configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
    
    log_success "Main Nginx configuration updated"
}

# Enable site configurations
enable_site_configs() {
    log_info "Enabling site configurations..."
    
    # Remove existing enabled sites
    rm -f "$NGINX_SITES_ENABLED"/*
    
    # Enable production site
    ln -sf "$NGINX_SITES_AVAILABLE/production.conf" "$NGINX_SITES_ENABLED/"
    log_success "Enabled production site"
    
    # Enable development site
    ln -sf "$NGINX_SITES_AVAILABLE/development.conf" "$NGINX_SITES_ENABLED/"
    log_success "Enabled development site"
    
    # Enable monitoring site (optional)
    if [[ "${ENABLE_MONITORING:-false}" == "true" ]]; then
        ln -sf "$NGINX_SITES_AVAILABLE/monitoring.conf" "$NGINX_SITES_ENABLED/"
        log_success "Enabled monitoring site"
    fi
}

# Test and reload Nginx configuration
test_and_reload_nginx() {
    log_info "Testing Nginx configuration..."
    
    if nginx -t; then
        log_success "Nginx configuration test passed"
        
        log_info "Reloading Nginx..."
        systemctl reload nginx
        log_success "Nginx reloaded successfully"
        
        # Verify Nginx is running
        if systemctl is-active --quiet nginx; then
            log_success "Nginx service is active and running"
        else
            log_error "Nginx service is not running after reload"
            return 1
        fi
    else
        log_error "Nginx configuration test failed"
        return 1
    fi
}

# Zero-downtime port redirection
redirect_traffic() {
    local from_port="$1"
    local to_port="$2"
    local environment="$3"
    
    log_info "Redirecting traffic from port $from_port to $to_port for $environment"
    
    # Create temporary configuration for redirection
    local temp_config="/tmp/nginx-redirect-$environment.conf"
    
    if [[ "$environment" == "production" ]]; then
        sed "s/127\.0\.0\.1:$from_port/127.0.0.1:$to_port/g" "$NGINX_SITES_AVAILABLE/production.conf" > "$temp_config"
    else
        sed "s/127\.0\.0\.1:$from_port/127.0.0.1:$to_port/g" "$NGINX_SITES_AVAILABLE/development.conf" > "$temp_config"
    fi
    
    # Backup current configuration
    backup_current_config
    
    # Apply new configuration
    cp "$temp_config" "$NGINX_SITES_AVAILABLE/${environment}.conf"
    
    # Test and reload
    if test_and_reload_nginx; then
        log_success "Traffic redirection completed successfully"
        rm -f "$temp_config"
    else
        log_error "Traffic redirection failed, rolling back"
        rollback_nginx_config
        rm -f "$temp_config"
        return 1
    fi
}

# SSL certificate management
manage_ssl_certificates() {
    log_info "Managing SSL certificates..."
    
    # Check if SSL certificates exist
    if [[ -f "$SSL_CERT_DIR/consulting.sa.crt" && -f "$SSL_CERT_DIR/consulting.sa.key" ]]; then
        log_success "SSL certificates found"
        
        # Verify certificate validity
        if openssl x509 -in "$SSL_CERT_DIR/consulting.sa.crt" -noout -checkend 2592000; then
            log_success "SSL certificate is valid for at least 30 days"
        else
            log_warn "SSL certificate expires within 30 days"
        fi
    else
        log_warn "SSL certificates not found in $SSL_CERT_DIR"
        log_info "Please place your SSL certificates in:"
        log_info "  - Certificate: $SSL_CERT_DIR/consulting.sa.crt"
        log_info "  - Private Key: $SSL_CERT_DIR/consulting.sa.key"
    fi
}

# Create management commands
create_management_commands() {
    log_info "Creating Nginx management commands..."
    
    # Create nginx management script
    cat > /opt/scripts/nginx-manager.sh << 'EOF'
#!/bin/bash

# Nginx Management Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: $0 {status|test|reload|redirect|enable|disable} [options]"
    echo ""
    echo "Commands:"
    echo "  status                    - Show Nginx status and configuration"
    echo "  test                      - Test Nginx configuration"
    echo "  reload                    - Reload Nginx configuration"
    echo "  redirect <from> <to> <env> - Redirect traffic (zero-downtime)"
    echo "  enable <site>             - Enable site configuration"
    echo "  disable <site>            - Disable site configuration"
    echo ""
    echo "Examples:"
    echo "  $0 redirect 3000 3002 production  # Redirect prod traffic to new container"
    echo "  $0 enable monitoring               # Enable monitoring site"
    echo "  $0 test                           # Test configuration"
    exit 1
}

nginx_status() {
    echo -e "${BLUE}=== Nginx Status ===${NC}"
    systemctl status nginx --no-pager -l | head -10
    echo ""
    
    echo -e "${BLUE}=== Enabled Sites ===${NC}"
    ls -la /etc/nginx/sites-enabled/
    echo ""
    
    echo -e "${BLUE}=== Active Connections ===${NC}"
    ss -tuln | grep -E ":80|:443"
    echo ""
    
    echo -e "${BLUE}=== Recent Access Log ===${NC}"
    tail -5 /var/log/nginx/access.log 2>/dev/null || echo "No access log found"
}

nginx_test() {
    echo -e "${BLUE}Testing Nginx configuration...${NC}"
    if nginx -t; then
        echo -e "${GREEN}✓ Configuration test passed${NC}"
    else
        echo -e "${RED}✗ Configuration test failed${NC}"
        exit 1
    fi
}

nginx_reload() {
    nginx_test
    echo -e "${BLUE}Reloading Nginx...${NC}"
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx reloaded successfully${NC}"
}

nginx_redirect() {
    local from_port="$1"
    local to_port="$2"
    local environment="$3"
    
    echo -e "${YELLOW}Redirecting $environment traffic: $from_port → $to_port${NC}"
    /opt/scripts/manage-nginx-config.sh redirect "$from_port" "$to_port" "$environment"
}

nginx_enable_site() {
    local site="$1"
    echo -e "${BLUE}Enabling site: $site${NC}"
    ln -sf "/etc/nginx/sites-available/$site.conf" "/etc/nginx/sites-enabled/"
    nginx_reload
    echo -e "${GREEN}✓ Site $site enabled${NC}"
}

nginx_disable_site() {
    local site="$1"
    echo -e "${YELLOW}Disabling site: $site${NC}"
    rm -f "/etc/nginx/sites-enabled/$site.conf"
    nginx_reload
    echo -e "${GREEN}✓ Site $site disabled${NC}"
}

main() {
    case "${1:-}" in
        status)
            nginx_status
            ;;
        test)
            nginx_test
            ;;
        reload)
            nginx_reload
            ;;
        redirect)
            if [[ $# -ne 4 ]]; then
                echo -e "${RED}Error: redirect requires 3 arguments${NC}"
                usage
            fi
            nginx_redirect "$2" "$3" "$4"
            ;;
        enable)
            if [[ $# -ne 2 ]]; then
                echo -e "${RED}Error: enable requires site name${NC}"
                usage
            fi
            nginx_enable_site "$2"
            ;;
        disable)
            if [[ $# -ne 2 ]]; then
                echo -e "${RED}Error: disable requires site name${NC}"
                usage
            fi
            nginx_disable_site "$2"
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
EOF
    
    chmod +x /opt/scripts/nginx-manager.sh
    
    log_success "Nginx management commands created"
}

# Validate Nginx setup
validate_nginx_setup() {
    log_info "Validating Nginx setup..."
    
    local validation_errors=0
    
    # Check configuration files
    local required_configs=(
        "$NGINX_SITES_AVAILABLE/production.conf"
        "$NGINX_SITES_AVAILABLE/development.conf"
    )
    
    for config in "${required_configs[@]}"; do
        if [[ ! -f "$config" ]]; then
            log_error "Required configuration missing: $config"
            ((validation_errors++))
        fi
    done
    
    # Check enabled sites
    if [[ ! -L "$NGINX_SITES_ENABLED/production.conf" ]]; then
        log_error "Production site not enabled"
        ((validation_errors++))
    fi
    
    if [[ ! -L "$NGINX_SITES_ENABLED/development.conf" ]]; then
        log_error "Development site not enabled"
        ((validation_errors++))
    fi
    
    # Test Nginx configuration
    if ! nginx -t 2>/dev/null; then
        log_error "Nginx configuration test failed"
        ((validation_errors++))
    fi
    
    # Check Nginx service
    if ! systemctl is-active --quiet nginx; then
        log_error "Nginx service is not active"
        ((validation_errors++))
    fi
    
    # Check management script
    if [[ ! -x "/opt/scripts/nginx-manager.sh" ]]; then
        log_error "Nginx management script not found or not executable"
        ((validation_errors++))
    fi
    
    if [[ $validation_errors -eq 0 ]]; then
        log_success "All validation checks passed"
        return 0
    else
        log_error "Validation failed with $validation_errors errors"
        return 1
    fi
}

# Generate configuration report
generate_config_report() {
    local report_file="/opt/nginx-config-report.txt"
    
    cat > "$report_file" << EOF
=== NGINX CONFIGURATION MANAGEMENT REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION

=== NGINX STATUS ===
Version: $(nginx -v 2>&1)
Status: $(systemctl is-active nginx)
Configuration Test: $(nginx -t 2>&1 | head -1)

=== SITE CONFIGURATIONS ===
Available Sites:
$(ls -la $NGINX_SITES_AVAILABLE/ | grep -v '^total')

Enabled Sites:
$(ls -la $NGINX_SITES_ENABLED/ | grep -v '^total')

=== SSL CERTIFICATES ===
$(if [[ -f "$SSL_CERT_DIR/consulting.sa.crt" ]]; then
    echo "Certificate: Found"
    openssl x509 -in "$SSL_CERT_DIR/consulting.sa.crt" -noout -subject -dates
else
    echo "Certificate: Not found"
fi)

=== DOMAIN ROUTING ===
Production Domains: main.consulting.sa, consulting.sa, www.consulting.sa
Development Domain: dev.consulting.sa
Monitoring Domain: monitoring.consulting.sa (optional)

=== PORT MAPPING ===
Production:
- Frontend: 443 → 3000
- Backend API: 443/api → 8000
- N8N Workflows: 443/workflows → 5678

Development:
- Frontend: 443 → 3001
- Backend API: 443/api → 8001
- N8N Workflows: 443/workflows → 5679

=== MANAGEMENT COMMANDS ===
Status Check: /opt/scripts/nginx-manager.sh status
Test Config: /opt/scripts/nginx-manager.sh test
Reload Config: /opt/scripts/nginx-manager.sh reload
Traffic Redirect: /opt/scripts/nginx-manager.sh redirect <from> <to> <env>

=== ZERO-DOWNTIME DEPLOYMENT ===
1. Duplicate development stack to new production containers
2. Use traffic redirection to switch to new containers
3. Validate new deployment health
4. Keep old containers for rollback (2 weeks)

=== SECURITY FEATURES ===
- SSL/TLS termination with modern protocols
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting and connection limits
- Gzip compression for performance
- Access logging and monitoring

=== LOG LOCATIONS ===
Main Access Log: /var/log/nginx/access.log
Main Error Log: /var/log/nginx/error.log
Production Logs: /var/log/nginx/production.*.log
Development Logs: /var/log/nginx/development.*.log
Management Log: $LOG_FILE

=== NEXT STEPS ===
1. Place SSL certificates in $SSL_CERT_DIR/
2. Update DNS records to point to this server
3. Test domain resolution and SSL
4. Deploy application containers
5. Test zero-downtime deployment process

EOF
    
    log_success "Configuration report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🚀 NGINX CONFIGURATION MANAGEMENT SYSTEM${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo ""
    
    # Handle command line arguments
    case "${1:-setup}" in
        setup)
            log_info "Starting Nginx configuration setup..."
            
            # Create log file
            mkdir -p "$(dirname "$LOG_FILE")"
            touch "$LOG_FILE"
            
            # Execute setup steps
            validate_prerequisites
            backup_current_config
            update_main_nginx_config
            create_production_config
            create_development_config
            create_monitoring_config
            enable_site_configs
            manage_ssl_certificates
            test_and_reload_nginx
            create_management_commands
            validate_nginx_setup
            generate_config_report
            
            echo ""
            echo -e "${GREEN}🎉 NGINX CONFIGURATION SETUP COMPLETED!${NC}"
            echo -e "${BLUE}📋 Configuration report: /opt/nginx-config-report.txt${NC}"
            echo -e "${BLUE}📋 Management log: $LOG_FILE${NC}"
            echo ""
            echo -e "${YELLOW}📝 Quick Commands:${NC}"
            echo "- Status: /opt/scripts/nginx-manager.sh status"
            echo "- Test: /opt/scripts/nginx-manager.sh test"
            echo "- Reload: /opt/scripts/nginx-manager.sh reload"
            echo ""
            ;;
        redirect)
            if [[ $# -ne 4 ]]; then
                echo "Usage: $0 redirect <from_port> <to_port> <environment>"
                exit 1
            fi
            redirect_traffic "$2" "$3" "$4"
            ;;
        *)
            echo "Usage: $0 {setup|redirect}"
            echo ""
            echo "Commands:"
            echo "  setup                     - Initial Nginx configuration setup"
            echo "  redirect <from> <to> <env> - Zero-downtime traffic redirection"
            exit 1
            ;;
    esac
    
    log_success "Nginx configuration management completed successfully"
}

# Execute main function
main "$@"