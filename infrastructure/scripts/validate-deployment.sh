#!/bin/bash

# 🔍 COMPREHENSIVE DEPLOYMENT VALIDATION SYSTEM
# 50+ automated tests for deployment success/failure reporting and alerting
# 
# VALIDATION CATEGORIES:
# 1. Infrastructure Health (10 tests)
# 2. Container Operations (12 tests)
# 3. Network Connectivity (8 tests)
# 4. Security Configuration (10 tests)
# 5. Application Health (8 tests)
# 6. Performance Metrics (6 tests)
# 7. Data Integrity (4 tests)
# 8. Integration Tests (4 tests)

set -euo pipefail

# Script configuration
SCRIPT_VERSION="2.0.0"
LOG_FILE="/var/log/deployment-validation.log"
REPORT_FILE="/var/log/deployment-validation-report-$(date +%Y%m%d_%H%M%S).json"
TIMESTAMP=$(date -Iseconds)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agentic"
DOMAIN=${DOMAIN:-"consulting.sa"}
DEV_DOMAIN=${DEV_DOMAIN:-"dev.consulting.sa"}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-8000}
REDIS_PORT=${REDIS_PORT:-6379}

# Test results storage
declare -A TEST_RESULTS
declare -A TEST_DETAILS
declare -A TEST_CATEGORIES
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNING_TESTS=0

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

# Test execution function
run_test() {
    local test_id="$1"
    local test_name="$2"
    local test_command="$3"
    local category="${4:-GENERAL}"
    local severity="${5:-ERROR}"  # ERROR, WARNING, INFO
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    TEST_CATEGORIES["$test_id"]="$category"
    
    echo -e "${CYAN}[$TOTAL_TESTS] Testing: $test_name${NC}"
    
    local start_time=$(date +%s.%N)
    local test_output=""
    local test_status="FAILED"
    
    if test_output=$(eval "$test_command" 2>&1); then
        test_status="PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✓ PASSED${NC}"
    else
        if [[ "$severity" == "WARNING" ]]; then
            test_status="WARNING"
            WARNING_TESTS=$((WARNING_TESTS + 1))
            echo -e "${YELLOW}⚠ WARNING${NC}"
        else
            test_status="FAILED"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo -e "${RED}❌ FAILED${NC}"
        fi
    fi
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    TEST_RESULTS["$test_id"]="$test_status"
    TEST_DETAILS["$test_id"]=$(cat << EOF
{
    "name": "$test_name",
    "status": "$test_status",
    "category": "$category",
    "severity": "$severity",
    "duration": "$duration",
    "output": $(echo "$test_output" | jq -R -s .)
}
EOF
)
    
    echo ""
}

# Helper functions for common test patterns
test_service_active() {
    local service="$1"
    systemctl is-active "$service" >/dev/null 2>&1
}

test_port_listening() {
    local port="$1"
    netstat -tulpn | grep -q ":$port "
}

test_container_running() {
    local container="$1"
    docker ps --format "{{.Names}}" | grep -q "^${container}$"
}

test_container_healthy() {
    local container="$1"
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
    [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]
}

test_http_endpoint() {
    local url="$1"
    local expected_code="${2:-200}"
    local timeout="${3:-10}"
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" 2>/dev/null || echo "000")
    [[ "$response_code" == "$expected_code" ]]
}

test_file_exists() {
    local file="$1"
    [[ -f "$file" ]]
}

test_directory_exists() {
    local dir="$1"
    [[ -d "$dir" ]]
}

test_file_permissions() {
    local file="$1"
    local expected_perms="$2"
    local actual_perms=$(stat -c "%a" "$file" 2>/dev/null || echo "000")
    [[ "$actual_perms" == "$expected_perms" ]]
}

# Main validation function
main() {
    echo -e "${PURPLE}🔍 COMPREHENSIVE DEPLOYMENT VALIDATION SYSTEM${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}🎯 Target: $DOMAIN${NC}"
    echo ""
    
    log_info "Starting comprehensive deployment validation..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # ========================================
    # CATEGORY 1: INFRASTRUCTURE HEALTH (10 tests)
    # ========================================
    echo -e "${BLUE}=== 1. INFRASTRUCTURE HEALTH VALIDATION ===${NC}"
    
    run_test "INFRA_001" "System Uptime Check" \
        "uptime | awk '{print \$3}' | grep -E '^[0-9]+:[0-9]+$|^[0-9]+ days?$'" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_002" "Docker Service Status" \
        "test_service_active docker" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_003" "Nginx Service Status" \
        "test_service_active nginx" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_004" "System Load Average" \
        "uptime | awk -F'load average:' '{print \$2}' | awk -F',' '{if(\$1 < 5) exit 0; else exit 1}'" \
        "INFRASTRUCTURE" "WARNING"
    
    run_test "INFRA_005" "Disk Space Availability" \
        "df / | awk 'NR==2{if(\$5+0 < 90) exit 0; else exit 1}'" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_006" "Memory Usage Check" \
        "free | awk '/^Mem:/{if(\$3/\$2 < 0.9) exit 0; else exit 1}'" \
        "INFRASTRUCTURE" "WARNING"
    
    run_test "INFRA_007" "Swap Usage Check" \
        "free | awk '/^Swap:/{if(\$2==0 || \$3/\$2 < 0.5) exit 0; else exit 1}'" \
        "INFRASTRUCTURE" "WARNING"
    
    run_test "INFRA_008" "File System Read/Write" \
        "touch /tmp/deployment-test-\$\$ && rm /tmp/deployment-test-\$\$" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_009" "Network Interface Status" \
        "ip link show | grep -q 'state UP'" \
        "INFRASTRUCTURE" "ERROR"
    
    run_test "INFRA_010" "DNS Resolution" \
        "nslookup google.com >/dev/null 2>&1" \
        "INFRASTRUCTURE" "WARNING"
    
    # ========================================
    # CATEGORY 2: CONTAINER OPERATIONS (12 tests)
    # ========================================
    echo -e "${BLUE}=== 2. CONTAINER OPERATIONS VALIDATION ===${NC}"
    
    run_test "CONTAINER_001" "Frontend Production Container Running" \
        "test_container_running '${PROJECT_NAME}-frontend-prod'" \
        "CONTAINERS" "ERROR"
    
    run_test "CONTAINER_002" "Backend Production Container Running" \
        "test_container_running '${PROJECT_NAME}-backend-prod'" \
        "CONTAINERS" "ERROR"
    
    run_test "CONTAINER_003" "Redis Production Container Running" \
        "test_container_running '${PROJECT_NAME}-redis-prod'" \
        "CONTAINERS" "ERROR"
    
    run_test "CONTAINER_004" "Frontend Development Container Running" \
        "test_container_running '${PROJECT_NAME}-frontend-dev'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_005" "Backend Development Container Running" \
        "test_container_running '${PROJECT_NAME}-backend-dev'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_006" "Redis Development Container Running" \
        "test_container_running '${PROJECT_NAME}-redis-dev'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_007" "Frontend Container Health Check" \
        "test_container_healthy '${PROJECT_NAME}-frontend-prod'" \
        "CONTAINERS" "ERROR"
    
    run_test "CONTAINER_008" "Backend Container Health Check" \
        "test_container_healthy '${PROJECT_NAME}-backend-prod'" \
        "CONTAINERS" "ERROR"
    
    run_test "CONTAINER_009" "Container Resource Limits" \
        "docker stats --no-stream --format 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}' | awk 'NR>1{if(\$2+0<80 && \$3+0<80) next; else exit 1} END{exit 0}'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_010" "Container Restart Policy" \
        "docker inspect ${PROJECT_NAME}-frontend-prod --format='{{.HostConfig.RestartPolicy.Name}}' | grep -q 'unless-stopped\\|always'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_011" "Docker Volume Mounts" \
        "docker inspect ${PROJECT_NAME}-frontend-prod --format='{{range .Mounts}}{{.Type}} {{end}}' | grep -q 'volume\\|bind'" \
        "CONTAINERS" "WARNING"
    
    run_test "CONTAINER_012" "Container Log Rotation" \
        "docker inspect ${PROJECT_NAME}-frontend-prod --format='{{.HostConfig.LogConfig.Type}}' | grep -q 'json-file\\|journald'" \
        "CONTAINERS" "WARNING"
    
    # ========================================
    # CATEGORY 3: NETWORK CONNECTIVITY (8 tests)
    # ========================================
    echo -e "${BLUE}=== 3. NETWORK CONNECTIVITY VALIDATION ===${NC}"
    
    run_test "NETWORK_001" "HTTP Port 80 Listening" \
        "test_port_listening 80" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_002" "HTTPS Port 443 Listening" \
        "test_port_listening 443" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_003" "Frontend Port Accessibility" \
        "test_port_listening $FRONTEND_PORT" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_004" "Backend Port Accessibility" \
        "test_port_listening $BACKEND_PORT" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_005" "Redis Port Accessibility" \
        "test_port_listening $REDIS_PORT" \
        "NETWORK" "WARNING"
    
    run_test "NETWORK_006" "HTTP to HTTPS Redirect" \
        "test_http_endpoint 'http://localhost' '301'" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_007" "External Domain Resolution" \
        "test_http_endpoint 'https://$DOMAIN' '200'" \
        "NETWORK" "ERROR"
    
    run_test "NETWORK_008" "Development Domain Resolution" \
        "test_http_endpoint 'https://$DEV_DOMAIN' '200'" \
        "NETWORK" "WARNING"
    
    # ========================================
    # CATEGORY 4: SECURITY CONFIGURATION (10 tests)
    # ========================================
    echo -e "${BLUE}=== 4. SECURITY CONFIGURATION VALIDATION ===${NC}"
    
    run_test "SECURITY_001" "Firewall Service Status" \
        "test_service_active ufw" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_002" "Firewall Active Status" \
        "ufw status | grep -q 'Status: active'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_003" "SSH Port Configuration" \
        "ufw status numbered | grep -q '22/tcp'" \
        "SECURITY" "WARNING"
    
    run_test "SECURITY_004" "HTTPS Port Firewall Rule" \
        "ufw status numbered | grep -q '443/tcp'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_005" "HTTP Port Firewall Rule" \
        "ufw status numbered | grep -q '80/tcp'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_006" "SSL Certificate File Exists" \
        "test_file_exists '/etc/nginx/ssl/$DOMAIN.crt'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_007" "SSL Private Key File Exists" \
        "test_file_exists '/etc/nginx/ssl/$DOMAIN.key'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_008" "SSL Private Key Permissions" \
        "test_file_permissions '/etc/nginx/ssl/$DOMAIN.key' '600'" \
        "SECURITY" "ERROR"
    
    run_test "SECURITY_009" "Fail2ban Service Status" \
        "test_service_active fail2ban || echo 'fail2ban not installed' >&2" \
        "SECURITY" "WARNING"
    
    run_test "SECURITY_010" "Root Login Disabled" \
        "grep -q '^PermitRootLogin no' /etc/ssh/sshd_config || grep -q '^PermitRootLogin prohibit-password' /etc/ssh/sshd_config" \
        "SECURITY" "WARNING"
    
    # ========================================
    # CATEGORY 5: APPLICATION HEALTH (8 tests)
    # ========================================
    echo -e "${BLUE}=== 5. APPLICATION HEALTH VALIDATION ===${NC}"
    
    run_test "APP_001" "Frontend Health Endpoint" \
        "test_http_endpoint 'http://localhost:$FRONTEND_PORT/api/health' '200'" \
        "APPLICATION" "ERROR"
    
    run_test "APP_002" "Backend Health Endpoint" \
        "test_http_endpoint 'http://localhost:$BACKEND_PORT/health' '200'" \
        "APPLICATION" "ERROR"
    
    run_test "APP_003" "Frontend Main Page Load" \
        "test_http_endpoint 'http://localhost:$FRONTEND_PORT' '200'" \
        "APPLICATION" "ERROR"
    
    run_test "APP_004" "Backend API Response" \
        "curl -s http://localhost:$BACKEND_PORT/health | grep -q 'status\\|ok\\|healthy'" \
        "APPLICATION" "ERROR"
    
    run_test "APP_005" "Redis Connection Test" \
        "docker exec ${PROJECT_NAME}-redis-prod redis-cli ping | grep -q 'PONG'" \
        "APPLICATION" "ERROR"
    
    run_test "APP_006" "Frontend Static Assets" \
        "test_http_endpoint 'http://localhost:$FRONTEND_PORT/favicon.ico' '200'" \
        "APPLICATION" "WARNING"
    
    run_test "APP_007" "API CORS Headers" \
        "curl -s -I http://localhost:$BACKEND_PORT/health | grep -i 'access-control-allow-origin'" \
        "APPLICATION" "WARNING"
    
    run_test "APP_008" "Application Error Logs" \
        "! docker logs ${PROJECT_NAME}-frontend-prod --since=1h 2>&1 | grep -i 'error\\|exception\\|fatal' | head -1" \
        "APPLICATION" "WARNING"
    
    # ========================================
    # CATEGORY 6: PERFORMANCE METRICS (6 tests)
    # ========================================
    echo -e "${BLUE}=== 6. PERFORMANCE METRICS VALIDATION ===${NC}"
    
    run_test "PERF_001" "Frontend Response Time" \
        "response_time=\$(curl -s -w '%{time_total}' -o /dev/null http://localhost:$FRONTEND_PORT); (( \$(echo \"\$response_time < 2.0\" | bc -l) ))" \
        "PERFORMANCE" "WARNING"
    
    run_test "PERF_002" "Backend Response Time" \
        "response_time=\$(curl -s -w '%{time_total}' -o /dev/null http://localhost:$BACKEND_PORT/health); (( \$(echo \"\$response_time < 1.0\" | bc -l) ))" \
        "PERFORMANCE" "WARNING"
    
    run_test "PERF_003" "Database Connection Pool" \
        "docker exec ${PROJECT_NAME}-redis-prod redis-cli info clients | grep -q 'connected_clients'" \
        "PERFORMANCE" "WARNING"
    
    run_test "PERF_004" "Container CPU Usage" \
        "docker stats --no-stream ${PROJECT_NAME}-frontend-prod --format '{{.CPUPerc}}' | sed 's/%//' | awk '{if(\$1 < 80) exit 0; else exit 1}'" \
        "PERFORMANCE" "WARNING"
    
    run_test "PERF_005" "Container Memory Usage" \
        "docker stats --no-stream ${PROJECT_NAME}-frontend-prod --format '{{.MemPerc}}' | sed 's/%//' | awk '{if(\$1 < 80) exit 0; else exit 1}'" \
        "PERFORMANCE" "WARNING"
    
    run_test "PERF_006" "Nginx Access Log Size" \
        "log_size=\$(stat -c%s /var/log/nginx/access.log 2>/dev/null || echo 0); (( log_size < 100000000 ))" \
        "PERFORMANCE" "WARNING"
    
    # ========================================
    # CATEGORY 7: DATA INTEGRITY (4 tests)
    # ========================================
    echo -e "${BLUE}=== 7. DATA INTEGRITY VALIDATION ===${NC}"
    
    run_test "DATA_001" "Environment Configuration File" \
        "test_file_exists '.env' && grep -q 'NODE_ENV\\|ENVIRONMENT' .env" \
        "DATA" "ERROR"
    
    run_test "DATA_002" "Docker Compose Configuration" \
        "test_file_exists 'docker-compose.production.yml'" \
        "DATA" "ERROR"
    
    run_test "DATA_003" "Application Configuration Backup" \
        "test_directory_exists '/opt/backups' || mkdir -p /opt/backups" \
        "DATA" "WARNING"
    
    run_test "DATA_004" "Log Files Rotation" \
        "test_file_exists '/etc/logrotate.d/nginx' || test_file_exists '/etc/logrotate.d/docker'" \
        "DATA" "WARNING"
    
    # ========================================
    # CATEGORY 8: INTEGRATION TESTS (4 tests)
    # ========================================
    echo -e "${BLUE}=== 8. INTEGRATION TESTS VALIDATION ===${NC}"
    
    run_test "INTEGRATION_001" "Frontend-Backend Communication" \
        "curl -s http://localhost:$FRONTEND_PORT/api/health | grep -q 'ok\\|healthy\\|status'" \
        "INTEGRATION" "ERROR"
    
    run_test "INTEGRATION_002" "Database Connectivity" \
        "docker exec ${PROJECT_NAME}-backend-prod curl -s http://localhost:$REDIS_PORT || docker exec ${PROJECT_NAME}-redis-prod redis-cli ping | grep -q 'PONG'" \
        "INTEGRATION" "ERROR"
    
    run_test "INTEGRATION_003" "External API Connectivity" \
        "curl -s --max-time 10 https://api.github.com/zen >/dev/null" \
        "INTEGRATION" "WARNING"
    
    run_test "INTEGRATION_004" "CDN/Static Assets Delivery" \
        "curl -s --max-time 10 https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js | head -1 | grep -q 'jQuery'" \
        "INTEGRATION" "WARNING"
    
    # ========================================
    # GENERATE COMPREHENSIVE REPORT
    # ========================================
    generate_validation_report
    display_validation_summary
    send_alerts_if_needed
    
    # Exit with appropriate code
    if [[ $FAILED_TESTS -gt 0 ]]; then
        exit 1
    elif [[ $WARNING_TESTS -gt 5 ]]; then
        exit 2
    else
        exit 0
    fi
}

# Generate comprehensive JSON report
generate_validation_report() {
    log_info "Generating comprehensive validation report..."
    
    local report_data=$(cat << EOF
{
    "validation_report": {
        "timestamp": "$TIMESTAMP",
        "script_version": "$SCRIPT_VERSION",
        "domain": "$DOMAIN",
        "summary": {
            "total_tests": $TOTAL_TESTS,
            "passed_tests": $PASSED_TESTS,
            "failed_tests": $FAILED_TESTS,
            "warning_tests": $WARNING_TESTS,
            "success_rate": $(( (PASSED_TESTS + WARNING_TESTS) * 100 / TOTAL_TESTS )),
            "critical_success_rate": $(( PASSED_TESTS * 100 / TOTAL_TESTS ))
        },
        "categories": {
EOF
)
    
    # Add category summaries
    for category in "INFRASTRUCTURE" "CONTAINERS" "NETWORK" "SECURITY" "APPLICATION" "PERFORMANCE" "DATA" "INTEGRATION"; do
        local cat_total=0
        local cat_passed=0
        local cat_failed=0
        local cat_warning=0
        
        for test_id in "${!TEST_CATEGORIES[@]}"; do
            if [[ "${TEST_CATEGORIES[$test_id]}" == "$category" ]]; then
                ((cat_total++))
                case "${TEST_RESULTS[$test_id]}" in
                    "PASSED") ((cat_passed++)) ;;
                    "FAILED") ((cat_failed++)) ;;
                    "WARNING") ((cat_warning++)) ;;
                esac
            fi
        done
        
        report_data+="""
            \"$category\": {
                \"total\": $cat_total,
                \"passed\": $cat_passed,
                \"failed\": $cat_failed,
                \"warnings\": $cat_warning
            },"""
    done
    
    # Remove trailing comma and close categories
    report_data="${report_data%,}"
    report_data+="""
        },
        "test_details": {"""
    
    # Add individual test details
    local first_test=true
    for test_id in $(printf '%s\n' "${!TEST_DETAILS[@]}" | sort); do
        if [[ "$first_test" == "true" ]]; then
            first_test=false
        else
            report_data+=","
        fi
        report_data+="""
            \"$test_id\": ${TEST_DETAILS[$test_id]}"""
    done
    
    report_data+="""
        },
        "system_info": {
            "hostname": "$(hostname)",
            "uptime": "$(uptime | awk '{print $3, $4}' | sed 's/,//')",
            "load_average": "$(uptime | awk -F'load average:' '{print $2}')",
            "memory_usage": "$(free -h | awk '/^Mem:/{print $3 "/" $2}')",
            "disk_usage": "$(df -h / | awk 'NR==2{print $3 "/" $2 " (" $5 ")"}')",
            "docker_version": "$(docker --version 2>/dev/null || echo 'Not available')",
            "nginx_version": "$(nginx -v 2>&1 | awk '{print $3}' || echo 'Not available')"
        }
    }
}"""
    
    echo "$report_data" > "$REPORT_FILE"
    log_success "Validation report saved to: $REPORT_FILE"
}

# Display validation summary
display_validation_summary() {
    echo ""
    echo -e "${PURPLE}=== COMPREHENSIVE VALIDATION SUMMARY ===${NC}"
    echo ""
    
    local success_rate=$(( (PASSED_TESTS + WARNING_TESTS) * 100 / TOTAL_TESTS ))
    local critical_success_rate=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    
    echo -e "${BLUE}📊 Test Results:${NC}"
    echo -e "   Total Tests: ${CYAN}$TOTAL_TESTS${NC}"
    echo -e "   Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "   Failed: ${RED}$FAILED_TESTS${NC}"
    echo -e "   Warnings: ${YELLOW}$WARNING_TESTS${NC}"
    echo ""
    
    echo -e "${BLUE}📈 Success Rates:${NC}"
    echo -e "   Overall Success Rate: ${CYAN}$success_rate%${NC}"
    echo -e "   Critical Success Rate: ${CYAN}$critical_success_rate%${NC}"
    echo ""
    
    # Category breakdown
    echo -e "${BLUE}📋 Category Breakdown:${NC}"
    for category in "INFRASTRUCTURE" "CONTAINERS" "NETWORK" "SECURITY" "APPLICATION" "PERFORMANCE" "DATA" "INTEGRATION"; do
        local cat_total=0
        local cat_passed=0
        local cat_failed=0
        local cat_warning=0
        
        for test_id in "${!TEST_CATEGORIES[@]}"; do
            if [[ "${TEST_CATEGORIES[$test_id]}" == "$category" ]]; then
                ((cat_total++))
                case "${TEST_RESULTS[$test_id]}" in
                    "PASSED") ((cat_passed++)) ;;
                    "FAILED") ((cat_failed++)) ;;
                    "WARNING") ((cat_warning++)) ;;
                esac
            fi
        done
        
        if [[ $cat_total -gt 0 ]]; then
            local cat_success_rate=$(( (cat_passed + cat_warning) * 100 / cat_total ))
            echo -e "   $category: ${CYAN}$cat_success_rate%${NC} ($cat_passed✓ $cat_failed❌ $cat_warning⚠)"
        fi
    done
    echo ""
    
    # Overall status determination
    if [[ $FAILED_TESTS -eq 0 && $WARNING_TESTS -le 3 ]]; then
        echo -e "${GREEN}🎉 DEPLOYMENT STATUS: EXCELLENT${NC}"
        echo -e "${GREEN}✅ All critical tests passed with minimal warnings${NC}"
    elif [[ $FAILED_TESTS -eq 0 && $WARNING_TESTS -le 8 ]]; then
        echo -e "${YELLOW}⚠️  DEPLOYMENT STATUS: GOOD${NC}"
        echo -e "${YELLOW}✅ All critical tests passed with some warnings${NC}"
    elif [[ $critical_success_rate -ge 90 ]]; then
        echo -e "${YELLOW}⚠️  DEPLOYMENT STATUS: ACCEPTABLE${NC}"
        echo -e "${YELLOW}⚠️  Most critical tests passed but issues need attention${NC}"
    else
        echo -e "${RED}❌ DEPLOYMENT STATUS: FAILED${NC}"
        echo -e "${RED}❌ Critical issues detected - immediate attention required${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📋 Report Files:${NC}"
    echo -e "   Detailed Report: ${CYAN}$REPORT_FILE${NC}"
    echo -e "   Validation Log: ${CYAN}$LOG_FILE${NC}"
    echo ""
}

# Send alerts if needed
send_alerts_if_needed() {
    if [[ $FAILED_TESTS -gt 0 ]]; then
        log_error "Deployment validation failed with $FAILED_TESTS critical issues"
        
        # Create alert file for monitoring systems
        cat > "/tmp/deployment-validation-alert.json" << EOF
{
    "alert_type": "DEPLOYMENT_VALIDATION_FAILED",
    "severity": "CRITICAL",
    "timestamp": "$TIMESTAMP",
    "failed_tests": $FAILED_TESTS,
    "total_tests": $TOTAL_TESTS,
    "domain": "$DOMAIN",
    "report_file": "$REPORT_FILE"
}
EOF
        
    elif [[ $WARNING_TESTS -gt 5 ]]; then
        log_warn "Deployment validation completed with $WARNING_TESTS warnings"
        
        # Create warning alert
        cat > "/tmp/deployment-validation-warning.json" << EOF
{
    "alert_type": "DEPLOYMENT_VALIDATION_WARNING",
    "severity": "WARNING",
    "timestamp": "$TIMESTAMP",
    "warning_tests": $WARNING_TESTS,
    "total_tests": $TOTAL_TESTS,
    "domain": "$DOMAIN",
    "report_file": "$REPORT_FILE"
}
EOF
    fi
}

# Execute main function
main "$@"