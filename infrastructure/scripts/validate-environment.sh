#!/bin/bash

# 🚀 ENVIRONMENT CONFIGURATION VALIDATION SCRIPT
# This script validates environment configuration for systematic deployment
# 
# LESSONS LEARNED INTEGRATED:
# - Comprehensive validation of all required variables
# - Security checks for sensitive data
# - Network connectivity validation
# - Service availability checks
# - Configuration consistency validation
# - Environment-specific validation rules
#
# PREVENTS: Deployment failures due to missing or invalid configuration

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
LOG_FILE="/var/log/environment-validation.log"
ENV_FILE="${1:-.env}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Validation counters
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0
VALIDATION_PASSED=0

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; ((VALIDATION_WARNINGS++)); }
log_error() { log "ERROR" "$@"; ((VALIDATION_ERRORS++)); }
log_success() { log "SUCCESS" "$@"; ((VALIDATION_PASSED++)); }

# Validation functions
validate_file_exists() {
    log_info "Validating environment file existence..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Please copy .env.template to $ENV_FILE and configure it"
        exit 1
    fi
    
    log_success "Environment file found: $ENV_FILE"
}

# Load environment variables
load_environment() {
    log_info "Loading environment variables..."
    
    # Source the environment file
    set -a  # Automatically export all variables
    source "$ENV_FILE"
    set +a
    
    log_success "Environment variables loaded"
}

# Validate required variables
validate_required_variables() {
    log_info "Validating required environment variables..."
    
    # Core required variables
    local required_vars=(
        "PROJECT_NAME"
        "ENVIRONMENT"
        "VPS_HOST"
        "DOMAIN"
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_ROLE_KEY"
        "GOOGLE_API_KEY"
        "JWT_SECRET"
        "ENCRYPTION_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required variable not set: $var"
        else
            log_success "Required variable set: $var"
        fi
    done
    
    # Environment-specific required variables
    if [[ "${ENVIRONMENT:-}" == "production" ]]; then
        local prod_required=(
            "SSL_CERT_PATH"
            "SSL_KEY_PATH"
            "PRODUCTION_DOMAIN"
        )
        
        for var in "${prod_required[@]}"; do
            if [[ -z "${!var:-}" ]]; then
                log_error "Production required variable not set: $var"
            else
                log_success "Production variable set: $var"
            fi
        done
    fi
}

# Validate variable formats and values
validate_variable_formats() {
    log_info "Validating variable formats and values..."
    
    # Validate PROJECT_NAME format
    if [[ -n "${PROJECT_NAME:-}" ]]; then
        if [[ "$PROJECT_NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
            log_success "PROJECT_NAME format is valid: $PROJECT_NAME"
        else
            log_error "PROJECT_NAME format is invalid (use lowercase, hyphens allowed): $PROJECT_NAME"
        fi
    fi
    
    # Validate ENVIRONMENT value
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        case "$ENVIRONMENT" in
            production|development|staging)
                log_success "ENVIRONMENT value is valid: $ENVIRONMENT"
                ;;
            *)
                log_error "ENVIRONMENT value is invalid (must be: production, development, or staging): $ENVIRONMENT"
                ;;
        esac
    fi
    
    # Validate VPS_HOST format (IP address or hostname)
    if [[ -n "${VPS_HOST:-}" ]]; then
        if [[ "$VPS_HOST" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]] || [[ "$VPS_HOST" =~ ^[a-zA-Z0-9.-]+$ ]]; then
            log_success "VPS_HOST format is valid: $VPS_HOST"
        else
            log_error "VPS_HOST format is invalid: $VPS_HOST"
        fi
    fi
    
    # Validate DOMAIN format
    if [[ -n "${DOMAIN:-}" ]]; then
        if [[ "$DOMAIN" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            log_success "DOMAIN format is valid: $DOMAIN"
        else
            log_error "DOMAIN format is invalid: $DOMAIN"
        fi
    fi
    
    # Validate SUPABASE_URL format
    if [[ -n "${SUPABASE_URL:-}" ]]; then
        if [[ "$SUPABASE_URL" =~ ^https://[a-zA-Z0-9-]+\.supabase\.co$ ]]; then
            log_success "SUPABASE_URL format is valid"
        else
            log_error "SUPABASE_URL format is invalid (should be https://project-id.supabase.co)"
        fi
    fi
    
    # Validate email formats
    local email_vars=("ADMIN_EMAIL" "SUPPORT_EMAIL" "FROM_EMAIL" "ALERT_EMAIL")
    for var in "${email_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            if [[ "${!var}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                log_success "Email format valid: $var"
            else
                log_error "Email format invalid: $var = ${!var}"
            fi
        fi
    done
}

# Validate security requirements
validate_security_requirements() {
    log_info "Validating security requirements..."
    
    # Validate JWT_SECRET length
    if [[ -n "${JWT_SECRET:-}" ]]; then
        if [[ ${#JWT_SECRET} -ge 32 ]]; then
            log_success "JWT_SECRET length is adequate (${#JWT_SECRET} characters)"
        else
            log_error "JWT_SECRET is too short (${#JWT_SECRET} characters, minimum 32 required)"
        fi
    fi
    
    # Validate ENCRYPTION_KEY length
    if [[ -n "${ENCRYPTION_KEY:-}" ]]; then
        if [[ ${#ENCRYPTION_KEY} -eq 32 ]]; then
            log_success "ENCRYPTION_KEY length is correct (32 characters)"
        else
            log_error "ENCRYPTION_KEY length is incorrect (${#ENCRYPTION_KEY} characters, exactly 32 required)"
        fi
    fi
    
    # Validate SESSION_SECRET length
    if [[ -n "${SESSION_SECRET:-}" ]]; then
        if [[ ${#SESSION_SECRET} -ge 32 ]]; then
            log_success "SESSION_SECRET length is adequate (${#SESSION_SECRET} characters)"
        else
            log_error "SESSION_SECRET is too short (${#SESSION_SECRET} characters, minimum 32 required)"
        fi
    fi
    
    # Check for default/placeholder values
    local sensitive_vars=(
        "VPS_PASSWORD:your_vps_password_here"
        "SUPABASE_ANON_KEY:your_supabase_anon_key_here"
        "SUPABASE_SERVICE_ROLE_KEY:your_supabase_service_role_key_here"
        "GOOGLE_API_KEY:your_google_gemini_api_key_here"
        "JWT_SECRET:your_very_long_and_secure_jwt_secret_here"
        "ENCRYPTION_KEY:your_32_character_encryption_key_here"
    )
    
    for var_check in "${sensitive_vars[@]}"; do
        local var_name="${var_check%%:*}"
        local placeholder="${var_check##*:}"
        
        if [[ -n "${!var_name:-}" && "${!var_name}" == "$placeholder" ]]; then
            log_error "Variable contains placeholder value: $var_name"
        elif [[ -n "${!var_name:-}" ]]; then
            log_success "Variable configured: $var_name"
        fi
    done
}

# Validate network connectivity
validate_network_connectivity() {
    log_info "Validating network connectivity..."
    
    # Test VPS connectivity
    if [[ -n "${VPS_HOST:-}" ]]; then
        if ping -c 1 -W 5 "$VPS_HOST" &> /dev/null; then
            log_success "VPS host is reachable: $VPS_HOST"
        else
            log_error "VPS host is not reachable: $VPS_HOST"
        fi
    fi
    
    # Test domain resolution
    if [[ -n "${DOMAIN:-}" ]]; then
        if nslookup "$DOMAIN" &> /dev/null; then
            log_success "Domain resolves: $DOMAIN"
        else
            log_warn "Domain does not resolve (may not be configured yet): $DOMAIN"
        fi
    fi
    
    # Test Supabase connectivity
    if [[ -n "${SUPABASE_URL:-}" ]]; then
        if curl -s --max-time 10 "$SUPABASE_URL/rest/v1/" &> /dev/null; then
            log_success "Supabase is reachable: $SUPABASE_URL"
        else
            log_warn "Supabase is not reachable (check URL and network): $SUPABASE_URL"
        fi
    fi
}

# Validate file permissions and paths
validate_file_permissions() {
    log_info "Validating file permissions and paths..."
    
    # Check SSL certificate files (if specified)
    if [[ -n "${SSL_CERT_PATH:-}" ]]; then
        if [[ -f "$SSL_CERT_PATH" ]]; then
            if [[ -r "$SSL_CERT_PATH" ]]; then
                log_success "SSL certificate file is readable: $SSL_CERT_PATH"
            else
                log_error "SSL certificate file is not readable: $SSL_CERT_PATH"
            fi
        else
            log_warn "SSL certificate file not found (may not be deployed yet): $SSL_CERT_PATH"
        fi
    fi
    
    if [[ -n "${SSL_KEY_PATH:-}" ]]; then
        if [[ -f "$SSL_KEY_PATH" ]]; then
            if [[ -r "$SSL_KEY_PATH" ]]; then
                log_success "SSL private key file is readable: $SSL_KEY_PATH"
                
                # Check permissions (should be 600 or 400)
                local perms=$(stat -c "%a" "$SSL_KEY_PATH")
                if [[ "$perms" == "600" || "$perms" == "400" ]]; then
                    log_success "SSL private key has correct permissions: $perms"
                else
                    log_warn "SSL private key permissions should be 600 or 400, currently: $perms"
                fi
            else
                log_error "SSL private key file is not readable: $SSL_KEY_PATH"
            fi
        else
            log_warn "SSL private key file not found (may not be deployed yet): $SSL_KEY_PATH"
        fi
    fi
    
    # Check SSH key path (if specified)
    if [[ -n "${SSH_KEY_PATH:-}" ]]; then
        if [[ -f "$SSH_KEY_PATH" ]]; then
            if [[ -r "$SSH_KEY_PATH" ]]; then
                log_success "SSH key file is readable: $SSH_KEY_PATH"
                
                # Check permissions (should be 600 or 400)
                local perms=$(stat -c "%a" "$SSH_KEY_PATH")
                if [[ "$perms" == "600" || "$perms" == "400" ]]; then
                    log_success "SSH key has correct permissions: $perms"
                else
                    log_warn "SSH key permissions should be 600 or 400, currently: $perms"
                fi
            else
                log_error "SSH key file is not readable: $SSH_KEY_PATH"
            fi
        else
            log_warn "SSH key file not found: $SSH_KEY_PATH"
        fi
    fi
}

# Validate port configurations
validate_port_configurations() {
    log_info "Validating port configurations..."
    
    # Define expected ports for each environment
    local prod_ports=("3000" "8000" "6379" "5678")
    local dev_ports=("3001" "8001" "6380" "5679")
    
    if [[ "${ENVIRONMENT:-}" == "production" ]]; then
        for port in "${prod_ports[@]}"; do
            if ss -tuln | grep -q ":$port "; then
                log_warn "Production port $port is already in use"
            else
                log_success "Production port $port is available"
            fi
        done
    elif [[ "${ENVIRONMENT:-}" == "development" ]]; then
        for port in "${dev_ports[@]}"; do
            if ss -tuln | grep -q ":$port "; then
                log_warn "Development port $port is already in use"
            else
                log_success "Development port $port is available"
            fi
        done
    fi
    
    # Validate custom port configurations
    local port_vars=("DEV_FRONTEND_PORT" "DEV_BACKEND_PORT" "DEV_REDIS_PORT" "DEV_N8N_PORT")
    for var in "${port_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            if [[ "${!var}" =~ ^[0-9]+$ ]] && [[ "${!var}" -ge 1024 ]] && [[ "${!var}" -le 65535 ]]; then
                log_success "Port configuration valid: $var = ${!var}"
            else
                log_error "Port configuration invalid: $var = ${!var} (must be 1024-65535)"
            fi
        fi
    done
}

# Validate service configurations
validate_service_configurations() {
    log_info "Validating service configurations..."
    
    # Validate Redis configuration
    if [[ -n "${REDIS_URL:-}" ]]; then
        if [[ "$REDIS_URL" =~ ^redis://.*:[0-9]+$ ]]; then
            log_success "Redis URL format is valid"
        else
            log_error "Redis URL format is invalid: $REDIS_URL"
        fi
    fi
    
    # Validate N8N configuration
    if [[ -n "${N8N_BASIC_AUTH_USER:-}" && -n "${N8N_BASIC_AUTH_PASSWORD:-}" ]]; then
        if [[ ${#N8N_BASIC_AUTH_PASSWORD} -ge 8 ]]; then
            log_success "N8N authentication configured with adequate password length"
        else
            log_error "N8N password is too short (${#N8N_BASIC_AUTH_PASSWORD} characters, minimum 8 required)"
        fi
    else
        log_warn "N8N authentication not configured (recommended for security)"
    fi
    
    # Validate monitoring configuration
    if [[ "${PROMETHEUS_ENABLED:-}" == "true" ]]; then
        if [[ -n "${PROMETHEUS_PORT:-}" ]]; then
            log_success "Prometheus monitoring is enabled"
        else
            log_error "Prometheus enabled but port not specified"
        fi
    fi
    
    if [[ "${GRAFANA_ENABLED:-}" == "true" ]]; then
        if [[ -n "${GRAFANA_PORT:-}" && -n "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
            log_success "Grafana monitoring is properly configured"
        else
            log_error "Grafana enabled but missing port or admin password"
        fi
    fi
}

# Validate backup configuration
validate_backup_configuration() {
    log_info "Validating backup configuration..."
    
    if [[ "${BACKUP_ENABLED:-}" == "true" ]]; then
        # Validate backup schedule format (cron)
        if [[ -n "${BACKUP_SCHEDULE:-}" ]]; then
            # Basic cron format validation (5 fields)
            if [[ "$BACKUP_SCHEDULE" =~ ^[0-9*,-/]+[[:space:]]+[0-9*,-/]+[[:space:]]+[0-9*,-/]+[[:space:]]+[0-9*,-/]+[[:space:]]+[0-9*,-/]+$ ]]; then
                log_success "Backup schedule format is valid: $BACKUP_SCHEDULE"
            else
                log_error "Backup schedule format is invalid: $BACKUP_SCHEDULE"
            fi
        else
            log_error "Backup enabled but schedule not specified"
        fi
        
        # Validate retention days
        if [[ -n "${BACKUP_RETENTION_DAYS:-}" ]]; then
            if [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] && [[ "$BACKUP_RETENTION_DAYS" -gt 0 ]]; then
                log_success "Backup retention is valid: $BACKUP_RETENTION_DAYS days"
            else
                log_error "Backup retention is invalid: $BACKUP_RETENTION_DAYS"
            fi
        else
            log_error "Backup enabled but retention days not specified"
        fi
        
        # Validate S3 configuration if specified
        if [[ -n "${S3_BUCKET:-}" ]]; then
            if [[ -n "${S3_ACCESS_KEY:-}" && -n "${S3_SECRET_KEY:-}" ]]; then
                log_success "S3 backup configuration appears complete"
            else
                log_error "S3 bucket specified but access credentials missing"
            fi
        fi
    else
        log_warn "Backup is disabled (consider enabling for production)"
    fi
}

# Generate validation report
generate_validation_report() {
    local report_file="/opt/environment-validation-report.txt"
    
    cat > "$report_file" << EOF
=== ENVIRONMENT VALIDATION REPORT ===
Date: $(date)
Script Version: $SCRIPT_VERSION
Environment File: $ENV_FILE

=== VALIDATION SUMMARY ===
✅ Passed: $VALIDATION_PASSED
⚠️  Warnings: $VALIDATION_WARNINGS
❌ Errors: $VALIDATION_ERRORS

=== ENVIRONMENT CONFIGURATION ===
Project Name: ${PROJECT_NAME:-"Not set"}
Environment: ${ENVIRONMENT:-"Not set"}
VPS Host: ${VPS_HOST:-"Not set"}
Domain: ${DOMAIN:-"Not set"}

=== SECURITY STATUS ===
JWT Secret Length: ${#JWT_SECRET:-0} characters
Encryption Key Length: ${#ENCRYPTION_KEY:-0} characters
Session Secret Length: ${#SESSION_SECRET:-0} characters

=== SERVICE STATUS ===
Supabase: $(if [[ -n "${SUPABASE_URL:-}" ]]; then echo "Configured"; else echo "Not configured"; fi)
Google AI: $(if [[ -n "${GOOGLE_API_KEY:-}" ]]; then echo "Configured"; else echo "Not configured"; fi)
Stripe: $(if [[ -n "${STRIPE_SECRET_KEY:-}" ]]; then echo "Configured"; else echo "Not configured"; fi)
Livekit: $(if [[ -n "${LIVEKIT_API_KEY:-}" ]]; then echo "Configured"; else echo "Not configured"; fi)
N8N: $(if [[ -n "${N8N_BASIC_AUTH_USER:-}" ]]; then echo "Configured"; else echo "Not configured"; fi)

=== MONITORING STATUS ===
Prometheus: $(if [[ "${PROMETHEUS_ENABLED:-}" == "true" ]]; then echo "Enabled"; else echo "Disabled"; fi)
Grafana: $(if [[ "${GRAFANA_ENABLED:-}" == "true" ]]; then echo "Enabled"; else echo "Disabled"; fi)
Backup: $(if [[ "${BACKUP_ENABLED:-}" == "true" ]]; then echo "Enabled"; else echo "Disabled"; fi)

=== RECOMMENDATIONS ===
$(if [[ $VALIDATION_ERRORS -gt 0 ]]; then
    echo "❌ Fix all errors before deployment"
fi)
$(if [[ $VALIDATION_WARNINGS -gt 0 ]]; then
    echo "⚠️  Review warnings for potential issues"
fi)
$(if [[ "${ENVIRONMENT:-}" == "production" && "${BACKUP_ENABLED:-}" != "true" ]]; then
    echo "💾 Enable backups for production environment"
fi)
$(if [[ -z "${SSL_CERT_PATH:-}" || -z "${SSL_KEY_PATH:-}" ]]; then
    echo "🔒 Configure SSL certificates for HTTPS"
fi)

=== NEXT STEPS ===
1. Fix any validation errors
2. Review and address warnings
3. Test connectivity to external services
4. Deploy SSL certificates if needed
5. Run deployment scripts

=== LOG FILE ===
Detailed validation log: $LOG_FILE

EOF
    
    log_success "Validation report generated: $report_file"
}

# Main execution function
main() {
    echo -e "${PURPLE}🚀 ENVIRONMENT CONFIGURATION VALIDATION${NC}"
    echo -e "${BLUE}📋 Version: $SCRIPT_VERSION${NC}"
    echo -e "${BLUE}📅 Date: $(date)${NC}"
    echo -e "${BLUE}📁 Environment File: $ENV_FILE${NC}"
    echo ""
    
    log_info "Starting environment validation..."
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Execute validation steps
    validate_file_exists
    load_environment
    validate_required_variables
    validate_variable_formats
    validate_security_requirements
    validate_network_connectivity
    validate_file_permissions
    validate_port_configurations
    validate_service_configurations
    validate_backup_configuration
    generate_validation_report
    
    echo ""
    echo -e "${PURPLE}📊 VALIDATION SUMMARY${NC}"
    echo -e "${GREEN}✅ Passed: $VALIDATION_PASSED${NC}"
    echo -e "${YELLOW}⚠️  Warnings: $VALIDATION_WARNINGS${NC}"
    echo -e "${RED}❌ Errors: $VALIDATION_ERRORS${NC}"
    echo ""
    
    if [[ $VALIDATION_ERRORS -eq 0 ]]; then
        echo -e "${GREEN}🎉 ENVIRONMENT VALIDATION PASSED!${NC}"
        echo -e "${BLUE}📋 Validation report: /opt/environment-validation-report.txt${NC}"
        echo -e "${BLUE}📋 Validation log: $LOG_FILE${NC}"
        echo ""
        echo -e "${YELLOW}✅ Your environment is ready for deployment${NC}"
        
        if [[ $VALIDATION_WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}⚠️  Please review warnings for optimal configuration${NC}"
        fi
        
        exit 0
    else
        echo -e "${RED}❌ ENVIRONMENT VALIDATION FAILED!${NC}"
        echo -e "${RED}Please fix $VALIDATION_ERRORS error(s) before deployment${NC}"
        echo -e "${BLUE}📋 Validation report: /opt/environment-validation-report.txt${NC}"
        echo -e "${BLUE}📋 Validation log: $LOG_FILE${NC}"
        echo ""
        echo -e "${YELLOW}🔧 Common fixes:${NC}"
        echo "1. Update placeholder values in $ENV_FILE"
        echo "2. Ensure all required variables are set"
        echo "3. Check variable formats and lengths"
        echo "4. Verify network connectivity"
        echo "5. Configure SSL certificates"
        
        exit 1
    fi
}

# Execute main function
main "$@"