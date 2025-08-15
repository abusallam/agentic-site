#!/bin/bash
# Script: validate-deployment-v1-20250814.sh
# Version: v1
# Date: 2025-08-14
# Purpose: Comprehensive deployment validation for both production and development environments
# Usage: ./validate-deployment-v1-20250814.sh [prod|dev|all]
# Author: AI Assistant
# Last Modified: 2025-08-14
#
# Changelog:
# v1 - Initial version with comprehensive validation

set -e

# Configuration
VPS_IP="217.79.255.54"
SSH_USER="root"
SSH_PASS="gnqLG7FDd4"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to execute SSH commands
ssh_exec() {
    sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${VPS_IP}" "$1"
}

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ ${message}${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ ${message}${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  ${message}${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  ${message}${NC}"
            ;;
    esac
}

# Function to validate container health
validate_container() {
    local container_name=$1
    local environment=$2
    
    print_status "INFO" "Validating container: ${container_name}"
    
    # Check if container exists and is running
    if ! ssh_exec "docker ps --format '{{.Names}}' | grep -q '^${container_name}$'"; then
        print_status "ERROR" "Container ${container_name} is not running"
        return 1
    fi
    
    # Check container health status
    local health_status=$(ssh_exec "docker inspect --format='{{.State.Health.Status}}' ${container_name} 2>/dev/null || echo 'no-healthcheck'")
    
    case $health_status in
        "healthy")
            print_status "SUCCESS" "Container ${container_name} is healthy"
            ;;
        "unhealthy")
            print_status "ERROR" "Container ${container_name} is unhealthy"
            return 1
            ;;
        "starting")
            print_status "WARNING" "Container ${container_name} health check is starting"
            ;;
        "no-healthcheck")
            print_status "WARNING" "Container ${container_name} has no health check configured"
            ;;
        *)
            print_status "WARNING" "Container ${container_name} health status unknown: ${health_status}"
            ;;
    esac
    
    return 0
}

# Function to validate service endpoints
validate_endpoints() {
    local environment=$1
    
    print_status "INFO" "Validating service endpoints for ${environment}"
    
    case $environment in
        "production")
            # Test production frontend
            if curl -s -o /dev/null -w "%{http_code}" https://consulting.sa | grep -q "200"; then
                print_status "SUCCESS" "Production frontend (https://consulting.sa) is accessible"
            else
                print_status "ERROR" "Production frontend (https://consulting.sa) is not accessible"
            fi
            
            # Test production backend
            if curl -s -o /dev/null -w "%{http_code}" http://217.79.255.54:8000/health | grep -q "200"; then
                print_status "SUCCESS" "Production backend (port 8000) is accessible"
            else
                print_status "ERROR" "Production backend (port 8000) is not accessible"
            fi
            ;;
        "development")
            # Test development frontend
            if curl -s -o /dev/null -w "%{http_code}" https://dev.consulting.sa | grep -q "200"; then
                print_status "SUCCESS" "Development frontend (https://dev.consulting.sa) is accessible"
            else
                print_status "ERROR" "Development frontend (https://dev.consulting.sa) is not accessible"
            fi
            
            # Test development backend
            if curl -s -o /dev/null -w "%{http_code}" http://217.79.255.54:8001/health | grep -q "200"; then
                print_status "SUCCESS" "Development backend (port 8001) is accessible"
            else
                print_status "ERROR" "Development backend (port 8001) is not accessible"
            fi
            
            # Test development n8n
            if curl -s -o /dev/null -w "%{http_code}" http://217.79.255.54:5679 | grep -q "200"; then
                print_status "SUCCESS" "Development n8n (port 5679) is accessible"
            else
                print_status "ERROR" "Development n8n (port 5679) is not accessible"
            fi
            ;;
    esac
}

# Function to validate system resources
validate_system_resources() {
    print_status "INFO" "Validating system resources"
    
    # Check disk usage
    local disk_usage=$(ssh_exec "df -h / | tail -1 | awk '{print \$5}' | sed 's/%//'")
    if [ "$disk_usage" -lt 80 ]; then
        print_status "SUCCESS" "Disk usage is acceptable (${disk_usage}%)"
    elif [ "$disk_usage" -lt 90 ]; then
        print_status "WARNING" "Disk usage is high (${disk_usage}%)"
    else
        print_status "ERROR" "Disk usage is critical (${disk_usage}%)"
    fi
    
    # Check memory usage
    local memory_info=$(ssh_exec "free -h | grep Mem")
    print_status "INFO" "Memory usage: ${memory_info}"
    
    # Check load average
    local load_avg=$(ssh_exec "uptime | awk '{print \$(NF-2) \" \" \$(NF-1) \" \" \$NF}'")
    print_status "INFO" "Load average: ${load_avg}"
}

# Function to validate environment
validate_environment() {
    local environment=$1
    local validation_errors=0
    
    print_status "INFO" "Starting ${environment} environment validation"
    echo "----------------------------------------"
    
    case $environment in
        "production")
            # Validate production containers
            validate_container "agentic-frontend-prod" "production" || ((validation_errors++))
            validate_container "agentic-backend-prod" "production" || ((validation_errors++))
            validate_container "agentic-redis-prod" "production" || ((validation_errors++))
            
            # Validate production endpoints
            validate_endpoints "production" || ((validation_errors++))
            ;;
        "development")
            # Validate development containers
            validate_container "agentic-frontend-dev" "development" || ((validation_errors++))
            validate_container "agentic-backend-dev" "development" || ((validation_errors++))
            validate_container "agentic-redis-dev" "development" || ((validation_errors++))
            validate_container "agentic-n8n-dev" "development" || ((validation_errors++))
            
            # Validate development endpoints
            validate_endpoints "development" || ((validation_errors++))
            ;;
    esac
    
    echo "----------------------------------------"
    if [ $validation_errors -eq 0 ]; then
        print_status "SUCCESS" "${environment} environment validation completed successfully"
    else
        print_status "ERROR" "${environment} environment validation failed with ${validation_errors} errors"
    fi
    
    return $validation_errors
}

# Main execution
main() {
    local environment=${1:-"all"}
    local total_errors=0
    
    echo "🔍 Deployment Validation v1 - $(date)"
    echo "📍 Server: ${VPS_IP}"
    echo "🎯 Environment: ${environment}"
    echo "========================================"
    
    # Validate system resources first
    validate_system_resources
    echo ""
    
    case $environment in
        "prod"|"production")
            validate_environment "production"
            total_errors=$?
            ;;
        "dev"|"development")
            validate_environment "development"
            total_errors=$?
            ;;
        "all"|*)
            validate_environment "production"
            prod_errors=$?
            echo ""
            validate_environment "development"
            dev_errors=$?
            total_errors=$((prod_errors + dev_errors))
            ;;
    esac
    
    echo ""
    echo "========================================"
    if [ $total_errors -eq 0 ]; then
        print_status "SUCCESS" "All validations passed successfully!"
        echo "🎉 Deployment is healthy and operational"
    else
        print_status "ERROR" "Validation completed with ${total_errors} errors"
        echo "🚨 Please review and fix the issues above"
        exit 1
    fi
    
    echo "✅ Validation completed - $(date)"
}

# Execute main function with all arguments
main "$@"