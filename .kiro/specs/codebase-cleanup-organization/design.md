# Design Document

## Overview

This design outlines a comprehensive codebase cleanup and organization strategy for the AI consulting SaaS platform. The current codebase contains numerous temporary deployment scripts, backup files, and lacks proper organization. The solution will implement a systematic cleanup process, establish a clean project structure following Next.js best practices, and prepare the codebase for GitHub deployment.

## Architecture

### Current State Analysis

The codebase currently contains:
- **50+ temporary deployment Python scripts** (deploy_*.py, fix_*.py, etc.)
- **Large backup files** in `/backups` directory (tar.gz files)
- **Scattered test files** at root level
- **Mixed documentation files** throughout the project
- **Inconsistent component organization**
- **Proper .gitignore** already exists but needs enhancement

### Target State Structure

```
agentic-site/
├── app/                    # Next.js App Router (existing structure preserved)
│   ├── api/                # API routes
│   ├── auth/               # Authentication pages  
│   ├── admin/              # Admin dashboard
│   ├── customer/           # Customer dashboard
│   └── ...                 # Other app routes
├── components/             # React components (reorganized)
│   ├── ui/                 # shadcn/ui components (existing)
│   ├── layout/             # Layout components (header, footer, nav)
│   ├── features/           # Feature-specific components
│   ├── chatbot/            # Chatbot components
│   └── consulting/         # Consulting-specific components
├── agent/                  # Backend Python ADK agent (preserved as-is)
│   ├── my_adk_agent/       # Main agent code
│   ├── specialized_agents/ # Specialized agents
│   └── n8n_mcp_agent/      # N8N MCP integration
├── lib/                    # Utility functions (existing)
├── hooks/                  # React hooks (existing)
├── styles/                 # Global styles (existing)
├── public/                 # Static assets (existing)
├── tests/                  # Organized test structure
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/                # Essential utility scripts only
│   ├── deploy-to-vps.sh    # Main deployment script
│   ├── health-check.sh     # Health monitoring
│   └── start-production.sh # Production startup
├── docs/                   # Consolidated documentation
│   ├── api-reference.md    # API documentation
│   ├── deployment.md       # Deployment guide
│   └── configuration.md    # Configuration guide
├── supabase/               # Database migrations (existing)
├── n8n-mcp/                # N8N MCP server (existing)
└── [config files]         # Root config files (existing)
```

## Components and Interfaces

### Cleanup Engine

**Purpose**: Systematically identify and remove unnecessary files

**Key Functions**:
- `identify_temporary_files()`: Scan for deployment scripts matching patterns
- `remove_backup_files()`: Clean up large backup archives
- `preserve_essential_files()`: Maintain whitelist of required files
- `validate_cleanup()`: Ensure no critical files are removed

### File Organizer

**Purpose**: Move files to appropriate directories based on their purpose

**Key Functions**:
- `categorize_components()`: Sort React components by type
- `organize_tests()`: Group tests by testing strategy
- `consolidate_docs()`: Move documentation to docs directory
- `update_imports()`: Fix import paths after reorganization

### Git Configuration Manager

**Purpose**: Update version control configuration for clean repository

**Key Functions**:
- `enhance_gitignore()`: Add patterns for temporary files
- `stage_organized_files()`: Prepare files for commit
- `create_commit_message()`: Generate descriptive commit message
- `push_to_github()`: Deploy organized codebase to repository

## Data Models

### File Classification Schema

```typescript
interface FileClassification {
  path: string;
  category: 'component' | 'test' | 'doc' | 'script' | 'temp' | 'backup';
  action: 'keep' | 'move' | 'delete';
  targetPath?: string;
  reason: string;
}
```

### Cleanup Configuration

```typescript
interface CleanupConfig {
  temporaryPatterns: string[];     // Patterns for temp files to remove
  preservePatterns: string[];      // Patterns for files to keep
  organizationRules: {
    [category: string]: string;    // Target directories for each category
  };
  gitignoreAdditions: string[];    // New patterns to add to .gitignore
}
```

## Error Handling

### File Operation Safety

- **Backup Creation**: Create backup before any destructive operations
- **Dry Run Mode**: Preview changes before execution
- **Rollback Capability**: Ability to restore from backup if needed
- **Validation Checks**: Verify file integrity after moves

### Import Path Resolution

- **Dependency Analysis**: Scan for import statements that need updating
- **Path Validation**: Ensure all imports resolve correctly after reorganization
- **Build Verification**: Run build process to catch broken imports
- **Test Execution**: Verify tests still pass after reorganization

### Git Operation Safety

- **Branch Protection**: Work on feature branch, not main
- **Staged Commits**: Commit changes in logical groups
- **Push Verification**: Ensure remote repository reflects changes correctly
- **Conflict Resolution**: Handle any merge conflicts gracefully

## Testing Strategy

### Pre-Cleanup Validation

1. **Build Test**: Ensure current codebase builds successfully
2. **Test Suite**: Run existing tests to establish baseline
3. **Dependency Check**: Verify all imports and dependencies resolve
4. **File Inventory**: Create manifest of all current files

### Post-Cleanup Validation

1. **Structure Verification**: Confirm all files moved to correct locations
2. **Build Integrity**: Ensure reorganized codebase builds successfully
3. **Import Resolution**: Verify all import paths work correctly
4. **Test Execution**: Confirm all tests pass in new structure
5. **Git Status**: Validate clean git status after organization

### Cleanup Process Testing

1. **Dry Run Execution**: Test cleanup logic without making changes
2. **Selective Cleanup**: Test individual cleanup operations
3. **Rollback Testing**: Verify backup and restore functionality
4. **Edge Case Handling**: Test with various file types and structures

## Implementation Phases

### Phase 1: Analysis and Preparation
- Analyze current file structure
- Create file classification inventory
- Generate cleanup plan
- Create backup of current state

### Phase 2: Cleanup Execution
- Remove temporary deployment scripts
- Delete backup archives and logs
- Clean up test reports and analysis files
- Update .gitignore with new patterns

### Phase 3: Organization
- Move components to appropriate directories
- Organize test files by type
- Consolidate documentation
- Update import paths where necessary

### Phase 4: Validation and Deployment
- Verify build integrity
- Run test suite
- Commit organized structure
- Push to GitHub repository

## Security Considerations

### Sensitive File Protection
- Ensure no environment files are committed
- Verify API keys and secrets remain in .gitignore
- Protect database credentials and configuration

### Repository Security
- Review all files before commit for sensitive data
- Ensure proper .gitignore coverage
- Validate no large binary files are included

This design provides a systematic approach to cleaning up and organizing the codebase while maintaining functionality and preparing for professional GitHub deployment.