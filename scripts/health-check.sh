#!/bin/bash

# Comprehensive health check for Coolify
# Checks both frontend and backend services

set -e

FRONTEND_PORT=${PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-8080}

echo "🔍 Health Check - Frontend: $FRONTEND_PORT, Backend: $BACKEND_PORT"

# Check frontend health
if ! curl -f -s http://localhost:$FRONTEND_PORT/api/health >/dev/null; then
    echo "❌ Frontend health check failed"
    exit 1
fi

# Check backend health
if ! curl -f -s http://localhost:$BACKEND_PORT/api/health >/dev/null; then
    echo "❌ Backend health check failed"
    exit 1
fi

echo "✅ All services healthy"
exit 0