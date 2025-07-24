#!/bin/bash
# Setup All MCP Servers Script
# Comprehensive setup for all MCP servers in the agents-mcp hub

set -e

echo "🚀 Setting up MCP Services Hub..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="$HOME/Documents/agents-mcp"
SERVERS_DIR="$BASE_DIR/servers"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    print_error "MCP base directory not found: $BASE_DIR"
    exit 1
fi

cd "$BASE_DIR"

print_status "Checking system dependencies..."

# Check for required system packages
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is required but not installed"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    print_warning "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt update -qq
sudo apt install -y python3-paramiko python3-dotenv python3-pip

# Install MCP package
print_status "Installing MCP package..."
pip3 install --break-system-packages mcp

print_status "Setting up individual MCP servers..."

# Setup SSH Control Server (Production Ready)
print_status "Setting up ssh-control server..."
if [ -d "$SERVERS_DIR/ssh-control" ]; then
    cd "$SERVERS_DIR/ssh-control"
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip3 install --break-system-packages -r requirements.txt
    fi
    
    # Test SSH connection
    if python3 test_ssh_connection.py > /dev/null 2>&1; then
        print_success "ssh-control server is working"
    else
        print_warning "ssh-control server test failed"
    fi
else
    print_error "ssh-control server directory not found"
fi

# Setup File Utils Server (Production Ready)
print_status "Setting up file-utils server..."
if [ -d "$SERVERS_DIR/file-utils" ]; then
    cd "$SERVERS_DIR/file-utils"
    
    # Initialize uv project if needed
    if [ ! -f "pyproject.toml" ]; then
        uv init --no-readme
    fi
    
    # Install dependencies
    uv sync
    
    print_success "file-utils server is ready"
else
    print_error "file-utils server directory not found"
fi

# Setup other servers (create basic structure if missing)
servers=("filesystem-advanced" "github-tools" "n8n-tools" "coolify-tools" "mem0-tools" "playwright-tools")

for server in "${servers[@]}"; do
    print_status "Setting up $server server..."
    
    if [ -d "$SERVERS_DIR/$server" ]; then
        cd "$SERVERS_DIR/$server"
        
        # Initialize uv project if needed
        if [ ! -f "pyproject.toml" ]; then
            uv init --no-readme
        fi
        
        # Create basic structure if missing
        mkdir -p "src/${server//-/_}"
        
        # Create basic main.py if missing
        if [ ! -f "src/${server//-/_}/main.py" ]; then
            cat > "src/${server//-/_}/main.py" << EOF
#!/usr/bin/env python3
"""
${server} MCP Server - Placeholder implementation
"""

import asyncio
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("${server}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="placeholder_tool",
            description="Placeholder tool for ${server}",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Test message"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls."""
    
    if name == "placeholder_tool":
        message = arguments.get("message", "Hello")
        return [
            types.TextContent(
                type="text",
                text=f"${server} placeholder response: {message}"
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
EOF
        fi
        
        # Install basic dependencies
        uv add mcp
        
        print_success "$server server structure created"
    else
        print_warning "$server server directory not found"
    fi
done

# Create test script
print_status "Creating comprehensive test script..."
cd "$BASE_DIR"

cat > "scripts/test-all-servers.sh" << 'EOF'
#!/bin/bash
# Test All MCP Servers Script

set -e

echo "🧪 Testing All MCP Servers..."
echo "============================="

BASE_DIR="$HOME/Documents/agents-mcp"
SERVERS_DIR="$BASE_DIR/servers"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "🧪 Testing $1..."
}

print_pass() {
    echo -e "${GREEN}✅ $1 PASSED${NC}"
}

print_fail() {
    echo -e "${RED}❌ $1 FAILED${NC}"
}

# Test credentials
print_test "credentials system"
if python3 "$BASE_DIR/load_credentials.py" > /dev/null 2>&1; then
    print_pass "Credentials"
else
    print_fail "Credentials"
fi

# Test SSH Control
print_test "ssh-control server"
if [ -f "$SERVERS_DIR/ssh-control/test_ssh_connection.py" ]; then
    if python3 "$SERVERS_DIR/ssh-control/test_ssh_connection.py" > /dev/null 2>&1; then
        print_pass "SSH Control"
    else
        print_fail "SSH Control"
    fi
else
    print_fail "SSH Control (test file missing)"
fi

# Test File Utils
print_test "file-utils server"
cd "$SERVERS_DIR/file-utils"
if timeout 5 uv run python src/file_utils/main.py < /dev/null > /dev/null 2>&1; then
    print_pass "File Utils"
else
    print_fail "File Utils"
fi

echo ""
echo "🎯 Test Summary Complete"
echo "Check individual server logs for detailed results"
EOF

chmod +x "scripts/test-all-servers.sh"

# Set up MCP configuration
print_status "Setting up MCP configuration..."

if [ ! -d "$HOME/.kiro/settings" ]; then
    mkdir -p "$HOME/.kiro/settings"
fi

# Copy production configuration as default
cp "$BASE_DIR/configs/mcp-production.json" "$HOME/.kiro/settings/mcp.json"

print_success "MCP configuration installed"

# Final summary
echo ""
echo "🎉 MCP Services Hub Setup Complete!"
echo "===================================="
echo ""
echo "✅ Ready Services:"
echo "   - ssh-control (Remote server management)"
echo "   - file-utils (File operations)"
echo ""
echo "🔧 Services needing API keys:"
echo "   - github-tools (needs GITHUB_TOKEN)"
echo "   - n8n-tools (needs N8N_API_KEY)"
echo "   - coolify-tools (needs COOLIFY_API_TOKEN)"
echo "   - mem0-tools (needs OPENAI_API_KEY)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Test all servers: ~/Documents/agents-mcp/scripts/test-all-servers.sh"
echo "   2. Configure API keys in ~/.kiro/settings/mcp.json"
echo "   3. Enable additional servers by setting 'disabled': false"
echo ""
echo "📚 Documentation: ~/Documents/agents-mcp/README.md"

print_success "Setup completed successfully!"
EOF