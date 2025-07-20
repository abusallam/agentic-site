# file-utils MCP Server

## Description

A utility MCP server that provides file system operations like reading files, writing files, and listing directories.

## Development

This project uses `uv` for dependency management.

### Setup
```bash
# Install dependencies
uv sync

# Run the server
uv run python src/file_utils/main.py
```

### Testing
```bash
# Test the server locally
uv run python src/file_utils/main.py
```

## Configuration

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "file-utils": {
      "command": "uv",
      "args": ["run", "python", "src/file_utils/main.py"],
      "cwd": "/home/asim/Documents/agents-mcp/servers/file-utils",
      "disabled": false,
      "autoApprove": ["read_file", "list_directory"]
    }
  }
}
```

## Available Tools

- `read_file`: Read the contents of a file
- `write_file`: Write content to a file  
- `list_directory`: List contents of a directory

## Usage

Once configured, you can ask Kiro to:
- "Read the contents of /path/to/file.txt"
- "Write 'Hello World' to /path/to/output.txt"
- "List the files in /path/to/directory"