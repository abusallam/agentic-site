#!/bin/bash
set -e

# Deployment Hooks Script
# This script handles deployment lifecycle hooks and integrates with the agent

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
DEPLOYMENT_ID=${2:-$(date +%Y%m%d-%H%M%S)}
COMMIT_SHA=${3:-$(git rev-parse HEAD 2>/dev/null || echo "unknown")}
BRANCH=${4:-$(git branch --show-current 2>/dev/null || echo "unknown")}

# Agent API configuration
AGENT_URL=${AGENT_URL:-"http://localhost:8000"}
AGENT_API_KEY=${AGENT_API_KEY:-""}

echo -e "${BLUE}🚀 Running deployment hooks for environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Deployment ID: $DEPLOYMENT_ID${NC}"
echo -e "${YELLOW}Commit SHA: $COMMIT_SHA${NC}"
echo -e "${YELLOW}Branch: $BRANCH${NC}"

# Function to call agent API
call_agent_api() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-"{}"}
    
    local headers="-H 'Content-Type: application/json'"
    if [ -n "$AGENT_API_KEY" ]; then
        headers="$headers -H 'Authorization: Bearer $AGENT_API_KEY'"
    fi
    
    curl -s -X "$method" \
        $headers \
        -d "$data" \
        "$AGENT_URL$endpoint" || echo "{\"error\": \"API call failed\"}"
}

# Function to trigger deployment event in agent
trigger_deployment_event() {
    local event_type=$1
    local additional_data=${2:-"{}"}
    
    echo -e "${BLUE}Triggering deployment event: $event_type${NC}"
    
    local payload=$(cat <<EOF
{
    "action": "trigger_deployment",
    "event_type": "$event_type",
    "environment": "$ENVIRONMENT",
    "commit_sha": "$COMMIT_SHA",
    "branch": "$BRANCH",
    "deployment_id": "$DEPLOYMENT_ID",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "additional_data": $additional_data
}
EOF
)
    
    local result=$(call_agent_api "/api/tools/deployment_manager" "POST" "$payload")
    echo "Agent response: $result"
    
    # Check if the call was successful
    if echo "$result" | grep -q '"success": true'; then
        echo -e "${GREEN}✓ Deployment event triggered successfully${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Deployment event trigger failed or agent unavailable${NC}"
        return 1
    fi
}

# Function to validate workflows
validate_deployment_workflows() {
    echo -e "${BLUE}Validating deployment workflows...${NC}"
    
    local payload=$(cat <<EOF
{
    "action": "validate_workflows",
    "environment": "$ENVIRONMENT"
}
EOF
)
    
    local result=$(call_agent_api "/api/tools/deployment_manager" "POST" "$payload")
    echo "Validation result: $result"
    
    if echo "$result" | grep -q '"success": true'; then
        echo -e "${GREEN}✓ Workflow validation passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Workflow validation failed or incomplete${NC}"
        return 1
    fi
}

# Function to sync customer workflows
sync_customer_workflows() {
    local customer_ids=${1:-""}
    
    if [ -z "$customer_ids" ]; then
        echo -e "${YELLOW}No specific customers to sync, skipping customer workflow sync${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Syncing customer workflows...${NC}"
    
    # Split customer IDs and sync each
    IFS=',' read -ra CUSTOMERS <<< "$customer_ids"
    for customer_id in "${CUSTOMERS[@]}"; do
        customer_id=$(echo "$customer_id" | xargs) # trim whitespace
        
        local payload=$(cat <<EOF
{
    "action": "sync_customer_workflows",
    "customer_id": "$customer_id",
    "deployment_data": {
        "environment": "$ENVIRONMENT",
        "commit_sha": "$COMMIT_SHA",
        "branch": "$BRANCH",
        "deployment_id": "$DEPLOYMENT_ID",
        "version": "$(git describe --tags --always 2>/dev/null || echo 'unknown')"
    }
}
EOF
)
        
        local result=$(call_agent_api "/api/tools/deployment_manager" "POST" "$payload")
        
        if echo "$result" | grep -q '"success": true'; then
            echo -e "${GREEN}✓ Customer $customer_id workflows synced${NC}"
        else
            echo -e "${YELLOW}⚠ Failed to sync workflows for customer $customer_id${NC}"
        fi
    done
}

# Function to check deployment status
check_deployment_status() {
    echo -e "${BLUE}Checking deployment status...${NC}"
    
    local payload=$(cat <<EOF
{
    "action": "check_deployment_status",
    "deployment_id": "$DEPLOYMENT_ID"
}
EOF
)
    
    local result=$(call_agent_api "/api/tools/deployment_manager" "POST" "$payload")
    echo "Deployment status: $result"
    
    # Extract status from result
    local status=$(echo "$result" | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
    echo -e "${BLUE}Current status: $status${NC}"
    
    return 0
}

# Function to handle deployment failure
handle_deployment_failure() {
    local reason=${1:-"Deployment failed"}
    
    echo -e "${RED}❌ Deployment failed: $reason${NC}"
    
    # Trigger failure event
    local failure_data=$(cat <<EOF
{
    "failure_reason": "$reason",
    "failed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
)
    
    trigger_deployment_event "deployment_failed" "$failure_data"
    
    # Optionally trigger rollback
    if [ "${AUTO_ROLLBACK:-false}" = "true" ]; then
        echo -e "${YELLOW}Initiating automatic rollback...${NC}"
        rollback_deployment "$reason"
    fi
}

# Function to rollback deployment
rollback_deployment() {
    local reason=${1:-"Manual rollback"}
    
    echo -e "${YELLOW}🔄 Rolling back deployment...${NC}"
    
    local payload=$(cat <<EOF
{
    "action": "rollback_deployment",
    "deployment_id": "$DEPLOYMENT_ID",
    "reason": "$reason"
}
EOF
)
    
    local result=$(call_agent_api "/api/tools/deployment_manager" "POST" "$payload")
    
    if echo "$result" | grep -q '"success": true'; then
        echo -e "${GREEN}✓ Rollback initiated successfully${NC}"
    else
        echo -e "${RED}❌ Rollback failed${NC}"
    fi
}

# Main deployment hook logic
main() {
    local hook_type=${DEPLOYMENT_HOOK:-"post_deploy"}
    
    case $hook_type in
        "pre_deploy")
            echo -e "${BLUE}Running pre-deployment hooks...${NC}"
            
            # Validate workflows before deployment
            if ! validate_deployment_workflows; then
                echo -e "${YELLOW}⚠ Workflow validation issues detected, but continuing...${NC}"
            fi
            
            # Trigger pre-deployment event
            trigger_deployment_event "deployment_started"
            ;;
            
        "post_deploy")
            echo -e "${BLUE}Running post-deployment hooks...${NC}"
            
            # Trigger successful deployment event
            if trigger_deployment_event "deployment_success"; then
                echo -e "${GREEN}✓ Deployment event processed${NC}"
            fi
            
            # Sync customer workflows if specified
            sync_customer_workflows "$CUSTOMER_IDS"
            
            # Check final deployment status
            check_deployment_status
            ;;
            
        "deploy_failed")
            echo -e "${RED}Running failure hooks...${NC}"
            handle_deployment_failure "${FAILURE_REASON:-Deployment failed}"
            ;;
            
        "rollback")
            echo -e "${YELLOW}Running rollback hooks...${NC}"
            rollback_deployment "${ROLLBACK_REASON:-Manual rollback requested}"
            ;;
            
        "health_check")
            echo -e "${BLUE}Running health check hooks...${NC}"
            
            # Trigger health check workflows
            local health_data=$(cat <<EOF
{
    "check_type": "post_deployment",
    "services": ["frontend", "backend", "database"]
}
EOF
)
            trigger_deployment_event "health_check" "$health_data"
            ;;
            
        *)
            echo -e "${RED}Unknown hook type: $hook_type${NC}"
            echo "Available hooks: pre_deploy, post_deploy, deploy_failed, rollback, health_check"
            exit 1
            ;;
    esac
}

# Trap errors and handle deployment failures
trap 'handle_deployment_failure "Script error occurred"' ERR

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --deployment-id)
            DEPLOYMENT_ID="$2"
            shift 2
            ;;
        --commit-sha)
            COMMIT_SHA="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --hook-type)
            DEPLOYMENT_HOOK="$2"
            shift 2
            ;;
        --customer-ids)
            CUSTOMER_IDS="$2"
            shift 2
            ;;
        --agent-url)
            AGENT_URL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --environment ENV        Deployment environment (default: staging)"
            echo "  --deployment-id ID       Deployment ID (default: timestamp)"
            echo "  --commit-sha SHA         Git commit SHA (default: current HEAD)"
            echo "  --branch BRANCH          Git branch (default: current branch)"
            echo "  --hook-type TYPE         Hook type (pre_deploy, post_deploy, deploy_failed, rollback, health_check)"
            echo "  --customer-ids IDS       Comma-separated customer IDs to sync"
            echo "  --agent-url URL          Agent API URL (default: http://localhost:8000)"
            echo "  --help                   Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  DEPLOYMENT_HOOK          Hook type to run"
            echo "  CUSTOMER_IDS             Customer IDs to sync"
            echo "  AGENT_URL                Agent API URL"
            echo "  AGENT_API_KEY            Agent API key for authentication"
            echo "  AUTO_ROLLBACK            Enable automatic rollback on failure (true/false)"
            echo "  FAILURE_REASON           Reason for deployment failure"
            echo "  ROLLBACK_REASON          Reason for rollback"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run main function
main

echo -e "${GREEN}🎉 Deployment hooks completed successfully${NC}"