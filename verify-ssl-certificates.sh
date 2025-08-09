#!/bin/bash

# SSL Certificate Verification Script
echo "=== SSL Certificate Verification ==="
echo "Timestamp: $(date)"
echo

# Test certificate validity
echo "Testing SSL certificates..."

domains=("consulting.sa" "dev.consulting.sa")

for domain in "${domains[@]}"; do
    echo "Testing $domain..."
    
    # Test SSL certificate
    if command -v openssl &> /dev/null; then
        echo "  Certificate details:"
        echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null || echo "  SSL connection failed"
        
        # Test certificate chain
        echo "  Certificate chain:"
        echo | openssl s_client -servername "$domain" -connect "$domain:443" -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE" || echo "  Chain test failed"
    fi
    
    echo
done

echo "=== Local Certificate Verification ==="
ssh agentic-fixed-217-79-255-54-development 'openssl x509 -in /opt/docker-apps/shared/ssl/consulting.sa.pem -text -noout | grep -E "Subject:|DNS:|Not After"'
