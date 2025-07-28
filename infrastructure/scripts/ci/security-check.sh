#!/bin/bash
set -e

# Security Check Script for Local Development
# This script runs security checks locally before committing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 Running Security Checks...${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install missing tools
install_security_tools() {
    echo -e "${YELLOW}Installing security tools...${NC}"
    
    # Install npm audit (comes with npm)
    if ! command_exists npm; then
        echo -e "${RED}Error: npm is required but not installed${NC}"
        exit 1
    fi
    
    # Install safety for Python
    if ! command_exists safety; then
        echo "Installing safety..."
        pip install safety
    fi
    
    # Install semgrep
    if ! command_exists semgrep; then
        echo "Installing semgrep..."
        pip install semgrep
    fi
    
    # Install bandit for Python security
    if ! command_exists bandit; then
        echo "Installing bandit..."
        pip install bandit
    fi
    
    # Install trivy for container scanning
    if ! command_exists trivy; then
        echo "Installing trivy..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install trivy
        fi
    fi
}

# Check and install tools if needed
install_security_tools

# Initialize results
ISSUES_FOUND=0
RESULTS_DIR="security-results"
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}1. Frontend Dependency Security Scan${NC}"
echo "Running npm audit..."
if npm audit --audit-level=moderate > "$RESULTS_DIR/npm-audit.txt" 2>&1; then
    echo -e "${GREEN}✓ No high/critical vulnerabilities found in frontend dependencies${NC}"
else
    echo -e "${YELLOW}⚠ Vulnerabilities found in frontend dependencies${NC}"
    echo "See $RESULTS_DIR/npm-audit.txt for details"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo -e "\n${BLUE}2. Backend Dependency Security Scan${NC}"
echo "Running safety check..."
if [ -d "agent" ]; then
    cd agent
    if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        # Generate requirements.txt if using uv
        if command_exists uv && [ -f "pyproject.toml" ]; then
            uv export --format=requirements-txt > requirements.txt
        fi
        
        if safety check -r requirements.txt > "../$RESULTS_DIR/safety-check.txt" 2>&1; then
            echo -e "${GREEN}✓ No known vulnerabilities in backend dependencies${NC}"
        else
            echo -e "${YELLOW}⚠ Vulnerabilities found in backend dependencies${NC}"
            echo "See $RESULTS_DIR/safety-check.txt for details"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    else
        echo -e "${YELLOW}⚠ No requirements.txt or pyproject.toml found${NC}"
    fi
    cd ..
fi

echo -e "\n${BLUE}3. Static Code Analysis${NC}"
echo "Running semgrep..."
if semgrep --config=auto --json --output="$RESULTS_DIR/semgrep.json" . > /dev/null 2>&1; then
    # Check if any findings
    SEMGREP_FINDINGS=$(jq '.results | length' "$RESULTS_DIR/semgrep.json" 2>/dev/null || echo "0")
    if [ "$SEMGREP_FINDINGS" -eq 0 ]; then
        echo -e "${GREEN}✓ No security issues found by semgrep${NC}"
    else
        echo -e "${YELLOW}⚠ $SEMGREP_FINDINGS security issues found by semgrep${NC}"
        echo "See $RESULTS_DIR/semgrep.json for details"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠ Semgrep scan completed with warnings${NC}"
fi

echo -e "\n${BLUE}4. Python Security Analysis${NC}"
if [ -d "agent" ]; then
    echo "Running bandit..."
    if bandit -r agent/ -f json -o "$RESULTS_DIR/bandit.json" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ No security issues found by bandit${NC}"
    else
        echo -e "${YELLOW}⚠ Security issues found by bandit${NC}"
        echo "See $RESULTS_DIR/bandit.json for details"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

echo -e "\n${BLUE}5. Secrets Detection${NC}"
echo "Checking for potential secrets..."
SECRETS_FOUND=0

# Check for common secret patterns
if grep -r -E "(password|secret|key|token).*=.*['\"][^'\"]{20,}" . \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude-dir=.next \
    --exclude-dir=__pycache__ \
    --exclude="*.log" \
    --exclude="security-check.sh" > "$RESULTS_DIR/potential-secrets.txt" 2>/dev/null; then
    
    SECRETS_FOUND=$(wc -l < "$RESULTS_DIR/potential-secrets.txt")
    if [ "$SECRETS_FOUND" -gt 0 ]; then
        echo -e "${RED}⚠ $SECRETS_FOUND potential secrets found${NC}"
        echo "See $RESULTS_DIR/potential-secrets.txt for details"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${GREEN}✓ No obvious secrets detected${NC}"
fi

echo -e "\n${BLUE}6. Docker Security Scan${NC}"
if command_exists trivy && [ -f "Dockerfile.frontend" ]; then
    echo "Scanning Docker images..."
    
    # Build images for scanning
    if docker build -f Dockerfile.frontend -t agentic-frontend:security-scan . > /dev/null 2>&1; then
        if trivy image --format json --output "$RESULTS_DIR/trivy-frontend.json" agentic-frontend:security-scan > /dev/null 2>&1; then
            # Check for high/critical vulnerabilities
            HIGH_VULNS=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH" or .Severity == "CRITICAL")] | length' "$RESULTS_DIR/trivy-frontend.json" 2>/dev/null || echo "0")
            if [ "$HIGH_VULNS" -eq 0 ]; then
                echo -e "${GREEN}✓ No high/critical vulnerabilities in frontend image${NC}"
            else
                echo -e "${YELLOW}⚠ $HIGH_VULNS high/critical vulnerabilities in frontend image${NC}"
                ISSUES_FOUND=$((ISSUES_FOUND + 1))
            fi
        fi
        docker rmi agentic-frontend:security-scan > /dev/null 2>&1 || true
    fi
    
    if [ -f "agent/Dockerfile.backend" ]; then
        if docker build -f agent/Dockerfile.backend -t agentic-backend:security-scan agent/ > /dev/null 2>&1; then
            if trivy image --format json --output "$RESULTS_DIR/trivy-backend.json" agentic-backend:security-scan > /dev/null 2>&1; then
                HIGH_VULNS=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH" or .Severity == "CRITICAL")] | length' "$RESULTS_DIR/trivy-backend.json" 2>/dev/null || echo "0")
                if [ "$HIGH_VULNS" -eq 0 ]; then
                    echo -e "${GREEN}✓ No high/critical vulnerabilities in backend image${NC}"
                else
                    echo -e "${YELLOW}⚠ $HIGH_VULNS high/critical vulnerabilities in backend image${NC}"
                    ISSUES_FOUND=$((ISSUES_FOUND + 1))
                fi
            fi
            docker rmi agentic-backend:security-scan > /dev/null 2>&1 || true
        fi
    fi
else
    echo -e "${YELLOW}⚠ Trivy not available or Dockerfiles not found${NC}"
fi

echo -e "\n${BLUE}7. Configuration Security Check${NC}"
echo "Checking configuration files..."

# Check for insecure configurations
CONFIG_ISSUES=0

# Check for debug mode in production configs
if grep -r "debug.*=.*true" . --include="*.env*" --include="*.config.*" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Debug mode enabled in configuration files${NC}"
    CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
fi

# Check for default passwords
if grep -r -i "password.*=.*\(admin\|password\|123456\|default\)" . --include="*.env*" --include="*.config.*" > /dev/null 2>&1; then
    echo -e "${RED}⚠ Default passwords found in configuration${NC}"
    CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
fi

# Check for insecure protocols
if grep -r "http://" . --include="*.env*" --include="*.config.*" --exclude-dir=node_modules > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ HTTP URLs found (consider using HTTPS)${NC}"
    CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
fi

if [ "$CONFIG_ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✓ No obvious configuration security issues${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + CONFIG_ISSUES))
fi

# Generate summary report
echo -e "\n${BLUE}📊 Security Scan Summary${NC}"
echo "=========================="
echo "Scan completed at: $(date)"
echo "Total issues found: $ISSUES_FOUND"
echo ""
echo "Results saved in: $RESULTS_DIR/"
echo ""

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo -e "${GREEN}🎉 All security checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ $ISSUES_FOUND security issues found${NC}"
    echo ""
    echo "Recommendations:"
    echo "1. Review all findings in the $RESULTS_DIR/ directory"
    echo "2. Update vulnerable dependencies"
    echo "3. Fix any secrets or configuration issues"
    echo "4. Re-run this script after fixes"
    echo ""
    echo -e "${BLUE}To ignore non-critical issues and proceed:${NC}"
    echo "export SECURITY_IGNORE_WARNINGS=true"
    
    if [ "${SECURITY_IGNORE_WARNINGS:-false}" = "true" ]; then
        echo -e "${YELLOW}⚠ Proceeding despite warnings (SECURITY_IGNORE_WARNINGS=true)${NC}"
        exit 0
    else
        exit 1
    fi
fi