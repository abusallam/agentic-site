# Design Document

## Overview

This design addresses the systematic restoration and troubleshooting of the deployment environment. The solution focuses on container health restoration, environment isolation, and deployment process reliability while maintaining zero downtime for production services.

## Architecture

### Current State Analysis
- **Production**: `consulting-frontend-prod` (unhealthy), `consulting-backend-prod` (healthy)
- **Development**: Missing `agentic-frontend-dev` and `agentic-backend-dev`, `agentic-site-n8n-dev-1` (unhealthy), `agentic-site-redis-dev-1` (healthy)
- **Issues**: Container naming inconsistency, missing dev containers, unhealthy containers

### Target Architecture
```
Production Environment (Port Range: 3000-5999)
├── agentic-frontend-prod (3000) - Next.js Application
├── agentic-backend-prod (8000) - Python ADK Agent
├── agentic-redis-prod (6379) - Redis Cache
└── agentic-n8n-prod (5678) - N8N Workflow Engine

Development Environment (Port Range: 3001-5999 + offset)
├── agentic-frontend-dev (3001) - Next.js Application
├── agentic-backend-dev (8001) - Python ADK Agent
├── agentic-redis-dev (6380) - Redis Cache
└── agentic-n8n-dev (5679) - N8N Workflow Engine
```

## Components and Interfaces

### 1. Container Health Diagnostic System
```bash
# Health Check Interface
check_container_health() {
    container_name=$1
    health_status=$(docker inspect --format='{{.State.Health.Status}}' $container_name)
    return $health_status
}
```

### 2. Environment Restoration Engine
```bash
# Development Environment Restoration
restore_development_environment() {
    # Stop and remove existing dev containers
    # Recreate with proper configuration
    # Validate health and connectivity
}
```

### 3. Container Naming Standardization
```bash
# Naming Convention: agentic-[service]-[environment]
NAMING_PATTERN="agentic-{service}-{environment}"
SERVICES=("frontend" "backend" "redis" "n8n")
ENVIRONMENTS=("prod" "dev")
```

### 4. Deployment Validation Framework
```bash
# Pre-deployment Checks
validate_prerequisites() {
    check_docker_daemon()
    check_network_connectivity()
    check_port_availability()
    check_environment_variables()
}
```

## Data Models

### Container Configuration Model
```yaml
container_config:
  name: string (agentic-{service}-{environment})
  image: string
  ports: array
  environment: object
  health_check:
    test: string
    interval: duration
    timeout: duration
    retries: integer
  restart_policy: string
```

### Environment State Model
```yaml
environment_state:
  name: string (prod|dev)
  containers:
    - name: string
      status: string (running|stopped|unhealthy)
      health: string (healthy|unhealthy|none)
      ports: array
  network:
    isolation: boolean
    port_conflicts: array
```

## Error Handling

### Container Health Recovery
1. **Detection**: Automated health check monitoring
2. **Diagnosis**: Log analysis and resource inspection
3. **Recovery**: Graduated response (restart → recreate → rebuild)
4. **Validation**: Post-recovery health verification

### Environment Isolation Protection
1. **Validation**: Pre-operation environment checks
2. **Safeguards**: Production container protection locks
3. **Monitoring**: Cross-environment impact detection
4. **Rollback**: Automatic reversion on isolation breach

### Deployment Failure Handling
1. **Pre-flight**: Comprehensive prerequisite validation
2. **Atomic Operations**: All-or-nothing deployment steps
3. **Progress Tracking**: Detailed step-by-step logging
4. **Rollback**: Automatic restoration to last known good state

## Testing Strategy

### Health Check Testing
```bash
# Container Health Validation
test_container_health() {
    for container in $(get_all_containers); do
        assert_healthy $container
        assert_responsive $container
    done
}
```

### Environment Isolation Testing
```bash
# Environment Separation Validation
test_environment_isolation() {
    assert_no_port_conflicts()
    assert_separate_networks()
    assert_independent_operation()
}
```

### Deployment Process Testing
```bash
# End-to-End Deployment Validation
test_deployment_process() {
    backup_current_state()
    run_deployment()
    validate_all_services()
    run_integration_tests()
}
```

## Implementation Phases

### Phase 1: Diagnostic and Assessment
- Container health analysis
- Environment state mapping
- Issue root cause identification
- Recovery strategy planning

### Phase 2: Development Environment Restoration
- Stop unhealthy dev containers
- Remove inconsistent containers
- Recreate with standardized naming
- Validate full dev environment functionality

### Phase 3: Production Health Resolution
- Analyze production frontend health issues
- Implement zero-downtime health restoration
- Validate production service continuity
- Update monitoring and alerting

### Phase 4: Standardization and Validation
- Implement consistent naming across all containers
- Update management scripts for new naming
- Comprehensive testing of both environments
- Documentation and process validation

## Security Considerations

### Access Control
- SSH key-based authentication for server access
- Container-level access restrictions
- Environment-specific permission boundaries

### Data Protection
- Environment variable encryption
- Secure container communication
- Audit logging for all operations

### Network Security
- Port isolation between environments
- Firewall rules for service access
- SSL/TLS termination at proxy level