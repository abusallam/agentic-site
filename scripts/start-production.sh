#!/bin/bash

# Production startup script for Coolify deployment
# Starts both Next.js frontend and Python backend

set -e

echo "🚀 Starting AI SaaS Platform in Production Mode..."

# Get port from environment or use default
FRONTEND_PORT=${PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-8080}

echo "📱 Frontend will run on port: $FRONTEND_PORT"
echo "🤖 Backend will run on port: $BACKEND_PORT"

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup SIGTERM SIGINT

# Start Python backend
echo "🤖 Starting Python Backend Agent..."
cd /app/agent
export PYTHONPATH=/app/agent
export ADK_AGENT_PORT=$BACKEND_PORT
uv run python api_server.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 2
done

# Start Next.js frontend
echo "📱 Starting Next.js Frontend..."
cd /app
export PORT=$FRONTEND_PORT
node server.js &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:$FRONTEND_PORT/api/health >/dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start"
        exit 1
    fi
    sleep 2
done

echo "🎉 All services are running!"
echo "📱 Frontend: http://localhost:$FRONTEND_PORT"
echo "🤖 Backend: http://localhost:$BACKEND_PORT"

# Wait for any process to exit
wait