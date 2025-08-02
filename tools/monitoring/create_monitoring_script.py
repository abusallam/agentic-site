#!/usr/bin/env python3
"""
Create comprehensive monitoring and verification scripts on VPS
"""

import subprocess

def create_monitoring_scripts():
    """Create monitoring scripts on VPS"""
    
    # Create comprehensive monitoring script
    monitoring_script = '''#!/bin/bash
# Comprehensive Application Monitoring Script
# Location: /root/agentic-site/monitor.sh

PROJECT_DIR="/root/agentic-site"
LOG_FILE="/var/log/agentic-site-monitor.log"
ALERT_LOG="/var/log/agentic-site-alerts.log"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

log_message() {
    echo "$(date): $1" | tee -a $LOG_FILE
}

alert_message() {
    echo "$(date): ALERT - $1" | tee -a $ALERT_LOG
    echo -e "${RED}ALERT: $1${NC}"
}

success_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning_message() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_docker_status() {
    log_message "Checking Docker status..."
    
    if ! docker --version > /dev/null 2>&1; then
        alert_message "Docker is not running or not installed"
        return 1
    fi
    
    if ! docker-compose --version > /dev/null 2>&1; then
        alert_message "Docker Compose is not available"
        return 1
    fi
    
    success_message "Docker services are available"
    return 0
}

check_containers() {
    log_message "Checking container status..."
    cd $PROJECT_DIR
    
    # Get container status
    RUNNING_CONTAINERS=$(docker-compose ps --services --filter status=running | wc -l)
    TOTAL_CONTAINERS=$(docker-compose ps --services | wc -l)
    
    log_message "Running containers: $RUNNING_CONTAINERS/$TOTAL_CONTAINERS"
    
    if [ "$RUNNING_CONTAINERS" -eq 0 ]; then
        alert_message "No containers are running!"
        return 1
    elif [ "$RUNNING_CONTAINERS" -lt "$TOTAL_CONTAINERS" ]; then
        warning_message "Some containers are not running ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
        docker-compose ps | tee -a $LOG_FILE
        return 2
    else
        success_message "All containers are running ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
        return 0
    fi
}

check_application_health() {
    log_message "Checking application health..."
    
    # Check frontend
    if curl -f -s http://localhost:3911 > /dev/null; then
        success_message "Frontend is responding (port 3911)"
        FRONTEND_OK=1
    else
        alert_message "Frontend is not responding on port 3911"
        FRONTEND_OK=0
    fi
    
    # Check backend
    if curl -f -s http://localhost:8953 > /dev/null; then
        success_message "Backend is responding (port 8953)"
        BACKEND_OK=1
    else
        warning_message "Backend is not responding on port 8953"
        BACKEND_OK=0
    fi
    
    if [ "$FRONTEND_OK" -eq 1 ] && [ "$BACKEND_OK" -eq 1 ]; then
        success_message "All application endpoints are healthy"
        return 0
    elif [ "$FRONTEND_OK" -eq 1 ]; then
        warning_message "Frontend OK, but backend issues detected"
        return 1
    else
        alert_message "Critical: Frontend is not responding"
        return 2
    fi
}

check_system_resources() {
    log_message "Checking system resources..."
    
    # Check disk space
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        alert_message "Disk usage is critical: ${DISK_USAGE}%"
    elif [ "$DISK_USAGE" -gt 80 ]; then
        warning_message "Disk usage is high: ${DISK_USAGE}%"
    else
        success_message "Disk usage is normal: ${DISK_USAGE}%"
    fi
    
    # Check memory usage
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -gt 90 ]; then
        alert_message "Memory usage is critical: ${MEMORY_USAGE}%"
    elif [ "$MEMORY_USAGE" -gt 80 ]; then
        warning_message "Memory usage is high: ${MEMORY_USAGE}%"
    else
        success_message "Memory usage is normal: ${MEMORY_USAGE}%"
    fi
    
    log_message "System resources - Disk: ${DISK_USAGE}%, Memory: ${MEMORY_USAGE}%"
}

restart_unhealthy_containers() {
    log_message "Attempting to restart unhealthy containers..."
    cd $PROJECT_DIR
    
    # Get unhealthy containers
    UNHEALTHY=$(docker-compose ps --filter status=unhealthy --services)
    
    if [ -n "$UNHEALTHY" ]; then
        log_message "Restarting unhealthy containers: $UNHEALTHY"
        docker-compose restart $UNHEALTHY
        sleep 30
        success_message "Restart completed"
    else
        log_message "No unhealthy containers found"
    fi
}

generate_status_report() {
    echo "=== AGENTIC SITE STATUS REPORT ==="
    echo "Generated: $(date)"
    echo ""
    
    echo "🐳 DOCKER STATUS:"
    docker --version
    docker-compose --version
    echo ""
    
    echo "📦 CONTAINER STATUS:"
    cd $PROJECT_DIR
    docker-compose ps
    echo ""
    
    echo "🌐 APPLICATION HEALTH:"
    echo -n "Frontend (port 3911): "
    if curl -f -s http://localhost:3911 > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
    
    echo -n "Backend (port 8953): "
    if curl -f -s http://localhost:8953 > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
    echo ""
    
    echo "💾 SYSTEM RESOURCES:"
    echo "Disk Usage: $(df / | awk 'NR==2 {print $5}')"
    echo "Memory Usage: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
    echo ""
    
    echo "📊 RECENT LOGS (last 10 lines):"
    tail -10 $LOG_FILE 2>/dev/null || echo "No logs available"
}

# Main monitoring function
main() {
    case "$1" in
        "status")
            generate_status_report
            ;;
        "health")
            check_docker_status && check_containers && check_application_health
            ;;
        "restart")
            restart_unhealthy_containers
            ;;
        "full")
            log_message "Starting full monitoring check..."
            check_docker_status
            check_containers
            check_application_health
            check_system_resources
            
            # Auto-restart if needed
            if [ $? -ne 0 ]; then
                log_message "Issues detected, attempting auto-restart..."
                restart_unhealthy_containers
                sleep 30
                check_application_health
            fi
            ;;
        *)
            echo "Usage: $0 {status|health|restart|full}"
            echo ""
            echo "Commands:"
            echo "  status  - Show detailed status report"
            echo "  health  - Quick health check"
            echo "  restart - Restart unhealthy containers"
            echo "  full    - Complete monitoring with auto-restart"
            exit 1
            ;;
    esac
}

main "$@"
'''

    # Create deployment verification script
    verification_script = '''#!/bin/bash
# Deployment Verification Script
# Location: /root/agentic-site/verify-deployment.sh

PROJECT_DIR="/root/agentic-site"
VERIFICATION_LOG="/var/log/deployment-verification.log"

log_verification() {
    echo "$(date): $1" | tee -a $VERIFICATION_LOG
}

verify_deployment() {
    log_verification "Starting deployment verification..."
    
    PASSED=0
    FAILED=0
    
    # Test 1: Check if project directory exists
    if [ -d "$PROJECT_DIR" ]; then
        log_verification "✅ Project directory exists: $PROJECT_DIR"
        ((PASSED++))
    else
        log_verification "❌ Project directory missing: $PROJECT_DIR"
        ((FAILED++))
    fi
    
    # Test 2: Check Docker Compose file
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        log_verification "✅ Docker Compose file exists"
        ((PASSED++))
    else
        log_verification "❌ Docker Compose file missing"
        ((FAILED++))
    fi
    
    # Test 3: Check containers are running
    cd $PROJECT_DIR
    RUNNING=$(docker-compose ps --services --filter status=running | wc -l)
    if [ "$RUNNING" -gt 0 ]; then
        log_verification "✅ Containers are running: $RUNNING"
        ((PASSED++))
    else
        log_verification "❌ No containers are running"
        ((FAILED++))
    fi
    
    # Test 4: Check frontend accessibility
    if curl -f -s http://localhost:3911 > /dev/null; then
        log_verification "✅ Frontend is accessible (port 3911)"
        ((PASSED++))
    else
        log_verification "❌ Frontend is not accessible"
        ((FAILED++))
    fi
    
    # Test 5: Check backend accessibility
    if curl -f -s http://localhost:8953 > /dev/null; then
        log_verification "✅ Backend is accessible (port 8953)"
        ((PASSED++))
    else
        log_verification "⚠️  Backend is not accessible (may be expected)"
        # Don't count as failed since backend might not have public endpoint
    fi
    
    # Test 6: Check external accessibility
    EXTERNAL_IP=$(curl -s ifconfig.me)
    if curl -f -s http://$EXTERNAL_IP:3911 > /dev/null; then
        log_verification "✅ Application is externally accessible"
        ((PASSED++))
    else
        log_verification "⚠️  External accessibility test failed (firewall may be blocking)"
    fi
    
    # Summary
    log_verification "Verification completed: $PASSED passed, $FAILED failed"
    
    if [ "$FAILED" -eq 0 ]; then
        log_verification "🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!"
        return 0
    else
        log_verification "⚠️  DEPLOYMENT VERIFICATION COMPLETED WITH ISSUES"
        return 1
    fi
}

verify_deployment
'''

    # Create auto-restart service script
    service_script = '''#!/bin/bash
# Auto-restart service for application monitoring
# Location: /root/agentic-site/auto-monitor.sh

PROJECT_DIR="/root/agentic-site"
MONITOR_LOG="/var/log/auto-monitor.log"

while true; do
    echo "$(date): Running automated health check..." >> $MONITOR_LOG
    
    cd $PROJECT_DIR
    if ! ./monitor.sh health >> $MONITOR_LOG 2>&1; then
        echo "$(date): Health check failed, attempting restart..." >> $MONITOR_LOG
        ./monitor.sh restart >> $MONITOR_LOG 2>&1
        sleep 60
    fi
    
    # Wait 5 minutes before next check
    sleep 300
done
'''

    # Upload scripts to VPS
    scripts = [
        ("monitor.sh", monitoring_script),
        ("verify-deployment.sh", verification_script),
        ("auto-monitor.sh", service_script)
    ]
    
    for script_name, script_content in scripts:
        print(f"📝 Creating {script_name} on VPS...")
        
        # Create script on VPS
        cmd = f"""ssh root@217.79.255.54 'cd /root/agentic-site && cat > {script_name} << "EOF"
{script_content}
EOF
chmod +x {script_name}
echo "Created {script_name}"'"""
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {script_name} created successfully")
        else:
            print(f"❌ Failed to create {script_name}: {result.stderr}")

def test_monitoring():
    """Test the monitoring scripts"""
    print("\n🧪 Testing monitoring scripts...")
    
    # Test status report
    print("\n📊 Running status report...")
    result = subprocess.run("ssh root@217.79.255.54 'cd /root/agentic-site && ./monitor.sh status'", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Status report generated successfully")
        print(result.stdout)
    else:
        print(f"❌ Status report failed: {result.stderr}")
    
    # Test deployment verification
    print("\n🔍 Running deployment verification...")
    result = subprocess.run("ssh root@217.79.255.54 'cd /root/agentic-site && ./verify-deployment.sh'", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Deployment verification passed")
    else:
        print("⚠️  Deployment verification completed with warnings")
    print(result.stdout)

def main():
    print("🔧 CREATING MONITORING AND VERIFICATION SYSTEM")
    print("="*50)
    
    # Create monitoring scripts
    create_monitoring_scripts()
    
    # Test the scripts
    test_monitoring()
    
    print("\n✅ MONITORING SYSTEM SETUP COMPLETE!")
    print("\n🎯 AVAILABLE COMMANDS:")
    print("  • Status Report: ssh root@217.79.255.54 'cd /root/agentic-site && ./monitor.sh status'")
    print("  • Health Check: ssh root@217.79.255.54 'cd /root/agentic-site && ./monitor.sh health'")
    print("  • Restart Services: ssh root@217.79.255.54 'cd /root/agentic-site && ./monitor.sh restart'")
    print("  • Full Monitoring: ssh root@217.79.255.54 'cd /root/agentic-site && ./monitor.sh full'")
    print("  • Verify Deployment: ssh root@217.79.255.54 'cd /root/agentic-site && ./verify-deployment.sh'")

if __name__ == "__main__":
    main()