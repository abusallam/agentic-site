#!/bin/bash

# Test VPS Connection Script
# This script tests different ways to connect to the VPS

set -e

VPS_IP="217.79.255.54"
VPS_PASSWORD="gnqLG7FDd4"

echo "🔍 Testing VPS Connection Methods"
echo "================================="
echo "IP: $VPS_IP"
echo

echo "Test 1: Trying with root user and password..."
if sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no root@$VPS_IP "echo 'Root with password: SUCCESS'" 2>/dev/null; then
    echo "✅ Root with password works!"
    exit 0
else
    echo "❌ Root with password failed"
fi

echo
echo "Test 2: Trying with ubuntu user and password..."
if sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no ubuntu@$VPS_IP "echo 'Ubuntu with password: SUCCESS'" 2>/dev/null; then
    echo "✅ Ubuntu with password works!"
    echo "Use 'ubuntu' as username instead of 'root'"
    exit 0
else
    echo "❌ Ubuntu with password failed"
fi

echo
echo "Test 3: Checking if existing SSH key works with root..."
if ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PasswordAuthentication=no root@$VPS_IP "echo 'Root with existing key: SUCCESS'" 2>/dev/null; then
    echo "✅ Root with existing SSH key works!"
    echo "You already have SSH key access set up"
    exit 0
else
    echo "❌ Root with existing SSH key failed"
fi

echo
echo "Test 4: Checking if existing SSH key works with ubuntu..."
if ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o PasswordAuthentication=no ubuntu@$VPS_IP "echo 'Ubuntu with existing key: SUCCESS'" 2>/dev/null; then
    echo "✅ Ubuntu with existing SSH key works!"
    echo "You already have SSH key access set up with ubuntu user"
    exit 0
else
    echo "❌ Ubuntu with existing SSH key failed"
fi

echo
echo "Test 5: Getting detailed SSH server configuration..."
echo "Checking what authentication methods the server accepts..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 root@$VPS_IP 2>&1 | grep -E "(Permission denied|Authentication|publickey|password)" | head -5

echo
echo "🔍 Diagnosis:"
echo "The server is reachable but authentication is failing."
echo
echo "Possible causes:"
echo "1. Password has changed"
echo "2. Password authentication is disabled on the server"
echo "3. Username should be 'ubuntu' instead of 'root'"
echo "4. Server only accepts SSH key authentication"
echo
echo "Next steps:"
echo "1. Try connecting manually: ssh root@$VPS_IP"
echo "2. Check if you can connect via your VPS provider's console"
echo "3. Verify the correct username and password from your VPS provider"