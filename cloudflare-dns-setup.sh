#!/bin/bash

# Cloudflare DNS Configuration Script
# Usage: ./cloudflare-dns-setup.sh

CLOUDFLARE_TOKEN="58647784bbf3bf735c3b7d8dac44eb0952e94"
ZONE_ID="your-zone-id-here"  # Get from Cloudflare dashboard
VPS_IP="217.79.255.54"

echo "Setting up DNS records for consulting.sa..."

# Function to create/update DNS record
update_dns_record() {
    local name=$1
    local ip=$2
    
    echo "Updating DNS record: $name -> $ip"
    
    curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
         -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
         -H "Content-Type: application/json" \
         --data '{
           "type": "A",
           "name": "'$name'",
           "content": "'$ip'",
           "ttl": 300,
           "proxied": true
         }'
}

# Create DNS records
update_dns_record "consulting.sa" "$VPS_IP"
update_dns_record "www.consulting.sa" "$VPS_IP"
update_dns_record "dev.consulting.sa" "$VPS_IP"

echo "DNS configuration complete!"
echo "Note: Update ZONE_ID in this script with your actual Cloudflare Zone ID"
