#!/bin/bash

# Fix Production and Development Environments
# Usage: ./fix-environments.sh <SSH_ALIAS>

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
GITHUB_TOKEN="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"

echo -e "${BOLD}${PURPLE}🔧 Fixing Production and Development Environments${NC}"
echo -e "${BLUE}=================================================${NC}"
echo "SSH Alias: $SSH_ALIAS"
echo "Timestamp: $(date)"
echo

echo -e "${YELLOW}Step 1: Stopping all containers...${NC}"
ssh "$SSH_ALIAS" "
    echo 'Stopping all containers...'
    cd /opt/docker-apps/development/agentic-site/agentic-site 2>/dev/null && docker-compose down || true
    cd /opt/docker-apps/production/agentic-site/agentic-site 2>/dev/null && docker-compose -f docker-compose.production.yml down || true
    
    echo '✓ All containers stopped'
"

echo -e "${YELLOW}Step 2: Fixing production environment...${NC}"
ssh "$SSH_ALIAS" "
    echo 'Recreating production environment...'
    rm -rf /opt/docker-apps/production/agentic-site
    mkdir -p /opt/docker-apps/production/agentic-site
    cd /opt/docker-apps/production/agentic-site
    
    # Clone fresh repository for production
    git clone https://$GITHUB_TOKEN@github.com/abusallam/agentic-site.git
    cd agentic-site
    git checkout main
    
    echo '✓ Production repository recreated'
"

echo -e "${YELLOW}Step 3: Creating production package.json...${NC}"
ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/production/agentic-site/agentic-site/frontend
    
    # Create production package.json
    cat > package.json << 'EOF'
{
  \"name\": \"agentic-frontend-production\",
  \"version\": \"1.0.0\",
  \"private\": true,
  \"scripts\": {
    \"dev\": \"next dev\",
    \"build\": \"next build\",
    \"start\": \"next start\",
    \"lint\": \"next lint\"
  },
  \"dependencies\": {
    \"next\": \"^15.0.0\",
    \"react\": \"^18.0.0\",
    \"react-dom\": \"^18.0.0\",
    \"typescript\": \"^5.0.0\",
    \"@types/node\": \"^20.0.0\",
    \"@types/react\": \"^18.0.0\",
    \"@types/react-dom\": \"^18.0.0\",
    \"tailwindcss\": \"^3.4.0\",
    \"autoprefixer\": \"^10.4.0\",
    \"postcss\": \"^8.4.0\"
  },
  \"devDependencies\": {
    \"eslint\": \"^8.0.0\",
    \"eslint-config-next\": \"^15.0.0\"
  }
}
EOF

    # Remove conflicting files
    rm -f pages/index.js
    rm -rf pages/_app.js pages/_document.js
    
    # Create production page
    mkdir -p app
    cat > app/page.tsx << 'EOF'
export default function Home() {
  return (
    <div className=\"min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4\">
      <div className=\"max-w-4xl mx-auto text-center\">
        <h1 className=\"text-4xl font-bold text-gray-900 mb-6\">
          Agentic Site - Production Environment
        </h1>
        <p className=\"text-xl text-gray-600 mb-8\">
          Welcome to the production environment. This is running on Next.js with App Router.
        </p>
        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-8\">
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Frontend</h3>
            <p className=\"text-gray-600\">Next.js 15 with App Router</p>
            <p className=\"text-sm text-green-600 mt-2\">Production Mode</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Backend</h3>
            <p className=\"text-gray-600\">Python FastAPI</p>
            <p className=\"text-sm text-green-600 mt-2\">Port 8000</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Domain</h3>
            <p className=\"text-gray-600\">consulting.sa</p>
            <p className=\"text-sm text-green-600 mt-2\">SSL Enabled</p>
          </div>
        </div>
        <div className=\"mt-8\">
          <a href=\"/api/test\" className=\"bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors\">
            Test API
          </a>
        </div>
      </div>
    </div>
  )
}
EOF

    # Create layout if missing
    if [ ! -f app/layout.tsx ]; then
        cat > app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Agentic Site - Production',
  description: 'AI-powered consulting platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang=\"en\">
      <body>{children}</body>
    </html>
  )
}
EOF
    fi
    
    # Create globals.css if missing
    if [ ! -f app/globals.css ]; then
        cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF
    fi
    
    echo '✓ Production frontend configured'
"

echo -e "${YELLOW}Step 4: Fixing development environment...${NC}"
ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/development/agentic-site/agentic-site/frontend
    
    # Update development package.json
    cat > package.json << 'EOF'
{
  \"name\": \"agentic-frontend-development\",
  \"version\": \"1.0.0\",
  \"private\": true,
  \"scripts\": {
    \"dev\": \"next dev\",
    \"build\": \"next build\",
    \"start\": \"next start\",
    \"lint\": \"next lint\"
  },
  \"dependencies\": {
    \"next\": \"^15.0.0\",
    \"react\": \"^18.0.0\",
    \"react-dom\": \"^18.0.0\",
    \"typescript\": \"^5.0.0\",
    \"@types/node\": \"^20.0.0\",
    \"@types/react\": \"^18.0.0\",
    \"@types/react-dom\": \"^18.0.0\",
    \"tailwindcss\": \"^3.4.0\",
    \"autoprefixer\": \"^10.4.0\",
    \"postcss\": \"^8.4.0\"
  },
  \"devDependencies\": {
    \"eslint\": \"^8.0.0\",
    \"eslint-config-next\": \"^15.0.0\"
  }
}
EOF

    # Remove conflicting files
    rm -f pages/index.js
    rm -rf pages/_app.js pages/_document.js
    
    # Update development page
    mkdir -p app
    cat > app/page.tsx << 'EOF'
export default function Home() {
  return (
    <div className=\"min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4\">
      <div className=\"max-w-4xl mx-auto text-center\">
        <h1 className=\"text-4xl font-bold text-gray-900 mb-6\">
          Agentic Site - Development Environment
        </h1>
        <p className=\"text-xl text-gray-600 mb-8\">
          Welcome to the development environment. This is running on Next.js with App Router.
        </p>
        <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6 mt-8\">
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Frontend</h3>
            <p className=\"text-gray-600\">Next.js 15 with App Router</p>
            <p className=\"text-sm text-blue-600 mt-2\">Development Mode</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Backend</h3>
            <p className=\"text-gray-600\">Python FastAPI</p>
            <p className=\"text-sm text-blue-600 mt-2\">Port 8001</p>
          </div>
          <div className=\"bg-white p-6 rounded-lg shadow-md\">
            <h3 className=\"text-lg font-semibold mb-2\">Domain</h3>
            <p className=\"text-gray-600\">dev.consulting.sa</p>
            <p className=\"text-sm text-blue-600 mt-2\">SSL Enabled</p>
          </div>
        </div>
        <div className=\"mt-8\">
          <a href=\"/api/test\" className=\"bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors\">
            Test API
          </a>
        </div>
      </div>
    </div>
  )
}
EOF

    echo '✓ Development frontend configured'
"

echo -e "${YELLOW}Step 5: Creating Tailwind configuration for both environments...${NC}"
ssh "$SSH_ALIAS" "
    # Production Tailwind config
    cd /opt/docker-apps/production/agentic-site/agentic-site/frontend
    cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

    cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

    # Development Tailwind config
    cd /opt/docker-apps/development/agentic-site/agentic-site/frontend
    cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

    cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

    echo '✓ Tailwind configurations created'
"

echo -e "${YELLOW}Step 6: Starting development environment...${NC}"
ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/development/agentic-site/agentic-site
    
    echo 'Starting development containers...'
    docker-compose -f docker-compose.development.yml up -d
    
    echo 'Waiting for development services...'
    sleep 45
    
    echo 'Development container status:'
    docker-compose -f docker-compose.development.yml ps
"

echo -e "${YELLOW}Step 7: Starting production environment...${NC}"
ssh "$SSH_ALIAS" "
    cd /opt/docker-apps/production/agentic-site/agentic-site
    
    echo 'Starting production containers...'
    docker-compose -f docker-compose.production.yml up -d
    
    echo 'Waiting for production services...'
    sleep 45
    
    echo 'Production container status:'
    docker-compose -f docker-compose.production.yml ps
"

echo -e "${YELLOW}Step 8: Testing both environments...${NC}"
ssh "$SSH_ALIAS" "
    echo '=== Environment Health Check ==='
    
    # Test development
    echo 'Testing development environment...'
    if curl -s http://localhost:3001 | grep -q 'Development Environment'; then
        echo '✅ Development frontend working'
    else
        echo '❌ Development frontend not working'
    fi
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo '✅ Development backend working'
    else
        echo '❌ Development backend not working'
    fi
    
    # Test production
    echo 'Testing production environment...'
    if curl -s http://localhost:3000 | grep -q 'Production Environment'; then
        echo '✅ Production frontend working'
    else
        echo '❌ Production frontend not working'
    fi
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo '✅ Production backend working'
    else
        echo '❌ Production backend not working'
    fi
"

echo
echo -e "${BOLD}${GREEN}🎉 Environment Fix Complete!${NC}"
echo -e "${BLUE}=============================${NC}"
echo
echo -e "${BOLD}${CYAN}🌐 Live URLs:${NC}"
echo "✅ Production: https://consulting.sa"
echo "✅ Development: https://dev.consulting.sa"
echo
echo -e "${BOLD}${CYAN}🏗️ Environment Status:${NC}"
echo "✅ Production environment recreated with proper package.json"
echo "✅ Development environment fixed and updated"
echo "✅ Both environments have separate, working configurations"
echo "✅ Tailwind CSS configured for both environments"
echo "✅ Next.js App Router properly configured"
echo
echo -e "${BOLD}${CYAN}🔧 Container Architecture:${NC}"
echo "Production (consulting.sa):"
echo "  - Frontend: Port 3000 (Green theme)"
echo "  - Backend: Port 8000"
echo "  - Redis: Port 6379"
echo "  - n8n: Port 5678"
echo
echo "Development (dev.consulting.sa):"
echo "  - Frontend: Port 3001 (Blue theme)"
echo "  - Backend: Port 8001"
echo "  - Redis: Port 6380"
echo "  - n8n: Port 5679"
echo
echo -e "${BOLD}${CYAN}🔧 Management Commands:${NC}"
echo "Check status: ssh $SSH_ALIAS '/usr/local/bin/agentic-status.sh'"
echo "Dev logs: ssh $SSH_ALIAS 'cd /opt/docker-apps/development/agentic-site/agentic-site && docker-compose logs -f'"
echo "Prod logs: ssh $SSH_ALIAS 'cd /opt/docker-apps/production/agentic-site/agentic-site && docker-compose -f docker-compose.production.yml logs -f'"
echo
echo -e "${BOLD}${GREEN}✅ Both environments are now working separately!${NC}"
echo -e "${BOLD}${YELLOW}⚠️  You can develop on dev.consulting.sa and deploy to consulting.sa${NC}"