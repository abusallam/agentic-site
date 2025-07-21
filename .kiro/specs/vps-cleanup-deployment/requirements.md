# Requirements Document

## Introduction

This feature involves cleaning up the current project structure by removing the duplicate `agentic-site` folder, properly organizing MCP-related files in their correct location (`/home/asim/Documents/agents-mcp`), and establishing a clean deployment workflow from local development to VPS production using Docker.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to clean up the duplicate agentic-site folder structure, so that I have a single clean project structure without confusion.

#### Acceptance Criteria

1. WHEN the cleanup process starts THEN the system SHALL identify all duplicate files between root and agentic-site folder
2. WHEN duplicate files are found THEN the system SHALL keep the root version and remove the agentic-site duplicate
3. WHEN unique files exist in agentic-site THEN the system SHALL move them to appropriate locations in the root structure
4. WHEN the cleanup is complete THEN the agentic-site folder SHALL be completely removed

### Requirement 2

**User Story:** As a developer, I want MCP-related files properly organized in `/home/asim/Documents/agents-mcp` on the VPS, so that the MCP server can function correctly.

#### Acceptance Criteria

1. WHEN MCP files are identified THEN the system SHALL move them to `/home/asim/Documents/agents-mcp` via SSH
2. WHEN MCP configuration is updated THEN the system SHALL ensure proper file permissions and ownership
3. WHEN MCP server starts THEN it SHALL find all required files in the correct location
4. WHEN the organization is complete THEN the main project SHALL not contain MCP server files

### Requirement 3

**User Story:** As a developer, I want a clean development-to-production workflow, so that I can develop locally, push to GitHub, and deploy via Docker on the VPS.

#### Acceptance Criteria

1. WHEN local development is complete THEN the system SHALL allow pushing changes to GitHub repository
2. WHEN changes are pushed to GitHub THEN the VPS SHALL be able to pull the latest changes
3. WHEN Docker deployment starts THEN the system SHALL use the clean project structure
4. WHEN deployment completes THEN the application SHALL be running correctly on the VPS

### Requirement 4

**User Story:** As a developer, I want to use SSH connection (root@217.79.255.54) for all VPS operations, so that I can manage the server directly and efficiently.

#### Acceptance Criteria

1. WHEN VPS operations are needed THEN the system SHALL use SSH connection with provided credentials
2. WHEN file operations are performed THEN they SHALL be executed directly on the VPS via SSH
3. WHEN Docker commands are run THEN they SHALL be executed on the VPS through SSH connection
4. WHEN deployment status is checked THEN it SHALL be verified through SSH connection to the VPS