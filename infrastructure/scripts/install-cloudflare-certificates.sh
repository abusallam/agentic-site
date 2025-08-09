#!/bin/bash

# Install Cloudflare Origin Certificates
# Usage: ./install-cloudflare-certificates.sh <SSH_ALIAS>

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
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <SSH_ALIAS>${NC}"
    echo -e "${YELLOW}Example: $0 agentic-fixed-217-79-255-54-development${NC}"
    exit 1
fi

SSH_ALIAS="$1"

echo -e "${BOLD}${PURPLE}🔐 Installing Cloudflare Origin Certificates${NC}"
echo -e "${BLUE}=============================================${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Timestamp: $(date)"
echo

echo -e "${YELLOW}Step 1: Creating SSL directory and installing certificates...${NC}"

ssh "$SSH_ALIAS" "
    # Create SSL directory
    mkdir -p /opt/docker-apps/shared/ssl
    
    # Install the certificate
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
    
    echo '✓ Certificates installed and secured'
"

echo -e "${YELLOW}Step 2: Verifying certificate installation...${NC}"

ssh "$SSH_ALIAS" "
    echo 'Certificate details:'
    openssl x509 -in /opt/docker-apps/shared/ssl/consulting.sa.pem -text -noout | grep -E 'Subject:|DNS:|Not After'
    
    echo
    echo 'Certificate files:'
    ls -la /opt/docker-apps/shared/ssl/
"

echo -e "${YELLOW}Step 3: Creating updated Nginx configurations...${NC}"

ssh "$SSH_ALIAS" "
    # Create production Nginx configuration
    cat > /opt/docker-apps/shared/nginx/production.conf << 'EOF'
# Production Nginx Configuration for consulting.sa
server {
    listen 80;
    server_name consulting.sa www.consulting.sa;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consulting.sa www.consulting.sa;

    # SSL Configuration (Cloudflare Origin Certificate)
    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;

    # Main application
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
        proxy_read_timeout 86400;
    }

    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # n8n workflows
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
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Create development Nginx configuration
    cat > /opt/docker-apps/shared/nginx/development.conf << 'EOF'
# Development Nginx Configuration for dev.consulting.sa
server {
    listen 80;
    server_name dev.consulting.sa;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dev.consulting.sa;

    # SSL Configuration (Cloudflare Origin Certificate)
    ssl_certificate /opt/docker-apps/shared/ssl/consulting.sa.pem;
    ssl_certificate_key /opt/docker-apps/shared/ssl/consulting.sa.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header Referrer-Policy \"strict-origin-when-cross-origin\" always;
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\" always;

    # Main application
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
        proxy_read_timeout 86400;
    }

    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # n8n workflows
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
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    echo '✓ Nginx configurations created'
"

echo -e "${YELLOW}Step 4: Enabling Nginx sites and testing configuration...${NC}"

ssh "$SSH_ALIAS" "
    # Remove any existing configurations
    rm -f /etc/nginx/sites-enabled/default
    rm -f /etc/nginx/sites-enabled/production.conf
    rm -f /etc/nginx/sites-enabled/development.conf
    
    # Link new configurations
    ln -sf /opt/docker-apps/shared/nginx/production.conf /etc/nginx/sites-available/production.conf
    ln -sf /opt/docker-apps/shared/nginx/development.conf /etc/nginx/sites-available/development.conf
    
    # Enable sites
    ln -sf /etc/nginx/sites-available/production.conf /etc/nginx/sites-enabled/
    ln -sf /etc/nginx/sites-available/development.conf /etc/nginx/sites-enabled/
    
    # Test Nginx configuration
    echo 'Testing Nginx configuration...'
    if nginx -t; then
        echo '✓ Nginx configuration is valid'
        systemctl reload nginx
        echo '✓ Nginx reloaded successfully'
    else
        echo '❌ Nginx configuration has errors'
        exit 1
    fi
"

echo -e "${YELLOW}Step 5: Creating certificate verification script...${NC}"

cat > "verify-ssl-certificates.sh" << EOF
#!/bin/bash

# SSL Certificate Verification Script
echo "=== SSL Certificate Verification ==="
echo "Timestamp: \$(date)"
echo

# Test certificate validity
echo "Testing SSL certificates..."

domains=("consulting.sa" "dev.consulting.sa")

for domain in "\${domains[@]}"; do
    echo "Testing \$domain..."
    
    # Test SSL certificate
    if command -v openssl &> /dev/null; then
        echo "  Certificate details:"
        echo | openssl s_client -servername "\$domain" -connect "\$domain:443" 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null || echo "  SSL connection failed"
        
        # Test certificate chain
        echo "  Certificate chain:"
        echo | openssl s_client -servername "\$domain" -connect "\$domain:443" -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE" || echo "  Chain test failed"
    fi
    
    echo
done

echo "=== Local Certificate Verification ==="
ssh $SSH_ALIAS 'openssl x509 -in /opt/docker-apps/shared/ssl/consulting.sa.pem -text -noout | grep -E "Subject:|DNS:|Not After"'
EOF

chmod +x verify-ssl-certificates.sh

echo
echo -e "${BOLD}${GREEN}🎉 Cloudflare Certificates Installed Successfully!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo
echo -e "${BOLD}${CYAN}🔐 Certificate Details:${NC}"
echo "✅ Wildcard certificate for *.consulting.sa installed"
echo "✅ Certificate valid until July 17, 2040"
echo "✅ Nginx configurations updated with SSL"
echo "✅ Security headers configured"
echo
echo -e "${BOLD}${CYAN}🌐 Ready Domains:${NC}"
echo "✅ https://consulting.sa (Production - when containers are running)"
echo "✅ https://dev.consulting.sa (Development - when containers are running)"
echo "✅ https://www.consulting.sa (Production redirect)"
echo
echo -e "${BOLD}${CYAN}🔧 Next Steps:${NC}"
echo "1. Set up production environment:"
echo "   ./infrastructure/scripts/setup-production-environment.sh $SSH_ALIAS <CLOUDFLARE_TOKEN>"
echo
echo "2. Configure Cloudflare DNS (you'll need your Zone ID):"
echo "   ./infrastructure/scripts/configure-cloudflare-domains.sh $SSH_ALIAS <CLOUDFLARE_TOKEN> <ZONE_ID>"
echo
echo "3. Deploy production containers:"
echo "   ssh $SSH_ALIAS '/usr/local/bin/deploy-production.sh'"
echo
echo "4. Verify SSL certificates:"
echo "   ./verify-ssl-certificates.sh"
echo
echo -e "${BOLD}${CYAN}📋 Files Created:${NC}"
echo "- verify-ssl-certificates.sh (SSL verification script)"
echo "- /opt/docker-apps/shared/ssl/consulting.sa.pem (Certificate)"
echo "- /opt/docker-apps/shared/ssl/consulting.sa.key (Private Key)"
echo "- /opt/docker-apps/shared/nginx/*.conf (Nginx configurations)"
echo
echo -e "${BOLD}${GREEN}✅ SSL certificates are ready for production use!${NC}"
echo -e "${BOLD}${YELLOW}⚠️  Now you need your Cloudflare API token and Zone ID to complete the setup${NC}"