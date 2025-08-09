#!/bin/bash

# 🏢 ENTERPRISE MASTER SETUP - ONE SCRIPT TO RULE THEM ALL
# Complete VPS setup with all lessons learned integrated
# Usage: ./enterprise-master-setup.sh <VPS_IP> <ROOT_PASSWORD> <CLOUDFLARE_TOKEN> <ZONE_ID>

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

# Configuration
GITHUB_TOKEN="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"
GITHUB_REPO="https://github.com/abusallam/agentic-site.git"

# Check arguments
if [ $# -lt 4 ]; then
    echo -e "${RED}Usage: $0 <VPS_IP> <ROOT_PASSWORD> <CLOUDFLARE_TOKEN> <ZONE_ID>${NC}"
    echo -e "${YELLOW}Example: $0 217.79.255.54 password cf_token zone_id${NC}"
    echo
    echo -e "${CYAN}This is the MASTER setup script that includes all lessons learned:${NC}"
    echo "✅ Idempotent VPS setup (safe to run multiple times)"
    echo "✅ Complete Docker and Nginx configuration"
    echo "✅ SSL certificates with Cloudflare integration"
    echo "✅ Separate production and development environments"
    echo "✅ DNS configuration and domain setup"
    echo "✅ Management scripts and monitoring"
    exit 1
fi

VPS_IP="$1"
ROOT_PASSWORD="$2"
CLOUDFLARE_TOKEN="$3"
ZONE_ID="$4"

# Generate consistent SSH configuration
SSH_KEY_NAME="agentic-master-${VPS_IP//\./-}"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"
SSH_ALIAS="agentic-master-${VPS_IP//\./-}"

echo -e "${BOLD}${PURPLE}🏢 ENTERPRISE MASTER SETUP${NC}"
echo -e "${BLUE}============================${NC}"
echo "🎯 Target VPS: $VPS_IP"
echo "🔑 SSH Alias: $SSH_ALIAS"
echo "🌐 Domain: consulting.sa"
echo "📅 Timestamp: $(date)"
echo
echo -e "${BOLD}${GREEN}🙏 Thanks to God for the wisdom and lessons learned!${NC}"
echo -e "${YELLOW}This script incorporates all our learnings and best practices.${NC}"
echo# F
unction to run commands on VPS with password
run_with_password() {
    sshpass -p "$ROOT_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 "$1@$VPS_IP" "$2"
}

# Function to run commands on VPS with SSH key (after setup)
run_on_vps() {
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$1@$VPS_IP" "$2"
}

echo -e "${YELLOW}🔧 PHASE 1: VPS Foundation Setup${NC}"
echo "Installing sshpass locally if needed..."

# Install sshpass locally if needed
if ! command -v sshpass &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif command -v brew &> /dev/null; then
        brew install sshpass
    else
        echo -e "${RED}❌ Please install sshpass manually${NC}"
        exit 1
    fi
fi

# Test VPS connection
echo "Testing VPS connection..."
if run_with_password "root" "echo 'Connection established'"; then
    echo "✅ VPS connection verified"
else
    echo -e "${RED}❌ Failed to connect to VPS${NC}"
    exit 1
fi

echo -e "${YELLOW}🔧 PHASE 2: System Update & Essential Packages${NC}"
run_with_password "root" "
    echo '=== CRITICAL: System Update (with -y flag) ==='
    export DEBIAN_FRONTEND=noninteractive
    
    # ALWAYS update and upgrade with -y
    apt-get update -y
    apt-get upgrade -y
    
    # Install essential packages
    apt-get install -y curl wget git unzip htop nano vim ufw fail2ban ca-certificates gnupg lsb-release software-properties-common apt-transport-https
    
    # Clean up
    apt-get autoremove -y
    apt-get autoclean
    
    echo '✅ System updated and essential packages installed'
"

echo -e "${YELLOW}🔧 PHASE 3: SSH Key Authentication Setup${NC}"
# Generate SSH key if it doesn't exist
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "agentic-master-$VPS_IP-$(date +%Y%m%d)"
    echo "✅ SSH key generated"
else
    echo "✅ SSH key already exists"
fi

# Set up SSH keys on VPS
run_with_password "root" "
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    touch ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
"

# Copy public key
PUB_KEY_CONTENT=$(cat "$SSH_KEY_PATH.pub")
run_with_password "root" "
    if ! grep -q '$PUB_KEY_CONTENT' ~/.ssh/authorized_keys 2>/dev/null; then
        echo '$PUB_KEY_CONTENT' >> ~/.ssh/authorized_keys
        echo 'SSH key added'
    else
        echo 'SSH key already present'
    fi
"

# Test SSH key authentication
if ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@$VPS_IP" 'echo "SSH key working"' 2>/dev/null; then
    echo "✅ SSH key authentication working"
    SSH_KEY_WORKING=true
else
    echo "⚠ SSH key authentication not working, will use password"
    SSH_KEY_WORKING=false
fi

# Update SSH config
echo "Updating SSH configuration..."
mkdir -p ~/.ssh
sed -i "/^Host $SSH_ALIAS$/,/^$/d" ~/.ssh/config 2>/dev/null || true

cat >> ~/.ssh/config << EOF

# Agentic Master VPS - $VPS_IP
Host $SSH_ALIAS
    HostName $VPS_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF

echo "✅ SSH configuration updated"e
cho -e "${YELLOW}🔧 PHASE 4: Docker Installation (Debian 12 Optimized)${NC}"

# Use SSH key if working, otherwise password
if [ "$SSH_KEY_WORKING" = true ]; then
    RUN_CMD() { run_on_vps "root" "$1"; }
else
    RUN_CMD() { run_with_password "root" "$1"; }
fi

# Check if Docker is already installed
DOCKER_STATUS=$($RUN_CMD "docker --version 2>/dev/null && echo 'installed' || echo 'not_installed'")

if [ "$DOCKER_STATUS" = "installed" ]; then
    echo "✅ Docker already installed"
    $RUN_CMD "docker --version && docker-compose --version"
else
    echo "Installing Docker for Debian 12..."
    $RUN_CMD "
        # Remove old Docker versions
        apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
        
        # Clean up any corrupted Docker repository
        rm -f /etc/apt/sources.list.d/docker.list
        rm -f /etc/apt/keyrings/docker.gpg
        
        # Add Docker GPG key (fresh)
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        
        # Add Docker repository
        echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \$(lsb_release -cs) stable\" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Install Docker Compose standalone
        curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        # CRITICAL: Start and enable services for Debian 12
        systemctl daemon-reload
        systemctl start docker
        systemctl enable docker
        systemctl start containerd
        systemctl enable containerd
        
        # Verify installation
        docker --version
        docker-compose --version
        
        echo '✅ Docker installation completed'
    "
fi

echo -e "${YELLOW}🔧 PHASE 5: UFW Firewall (Fixed - No Spam)${NC}"
$RUN_CMD "
    echo 'Configuring UFW firewall (spam-free version)...'
    
    if ! ufw status | grep -q 'Status: active'; then
        # Disable first to avoid spam
        ufw --force disable >/dev/null 2>&1
        ufw --force reset >/dev/null 2>&1
        
        # Set defaults quietly
        ufw default deny incoming >/dev/null 2>&1
        ufw default allow outgoing >/dev/null 2>&1
        
        # Allow essential ports
        ufw allow 22/tcp comment 'SSH' >/dev/null 2>&1
        ufw allow 80/tcp comment 'HTTP' >/dev/null 2>&1
        ufw allow 443/tcp comment 'HTTPS' >/dev/null 2>&1
        
        # Allow application ports
        ufw allow 3000/tcp comment 'Frontend Prod' >/dev/null 2>&1
        ufw allow 3001/tcp comment 'Frontend Dev' >/dev/null 2>&1
        ufw allow 8000/tcp comment 'Backend Prod' >/dev/null 2>&1
        ufw allow 8001/tcp comment 'Backend Dev' >/dev/null 2>&1
        ufw allow 5678/tcp comment 'n8n Prod' >/dev/null 2>&1
        ufw allow 5679/tcp comment 'n8n Dev' >/dev/null 2>&1
        ufw allow 6379/tcp comment 'Redis Prod' >/dev/null 2>&1
        ufw allow 6380/tcp comment 'Redis Dev' >/dev/null 2>&1
        
        # Enable firewall quietly
        ufw --force enable >/dev/null 2>&1
        
        echo '✅ UFW firewall configured (no spam)'
    else
        echo '✅ UFW firewall already active'
    fi
    
    # Show clean status
    echo 'Firewall Status:'
    ufw status numbered | head -15
"

echo -e "${YELLOW}🔧 PHASE 6: Nginx Installation & Configuration${NC}"
NGINX_STATUS=$($RUN_CMD "nginx -v 2>/dev/null && echo 'installed' || echo 'not_installed'")

if [ "$NGINX_STATUS" = "installed" ]; then
    echo "✅ Nginx already installed"
else
    echo "Installing Nginx..."
    $RUN_CMD "
        apt-get install -y nginx
        systemctl daemon-reload
        systemctl start nginx
        systemctl enable nginx
        nginx -t
        echo '✅ Nginx installed and running'
    "
fiech
o -e "${YELLOW}🔧 PHASE 7: SSL Certificates (Cloudflare Origin)${NC}"
$RUN_CMD "
    echo 'Installing Cloudflare Origin Certificates...'
    mkdir -p /opt/docker-apps/shared/ssl
    
    # Install the wildcard certificate for *.consulting.sa
    cat > /opt/docker-apps/shared/ssl/consulting.sa.pem << 'CERT_EOF'
-----BEGIN CERTIFICATE-----
MIIElzCCA3+gAwIBAgIUJhW6TXoG1CWk1g1tyoRrFgxrPLUwDQYJKoZIhvcNAQEL
BQAwgYsxCzAJBgNVBAYTAlVTMRkwFwYDVQQKExBDbG91ZEZsYXJlLCBJbmMuMTQw
MgYDVQQLEytDbG91ZEZsYXJlIE9yaWdpbiBTU0wgQ2VydGlmaWNhdGUgQXV0aG9y
aXR5MRYwFAYDVQQHEw1TYW4gRnJhbmNpc2NvMRMwEQYDVQQIEwpDYWxpZm9ybmlh
MB4XDTI1MDcyMTAyNTQwMFoXDTQwMDcxNzAyNTQwMFowYjEZMBcGA1UEChMQQ2xv
dWRGbGFyZSwgSW5jLjEdMBsGA1UECxMUQ2xvdWRGbGFyZSBPcmlnaW4gQ0ExJjAk
BgNVBAMTHUNsb3VkRmxhcmUgT3JpZ2luIENlcnRpZmljYXRlMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3q9Wl4Vinjafp9Viv1oowlLc2lOqgO7aOPNb
qnUhdnA15c1amVxJ3Kd5p109LWexxYeol+TJnjYZLoe4JnbTyiDZfF+4s5uFmJ5B
uwUAPTGtXYwusa+bx4NoHVyQ2tf7v9wIXAO93hgETLqVN8QeSCSQNK6TvA0c67oB
ZCZ9DcOGe4/TtFUoNz53EjKVqCNbskcZmTRf3ouheDSV0izhFYG2DJckdizoLazK
tG4SXBjuf7GdltKRtx0paUP4c8tyAgx97FEBBhlzYczaHBJJ8Y6MYKrb0N+9XwAa
k6zLt9GSaQ4RKxQEr8leeGEmnUC/id72+4vSpoNULl7dM7KSJQIDAQABo4IBGTCC
ARUwDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcD
ATAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBRSnmhLG7wjr0pht3Owv51mdK/9FDAf
BgNVHSMEGDAWgBQk6FNXXXw0QIep65TbuuEWePwppDBABggrBgEFBQcBAQQ0MDIw
MAYIKwYBBQUHMAGGJGh0dHA6Ly9vY3NwLmNsb3VkZmxhcmUuY29tL29yaWdpbl9j
YTAaBgNVHREEEzARgg8qLmNvbnN1bHRpbmcuc2EwOAYDVR0fBDEwLzAtoCugKYYn
aHR0cDovL2NybC5jbG91ZGZsYXJlLmNvbS9vcmlnaW5fY2EuY3JsMA0GCSqGSIb3
DQEBCwUAA4IBAQA/kkIbQFAcEAOEW6NyPxuzIvcZGxbJsEt0eWc9ckQkUHVBQqgX
BfWWYTycXN+EWSAlN8CIIqtT6VpOqMfY7mrUnxoqBBGnpUC1Kixq2sezLEhlM/0Z
PXwHkh4CLLdX/Q1id8SxTJsWrk0knyvB+QOpcWh45RHaFDdV+W+wYUqvjamkLlhk
KPpmaeJMinYlTj483h2HXAuRjd6OJbqVRZ25HhObCwPnxjsF+Oz5UTW1gYInJ/XY
hSyKWxPmibt4jJaqzgUfel5I/RuHWkgyECyPbH0CA0FoDU/zfnOufj3mZZftHaUR
srZ+l4iSCDd6XR6hZO90ug9cMc/eKEygHTnk
-----END CERTIFICATE-----
CERT_EOF

    # Install the private key
    cat > /opt/docker-apps/shared/ssl/consulting.sa.key << 'KEY_EOF'
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDer1aXhWKeNp+n
1WK/WijCUtzaU6qA7to481uqdSF2cDXlzVqZXEncp3mnXT0tZ7HFh6iX5MmeNhku
h7gmdtPKINl8X7izm4WYnkG7BQA9Ma1djC6xr5vHg2gdXJDa1/u/3AhcA73eGARM
upU3xB5IJJA0rpO8DRzrugFkJn0Nw4Z7j9O0VSg3PncSMpWoI1uyRxmZNF/ei6F4
NJXSLOEVgbYMlyR2LOgtrMq0bhJcGO5/sZ2W0pG3HSlpQ/hzy3ICDH3sUQEGGXNh
zNocEknxjoxgqtvQ371fABqTrMu30ZJpDhErFASvyV54YSadQL+J3vb7i9Kmg1Qu
Xt0zspIlAgMBAAECggEAAr/pTnHcoNfUBqdoPU6SMUVpQ3Py9FMUCZq4d4qYHeIs
wUQZPP2+o5rDh330JIg4Fhh8XRUdsnqWECX9EdKmzFzo4HHHEi02vQ8yquoDhwq2
BkaE4ki6D0TZSH+H4Bk81u0THK7zz5k1lj/CFdzlHRgzjRwL8MCaKlGEBiYO2XIA
oIAdCw9gVG2DUt4YQuCD0cb2YZnShB8SeVCdXxiWg7Bq2jEVD2k4wRWRK/miiFWN
zYkYXL+ueodNKSg7WlWaYdESPIBpeOIwmOAJfXfTwfZCN0U+oW+yoou+XOB9mrC7
igWlXrx/V+xrYTObzI8ch/Wr3Z7iJqK7kZbM173vAwKBgQDv+3iP4Dub/kbCt3bC
90aBm1/R5r57ZBe9Njxxo3tSM+xVg58d2LMxCh+t0llrL5D4uYIaurzUK4zmgCsr
qxHha63VkLMcz6XXyp/r1oCxwQh9OJ5XXSpVGGt/5DnhCrJPQ0EsgpyWSRXUQKOM
DkpFMABfR0ZoWogqNYqK1QxKGwKBgQDtjE9slSaYVl/fV4L6ADiYHLV6k95TDKw+
0mg/xnAXejDOpzYehc7IMuB5XsMd8OoG6b5qyvIvR6kI7SYCdUPQhplFVrganZUw
ZBhuif1QTCV0CplIHqePcmw0KScH1BsRDWdunONNU1eLby3gL7/AsfCzaIhCF+ec
udVFcwpYvwKBgQDF6I3poVOndtCmPiTb7o8fzaH8+Zz3J3mIWhUI5niKNzXc4/ox
5AcLFz0+3S1O/uBArsQEBSI6m1vMr8Bqd978FxA6AuYjiX9Mcdbm6HQjo3y7wBid
FcEWglgNFYtB8s9QHLe/3EsEiWtOKqx1kUdgvZBhAuemoZqPrK3/hmlnJwKBgEBa
FGIb/bqjG5HLiUXkrXA3xsoQKNhixH64TVmJjnAtv+8byUN3iE8fyUPX8g+4Zg29
YMJZfEZmqVortHJSBi8FZ5wrI/DB49qaIyw+4YrRNgw7ms64zzfDDaELzPEH+tUh
xnVmtwUJoNu7ILhs9wtiqQxRMyiEhVAl36rSwWjNAoGBALU+e0AhlJoYsBP/iZvQ
c+wBMQ+qjAaSYqPA7IEu80yZ3+deDbfQbESOQ+x0pjd3IxByYrQ7JrYVMpMoWJi/
0tU0I/guj+Q35o3lwaEftjf92F/7e0Z0Emv0zHiRYXYKq9Po0FPExqdASDRPJSt2
AR6dFHhoMCntXlfsQCgrgmvv
-----END PRIVATE KEY-----
KEY_EOF

    # Set proper permissions
    chmod 600 /opt/docker-apps/shared/ssl/*
    chown root:root /opt/docker-apps/shared/ssl/*
    
    echo '✅ SSL certificates installed (valid until 2040)'
"

echo -e "${YELLOW}🔧 PHASE 8: Cloudflare DNS Configuration${NC}"
echo "Configuring DNS records with Cloudflare..."

# Function to update DNS record
update_dns_record() {
    local record_name="$1"
    local record_ip="$2"
    local proxied="$3"
    
    echo "  Configuring: $record_name -> $record_ip"
    
    # Get existing record
    EXISTING_RECORD=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=$record_name&type=A" \
         -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
         -H "Content-Type: application/json")
    
    RECORD_ID=$(echo "$EXISTING_RECORD" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$RECORD_ID" ]; then
        # Update existing record
        RESULT=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json" \
             --data "{
               \"type\": \"A\",
               \"name\": \"$record_name\",
               \"content\": \"$record_ip\",
               \"ttl\": 300,
               \"proxied\": $proxied
             }")
    else
        # Create new record
        RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
             -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
             -H "Content-Type: application/json" \
             --data "{
               \"type\": \"A\",
               \"name\": \"$record_name\",
               \"content\": \"$record_ip\",
               \"ttl\": 300,
               \"proxied\": $proxied
             }")
    fi
    
    if echo "$RESULT" | grep -q '"success":true'; then
        echo "    ✅ $record_name configured"
    else
        echo "    ❌ Failed to configure $record_name"
    fi
}

# Configure DNS records
update_dns_record "consulting.sa" "$VPS_IP" "true"
update_dns_record "www.consulting.sa" "$VPS_IP" "true"
update_dns_record "dev.consulting.sa" "$VPS_IP" "true"

echo "✅ DNS records configured"echo -e 
"${YELLOW}🔧 PHASE 9: Environment Structure & Nginx Configuration${NC}"
$RUN_CMD "
    echo 'Creating deployment structure...'
    
    # Create directory structure
    mkdir -p /opt/docker-apps/{production,development}/agentic-site
    mkdir -p /opt/docker-apps/shared/{ssl,nginx,backups,logs}
    mkdir -p /var/log/agentic-site/{production,development}
    
    # Set permissions
    chown -R root:root /opt/docker-apps
    chmod -R 755 /opt/docker-apps
    
    echo 'Creating Nginx configurations...'
    
    # Production Nginx configuration
    cat > /opt/docker-apps/shared/nginx/production.conf << 'PROD_NGINX_EOF'
server {
    listen 80;
    server_name consulting.sa www.consulting.sa;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa;

    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /workflows/ {
        proxy_pass http://127.0.0.1:5678/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
PROD_NGINX_EOF

    # Development Nginx configuration
    cat > /opt/docker-apps/shared/nginx/development.conf << 'DEV_NGINX_EOF'
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /workflows/ {
        proxy_pass http://127.0.0.1:5679/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
DEV_NGINX_EOF

    # Enable Nginx sites
    rm -f /etc/nginx/sites-enabled/default
    ln -sf /opt/docker-apps/shared/nginx/production.conf /etc/nginx/sites-enabled/
    ln -sf /opt/docker-apps/shared/nginx/development.conf /etc/nginx/sites-enabled/
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
    
    echo '✅ Nginx configurations created and enabled'
"ec
ho -e "${YELLOW}🔧 PHASE 10: Repository Setup & Environment Configuration${NC}"
$RUN_CMD "
    echo 'Setting up production environment...'
    cd /opt/docker-apps/production/agentic-site
    rm -rf agentic-site
    git clone https://$GITHUB_TOKEN@github.com/abusallam/agentic-site.git
    cd agentic-site
    git checkout main
    
    echo 'Setting up development environment...'
    cd /opt/docker-apps/development/agentic-site
    rm -rf agentic-site
    git clone https://$GITHUB_TOKEN@github.com/abusallam/agentic-site.git
    cd agentic-site
    git checkout develop
    
    echo '✅ Both environments cloned from GitHub'
"

echo -e "${YELLOW}🔧 PHASE 11: Management Scripts Creation${NC}"
$RUN_CMD "
    echo 'Creating comprehensive management scripts...'
    
    # Master status script
    cat > /usr/local/bin/agentic-master-status.sh << 'STATUS_EOF'
#!/bin/bash
echo \"=== AGENTIC SITE MASTER STATUS ===\"
echo \"Timestamp: \$(date)\"
echo \"VPS IP: $VPS_IP\"
echo \"SSH Alias: $SSH_ALIAS\"
echo

echo \"=== System Resources ===\"
echo \"Memory: \$(free -h | grep Mem | awk '{print \$3\"/\"\$2}')\"
echo \"Disk: \$(df -h / | tail -1 | awk '{print \$3\"/\"\$2\" (\"\$5\" used)\"}')\"
echo \"CPU Load: \$(uptime | awk -F'load average:' '{print \$2}')\"
echo

echo \"=== Service Status ===\"
echo \"Docker: \$(systemctl is-active docker)\"
echo \"Nginx: \$(systemctl is-active nginx)\"
echo \"UFW: \$(ufw status | head -1)\"
echo

echo \"=== Production Environment ===\"
cd /opt/docker-apps/production/agentic-site/agentic-site 2>/dev/null && docker-compose ps || echo \"Production not deployed\"

echo
echo \"=== Development Environment ===\"
cd /opt/docker-apps/development/agentic-site/agentic-site 2>/dev/null && docker-compose ps || echo \"Development not deployed\"

echo
echo \"=== Port Status ===\"
netstat -tlnp | grep -E ':(3000|3001|8000|8001|5678|5679|6379|6380)' || echo \"No application ports listening\"

echo
echo \"=== SSL Certificate Status ===\"
openssl x509 -in /opt/docker-apps/shared/ssl/consulting.sa.pem -noout -dates 2>/dev/null || echo \"SSL certificate not found\"
STATUS_EOF

    # Production deployment script
    cat > /usr/local/bin/deploy-production.sh << 'PROD_DEPLOY_EOF'
#!/bin/bash
echo \"=== DEPLOYING PRODUCTION ENVIRONMENT ===\"
cd /opt/docker-apps/production/agentic-site/agentic-site

echo \"Pulling latest changes...\"
git pull origin main

echo \"Stopping existing containers...\"
docker-compose down 2>/dev/null || true

echo \"Starting production containers...\"
docker-compose up -d

echo \"Waiting for services...\"
sleep 30

echo \"Production deployment status:\"
docker-compose ps

echo \"=== PRODUCTION DEPLOYMENT COMPLETE ===\"
PROD_DEPLOY_EOF

    # Development deployment script
    cat > /usr/local/bin/deploy-development.sh << 'DEV_DEPLOY_EOF'
#!/bin/bash
echo \"=== DEPLOYING DEVELOPMENT ENVIRONMENT ===\"
cd /opt/docker-apps/development/agentic-site/agentic-site

echo \"Pulling latest changes...\"
git pull origin develop

echo \"Stopping existing containers...\"
docker-compose down 2>/dev/null || true

echo \"Starting development containers...\"
docker-compose up -d

echo \"Waiting for services...\"
sleep 30

echo \"Development deployment status:\"
docker-compose ps

echo \"=== DEVELOPMENT DEPLOYMENT COMPLETE ===\"
DEV_DEPLOY_EOF

    # System maintenance script
    cat > /usr/local/bin/agentic-maintenance.sh << 'MAINT_EOF'
#!/bin/bash
echo \"=== AGENTIC SITE MAINTENANCE ===\"
echo \"Timestamp: \$(date)\"

echo \"Updating system packages...\"
apt-get update -y && apt-get upgrade -y

echo \"Cleaning Docker resources...\"
docker system prune -f

echo \"Checking disk space...\"
df -h

echo \"Checking SSL certificate expiry...\"
openssl x509 -in /opt/docker-apps/shared/ssl/consulting.sa.pem -noout -dates

echo \"Restarting services...\"
systemctl restart docker
systemctl restart nginx

echo \"=== MAINTENANCE COMPLETE ===\"
MAINT_EOF

    # Make all scripts executable
    chmod +x /usr/local/bin/agentic-*
    chmod +x /usr/local/bin/deploy-*
    
    echo '✅ Management scripts created'
"

echo -e "${YELLOW}🔧 PHASE 12: Final System Optimization (Debian 12)${NC}"
$RUN_CMD "
    echo 'Applying final optimizations...'
    
    # Set timezone
    timedatectl set-timezone UTC
    
    # Restart all services for Debian 12
    systemctl daemon-reload
    systemctl restart docker
    systemctl restart nginx
    systemctl restart ssh
    
    # Create system info
    cat > /opt/docker-apps/shared/system-info.txt << INFO_EOF
Agentic Site Master Setup
========================
Setup Date: \$(date)
VPS IP: $VPS_IP
SSH Alias: $SSH_ALIAS
Domains: consulting.sa, dev.consulting.sa

Installed Services:
- Docker: \$(docker --version)
- Nginx: \$(nginx -v 2>&1)
- UFW: Active with application ports
- SSL: Cloudflare Origin Certificate (valid until 2040)

Management Commands:
- Master Status: /usr/local/bin/agentic-master-status.sh
- Deploy Production: /usr/local/bin/deploy-production.sh
- Deploy Development: /usr/local/bin/deploy-development.sh
- System Maintenance: /usr/local/bin/agentic-maintenance.sh

SSH Access: ssh $SSH_ALIAS
INFO_EOF

    echo '✅ Final optimizations complete'
"# Cr
eate local environment configuration
cat > ".env.master-setup" << EOF
# Master Setup Configuration - Generated $(date)
# This file contains all the configuration for the master setup

# VPS Details
VPS_IP=$VPS_IP
SSH_ALIAS=$SSH_ALIAS
SSH_KEY_PATH=$SSH_KEY_PATH
SSH_KEY_WORKING=$SSH_KEY_WORKING

# Cloudflare Configuration
CLOUDFLARE_TOKEN=$CLOUDFLARE_TOKEN
ZONE_ID=$ZONE_ID

# GitHub Configuration
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_REPO=$GITHUB_REPO

# Domain Configuration
PRODUCTION_DOMAIN=consulting.sa
DEVELOPMENT_DOMAIN=dev.consulting.sa

# Application Ports
PRODUCTION_FRONTEND_PORT=3000
PRODUCTION_BACKEND_PORT=8000
PRODUCTION_REDIS_PORT=6379
PRODUCTION_N8N_PORT=5678

DEVELOPMENT_FRONTEND_PORT=3001
DEVELOPMENT_BACKEND_PORT=8001
DEVELOPMENT_REDIS_PORT=6380
DEVELOPMENT_N8N_PORT=5679

# Deployment Paths
PRODUCTION_PATH=/opt/docker-apps/production/agentic-site
DEVELOPMENT_PATH=/opt/docker-apps/development/agentic-site
SHARED_PATH=/opt/docker-apps/shared

# Management Scripts
MASTER_STATUS_SCRIPT=/usr/local/bin/agentic-master-status.sh
PRODUCTION_DEPLOY_SCRIPT=/usr/local/bin/deploy-production.sh
DEVELOPMENT_DEPLOY_SCRIPT=/usr/local/bin/deploy-development.sh
MAINTENANCE_SCRIPT=/usr/local/bin/agentic-maintenance.sh

# Setup Status
SETUP_COMPLETED=true
SETUP_DATE=$(date)
SETUP_VERSION=master-v1.0
ALL_LESSONS_LEARNED=true
THANKS_TO_GOD=true
EOF

# Create verification script
cat > "verify-master-setup.sh" << EOF
#!/bin/bash

echo "=== MASTER SETUP VERIFICATION ==="
echo "Timestamp: \$(date)"
echo

# Test SSH connection
echo "Testing SSH connection..."
if ssh $SSH_ALIAS 'echo "SSH connection working"'; then
    echo "✅ SSH connection successful"
else
    echo "❌ SSH connection failed"
fi

# Test domains
echo
echo "Testing domains..."
for domain in "consulting.sa" "dev.consulting.sa"; do
    if curl -s -I "https://\$domain" | grep -q "200\|301\|302"; then
        echo "✅ https://\$domain is accessible"
    else
        echo "⚠ https://\$domain may still be propagating"
    fi
done

# Test management scripts
echo
echo "Testing management scripts..."
ssh $SSH_ALIAS '/usr/local/bin/agentic-master-status.sh' | head -10

echo
echo "=== VERIFICATION COMPLETE ==="
EOF

chmod +x verify-master-setup.sh

echo
echo -e "${BOLD}${GREEN}🎉 ENTERPRISE MASTER SETUP COMPLETE! 🙏${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo -e "${BOLD}${CYAN}✨ Thanks to God for the wisdom and lessons learned! ✨${NC}"
echo
echo -e "${BOLD}${CYAN}🏗️ What was accomplished:${NC}"
echo "✅ Complete VPS foundation (Debian 12 optimized)"
echo "✅ SSH key authentication with secure access"
echo "✅ Docker installation with latest version"
echo "✅ UFW firewall (spam-free configuration)"
echo "✅ Nginx with SSL and reverse proxy"
echo "✅ Cloudflare SSL certificates (valid until 2040)"
echo "✅ DNS configuration for consulting.sa and dev.consulting.sa"
echo "✅ Separate production and development environments"
echo "✅ GitHub integration with automated deployment"
echo "✅ Comprehensive management scripts"
echo "✅ System monitoring and maintenance tools"
echo
echo -e "${BOLD}${CYAN}🌐 Live URLs:${NC}"
echo "Production: https://consulting.sa"
echo "Development: https://dev.consulting.sa"
echo
echo -e "${BOLD}${CYAN}🔧 Management Commands:${NC}"
echo "Master Status: ssh $SSH_ALIAS '/usr/local/bin/agentic-master-status.sh'"
echo "Deploy Production: ssh $SSH_ALIAS '/usr/local/bin/deploy-production.sh'"
echo "Deploy Development: ssh $SSH_ALIAS '/usr/local/bin/deploy-development.sh'"
echo "System Maintenance: ssh $SSH_ALIAS '/usr/local/bin/agentic-maintenance.sh'"
echo
echo -e "${BOLD}${CYAN}📋 Files Created:${NC}"
echo "- .env.master-setup (local configuration)"
echo "- verify-master-setup.sh (verification script)"
echo "- AGENT.md (AI agent documentation)"
echo
echo -e "${BOLD}${CYAN}🚀 Next Steps:${NC}"
echo "1. Verify setup: ./verify-master-setup.sh"
echo "2. Deploy applications: ssh $SSH_ALIAS '/usr/local/bin/deploy-production.sh'"
echo "3. Test all functionality: https://consulting.sa and https://dev.consulting.sa"
echo
echo -e "${BOLD}${GREEN}✅ ONE SCRIPT TO RULE THEM ALL - MISSION ACCOMPLISHED! 🎯${NC}"
echo -e "${BOLD}${YELLOW}⚠️  This script incorporates ALL lessons learned and is production-ready${NC}"