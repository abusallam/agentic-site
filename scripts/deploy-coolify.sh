#!/bin/bash

# Coolify Deployment Script for AI SaaS Platform
# This script prepares and deploys the application to Coolify

set -e

echo "🚀 Preparing AI SaaS Platform for Coolify Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the project root."
    exit 1
fi

# Check if required files exist
print_status "Checking required files..."

required_files=(
    "Dockerfile.simple"
    "coolify.json"
    "next.config.mjs"
    ".env.example"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found!"
        exit 1
    fi
done

print_success "All required files found"

# Validate environment variables
print_status "Validating environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please update .env with your actual values before deployment"
fi

# Check if critical environment variables are set
critical_vars=(
    "NEXT_PUBLIC_SUPABASE_URL"
    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    "GEMINI_API_KEY"
)

missing_vars=()
for var in "${critical_vars[@]}"; do
    if ! grep -q "^$var=" .env 2>/dev/null || grep -q "^$var=$" .env 2>/dev/null; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    print_warning "The following critical environment variables are missing or empty:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    print_warning "Please update your .env file before deployment"
fi

# Test build locally (optional)
if [ "$1" = "--test-build" ]; then
    print_status "Testing local build..."
    
    if command -v docker &> /dev/null; then
        print_status "Building Docker image locally..."
        docker build -f Dockerfile.simple -t ai-saas-platform:test .
        print_success "Local build successful"
        
        print_status "Testing container startup..."
        docker run --rm -d --name ai-saas-test -p 3001:3000 -p 8081:8080 ai-saas-platform:test
        
        # Wait for container to start
        sleep 30
        
        # Test health check
        if curl -f http://localhost:3001/api/health >/dev/null 2>&1; then
            print_success "Health check passed"
        else
            print_error "Health check failed"
            docker logs ai-saas-test
            docker stop ai-saas-test
            exit 1
        fi
        
        docker stop ai-saas-test
        print_success "Local test completed successfully"
    else
        print_warning "Docker not found. Skipping local build test."
    fi
fi

# Generate deployment summary
print_status "Generating deployment summary..."

cat << EOF

📋 DEPLOYMENT SUMMARY
====================

🏗️  Build Configuration:
   - Dockerfile: Dockerfile.simple
   - Framework: Next.js with Python backend
   - Port: 3000 (frontend), 8080 (backend)
   - Health Check: /api/health

🌐 Domain Configuration:
   - Primary: consulting.sa
   - WWW: www.consulting.sa
   - SSL: Enabled
   - Redirect: HTTP → HTTPS

🔧 Environment Variables Required:
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY
   - GEMINI_API_KEY
   - OPENAI_API_KEY (optional)
   - STRIPE_SECRET_KEY (optional)
   - LIVEKIT_URL (optional)
   - N8N_URL (optional)

📦 Resources:
   - Memory: 2GB
   - CPU: 1.0 core
   - Auto-scaling: Enabled

🔍 Health Check:
   - Path: /api/health
   - Interval: 30s
   - Timeout: 15s
   - Retries: 3

EOF

# Coolify deployment instructions
cat << EOF

🚀 COOLIFY DEPLOYMENT INSTRUCTIONS
==================================

1. Push your code to Git repository:
   git add .
   git commit -m "Deploy to Coolify"
   git push origin main

2. In Coolify Dashboard:
   - Create new application
   - Connect your Git repository
   - Select branch: main
   - Use Dockerfile: Dockerfile.simple

3. Set Environment Variables:
   - Go to Environment tab
   - Add all required variables from your .env file
   - Enable "Build Time" for NEXT_PUBLIC_* variables

4. Configure Domains:
   - Add consulting.sa
   - Add www.consulting.sa
   - Enable SSL
   - Enable redirect

5. Deploy:
   - Click "Deploy" button
   - Monitor logs for any issues
   - Test health check: https://consulting.sa/api/health

📊 Monitoring:
   - Frontend: https://consulting.sa
   - Admin: https://consulting.sa/admin/dashboard
   - Customer: https://consulting.sa/customer/dashboard
   - Health: https://consulting.sa/api/health

EOF

print_success "Deployment preparation completed!"
print_status "Your application is ready for Coolify deployment."

# Optional: Create deployment archive
if [ "$1" = "--archive" ]; then
    print_status "Creating deployment archive..."
    
    # Create temporary directory
    temp_dir=$(mktemp -d)
    
    # Copy necessary files
    rsync -av --exclude='node_modules' --exclude='.next' --exclude='.git' --exclude='agent/.venv' . "$temp_dir/"
    
    # Create archive
    cd "$temp_dir/.."
    tar -czf "ai-saas-platform-$(date +%Y%m%d-%H%M%S).tar.gz" "$(basename "$temp_dir")"
    
    print_success "Deployment archive created: ai-saas-platform-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    # Cleanup
    rm -rf "$temp_dir"
fi

echo ""
print_success "🎉 Ready for Coolify deployment!"
echo ""