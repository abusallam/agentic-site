#!/bin/bash

echo "🚀 AI SaaS Platform Status Check"
echo "=================================="
echo ""

# Check Frontend (Next.js)
echo "📱 Frontend (Next.js):"
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "   ✅ Running on http://localhost:3000"
    echo "   ✅ Health check: $(curl -s http://localhost:3000/api/health | jq -r '.status')"
else
    echo "   ❌ Not running on http://localhost:3000"
fi
echo ""

# Check Backend API (Python Agent)
echo "🤖 Backend API (Python Agent):"
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "   ✅ Running on http://localhost:8080"
    echo "   ✅ Health check: $(curl -s http://localhost:8080/api/health | jq -r '.status')"
    echo "   ✅ Agent initialized: $(curl -s http://localhost:8080/api/health | jq -r '.agent_initialized')"
else
    echo "   ❌ Not running on http://localhost:8080"
fi
echo ""

# Check Chat Integration
echo "💬 Chat Integration:"
if curl -s -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"message": "test"}' > /dev/null; then
    echo "   ✅ Frontend to Backend chat working"
else
    echo "   ❌ Chat integration not working"
fi
echo ""

# Check ADK Web UI
echo "🌐 ADK Web UI:"
if curl -s http://localhost:8082 > /dev/null; then
    echo "   ✅ Running on http://localhost:8082"
else
    echo "   ❌ Not running on http://localhost:8082"
fi
echo ""

# Check n8n MCP Server
echo "⚙️ n8n MCP Server:"
if curl -s http://localhost:8003/health > /dev/null; then
    echo "   ✅ Running on http://localhost:8003"
else
    echo "   ⚠️  Not running (start manually if needed)"
fi
echo ""

# Check Database Connection
echo "🗄️ Database (Supabase):"
if curl -s "https://xjkdaimasvoufshspibj.supabase.co/rest/v1/" > /dev/null; then
    echo "   ✅ Supabase connection working"
else
    echo "   ❌ Supabase connection failed"
fi
echo ""

echo "🎯 Access Points:"
echo "   • Website:        http://localhost:3000"
echo "   • Admin Panel:    http://localhost:8082"
echo "   • API Docs:       http://localhost:8080/docs"
echo "   • n8n MCP:        http://localhost:8003"
echo ""

echo "🧪 Test Commands:"
echo "   # Test chat API:"
echo "   curl -X POST http://localhost:3000/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello, I need a chatbot\"}'"
echo ""
echo "   # Test backend directly:"
echo "   curl -X POST http://localhost:8080/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello, I need a chatbot\"}'"
echo ""

echo "📝 Logs:"
echo "   • Frontend logs: Check terminal where 'npm run dev' is running"
echo "   • Backend logs:  Check terminal where Python API server is running"
echo "   • All processes: ps aux | grep -E '(node|python|uvicorn)'"