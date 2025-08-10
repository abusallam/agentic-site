#!/bin/bash
"""
Setup script for Security Incident Response Automation System
Configures automated threat containment and forensic data collection
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
    log "Installing incident response dependencies..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        iptables \
        iptables-persistent \
        auditd \
        acct \
        psmisc \
        lsof \
        strace \
        tcpdump \
        wireshark-common \
        forensics-all \
        sleuthkit \
        autopsy \
        volatility \
        binwalk \
        foremost \
        scalpel \
        dc3dd \
        ddrescue \
        safecopy \
        guymager
    
    # Install Python packages
    pip3 install \
        psutil \
        requests \
        asyncio \
        pathlib \
        smtplib \
        email \
        tarfile \
        hashlib
    
    log "Dependencies installed successfully"
}

# Setup directories and permissions
setup_directories() {
    log "Setting up directories..."
    
    # Create required directories
    mkdir -p /opt/incident-response
    mkdir -p /var/lib/incident-response/{incidents,evidence,quarantine,snapshots}
    mkdir -p /var/log/incident-response
    mkdir -p /etc/incident-response
    
    # Set proper permissions
    chmod 755 /opt/incident-response
    chmod 700 /var/lib/incident-response  # Restricted access for sensitive data
    chmod 700 /var/lib/incident-response/evidence
    chmod 700 /var/lib/incident-response/quarantine
    chmod 755 /var/lib/incident-response/incidents
    chmod 755 /var/lib/incident-response/snapshots
    chmod 755 /var/log/incident-response
    chmod 755 /etc/incident-response
    
    log "Directories created successfully"
}

# Configure notification system
setup_notifications() {
    log "Setting up notification system..."
    
    # Create notification configuration
    cat > /etc/incident-response/notifications.json << 'EOF'
{
  "email": {
    "enabled": false,
    "smtp_server": "localhost",
    "smtp_port": 587,
    "use_tls": true,
    "username": "",
    "password": "",
    "recipients": [
      "security-team@company.com",
      "admin@company.com"
    ]
  },
  "webhook": {
    "enabled": false,
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "headers": {
      "Content-Type": "application/json"
    },
    "timeout": 30
  },
  "syslog": {
    "enabled": true,
    "facility": "local0",
    "priority_mapping": {
      "CRITICAL": "crit",
      "HIGH": "err",
      "MEDIUM": "warning",
      "LOW": "info"
    }
  },
  "escalation_rules": {
    "CRITICAL": {
      "immediate_notifications": ["email", "webhook", "syslog"],
      "escalation_time_minutes": 5,
      "escalation_notifications": ["email", "webhook"]
    },
    "HIGH": {
      "immediate_notifications": ["email", "syslog"],
      "escalation_time_minutes": 15,
      "escalation_notifications": ["email"]
    },
    "MEDIUM": {
      "immediate_notifications": ["syslog"],
      "escalation_time_minutes": 60,
      "escalation_notifications": ["email"]
    },
    "LOW": {
      "immediate_notifications": ["syslog"],
      "escalation_time_minutes": 1440,
      "escalation_notifications": []
    }
  }
}
EOF

    chmod 600 /etc/incident-response/notifications.json
    
    log "Notification system configured"
}

# Configure containment policies
setup_containment_policies() {
    log "Setting up containment policies..."
    
    # Create containment policy configuration
    cat > /etc/incident-response/containment-policies.json << 'EOF'
{
  "automatic_containment": {
    "enabled": true,
    "severity_threshold": "HIGH",
    "max_actions_per_incident": 10,
    "confirmation_required": false
  },
  "containment_actions": {
    "MALICIOUS_IP": {
      "enabled": true,
      "actions": ["block_ip", "log_connections"],
      "auto_execute": true,
      "max_ips_per_incident": 100
    },
    "SUSPICIOUS_PROCESS": {
      "enabled": true,
      "actions": ["terminate_process", "collect_process_info"],
      "auto_execute": true,
      "confirmation_required_for_critical_processes": true
    },
    "COMPROMISED_ACCOUNT": {
      "enabled": true,
      "actions": ["disable_account", "kill_sessions", "revoke_privileges"],
      "auto_execute": false,
      "confirmation_required": true
    },
    "MALWARE_DETECTED": {
      "enabled": true,
      "actions": ["quarantine_file", "scan_system", "collect_samples"],
      "auto_execute": true,
      "backup_before_quarantine": true
    },
    "NETWORK_INTRUSION": {
      "enabled": true,
      "actions": ["isolate_segment", "block_traffic", "enhance_monitoring"],
      "auto_execute": false,
      "confirmation_required": true
    },
    "DATA_EXFILTRATION": {
      "enabled": true,
      "actions": ["block_outbound", "isolate_system", "collect_evidence"],
      "auto_execute": true,
      "emergency_containment": true
    },
    "PRIVILEGE_ESCALATION": {
      "enabled": true,
      "actions": ["revoke_privileges", "audit_permissions", "monitor_activity"],
      "auto_execute": false,
      "confirmation_required": true
    },
    "BRUTE_FORCE_ATTACK": {
      "enabled": true,
      "actions": ["rate_limit", "block_ip", "enhance_auth_logging"],
      "auto_execute": true,
      "threshold_attempts": 10
    }
  },
  "forensic_collection": {
    "automatic_collection": true,
    "severity_threshold": "MEDIUM",
    "collect_memory_dump": {
      "enabled": true,
      "severity_threshold": "CRITICAL",
      "max_dump_size_mb": 1024
    },
    "collect_disk_image": {
      "enabled": false,
      "severity_threshold": "CRITICAL",
      "confirmation_required": true
    },
    "collect_network_traffic": {
      "enabled": true,
      "duration_minutes": 30,
      "max_capture_size_mb": 500
    },
    "preserve_logs": {
      "enabled": true,
      "retention_days": 90,
      "compress_after_days": 7
    }
  }
}
EOF

    chmod 600 /etc/incident-response/containment-policies.json
    
    log "Containment policies configured"
}

# Configure audit system
setup_audit_system() {
    log "Configuring audit system..."
    
    # Enable auditd
    systemctl enable auditd
    
    # Create audit rules for incident response
    cat > /etc/audit/rules.d/incident-response.rules << 'EOF'
# Incident Response Audit Rules

# Monitor file access in sensitive directories
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k identity
-w /etc/ssh/sshd_config -p wa -k sshd

# Monitor privilege escalation
-w /bin/su -p x -k privilege_escalation
-w /usr/bin/sudo -p x -k privilege_escalation
-w /etc/sudoers -p wa -k privilege_escalation

# Monitor network configuration changes
-w /etc/network/ -p wa -k network_config
-w /etc/hosts -p wa -k network_config
-w /etc/resolv.conf -p wa -k network_config

# Monitor system calls that could indicate compromise
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time_change
-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time_change
-a always,exit -F arch=b64 -S clock_settime -k time_change
-a always,exit -F arch=b32 -S clock_settime -k time_change

# Monitor file deletion
-a always,exit -F arch=b64 -S unlink -S unlinkat -S rename -S renameat -k delete
-a always,exit -F arch=b32 -S unlink -S unlinkat -S rename -S renameat -k delete

# Monitor process execution
-a always,exit -F arch=b64 -S execve -k process_execution
-a always,exit -F arch=b32 -S execve -k process_execution

# Make the configuration immutable
-e 2
EOF

    # Restart auditd
    systemctl restart auditd
    
    log "Audit system configured"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/incident-response.service << 'EOF'
[Unit]
Description=Security Incident Response System
After=network.target auditd.service
Wants=network.target
Requires=auditd.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/incident-response
ExecStart=/usr/bin/python3 /opt/incident-response/incident-response.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=incident-response

# Security settings
NoNewPrivileges=false
ProtectSystem=false
ProtectHome=false
ReadWritePaths=/var/log /var/lib /etc/incident-response /tmp
PrivateTmp=false

# Environment
Environment=PYTHONPATH=/opt/incident-response
Environment=INCIDENT_RESPONSE_CONFIG=/etc/incident-response

[Install]
WantedBy=multi-user.target
EOF

    # Copy the incident response script
    if [[ -f "tools/security/incident-response.py" ]]; then
        cp tools/security/incident-response.py /opt/incident-response/
        chmod +x /opt/incident-response/incident-response.py
    fi
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable incident-response
    
    log "Systemd service created"
}

# Configure log rotation
setup_log_rotation() {
    log "Configuring log rotation..."
    
    cat > /etc/logrotate.d/incident-response << 'EOF'
/var/log/incident-response.log {
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

/var/log/security-incidents.json {
    daily
    rotate 365
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}

/var/log/incident-response/*.log {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

    log "Log rotation configured"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."
    
    # Status script
    cat > /opt/incident-response/status.sh << 'EOF'
#!/bin/bash
# Incident Response System Status

echo "🚨 Security Incident Response System Status"
echo "==========================================="

# Check service status
if systemctl is-active --quiet incident-response; then
    echo "✅ Incident Response Service: RUNNING"
else
    echo "❌ Incident Response Service: STOPPED"
fi

# Check active incidents
ACTIVE_INCIDENTS=$(find /var/lib/incident-response/incidents -name "*.json" -mtime -1 | wc -l)
echo "📊 Active Incidents (last 24h): $ACTIVE_INCIDENTS"

# Check evidence collection
EVIDENCE_ITEMS=$(find /var/lib/incident-response/evidence -type d -name "incident-*" | wc -l)
echo "🔍 Evidence Collections: $EVIDENCE_ITEMS"

# Check quarantined files
QUARANTINED_FILES=$(find /var/lib/incident-response/quarantine -type f | wc -l)
echo "🔒 Quarantined Files: $QUARANTINED_FILES"

# Check recent alerts
RECENT_ALERTS=$(tail -n 100 /var/log/security-incidents.json 2>/dev/null | wc -l)
echo "🚨 Recent Alerts (last 100): $RECENT_ALERTS"

# Check audit system
if systemctl is-active --quiet auditd; then
    echo "✅ Audit System: RUNNING"
    AUDIT_RULES=$(auditctl -l | wc -l)
    echo "   Audit Rules: $AUDIT_RULES"
else
    echo "❌ Audit System: STOPPED"
fi

# Check containment capabilities
echo
echo "🛡️  Containment Capabilities:"
if command -v iptables >/dev/null 2>&1; then
    echo "   ✅ IP Blocking: Available"
    BLOCKED_IPS=$(iptables -L INPUT -n | grep DROP | wc -l)
    echo "   🚫 Currently Blocked IPs: $BLOCKED_IPS"
else
    echo "   ❌ IP Blocking: Not available"
fi

if [[ -d /var/lib/incident-response/quarantine ]]; then
    echo "   ✅ File Quarantine: Available"
else
    echo "   ❌ File Quarantine: Not available"
fi

# System resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
DISK_USAGE=$(df /var/lib/incident-response | tail -1 | awk '{print $5}' | sed 's/%//')

echo
echo "💻 System Resources:"
echo "   CPU Usage: ${CPU_USAGE}%"
echo "   Memory Usage: ${MEM_USAGE}%"
echo "   Incident Response Disk Usage: ${DISK_USAGE}%"

# Log file sizes
LOG_SIZE=$(du -sh /var/log/incident-response 2>/dev/null | cut -f1 || echo "0")
EVIDENCE_SIZE=$(du -sh /var/lib/incident-response/evidence 2>/dev/null | cut -f1 || echo "0")

echo
echo "📝 Storage Usage:"
echo "   Logs: $LOG_SIZE"
echo "   Evidence: $EVIDENCE_SIZE"
EOF

    # Management script
    cat > /opt/incident-response/manage.sh << 'EOF'
#!/bin/bash
# Incident Response System Management

case "$1" in
    start)
        echo "Starting Incident Response System..."
        systemctl start incident-response
        systemctl start auditd
        ;;
    stop)
        echo "Stopping Incident Response System..."
        systemctl stop incident-response
        ;;
    restart)
        echo "Restarting Incident Response System..."
        systemctl restart incident-response
        systemctl restart auditd
        ;;
    status)
        systemctl status incident-response
        ;;
    logs)
        journalctl -u incident-response -f
        ;;
    incidents)
        echo "Recent security incidents:"
        find /var/lib/incident-response/incidents -name "*.json" -mtime -7 | sort -r | head -10
        ;;
    evidence)
        echo "Evidence collections:"
        find /var/lib/incident-response/evidence -type d -name "incident-*" | sort -r | head -10
        ;;
    quarantine)
        echo "Quarantined files:"
        find /var/lib/incident-response/quarantine -type f | sort -r | head -20
        ;;
    monitor)
        /opt/incident-response/status.sh
        ;;
    test-incident)
        echo "Creating test security incident..."
        python3 /opt/incident-response/incident-response.py --test
        ;;
    blocked-ips)
        echo "Currently blocked IPs:"
        iptables -L INPUT -n | grep DROP | awk '{print $4}' | grep -v "0.0.0.0/0"
        ;;
    unblock-ip)
        if [[ -n "$2" ]]; then
            echo "Unblocking IP: $2"
            iptables -D INPUT -s "$2" -j DROP 2>/dev/null || echo "IP not found in blocked list"
        else
            echo "Usage: $0 unblock-ip <IP_ADDRESS>"
        fi
        ;;
    clean-evidence)
        echo "Cleaning old evidence (older than 90 days)..."
        find /var/lib/incident-response/evidence -type d -name "incident-*" -mtime +90 -exec rm -rf {} \; 2>/dev/null
        echo "Old evidence cleaned"
        ;;
    clean-quarantine)
        echo "Cleaning old quarantine files (older than 30 days)..."
        find /var/lib/incident-response/quarantine -type f -mtime +30 -delete
        echo "Old quarantine files cleaned"
        ;;
    audit-report)
        echo "Generating audit report..."
        if command -v aureport >/dev/null 2>&1; then
            aureport --summary
        else
            echo "Audit reporting tools not available"
        fi
        ;;
    forensic-timeline)
        if [[ -n "$2" ]]; then
            echo "Generating forensic timeline for incident: $2"
            INCIDENT_DIR="/var/lib/incident-response/evidence/incident-$2"
            if [[ -d "$INCIDENT_DIR" ]]; then
                echo "Evidence directory: $INCIDENT_DIR"
                ls -la "$INCIDENT_DIR"
            else
                echo "No evidence found for incident: $2"
            fi
        else
            echo "Usage: $0 forensic-timeline <INCIDENT_ID>"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|incidents|evidence|quarantine|monitor|test-incident|blocked-ips|unblock-ip|clean-evidence|clean-quarantine|audit-report|forensic-timeline}"
        echo
        echo "Commands:"
        echo "  start             - Start incident response system"
        echo "  stop              - Stop incident response system"
        echo "  restart           - Restart incident response system"
        echo "  status            - Show service status"
        echo "  logs              - View live logs"
        echo "  incidents         - List recent incidents"
        echo "  evidence          - List evidence collections"
        echo "  quarantine        - List quarantined files"
        echo "  monitor           - Show system status"
        echo "  test-incident     - Create test incident"
        echo "  blocked-ips       - Show blocked IP addresses"
        echo "  unblock-ip <ip>   - Unblock specific IP address"
        echo "  clean-evidence    - Clean old evidence files"
        echo "  clean-quarantine  - Clean old quarantine files"
        echo "  audit-report      - Generate audit report"
        echo "  forensic-timeline - Show forensic timeline for incident"
        exit 1
        ;;
esac
EOF

    # Make scripts executable
    chmod +x /opt/incident-response/status.sh
    chmod +x /opt/incident-response/manage.sh
    
    # Create symlink for easy access
    ln -sf /opt/incident-response/manage.sh /usr/local/bin/incident-manage
    
    log "Management scripts created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > /opt/incident-response/health-check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check script for Security Incident Response System
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_service_status():
    """Check if the incident response service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'incident-response'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_audit_system():
    """Check if audit system is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'auditd'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_containment_capabilities():
    """Check if containment tools are available"""
    tools = ['iptables', 'kill', 'usermod', 'auditctl']
    available_tools = []
    missing_tools = []
    
    for tool in tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode == 0:
            available_tools.append(tool)
        else:
            missing_tools.append(tool)
    
    return available_tools, missing_tools

def check_storage_space():
    """Check available storage space for evidence and logs"""
    issues = []
    
    # Check evidence directory space
    evidence_dir = Path('/var/lib/incident-response/evidence')
    if evidence_dir.exists():
        result = subprocess.run(['df', str(evidence_dir)], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                usage = lines[1].split()[4].rstrip('%')
                if int(usage) > 90:
                    issues.append(f"Evidence directory disk usage high: {usage}%")
    
    # Check log directory space
    log_dir = Path('/var/log/incident-response')
    if log_dir.exists():
        result = subprocess.run(['df', str(log_dir)], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                usage = lines[1].split()[4].rstrip('%')
                if int(usage) > 90:
                    issues.append(f"Log directory disk usage high: {usage}%")
    
    return issues

def check_configuration_files():
    """Check if configuration files exist and are readable"""
    config_files = [
        '/etc/incident-response/notifications.json',
        '/etc/incident-response/containment-policies.json'
    ]
    
    issues = []
    for config_file in config_files:
        if not os.path.exists(config_file):
            issues.append(f"Configuration file missing: {config_file}")
        elif not os.access(config_file, os.R_OK):
            issues.append(f"Configuration file not readable: {config_file}")
    
    return issues

def check_recent_activity():
    """Check for recent incident response activity"""
    incidents_dir = Path('/var/lib/incident-response/incidents')
    
    if not incidents_dir.exists():
        return False, "Incidents directory not found"
    
    # Check for recent incidents (within last 30 days)
    recent_incidents = []
    for incident_file in incidents_dir.glob('*.json'):
        mtime = datetime.fromtimestamp(incident_file.stat().st_mtime)
        if (datetime.now() - mtime).days <= 30:
            recent_incidents.append(incident_file)
    
    return True, f"Found {len(recent_incidents)} recent incidents"

def main():
    """Main health check function"""
    print("🚨 Security Incident Response System Health Check")
    print("=" * 55)
    
    all_good = True
    
    # Check service status
    if check_service_status():
        print("✅ Incident Response Service: RUNNING")
    else:
        print("❌ Incident Response Service: NOT RUNNING")
        all_good = False
    
    # Check audit system
    if check_audit_system():
        print("✅ Audit System: RUNNING")
    else:
        print("❌ Audit System: NOT RUNNING")
        all_good = False
    
    # Check containment capabilities
    available_tools, missing_tools = check_containment_capabilities()
    if not missing_tools:
        print("✅ Containment Tools: All Available")
    else:
        print(f"❌ Missing Containment Tools: {', '.join(missing_tools)}")
        all_good = False
    
    if available_tools:
        print(f"✅ Available Tools: {', '.join(available_tools)}")
    
    # Check storage space
    storage_issues = check_storage_space()
    if not storage_issues:
        print("✅ Storage Space: OK")
    else:
        print("⚠️  Storage Space: WARNINGS")
        for issue in storage_issues:
            print(f"   - {issue}")
    
    # Check configuration files
    config_issues = check_configuration_files()
    if not config_issues:
        print("✅ Configuration Files: OK")
    else:
        print("❌ Configuration Files: ISSUES FOUND")
        for issue in config_issues:
            print(f"   - {issue}")
        all_good = False
    
    # Check recent activity
    activity_ok, activity_msg = check_recent_activity()
    if activity_ok:
        print(f"✅ Recent Activity: {activity_msg}")
    else:
        print(f"⚠️  Recent Activity: {activity_msg}")
    
    # Check directory structure
    required_dirs = [
        '/var/lib/incident-response/incidents',
        '/var/lib/incident-response/evidence',
        '/var/lib/incident-response/quarantine',
        '/var/lib/incident-response/snapshots'
    ]
    
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    if not missing_dirs:
        print("✅ Directory Structure: OK")
    else:
        print(f"❌ Missing Directories: {', '.join(missing_dirs)}")
        all_good = False
    
    print("=" * 55)
    if all_good:
        print("🎉 Overall Status: HEALTHY")
        sys.exit(0)
    else:
        print("🚨 Overall Status: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x /opt/incident-response/health-check.py
    
    log "Health check script created"
}

# Main setup function
main() {
    log "Starting Security Incident Response System setup..."
    
    check_root
    install_dependencies
    setup_directories
    setup_notifications
    setup_containment_policies
    setup_audit_system
    create_systemd_service
    setup_log_rotation
    create_management_scripts
    create_health_check
    
    log "Setup completed successfully!"
    echo
    echo "🎉 Security Incident Response System is now configured!"
    echo
    echo "Next steps:"
    echo "1. Start the service: systemctl start incident-response"
    echo "2. Check status: incident-manage status"
    echo "3. Monitor incidents: incident-manage incidents"
    echo "4. Test the system: incident-manage test-incident"
    echo "5. Run health check: /opt/incident-response/health-check.py"
    echo
    echo "Management commands available via: incident-manage"
    echo
    echo "⚠️  IMPORTANT SECURITY NOTES:"
    echo "- Review and customize notification settings in /etc/incident-response/"
    echo "- Test incident response procedures regularly"
    echo "- Ensure proper access controls for evidence directories"
    echo "- Monitor system resources and clean old evidence regularly"
    echo "- Integrate with existing security tools and SIEM systems"
}

# Run main function
main "$@"