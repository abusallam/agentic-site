# 🏗️ Project Architecture & Development Rules - PRODUCTION READY

## 🎯 Project Overview
Complete AI SaaS platform with dual-agent architecture for customer journey orchestration and n8n workflow automation. **STATUS: PRODUCTION READY** ✅

### **Current Implementation Status**
- ✅ **CustomerJourneyAgent**: Main orchestration agent (WORKING)
- ✅ **N8nMCPAgent**: Dedicated n8n workflow agent (WORKING)  
- ✅ **Real API Integrations**: Live n8n, Supabase, Gemini (CONNECTED)
- ✅ **Testing Suite**: Comprehensive integration tests (PASSING)
- ✅ **Documentation**: Complete setup and usage guides (READY)

## Architecture Principles

### Four-Agent System Architecture
- **Frontend (Next.js)**: Customer-facing website with intelligent agent routing
- **Backend (Multi-Agent System)**: Four specialized agents with different frameworks
- **Intelligent Routing**: Automatic message routing to appropriate specialized agent
- **Shared Database**: All agents use Supabase with specialized data models
- **n8n MCP Integration**: Direct workflow automation via Model Context Protocol
- **LiveKit Integration**: Human handoff capabilities for consulting services

### Four-Agent Customer Journey
1. **InitialCustomerAgent (Google ADK)**: New customer onboarding with Arabic/English detection
2. **N8nWorkflowAgent (ADK + MCP)**: Authenticated workflow automation with n8n integration
3. **CodeGenerationAgent (LangGraph)**: Custom AI agent development with multi-framework support
4. **ConsultingAgent (Pydantic AI)**: Strategic consulting with LiveKit human handoff
5. **Intelligent Routing**: 100% accuracy in message routing to appropriate agents

### Multi-Framework Integration
- **Google ADK**: InitialCustomerAgent and N8nWorkflowAgent (production-ready)
- **LangGraph**: CodeGenerationAgent (complex workflow orchestration)
- **Pydantic AI**: ConsultingAgent (structured AI applications)
- **n8n MCP**: Direct workflow automation communication
- **LiveKit**: Real-time video/audio for human consultations

## Development Constraints

### Backend Development
- **Location**: All backend code MUST stay within `/agent` folder
- **Structure**: Use `/agent/my_adk_agent/` for ADK discovery compatibility
- **Environment Management**: Use `uv` for Python environment management
- **Framework**: Google ADK for agent development

### Frontend Development
- **Constraint**: DO NOT modify existing Next.js website - it's working perfectly
- **Chatbot Integration**: Embed chatbots as components, don't alter core functionality
- **Styling**: Continue using Tailwind CSS and shadcn/ui components

### Admin Interface
- **Foundation**: Use ADK's built-in web UI (`adk web`) as admin interface base
- **Authentication**: Secure ADK web UI with environment-based access control
- **Enhancement**: Extend existing ADK web interface rather than building from scratch
- **Features**: Leverage built-in agent monitoring, debugging, evaluation tools

## Technology Stack

### Frontend
- Next.js 15+ with App Router
- TypeScript
- Tailwind CSS + shadcn/ui
- Supabase client for database operations
- React 19

### Backend
- Python with Google ADK framework
- Supabase Python client
- Integration services: n8n, MCP, Stripe, Livekit
- Google Gemini for AI capabilities
- FastAPI for additional API endpoints if needed

### Infrastructure
- Docker deployment (single container or docker-compose)
- Supabase for database and authentication
- Environment variables managed centrally
- GitHub Actions for CI/CD

## Service Integrations

### Required Services
- **Supabase**: Database, authentication, real-time subscriptions
- **Google Gemini**: AI model for chatbots and agents
- **Livekit**: Real-time communication for live agent handoff
- **n8n**: Workflow automation platform
- **MCP Server**: Communication bridge between agent and n8n
- **Stripe**: Payment processing

### Integration Patterns
- Each service should have its own service class in `/agent/my_adk_agent/services/`
- Use environment variables for all API keys and configuration
- Implement proper error handling and retry logic
- Mock implementations for development and testing

## Development Workflow

### Code Organization
```
/agent/my_adk_agent/
├── agent.py              # Main agent class
├── services/             # Service integrations
│   ├── auth_service.py
│   ├── livekit_service.py
│   ├── mcp_service.py
│   ├── supabase_service.py
│   └── stripe_service.py
├── tools/                # ADK tools
├── tests/                # Test files
└── __init__.py
```

### Testing Strategy
- Use ADK's built-in evaluation framework
- `adk web` for interactive testing and debugging
- `pytest` for programmatic testing
- `adk eval` for CLI-based evaluation
- Create evaluation datasets for different customer scenarios

### Documentation Requirements
- Keep all documentation updated with changes
- Document API integrations and service configurations
- Maintain troubleshooting guides
- Update deployment instructions

## Security & Best Practices

### Environment Variables
- Store all sensitive data in environment variables
- Use single `.env` file at project root
- Never commit API keys or secrets
- Use different configurations for development/production

### Authentication
- Secure ADK web UI access
- Implement proper session management
- Use Supabase Auth for customer authentication
- Separate admin and customer access levels

### Data Handling
- Follow GDPR/privacy compliance
- Secure customer data in Supabase
- Implement proper data retention policies
- Log important events for debugging

## Deployment Strategy

### Container Strategy
- Single deployment containing both Next.js and Python systems
- Use existing Docker configuration
- Maintain separation of concerns within container
- Environment-based configuration

### Monitoring
- Leverage ADK web UI monitoring capabilities
- Implement health checks for all services
- Monitor customer interaction flows
- Track agent performance metrics

## Common Patterns

### Error Handling
- Graceful degradation when services are unavailable
- Proper logging for debugging
- User-friendly error messages
- Retry logic for transient failures

### State Management
- Use Supabase for persistent state
- Session management for customer interactions
- Agent state tracking for workflow continuity
- Real-time updates where needed

This document should be referenced for all development decisions and updated as the project evolves.