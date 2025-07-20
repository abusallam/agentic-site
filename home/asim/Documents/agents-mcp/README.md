# MCP Servers Collection

This directory contains custom MCP (Model Context Protocol) servers for use with Kiro and other AI assistants. All servers are built using modern Python tooling with `uv` for dependency management.

## 🚀 Available Servers

### 📁 **file-utils** - Basic File Operations
- **Tools**: `read_file`, `write_file`, `list_directory`
- **Description**: Essential file system operations for reading, writing, and listing files
- **Auto-approved**: `read_file`, `list_directory`

### 🐙 **github-tools** - GitHub Integration
- **Tools**: `list_repos`, `get_repo_info`, `create_issue`, `list_issues`, `get_file_content`
- **Description**: Complete GitHub API integration for repository management
- **Requirements**: `GITHUB_TOKEN` environment variable
- **Auto-approved**: `list_repos`, `get_repo_info`

### 🎭 **playwright-tools** - Web Automation
- **Tools**: `scrape_page`, `screenshot_page`, `fill_form`, `click_element`
- **Description**: Web scraping and browser automation using Playwright
- **Auto-approved**: `scrape_page`

### 🔄 **n8n-tools** - Workflow Automation
- **Tools**: `list_workflows`, `execute_workflow`, `get_executions`, `activate_workflow`, `create_webhook_workflow`
- **Description**: N8N workflow automation platform integration
- **Requirements**: `N8N_API_KEY`, `N8N_BASE_URL` environment variables
- **Auto-approved**: `list_workflows`, `get_executions`

### 🚢 **coolify-tools** - Self-Hosting Platform
- **Tools**: `list_applications`, `deploy_application`, `stop_application`, `restart_application`, `list_servers`, `create_application`
- **Description**: Coolify self-hosting platform management
- **Requirements**: `COOLIFY_API_TOKEN`, `COOLIFY_BASE_URL` environment variables
- **Auto-approved**: `list_applications`, `list_servers`

### 🧠 **mem0-tools** - AI Memory Management
- **Tools**: `add_memory`, `search_memories`, `get_all_memories`, `update_memory`, `delete_memory`
- **Description**: Persistent AI memory using Mem0 with vector storage
- **Requirements**: `OPENAI_API_KEY`, `QDRANT_HOST`, `QDRANT_PORT` environment variables
- **Auto-approved**: `search_memories`, `get_all_memories`

### 🗂️ **filesystem-advanced** - Advanced File Operations
- **Tools**: `search_files`, `get_file_info`, `copy_file`, `move_file`, `delete_file`, `get_file_hash`, `compress_directory`, `extract_archive`
- **Description**: Advanced file system operations including search, compression, and detailed file information
- **Auto-approved**: `get_file_info`, `search_files`

## 📋 Structure

```
~/Documents/agents-mcp/
├── README.md                    # This file
├── servers/                     # Individual MCP server implementations
│   ├── file-utils/             # Basic file operations
│   ├── github-tools/           # GitHub API integration
│   ├── playwright-tools/       # Web automation
│   ├── n8n-tools/             # N8N workflow automation
│   ├── coolify-tools/         # Coolify platform management
│   ├── mem0-tools/            # AI memory management
│   └── filesystem-advanced/   # Advanced file operations
├── configs/                     # Configuration templates
│   └── mcp-template.json      # Complete MCP configuration
├── scripts/                     # Utility scripts
│   └── create-server.sh       # Create new server template
└── docs/                       # Documentation
    └── getting-started.md     # Setup and usage guide
```

## 🛠️ Quick Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Copy the configuration template**:
   ```bash
   cp ~/Documents/agents-mcp/configs/mcp-template.json ~/.kiro/settings/mcp.json
   ```

3. **Update environment variables** in your MCP config:
   - Replace `your_github_token_here` with your GitHub token
   - Replace `your_n8n_api_key_here` with your N8N API key
   - Replace `your_coolify_token_here` with your Coolify token
   - Replace `your_openai_key_here` with your OpenAI API key

4. **Install Playwright browsers** (for playwright-tools):
   ```bash
   cd ~/Documents/agents-mcp/servers/playwright-tools
   uv run playwright install
   ```

## 🔧 Creating New Servers

Use the provided script to create new servers:

```bash
cd ~/Documents/agents-mcp
./scripts/create-server.sh my-new-server
```

This will create a complete uv project structure with MCP server template.

## 🧪 Testing Servers

Test any server locally:

```bash
cd ~/Documents/agents-mcp/servers/[server-name]
uv run python src/[server_name]/main.py
```

## 📖 Environment Variables Reference

| Server | Variable | Description | Default |
|--------|----------|-------------|---------|
| github-tools | `GITHUB_TOKEN` | GitHub personal access token | Required |
| n8n-tools | `N8N_API_KEY` | N8N API key | Required |
| n8n-tools | `N8N_BASE_URL` | N8N instance URL | `http://localhost:5678` |
| coolify-tools | `COOLIFY_API_TOKEN` | Coolify API token | Required |
| coolify-tools | `COOLIFY_BASE_URL` | Coolify instance URL | `http://localhost:8000` |
| mem0-tools | `OPENAI_API_KEY` | OpenAI API key | Required |
| mem0-tools | `QDRANT_HOST` | Qdrant vector DB host | `localhost` |
| mem0-tools | `QDRANT_PORT` | Qdrant vector DB port | `6333` |

## 🎯 Usage Examples

Once configured, you can ask Kiro to:

- **File Operations**: "Read the contents of my config file" or "List files in my project directory"
- **GitHub**: "Show me my repositories" or "Create an issue in my project"
- **Web Automation**: "Scrape the latest news from example.com" or "Take a screenshot of my website"
- **N8N**: "List my active workflows" or "Execute my data processing workflow"
- **Coolify**: "Show my deployed applications" or "Deploy my latest changes"
- **Memory**: "Remember that I prefer TypeScript for new projects" or "What do you remember about my coding preferences?"
- **Advanced Files**: "Find all Python files containing 'async'" or "Get the SHA256 hash of this file"

## 🔒 Security Notes

- Store API keys securely and never commit them to version control
- Use environment variables or secure secret management
- Review auto-approved tools and adjust based on your security requirements
- Test servers in isolated environments before production use

## 🤝 Contributing

To add new servers:
1. Use `./scripts/create-server.sh server-name` to create the structure
2. Implement your MCP server in `src/server_name/main.py`
3. Add configuration to `configs/mcp-template.json`
4. Update this README with server documentation
5. Test thoroughly before deployment