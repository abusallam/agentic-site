#!/bin/bash

# VPS Discovery Agent - Intelligent Server State Analysis
# This script discovers and analyzes VPS server state before deployment
# Usage: ./vps-discover.sh [--analyze-all|--check-ports|--list-containers|--security-audit]

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
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/discovery-reports"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/vps-discovery.log"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# SSH connection function with retry logic
ssh_connect() {
    local command="$1"
    local max_attempts="${MAX_RETRY_ATTEMPTS:-3}"
    local timeout="${CONNECTION_TIMEOUT:-30}"
    local retry_delay="${RETRY_DELAY:-5}"
    
    for attempt in $(seq 1 $max_attempts); do
        if [[ -n "${SSH_KEY_PATH:-}" && -f "$SSH_KEY_PATH" ]]; then
            # Try SSH key authentication first
            if timeout "$timeout" ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout="$timeout" "$VPS_USERNAME@$VPS_IP" "$command" 2>/dev/null; then
                return 0
            fi
        fi
        
        # Fallback to password authentication
        if command -v sshpass >/dev/null 2>&1; then
            if timeout "$timeout" sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout="$timeout" "$VPS_USERNAME@$VPS_IP" "$command" 2>/dev/null; then
                return 0
            fi
        fi
        
        if [[ $attempt -lt $max_attempts ]]; then
            log_warn "Connection attempt $attempt failed, retrying in ${retry_delay}s..."
            sleep "$retry_delay"
        fi
    done
    
    log_error "Failed to connect to VPS after $max_attempts attempts"
    return 1
}

# Test VPS connection
test_connection() {
    log_info "Testing VPS connection to $VPS_IP..."
    
    if ssh_connect "echo 'Connection successful'"; then
        log_success "VPS connection established successfully"
        return 0
    else
        log_error "Failed to establish VPS connection"
        return 1
    fi
}

# Discover system information
discover_system_info() {
    log_info "Discovering system information..."
    
    local system_info
    system_info=$(ssh_connect "
        echo '=== SYSTEM INFO ==='
        echo 'Hostname:' \$(hostname)
        echo 'OS:' \$(cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2)
        echo 'Kernel:' \$(uname -r)
        echo 'Architecture:' \$(uname -m)
        echo 'CPU Cores:' \$(nproc)
        echo 'Memory:' \$(free -h | awk '/^Mem:/{print \$2}')
        echo 'Disk:' \$(df -h / | awk 'NR==2{print \$2}')
        echo 'Load Average:' \$(cat /proc/loadavg)
        echo 'Uptime:' \$(uptime -p)
    ")
    
    echo "$system_info"
    echo "$system_info" > "$CONFIG_DIR/discovery-reports/system-info-$(date +%Y%m%d-%H%M%S).txt"
}

# Discover running containers
discover_containers() {
    log_info "Discovering running containers..."
    
    local containers_info
    containers_info=$(ssh_connect "
        echo '=== DOCKER CONTAINERS ==='
        if command -v docker >/dev/null 2>&1; then
            echo 'Docker Version:' \$(docker --version)
            echo 'Docker Compose Version:' \$(docker-compose --version 2>/dev/null || echo 'Not installed')
            echo ''
            echo 'Running Containers:'
            docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' 2>/dev/null || echo 'No containers running'
            echo ''
            echo 'All Containers:'
            docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}' 2>/dev/null || echo 'No containers found'
            echo ''
            echo 'Docker Networks:'
            docker network ls 2>/dev/null || echo 'No networks found'
            echo ''
            echo 'Docker Volumes:'
            docker volume ls 2>/dev/null || echo 'No volumes found'
        else
            echo 'Docker not installed'
        fi
    ")
    
    echo "$containers_info"
    echo "$containers_info" > "$CONFIG_DIR/discovery-reports/containers-info-$(date +%Y%m%d-%H%M%S).txt"
}

# Discover network and port usage
discover_network() {
    log_info "Discovering network configuration and port usage..."
    
    local network_info
    network_info=$(ssh_connect "
        echo '=== NETWORK CONFIGURATION ==='
        echo 'Network Interfaces:'
        ip addr show | grep -E '^[0-9]+:|inet ' | head -20
        echo ''
        echo 'Listening Ports:'
        netstat -tlnp 2>/dev/null | head -30 || ss -tlnp | head -30
        echo ''
        echo 'Active Connections:'
        netstat -tn 2>/dev/null | head -20 || ss -tn | head -20
        echo ''
        echo 'Firewall Status:'
        if command -v ufw >/dev/null 2>&1; then
            ufw status numbered 2>/dev/null || echo 'UFW not configured'
        else
            echo 'UFW not installed'
        fi
        echo ''
        echo 'Iptables Rules:'
        iptables -L -n | head -20 2>/dev/null || echo 'Cannot access iptables'
    ")
    
    echo "$network_info"
    echo "$network_info" > "$CONFIG_DIR/discovery-reports/network-info-$(date +%Y%m%d-%H%M%S).txt"
}

# Discover services and processes
discover_services() {
    log_info "Discovering system services and processes..."
    
    local services_info
    services_info=$(ssh_connect "
        echo '=== SYSTEM SERVICES ==='
        echo 'Systemd Services (Active):'
        systemctl list-units --type=service --state=active | head -20
        echo ''
        echo 'Key Service Status:'
        for service in nginx apache2 caddy docker ssh fail2ban ufw; do
            if systemctl is-active --quiet \$service 2>/dev/null; then
                echo \"\$service: \$(systemctl is-active \$service)\"
            fi
        done
        echo ''
        echo 'Top Processes by CPU:'
        ps aux --sort=-%cpu | head -10
        echo ''
        echo 'Top Processes by Memory:'
        ps aux --sort=-%mem | head -10
    ")
    
    echo "$services_info"
    echo "$services_info" > "$CONFIG_DIR/discovery-reports/services-info-$(date +%Y%m%d-%H%M%S).txt"
}

# Discover SSL certificates and web server configuration
discover_ssl_web() {
    log_info "Discovering SSL certificates and web server configuration..."
    
    local ssl_web_info
    ssl_web_info=$(ssh_connect "
        echo '=== SSL AND WEB SERVER CONFIGURATION ==='
        echo 'Nginx Configuration:'
        if command -v nginx >/dev/null 2>&1; then
            echo 'Nginx Version:' \$(nginx -v 2>&1)
            echo 'Nginx Status:' \$(systemctl is-active nginx 2>/dev/null || echo 'Not running')
            echo 'Nginx Sites Enabled:'
            ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo 'No sites enabled'
            echo 'SSL Certificates:'
            find /etc/nginx/ssl /etc/ssl /opt/ssl -name '*.crt' -o -name '*.pem' 2>/dev/null | head -10 || echo 'No SSL certificates found'
        else
            echo 'Nginx not installed'
        fi
        echo ''
        echo 'Caddy Configuration:'
        if command -v caddy >/dev/null 2>&1; then
            echo 'Caddy Version:' \$(caddy version 2>/dev/null)
            echo 'Caddy Status:' \$(systemctl is-active caddy 2>/dev/null || echo 'Not running')
        else
            echo 'Caddy not installed'
        fi
        echo ''
        echo 'Certificate Expiration Check:'
        for domain in consulting.sa tacticalops.console.ts; do
            echo \"Checking \$domain:\"
            echo | timeout 10 openssl s_client -servername \$domain -connect \$domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo \"Cannot check \$domain\"
        done
    ")
    
    echo "$ssl_web_info"
    echo "$ssl_web_info" > "$CONFIG_DIR/discovery-reports/ssl-web-info-$(date +%Y%m%d-%H%M%S).txt"
}

# Security audit
security_audit() {
    log_info "Performing security audit..."
    
    local security_info
    security_info=$(ssh_connect "
        echo '=== SECURITY AUDIT ==='
        echo 'SSH Configuration:'
        grep -E '^(Port|PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)' /etc/ssh/sshd_config 2>/dev/null || echo 'Cannot read SSH config'
        echo ''
        echo 'Failed Login Attempts (last 100):'
        grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -10 || echo 'No failed login attempts found'
        echo ''
        echo 'Fail2ban Status:'
        if command -v fail2ban-client >/dev/null 2>&1; then
            fail2ban-client status 2>/dev/null || echo 'Fail2ban not running'
        else
            echo 'Fail2ban not installed'
        fi
        echo ''
        echo 'Open Ports Summary:'
        netstat -tlnp 2>/dev/null | awk '/LISTEN/ {print \$4}' | cut -d: -f2 | sort -n | uniq || ss -tlnp | awk '/LISTEN/ {print \$4}' | cut -d: -f2 | sort -n | uniq
        echo ''
        echo 'System Updates Available:'
        apt list --upgradable 2>/dev/null | wc -l || echo 'Cannot check updates'
    ")
    
    echo "$security_info"
    echo "$security_info" > "$CONFIG_DIR/discovery-reports/security-audit-$(date +%Y%m%d-%H%M%S).txt"
}

# Generate JSON report
generate_json_report() {
    log_info "Generating JSON discovery report..."
    
    local json_report
    json_report=$(ssh_connect "
        cat << 'EOF'
{
  \"discovery_timestamp\": \"\$(date -Iseconds)\",
  \"server_info\": {
    \"ip\": \"$VPS_IP\",
    \"hostname\": \"\$(hostname)\",
    \"os\": \"\$(cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2)\",
    \"kernel\": \"\$(uname -r)\",
    \"architecture\": \"\$(uname -m)\",
    \"cpu_cores\": \$(nproc),
    \"memory_gb\": \$(free -g | awk '/^Mem:/{print \$2}'),
    \"disk_gb\": \$(df -BG / | awk 'NR==2{gsub(/G/,\"\",\$2); print \$2}'),
    \"uptime_seconds\": \$(cat /proc/uptime | cut -d' ' -f1 | cut -d'.' -f1)
  },
  \"docker_info\": {
    \"installed\": \$(command -v docker >/dev/null 2>&1 && echo true || echo false),
    \"version\": \"\$(docker --version 2>/dev/null | cut -d' ' -f3 | cut -d',' -f1 || echo 'N/A')\",
    \"compose_installed\": \$(command -v docker-compose >/dev/null 2>&1 && echo true || echo false),
    \"running_containers\": \$(docker ps -q 2>/dev/null | wc -l || echo 0),
    \"total_containers\": \$(docker ps -aq 2>/dev/null | wc -l || echo 0)
  },
  \"network_info\": {
    \"listening_ports\": [\$(netstat -tln 2>/dev/null | awk '/LISTEN/ {print \$4}' | cut -d: -f2 | sort -n | uniq | tr '\n' ',' | sed 's/,\$//' || echo '')],
    \"firewall_enabled\": \$(ufw status 2>/dev/null | grep -q 'Status: active' && echo true || echo false)
  },
  \"services\": {
    \"nginx\": {
      \"installed\": \$(command -v nginx >/dev/null 2>&1 && echo true || echo false),
      \"active\": \$(systemctl is-active nginx 2>/dev/null | grep -q 'active' && echo true || echo false)
    },
    \"caddy\": {
      \"installed\": \$(command -v caddy >/dev/null 2>&1 && echo true || echo false),
      \"active\": \$(systemctl is-active caddy 2>/dev/null | grep -q 'active' && echo true || echo false)
    },
    \"fail2ban\": {
      \"installed\": \$(command -v fail2ban-client >/dev/null 2>&1 && echo true || echo false),
      \"active\": \$(systemctl is-active fail2ban 2>/dev/null | grep -q 'active' && echo true || echo false)
    }
  },
  \"security\": {
    \"ssh_port\": \$(grep '^Port' /etc/ssh/sshd_config 2>/dev/null | awk '{print \$2}' || echo 22),
    \"root_login_permitted\": \$(grep '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | awk '{print \$2}' || echo 'unknown'),
    \"password_auth_enabled\": \$(grep '^PasswordAuthentication' /etc/ssh/sshd_config 2>/dev/null | awk '{print \$2}' || echo 'unknown')
  }
}
EOF
    ")
    
    echo "$json_report" | jq . 2>/dev/null || echo "$json_report"
    echo "$json_report" > "$CONFIG_DIR/discovery-reports/discovery-report-$(date +%Y%m%d-%H%M%S).json"
}

# Find available ports
find_available_ports() {
    log_info "Finding available ports for deployment..."
    
    local available_ports
    available_ports=$(ssh_connect "
        echo 'Checking port availability...'
        used_ports=\$(netstat -tln 2>/dev/null | awk '/LISTEN/ {print \$4}' | cut -d: -f2 | sort -n || ss -tln | awk '/LISTEN/ {print \$4}' | cut -d: -f2 | sort -n)
        
        echo 'Used ports:'
        echo \"\$used_ports\" | tr '\n' ' '
        echo ''
        
        echo 'Available ports in common ranges:'
        for port in {3000..3010} {8000..8010} {5678..5688} {6379..6389} {9090..9100}; do
            if ! echo \"\$used_ports\" | grep -q \"^\$port\$\"; then
                echo \$port
            fi
        done | head -20
    ")
    
    echo "$available_ports"
}

# Analyze deployment recommendations
analyze_deployment_recommendations() {
    log_info "Analyzing deployment recommendations..."
    
    local recommendations
    recommendations=$(ssh_connect "
        echo '=== DEPLOYMENT RECOMMENDATIONS ==='
        
        # Check resource usage
        cpu_usage=\$(top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1)
        memory_usage=\$(free | awk '/^Mem:/ {printf \"%.1f\", \$3/\$2 * 100}')
        disk_usage=\$(df / | awk 'NR==2 {print \$5}' | cut -d'%' -f1)
        
        echo \"Current Resource Usage:\"
        echo \"- CPU: \${cpu_usage}%\"
        echo \"- Memory: \${memory_usage}%\"
        echo \"- Disk: \${disk_usage}%\"
        echo ''
        
        # Resource recommendations
        echo 'Resource Recommendations:'
        if (( \$(echo \"\$cpu_usage > 70\" | bc -l) )); then
            echo '- WARNING: High CPU usage detected. Consider optimizing existing services.'
        else
            echo '- CPU usage is acceptable for new deployments.'
        fi
        
        if (( \$(echo \"\$memory_usage > 80\" | bc -l) )); then
            echo '- WARNING: High memory usage detected. Monitor memory allocation for new containers.'
        else
            echo '- Memory usage is acceptable for new deployments.'
        fi
        
        if (( disk_usage > 85 )); then
            echo '- WARNING: High disk usage detected. Consider cleanup or disk expansion.'
        else
            echo '- Disk usage is acceptable for new deployments.'
        fi
        
        echo ''
        echo 'Container Deployment Recommendations:'
        
        # Check for existing containers
        container_count=\$(docker ps -q 2>/dev/null | wc -l || echo 0)
        if (( container_count > 0 )); then
            echo \"- Found \$container_count running containers\"
            echo '- Use port mapping to avoid conflicts'
            echo '- Consider using Docker networks for container communication'
        else
            echo '- No running containers detected'
            echo '- Fresh deployment environment available'
        fi
        
        # SSL recommendations
        echo ''
        echo 'SSL Configuration Recommendations:'
        if systemctl is-active nginx >/dev/null 2>&1; then
            echo '- Nginx is running and can be used for SSL termination'
            if [[ -d /etc/nginx/ssl ]] && [[ \$(ls /etc/nginx/ssl/*.crt 2>/dev/null | wc -l) -gt 0 ]]; then
                echo '- Existing SSL certificates found'
            else
                echo '- No SSL certificates found. Configure SSL for new domains.'
            fi
        elif systemctl is-active caddy >/dev/null 2>&1; then
            echo '- Caddy is running and can handle automatic SSL'
        else
            echo '- No reverse proxy detected. Install and configure Nginx or Caddy.'
        fi
        
        # Security recommendations
        echo ''
        echo 'Security Recommendations:'
        if systemctl is-active fail2ban >/dev/null 2>&1; then
            echo '- Fail2ban is active and protecting against intrusions'
        else
            echo '- Install and configure fail2ban for security'
        fi
        
        if ufw status 2>/dev/null | grep -q 'Status: active'; then
            echo '- UFW firewall is active'
        else
            echo '- Enable UFW firewall for network security'
        fi
    ")
    
    echo "$recommendations"
    echo "$recommendations" > "$CONFIG_DIR/discovery-reports/recommendations-$(date +%Y%m%d-%H%M%S).txt"
}

# Main discovery function
run_full_discovery() {
    echo -e "${PURPLE}🔍 VPS Discovery Agent - Full Analysis${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo "Target VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    # Test connection first
    if ! test_connection; then
        exit 1
    fi
    
    echo ""
    echo -e "${CYAN}📊 Discovering System Information...${NC}"
    discover_system_info
    
    echo ""
    echo -e "${CYAN}🐳 Discovering Docker Containers...${NC}"
    discover_containers
    
    echo ""
    echo -e "${CYAN}🌐 Discovering Network Configuration...${NC}"
    discover_network
    
    echo ""
    echo -e "${CYAN}⚙️ Discovering System Services...${NC}"
    discover_services
    
    echo ""
    echo -e "${CYAN}🔒 Discovering SSL and Web Configuration...${NC}"
    discover_ssl_web
    
    echo ""
    echo -e "${CYAN}🛡️ Performing Security Audit...${NC}"
    security_audit
    
    echo ""
    echo -e "${CYAN}🔍 Finding Available Ports...${NC}"
    find_available_ports
    
    echo ""
    echo -e "${CYAN}💡 Analyzing Deployment Recommendations...${NC}"
    analyze_deployment_recommendations
    
    echo ""
    echo -e "${CYAN}📋 Generating JSON Report...${NC}"
    generate_json_report
    
    echo ""
    echo -e "${GREEN}✅ VPS Discovery Complete!${NC}"
    echo -e "${BLUE}Reports saved to: $CONFIG_DIR/discovery-reports/${NC}"
    echo -e "${BLUE}Logs available at: $LOGS_DIR/vps-discovery.log${NC}"
}

# Command line argument handling
case "${1:-}" in
    --analyze-all)
        run_full_discovery
        ;;
    --check-ports)
        test_connection && find_available_ports
        ;;
    --list-containers)
        test_connection && discover_containers
        ;;
    --security-audit)
        test_connection && security_audit
        ;;
    --system-info)
        test_connection && discover_system_info
        ;;
    --network-info)
        test_connection && discover_network
        ;;
    --ssl-info)
        test_connection && discover_ssl_web
        ;;
    --recommendations)
        test_connection && analyze_deployment_recommendations
        ;;
    --json-report)
        test_connection && generate_json_report
        ;;
    --test-connection)
        test_connection
        ;;
    --help|-h)
        echo "VPS Discovery Agent - Usage:"
        echo ""
        echo "  --analyze-all        Run complete VPS analysis"
        echo "  --check-ports        Check available ports"
        echo "  --list-containers    List Docker containers"
        echo "  --security-audit     Perform security audit"
        echo "  --system-info        Get system information"
        echo "  --network-info       Get network configuration"
        echo "  --ssl-info           Get SSL and web server info"
        echo "  --recommendations    Get deployment recommendations"
        echo "  --json-report        Generate JSON report"
        echo "  --test-connection    Test VPS connection"
        echo "  --help, -h           Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./vps-discover.sh --analyze-all"
        echo "  ./vps-discover.sh --check-ports"
        echo "  ./vps-discover.sh --security-audit"
        ;;
    *)
        echo -e "${YELLOW}No option specified. Running full discovery...${NC}"
        echo -e "${YELLOW}Use --help for available options.${NC}"
        echo ""
        run_full_discovery
        ;;
esac