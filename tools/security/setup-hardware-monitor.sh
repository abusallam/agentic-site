#!/bin/bash
"""
Setup script for Hardware Security Monitoring System
Configures hardware integrity monitoring and tamper detection
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
    log "Installing hardware monitoring dependencies..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        lshw \
        dmidecode \
        smartmontools \
        lsusb \
        pciutils \
        usbutils \
        rkhunter \
        chkrootkit \
        aide \
        tripwire \
        lynis \
        debsums
    
    # Install Python packages
    pip3 install \
        psutil \
        asyncio \
        hashlib \
        pathlib
    
    log "Dependencies installed successfully"
}

# Setup directories and permissions
setup_directories() {
    log "Setting up directories..."
    
    # Create required directories
    mkdir -p /opt/hardware-monitor
    mkdir -p /var/lib/hardware-monitor
    mkdir -p /var/log/hardware-monitor
    mkdir -p /etc/security/hardware
    
    # Set proper permissions
    chmod 755 /opt/hardware-monitor
    chmod 755 /var/lib/hardware-monitor
    chmod 755 /var/log/hardware-monitor
    chmod 755 /etc/security/hardware
    
    log "Directories created successfully"
}

# Create hardware baseline
create_hardware_baseline() {
    log "Creating hardware baseline..."
    
    # Create initial hardware inventory
    if [[ -f "tools/security/hardware-monitor.py" ]]; then
        cp tools/security/hardware-monitor.py /opt/hardware-monitor/
        chmod +x /opt/hardware-monitor/hardware-monitor.py
        
        # Run initial scan to create baseline
        cd /opt/hardware-monitor
        python3 hardware-monitor.py --create-baseline || warn "Could not create initial baseline"
    fi
    
    # Create trusted boot hashes file
    cat > /etc/security/trusted-boot-hashes.txt << 'EOF'
# Trusted boot component hashes
# Add SHA256 hashes of trusted kernel and initrd files
# Format: one hash per line
# Example:
# a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456

# Kernel hashes (update after kernel updates)
# initrd hashes (update after initrd changes)
EOF

    # Create rootkit signatures file
    cat > /etc/security/rootkit-signatures.txt << 'EOF'
# Known rootkit signatures and indicators
# Updated: 2025-01-09

# File-based rootkit signatures
/dev/shm/.ICE-unix
/tmp/.ICE-unix
/var/tmp/.ICE-unix
/usr/bin/host.
/usr/bin/du.
/usr/bin/ls.
/bin/netstat.
/bin/ps.

# Process names
rootkit
backdoor
keylogger
stealth
hide_process
invisible
ghost_process

# Network signatures
:1337
:31337
:4444
:5555
:6666
:7777
:8888
:9999

# Registry/config signatures (Linux equivalents)
LD_PRELOAD
/etc/ld.so.preload
/lib/security/
/usr/lib/security/

# Suspicious kernel modules
rootkit.ko
backdoor.ko
keylogger.ko
stealth.ko
hide.ko
EOF

    log "Hardware baseline created"
}

# Configure AIDE (Advanced Intrusion Detection Environment)
setup_aide() {
    log "Configuring AIDE..."
    
    # Initialize AIDE database
    if command -v aide >/dev/null 2>&1; then
        # Create AIDE configuration
        cat > /etc/aide/aide.conf.d/hardware-monitor << 'EOF'
# Hardware monitoring specific AIDE rules

# Monitor critical system binaries
/bin/ls f+p+u+g+s+m+c+md5+sha256
/bin/ps f+p+u+g+s+m+c+md5+sha256
/bin/netstat f+p+u+g+s+m+c+md5+sha256
/usr/bin/who f+p+u+g+s+m+c+md5+sha256
/usr/bin/w f+p+u+g+s+m+c+md5+sha256
/usr/bin/last f+p+u+g+s+m+c+md5+sha256
/sbin/ifconfig f+p+u+g+s+m+c+md5+sha256

# Monitor boot files
/boot f+p+u+g+s+m+c+md5+sha256

# Monitor kernel modules
/lib/modules f+p+u+g+s+m+c+md5+sha256

# Monitor system libraries
/lib f+p+u+g+s+m+c+md5+sha256
/usr/lib f+p+u+g+s+m+c+md5+sha256
EOF

        # Initialize AIDE database
        aide --init || warn "AIDE initialization failed"
        
        # Move database to proper location
        if [[ -f /var/lib/aide/aide.db.new ]]; then
            mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
        fi
    fi
    
    log "AIDE configured"
}

# Configure rkhunter
setup_rkhunter() {
    log "Configuring rkhunter..."
    
    if command -v rkhunter >/dev/null 2>&1; then
        # Update rkhunter configuration
        cat >> /etc/rkhunter.conf << 'EOF'

# Hardware monitoring specific configuration
ALLOWHIDDENDIR=/etc/.java
ALLOWHIDDENFILE=/etc/.pwd.lock
ALLOWHIDDENFILE=/etc/.updated
ALLOWHIDDENFILE=/usr/share/man/man1/..1.gz
ALLOWHIDDENFILE=/lib/modules/*/modules.builtin.bin

# Skip some checks that may cause false positives
DISABLE_TESTS="suspscan hidden_procs deleted_files packet_cap_apps apps"

# Enable additional checks
ENABLE_TESTS="all"

# Logging
LOGFILE=/var/log/rkhunter.log
APPEND_LOG=1
COPY_LOG_ON_ERROR=1
EOF

        # Update rkhunter database
        rkhunter --update || warn "rkhunter update failed"
        rkhunter --propupd || warn "rkhunter property update failed"
    fi
    
    log "rkhunter configured"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/hardware-monitor.service << 'EOF'
[Unit]
Description=Hardware Security Monitor
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/hardware-monitor
ExecStart=/usr/bin/python3 /opt/hardware-monitor/hardware-monitor.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hardware-monitor

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /var/lib /etc/security
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable hardware-monitor
    
    log "Systemd service created"
}

# Configure log rotation
setup_log_rotation() {
    log "Configuring log rotation..."
    
    cat > /etc/logrotate.d/hardware-monitor << 'EOF'
/var/log/hardware-security.log {
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

/var/log/hardware-security-events.json {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}

/var/log/hardware-security-alerts.json {
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

# Create monitoring scripts
create_monitoring_scripts() {
    log "Creating monitoring scripts..."
    
    # Hardware status script
    cat > /opt/hardware-monitor/status.sh << 'EOF'
#!/bin/bash
# Hardware Security Monitor Status

echo "🔧 Hardware Security Monitor Status"
echo "=================================="

# Check service status
if systemctl is-active --quiet hardware-monitor; then
    echo "✅ Hardware Monitor Service: RUNNING"
else
    echo "❌ Hardware Monitor Service: STOPPED"
fi

# Check recent events
RECENT_EVENTS=$(tail -n 100 /var/log/hardware-security-events.json 2>/dev/null | wc -l)
echo "📊 Recent Events (last 100): $RECENT_EVENTS"

# Check alerts
RECENT_ALERTS=$(tail -n 10 /var/log/hardware-security-alerts.json 2>/dev/null | wc -l)
echo "🚨 Recent Alerts (last 10): $RECENT_ALERTS"

# Check hardware inventory
if [[ -f /var/lib/hardware-inventory.json ]]; then
    COMPONENTS=$(jq 'keys | length' /var/lib/hardware-inventory.json 2>/dev/null || echo "0")
    echo "🖥️  Hardware Components: $COMPONENTS"
else
    echo "🖥️  Hardware Components: No inventory found"
fi

# Check system integrity
echo "🔍 System Integrity Checks:"

# AIDE check
if command -v aide >/dev/null 2>&1; then
    if [[ -f /var/lib/aide/aide.db ]]; then
        echo "   ✅ AIDE: Database present"
    else
        echo "   ⚠️  AIDE: No database found"
    fi
else
    echo "   ❌ AIDE: Not installed"
fi

# rkhunter status
if command -v rkhunter >/dev/null 2>&1; then
    echo "   ✅ rkhunter: Available"
else
    echo "   ❌ rkhunter: Not installed"
fi

# chkrootkit status
if command -v chkrootkit >/dev/null 2>&1; then
    echo "   ✅ chkrootkit: Available"
else
    echo "   ❌ chkrootkit: Not installed"
fi

# System resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
echo "💻 System: CPU ${CPU_USAGE}%, Memory ${MEM_USAGE}%"

# Log file sizes
LOG_SIZE=$(du -sh /var/log/hardware-security-events.json 2>/dev/null | cut -f1 || echo "0")
echo "📝 Hardware Events Log: $LOG_SIZE"
EOF

    # Management script
    cat > /opt/hardware-monitor/manage.sh << 'EOF'
#!/bin/bash
# Hardware Security Monitor Management

case "$1" in
    start)
        echo "Starting Hardware Security Monitor..."
        systemctl start hardware-monitor
        ;;
    stop)
        echo "Stopping Hardware Security Monitor..."
        systemctl stop hardware-monitor
        ;;
    restart)
        echo "Restarting Hardware Security Monitor..."
        systemctl restart hardware-monitor
        ;;
    status)
        systemctl status hardware-monitor
        ;;
    logs)
        journalctl -u hardware-monitor -f
        ;;
    events)
        tail -f /var/log/hardware-security-events.json
        ;;
    alerts)
        tail -f /var/log/hardware-security-alerts.json
        ;;
    monitor)
        /opt/hardware-monitor/status.sh
        ;;
    scan)
        echo "Running manual hardware scan..."
        python3 /opt/hardware-monitor/hardware-monitor.py --scan
        ;;
    baseline)
        echo "Creating new hardware baseline..."
        python3 /opt/hardware-monitor/hardware-monitor.py --create-baseline
        ;;
    integrity-check)
        echo "Running integrity checks..."
        if command -v aide >/dev/null 2>&1; then
            aide --check
        fi
        if command -v rkhunter >/dev/null 2>&1; then
            rkhunter --check --sk
        fi
        if command -v chkrootkit >/dev/null 2>&1; then
            chkrootkit
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|events|alerts|monitor|scan|baseline|integrity-check}"
        exit 1
        ;;
esac
EOF

    # Make scripts executable
    chmod +x /opt/hardware-monitor/status.sh
    chmod +x /opt/hardware-monitor/manage.sh
    
    # Create symlink for easy access
    ln -sf /opt/hardware-monitor/manage.sh /usr/local/bin/hwmon-manage
    
    log "Monitoring scripts created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > /opt/hardware-monitor/health-check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check script for Hardware Security Monitor
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
        result = subprocess.run(['systemctl', 'is-active', 'hardware-monitor'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_hardware_inventory():
    """Check if hardware inventory exists and is recent"""
    inventory_file = Path('/var/lib/hardware-inventory.json')
    
    if not inventory_file.exists():
        return False, "Hardware inventory file not found"
    
    # Check if inventory is recent (within last 24 hours)
    mtime = datetime.fromtimestamp(inventory_file.stat().st_mtime)
    if datetime.now() - mtime > timedelta(hours=24):
        return False, f"Hardware inventory outdated (last updated: {mtime})"
    
    return True, "Hardware inventory is current"

def check_integrity_tools():
    """Check if integrity monitoring tools are available"""
    tools = {
        'aide': 'Advanced Intrusion Detection Environment',
        'rkhunter': 'Rootkit Hunter',
        'chkrootkit': 'Check Rootkit'
    }
    
    available_tools = []
    missing_tools = []
    
    for tool, description in tools.items():
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode == 0:
            available_tools.append(f"{tool} ({description})")
        else:
            missing_tools.append(f"{tool} ({description})")
    
    return available_tools, missing_tools

def check_log_files():
    """Check if log files are being written"""
    log_files = [
        '/var/log/hardware-security.log',
        '/var/log/hardware-security-events.json'
    ]
    
    issues = []
    for log_file in log_files:
        if not os.path.exists(log_file):
            issues.append(f"Log file missing: {log_file}")
        else:
            # Check if file was modified in last 2 hours
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            if datetime.now() - mtime > timedelta(hours=2):
                issues.append(f"Log file not updated: {log_file}")
    
    return issues

def main():
    """Main health check function"""
    print("🔧 Hardware Security Monitor Health Check")
    print("=" * 50)
    
    all_good = True
    
    # Check service status
    if check_service_status():
        print("✅ Service Status: RUNNING")
    else:
        print("❌ Service Status: NOT RUNNING")
        all_good = False
    
    # Check hardware inventory
    inventory_ok, inventory_msg = check_hardware_inventory()
    if inventory_ok:
        print(f"✅ Hardware Inventory: {inventory_msg}")
    else:
        print(f"⚠️  Hardware Inventory: {inventory_msg}")
    
    # Check integrity tools
    available_tools, missing_tools = check_integrity_tools()
    if available_tools:
        print("✅ Integrity Tools Available:")
        for tool in available_tools:
            print(f"   - {tool}")
    
    if missing_tools:
        print("⚠️  Missing Integrity Tools:")
        for tool in missing_tools:
            print(f"   - {tool}")
    
    # Check log files
    log_issues = check_log_files()
    if not log_issues:
        print("✅ Log Files: OK")
    else:
        print("❌ Log Files: ISSUES FOUND")
        for issue in log_issues:
            print(f"   - {issue}")
        all_good = False
    
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

    chmod +x /opt/hardware-monitor/health-check.py
    
    log "Health check script created"
}

# Main setup function
main() {
    log "Starting Hardware Security Monitor setup..."
    
    check_root
    install_dependencies
    setup_directories
    create_hardware_baseline
    setup_aide
    setup_rkhunter
    create_systemd_service
    setup_log_rotation
    create_monitoring_scripts
    create_health_check
    
    log "Setup completed successfully!"
    echo
    echo "🎉 Hardware Security Monitor is now configured!"
    echo
    echo "Next steps:"
    echo "1. Start the service: systemctl start hardware-monitor"
    echo "2. Check status: hwmon-manage status"
    echo "3. Create baseline: hwmon-manage baseline"
    echo "4. Monitor events: hwmon-manage events"
    echo "5. Run integrity check: hwmon-manage integrity-check"
    echo "6. Run health check: /opt/hardware-monitor/health-check.py"
    echo
    echo "Management commands available via: hwmon-manage"
}

# Run main function
main "$@"