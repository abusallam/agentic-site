#!/bin/bash

# Health Check and Monitoring System
# This script monitors VPS services, containers, and system health
# Usage: ./health-check.sh [--check-all-services|--generate-report|--setup-alerts]

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
mkdir -p "$LOGS_DIR" "$CONFIG_DIR/health-reports"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOGS_DIR/health-check.log"
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

# Check system health
check_system_health() {
    log_info "Checking system health..."
    
    local health_report
    health_report=$(ssh_connect "
        echo '=== SYSTEM HEALTH CHECK ==='
        echo 'Timestamp:' \$(date)
        echo 'Hostname:' \$(hostname)
        echo 'Uptime:' \$(uptime -p)
        echo ''
        
        echo '=== RESOURCE USAGE ==='
        echo 'CPU Usage:'
        top -bn1 | grep 'Cpu(s)' | head -1
        echo 'Memory Usage:'
        free -h
        echo 'Disk Usage:'
        df -h / | tail -1
        echo 'Load Average:' \$(cat /proc/loadavg)
        echo ''
        
        echo '=== SYSTEM SERVICES ==='
        for service in nginx docker ssh fail2ban; do
            if systemctl is-active --quiet \$service 2>/dev/null; then
                echo \"\$service: ✅ ACTIVE\"
            else
                echo \"\$service: ❌ INACTIVE\"
            fi
        done
        echo ''
        
        echo '=== NETWORK STATUS ==='
        echo 'Listening Ports:'
        netstat -tlnp 2>/dev/null | grep LISTEN | head -10 || ss -tlnp | grep LISTEN | head -10
        echo ''
        echo 'Firewall Status:'
        ufw status | head -5
        echo ''
        
        echo '=== SECURITY STATUS ==='
        echo 'Failed Login Attempts (last 10):'
        grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -10 | cut -d' ' -f1-3,9-11 || echo 'No recent failed attempts'
        echo ''
        echo 'Fail2ban Status:'
        fail2ban-client status 2>/dev/null || echo 'Fail2ban not running'
    ")
    
    echo "$health_report"
    echo "$health_report" > "$CONFIG_DIR/health-reports/system-health-$(date +%Y%m%d-%H%M%S).txt"
}

# Check container health
check_container_health() {
    log_info "Checking container health..."
    
    local container_report
    container_report=$(ssh_connect "
        echo '=== CONTAINER HEALTH CHECK ==='
        echo 'Docker Status:' \$(systemctl is-active docker)
        echo 'Docker Version:' \$(docker --version)
        echo ''
        
        echo '=== RUNNING CONTAINERS ==='
        docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo 'No containers running'
        echo ''
        
        echo '=== CONTAINER HEALTH STATUS ==='
        for container in \$(docker ps --format '{{.Names}}' 2>/dev/null); do
            health=\$(docker inspect \$container --format '{{.State.Health.Status}}' 2>/dev/null || echo 'no-health-check')
            if [ \"\$health\" = \"healthy\" ]; then
                echo \"\$container: ✅ HEALTHY\"
            elif [ \"\$health\" = \"unhealthy\" ]; then
                echo \"\$container: ❌ UNHEALTHY\"
            elif [ \"\$health\" = \"starting\" ]; then
                echo \"\$container: 🔄 STARTING\"
            else
                echo \"\$container: ⚠️  NO HEALTH CHECK\"
            fi
        done
        echo ''
        
        echo '=== CONTAINER RESOURCE USAGE ==='
        docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' 2>/dev/null || echo 'Cannot get container stats'
        echo ''
        
        echo '=== DOCKER NETWORKS ==='
        docker network ls 2>/dev/null || echo 'Cannot list networks'
        echo ''
        
        echo '=== DOCKER VOLUMES ==='
        docker volume ls 2>/dev/null | head -10 || echo 'Cannot list volumes'
    ")
    
    echo "$container_report"
    echo "$container_report" > "$CONFIG_DIR/health-reports/container-health-$(date +%Y%m%d-%H%M%S).txt"
}

# Check application health
check_application_health() {
    log_info "Checking application health..."
    
    local app_report
    app_report=$(ssh_connect "
        echo '=== APPLICATION HEALTH CHECK ==='
        echo ''
        
        echo '=== HTTP ENDPOINT TESTS ==='
        # Test common application endpoints
        for port in 3000 3001 8000 8001; do
            if netstat -tln 2>/dev/null | grep -q \":\$port \" || ss -tln 2>/dev/null | grep -q \":\$port \"; then
                echo \"Testing port \$port:\"
                if curl -f -s -m 10 http://localhost:\$port/health 2>/dev/null; then
                    echo \"  ✅ Port \$port health check: PASSED\"
                elif curl -f -s -m 10 http://localhost:\$port/ 2>/dev/null >/dev/null; then
                    echo \"  ✅ Port \$port basic check: PASSED\"
                else
                    echo \"  ❌ Port \$port: NOT RESPONDING\"
                fi
            fi
        done
        echo ''
        
        echo '=== SSL CERTIFICATE STATUS ==='
        for domain in consulting.sa tacticalops.console.ts; do
            echo \"Checking \$domain:\"
            if echo | timeout 10 openssl s_client -servername \$domain -connect \$domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
                echo \"  ✅ SSL certificate valid\"
            else
                echo \"  ❌ SSL certificate issue\"
            fi
        done
        echo ''
        
        echo '=== NGINX STATUS ==='
        if systemctl is-active --quiet nginx; then
            echo 'Nginx: ✅ ACTIVE'
            echo 'Nginx Configuration Test:'
            nginx -t 2>&1 | head -3
            echo 'Active Sites:'
            ls -la /etc/nginx/sites-enabled/ | grep -v '^total' | awk '{print \"  \" \$9 \" -> \" \$11}'
        else
            echo 'Nginx: ❌ INACTIVE'
        fi
    ")
    
    echo "$app_report"
    echo "$app_report" > "$CONFIG_DIR/health-reports/application-health-$(date +%Y%m%d-%H%M%S).txt"
}

# Check security status
check_security_status() {
    log_info "Checking security status..."
    
    local security_report
    security_report=$(ssh_connect "
        echo '=== SECURITY STATUS CHECK ==='
        echo ''
        
        echo '=== FIREWALL STATUS ==='
        ufw status numbered | head -15
        echo ''
        
        echo '=== SSH SECURITY ==='
        echo 'SSH Configuration:'
        grep -E '^(Port|PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)' /etc/ssh/sshd_config 2>/dev/null || echo 'Cannot read SSH config'
        echo ''
        echo 'Active SSH Sessions:'
        who | head -10
        echo ''
        
        echo '=== FAIL2BAN STATUS ==='
        if systemctl is-active --quiet fail2ban; then
            echo 'Fail2ban: ✅ ACTIVE'
            fail2ban-client status 2>/dev/null || echo 'Cannot get fail2ban status'
        else
            echo 'Fail2ban: ❌ INACTIVE'
        fi
        echo ''
        
        echo '=== RECENT SECURITY EVENTS ==='
        echo 'Failed Login Attempts (last 24 hours):'
        grep 'Failed password' /var/log/auth.log 2>/dev/null | grep \"\$(date +%Y-%m-%d)\" | wc -l || echo '0'
        echo ''
        echo 'Successful Logins (last 24 hours):'
        grep 'Accepted password' /var/log/auth.log 2>/dev/null | grep \"\$(date +%Y-%m-%d)\" | wc -l || echo '0'
        echo ''
        
        echo '=== SYSTEM UPDATES ==='
        echo 'Available Updates:'
        apt list --upgradable 2>/dev/null | wc -l || echo 'Cannot check updates'
        echo ''
        echo 'Last Update:'
        stat /var/log/apt/history.log 2>/dev/null | grep Modify || echo 'Cannot determine last update'
    ")
    
    echo "$security_report"
    echo "$security_report" > "$CONFIG_DIR/health-reports/security-status-$(date +%Y%m%d-%H%M%S).txt"
}

# Generate comprehensive health report
generate_comprehensive_report() {
    log_info "Generating comprehensive health report..."
    
    local report_file="$CONFIG_DIR/health-reports/comprehensive-health-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
=== COMPREHENSIVE VPS HEALTH REPORT ===
Generated: $(date)
VPS: $VPS_IP
Report ID: health-$(date +%Y%m%d-%H%M%S)

EOF
    
    # System Health
    echo "=== SYSTEM HEALTH ===" >> "$report_file"
    check_system_health >> "$report_file" 2>/dev/null
    echo "" >> "$report_file"
    
    # Container Health
    echo "=== CONTAINER HEALTH ===" >> "$report_file"
    check_container_health >> "$report_file" 2>/dev/null
    echo "" >> "$report_file"
    
    # Application Health
    echo "=== APPLICATION HEALTH ===" >> "$report_file"
    check_application_health >> "$report_file" 2>/dev/null
    echo "" >> "$report_file"
    
    # Security Status
    echo "=== SECURITY STATUS ===" >> "$report_file"
    check_security_status >> "$report_file" 2>/dev/null
    echo "" >> "$report_file"
    
    # Health Score Calculation
    echo "=== HEALTH SCORE ===" >> "$report_file"
    local health_score=0
    local max_score=100
    
    # Calculate score based on various factors
    if ssh_connect "systemctl is-active --quiet nginx"; then health_score=$((health_score + 15)); fi
    if ssh_connect "systemctl is-active --quiet docker"; then health_score=$((health_score + 15)); fi
    if ssh_connect "systemctl is-active --quiet fail2ban"; then health_score=$((health_score + 10)); fi
    if ssh_connect "ufw status | grep -q 'Status: active'"; then health_score=$((health_score + 10)); fi
    
    # Check resource usage
    local cpu_usage=$(ssh_connect "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1" || echo "0")
    local memory_usage=$(ssh_connect "free | awk '/^Mem:/ {printf \"%.1f\", \$3/\$2 * 100}'" || echo "0")
    local disk_usage=$(ssh_connect "df / | awk 'NR==2 {print \$5}' | cut -d'%' -f1" || echo "0")
    
    if (( $(echo "$cpu_usage < 70" | bc -l) )); then health_score=$((health_score + 15)); fi
    if (( $(echo "$memory_usage < 80" | bc -l) )); then health_score=$((health_score + 15)); fi
    if (( disk_usage < 80 )); then health_score=$((health_score + 10)); fi
    
    # Check container health
    local healthy_containers=$(ssh_connect "docker ps --format '{{.Names}}' 2>/dev/null | wc -l" || echo "0")
    if (( healthy_containers > 0 )); then health_score=$((health_score + 10)); fi
    
    echo "Overall Health Score: $health_score/$max_score" >> "$report_file"
    
    if (( health_score >= 80 )); then
        echo "Status: ✅ EXCELLENT - System is healthy and performing well" >> "$report_file"
    elif (( health_score >= 60 )); then
        echo "Status: ✅ GOOD - System is stable with minor issues" >> "$report_file"
    elif (( health_score >= 40 )); then
        echo "Status: ⚠️  WARNING - System has some issues that need attention" >> "$report_file"
    else
        echo "Status: ❌ CRITICAL - System has serious issues requiring immediate attention" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "=== RECOMMENDATIONS ===" >> "$report_file"
    
    if (( $(echo "$cpu_usage > 70" | bc -l) )); then
        echo "- High CPU usage detected ($cpu_usage%). Consider optimizing applications or upgrading resources." >> "$report_file"
    fi
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        echo "- High memory usage detected ($memory_usage%). Monitor memory leaks and consider adding more RAM." >> "$report_file"
    fi
    
    if (( disk_usage > 80 )); then
        echo "- High disk usage detected ($disk_usage%). Clean up old files and logs, or expand storage." >> "$report_file"
    fi
    
    if ! ssh_connect "systemctl is-active --quiet fail2ban"; then
        echo "- Fail2ban is not active. Enable it for better security protection." >> "$report_file"
    fi
    
    echo "- Regular security updates are recommended." >> "$report_file"
    echo "- Monitor container health and restart unhealthy containers." >> "$report_file"
    echo "- Review and rotate SSL certificates before expiration." >> "$report_file"
    
    cat "$report_file"
    echo ""
    log_success "Comprehensive health report saved to: $report_file"
}

# Setup monitoring alerts
setup_monitoring_alerts() {
    log_info "Setting up monitoring alerts..."
    
    # Create monitoring script on VPS
    ssh_connect "
        echo 'Creating monitoring script on VPS...'
        mkdir -p /opt/monitoring/scripts
        
        cat > /opt/monitoring/scripts/health-monitor.sh << 'MONITOR_EOF'
#!/bin/bash
# VPS Health Monitor - Automated Alerts

WEBHOOK_URL=\"${ALERTS_WEBHOOK_URL:-}\"
EMAIL=\"${ALERTS_EMAIL:-}\"
THRESHOLD_CPU=80
THRESHOLD_MEMORY=85
THRESHOLD_DISK=90

send_alert() {
    local message=\"\$1\"
    local severity=\"\$2\"
    
    echo \"[\$(date)] ALERT [\$severity]: \$message\" >> /var/log/health-monitor.log
    
    if [[ -n \"\$WEBHOOK_URL\" ]]; then
        curl -X POST \"\$WEBHOOK_URL\" -H \"Content-Type: application/json\" -d \"{\\\"text\\\":\\\"VPS Alert [\$severity]: \$message\\\"}\" 2>/dev/null || echo \"Webhook failed\"
    fi
    
    if [[ -n \"\$EMAIL\" ]] && command -v mail >/dev/null 2>&1; then
        echo \"\$message\" | mail -s \"VPS Alert [\$severity]\" \"\$EMAIL\" 2>/dev/null || echo \"Email failed\"
    fi
}

# Check CPU usage
cpu_usage=\$(top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1)
if (( \$(echo \"\$cpu_usage > \$THRESHOLD_CPU\" | bc -l) )); then
    send_alert \"High CPU usage: \${cpu_usage}%\" \"WARNING\"
fi

# Check memory usage
memory_usage=\$(free | awk '/^Mem:/ {printf \"%.1f\", \$3/\$2 * 100}')
if (( \$(echo \"\$memory_usage > \$THRESHOLD_MEMORY\" | bc -l) )); then
    send_alert \"High memory usage: \${memory_usage}%\" \"WARNING\"
fi

# Check disk usage
disk_usage=\$(df / | awk 'NR==2 {print \$5}' | cut -d'%' -f1)
if (( disk_usage > THRESHOLD_DISK )); then
    send_alert \"High disk usage: \${disk_usage}%\" \"WARNING\"
fi

# Check critical services
for service in nginx docker ssh; do
    if ! systemctl is-active --quiet \$service; then
        send_alert \"Service \$service is not running\" \"CRITICAL\"
    fi
done

# Check container health
unhealthy_containers=\$(docker ps --filter health=unhealthy --format '{{.Names}}' 2>/dev/null)
if [[ -n \"\$unhealthy_containers\" ]]; then
    send_alert \"Unhealthy containers detected: \$unhealthy_containers\" \"WARNING\"
fi
MONITOR_EOF

        chmod +x /opt/monitoring/scripts/health-monitor.sh
        
        echo 'Setting up cron job for monitoring...'
        (crontab -l 2>/dev/null; echo '*/5 * * * * /opt/monitoring/scripts/health-monitor.sh') | crontab -
        
        echo 'Testing monitoring script...'
        /opt/monitoring/scripts/health-monitor.sh
        
        echo 'Monitoring alerts setup completed'
    "
    
    log_success "Monitoring alerts configured"
}

# Main health check function
run_comprehensive_health_check() {
    echo -e "${PURPLE}🏥 Health Check and Monitoring System${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo "VPS: $VPS_IP"
    echo "Timestamp: $(date)"
    echo ""
    
    echo -e "${CYAN}🖥️ Checking System Health...${NC}"
    check_system_health
    
    echo ""
    echo -e "${CYAN}🐳 Checking Container Health...${NC}"
    check_container_health
    
    echo ""
    echo -e "${CYAN}🌐 Checking Application Health...${NC}"
    check_application_health
    
    echo ""
    echo -e "${CYAN}🔒 Checking Security Status...${NC}"
    check_security_status
    
    echo ""
    echo -e "${CYAN}📊 Generating Comprehensive Report...${NC}"
    generate_comprehensive_report
    
    echo ""
    echo -e "${GREEN}✅ Health Check Complete!${NC}"
    echo -e "${BLUE}Reports saved to: $CONFIG_DIR/health-reports/${NC}"
    echo -e "${BLUE}Logs available at: $LOGS_DIR/health-check.log${NC}"
}

# Command line argument handling
case "${1:-}" in
    --check-all-services)
        run_comprehensive_health_check
        ;;
    --system-health)
        check_system_health
        ;;
    --container-health)
        check_container_health
        ;;
    --application-health)
        check_application_health
        ;;
    --security-status)
        check_security_status
        ;;
    --generate-report)
        generate_comprehensive_report
        ;;
    --setup-alerts)
        setup_monitoring_alerts
        ;;
    --help|-h)
        echo "Health Check and Monitoring System - Usage:"
        echo ""
        echo "  --check-all-services     Run comprehensive health check"
        echo "  --system-health          Check system resource usage and services"
        echo "  --container-health       Check Docker container status"
        echo "  --application-health     Check application endpoints and SSL"
        echo "  --security-status        Check security configuration and events"
        echo "  --generate-report        Generate comprehensive health report"
        echo "  --setup-alerts           Setup automated monitoring alerts"
        echo "  --help, -h               Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./health-check.sh --check-all-services"
        echo "  ./health-check.sh --container-health"
        echo "  ./health-check.sh --generate-report"
        ;;
    *)
        echo -e "${YELLOW}No option specified. Running comprehensive health check...${NC}"
        echo -e "${YELLOW}Use --help for available options.${NC}"
        echo ""
        run_comprehensive_health_check
        ;;
esac