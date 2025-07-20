#!/bin/bash

# Setup script for all MCP servers

echo "🚀 Setting up MCP Servers Collection..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

echo "✅ uv is available"

# Install dependencies for all servers
SERVERS=("file-utils" "github-tools" "playwright-tools" "n8n-tools" "coolify-tools" "mem0-tools" "filesystem-advanced")

for server in "${SERVERS[@]}"; do
    echo "📦 Installing dependencies for $server..."
    cd "/home/asim/Documents/agents-mcp/servers/$server"
    
    if [ -f "pyproject.toml" ]; then
        uv sync
        echo "✅ $server dependencies installed"
    else
        echo "⚠️  $server project not found, skipping..."
    fi
done

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
cd "/home/asim/Documents/agents-mcp/servers/playwright-tools"
uv run playwright install

# Copy configuration template if it doesn't exist
if [ ! -f ~/.kiro/settings/mcp.json ]; then
    echo "📋 Copying MCP configuration template..."
    mkdir -p ~/.kiro/settings
    cp /home/asim/Documents/agents-mcp/configs/mcp-template.json ~/.kiro/settings/mcp.json
    echo "✅ Configuration template copied to ~/.kiro/settings/mcp.json"
    echo "⚠️  Remember to update your API keys in the configuration!"
else
    echo "ℹ️  MCP configuration already exists at ~/.kiro/settings/mcp.json"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit ~/.kiro/settings/mcp.json and add your API keys:"
echo "   - GITHUB_TOKEN for GitHub integration"
echo "   - N8N_API_KEY for N8N workflows"
echo "   - COOLIFY_API_TOKEN for Coolify management"
echo "   - OPENAI_API_KEY for Mem0 AI memory"
echo ""
echo "2. Restart Kiro to load the new MCP servers"
echo ""
echo "3. Test the servers by asking Kiro to use them!"
echo ""
echo "📖 See README.md for detailed usage examples"