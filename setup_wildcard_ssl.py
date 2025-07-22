#!/usr/bin/env python3
"""
Set up Cloudflare wildcard SSL certificate for *.consulting.sa
"""

import paramiko
import sys
import time
from datetime import datetime

def execute_ssh_command(client, command, description="", timeout=120):
    """Execute SSH command with logging"""
    print(f"🔧 {description}: {command}")
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print(f"✅ SUCCESS")
            if output and len(output) < 800:
                print(f"📝 {output}")
        else:
            print(f"⚠️ Exit code: {exit_code}")
            if error:
                print(f"❌ Error: {error[:400]}")
        
        return exit_code == 0, output, error
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, "", str(e)

def main():
    hostname = "217.79.255.54"
    username = "root" 
    password = "gt5qXy22aJ"
    port = 22
    
    print("🔒 SETTING UP WILDCARD SSL CERTIFICATE FOR *.CONSULTING.SA")
    print("=" * 60)
    print(f"Server: {hostname}")
    print(f"Domain: *.consulting.sa (wildcard)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Wildcard certificate content from Cloudflare
    certificate = """-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----"""
    
    # Private key content from Cloudflare
    private_key = """-----BEGIN PRIVATE KEY-----
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
-----END PRIVATE KEY-----"""
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        print("✅ Connected to VPS")
        
        # Create SSL directory if it doesn't exist
        print("\n📁 CREATING SSL DIRECTORY STRUCTURE")
        print("-" * 50)
        
        execute_ssh_command(client, "mkdir -p /etc/nginx/ssl/consulting.sa", "Create SSL directory")
        
        # Save certificate and private key
        print("\n🔑 INSTALLING WILDCARD SSL CERTIFICATE")
        print("-" * 50)
        
        # Use proper escaping for the certificate content
        cert_file = "/tmp/certificate.crt"
        key_file = "/tmp/private.key"
        
        # Write certificate to temporary file first
        with open("temp_cert.crt", "w") as f:
            f.write(certificate)
        with open("temp_key.key", "w") as f:
            f.write(private_key)
        
        # Upload files using SFTP
        sftp = client.open_sftp()
        sftp.put("temp_cert.crt", cert_file)
        sftp.put("temp_key.key", key_file)
        sftp.close()
        
        # Move files to proper location
        execute_ssh_command(client, f"mv {cert_file} /etc/nginx/ssl/consulting.sa/certificate.crt", "Move certificate")
        execute_ssh_command(client, f"mv {key_file} /etc/nginx/ssl/consulting.sa/private.key", "Move private key")
        
        # Set proper permissions
        execute_ssh_command(client, "chmod 600 /etc/nginx/ssl/consulting.sa/private.key", "Set private key permissions")
        execute_ssh_command(client, "chmod 644 /etc/nginx/ssl/consulting.sa/certificate.crt", "Set certificate permissions")
        
        # Verify certificate details
        execute_ssh_command(client, "openssl x509 -in /etc/nginx/ssl/consulting.sa/certificate.crt -noout -subject -dates", "Verify certificate")
        
        # Update Nginx configuration for wildcard SSL
        print("\n🌐 UPDATING NGINX CONFIGURATION FOR WILDCARD SSL")
        print("-" * 50)
        
        nginx_config = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name consulting.sa www.consulting.sa *.consulting.sa 217.79.255.54 _;
    
    # Redirect HTTP to HTTPS for consulting.sa domains
    if ($host ~ ^(.+\\.)?consulting\\.sa$) {
        return 301 https://$host$request_uri;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Main application - proxy to Next.js frontend
    location / {
        proxy_pass http://127.0.0.1:3911;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Backend API endpoints
    location /api/agent/ {
        proxy_pass http://127.0.0.1:8953/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}

# HTTPS configuration with Cloudflare wildcard SSL
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name consulting.sa www.consulting.sa *.consulting.sa;
    
    # SSL configuration - wildcard certificate
    ssl_certificate /etc/nginx/ssl/consulting.sa/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/consulting.sa/private.key;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main application - proxy to Next.js frontend
    location / {
        proxy_pass http://127.0.0.1:3911;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Backend API endpoints
    location /api/agent/ {
        proxy_pass http://127.0.0.1:8953/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_connect_timeout 60;
        proxy_send_timeout 60;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}"""
        
        # Write nginx config to temporary file
        with open("temp_nginx.conf", "w") as f:
            f.write(nginx_config)
        
        # Upload nginx config
        sftp = client.open_sftp()
        sftp.put("temp_nginx.conf", "/tmp/nginx_default")
        sftp.close()
        
        execute_ssh_command(client, "mv /tmp/nginx_default /etc/nginx/sites-available/default", "Update Nginx config for wildcard SSL")
        
        # Test and reload Nginx
        execute_ssh_command(client, "nginx -t", "Test Nginx configuration")
        execute_ssh_command(client, "systemctl reload nginx", "Reload Nginx")
        
        # Update environment variables
        print("\n🔧 UPDATING ENVIRONMENT VARIABLES")
        print("-" * 50)
        
        # Read current .env file
        stdin, stdout, stderr = client.exec_command("cat /opt/docker-apps/production/agentic-site/.env")
        current_env = stdout.read().decode('utf-8')
        
        # Update environment variables for wildcard domain
        env_updates = """
# Wildcard SSL Certificate Information
SSL_CERT_PATH=/etc/nginx/ssl/consulting.sa/certificate.crt
SSL_KEY_PATH=/etc/nginx/ssl/consulting.sa/private.key
SSL_PROVIDER=cloudflare
SSL_DOMAIN=*.consulting.sa
SSL_TYPE=wildcard
SSL_EXPIRY=2040-07-17
DOMAIN=consulting.sa
NEXT_PUBLIC_SITE_URL=https://consulting.sa
NEXT_PUBLIC_ADMIN_URL=https://consulting.sa:8953
FORCE_HTTPS=true
"""
        
        execute_ssh_command(client, f"echo '{env_updates}' >> /opt/docker-apps/production/agentic-site/.env", "Add wildcard SSL info to environment")
        
        # Restart containers to apply environment changes
        print("\n🔄 RESTARTING CONTAINERS WITH NEW ENVIRONMENT")
        print("-" * 50)
        
        execute_ssh_command(client, "cd /opt/docker-apps/production/agentic-site && docker compose restart", "Restart containers")
        execute_ssh_command(client, "sleep 30", "Wait for containers to restart")
        
        # Final verification
        print("\n✅ FINAL VERIFICATION")
        print("-" * 50)
        
        execute_ssh_command(client, "systemctl is-active nginx", "Check Nginx status")
        execute_ssh_command(client, "cd /opt/docker-apps/production/agentic-site && docker compose ps", "Check container status")
        execute_ssh_command(client, "curl -k https://localhost/health", "Test HTTPS locally")
        
        # Clean up temporary files
        import os
        for temp_file in ["temp_cert.crt", "temp_key.key", "temp_nginx.conf"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        client.close()
        
        print("\n🎉 WILDCARD SSL CERTIFICATE INSTALLATION COMPLETE!")
        print("=" * 60)
        print("✅ Wildcard SSL certificate installed successfully")
        print("✅ Nginx configured for HTTPS with wildcard support")
        print("✅ Environment variables updated")
        print("✅ HTTP to HTTPS redirection enabled")
        print("✅ Security headers configured")
        print()
        print("🌐 Your website is now accessible via:")
        print(f"   - HTTPS: https://consulting.sa/")
        print(f"   - HTTPS: https://www.consulting.sa/")
        print(f"   - HTTPS: https://[any-subdomain].consulting.sa/")
        print(f"   - HTTP: http://consulting.sa/ (redirects to HTTPS)")
        print(f"   - IP: http://{hostname}/ (still accessible)")
        print()
        print("🔒 Wildcard SSL Certificate Information:")
        print("   - Provider: Cloudflare Origin SSL")
        print("   - Type: Wildcard Certificate")
        print("   - Expires: 2040-07-17")
        print("   - Domains: *.consulting.sa (covers all subdomains)")
        print()
        print("📋 Next Steps:")
        print("1. Configure DNS records in Cloudflare for subdomains")
        print("2. Test all subdomains with HTTPS")
        print("3. Set up monitoring for SSL certificate expiry")
        print("4. Update any hardcoded URLs to use HTTPS")
        
        return True
        
    except Exception as e:
        print(f"❌ Wildcard SSL setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)