# Requirements Document

## Introduction

The deployment system encountered critical issues during agentic workflow testing, specifically when testing the N8nWorkflowAgent. During N8N troubleshooting, there was confusion between production and development N8N instances, leading to a cascade of deployment problems. The development environment is now partially broken with missing containers, and some production services are unhealthy. This spec addresses the systematic restoration of the development environment and agentic workflow testing while maintaining strict separation from production.

## Requirements

### Requirement 1: Development Environment Restoration

**User Story:** As a developer, I want a fully functional development environment so that I can safely test changes without affecting production.

#### Acceptance Criteria

1. WHEN checking development containers THEN the system SHALL show all required dev containers running and healthy
2. WHEN accessing dev.consulting.sa THEN the system SHALL respond with a functional frontend application
3. WHEN the development backend is called THEN the system SHALL respond with healthy API endpoints
4. IF development containers are missing THEN the system SHALL recreate them with proper configuration
5. WHEN development containers are recreated THEN they SHALL use consistent naming conventions

### Requirement 2: Production Environment Health Restoration

**User Story:** As a system administrator, I want the production environment to be fully healthy so that users have a reliable service experience.

#### Acceptance Criteria

1. WHEN checking production containers THEN all containers SHALL report healthy status
2. WHEN the production frontend health check fails THEN the system SHALL identify and resolve the root cause
3. WHEN production issues are fixed THEN the system SHALL maintain zero downtime for users
4. IF production containers need restart THEN the system SHALL use rolling restart to avoid service interruption
5. WHEN production is restored THEN all health checks SHALL pass consistently

### Requirement 3: Container Naming Standardization

**User Story:** As a DevOps engineer, I want consistent container naming across all environments so that management scripts work reliably.

#### Acceptance Criteria

1. WHEN containers are deployed THEN they SHALL follow the naming pattern: `agentic-[service]-[environment]`
2. WHEN existing containers have inconsistent names THEN the system SHALL migrate them to the standard pattern
3. WHEN scripts reference containers THEN they SHALL use the standardized naming convention
4. IF container names conflict THEN the system SHALL resolve conflicts without service disruption
5. WHEN naming is standardized THEN all management scripts SHALL work correctly

### Requirement 4: Deployment Process Validation

**User Story:** As a developer, I want a reliable deployment process so that I can confidently deploy changes from local development to the server.

#### Acceptance Criteria

1. WHEN deploying to development THEN the system SHALL validate all prerequisites are met
2. WHEN the deployment process runs THEN it SHALL provide clear status feedback at each step
3. WHEN deployment completes THEN the system SHALL run comprehensive health checks
4. IF deployment fails THEN the system SHALL provide clear error messages and rollback options
5. WHEN deployment succeeds THEN all services SHALL be accessible and functional

### Requirement 5: Environment Isolation Verification

**User Story:** As a system administrator, I want guaranteed isolation between production and development environments so that development work cannot impact live users.

#### Acceptance Criteria

1. WHEN development containers are managed THEN production containers SHALL remain untouched
2. WHEN development services fail THEN production services SHALL continue operating normally
3. WHEN ports are assigned THEN there SHALL be no conflicts between environments
4. IF environment isolation is compromised THEN the system SHALL alert and prevent cross-environment impact
5. WHEN both environments run THEN they SHALL operate independently with separate resources

### Requirement 6: N8N Development Environment Isolation

**User Story:** As a developer testing agentic workflows, I want a completely isolated N8N development instance so that workflow testing never affects production N8N.

#### Acceptance Criteria

1. WHEN testing N8nWorkflowAgent THEN it SHALL connect only to development N8N instance (port 5680)
2. WHEN N8N development container is unhealthy THEN the system SHALL fix it without touching production N8N
3. WHEN N8N workflows are tested THEN they SHALL run in development environment only
4. IF N8N development fails THEN production N8N SHALL remain completely unaffected
5. WHEN N8N development is restored THEN agentic workflow testing SHALL resume successfully

### Requirement 7: Agentic Workflow Testing Restoration

**User Story:** As a developer, I want to test the four-agent system workflows so that I can verify the N8nWorkflowAgent integration works correctly.

#### Acceptance Criteria

1. WHEN InitialCustomerAgent is tested THEN it SHALL respond correctly in development environment
2. WHEN N8nWorkflowAgent is tested THEN it SHALL connect to development N8N instance successfully
3. WHEN CodeGenerationAgent is tested THEN it SHALL function independently of N8N issues
4. WHEN ConsultingAgent is tested THEN it SHALL work with LiveKit integration in development
5. WHEN all agents are tested THEN the intelligent routing SHALL work with 100% accuracy

### Requirement 8: Development Branch Strict Enforcement

**User Story:** As a system administrator, I want absolute guarantee that development work never touches production so that live users are never impacted.

#### Acceptance Criteria

1. WHEN any deployment script runs THEN it SHALL verify it's targeting development environment only
2. WHEN containers are managed THEN the system SHALL prevent any production container interaction
3. WHEN N8N is accessed THEN it SHALL use development port 5680, never production port 5678
4. IF any script attempts production access THEN the system SHALL block it and alert
5. WHEN development work is complete THEN production SHALL remain in its original state

### Requirement 9: Monitoring and Health Check Enhancement

**User Story:** As a system administrator, I want comprehensive monitoring of both environments so that I can proactively identify and resolve issues.

#### Acceptance Criteria

1. WHEN containers are deployed THEN they SHALL include proper health check configurations
2. WHEN health checks fail THEN the system SHALL provide detailed diagnostic information
3. WHEN monitoring detects issues THEN it SHALL alert with actionable information
4. IF containers become unhealthy THEN the system SHALL attempt automatic recovery
5. WHEN health is restored THEN the system SHALL log the resolution for future reference