# Design Document

## Overview

This design outlines a comprehensive cleanup and reorganization strategy to transform the current scattered codebase into a senior-level, maintainable project structure. The cleanup addresses multiple issues: scattered configuration files, mixed concerns, duplicate Docker files, temporary scripts cluttering the root, and improper separation of frontend/backend systems.

## Architecture

### Current State Analysis
- **Root Directory Clutter**: 50+ files in root including temporary Python scripts, multiple Docker files, and scattered configs
- **Mixed Concerns**: Frontend (Next.js) and backend (Python ADK) code mixed with deployment scripts
- **Configuration Duplication**: Multiple Docker files, environment files, and package configurations
- **Temporary Files**: Cleanup logs, analysis files, and one-off scripts polluting the workspace
- **Inconsistent Structure**: No clear separation between development, deployment, and operational concerns

### Target State Architecture

```
project-root/
├── frontend/                    # Next.js application (clean separation)
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   ├── lib/                    # Frontend utilities
│   ├── public/                 # Static assets
│   ├── styles/                 # CSS and styling
│   ├── package.json            # Frontend dependencies
│   ├── next.config.mjs         # Next.js configuration
│   ├── tailwind.config.ts      # Tailwind configuration
│   └── tsconfig.json           # TypeScript configuration
├── backend/                     # Python ADK agent system
│   ├── agent/                  # Current agent code (preserved structure)
│   ├── services/               # External service integrations
│   ├── tests/                  # Backend-specific tests
│   ├── pyproject.toml          # Python dependencies
│   └── uv.lock                 # Python lock file
├── infrastructure/              # Deployment and infrastructure
│   ├── docker/                 # All Docker configurations
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.production
│   │   └── docker-compose.yml
│   ├── scripts/                # Deployment and utility scripts
│   └── configs/                # Infrastructure configurations
├── docs/                       # Documentation (organized)
├── tests/                      # Integration and E2E tests
├── .github/                    # GitHub workflows and templates
├── .env.example                # Environment template
├── package.json                # Root package.json for workspace management
├── README.md                   # Updated project documentation
└── workspace.json              # Workspace configuration
```

## Components and Interfaces

### 1. File Analysis and Categorization Component
**Purpose**: Analyze all files and categorize them for proper organization

**Interface**:
- Input: Current project file tree
- Output: Categorized file mapping with move/delete/consolidate actions
- Methods: `analyze_file_structure()`, `categorize_files()`, `identify_duplicates()`

**Categories**:
- Frontend files (Next.js app, components, styles)
- Backend files (Python agent, services, utilities)
- Infrastructure files (Docker, deployment scripts)
- Configuration files (environment, build configs)
- Documentation files
- Temporary/cleanup files (to be removed)
- Test files

### 2. Configuration Consolidation Component
**Purpose**: Merge and standardize configuration files

**Interface**:
- Input: Multiple configuration files of same type
- Output: Single, authoritative configuration
- Methods: `merge_docker_configs()`, `consolidate_env_files()`, `standardize_package_configs()`

**Consolidation Rules**:
- Docker: Single production Dockerfile, separate development compose
- Environment: Single .env.example with all required variables documented
- Package management: Workspace-aware package.json structure
- Linting/formatting: Consistent ESLint, Prettier, and Python formatting

### 3. Code Organization Component
**Purpose**: Restructure code following best practices

**Interface**:
- Input: Current code structure
- Output: Organized code with clear separation of concerns
- Methods: `separate_frontend_backend()`, `organize_utilities()`, `structure_tests()`

**Organization Principles**:
- Clear frontend/backend separation
- Service layer pattern for external integrations
- Utility functions properly modularized
- Test files co-located with relevant code
- Configuration files at appropriate levels

### 4. Cleanup and Removal Component
**Purpose**: Safely remove unnecessary files and dead code

**Interface**:
- Input: File analysis results
- Output: Clean project structure
- Methods: `remove_temporary_files()`, `clean_dead_code()`, `archive_old_files()`

**Cleanup Strategy**:
- Remove temporary Python scripts used for one-time operations
- Archive old deployment logs and analysis files
- Remove duplicate configurations
- Clean up unused dependencies
- Remove dead code and unused imports

## Data Models

### FileMapping
```typescript
{
  "source_path": "string",
  "target_path": "string",
  "action": "move" | "copy" | "merge" | "delete",
  "category": "frontend" | "backend" | "infrastructure" | "docs" | "temp",
  "priority": number,
  "dependencies": ["string"]
}
```

### ConfigurationMerge
```typescript
{
  "config_type": "docker" | "env" | "package" | "lint",
  "source_files": ["string"],
  "target_file": "string",
  "merge_strategy": "override" | "merge" | "append",
  "conflicts": ["string"]
}
```

### ProjectStructure
```typescript
{
  "workspace_type": "monorepo",
  "frontend": {
    "framework": "nextjs",
    "package_manager": "npm",
    "build_output": "frontend/.next"
  },
  "backend": {
    "framework": "python-adk",
    "package_manager": "uv",
    "entry_point": "backend/agent/main.py"
  },
  "infrastructure": {
    "containerization": "docker",
    "orchestration": "docker-compose",
    "deployment": "vps"
  }
}
```

## Error Handling

### File Operation Errors
- **Backup Strategy**: Create full project backup before any destructive operations
- **Atomic Operations**: Use transaction-like approach for file moves
- **Rollback Mechanism**: Ability to restore original structure if issues occur
- **Dependency Tracking**: Ensure file moves don't break import paths

### Configuration Merge Conflicts
- **Conflict Detection**: Identify conflicting configuration values
- **Manual Review Process**: Flag conflicts for human decision
- **Validation**: Test merged configurations before applying
- **Fallback Strategy**: Keep original configs as backup

### Code Restructuring Errors
- **Import Path Updates**: Automatically update import statements
- **Build Verification**: Ensure project builds after restructuring
- **Test Validation**: Run tests to verify functionality preserved
- **Incremental Approach**: Restructure in phases to minimize risk

## Testing Strategy

### Structure Validation
- **Build Tests**: Verify both frontend and backend build successfully
- **Import Tests**: Ensure all import paths are correct after restructuring
- **Configuration Tests**: Validate all configuration files are syntactically correct
- **Dependency Tests**: Verify all dependencies are properly resolved

### Functionality Preservation
- **Unit Tests**: Run existing unit tests to ensure functionality preserved
- **Integration Tests**: Test frontend-backend communication still works
- **E2E Tests**: Verify complete user workflows function correctly
- **Deployment Tests**: Test deployment process with new structure

### Quality Assurance
- **Linting**: Ensure code passes all linting rules
- **Formatting**: Verify consistent code formatting
- **Documentation**: Validate documentation reflects new structure
- **Performance**: Ensure restructuring doesn't impact performance

## Implementation Phases

### Phase 1: Analysis and Planning
1. Complete file analysis and categorization
2. Identify all configuration conflicts
3. Create detailed migration plan
4. Set up backup and rollback mechanisms

### Phase 2: Infrastructure Reorganization
1. Consolidate Docker configurations
2. Organize deployment scripts
3. Standardize environment configurations
4. Set up workspace structure

### Phase 3: Code Restructuring
1. Separate frontend and backend code
2. Organize utility functions and services
3. Restructure test files
4. Update import paths and dependencies

### Phase 4: Cleanup and Optimization
1. Remove temporary and unnecessary files
2. Clean up dead code and unused dependencies
3. Optimize build configurations
4. Update documentation

### Phase 5: Validation and Testing
1. Comprehensive testing of new structure
2. Performance validation
3. Deployment testing
4. Documentation review and updates