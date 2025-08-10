#!/bin/bash
"""
Setup script for Intrusion Detection System
Configures system for real-time threat monitoring
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Install required packages
install_dependencies() {
    log "Installing required packages..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        iptables \
        iptables-persistent \
        rsyslog \
        logrotate \
        fail2ban \
        rkhunter \
        chkrootkit
    
    # Install Python packages
    pip3 install \
        psutil \
        asyncio \
        watchdog \
        requests \
        python-dateutil
    
    log "Dependencies installed successfully"
}

# Create required directories
setup_directories() {
    log "Setting up directories..."
    
    # Create security directories
    mkdir -p /etc/security
    mkdir -p /var/log/security
    mkdir -p /opt/intrusion-detection
    
    # Set proper permissions
    chmod 755 /etc/security
    chmod 755 /var/log/security
    chmod 755 /opt/intrusion-detection
    
    # Create threat intelligence directory
    mkdir -p /etc/security/threat-feeds
    
    log "Directories created successfully"
}

# Copy threat intelligence feeds
setup_threat_feeds() {
    log "Setting up threat intelligence feeds..."
    
    # Copy threat feeds if they exist
    if [[ -f "tools/security/threat-feeds/malicious-ips.txt" ]]; then
        cp tools/security/threat-feeds/malicious-ips.txt /etc/security/malicious-ips.txt
        chmod 644 /etc/security/malicious-ips.txt
    fi
    
    if [[ -f "tools/security/threat-feeds/suspicious-patterns.txt" ]]; then
        cp tools/security/threat-feeds/suspicious-patterns.txt /etc/security/suspicious-patterns.txt
        chmod 644 /etc/security/suspicious-patterns.txt
    fi
    
    log "Threat feeds configured"
}

# Configure log rotation
setup_log_rotation() {
    log "Configuring log rotation..."
    
    cat > /etc/logrotate.d/intrusion-detection << 'EOF'
/var/log/intrusion-detection.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}

/var/log/security-events.json {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}

/var/log/security-alerts.json {
    daily
    rotate 365
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

    log "Log rotation configured"
}

# Configure fail2ban
setup_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create custom jail for our intrusion detection
    cat > /etc/fail2ban/jail.d/intrusion-detection.conf << 'EOF'
[intrusion-detection]
enabled = true
port = ssh,http,https
filter = intrusion-detection
logpath = /var/log/security-events.json
maxretry = 3
bantime = 3600
findtime = 600
action = iptables-multiport[name=intrusion-detection, port="ssh,http,https", protocol=tcp]
EOF

    # Create custom filter
    cat > /etc/fail2ban/filter.d/intrusion-detection.conf << 'EOF'
[Definition]
failregex = .*"source_ip": "(<HOST>)".*"severity": "(HIGH|CRITICAL)".*
ignoreregex =
EOF

    # Restart fail2ban
    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log "Fail2ban configured"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/intrusion-detection.service << 'EOF'
[Unit]
Description=Intrusion Detection System
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/intrusion-detection
ExecStart=/usr/bin/python3 /opt/intrusion-detection/intrusion-detection.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=intrusion-detection

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /etc/security
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # Copy the intrusion detection script
    if [[ -f "tools/security/intrusion-detection.py" ]]; then
        cp tools/security/intrusion-detection.py /opt/intrusion-detection/
        chmod 755 /opt/intrusion-detection/intrusion-detection.py
    fi
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable intrusion-detection
    
    log "Systemd service created"
}

# Configure iptables rules
setup_iptables() {
    log "Setting up iptables rules..."
    
    # Create chain for intrusion detection
    iptables -N INTRUSION_DETECTION 2>/dev/null || true
    iptables -F INTRUSION_DETECTION
    
    # Add rule to jump to our chain
    iptables -I INPUT -j INTRUSION_DETECTION
    
    # Save iptables rules
    iptables-save > /etc/iptables/rules.v4
    
    log "Iptables configured"
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > /opt/intrusion-detection/monitor.sh << 'EOF'
#!/bin/bash
# Intrusion Detection System Monitor

# Check service status
if systemctl is-active --quiet intrusion-detection; then
    echo "✅ Intrusion Detection Service: RUNNING"
else
    echo "❌ Intrusion Detection Service: STOPPED"
fi

# Check recent events
RECENT_EVENTS=$(tail -n 100 /var/log/security-events.json 2>/dev/null | wc -l)
echo "📊 Recent Events (last 100): $RECENT_EVENTS"

# Check alerts
RECENT_ALERTS=$(tail -n 10 /var/log/security-alerts.json 2>/dev/null | wc -l)
echo "🚨 Recent Alerts (last 10): $RECENT_ALERTS"

# Check blocked IPs
BLOCKED_IPS=$(iptables -L INTRUSION_DETECTION -n | grep DROP | wc -l)
echo "🚫 Blocked IPs: $BLOCKED_IPS"

# Check system resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
echo "💻 System: CPU ${CPU_USAGE}%, Memory ${MEM_USAGE}%"

# Check log file sizes
LOG_SIZE=$(du -sh /var/log/security-events.json 2>/dev/null | cut -f1 || echo "0")
echo "📝 Security Events Log: $LOG_SIZE"
EOF

    chmod +x /opt/intrusion-detection/monitor.sh
    
    log "Monitoring script created"
}

# Create management script
create_management_script() {
    log "Creating management script..."
    
    cat > /opt/intrusion-detection/manage.sh << 'EOF'
#!/bin/bash
# Intrusion Detection System Management

case "$1" in
    start)
        echo "Starting Intrusion Detection System..."
        systemctl start intrusion-detection
        ;;
    stop)
        echo "Stopping Intrusion Detection System..."
        systemctl stop intrusion-detection
        ;;
    restart)
        echo "Restarting Intrusion Detection System..."
        systemctl restart intrusion-detection
        ;;
    status)
        systemctl status intrusion-detection
        ;;
    logs)
        journalctl -u intrusion-detection -f
        ;;
    events)
        tail -f /var/log/security-events.json
        ;;
    alerts)
        tail -f /var/log/security-alerts.json
        ;;
    monitor)
        /opt/intrusion-detection/monitor.sh
        ;;
    unblock)
        if [[ -n "$2" ]]; then
            echo "Unblocking IP: $2"
            iptables -D INTRUSION_DETECTION -s "$2" -j DROP 2>/dev/null || echo "IP not found in blocked list"
        else
            echo "Usage: $0 unblock <IP_ADDRESS>"
        fi
        ;;
    list-blocked)
        echo "Blocked IPs:"
        iptables -L INTRUSION_DETECTION -n | grep DROP | awk '{print $4}'
        ;;
    update-feeds)
        echo "Updating threat intelligence feeds..."
        # This would typically download from external sources
        echo "Manual update required - check threat-feeds directory"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|events|alerts|monitor|unblock|list-blocked|update-feeds}"
        exit 1
        ;;
esac
EOF

    chmod +x /opt/intrusion-detection/manage.sh
    
    # Create symlink for easy access
    ln -sf /opt/intrusion-detection/manage.sh /usr/local/bin/ids-manage
    
    log "Management script created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > /opt/intrusion-detection/health-check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check script for Intrusion Detection System
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_service_status():
    """Check if the service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'intrusion-detection'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_log_files():
    """Check if log files are being written"""
    log_files = [
        '/var/log/intrusion-detection.log',
        '/var/log/security-events.json'
    ]
    
    issues = []
    for log_file in log_files:
        if not os.path.exists(log_file):
            issues.append(f"Log file missing: {log_file}")
        else:
            # Check if file was modified in last hour
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            if datetime.now() - mtime > timedelta(hours=1):
                issues.append(f"Log file not updated: {log_file}")
    
    return issues

def check_threat_feeds():
    """Check if threat intelligence feeds are available"""
    feeds = [
        '/etc/security/malicious-ips.txt',
        '/etc/security/suspicious-patterns.txt'
    ]
    
    issues = []
    for feed in feeds:
        if not os.path.exists(feed):
            issues.append(f"Threat feed missing: {feed}")
    
    return issues

def check_system_resources():
    """Check system resource usage"""
    issues = []
    
    # Check disk space
    result = subprocess.run(['df', '/var/log'], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            usage = lines[1].split()[4].rstrip('%')
            if int(usage) > 90:
                issues.append(f"High disk usage in /var/log: {usage}%")
    
    return issues

def main():
    """Main health check function"""
    print("🔍 Intrusion Detection System Health Check")
    print("=" * 50)
    
    all_good = True
    
    # Check service status
    if check_service_status():
        print("✅ Service Status: RUNNING")
    else:
        print("❌ Service Status: NOT RUNNING")
        all_good = False
    
    # Check log files
    log_issues = check_log_files()
    if not log_issues:
        print("✅ Log Files: OK")
    else:
        print("❌ Log Files: ISSUES FOUND")
        for issue in log_issues:
            print(f"   - {issue}")
        all_good = False
    
    # Check threat feeds
    feed_issues = check_threat_feeds()
    if not feed_issues:
        print("✅ Threat Feeds: OK")
    else:
        print("❌ Threat Feeds: ISSUES FOUND")
        for issue in feed_issues:
            print(f"   - {issue}")
        all_good = False
    
    # Check system resources
    resource_issues = check_system_resources()
    if not resource_issues:
        print("✅ System Resources: OK")
    else:
        print("⚠️  System Resources: WARNINGS")
        for issue in resource_issues:
            print(f"   - {issue}")
    
    print("=" * 50)
    if all_good:
        print("🎉 Overall Status: HEALTHY")
        sys.exit(0)
    else:
        print("🚨 Overall Status: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x /opt/intrusion-detection/health-check.py
    
    log "Health check script created"
}

# Main setup function
main() {
    log "Starting Intrusion Detection System setup..."
    
    check_root
    install_dependencies
    setup_directories
    setup_threat_feeds
    setup_log_rotation
    setup_fail2ban
    create_systemd_service
    setup_iptables
    create_monitoring_script
    create_management_script
    create_health_check
    
    log "Setup completed successfully!"
    echo
    echo "🎉 Intrusion Detection System is now configured!"
    echo
    echo "Next steps:"
    echo "1. Start the service: systemctl start intrusion-detection"
    echo "2. Check status: ids-manage status"
    echo "3. Monitor events: ids-manage events"
    echo "4. View alerts: ids-manage alerts"
    echo "5. Run health check: /opt/intrusion-detection/health-check.py"
    echo
    echo "Management commands available via: ids-manage"
}

# Run main function
main "$@"