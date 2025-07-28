#!/bin/bash

# 🚀 Agentic AI Platform - One-Click Deployment
# This is your main deployment script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 🚀 AGENTIC AI PLATFORM                      ║"
echo "║                Complete Deployment System                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}🏗️ Your VPS Configuration:${NC}"
echo "• Host: 217.79.255.54"
echo "• User: root"
echo "• Domain: consulting.sa"
echo ""

echo -e "${YELLOW}📋 What you need to provide:${NC}"
echo "1. Supabase URL and API keys"
echo "2. Google Gemini API key"
echo "3. GitHub token (optional, for CI/CD)"
echo ""

echo -e "${BLUE}🎯 Deployment Options:${NC}"
echo ""
echo "1) 🔧 Configure Environment (Update .env with your keys)"
echo "2) 🧪 Test & Deploy Everything (Full deployment process)"
echo "3) 📊 Setup Monitoring (n8n, Grafana - Phase 2)"
echo "4) 🔍 Check Deployment Status"
echo "5) 📖 View Deployment Guide"
echo "6) ❌ Exit"
echo ""

read -p "Choose an option (1-6): " choice

case $choice in
    1)
        echo -e "\n${BLUE}🔧 Starting Configuration...${NC}"
        ./scripts/update-config.sh
        ;;
    2)
        echo -e "\n${BLUE}🧪 Starting Test & Deploy Process...${NC}"
        echo -e "${YELLOW}This will:${NC}"
        echo "• Test frontend and backend locally"
        echo "• Build Docker containers"
        echo "• Run security checks"
        echo "• Deploy to your VPS"
        echo "• Configure SSL certificates"
        echo ""
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./scripts/test-and-deploy.sh
        else
            echo "Deployment cancelled."
        fi
        ;;
    3)
        echo -e "\n${BLUE}📊 Setting up Monitoring...${NC}"
        echo -e "${YELLOW}This will install:${NC}"
        echo "• n8n workflow automation"
        echo "• Grafana dashboards"
        echo "• Prometheus monitoring"
        echo ""
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./scripts/setup-monitoring.sh
        else
            echo "Monitoring setup cancelled."
        fi
        ;;
    4)
        echo -e "\n${BLUE}🔍 Checking Deployment Status...${NC}"
        ./scripts/check-deployment.sh
        ;;
    5)
        echo -e "\n${BLUE}📖 Opening Deployment Guide...${NC}"
        if command -v less &> /dev/null; then
            less DEPLOYMENT_GUIDE.md
        else
            cat DEPLOYMENT_GUIDE.md
        fi
        ;;
    6)
        echo -e "\n${YELLOW}👋 Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}❌ Invalid option. Please choose 1-6.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✅ Operation completed!${NC}"
echo ""
echo -e "${BLUE}📚 Quick Reference:${NC}"
echo "• Configuration: ./scripts/update-config.sh"
echo "• Full Deploy: ./scripts/test-and-deploy.sh"
echo "• Check Status: ./scripts/check-deployment.sh"
echo "• Setup Monitoring: ./scripts/setup-monitoring.sh"
echo "• View Guide: cat DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${YELLOW}🌐 After deployment, access your platform at:${NC}"
echo "• Website: https://consulting.sa"
echo "• API: https://consulting.sa/api"
echo "• n8n: http://217.79.255.54:5678"
echo "• Grafana: http://217.79.255.54:3001"
echo ""
echo -e "${GREEN}🎉 Your Agentic AI Platform is ready to go!${NC}"