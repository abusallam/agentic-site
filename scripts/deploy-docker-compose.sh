#!/bin/bash

# Docker Compose Deployment Script for Coolify
# Deploys the AI SaaS Platform using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

print_status "🚀 Preparing AI SaaS Platform for Docker Compose Deployment"

# Validate required files
required_files=(
    "docker-compose.yml"
    "docker-compose.coolify.yml"
    "Dockerfile.frontend"
    "Dockerfile.backend"
    "Dockerfile.migrate"
    ".env.example"
)

print_status "Checking required files..."
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found!"
        exit 1
    fi
done
print_success "All required files found"

# Check environment file
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please update .env with your actual values before deployment"
fi

# Validate critical environment variables
print_status "Validating environment configuration..."
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
    print_status "Testing local Docker Compose build..."
    
    if command -v docker-compose &> /dev/null; then
        print_status "Building services..."
        docker-compose build
        print_success "Build completed successfully"
        
        print_status "Testing services startup..."
        docker-compose up -d
        
        # Wait for services to start
        sleep 60
        
        # Test health checks
        print_status "Testing health checks..."
        
        # Test frontend
        if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
            print_success "Frontend health check passed"
        else
            print_error "Frontend health check failed"
            docker-compose logs frontend
            docker-compose down
            exit 1
        fi
        
        # Test backend
        if curl -f http://localhost:8080/api/health >/dev/null 2>&1; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check failed"
            docker-compose logs backend
            docker-compose down
            exit 1
        fi
        
        docker-compose down
        print_success "Local test completed successfully"
    else
        print_error "docker-compose not found. Please install Docker Compose."
        exit 1
    fi
fi

# Generate deployment summary
print_status "Generating deployment summary..."

cat << EOF

📋 DOCKER COMPOSE DEPLOYMENT SUMMARY
====================================

🏗️  Architecture:
   - Frontend: Next.js (Port 3000)
   - Backend: Python Agent (Port 8080)
   - Migration: Database setup (One-time)

🐳 Docker Services:
   - ai-saas-frontend: Next.js application
   - ai-saas-backend: Python agent system
   - ai-saas-migrate: Database migration

🌐 Network Configuration:
   - Internal communication between services
   - Frontend exposed on port 3000
   - Backend internal on port 8080

🔍 Health Checks:
   - Frontend: /api/health (port 3000)
   - Backend: /api/health (port 8080)
   - Interval: 30s, Timeout: 10s

📦 Resource Configuration:
   - Memory: 1GB per service
   - CPU: 0.5 cores per service
   - Auto-restart: unless-stopped

EOF

# Coolify deployment instructions
cat << EOF

🚀 COOLIFY DOCKER COMPOSE DEPLOYMENT
====================================

1. Push your code to Git repository:
   git add .
   git commit -m "Docker Compose deployment ready"
   git push origin main

2. In Coolify Dashboard:
   - Create new application
   - Select "Docker Compose" as deployment type
   - Connect your Git repository
   - Select branch: main
   - Use compose file: docker-compose.yml

3. Environment Variables:
   Add these in Coolify Environment tab:
   
   Required:
   - NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   - NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
   - GEMINI_API_KEY=your_gemini_key
   
   Optional:
   - OPENAI_API_KEY=your_openai_key
   - STRIPE_SECRET_KEY=your_stripe_key
   - LIVEKIT_URL=your_livekit_url
   - N8N_URL=your_n8n_url
   - GITHUB_TOKEN=your_github_token

4. Domain Configuration:
   - Primary domain: consulting.sa
   - WWW redirect: www.consulting.sa
   - SSL: Enabled
   - Auto-redirect HTTP to HTTPS

5. Deploy:
   - Click "Deploy" button
   - Monitor build logs
   - Wait for all services to be healthy

📊 Service Monitoring:
   - Frontend: https://consulting.sa
   - Health Check: https://consulting.sa/api/health
   - Admin Panel: https://consulting.sa/admin/dashboard
   - Customer Portal: https://consulting.sa/customer/dashboard

🔧 Local Development:
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop services
   docker-compose down
   
   # Rebuild services
   docker-compose build --no-cache

EOF

print_success "Docker Compose deployment preparation completed!"
print_status "Your application is ready for Coolify deployment using Docker Compose."

# Optional: Create deployment archive
if [ "$1" = "--archive" ]; then
    print_status "Creating deployment archive..."
    
    timestamp=$(date +%Y%m%d-%H%M%S)
    archive_name="ai-saas-docker-compose-$timestamp.tar.gz"
    
    # Create temporary directory
    temp_dir=$(mktemp -d)
    
    # Copy necessary files
    rsync -av \
        --exclude='node_modules' \
        --exclude='.next' \
        --exclude='.git' \
        --exclude='agent/.venv' \
        --exclude='*.log' \
        . "$temp_dir/"
    
    # Create archive
    cd "$temp_dir/.."
    tar -czf "$archive_name" "$(basename "$temp_dir")"
    mv "$archive_name" "$OLDPWD/"
    
    print_success "Deployment archive created: $archive_name"
    
    # Cleanup
    rm -rf "$temp_dir"
fi

echo ""
print_success "🎉 Ready for Coolify Docker Compose deployment!"
echo ""

# Display quick commands
cat << EOF
🚀 QUICK DEPLOYMENT COMMANDS
============================

# Test locally:
./scripts/deploy-docker-compose.sh --test-build

# Deploy to Coolify:
1. git push origin main
2. Create Docker Compose app in Coolify
3. Set environment variables
4. Deploy and monitor

# Local development:
docker-compose up -d          # Start services
docker-compose logs -f        # View logs
docker-compose down           # Stop services

EOF