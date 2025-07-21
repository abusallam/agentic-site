# Design Document

## Overview

This design outlines a systematic approach to clean up the project structure by removing duplicate folders, properly organizing MCP files, and establishing a streamlined deployment workflow. The solution involves three main phases: local cleanup, MCP file organization on VPS, and Docker-based deployment setup.

## Architecture

### Current State Analysis
- Root project contains the main agentic site
- Duplicate `agentic-site/` folder exists with potentially different files
- MCP-related files are scattered in the project
- VPS deployment needs to be streamlined through Docker

### Target State
- Single clean project structure at root level
- MCP files properly organized in `/home/asim/Documents/agents-mcp` on VPS
- Clean development workflow: Local → GitHub → VPS Docker deployment
- All VPS operations performed via SSH connection

## Components and Interfaces

### 1. File Analysis Component
**Purpose**: Compare and identify differences between root and agentic-site folders

**Interface**:
- Input: File paths from both locations
- Output: List of duplicates, unique files, and conflicts
- Methods: `compare_directories()`, `identify_unique_files()`, `detect_conflicts()`

### 2. Cleanup Component
**Purpose**: Execute the cleanup process safely

**Interface**:
- Input: Analysis results from File Analysis Component
- Output: Clean project structure
- Methods: `backup_unique_files()`, `merge_configurations()`, `remove_duplicates()`

### 3. MCP Organization Component
**Purpose**: Move MCP-related files to correct VPS location

**Interface**:
- Input: MCP file list and SSH connection details
- Output: Properly organized MCP structure on VPS
- Methods: `identify_mcp_files()`, `transfer_via_ssh()`, `set_permissions()`

### 4. Deployment Component
**Purpose**: Handle Docker-based deployment on VPS

**Interface**:
- Input: Clean project structure and VPS connection
- Output: Running application on VPS
- Methods: `pull_from_github()`, `build_docker()`, `deploy_containers()`

## Data Models

### FileComparison
```
{
  "duplicates": [
    {
      "root_path": "string",
      "agentic_path": "string",
      "identical": "boolean",
      "action": "keep_root|merge|manual_review"
    }
  ],
  "unique_to_agentic": ["string"],
  "unique_to_root": ["string"]
}
```

### MCPFileStructure
```
{
  "server_files": ["string"],
  "config_files": ["string"],
  "data_files": ["string"],
  "target_location": "/home/asim/Documents/agents-mcp"
}
```

### DeploymentConfig
```
{
  "ssh_connection": {
    "host": "217.79.255.54",
    "user": "root",
    "password": "gt5qXy22aJ"
  },
  "github_repo": "string",
  "docker_config": "docker-compose.yml"
}
```

## Error Handling

### File Operation Errors
- **Backup Strategy**: Create backups before any destructive operations
- **Rollback Mechanism**: Ability to restore from backups if issues occur
- **Conflict Resolution**: Manual review process for conflicting files

### SSH Connection Errors
- **Connection Retry**: Automatic retry with exponential backoff
- **Authentication Handling**: Secure credential management
- **Network Timeout**: Appropriate timeout settings for VPS operations

### Docker Deployment Errors
- **Container Health Checks**: Verify containers are running correctly
- **Port Conflict Resolution**: Handle port binding issues
- **Resource Monitoring**: Check VPS resources before deployment

## Testing Strategy

### Local Testing
- **File Comparison Tests**: Verify accurate file analysis
- **Cleanup Simulation**: Test cleanup process with mock data
- **Backup/Restore Tests**: Ensure backup mechanisms work correctly

### VPS Integration Testing
- **SSH Connection Tests**: Verify SSH operations work correctly
- **File Transfer Tests**: Test MCP file organization
- **Docker Deployment Tests**: End-to-end deployment verification

### Rollback Testing
- **Cleanup Rollback**: Test ability to restore original structure
- **Deployment Rollback**: Test ability to revert to previous deployment
- **Data Integrity**: Verify no data loss during operations