#!/bin/bash

# Server Analysis Engine - Intelligent Deployment Planning
# This script analyzes VPS discovery data and provides deployment recommendations
# Usage: ./analyze-server.sh [--recommend-deployment|--check-conflicts|--optimize-resources]

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
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/analysis-reports"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/server-analysis.log"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# Get latest discovery report
get_latest_discovery_report() {
    local latest_report
    latest_report=$(find "$CONFIG_DIR/discovery-reports" -name "discovery-report-*.json" -type f 2>/dev/null | sort | tail -1)
    
    if [[ -z "$latest_report" || ! -f "$latest_report" ]]; then
        log_error "No discovery report found. Run vps-discover.sh first."
        return 1
    fi
    
    echo "$latest_report"
}

# Parse JSON report
parse_discovery_data() {
    local report_file="$1"
    
    if ! command -v jq >/dev/null 2>&1; then
        log_error "jq is required for JSON parsing. Please install jq."
        return 1
    fi
    
    # Extract key information from discovery report
    SERVER_IP=$(jq -r '.server_info.ip' "$report_file")
    SERVER_HOSTNAME=$(jq -r '.server_info.hostname' "$report_file")
    SERVER_OS=$(jq -r '.server_info.os' "$report_file")
    CPU_CORES=$(jq -r '.server_info.cpu_cores' "$report_file")
    MEMORY_GB=$(jq -r '.server_info.memory_gb' "$report_file")
    DISK_GB=$(jq -r '.server_info.disk_gb' "$report_file")
    
    DOCKER_INSTALLED=$(jq -r '.docker_info.installed' "$report_file")
    DOCKER_VERSION=$(jq -r '.docker_info.version' "$report_file")
    RUNNING_CONTAINERS=$(jq -r '.docker_info.running_containers' "$report_file")
    
    LISTENING_PORTS=$(jq -r '.network_info.listening_ports[]' "$report_file" 2>/dev/null | tr '\n' ' ')
    FIREWALL_ENABLED=$(jq -r '.network_info.firewall_enabled' "$report_file")
    
    NGINX_INSTALLED=$(jq -r '.services.nginx.installed' "$report_file")
    NGINX_ACTIVE=$(jq -r '.services.nginx.active' "$report_file")
    CADDY_INSTALLED=$(jq -r '.services.caddy.installed' "$report_file")
    CADDY_ACTIVE=$(jq -r '.services.caddy.active' "$report_file")
    
    SSH_PORT=$(jq -r '.security.ssh_port' "$report_file")
    ROOT_LOGIN=$(jq -r '.security.root_login_permitted' "$report_file")
}

# Analyze resource availability
analyze_resources() {
    log_info "Analyzing server resources..."
    
    local analysis_report="$CONFIG_DIR/analysis-reports/resource-analysis-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$analysis_report" << EOF
=== RESOURCE ANALYSIS REPORT ===
Generated: $(date)
Server: $SERVER_HOSTNAME ($SERVER_IP)

=== HARDWARE SPECIFICATIONS ===
CPU Cores: $CPU_CORES
Memory: ${MEMORY_GB}GB
Disk Space: ${DISK_GB}GB
Operating System: $SERVER_OS

=== RESOURCE RECOMMENDATIONS ===
EOF
    
    # CPU Analysis
    echo "" >> "$analysis_report"
    echo "CPU Analysis:" >> "$analysis_report"
    if [[ $CPU_CORES -ge 4 ]]; then
        echo "✅ Excellent CPU capacity ($CPU_CORES cores) - Can handle multiple containers" >> "$analysis_report"
        echo "   Recommended: Up to $((CPU_CORES * 2)) lightweight containers" >> "$analysis_report"
    elif [[ $CPU_CORES -ge 2 ]]; then
        echo "⚠️  Moderate CPU capacity ($CPU_CORES cores) - Suitable for small to medium deployments" >> "$analysis_report"
        echo "   Recommended: Up to $CPU_CORES containers with CPU limits" >> "$analysis_report"
    else
        echo "❌ Limited CPU capacity ($CPU_CORES core) - Minimal deployment recommended" >> "$analysis_report"
        echo "   Recommended: 1-2 lightweight containers maximum" >> "$analysis_report"
    fi
    
    # Memory Analysis
    echo "" >> "$analysis_report"
    echo "Memory Analysis:" >> "$analysis_report"
    if [[ $MEMORY_GB -ge 16 ]]; then
        echo "✅ Excellent memory capacity (${MEMORY_GB}GB) - Can handle resource-intensive applications" >> "$analysis_report"
        echo "   Recommended: Up to $((MEMORY_GB / 2))GB for containers, $((MEMORY_GB / 4))GB reserved for system" >> "$analysis_report"
    elif [[ $MEMORY_GB -ge 8 ]]; then
        echo "✅ Good memory capacity (${MEMORY_GB}GB) - Suitable for most applications" >> "$analysis_report"
        echo "   Recommended: Up to $((MEMORY_GB * 3 / 4))GB for containers, $((MEMORY_GB / 4))GB reserved for system" >> "$analysis_report"
    elif [[ $MEMORY_GB -ge 4 ]]; then
        echo "⚠️  Moderate memory capacity (${MEMORY_GB}GB) - Careful resource management needed" >> "$analysis_report"
        echo "   Recommended: Up to $((MEMORY_GB / 2))GB for containers, monitor memory usage closely" >> "$analysis_report"
    else
        echo "❌ Limited memory capacity (${MEMORY_GB}GB) - Minimal deployment only" >> "$analysis_report"
        echo "   Recommended: Lightweight containers with strict memory limits" >> "$analysis_report"
    fi
    
    # Disk Analysis
    echo "" >> "$analysis_report"
    echo "Disk Analysis:" >> "$analysis_report"
    if [[ $DISK_GB -ge 200 ]]; then
        echo "✅ Excellent disk capacity (${DISK_GB}GB) - Ample space for applications and data" >> "$analysis_report"
        echo "   Recommended: Up to $((DISK_GB * 3 / 4))GB for applications, $((DISK_GB / 4))GB reserved" >> "$analysis_report"
    elif [[ $DISK_GB -ge 100 ]]; then
        echo "✅ Good disk capacity (${DISK_GB}GB) - Sufficient for most deployments" >> "$analysis_report"
        echo "   Recommended: Monitor disk usage, implement log rotation" >> "$analysis_report"
    elif [[ $DISK_GB -ge 50 ]]; then
        echo "⚠️  Moderate disk capacity (${DISK_GB}GB) - Regular cleanup required" >> "$analysis_report"
        echo "   Recommended: Aggressive log rotation, regular cleanup procedures" >> "$analysis_report"
    else
        echo "❌ Limited disk capacity (${DISK_GB}GB) - Minimal deployment only" >> "$analysis_report"
        echo "   Recommended: Lightweight images, external storage for data" >> "$analysis_report"
    fi
    
    cat "$analysis_report"
    echo ""
    log_success "Resource analysis saved to: $analysis_report"
}

# Check for port conflicts
check_port_conflicts() {
    log_info "Checking for port conflicts..."
    
    local conflicts_report="$CONFIG_DIR/analysis-reports/port-conflicts-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$conflicts_report" << EOF
=== PORT CONFLICT ANALYSIS ===
Generated: $(date)
Server: $SERVER_HOSTNAME ($SERVER_IP)

=== CURRENTLY USED PORTS ===
$LISTENING_PORTS

=== CONFLICT ANALYSIS ===
EOF
    
    # Common application ports to check
    local common_ports=(3000 3001 8000 8001 5678 5679 6379 6380 9090 3001 80 443)
    local available_ports=()
    local conflicted_ports=()
    
    for port in "${common_ports[@]}"; do
        if echo "$LISTENING_PORTS" | grep -q "\b$port\b"; then
            conflicted_ports+=("$port")
            echo "❌ Port $port: IN USE" >> "$conflicts_report"
        else
            available_ports+=("$port")
            echo "✅ Port $port: AVAILABLE" >> "$conflicts_report"
        fi
    done
    
    echo "" >> "$conflicts_report"
    echo "=== RECOMMENDATIONS ===" >> "$conflicts_report"
    
    if [[ ${#conflicted_ports[@]} -gt 0 ]]; then
        echo "Conflicted Ports: ${conflicted_ports[*]}" >> "$conflicts_report"
        echo "Available Alternatives: ${available_ports[*]}" >> "$conflicts_report"
        echo "" >> "$conflicts_report"
        echo "Deployment Strategies:" >> "$conflicts_report"
        echo "1. Use available ports from the list above" >> "$conflicts_report"
        echo "2. Stop conflicting services if not needed" >> "$conflicts_report"
        echo "3. Use Docker port mapping to avoid conflicts" >> "$conflicts_report"
        echo "4. Consider using a reverse proxy for multiple services" >> "$conflicts_report"
    else
        echo "✅ No conflicts detected with common application ports" >> "$conflicts_report"
        echo "All standard ports are available for deployment" >> "$conflicts_report"
    fi
    
    # Suggest port ranges for new deployments
    echo "" >> "$conflicts_report"
    echo "=== SUGGESTED PORT ASSIGNMENTS ===" >> "$conflicts_report"
    echo "Frontend Applications: 3000-3010 (Available: $(echo "${available_ports[@]}" | tr ' ' '\n' | grep -E '^30[0-9][0-9]$' | tr '\n' ' '))" >> "$conflicts_report"
    echo "Backend Applications: 8000-8010 (Available: $(echo "${available_ports[@]}" | tr ' ' '\n' | grep -E '^80[0-9][0-9]$' | tr '\n' ' '))" >> "$conflicts_report"
    echo "Database Services: 5432, 3306, 6379-6389" >> "$conflicts_report"
    echo "Monitoring Services: 9090-9100" >> "$conflicts_report"
    
    cat "$conflicts_report"
    echo ""
    log_success "Port conflict analysis saved to: $conflicts_report"
}

# Analyze deployment strategy
recommend_deployment_strategy() {
    log_info "Analyzing optimal deployment strategy..."
    
    local strategy_report="$CONFIG_DIR/analysis-reports/deployment-strategy-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$strategy_report" << EOF
=== DEPLOYMENT STRATEGY RECOMMENDATIONS ===
Generated: $(date)
Server: $SERVER_HOSTNAME ($SERVER_IP)

=== CURRENT INFRASTRUCTURE STATUS ===
Docker Installed: $DOCKER_INSTALLED
Docker Version: $DOCKER_VERSION
Running Containers: $RUNNING_CONTAINERS
Nginx Installed: $NGINX_INSTALLED (Active: $NGINX_ACTIVE)
Caddy Installed: $CADDY_INSTALLED (Active: $CADDY_ACTIVE)
Firewall Enabled: $FIREWALL_ENABLED

=== DEPLOYMENT RECOMMENDATIONS ===
EOF
    
    # Docker strategy
    echo "" >> "$strategy_report"
    echo "Container Orchestration Strategy:" >> "$strategy_report"
    if [[ "$DOCKER_INSTALLED" == "true" ]]; then
        echo "✅ Docker is installed and ready" >> "$strategy_report"
        if [[ $RUNNING_CONTAINERS -gt 0 ]]; then
            echo "   Current containers: $RUNNING_CONTAINERS running" >> "$strategy_report"
            echo "   Recommendation: Use Docker networks for container communication" >> "$strategy_report"
            echo "   Recommendation: Implement container naming conventions" >> "$strategy_report"
        else
            echo "   No running containers - fresh deployment environment" >> "$strategy_report"
            echo "   Recommendation: Start with docker-compose for multi-service applications" >> "$strategy_report"
        fi
    else
        echo "❌ Docker not installed" >> "$strategy_report"
        echo "   Action Required: Install Docker and Docker Compose" >> "$strategy_report"
        echo "   Command: curl -fsSL https://get.docker.com | sh" >> "$strategy_report"
    fi
    
    # Reverse proxy strategy
    echo "" >> "$strategy_report"
    echo "Reverse Proxy Strategy:" >> "$strategy_report"
    if [[ "$NGINX_INSTALLED" == "true" && "$NGINX_ACTIVE" == "true" ]]; then
        echo "✅ Nginx is installed and active" >> "$strategy_report"
        echo "   Recommendation: Use Nginx for SSL termination and load balancing" >> "$strategy_report"
        echo "   Recommendation: Configure virtual hosts for multiple domains" >> "$strategy_report"
    elif [[ "$CADDY_INSTALLED" == "true" && "$CADDY_ACTIVE" == "true" ]]; then
        echo "✅ Caddy is installed and active" >> "$strategy_report"
        echo "   Recommendation: Use Caddy for automatic SSL and reverse proxy" >> "$strategy_report"
        echo "   Recommendation: Configure Caddyfile for multiple services" >> "$strategy_report"
    else
        echo "⚠️  No active reverse proxy detected" >> "$strategy_report"
        echo "   Recommendation: Install and configure Nginx or Caddy" >> "$strategy_report"
        echo "   Nginx: Better for complex configurations and high performance" >> "$strategy_report"
        echo "   Caddy: Better for automatic SSL and simple configurations" >> "$strategy_report"
    fi
    
    # Security strategy
    echo "" >> "$strategy_report"
    echo "Security Strategy:" >> "$strategy_report"
    if [[ "$FIREWALL_ENABLED" == "true" ]]; then
        echo "✅ Firewall is enabled" >> "$strategy_report"
        echo "   Recommendation: Review firewall rules for new services" >> "$strategy_report"
    else
        echo "❌ Firewall not enabled" >> "$strategy_report"
        echo "   Action Required: Enable UFW firewall" >> "$strategy_report"
        echo "   Commands: ufw enable && ufw allow ssh && ufw allow http && ufw allow https" >> "$strategy_report"
    fi
    
    # SSL strategy
    echo "" >> "$strategy_report"
    echo "SSL Certificate Strategy:" >> "$strategy_report"
    if [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]]; then
        echo "✅ Cloudflare integration configured" >> "$strategy_report"
        echo "   Recommendation: Use Cloudflare Origin SSL certificates" >> "$strategy_report"
        echo "   Recommendation: Enable Cloudflare proxy for DDoS protection" >> "$strategy_report"
    else
        echo "⚠️  No Cloudflare integration configured" >> "$strategy_report"
        echo "   Option 1: Configure Cloudflare for managed SSL" >> "$strategy_report"
        echo "   Option 2: Use Let's Encrypt for free SSL certificates" >> "$strategy_report"
    fi
    
    # Monitoring strategy
    echo "" >> "$strategy_report"
    echo "Monitoring Strategy:" >> "$strategy_report"
    echo "   Recommendation: Implement health checks for all services" >> "$strategy_report"
    echo "   Recommendation: Set up log aggregation and rotation" >> "$strategy_report"
    echo "   Recommendation: Configure resource usage alerts" >> "$strategy_report"
    if [[ $MEMORY_GB -ge 8 ]]; then
        echo "   Optional: Deploy Prometheus + Grafana for advanced monitoring" >> "$strategy_report"
    fi
    
    # Backup strategy
    echo "" >> "$strategy_report"
    echo "Backup Strategy:" >> "$strategy_report"
    echo "   Recommendation: Implement automated daily backups" >> "$strategy_report"
    echo "   Recommendation: Store backups in external location" >> "$strategy_report"
    echo "   Recommendation: Test backup restoration procedures" >> "$strategy_report"
    
    cat "$strategy_report"
    echo ""
    log_success "Deployment strategy saved to: $strategy_report"
}

# Optimize resource allocation
optimize_resources() {
    log_info "Optimizing resource allocation recommendations..."
    
    local optimization_report="$CONFIG_DIR/analysis-reports/resource-optimization-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$optimization_report" << EOF
=== RESOURCE OPTIMIZATION RECOMMENDATIONS ===
Generated: $(date)
Server: $SERVER_HOSTNAME ($SERVER_IP)

=== CURRENT RESOURCE ALLOCATION ===
Total CPU Cores: $CPU_CORES
Total Memory: ${MEMORY_GB}GB
Total Disk: ${DISK_GB}GB
Running Containers: $RUNNING_CONTAINERS

=== OPTIMIZATION STRATEGIES ===
EOF
    
    # Calculate optimal resource allocation
    local system_memory_reserve=$((MEMORY_GB / 4))
    local container_memory_limit=$((MEMORY_GB * 3 / 4))
    local cpu_limit_per_container="1.0"
    
    if [[ $CPU_CORES -gt 2 ]]; then
        cpu_limit_per_container="$((CPU_CORES / 2)).0"
    fi
    
    echo "" >> "$optimization_report"
    echo "Memory Optimization:" >> "$optimization_report"
    echo "   System Reserve: ${system_memory_reserve}GB (25% of total)" >> "$optimization_report"
    echo "   Available for Containers: ${container_memory_limit}GB (75% of total)" >> "$optimization_report"
    echo "   Recommended per Container: $((container_memory_limit / 4))GB (for 4 containers)" >> "$optimization_report"
    echo "   Docker Compose Memory Limits:" >> "$optimization_report"
    echo "     mem_limit: ${container_memory_limit}g" >> "$optimization_report"
    echo "     mem_reservation: $((container_memory_limit / 2))g" >> "$optimization_report"
    
    echo "" >> "$optimization_report"
    echo "CPU Optimization:" >> "$optimization_report"
    echo "   Total CPU Cores: $CPU_CORES" >> "$optimization_report"
    echo "   Recommended CPU Limit per Container: $cpu_limit_per_container" >> "$optimization_report"
    echo "   Docker Compose CPU Limits:" >> "$optimization_report"
    echo "     cpus: '$cpu_limit_per_container'" >> "$optimization_report"
    echo "     cpu_shares: 1024" >> "$optimization_report"
    
    echo "" >> "$optimization_report"
    echo "Disk Optimization:" >> "$optimization_report"
    echo "   Total Disk Space: ${DISK_GB}GB" >> "$optimization_report"
    echo "   Recommended for Applications: $((DISK_GB * 60 / 100))GB (60%)" >> "$optimization_report"
    echo "   Reserved for System/Logs: $((DISK_GB * 25 / 100))GB (25%)" >> "$optimization_report"
    echo "   Reserved for Backups: $((DISK_GB * 15 / 100))GB (15%)" >> "$optimization_report"
    
    # Generate Docker Compose resource template
    echo "" >> "$optimization_report"
    echo "=== DOCKER COMPOSE RESOURCE TEMPLATE ===" >> "$optimization_report"
    cat >> "$optimization_report" << EOF

version: '3.8'
services:
  frontend:
    image: your-frontend:latest
    deploy:
      resources:
        limits:
          cpus: '$cpu_limit_per_container'
          memory: ${container_memory_limit}G
        reservations:
          cpus: '0.5'
          memory: $((container_memory_limit / 2))G
    restart: unless-stopped
    
  backend:
    image: your-backend:latest
    deploy:
      resources:
        limits:
          cpus: '$cpu_limit_per_container'
          memory: ${container_memory_limit}G
        reservations:
          cpus: '0.5'
          memory: $((container_memory_limit / 2))G
    restart: unless-stopped

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF
    
    # Performance tuning recommendations
    echo "" >> "$optimization_report"
    echo "=== PERFORMANCE TUNING RECOMMENDATIONS ===" >> "$optimization_report"
    echo "" >> "$optimization_report"
    echo "System-level Optimizations:" >> "$optimization_report"
    echo "   1. Increase file descriptor limits:" >> "$optimization_report"
    echo "      echo '* soft nofile 65536' >> /etc/security/limits.conf" >> "$optimization_report"
    echo "      echo '* hard nofile 65536' >> /etc/security/limits.conf" >> "$optimization_report"
    echo "" >> "$optimization_report"
    echo "   2. Optimize network settings:" >> "$optimization_report"
    echo "      echo 'net.core.somaxconn = 65536' >> /etc/sysctl.conf" >> "$optimization_report"
    echo "      echo 'net.ipv4.tcp_max_syn_backlog = 65536' >> /etc/sysctl.conf" >> "$optimization_report"
    echo "" >> "$optimization_report"
    echo "   3. Configure swap (if memory < 8GB):" >> "$optimization_report"
    if [[ $MEMORY_GB -lt 8 ]]; then
        echo "      fallocate -l 2G /swapfile && chmod 600 /swapfile" >> "$optimization_report"
        echo "      mkswap /swapfile && swapon /swapfile" >> "$optimization_report"
    else
        echo "      Swap not recommended with ${MEMORY_GB}GB RAM" >> "$optimization_report"
    fi
    
    echo "" >> "$optimization_report"
    echo "Docker Optimizations:" >> "$optimization_report"
    echo "   1. Configure Docker daemon:" >> "$optimization_report"
    echo "      Create /etc/docker/daemon.json with log rotation" >> "$optimization_report"
    echo "   2. Use multi-stage builds for smaller images" >> "$optimization_report"
    echo "   3. Implement health checks for all containers" >> "$optimization_report"
    echo "   4. Use Docker networks for service communication" >> "$optimization_report"
    
    cat "$optimization_report"
    echo ""
    log_success "Resource optimization saved to: $optimization_report"
}

# Generate comprehensive analysis report
generate_comprehensive_analysis() {
    log_info "Generating comprehensive server analysis..."
    
    local comprehensive_report="$CONFIG_DIR/analysis-reports/comprehensive-analysis-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$comprehensive_report" << EOF
=== COMPREHENSIVE SERVER ANALYSIS ===
Generated: $(date)
Server: $SERVER_HOSTNAME ($SERVER_IP)

=== EXECUTIVE SUMMARY ===
EOF
    
    # Calculate overall server score
    local score=0
    local max_score=100
    
    # Resource scoring
    if [[ $CPU_CORES -ge 4 ]]; then score=$((score + 20)); elif [[ $CPU_CORES -ge 2 ]]; then score=$((score + 15)); else score=$((score + 5)); fi
    if [[ $MEMORY_GB -ge 16 ]]; then score=$((score + 20)); elif [[ $MEMORY_GB -ge 8 ]]; then score=$((score + 15)); else score=$((score + 5)); fi
    if [[ $DISK_GB -ge 200 ]]; then score=$((score + 15)); elif [[ $DISK_GB -ge 100 ]]; then score=$((score + 10)); else score=$((score + 5)); fi
    
    # Infrastructure scoring
    if [[ "$DOCKER_INSTALLED" == "true" ]]; then score=$((score + 15)); fi
    if [[ "$NGINX_ACTIVE" == "true" || "$CADDY_ACTIVE" == "true" ]]; then score=$((score + 10)); fi
    if [[ "$FIREWALL_ENABLED" == "true" ]]; then score=$((score + 10)); fi
    
    # Security scoring
    if [[ "$SSH_PORT" != "22" ]]; then score=$((score + 5)); fi
    if [[ "$ROOT_LOGIN" == "no" ]]; then score=$((score + 5)); fi
    
    echo "Server Readiness Score: $score/$max_score" >> "$comprehensive_report"
    
    if [[ $score -ge 80 ]]; then
        echo "Status: ✅ EXCELLENT - Ready for production deployments" >> "$comprehensive_report"
    elif [[ $score -ge 60 ]]; then
        echo "Status: ✅ GOOD - Ready for most deployments with minor optimizations" >> "$comprehensive_report"
    elif [[ $score -ge 40 ]]; then
        echo "Status: ⚠️  FAIR - Requires optimization before production deployment" >> "$comprehensive_report"
    else
        echo "Status: ❌ POOR - Significant improvements needed before deployment" >> "$comprehensive_report"
    fi
    
    echo "" >> "$comprehensive_report"
    echo "=== DETAILED ANALYSIS ===" >> "$comprehensive_report"
    
    # Include all analysis sections
    echo "" >> "$comprehensive_report"
    echo "Resource Analysis:" >> "$comprehensive_report"
    analyze_resources >> "$comprehensive_report" 2>/dev/null
    
    echo "" >> "$comprehensive_report"
    echo "Port Conflict Analysis:" >> "$comprehensive_report"
    check_port_conflicts >> "$comprehensive_report" 2>/dev/null
    
    echo "" >> "$comprehensive_report"
    echo "Deployment Strategy:" >> "$comprehensive_report"
    recommend_deployment_strategy >> "$comprehensive_report" 2>/dev/null
    
    echo "" >> "$comprehensive_report"
    echo "Resource Optimization:" >> "$comprehensive_report"
    optimize_resources >> "$comprehensive_report" 2>/dev/null
    
    cat "$comprehensive_report"
    echo ""
    log_success "Comprehensive analysis saved to: $comprehensive_report"
}

# Main analysis function
run_server_analysis() {
    echo -e "${PURPLE}🧠 Server Analysis Engine - Intelligent Deployment Planning${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo "Target VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    # Get latest discovery report
    local discovery_report
    if ! discovery_report=$(get_latest_discovery_report); then
        echo -e "${RED}Please run vps-discover.sh first to generate discovery data.${NC}"
        exit 1
    fi
    
    log_info "Using discovery report: $(basename "$discovery_report")"
    
    # Parse discovery data
    if ! parse_discovery_data "$discovery_report"; then
        log_error "Failed to parse discovery data"
        exit 1
    fi
    
    echo ""
    echo -e "${CYAN}📊 Analyzing Server Resources...${NC}"
    analyze_resources
    
    echo ""
    echo -e "${CYAN}🔍 Checking Port Conflicts...${NC}"
    check_port_conflicts
    
    echo ""
    echo -e "${CYAN}🎯 Recommending Deployment Strategy...${NC}"
    recommend_deployment_strategy
    
    echo ""
    echo -e "${CYAN}⚡ Optimizing Resource Allocation...${NC}"
    optimize_resources
    
    echo ""
    echo -e "${CYAN}📋 Generating Comprehensive Analysis...${NC}"
    generate_comprehensive_analysis
    
    echo ""
    echo -e "${GREEN}✅ Server Analysis Complete!${NC}"
    echo -e "${BLUE}Reports saved to: $CONFIG_DIR/analysis-reports/${NC}"
    echo -e "${BLUE}Logs available at: $LOGS_DIR/server-analysis.log${NC}"
}

# Command line argument handling
case "${1:-}" in
    --recommend-deployment)
        discovery_report=$(get_latest_discovery_report) && parse_discovery_data "$discovery_report" && recommend_deployment_strategy
        ;;
    --check-conflicts)
        discovery_report=$(get_latest_discovery_report) && parse_discovery_data "$discovery_report" && check_port_conflicts
        ;;
    --optimize-resources)
        discovery_report=$(get_latest_discovery_report) && parse_discovery_data "$discovery_report" && optimize_resources
        ;;
    --analyze-resources)
        discovery_report=$(get_latest_discovery_report) && parse_discovery_data "$discovery_report" && analyze_resources
        ;;
    --comprehensive)
        discovery_report=$(get_latest_discovery_report) && parse_discovery_data "$discovery_report" && generate_comprehensive_analysis
        ;;
    --help|-h)
        echo "Server Analysis Engine - Usage:"
        echo ""
        echo "  --recommend-deployment   Generate deployment strategy recommendations"
        echo "  --check-conflicts        Check for port conflicts and suggest alternatives"
        echo "  --optimize-resources     Optimize resource allocation recommendations"
        echo "  --analyze-resources      Analyze server resource capacity"
        echo "  --comprehensive          Generate comprehensive analysis report"
        echo "  --help, -h               Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./analyze-server.sh --recommend-deployment"
        echo "  ./analyze-server.sh --check-conflicts"
        echo "  ./analyze-server.sh --comprehensive"
        echo ""
        echo "Note: Run vps-discover.sh first to generate discovery data."
        ;;
    *)
        echo -e "${YELLOW}No option specified. Running comprehensive analysis...${NC}"
        echo -e "${YELLOW}Use --help for available options.${NC}"
        echo ""
        run_server_analysis
        ;;
esac