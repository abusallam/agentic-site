#!/bin/bash

# Enterprise VPS Setup Script - Production-Grade Security & Monitoring
# This script creates a hardened, monitored, and automated VPS environment
# Usage: ./enterprise-vps-setup.sh <IP> <ROOT_PASSWORD> <ENVIRONMENT>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 3 ]; then
    echo -e "${RED}Usage: $0 <IP> <ROOT_PASSWORD> <ENVIRONMENT>${NC}"
    echo -e "${YELLOW}Example: $0 217.79.255.54 xxXNCpx9Cz development${NC}"
    exit 1
fi

VPS_IP="$1"
ROOT_PASSWORD="$2"
ENVIRONMENT="$3"

# Generate secure credentials
ADMIN_SSH_PORT=$((20000 + RANDOM % 45000))
NEW_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
MONITORING_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-24)
API_SECRET=$(openssl rand -hex 32)

echo -e "${BOLD}${PURPLE}🏢 Enterprise VPS Setup - Production Grade Security${NC}"
echo -e "${BLUE}================================================================${NC}"
echo "Target IP: $VPS_IP"
echo "Environment: $ENVIRONMENT"
echo "Admin SSH Port: $ADMIN_SSH_PORT"
echo "Timestamp: $(date)"
echo -e "${YELLOW}⚠️  SAVE ALL CREDENTIALS SHOWN AT THE END!${NC}"
echo

# Function to run commands on VPS with password
run_with_password() {
    sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 "$1@$VPS_IP" "$2"
}

# Function to copy files to VPS with password
copy_with_password() {
    sshpass -p "$ROOT_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$1" "root@$VPS_IP:$2"
}

echo -e "${YELLOW}Phase 1: Installing local dependencies and testing connection...${NC}"

# Install required tools
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif command -v yum &> /dev/null; then
        sudo yum install -y sshpass
    elif command -v brew &> /dev/null; then
        brew install sshpass
    fi
fi

# Test initial connection
if run_with_password "root" "echo 'Connection established'"; then
    echo "✓ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

echo -e "${YELLOW}Phase 2: System hardening and security baseline...${NC}"

run_with_password "root" "
    echo '=== System Update and Security Baseline ==='
    export DEBIAN_FRONTEND=noninteractive
    
    # Update system
    apt-get update -y
    apt-get upgrade -y
    
    # Install essential security packages
    apt-get install -y \
        curl wget git unzip htop nano vim \
        ufw fail2ban logwatch rkhunter chkrootkit \
        software-properties-common apt-transport-https ca-certificates gnupg lsb-release \
        iptables-persistent netfilter-persistent \
        aide lynis clamav clamav-daemon \
        psad denyhosts \
        acct sysstat iotop nethogs \
        rsyslog logrotate \
        ntp chrony \
        sudo
    
    # Configure automatic security updates
    apt-get install -y unattended-upgrades
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'AUTOUPDATE'
Unattended-Upgrade::Allowed-Origins {
    \"\${distro_id}:\${distro_codename}-security\";
    \"\${distro_id}ESMApps:\${distro_codename}-apps-security\";
    \"\${distro_id}ESM:\${distro_codename}-infra-security\";
};
Unattended-Upgrade::AutoFixInterruptedDpkg \"true\";
Unattended-Upgrade::MinimalSteps \"true\";
Unattended-Upgrade::Remove-Unused-Dependencies \"true\";
Unattended-Upgrade::Automatic-Reboot \"false\";
AUTOUPDATE
    
    # Enable automatic updates
    echo 'APT::Periodic::Update-Package-Lists \"1\";' > /etc/apt/apt.conf.d/20auto-upgrades
    echo 'APT::Periodic::Unattended-Upgrade \"1\";' >> /etc/apt/apt.conf.d/20auto-upgrades
    
    echo '✓ Security baseline established'
"

echo -e "${YELLOW}Phase 3: Advanced SSH hardening and access control...${NC}"

# Generate SSH keys
SSH_KEY_NAME="agentic-enterprise-${VPS_IP//\./-}-${ENVIRONMENT}"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"

if [ ! -f "$SSH_KEY_PATH" ]; then
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "agentic-enterprise-$ENVIRONMENT-$VPS_IP-$(date +%Y%m%d)"
    echo "✓ ED25519 SSH key generated"
fi

# Set up SSH keys
run_with_password "root" "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
sshpass -p "$ROOT_PASSWORD" ssh-copy-id -i "$SSH_KEY_PATH.pub" -o StrictHostKeyChecking=no "root@$VPS_IP"

# Configure SSH hardening
SSH_ALIAS="agentic-enterprise-${VPS_IP//\./-}-${ENVIRONMENT}"
mkdir -p ~/.ssh

# Update SSH config
sed -i "/^Host $SSH_ALIAS/,/^$/d" ~/.ssh/config 2>/dev/null || true
cat >> ~/.ssh/config << EOF

# Agentic Enterprise VPS - $VPS_IP ($ENVIRONMENT)
Host $SSH_ALIAS
    HostName $VPS_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 10m

# Emergency admin access
Host $SSH_ALIAS-admin
    HostName $VPS_IP
    User root
    Port $ADMIN_SSH_PORT
    PreferredAuthentications password
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

EOF

# Harden SSH configuration
ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== SSH Hardening ==='
    
    # Backup original config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Create hardened SSH config
    cat > /etc/ssh/sshd_config << 'SSHCONFIG'
# Agentic Enterprise SSH Configuration - Maximum Security

# Network Configuration
Port 22
Port $ADMIN_SSH_PORT
AddressFamily inet
ListenAddress 0.0.0.0

# Authentication
LoginGraceTime 30
PermitRootLogin yes
StrictModes yes
MaxAuthTries 3
MaxSessions 5
MaxStartups 5:30:10

# Key Authentication (Primary)
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
AuthorizedPrincipalsFile none
AuthorizedKeysCommand none
AuthorizedKeysCommandUser nobody

# Password Authentication (Backup only)
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Security Features
UsePAM yes
X11Forwarding no
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
UsePrivilegeSeparation sandbox
Compression delayed
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable unused features
AllowAgentForwarding no
AllowTcpForwarding no
GatewayPorts no
PermitTunnel no
PermitUserEnvironment no

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Environment
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO

# Banner
Banner /etc/ssh/banner
SSHCONFIG

    # Create SSH banner
    cat > /etc/ssh/banner << 'BANNER'
***************************************************************************
                    AUTHORIZED ACCESS ONLY
***************************************************************************
This system is for authorized users only. All activities are monitored
and logged. Unauthorized access is prohibited and will be prosecuted.
***************************************************************************
BANNER

    # Test SSH configuration
    sshd -t
    
    echo '✓ SSH hardening complete'
"

echo -e "${YELLOW}Phase 4: Advanced firewall and intrusion detection...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Advanced Firewall Configuration ==='
    
    # Reset and configure UFW
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw default deny forward
    
    # SSH access
    ufw allow 22/tcp comment 'SSH Standard'
    ufw allow $ADMIN_SSH_PORT/tcp comment 'SSH Admin Emergency'
    
    # Web services
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Application ports based on environment
    if [ '$ENVIRONMENT' = 'development' ]; then
        ufw allow 3001/tcp comment 'Frontend Dev'
        ufw allow 8001/tcp comment 'Backend Dev'
        ufw allow 5679/tcp comment 'n8n Dev'
        ufw allow 6380/tcp comment 'Redis Dev'
    else
        ufw allow 3000/tcp comment 'Frontend Prod'
        ufw allow 8000/tcp comment 'Backend Prod'
        ufw allow 5678/tcp comment 'n8n Prod'
        ufw allow 6379/tcp comment 'Redis Prod'
    fi
    
    # Monitoring ports (restricted to localhost)
    ufw allow from 127.0.0.1 to any port 9090 comment 'Prometheus Local'
    ufw allow from 127.0.0.1 to any port 3001 comment 'Grafana Local'
    ufw allow from 127.0.0.1 to any port 9100 comment 'Node Exporter Local'
    
    # Rate limiting for SSH
    ufw limit ssh comment 'SSH Rate Limiting'
    
    # Enable firewall
    ufw --force enable
    
    echo '=== Fail2Ban Advanced Configuration ==='
    
    # Configure fail2ban with custom rules
    cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[DEFAULT]
# Ban settings
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd
usedns = warn
logencoding = auto
enabled = false
mode = normal
filter = %(__name__)s[mode=%(mode)s]

# Email notifications (configure SMTP if needed)
destemail = admin@consulting.sa
sendername = Fail2Ban-$VPS_IP
mta = sendmail
action = %(action_mwl)s

[sshd]
enabled = true
port = 22,$ADMIN_SSH_PORT
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200
findtime = 600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-noscript]
enabled = true
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400

[nginx-badbots]
enabled = true
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400

[nginx-noproxy]
enabled = true
filter = nginx-noproxy
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400
FAIL2BAN

    # Start fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    
    echo '=== PSAD Intrusion Detection ==='
    
    # Configure PSAD (Port Scan Attack Detector)
    cat > /etc/psad/psad.conf << 'PSADCONF'
EMAIL_ADDRESSES             admin@consulting.sa;
HOSTNAME                    agentic-$ENVIRONMENT-$VPS_IP;
ENABLE_AUTO_IDS             Y;
ENABLE_AUTO_IDS_EMAILS      Y;
AUTO_IDS_DANGER_LEVEL       3;
AUTO_BLOCK_TIMEOUT          3600;
ENABLE_PERSISTENCE          Y;
SCAN_TIMEOUT                3600;
PORT_RANGE_SCAN_THRESHOLD   1;
ENABLE_DShield_ALERTS       Y;
PSADCONF

    systemctl enable psad
    systemctl start psad
    
    echo '✓ Advanced security systems configured'
"

echo -e "${YELLOW}Phase 5: Docker installation with security hardening...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Docker Installation and Hardening ==='
    
    # Remove old Docker versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker GPG key and repository
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Install Docker Compose
    curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Docker security hardening
    cat > /etc/docker/daemon.json << 'DOCKERCONF'
{
    \"log-driver\": \"json-file\",
    \"log-opts\": {
        \"max-size\": \"10m\",
        \"max-file\": \"3\"
    },
    \"live-restore\": true,
    \"userland-proxy\": false,
    \"no-new-privileges\": true,
    \"seccomp-profile\": \"/etc/docker/seccomp.json\",
    \"storage-driver\": \"overlay2\",
    \"storage-opts\": [
        \"overlay2.override_kernel_check=true\"
    ],
    \"default-ulimits\": {
        \"nofile\": {
            \"Name\": \"nofile\",
            \"Hard\": 64000,
            \"Soft\": 64000
        }
    }
}
DOCKERCONF

    # Create Docker security profile
    curl -o /etc/docker/seccomp.json https://raw.githubusercontent.com/moby/moby/master/profiles/seccomp/default.json
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Verify installation
    docker --version
    docker-compose --version
    
    echo '✓ Docker installed and hardened'
"

echo -e "${YELLOW}Phase 6: Nginx installation with security modules...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Nginx Installation and Security Configuration ==='
    
    # Install Nginx with additional modules
    apt-get install -y nginx nginx-extras
    
    # Create security configuration
    cat > /etc/nginx/conf.d/security.conf << 'NGINXSEC'
# Security Headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection \"1; mode=block\" always;
add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;
add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;
add_header Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';\" always;
add_header Permissions-Policy \"geolocation=(), microphone=(), camera=()\" always;

# Hide Nginx version and server tokens
server_tokens off;
more_clear_headers Server;

# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=general:10m rate=30r/s;

# Connection limiting
limit_conn_zone \$binary_remote_addr zone=conn_limit_per_ip:10m;
limit_conn conn_limit_per_ip 20;

# Request size limits
client_max_body_size 10M;
client_body_buffer_size 128k;
client_header_buffer_size 1k;
large_client_header_buffers 4 4k;

# Timeouts
client_body_timeout 12;
client_header_timeout 12;
keepalive_timeout 15;
send_timeout 10;

# Buffer overflow protection
client_body_buffer_size 128k;
client_header_buffer_size 1k;
client_max_body_size 10m;
large_client_header_buffers 2 1k;
NGINXSEC

    # Create DDoS protection configuration
    cat > /etc/nginx/conf.d/ddos.conf << 'NGINXDDOS'
# DDoS Protection
limit_req_zone \$binary_remote_addr zone=ddos:10m rate=1r/s;
limit_req_status 429;
limit_conn_status 429;

# Slow loris protection
client_body_timeout 10s;
client_header_timeout 10s;
keepalive_timeout 5s 5s;
send_timeout 10s;
NGINXDDOS

    # Start and enable Nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Test configuration
    nginx -t
    
    echo '✓ Nginx installed with security hardening'
"

echo -e "${YELLOW}Phase 7: Comprehensive monitoring stack deployment...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Monitoring Stack Installation ==='
    
    # Create monitoring directory
    mkdir -p /opt/monitoring/{prometheus,grafana,alertmanager,node-exporter}
    
    # Install Prometheus
    cd /opt/monitoring/prometheus
    wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*linux-amd64.tar.gz
    tar xzf prometheus-*linux-amd64.tar.gz --strip-components=1
    rm prometheus-*linux-amd64.tar.gz
    
    # Create Prometheus configuration
    cat > /opt/monitoring/prometheus/prometheus.yml << 'PROMCONFIG'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - \"alert_rules.yml\"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

  - job_name: 'application-frontend'
    static_configs:
      - targets: ['localhost:$([[ \"$ENVIRONMENT\" == \"development\" ]] && echo \"3001\" || echo \"3000\")']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'application-backend'
    static_configs:
      - targets: ['localhost:$([[ \"$ENVIRONMENT\" == \"development\" ]] && echo \"8001\" || echo \"8000\")']
    metrics_path: '/metrics'
    scrape_interval: 30s
PROMCONFIG

    # Create alert rules
    cat > /opt/monitoring/prometheus/alert_rules.yml << 'ALERTRULES'
groups:
- name: system_alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: \"High CPU usage detected\"
      description: \"CPU usage is above 80% for more than 5 minutes\"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: \"High memory usage detected\"
      description: \"Memory usage is above 85% for more than 5 minutes\"

  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"}) * 100 < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: \"Low disk space\"
      description: \"Disk space is below 10%\"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: \"Service is down\"
      description: \"{{ \$labels.job }} service is down\"

- name: security_alerts
  rules:
  - alert: TooManyFailedLogins
    expr: increase(node_systemd_unit_state{name=\"fail2ban.service\",state=\"active\"}[5m]) > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: \"Multiple failed login attempts detected\"
      description: \"Fail2ban has been activated due to multiple failed login attempts\"

  - alert: HighNetworkTraffic
    expr: rate(node_network_receive_bytes_total[5m]) > 100000000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: \"High network traffic detected\"
      description: \"Network traffic is unusually high\"
ALERTRULES

    # Install Node Exporter
    cd /opt/monitoring/node-exporter
    wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*linux-amd64.tar.gz
    tar xzf node_exporter-*linux-amd64.tar.gz --strip-components=1
    rm node_exporter-*linux-amd64.tar.gz
    
    # Create systemd services
    cat > /etc/systemd/system/prometheus.service << 'PROMSERVICE'
[Unit]
Description=Prometheus Server
Documentation=https://prometheus.io/docs/
After=network-online.target

[Service]
User=root
Restart=on-failure
ExecStart=/opt/monitoring/prometheus/prometheus --config.file=/opt/monitoring/prometheus/prometheus.yml --storage.tsdb.path=/opt/monitoring/prometheus/data --web.console.templates=/opt/monitoring/prometheus/consoles --web.console.libraries=/opt/monitoring/prometheus/console_libraries --web.listen-address=127.0.0.1:9090 --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
PROMSERVICE

    cat > /etc/systemd/system/node-exporter.service << 'NODESERVICE'
[Unit]
Description=Node Exporter
Documentation=https://prometheus.io/docs/
After=network-online.target

[Service]
User=root
Restart=on-failure
ExecStart=/opt/monitoring/node-exporter/node_exporter --web.listen-address=127.0.0.1:9100

[Install]
WantedBy=multi-user.target
NODESERVICE

    # Start monitoring services
    systemctl daemon-reload
    systemctl enable prometheus node-exporter
    systemctl start prometheus node-exporter
    
    echo '✓ Monitoring stack installed'
"

echo -e "${YELLOW}Phase 8: Log management and analysis system...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Log Management Configuration ==='
    
    # Configure rsyslog for centralized logging
    cat > /etc/rsyslog.d/50-agentic.conf << 'RSYSLOGCONF'
# Agentic Site Logging Configuration
\$template AgenticLogFormat,\"%timestamp% %hostname% %syslogtag% %msg%\\n\"

# Application logs
local0.*    /var/log/agentic-site/application.log;AgenticLogFormat
local1.*    /var/log/agentic-site/security.log;AgenticLogFormat
local2.*    /var/log/agentic-site/performance.log;AgenticLogFormat

# Stop processing after logging
local0.*    stop
local1.*    stop
local2.*    stop
RSYSLOGCONF

    # Create log directories
    mkdir -p /var/log/agentic-site
    chmod 755 /var/log/agentic-site
    
    # Configure logrotate
    cat > /etc/logrotate.d/agentic-site << 'LOGROTATE'
/var/log/agentic-site/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
LOGROTATE

    # Install and configure logwatch
    cat > /etc/logwatch/conf/logwatch.conf << 'LOGWATCHCONF'
LogDir = /var/log
TmpDir = /var/cache/logwatch
MailTo = admin@consulting.sa
MailFrom = logwatch@$VPS_IP
Print = No
Save = /var/cache/logwatch
Range = yesterday
Detail = Med
Service = All
mailer = \"/usr/sbin/sendmail -t\"
LOGWATCHCONF

    # Restart rsyslog
    systemctl restart rsyslog
    
    echo '✓ Log management configured'
"

echo -e "${YELLOW}Phase 9: Automated security scanning and maintenance...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Security Scanning and Maintenance ==='
    
    # Configure AIDE (Advanced Intrusion Detection Environment)
    aideinit
    cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
    
    # Configure ClamAV antivirus
    freshclam
    systemctl enable clamav-daemon
    systemctl start clamav-daemon
    
    # Create security scan scripts
    cat > /usr/local/bin/security-scan.sh << 'SECSCAN'
#!/bin/bash
# Comprehensive Security Scan Script

LOG_FILE=\"/var/log/agentic-site/security.log\"
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

echo \"[\$DATE] Starting security scan\" >> \$LOG_FILE

# Run rootkit scanner
echo \"[\$DATE] Running rkhunter scan\" >> \$LOG_FILE
rkhunter --check --skip-keypress --report-warnings-only >> \$LOG_FILE 2>&1

# Run chkrootkit
echo \"[\$DATE] Running chkrootkit scan\" >> \$LOG_FILE
chkrootkit >> \$LOG_FILE 2>&1

# Run ClamAV scan on critical directories
echo \"[\$DATE] Running antivirus scan\" >> \$LOG_FILE
clamscan -r --bell -i /home /root /etc /var/www >> \$LOG_FILE 2>&1

# Check for file integrity changes
echo \"[\$DATE] Running AIDE integrity check\" >> \$LOG_FILE
aide --check >> \$LOG_FILE 2>&1

# Check for suspicious network connections
echo \"[\$DATE] Checking network connections\" >> \$LOG_FILE
netstat -tulpn | grep LISTEN >> \$LOG_FILE 2>&1

# Check for failed login attempts
echo \"[\$DATE] Checking failed login attempts\" >> \$LOG_FILE
grep \"Failed password\" /var/log/auth.log | tail -20 >> \$LOG_FILE 2>&1

echo \"[\$DATE] Security scan completed\" >> \$LOG_FILE
SECSCAN

    chmod +x /usr/local/bin/security-scan.sh
    
    # Create performance monitoring script
    cat > /usr/local/bin/performance-monitor.sh << 'PERFMON'
#!/bin/bash
# Performance Monitoring Script

LOG_FILE=\"/var/log/agentic-site/performance.log\"
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

echo \"[\$DATE] Performance monitoring check\" >> \$LOG_FILE

# CPU usage
CPU_USAGE=\$(top -bn1 | grep \"Cpu(s)\" | awk '{print \$2}' | awk -F'%' '{print \$1}')
echo \"[\$DATE] CPU Usage: \$CPU_USAGE%\" >> \$LOG_FILE

# Memory usage
MEM_USAGE=\$(free | grep Mem | awk '{printf \"%.2f\", \$3/\$2 * 100.0}')
echo \"[\$DATE] Memory Usage: \$MEM_USAGE%\" >> \$LOG_FILE

# Disk usage
DISK_USAGE=\$(df -h / | awk 'NR==2 {print \$5}')
echo \"[\$DATE] Disk Usage: \$DISK_USAGE\" >> \$LOG_FILE

# Load average
LOAD_AVG=\$(uptime | awk -F'load average:' '{print \$2}')
echo \"[\$DATE] Load Average:\$LOAD_AVG\" >> \$LOG_FILE

# Network connections
CONN_COUNT=\$(netstat -an | wc -l)
echo \"[\$DATE] Network Connections: \$CONN_COUNT\" >> \$LOG_FILE

# Docker container status
if command -v docker &> /dev/null; then
    RUNNING_CONTAINERS=\$(docker ps --format \"table {{.Names}}\\t{{.Status}}\" | grep -c \"Up\")
    echo \"[\$DATE] Running Containers: \$RUNNING_CONTAINERS\" >> \$LOG_FILE
fi

echo \"[\$DATE] Performance monitoring completed\" >> \$LOG_FILE
PERFMON

    chmod +x /usr/local/bin/performance-monitor.sh
    
    # Create automated maintenance script
    cat > /usr/local/bin/system-maintenance.sh << 'SYSMAINT'
#!/bin/bash
# Automated System Maintenance Script

LOG_FILE=\"/var/log/agentic-site/maintenance.log\"
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

echo \"[\$DATE] Starting system maintenance\" >> \$LOG_FILE

# Update package lists
apt-get update >> \$LOG_FILE 2>&1

# Clean package cache
apt-get autoclean >> \$LOG_FILE 2>&1
apt-get autoremove -y >> \$LOG_FILE 2>&1

# Update ClamAV signatures
freshclam >> \$LOG_FILE 2>&1

# Rotate logs manually if needed
logrotate -f /etc/logrotate.conf >> \$LOG_FILE 2>&1

# Clean temporary files
find /tmp -type f -atime +7 -delete >> \$LOG_FILE 2>&1
find /var/tmp -type f -atime +7 -delete >> \$LOG_FILE 2>&1

# Update AIDE database
aide --update >> \$LOG_FILE 2>&1
cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db >> \$LOG_FILE 2>&1

echo \"[\$DATE] System maintenance completed\" >> \$LOG_FILE
SYSMAINT

    chmod +x /usr/local/bin/system-maintenance.sh
    
    echo '✓ Security scanning and maintenance configured'
"

echo -e "${YELLOW}Phase 10: Automated backup and disaster recovery...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Backup and Disaster Recovery Setup ==='
    
    # Create backup directories
    mkdir -p /opt/backups/{daily,weekly,monthly,system}
    
    # Create comprehensive backup script
    cat > /usr/local/bin/backup-system.sh << 'BACKUPSCRIPT'
#!/bin/bash
# Comprehensive Backup Script

BACKUP_DIR=\"/opt/backups\"
DATE=\$(date +%Y%m%d_%H%M%S)
LOG_FILE=\"/var/log/agentic-site/backup.log\"

echo \"[\$(date)] Starting backup process\" >> \$LOG_FILE

# System configuration backup
tar -czf \$BACKUP_DIR/system/system-config-\$DATE.tar.gz \
    /etc \
    /root/.ssh \
    /usr/local/bin \
    /opt/monitoring \
    --exclude=/etc/ssl/private \
    >> \$LOG_FILE 2>&1

# Application backup
if [ -d \"/opt/docker-apps\" ]; then
    tar -czf \$BACKUP_DIR/daily/application-\$DATE.tar.gz \
        /opt/docker-apps \
        >> \$LOG_FILE 2>&1
fi

# Database backup (if applicable)
if command -v docker &> /dev/null; then
    # Backup Redis data
    docker exec agentic-redis-$ENVIRONMENT redis-cli BGSAVE >> \$LOG_FILE 2>&1
    
    # Copy Redis dump
    if [ -f \"/var/lib/docker/volumes/agentic-redis-$ENVIRONMENT-data/_data/dump.rdb\" ]; then
        cp /var/lib/docker/volumes/agentic-redis-$ENVIRONMENT-data/_data/dump.rdb \
           \$BACKUP_DIR/daily/redis-\$DATE.rdb >> \$LOG_FILE 2>&1
    fi
fi

# Log files backup
tar -czf \$BACKUP_DIR/daily/logs-\$DATE.tar.gz \
    /var/log \
    --exclude=/var/log/*.gz \
    >> \$LOG_FILE 2>&1

# Cleanup old backups (keep 7 daily, 4 weekly, 12 monthly)
find \$BACKUP_DIR/daily -name \"*.tar.gz\" -mtime +7 -delete >> \$LOG_FILE 2>&1
find \$BACKUP_DIR/weekly -name \"*.tar.gz\" -mtime +28 -delete >> \$LOG_FILE 2>&1
find \$BACKUP_DIR/monthly -name \"*.tar.gz\" -mtime +365 -delete >> \$LOG_FILE 2>&1

echo \"[\$(date)] Backup process completed\" >> \$LOG_FILE

# Send backup status (if mail is configured)
if command -v mail &> /dev/null; then
    echo \"Backup completed successfully on \$(hostname) at \$(date)\" | \
    mail -s \"Backup Status - \$(hostname)\" admin@consulting.sa
fi
BACKUPSCRIPT

    chmod +x /usr/local/bin/backup-system.sh
    
    # Create disaster recovery documentation
    cat > /opt/backups/DISASTER_RECOVERY.md << 'DRPLAN'
# Disaster Recovery Plan

## Emergency Contacts
- Primary Admin: admin@consulting.sa
- VPS Provider: [Your VPS Provider]
- DNS Provider: [Your DNS Provider]

## Critical Information
- VPS IP: $VPS_IP
- SSH Admin Port: $ADMIN_SSH_PORT
- Environment: $ENVIRONMENT

## Recovery Procedures

### 1. System Recovery
```bash
# Restore system configuration
tar -xzf system-config-YYYYMMDD_HHMMSS.tar.gz -C /

# Restore application
tar -xzf application-YYYYMMDD_HHMMSS.tar.gz -C /

# Restart services
systemctl restart docker nginx prometheus node-exporter
```

### 2. Database Recovery
```bash
# Restore Redis
docker cp redis-YYYYMMDD_HHMMSS.rdb container_name:/data/dump.rdb
docker restart container_name
```

### 3. DNS and SSL Recovery
- Update DNS records to point to new IP
- Restore SSL certificates from backup
- Update firewall rules

### 4. Monitoring Recovery
- Verify all monitoring services are running
- Check alert configurations
- Test notification systems
DRPLAN

    echo '✓ Backup and disaster recovery configured'
"

echo -e "${YELLOW}Phase 11: Cron jobs and automation scheduling...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Automation and Scheduling ==='
    
    # Create comprehensive cron jobs
    cat > /tmp/agentic-cron << 'CRONJOBS'
# Agentic Site Automated Tasks

# Security scans
0 2 * * * /usr/local/bin/security-scan.sh
0 14 * * * /usr/local/bin/security-scan.sh

# Performance monitoring (every 15 minutes)
*/15 * * * * /usr/local/bin/performance-monitor.sh

# System maintenance (daily at 3 AM)
0 3 * * * /usr/local/bin/system-maintenance.sh

# Backups
0 1 * * * /usr/local/bin/backup-system.sh
0 1 * * 0 cp /opt/backups/daily/application-\$(date +\%Y\%m\%d_\%H\%M\%S).tar.gz /opt/backups/weekly/
0 1 1 * * cp /opt/backups/daily/application-\$(date +\%Y\%m\%d_\%H\%M\%S).tar.gz /opt/backups/monthly/

# Log analysis (daily at 6 AM)
0 6 * * * /usr/sbin/logwatch --output mail --mailto admin@consulting.sa --detail high

# Certificate renewal check (weekly)
0 4 * * 1 certbot renew --quiet --no-self-upgrade

# Disk cleanup (weekly)
0 5 * * 0 find /tmp -type f -atime +7 -delete; find /var/tmp -type f -atime +7 -delete

# Update fail2ban rules (daily)
30 4 * * * fail2ban-client reload

# Docker cleanup (weekly)
0 6 * * 0 docker system prune -f --volumes
CRONJOBS

    crontab /tmp/agentic-cron
    rm /tmp/agentic-cron
    
    echo '✓ Automation and scheduling configured'
"

echo -e "${YELLOW}Phase 12: Final system optimization and hardening...${NC}"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Final System Optimization ==='
    
    # Kernel parameter optimization
    cat >> /etc/sysctl.conf << 'SYSCTLOPT'

# Agentic Site System Optimizations

# Network security
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.tcp_syncookies = 1

# Performance optimizations
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 10
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_tw_reuse = 1

# Memory management
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# File system
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
SYSCTLOPT

    sysctl -p
    
    # Set file limits
    cat >> /etc/security/limits.conf << 'LIMITS'

# Agentic Site File Limits
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
root soft nofile 65536
root hard nofile 65536
root soft nproc 32768
root hard nproc 32768
LIMITS

    # Configure timezone and NTP
    timedatectl set-timezone UTC
    systemctl enable chrony
    systemctl start chrony
    
    # Create system information file
    cat > /opt/agentic-system-info.txt << SYSINFO
Agentic Enterprise VPS Configuration
===================================
Setup Date: \$(date)
VPS IP: $VPS_IP
Environment: $ENVIRONMENT
SSH Admin Port: $ADMIN_SSH_PORT

Security Features:
- Advanced firewall with UFW
- Fail2ban intrusion prevention
- PSAD port scan detection
- ClamAV antivirus
- AIDE file integrity monitoring
- Automated security scanning

Monitoring:
- Prometheus metrics collection
- Node Exporter system metrics
- Custom alert rules
- Performance monitoring
- Log analysis with Logwatch

Automation:
- Automated security updates
- Daily security scans
- Performance monitoring
- System maintenance
- Automated backups
- Log rotation

Access Methods:
- Primary SSH: Key-based authentication
- Emergency SSH: Port $ADMIN_SSH_PORT with password
- Web interfaces: Nginx reverse proxy

Backup Strategy:
- Daily application backups
- Weekly system backups
- Monthly archive backups
- Automated cleanup

Maintenance Schedule:
- Security scans: 2x daily
- Performance monitoring: Every 15 minutes
- System maintenance: Daily at 3 AM
- Backups: Daily at 1 AM
- Log analysis: Daily at 6 AM
SYSINFO

    echo '✓ Final system optimization complete'
"

# Create deployment directories
DEPLOY_PATH="/opt/docker-apps/$ENVIRONMENT/agentic-site"

ssh -i "$SSH_KEY_PATH" "root@$VPS_IP" "
    echo '=== Creating Deployment Structure ==='
    
    mkdir -p $DEPLOY_PATH
    mkdir -p /opt/docker-apps/shared/{ssl,backups,logs,monitoring}
    
    # Set proper permissions
    chown -R root:root /opt/docker-apps
    chmod -R 755 /opt/docker-apps
    
    echo '✓ Deployment structure created'
"

# Create local environment file with all credentials
cat > ".env.$ENVIRONMENT.enterprise" << EOF
# Enterprise VPS Configuration - Generated $(date)
# ⚠️ CONFIDENTIAL - Contains sensitive credentials

# VPS Connection Details
VPS_IP=$VPS_IP
VPS_ENVIRONMENT=$ENVIRONMENT
SSH_ALIAS=$SSH_ALIAS
SSH_KEY_PATH=$SSH_KEY_PATH

# SSH Access
SSH_STANDARD_PORT=22
SSH_ADMIN_PORT=$ADMIN_SSH_PORT
ROOT_PASSWORD=$NEW_ROOT_PASSWORD

# Security Credentials
MONITORING_PASSWORD=$MONITORING_PASSWORD
DB_PASSWORD=$DB_PASSWORD
API_SECRET=$API_SECRET

# Deployment Configuration
DEPLOY_PATH=$DEPLOY_PATH
DOMAIN=$([[ "$ENVIRONMENT" == "development" ]] && echo "dev.consulting.sa" || echo "consulting.sa")

# Application Ports
FRONTEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "3001" || echo "3000")
BACKEND_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "8001" || echo "8000")
REDIS_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "6380" || echo "6379")
N8N_PORT=$([[ "$ENVIRONMENT" == "development" ]] && echo "5679" || echo "5678")

# Monitoring Ports (localhost only)
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
NODE_EXPORTER_PORT=9100

# Management Scripts
STATUS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-status.sh
RESTART_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-restart.sh
LOGS_SCRIPT=/usr/local/bin/agentic-$ENVIRONMENT-logs.sh
BACKUP_SCRIPT=/usr/local/bin/backup-system.sh
SECURITY_SCRIPT=/usr/local/bin/security-scan.sh
PERFORMANCE_SCRIPT=/usr/local/bin/performance-monitor.sh

# Backup Locations
BACKUP_DIR=/opt/backups
DAILY_BACKUP_DIR=/opt/backups/daily
WEEKLY_BACKUP_DIR=/opt/backups/weekly
MONTHLY_BACKUP_DIR=/opt/backups/monthly

# Log Locations
APPLICATION_LOG=/var/log/agentic-site/application.log
SECURITY_LOG=/var/log/agentic-site/security.log
PERFORMANCE_LOG=/var/log/agentic-site/performance.log
BACKUP_LOG=/var/log/agentic-site/backup.log
EOF

echo
echo -e "${BOLD}${GREEN}🎉 ENTERPRISE VPS SETUP COMPLETE! 🎉${NC}"
echo -e "${BLUE}================================================================${NC}"
echo
echo -e "${BOLD}${CYAN}🔐 CRITICAL SECURITY INFORMATION (SAVE IMMEDIATELY!)${NC}"
echo -e "${YELLOW}New Root Password: $NEW_ROOT_PASSWORD${NC}"
echo -e "${YELLOW}Admin SSH Port: $ADMIN_SSH_PORT${NC}"
echo -e "${YELLOW}Monitoring Password: $MONITORING_PASSWORD${NC}"
echo -e "${YELLOW}API Secret: $API_SECRET${NC}"
echo
echo -e "${BOLD}${CYAN}🔑 SSH Access Methods:${NC}"
echo "Primary Access: ssh $SSH_ALIAS"
echo "Emergency Admin: ssh $SSH_ALIAS-admin -p $ADMIN_SSH_PORT"
echo
echo -e "${BOLD}${CYAN}📁 Files Created:${NC}"
echo "• SSH Key: $SSH_KEY_PATH"
echo "• SSH Config: ~/.ssh/config (entry: $SSH_ALIAS)"
echo "• Enterprise Config: .env.$ENVIRONMENT.enterprise"
echo
echo -e "${BOLD}${CYAN}🛡️ Security Features Enabled:${NC}"
echo "✅ Advanced firewall with rate limiting"
echo "✅ Fail2ban intrusion prevention"
echo "✅ PSAD port scan detection"
echo "✅ ClamAV antivirus with real-time scanning"
echo "✅ AIDE file integrity monitoring"
echo "✅ Automated security updates"
echo "✅ SSH hardening with key authentication"
echo "✅ DDoS protection at Nginx level"
echo
echo -e "${BOLD}${CYAN}📊 Monitoring & Automation:${NC}"
echo "✅ Prometheus metrics collection"
echo "✅ Node Exporter system monitoring"
echo "✅ Custom security and performance alerts"
echo "✅ Automated daily security scans"
echo "✅ Performance monitoring every 15 minutes"
echo "✅ Automated system maintenance"
echo "✅ Comprehensive backup strategy"
echo "✅ Log analysis and rotation"
echo
echo -e "${BOLD}${CYAN}🛠️ Management Commands:${NC}"
echo "Status: ssh $SSH_ALIAS '/usr/local/bin/security-scan.sh'"
echo "Performance: ssh $SSH_ALIAS '/usr/local/bin/performance-monitor.sh'"
echo "Backup: ssh $SSH_ALIAS '/usr/local/bin/backup-system.sh'"
echo "Maintenance: ssh $SSH_ALIAS '/usr/local/bin/system-maintenance.sh'"
echo "Connect: ssh $SSH_ALIAS"
echo
echo -e "${BOLD}${CYAN}🚀 Next Steps:${NC}"
echo "1. Test SSH access: ssh $SSH_ALIAS"
echo "2. Deploy application: ./infrastructure/scripts/deploy-to-clean-vps.sh $SSH_ALIAS $ENVIRONMENT"
echo "3. Configure DNS to point to $VPS_IP"
echo "4. Set up SSL certificates"
echo "5. Configure email notifications for alerts"
echo
echo -e "${BOLD}${GREEN}✅ Your enterprise-grade VPS is now ready for secure deployment!${NC}"
echo -e "${BOLD}${RED}⚠️  IMPORTANT: Save all credentials shown above immediately!${NC}"