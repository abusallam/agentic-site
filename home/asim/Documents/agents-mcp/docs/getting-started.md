# Getting Started with MCP Servers

## What are MCP Servers?

Model Context Protocol (MCP) servers allow you to extend AI assistants like Kiro with custom tools and capabilities. They run as separate processes and communicate with the AI through a standardized protocol.

## Setting Up Your Environment

1. **Install uv (Python package manager):**
   ```bash
   # On Ubuntu/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or with pip
   pip install uv
   ```

2. **Verify installation:**
   ```bash
   uv --version
   uvx --version
   ```

## Creating Your First Server

Use the provided script to create a new server:

```bash
cd /home/asim/Documents/agents-mcp
./scripts/create-server.sh my-first-server
```

## Adding to Kiro Configuration

1. Edit your MCP configuration file (usually at `~/.kiro/settings/mcp.json`)
2. Add your server configuration:

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "uv",
      "args": ["run", "python", "src/my-first-server/main.py"],
      "cwd": "/home/asim/Documents/agents-mcp/servers/my-first-server",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Testing Your Server

1. Test locally:
   ```bash
   cd /home/asim/Documents/agents-mcp/servers/my-first-server
   uv run python src/my-first-server/main.py
   ```

2. Test with Kiro by asking it to use your custom tools

## Common Server Types

- **File processors**: Tools for reading, writing, or transforming files
- **API integrations**: Connect to external services and APIs  
- **Data analyzers**: Process and analyze data sets
- **System utilities**: Interact with system resources and processes
- **Custom workflows**: Automate complex multi-step tasks

## Best Practices

- Keep servers focused on specific domains
- Include comprehensive error handling
- Document all tools and their parameters
- Test thoroughly before deployment
- Use meaningful tool and parameter names