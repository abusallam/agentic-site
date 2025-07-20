#!/bin/bash

# Start Development Servers for AI SaaS Platform
echo "🚀 Starting AI SaaS Platform Development Servers..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start Next.js frontend
echo "📱 Starting Next.js Frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Start Python backend with UV
echo "🤖 Starting Python Backend Agent..."
cd agent
uv run python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start ADK Web UI
echo "🌐 Starting ADK Web UI on http://localhost:8082..."
uv run adk web --port 8082 . &
ADK_PID=$!

cd ..

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "🌐 Access Points:"
echo "   • Frontend (Next.js):  http://localhost:3000"
echo "   • Backend Agent:       Running in background"
echo "   • ADK Web UI:          http://localhost:8082"
echo "   • n8n MCP Server:      http://localhost:8003 (when started)"
echo ""
echo "📝 Logs:"
echo "   • Frontend: Terminal output above"
echo "   • Backend:  Check agent logs"
echo "   • ADK Web:  http://localhost:8082"
echo ""
echo "🛑 Press Ctrl+C to stop all servers"
echo ""

# Wait for all background processes
wait