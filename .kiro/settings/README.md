# ⚙️ Kiro Settings & Configuration

## Overview

This directory contains Kiro-specific configuration files that control how the AI assistant interacts with your project. These settings enable advanced features like MCP (Model Context Protocol) integrations, custom tool configurations, and project-specific behaviors.

## Configuration Files

### 1. MCP Configuration (`mcp.json`)

The MCP (Model Context Protocol) configuration enables Kiro to interact with external tools and services through standardized protocols.

**Current Configuration**:
- **n8n-mcp-server**: Integration with n8n workflow automation
- **supabase-mcp**: Database operations and queries
- **monitoring-mcp**: System monitoring and health checks

### 2. Project Settings (`project.json`)

Project-specific settings that customize Kiro's behavior for this codebase.

### 3. Tool Configurations (`tools/`)

Custom tool definitions and configurations for project-specific automation.

## MCP Server Management

### Available MCP Servers

#### n8n MCP Server
```json
{
  "name": "n8n-mcp-server",
  "command": "uvx",
  "args": ["n8n-mcp-server@latest"],
  "description": "n8n workflow automation integration",
  "tools": [
    "create_workflow",
    "execute_workflow",
    "list_workflows",
    "get_workflow_status"
  ]
}
```

#### Supabase MCP Server
```json
{
  "name": "supabase-mcp",
  "command": "uvx", 
  "args": ["supabase-mcp@latest"],
  "description": "Database operations and queries",
  "tools": [
    "query_database",
    "create_table",
    "insert_data",
    "update_data"
  ]
}
```

### MCP Server Status

Check MCP server status using these commands:

```bash
# List all configured MCP servers
kiro mcp list

# Check server status
kiro mcp status server-name

# Restart MCP server
kiro mcp restart server-name

# Test MCP server connection
kiro mcp test server-name
```

## Project-Specific Settings

### Code Analysis Settings
```json
{
  "codeAnalysis": {
    "languages": ["typescript", "python", "javascript"],
    "frameworks": ["nextjs", "react", "adk", "fastapi"],
    "excludePatterns": [
      "node_modules/**",
      "**/__pycache__/**",
      ".git/**",
      "dist/**",
      "build/**"
    ]
  }
}
```

### Documentation Settings
```json
{
  "documentation": {
    "autoUpdate": true,
    "formats": ["markdown", "jsdoc", "sphinx"],
    "outputPath": "docs/",
    "includeExamples": true
  }
}
```

### Testing Settings
```json
{
  "testing": {
    "frameworks": ["jest", "pytest", "playwright"],
    "coverageThreshold": 80,
    "autoGenerateTests": true,
    "testPatterns": [
      "**/*.test.{ts,tsx,py}",
      "**/*.spec.{ts,tsx,py}"
    ]
  }
}
```

## Environment-Specific Configurations

### Development Environment
```json
{
  "environment": "development",
  "features": {
    "hotReload": true,
    "debugMode": true,
    "verboseLogging": true,
    "autoSave": true
  },
  "integrations": {
    "enableAllMCP": true,
    "mockExternalServices": true
  }
}
```

### Production Environment
```json
{
  "environment": "production",
  "features": {
    "hotReload": false,
    "debugMode": false,
    "verboseLogging": false,
    "autoSave": false
  },
  "integrations": {
    "enableAllMCP": false,
    "mockExternalServices": false
  }
}
```

## Custom Tool Definitions

### Agent Development Tools
```json
{
  "tools": {
    "adk-agent-generator": {
      "description": "Generate ADK agent boilerplate",
      "command": "generate-adk-agent",
      "parameters": {
        "agentName": "string",
        "services": "array",
        "tools": "array"
      }
    },
    "service-integrator": {
      "description": "Create service integration code",
      "command": "integrate-service",
      "parameters": {
        "serviceName": "string",
        "apiEndpoint": "string",
        "authMethod": "string"
      }
    }
  }
}
```

### Frontend Development Tools
```json
{
  "tools": {
    "component-generator": {
      "description": "Generate React component with tests",
      "command": "generate-component",
      "parameters": {
        "componentName": "string",
        "componentType": "string",
        "includeTests": "boolean"
      }
    },
    "api-route-generator": {
      "description": "Generate Next.js API routes",
      "command": "generate-api-route",
      "parameters": {
        "routeName": "string",
        "methods": "array",
        "middleware": "array"
      }
    }
  }
}
```

## Security and Access Control

### API Key Management
```json
{
  "security": {
    "apiKeys": {
      "storage": "environment",
      "rotation": "monthly",
      "validation": "strict"
    },
    "accessControl": {
      "enableRBAC": true,
      "defaultRole": "developer",
      "adminUsers": ["admin@consulting.sa"]
    }
  }
}
```

### MCP Security Settings
```json
{
  "mcpSecurity": {
    "enableAuth": true,
    "tokenExpiry": "24h",
    "allowedOrigins": ["localhost", "consulting.sa"],
    "rateLimiting": {
      "enabled": true,
      "requestsPerMinute": 100
    }
  }
}
```

## Performance Optimization

### Caching Settings
```json
{
  "performance": {
    "caching": {
      "enabled": true,
      "ttl": "1h",
      "maxSize": "100MB",
      "strategy": "lru"
    },
    "parallelization": {
      "maxConcurrentTasks": 5,
      "enableBatching": true
    }
  }
}
```

### Resource Limits
```json
{
  "resources": {
    "memory": {
      "maxUsage": "2GB",
      "warningThreshold": "1.5GB"
    },
    "cpu": {
      "maxUsage": "80%",
      "warningThreshold": "60%"
    },
    "disk": {
      "maxUsage": "10GB",
      "warningThreshold": "8GB"
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Check server status: `kiro mcp status`
   - Restart server: `kiro mcp restart server-name`
   - Verify configuration in `mcp.json`

2. **Tool Not Found**
   - Check tool registration in settings
   - Verify tool installation: `uvx list`
   - Update tool: `uvx install tool-name@latest`

3. **Performance Issues**
   - Check resource usage in settings
   - Adjust caching settings
   - Reduce concurrent task limits

### Debug Commands

```bash
# Check all settings
kiro settings show

# Validate configuration
kiro settings validate

# Reset to defaults
kiro settings reset

# Export current settings
kiro settings export settings-backup.json
```

## Configuration Updates

### Automatic Updates
- Settings are automatically synced across sessions
- MCP servers auto-reconnect on configuration changes
- Tool definitions are hot-reloaded

### Manual Updates
- Edit configuration files directly
- Use `kiro settings reload` to apply changes
- Validate changes with `kiro settings validate`

---

**Last Updated**: January 2025  
**Configuration Version**: 2.1.0  
**Next Review**: Monthly settings optimization