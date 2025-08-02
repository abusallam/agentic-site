#!/bin/bash

# 🧹 Project Cleanup Script
# This script cleans up unnecessary files and organizes the project structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Project Cleanup Script${NC}"
echo -e "${BLUE}========================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to safely remove files/directories
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        rm -rf "$path"
        print_status 0 "Removed $description"
    else
        print_status 1 "$description not found"
    fi
}

print_section "Phase 1: Cleaning Build Artifacts"

echo -e "${CYAN}🗑️ Removing build artifacts...${NC}"
safe_remove ".next" "Next.js build directory"
safe_remove ".swc" "SWC cache directory"
safe_remove "frontend/.next" "Frontend Next.js build directory"
safe_remove "frontend/.swc" "Frontend SWC cache directory"
safe_remove "frontend/tsconfig.tsbuildinfo" "TypeScript build info"
safe_remove "frontend/out" "Static export directory"
safe_remove "frontend/dist" "Distribution directory"
safe_remove "frontend/coverage" "Test coverage directory"

print_section "Phase 2: Cleaning Node Modules"

echo -e "${CYAN}📦 Cleaning node_modules...${NC}"
safe_remove "node_modules" "Root node_modules"
safe_remove "frontend/node_modules" "Frontend node_modules"

print_section "Phase 3: Cleaning Python Artifacts"

echo -e "${CYAN}🐍 Cleaning Python artifacts...${NC}"
safe_remove ".venv" "Python virtual environment"
safe_remove "__pycache__" "Python cache directories"
safe_remove "backend/__pycache__" "Backend Python cache"
safe_remove "backend/agent/__pycache__" "Agent Python cache"
safe_remove "backend/.pytest_cache" "Backend pytest cache"
safe_remove "backend/.coverage" "Backend coverage file"
safe_remove "backend/htmlcov" "Backend HTML coverage"

print_section "Phase 4: Cleaning Docker Artifacts"

echo -e "${CYAN}🐳 Cleaning Docker artifacts...${NC}"
safe_remove ".dockerignore" "Docker ignore file (will recreate)"
safe_remove "Dockerfile" "Root Dockerfile (if exists)"

print_section "Phase 5: Cleaning Temporary Files"

echo -e "${CYAN}📄 Cleaning temporary files...${NC}"
safe_remove "*.log" "Log files"
safe_remove "*.tmp" "Temporary files"
safe_remove "*.temp" "Temporary files"
safe_remove ".DS_Store" "macOS system files"
safe_remove "Thumbs.db" "Windows system files"

print_section "Phase 6: Cleaning Documentation Duplicates"

echo -e "${CYAN}📚 Cleaning documentation duplicates...${NC}"
safe_remove "docs/project-status" "Old project status docs"
safe_remove "docs/development" "Old development docs"

print_section "Phase 7: Cleaning Archive and Backup Directories"

echo -e "${CYAN}📦 Cleaning archive directories...${NC}"
safe_remove "archive" "Archive directory"
safe_remove "frontend/app-backup-disabled" "Disabled app backup"
safe_remove "home" "Home directory (if not needed)"
safe_remove "~" "Tilde directory (if not needed)"

print_section "Phase 8: Regenerating Lock Files"

echo -e "${CYAN}🔒 Regenerating lock files...${NC}"

# Regenerate frontend package-lock.json
if [ -f "frontend/package.json" ]; then
    echo "Regenerating frontend package-lock.json..."
    cd frontend
    npm install
    cd ..
    print_status 0 "Frontend package-lock.json regenerated"
else
    print_status 1 "Frontend package.json not found"
fi

# Regenerate root package-lock.json if needed
if [ -f "package.json" ]; then
    echo "Regenerating root package-lock.json..."
    npm install
    print_status 0 "Root package-lock.json regenerated"
else
    print_status 1 "Root package.json not found"
fi

# Regenerate uv.lock if uv is available
if command -v uv &> /dev/null; then
    echo "Regenerating uv.lock..."
    if [ -f "backend/pyproject.toml" ]; then
        cd backend
        uv sync
        cd ..
        print_status 0 "Backend uv.lock regenerated"
    fi
    
    if [ -f "backend/agent/pyproject.toml" ]; then
        cd backend/agent
        uv sync
        cd ../..
        print_status 0 "Agent uv.lock regenerated"
    fi
else
    print_status 1 "uv package manager not available"
fi

print_section "Phase 9: Updating .gitignore"

echo -e "${CYAN}📝 Updating .gitignore...${NC}"

# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
*/node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov
.nyc_output
.pytest_cache/
htmlcov/

# Next.js
.next/
out/
dist/
*.tsbuildinfo

# Production
build/
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# Deployment
deployment*.tar.gz
EOF

print_status 0 ".gitignore updated"

print_section "Phase 10: Creating .dockerignore"

echo -e "${CYAN}🐳 Creating .dockerignore...${NC}"

cat > .dockerignore << 'EOF'
node_modules
npm-debug.log
.next
.git
.gitignore
README.md
.env
.nyc_output
coverage
.nyc_output
.pytest_cache
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis
.pytest_cache
.venv
venv
ENV
env.bak
venv.bak
.idea
.vscode
*.swp
*.swo
*~
.DS_Store
Thumbs.db
EOF

print_status 0 ".dockerignore created"

print_section "Phase 11: Final Validation"

echo -e "${CYAN}🔍 Running final validation...${NC}"

# Check if essential files exist
ESSENTIAL_FILES=(
    "package.json"
    "frontend/package.json"
    "backend/pyproject.toml"
    "backend/agent/pyproject.toml"
    "infrastructure/docker/docker-compose.development.yml"
    "infrastructure/docker/Dockerfile.frontend"
    "infrastructure/docker/Dockerfile.backend"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "$file exists"
    else
        print_status 1 "$file missing"
    fi
done

echo ""
echo -e "${BLUE}📊 Cleanup Summary${NC}"
echo -e "${BLUE}==================${NC}"
echo -e "${GREEN}✅ Project cleanup completed successfully!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "1. Run: ${YELLOW}./infrastructure/scripts/pre-deployment-check.sh${NC}"
echo -e "2. Run: ${YELLOW}cd frontend && npm run build${NC}"
echo -e "3. Run: ${YELLOW}./infrastructure/scripts/deploy-development-fixed.sh${NC}"
echo ""
echo -e "${GREEN}🎉 Your project is now clean and organized!${NC}" 