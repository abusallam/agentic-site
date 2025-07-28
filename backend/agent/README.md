# 🤖 ADK Agent System - Production Ready

## 🎯 Overview

Complete AI SaaS platform with dual-agent architecture for customer journey orchestration and n8n workflow automation.

## 🏗️ Architecture

```
CustomerJourneyAgent (Main)
├── Requirements Analysis (NLP)
├── Service Classification  
├── Customer Management
├── Payment Processing
└── Live Agent Handoff

N8nMCPAgent (Dedicated)
├── n8n MCP Server Management
├── Workflow Creation & Deployment
├── Real n8n API Integration
└── Automation Orchestration
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Navigate to agent directory
cd agent

# Install dependencies
uv sync

# Activate environment
source .venv/bin/activate
```

### 2. Test the System
```bash
# Test main agent
python test_agent.py

# Test n8n MCP integration
python test_n8n_mcp_integration.py

# Start ADK web UI
adk web --port 8082 .
```

### 3. Access Points
- **ADK Web UI**: http://localhost:8082
- **n8n MCP Server**: http://localhost:8003
- **Live n8n Instance**: https://n8n.consulting.sa

## 🔧 Configuration

### Environment Variables (Already Configured)
```bash
# Core Services
SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
N8N_URL=https://n8n.consulting.sa
GEMINI_API_KEY=AIzaSyBzj09AK5ZpQJf...
LIVEKIT_URL=wss://con.livekit.cloud

# Ports
N8N_MCP_PORT=8003
ADK_WEB_PORT=8082
```

## 🎯 Usage Examples

### Natural Language Interface
```python
# Customer requirements
"I need a chatbot for my e-commerce website"

# Server management  
"start n8n server"
"n8n server status"
```

### JSON Command Interface
```python
# Deploy service
{
    "action": "deploy_service",
    "params": {
        "email": "customer@example.com",
        "service_type": "chatbot",
        "config": {"language": "en"}
    }
}

# Get status
{
    "action": "get_status", 
    "params": {"email": "customer@example.com"}
}
```

## 📊 Service Status

| Service | Status | Integration |
|---------|--------|-------------|
| Supabase | ✅ Live | Real database |
| n8n | ✅ Live | Real API |
| Gemini | ✅ Live | Real AI model |
| Livekit | ✅ Live | Real-time comm |
| Stripe | ✅ Ready | Payment processing |

## 🧪 Testing

### Run All Tests
```bash
# Comprehensive integration test
python test_n8n_mcp_integration.py

# Individual agent test
python test_agent.py
```

### Expected Results
- ✅ n8n MCP server starts successfully
- ✅ Requirements analysis works perfectly
- ✅ Service classification accurate
- ✅ Real API connections functional
- ✅ Customer journey flow complete

## 🔍 Troubleshooting

### Common Issues
1. **Port conflicts**: Use different ports (8003, 8082)
2. **Environment loading**: Ensure `.env` path is correct
3. **API credentials**: All real credentials configured

### Debug Commands
```bash
# Check environment
python -c "from dotenv import load_dotenv; load_dotenv('../.env'); import os; print(os.getenv('N8N_URL'))"

# Test n8n connection
curl -H "Authorization: Bearer $(cat ../.env | grep N8N_API_KEY | cut -d= -f2)" https://n8n.consulting.sa/api/v1/workflows
```

## 📚 Key Files

- `my_adk_agent/agent.py`: Main customer journey agent
- `n8n_mcp_agent/agent.py`: Dedicated n8n MCP agent  
- `database_schema.sql`: Supabase table definitions
- `test_n8n_mcp_integration.py`: Comprehensive tests
- `.venv/root_agent.yaml`: ADK agent configuration

## 🎉 Production Ready Features

- ✅ Real API integrations
- ✅ Error handling & logging
- ✅ Security & authentication
- ✅ Comprehensive testing
- ✅ Documentation complete
- ✅ Multi-modal interfaces
- ✅ Scalable architecture

## 📞 Support

- **Platform**: consulting.sa
- **Email**: asim@consulting.sa
- **Status**: Production Ready ✅

The system is fully functional and ready for customer onboarding! 🚀