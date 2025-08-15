#!/bin/bash

# SSL Certificate Manager - Automated SSL Configuration
# This script manages SSL certificates and proxy configuration
# Usage: ./ssl-manager.sh [--setup-domain|--fix-ssl-issues|--renew-certificates]

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

# Validate required environment variables
required_vars=("VPS_IP" "VPS_USERNAME" "VPS_PASSWORD")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo -e "${RED}Error: Required environment variable $var is not set${NC}"
        exit 1
    fi
done

# Create necessary directories
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/ssl-configs"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/ssl-manager.log"
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

# Copy file to VPS
copy_to_vps() {
    local local_file="$1"
    local remote_path="$2"
    
    if [[ -n "${SSH_KEY_PATH:-}" && -f "$SSH_KEY_PATH" ]]; then
        scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$local_file" "$VPS_USERNAME@$VPS_IP:$remote_path"
    elif command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$local_file" "$VPS_USERNAME@$VPS_IP:$remote_path"
    else
        log_error "No SSH method available"
        return 1
    fi
}

# Discover current tactical ops configuration
discover_tactical_ops() {
    log_info "Discovering tactical ops deployment configuration..."
    
    local tactical_info
    tactical_info=$(ssh_connect "
        echo '=== TACTICAL OPS DISCOVERY ==='
        echo 'Container Status:'
        docker ps --filter name=tactical --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}'
        echo ''
        echo 'Container Logs (last 20 lines):'
        docker logs --tail 20 tacticalops-app 2>/dev/null || echo 'No logs available'
        echo ''
        echo 'Nginx Configuration:'
        ls -la /etc/nginx/sites-available/ | grep tactical || echo 'No tactical nginx config found'
        echo ''
        echo 'Current Nginx Sites:'
        ls -la /etc/nginx/sites-enabled/
        echo ''
        echo 'Port 3020 Status:'
        netstat -tlnp | grep :3020 || echo 'Port 3020 not accessible externally'
        echo ''
        echo 'Docker Network:'
        docker inspect tacticalops-app --format '{{.NetworkSettings.Networks}}' 2>/dev/null || echo 'Cannot inspect container'
    ")
    
    echo "$tactical_info"
    echo "$tactical_info" > "$CONFIG_DIR/ssl-configs/tactical-ops-discovery-$(date +%Y%m%d-%H%M%S).txt"
}

# Create SSL certificate for domain
create_ssl_certificate() {
    local domain="$1"
    
    log_info "Creating SSL certificate for domain: $domain"
    
    # For now, we'll use a self-signed certificate since we don't have Cloudflare configured
    # In production, this would integrate with Cloudflare API
    
    ssh_connect "
        echo 'Creating SSL certificate for $domain...'
        
        # Create SSL directory
        mkdir -p /etc/nginx/ssl
        
        # Generate self-signed certificate (temporary solution)
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/${domain}.key \
            -out /etc/nginx/ssl/${domain}.crt \
            -subj '/C=SA/ST=Riyadh/L=Riyadh/O=Consulting/CN=${domain}'
        
        # Set proper permissions
        chmod 600 /etc/nginx/ssl/${domain}.key
        chmod 644 /etc/nginx/ssl/${domain}.crt
        
        echo 'SSL certificate created for $domain'
        ls -la /etc/nginx/ssl/${domain}.*
    "
}

# Configure Nginx for tactical ops with SSL
configure_tactical_ops_nginx() {
    local domain="$1"
    
    log_info "Configuring Nginx for tactical ops domain: $domain"
    
    # Create Nginx configuration
    local nginx_config="/tmp/tacticalops-ssl.conf"
    cat > "$nginx_config" << EOF
# Tactical Ops SSL Configuration
server {
    listen 80;
    server_name $domain;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $domain;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/$domain.crt;
    ssl_certificate_key /etc/nginx/ssl/$domain.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:3020;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:3020/health;
        access_log off;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://127.0.0.1:3020;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/${domain}_access.log;
    error_log /var/log/nginx/${domain}_error.log;
}
EOF

    # Copy configuration to VPS
    copy_to_vps "$nginx_config" "/tmp/tacticalops-ssl.conf"
    
    # Install and enable the configuration
    ssh_connect "
        echo 'Installing Nginx configuration for $domain...'
        
        # Move configuration to sites-available
        mv /tmp/tacticalops-ssl.conf /etc/nginx/sites-available/tacticalops-ssl.conf
        
        # Remove old tactical ops configurations
        rm -f /etc/nginx/sites-enabled/tacticalops*.conf
        rm -f /etc/nginx/sites-available/tacticalops-fixed.conf
        
        # Enable new configuration
        ln -sf /etc/nginx/sites-available/tacticalops-ssl.conf /etc/nginx/sites-enabled/
        
        # Test Nginx configuration
        nginx -t
        
        if [ \$? -eq 0 ]; then
            echo 'Nginx configuration is valid, reloading...'
            systemctl reload nginx
            echo 'Nginx reloaded successfully'
        else
            echo 'Nginx configuration test failed'
            exit 1
        fi
        
        # Show enabled sites
        echo 'Enabled Nginx sites:'
        ls -la /etc/nginx/sites-enabled/
    "
    
    # Clean up temporary file
    rm -f "$nginx_config"
}

# Fix tactical ops container networking
fix_tactical_ops_container() {
    log_info "Fixing tactical ops container configuration..."
    
    ssh_connect "
        echo 'Analyzing tactical ops container...'
        
        # Check container health
        container_status=\$(docker inspect tacticalops-app --format '{{.State.Health.Status}}' 2>/dev/null || echo 'no-health-check')
        echo \"Container health status: \$container_status\"
        
        # Check if container is binding to localhost only
        port_binding=\$(docker port tacticalops-app 2>/dev/null || echo 'no-ports')
        echo \"Port binding: \$port_binding\"
        
        # Get container logs
        echo 'Recent container logs:'
        docker logs --tail 50 tacticalops-app 2>/dev/null || echo 'No logs available'
        
        # Check if we need to restart the container with proper port binding
        if echo \"\$port_binding\" | grep -q '127.0.0.1:3020'; then
            echo 'Container is correctly bound to localhost:3020'
            echo 'Nginx proxy should handle external access'
        else
            echo 'Container port binding may need adjustment'
        fi
        
        # Restart container if unhealthy
        if [ \"\$container_status\" = \"unhealthy\" ]; then
            echo 'Restarting unhealthy container...'
            docker restart tacticalops-app
            sleep 10
            echo 'Container restarted, checking status...'
            docker ps --filter name=tacticalops-app --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
        fi
    "
}

# Update firewall rules
update_firewall_rules() {
    log_info "Updating firewall rules for HTTPS access..."
    
    ssh_connect "
        echo 'Checking firewall status...'
        ufw status numbered
        
        echo 'Ensuring HTTPS is allowed...'
        ufw allow 443/tcp comment 'HTTPS' 2>/dev/null || echo 'HTTPS already allowed'
        ufw allow 80/tcp comment 'HTTP' 2>/dev/null || echo 'HTTP already allowed'
        
        echo 'Updated firewall status:'
        ufw status numbered
    "
}

# Test SSL configuration
test_ssl_configuration() {
    local domain="$1"
    
    log_info "Testing SSL configuration for domain: $domain"
    
    ssh_connect "
        echo 'Testing SSL configuration for $domain...'
        
        # Test HTTP redirect
        echo 'Testing HTTP redirect:'
        curl -I -s http://$domain/ | head -5 || echo 'HTTP test failed'
        
        echo ''
        echo 'Testing HTTPS connection:'
        curl -I -s -k https://$domain/ | head -5 || echo 'HTTPS test failed'
        
        echo ''
        echo 'Testing SSL certificate:'
        echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo 'SSL certificate test failed'
        
        echo ''
        echo 'Testing application response:'
        curl -s -k https://$domain/health 2>/dev/null || curl -s -k https://$domain/ | head -10 || echo 'Application test failed'
    "
}

# Main function to fix tactical ops SSL
fix_tactical_ops_ssl() {
    local domain="${1:-tacticalops.console.ts}"
    
    echo -e "${PURPLE}🔒 SSL Manager - Fixing Tactical Ops SSL Configuration${NC}"
    echo -e "${BLUE}========================================================${NC}"
    echo "Target Domain: $domain"
    echo "VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    # Step 1: Discover current configuration
    echo -e "${CYAN}🔍 Step 1: Discovering current tactical ops configuration...${NC}"
    discover_tactical_ops
    
    # Step 2: Create SSL certificate
    echo ""
    echo -e "${CYAN}🔐 Step 2: Creating SSL certificate...${NC}"
    create_ssl_certificate "$domain"
    
    # Step 3: Configure Nginx with SSL
    echo ""
    echo -e "${CYAN}⚙️ Step 3: Configuring Nginx with SSL...${NC}"
    configure_tactical_ops_nginx "$domain"
    
    # Step 4: Fix container configuration
    echo ""
    echo -e "${CYAN}🐳 Step 4: Fixing container configuration...${NC}"
    fix_tactical_ops_container
    
    # Step 5: Update firewall
    echo ""
    echo -e "${CYAN}🛡️ Step 5: Updating firewall rules...${NC}"
    update_firewall_rules
    
    # Step 6: Test configuration
    echo ""
    echo -e "${CYAN}🧪 Step 6: Testing SSL configuration...${NC}"
    test_ssl_configuration "$domain"
    
    echo ""
    echo -e "${GREEN}✅ Tactical Ops SSL Configuration Complete!${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo "- HTTP (redirects to HTTPS): http://$domain"
    echo "- HTTPS: https://$domain"
    echo "- Health Check: https://$domain/health"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update DNS to point $domain to $VPS_IP"
    echo "2. Test the application functionality"
    echo "3. Configure proper SSL certificate with Cloudflare (optional)"
    echo "4. Monitor container health and logs"
    echo ""
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "- Check container logs: docker logs tacticalops-app"
    echo "- Check Nginx logs: tail -f /var/log/nginx/${domain}_error.log"
    echo "- Test SSL: curl -I -k https://$domain"
}

# Setup SSL for any domain
setup_domain_ssl() {
    local domain="$1"
    
    if [[ -z "$domain" ]]; then
        log_error "Domain name is required"
        return 1
    fi
    
    log_info "Setting up SSL for domain: $domain"
    
    # Create SSL certificate
    create_ssl_certificate "$domain"
    
    # Basic Nginx configuration template
    local nginx_config="/tmp/${domain}-ssl.conf"
    cat > "$nginx_config" << EOF
server {
    listen 80;
    server_name $domain;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $domain;

    ssl_certificate /etc/nginx/ssl/$domain.crt;
    ssl_certificate_key /etc/nginx/ssl/$domain.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        # Configure your application proxy here
        return 200 'SSL configured for $domain';
        add_header Content-Type text/plain;
    }
}
EOF

    copy_to_vps "$nginx_config" "/tmp/${domain}-ssl.conf"
    
    ssh_connect "
        mv /tmp/${domain}-ssl.conf /etc/nginx/sites-available/${domain}-ssl.conf
        ln -sf /etc/nginx/sites-available/${domain}-ssl.conf /etc/nginx/sites-enabled/
        nginx -t && systemctl reload nginx
    "
    
    rm -f "$nginx_config"
    log_success "SSL configured for domain: $domain"
}

# Command line argument handling
case "${1:-}" in
    --setup-domain)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Error: Domain name required${NC}"
            echo "Usage: $0 --setup-domain example.com"
            exit 1
        fi
        setup_domain_ssl "$2"
        ;;
    --fix-tactical-ops|--fix-ssl-issues)
        domain="${2:-tacticalops.console.ts}"
        fix_tactical_ops_ssl "$domain"
        ;;
    --discover-tactical)
        discover_tactical_ops
        ;;
    --test-ssl)
        if [[ -z "${2:-}" ]]; then
            echo -e "${RED}Error: Domain name required${NC}"
            exit 1
        fi
        test_ssl_configuration "$2"
        ;;
    --help|-h)
        echo "SSL Manager - Usage:"
        echo ""
        echo "  --setup-domain DOMAIN       Set up SSL for any domain"
        echo "  --fix-tactical-ops [DOMAIN]  Fix tactical ops SSL (default: tacticalops.console.ts)"
        echo "  --fix-ssl-issues [DOMAIN]    Alias for --fix-tactical-ops"
        echo "  --discover-tactical          Discover tactical ops configuration"
        echo "  --test-ssl DOMAIN           Test SSL configuration for domain"
        echo "  --help, -h                   Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./ssl-manager.sh --fix-tactical-ops"
        echo "  ./ssl-manager.sh --fix-tactical-ops mydomain.com"
        echo "  ./ssl-manager.sh --setup-domain example.com"
        echo "  ./ssl-manager.sh --test-ssl tacticalops.console.ts"
        ;;
    *)
        echo -e "${YELLOW}No option specified. Fixing tactical ops SSL...${NC}"
        echo -e "${YELLOW}Use --help for available options.${NC}"
        echo ""
        fix_tactical_ops_ssl
        ;;
esac