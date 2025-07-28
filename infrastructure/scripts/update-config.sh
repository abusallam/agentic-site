#!/bin/bash

# Configuration Update Script
# This script helps you update the .env file with your actual values

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Configuration Update Script${NC}"
echo "This script will help you update your .env file with the correct values."
echo ""

# Function to update env variable
update_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$(grep "^$var_name=" .env | cut -d'=' -f2-)
    
    echo -e "${YELLOW}$var_description${NC}"
    echo "Current value: $current_value"
    read -p "Enter new value (or press Enter to keep current): " new_value
    
    if [ -n "$new_value" ]; then
        # Escape special characters for sed
        escaped_value=$(echo "$new_value" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i "s|^$var_name=.*|$var_name=$escaped_value|" .env
        echo -e "${GREEN}✓ Updated $var_name${NC}"
    else
        echo -e "${BLUE}→ Keeping current value${NC}"
    fi
    echo ""
}

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found. Creating from template...${NC}"
    cp .env.example .env
fi

echo -e "${BLUE}Updating database configuration...${NC}"
update_env_var "SUPABASE_URL" "Supabase Project URL (e.g., https://your-project.supabase.co)"
update_env_var "SUPABASE_ANON_KEY" "Supabase Anonymous Key"
update_env_var "SUPABASE_SERVICE_KEY" "Supabase Service Role Key (optional)"
update_env_var "DATABASE_URL" "Database URL (usually same as Supabase URL)"

echo -e "${BLUE}Updating AI configuration...${NC}"
update_env_var "GEMINI_API_KEY" "Google Gemini API Key"

echo -e "${BLUE}Updating GitHub configuration...${NC}"
update_env_var "GITHUB_TOKEN" "GitHub Personal Access Token (for CI/CD)"
update_env_var "GITHUB_REPOSITORY" "GitHub Repository (e.g., username/repo-name)"

echo -e "${BLUE}Updating security configuration...${NC}"
update_env_var "JWT_SECRET" "JWT Secret Key (generate a random string)"
update_env_var "ENCRYPTION_KEY" "Encryption Key (generate a random string)"

echo -e "${BLUE}Optional: Updating additional services...${NC}"
read -p "Do you want to configure optional services (Livekit, Stripe)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    update_env_var "LIVEKIT_URL" "Livekit Server URL (optional)"
    update_env_var "LIVEKIT_API_KEY" "Livekit API Key (optional)"
    update_env_var "LIVEKIT_SECRET_KEY" "Livekit Secret Key (optional)"
    update_env_var "STRIPE_SECRET_KEY" "Stripe Secret Key (optional)"
    update_env_var "STRIPE_WEBHOOK_SECRET" "Stripe Webhook Secret (optional)"
fi

echo -e "${GREEN}✅ Configuration update completed!${NC}"
echo ""
echo -e "${BLUE}Current configuration summary:${NC}"
echo "VPS Host: $(grep '^VPS_HOST=' .env | cut -d'=' -f2-)"
echo "Domain: $(grep '^DOMAIN=' .env | cut -d'=' -f2-)"
echo "Supabase URL: $(grep '^SUPABASE_URL=' .env | cut -d'=' -f2-)"
echo "Gemini API: $(grep '^GEMINI_API_KEY=' .env | cut -d'=' -f2- | sed 's/./*/g')"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review your .env file: cat .env"
echo "2. Run the test and deploy script: ./scripts/test-and-deploy.sh"
echo "3. Monitor the deployment process"
echo ""
echo -e "${BLUE}To run deployment:${NC}"
echo "./scripts/test-and-deploy.sh"