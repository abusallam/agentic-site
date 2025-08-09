# Script Registry - Consulting.sa Project

## Current Active Scripts (Verified Working)

### Deployment Scripts
| Script Name | Version | Date | Purpose | Status | Last Used |
|-------------|---------|------|---------|--------|-----------|
| `deploy-dev-v1-20250108.sh` | v1 | 2025-01-08 | Deploy development environment with UI enhancements | ✅ Active | - |

### SSH Access Scripts
| Script Name | Version | Date | Purpose | Status | Last Used |
|-------------|---------|------|---------|--------|-----------|
| `ssh-status-v1-20250108.sh` | v1 | 2025-01-08 | Check container status via SSH with prod/dev separation | ✅ Active | - |
| `ssh-logs-v1-20250108.sh` | v1 | 2025-01-08 | View container logs via SSH with safety warnings | ✅ Active | - |

### Docker Management Scripts
| Script Name | Version | Date | Purpose | Status | Last Used |
|-------------|---------|------|---------|--------|-----------|
| `docker-dev-restart-v1-20250108.sh` | v1 | 2025-01-08 | Safely restart development containers only | ✅ Active | - |
| `docker-stack-migrate-v1-20250108.sh` | v1 | 2025-01-08 | Plan/execute migration to Docker stacks | 🚧 Planned | - |

### Health Check Scripts
| Script Name | Version | Date | Purpose | Status | Last Used |
|-------------|---------|------|---------|--------|-----------|
| `health-check-v1-20250108.sh` | v1 | 2025-01-08 | Comprehensive health check for all environments | ✅ Active | - |

## Deprecated Scripts (To Be Archived)
- All scripts in `infrastructure/scripts/` without version numbers
- Scripts with generic names like "deploy.sh", "fix-*.sh"

## Script Categories

### 1. Deployment Scripts (`/scripts/deployment/`)
- Production deployment
- Development deployment  
- Staging deployment
- Rollback procedures

### 2. SSH Management Scripts (`/scripts/ssh/`)
- Container status checks
- Log viewing
- Remote command execution
- Connection testing

### 3. Docker Management Scripts (`/scripts/docker/`)
- Container lifecycle management
- Stack management (future)
- Image building and pushing
- Volume and network management

### 4. Monitoring Scripts (`/scripts/monitoring/`)
- Health checks
- Performance monitoring
- Alert management
- Log analysis

### 5. Maintenance Scripts (`/scripts/maintenance/`)
- Database backups
- SSL certificate renewal
- System cleanup
- Security updates

## Usage Guidelines

### Script Naming Convention
```bash
{category}-{purpose}-v{version}-{YYYYMMDD}.sh
```

Examples:
- `deploy-dev-v1-20250108.sh`
- `ssh-status-v2-20250108.sh`
- `docker-stack-migrate-v1-20250108.sh`

### Script Header Template
```bash
#!/bin/bash
# Script: {script-name}
# Version: v{version}
# Date: {YYYY-MM-DD}
# Purpose: {clear description}
# Usage: ./{script-name} [parameters]
# Author: AI Assistant
# Last Modified: {date}
#
# Changelog:
# v1 - Initial version
```

## Server Information
- **VPS IP**: 217.79.255.54
- **SSH User**: root
- **SSH Password**: gnqLG7FDd4 (stored in SERVER_ACCESS.md)
- **Production Ports**: 3000, 8000, 6379, 5678
- **Development Ports**: 3001, 8001, 6380, 5679

## Container Information
### Production Containers (DO NOT TOUCH)
- `agentic-frontend-prod` (port 3000)
- `agentic-backend-prod` (port 8000)
- `agentic-redis-prod` (port 6379)
- `agentic-n8n-prod` (port 5678)

### Development Containers (SAFE TO MODIFY)
- `agentic-frontend-dev` (port 3001)
- `agentic-backend-dev` (port 8001)
- `agentic-redis-dev` (port 6380)
- `agentic-n8n-dev` (port 5679)

---

**Last Updated**: January 8, 2025  
**Maintained By**: AI Assistant  
**Review Cycle**: Updated with each script creation/modification