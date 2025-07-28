# N8N Tools MCP Server

A Model Context Protocol (MCP) server for N8N workflow automation integration.

## Features

- List N8N workflows
- Execute workflows with parameters
- Monitor workflow execution status
- Create webhook workflows
- Activate/deactivate workflows
- Get execution history

## Installation

```bash
cd ~/Documents/agents-mcp/servers/n8n-tools
uv sync
```

## Configuration

Set the following environment variables:

```bash
export N8N_BASE_URL="https://n8n.consulting.sa"
export N8N_API_KEY="your_n8n_api_key"
```

## Usage

Run the MCP server:

```bash
uv run python src/n8n_tools/main.py
```

## Available Tools

- `list_workflows` - List all workflows
- `get_workflow` - Get workflow details
- `execute_workflow` - Execute a workflow
- `get_executions` - Get execution history
- `activate_workflow` - Activate/deactivate workflow
- `create_webhook_workflow` - Create webhook workflow