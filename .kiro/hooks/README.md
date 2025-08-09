# 🪝 Agent Hooks - Event-Driven Automation

## Overview

Agent hooks are event-driven AI automations that trigger based on filesystem events or manual commands. They provide seamless integration between your development workflow and AI assistance, eliminating boilerplate tasks and enforcing consistency.

## How Hooks Work

Hooks operate like Git hooks but are AI-powered:
1. **Event Occurs**: File save, creation, deletion, or manual trigger
2. **Hook Activates**: Matching hook configuration executes
3. **AI Processes**: Kiro performs the defined automation task
4. **Result Applied**: Changes are made automatically or presented for review

## Hook Types

### 1. File Event Hooks
- **on_save**: Triggered when files are saved
- **on_create**: Triggered when new files are created
- **on_delete**: Triggered when files are deleted
- **on_modify**: Triggered when files are modified

### 2. Manual Hooks
- **Command Palette**: Triggered via Kiro command palette
- **Button Triggers**: Triggered via UI buttons
- **Keyboard Shortcuts**: Triggered via custom shortcuts

### 3. Scheduled Hooks
- **Periodic**: Run at regular intervals
- **Cron-style**: Run based on cron expressions

## Current Active Hooks

### Development Automation Hooks

#### 1. React Test Generator (`react-test-generator.yml`)
**Trigger**: When React component files are saved  
**Action**: Automatically generates corresponding test files  
**Pattern**: `frontend/components/**/*.tsx`

#### 2. Agent Documentation Updater (`agent-docs-updater.yml`)
**Trigger**: When agent service files are modified  
**Action**: Updates API documentation and service specs  
**Pattern**: `agent/my_adk_agent/services/**/*.py`

#### 3. Security Scanner (`security-scanner.yml`)
**Trigger**: Manual trigger or pre-commit  
**Action**: Runs security scans and vulnerability checks  
**Scope**: Entire codebase

## Hook Configuration Format

```yaml
# Hook Configuration Schema
name: "Hook Name"
description: "What this hook does"
trigger:
  type: "file_save" | "file_create" | "manual" | "scheduled"
  pattern: "glob pattern for file matching"
  exclude: "glob pattern for files to exclude"
conditions:
  - "Additional conditions for hook execution"
actions:
  - type: "generate" | "update" | "validate" | "notify"
    prompt: "AI prompt for the action"
    output: "Where to place the result"
settings:
  auto_apply: true | false
  require_confirmation: true | false
```

## Example Hook Configurations

### Frontend Component Test Generator

```yaml
name: "React Component Test Generator"
description: "Automatically generate test files for React components"
trigger:
  type: "file_save"
  pattern: "frontend/components/**/*.tsx"
  exclude: "frontend/components/**/*.test.tsx"
conditions:
  - "file_contains: 'export function' OR 'export const'"
  - "not_exists: corresponding test file"
actions:
  - type: "generate"
    prompt: |
      Generate a comprehensive test file for this React component.
      Include:
      - Component rendering tests
      - Props validation tests
      - User interaction tests
      - Accessibility tests
      Use @testing-library/react and Jest.
    output: "same_directory/{component_name}.test.tsx"
settings:
  auto_apply: false
  require_confirmation: true
```

### Python Service Documentation

```yaml
name: "Agent Service Documentation"
description: "Update documentation when agent services change"
trigger:
  type: "file_save"
  pattern: "agent/my_adk_agent/services/**/*.py"
conditions:
  - "file_contains: 'class.*Service'"
actions:
  - type: "update"
    prompt: |
      Update the service documentation based on the changes.
      Include:
      - Method signatures and docstrings
      - Usage examples
      - Integration patterns
      - Error handling
    output: "docs/api/services/{service_name}.md"
  - type: "update"
    prompt: "Update the main API reference with service changes"
    output: "docs/api-reference.md"
settings:
  auto_apply: true
  require_confirmation: false
```

### Security Validation Hook

```yaml
name: "Security Scanner"
description: "Run security scans on code changes"
trigger:
  type: "manual"
  command: "security-scan"
actions:
  - type: "validate"
    prompt: |
      Perform a security analysis of the codebase:
      - Check for hardcoded secrets
      - Validate input sanitization
      - Review authentication patterns
      - Check for SQL injection vulnerabilities
      - Validate CORS configurations
    output: "security-report.md"
  - type: "notify"
    prompt: "Send security scan results to team"
    output: "slack_notification"
settings:
  auto_apply: false
  require_confirmation: true
```

## Best Practices

### Hook Design Principles

1. **Specific Triggers**: Use precise file patterns to avoid unnecessary executions
2. **Clear Prompts**: Write detailed prompts that produce consistent results
3. **Safe Defaults**: Default to requiring confirmation for destructive actions
4. **Error Handling**: Include fallback behavior for failed executions
5. **Performance**: Avoid hooks on frequently changing files

### File Pattern Examples

```yaml
# React components only
pattern: "frontend/components/**/*.tsx"
exclude: "**/*.test.tsx"

# Python services
pattern: "agent/my_adk_agent/services/**/*.py"
exclude: "**/__pycache__/**"

# Configuration files
pattern: "**/*.{json,yaml,yml,toml}"
exclude: "node_modules/**"

# Documentation files
pattern: "**/*.md"
exclude: ".kiro/**"
```

### Prompt Engineering for Hooks

```yaml
# Good: Specific and actionable
prompt: |
  Generate a TypeScript interface for this React component's props.
  Include JSDoc comments for each property.
  Use strict typing with no 'any' types.
  Export the interface with the name {ComponentName}Props.

# Bad: Vague and unclear
prompt: "Make this component better"
```

## Hook Management

### Creating New Hooks

1. **Identify Need**: What repetitive task needs automation?
2. **Define Trigger**: When should the hook execute?
3. **Write Prompt**: What should the AI do?
4. **Test Safely**: Start with `auto_apply: false`
5. **Refine**: Iterate based on results
6. **Deploy**: Enable auto-apply when confident

### Hook Debugging

```yaml
# Add debugging to hooks
settings:
  debug: true
  log_level: "verbose"
  dry_run: true  # Test without applying changes
```

### Hook Performance

- **Monitor Execution Time**: Track how long hooks take
- **Batch Operations**: Group related changes
- **Cache Results**: Avoid redundant processing
- **Selective Triggers**: Use precise patterns

## Integration with Development Workflow

### CI/CD Integration

```yaml
# Pre-commit hook
name: "Pre-commit Validation"
trigger:
  type: "pre_commit"
actions:
  - type: "validate"
    prompt: "Run linting, tests, and security checks"
```

### Code Review Integration

```yaml
# PR review assistance
name: "Pull Request Review"
trigger:
  type: "pull_request"
actions:
  - type: "review"
    prompt: "Analyze code changes and provide review comments"
```

### Documentation Sync

```yaml
# Keep docs in sync
name: "Documentation Sync"
trigger:
  type: "file_save"
  pattern: "**/*.{ts,tsx,py}"
actions:
  - type: "update"
    prompt: "Update relevant documentation"
```

## Troubleshooting

### Common Issues

1. **Hook Not Triggering**: Check file patterns and conditions
2. **Slow Execution**: Optimize prompts and patterns
3. **Inconsistent Results**: Refine prompts for clarity
4. **Permission Errors**: Check file access permissions

### Debug Commands

```bash
# List active hooks
kiro hooks list

# Test hook execution
kiro hooks test hook-name

# View hook logs
kiro hooks logs hook-name

# Disable problematic hook
kiro hooks disable hook-name
```

---

**Last Updated**: January 2025  
**Active Hooks**: 3 production hooks  
**Next Review**: Monthly hook performance assessment