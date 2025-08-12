# 🔧 Technology Stack & Standards

## Core Technology Stack

### Frontend Stack
- **Framework**: Next.js 15.4.1 with App Router (MANDATORY)
- **Language**: TypeScript 5.7.3 (STRICT MODE)
- **Styling**: Tailwind CSS 3.4.17 + Shadcn/ui components
- **State Management**: React hooks + Supabase real-time subscriptions
- **Icons**: Lucide React (1000+ icons available)
- **Internationalization**: Custom i18n system (Arabic/English)

### Backend Stack - Multi-Agent System
- **Primary Framework**: Google ADK (Agent Development Kit) - InitialCustomerAgent & N8nWorkflowAgent
- **Secondary Framework**: LangGraph - CodeGenerationAgent (complex workflows)
- **Tertiary Framework**: Pydantic AI - ConsultingAgent (structured applications)
- **Language**: Python 3.11+ with uv package manager
- **API Layer**: FastAPI for additional endpoints (when needed)
- **AI Engine**: Google Gemini 2.0 Flash for conversational AI
- **Database**: Supabase (PostgreSQL-based) with real-time features
- **Workflow Engine**: n8n via MCP (Model Context Protocol) server
- **Real-time Communication**: LiveKit for human consultant handoff

### Infrastructure Stack
- **Containerization**: Docker + Docker Compose (PRODUCTION STANDARD)
- **Web Server**: Nginx with SSL termination
- **SSL Certificates**: Cloudflare Origin certificates
- **Monitoring**: Prometheus + Grafana + N8N workflows
- **CI/CD**: GitHub Actions with comprehensive pipeline
- **Deployment**: VPS (Debian 12, 23GB RAM, 394GB storage)

## Development Standards

### Code Quality Standards
```python
# Python Standards (ADK Agent Development)
- Use type hints for all functions
- Follow PEP 8 with 88-character line limit
- Use docstrings for all classes and methods
- Implement proper error handling with try/catch
- Use uv for dependency management
```

```typescript
// TypeScript Standards (Frontend)
- Strict mode enabled
- Use interfaces for all data structures
- Implement proper error boundaries
- Use React 19 features appropriately
- Follow Next.js App Router patterns
```

### Architecture Patterns

#### Agent Development (ADK)
```python
# Service Pattern
class SupabaseService:
    """Service class for database operations"""
    def __init__(self, config: dict):
        self.client = create_client(config['url'], config['key'])
    
    async def create_customer(self, data: CustomerData) -> Customer:
        # Implementation with proper error handling
        pass

# Tool Pattern (ADK Tools)
@tool
def analyze_customer_requirements(conversation: str) -> RequirementsAnalysis:
    """Extract requirements from customer conversation"""
    # Implementation using Gemini AI
    pass
```

#### Frontend Patterns
```typescript
// Component Pattern
interface ComponentProps {
  data: DataType;
  onAction: (action: ActionType) => void;
}

export function Component({ data, onAction }: ComponentProps) {
  // Implementation with proper error handling
  return <div>...</div>;
}

// Service Pattern
export class ApiService {
  private baseUrl: string;
  
  async fetchData<T>(endpoint: string): Promise<T> {
    // Implementation with error handling
  }
}
```

### File Organization Standards

#### Backend Structure (MANDATORY) - Four-Agent System
```
agent/my_adk_agent/
├── agents/               # Four specialized agents
│   ├── initial_customer_agent.py    # Google ADK - New customer onboarding
│   ├── n8n_workflow_agent.py        # Google ADK + MCP - Workflow automation
│   ├── code_generation_agent.py     # LangGraph - Custom development
│   ├── consulting_agent.py          # Pydantic AI - Strategic consulting
│   └── __init__.py
├── services/             # Service integrations
│   ├── supabase_service.py          # Database operations
│   ├── mcp_service.py               # n8n MCP communication
│   ├── livekit_service.py           # Human handoff
│   └── __init__.py
├── models/               # Data models
│   ├── customer.py                  # Customer data models
│   ├── workflow.py                  # Workflow data models
│   ├── project.py                   # Project data models
│   ├── consultation.py              # Consultation data models
│   └── __init__.py
├── mock_google_adk.py    # Mock implementations for development
├── demo_data_generator.py           # Demo data generation
├── test_multi_agent_system.py      # Comprehensive testing
└── __init__.py

n8n-mcp/                  # n8n MCP Server Integration
├── src/                  # MCP server source code
├── docker/               # Docker configuration
├── docs/                 # n8n MCP documentation
└── docker-compose.yml    # n8n MCP deployment
```

#### Frontend Structure (ESTABLISHED)
```
app/                      # Next.js App Router
├── (routes)/            # Route groups
├── api/                 # API routes
├── globals.css          # Global styles
└── layout.tsx           # Root layout

components/              # React components
├── ui/                  # Shadcn/ui components
├── features/            # Feature-specific components
└── layout/              # Layout components
```

## Dependencies & Versions

### Critical Dependencies (DO NOT CHANGE WITHOUT APPROVAL)
```json
{
  "frontend": {
    "next": "15.4.1",
    "react": "19.0.0",
    "typescript": "5.7.3",
    "tailwindcss": "3.4.17"
  },
  "backend": {
    "python": "3.11+",
    "google-adk": "latest",
    "supabase": "latest",
    "fastapi": "latest"
  }
}
```

### Service Integrations
- **Supabase**: Database, auth, real-time subscriptions
- **Google Gemini**: AI model for conversations and analysis
- **n8n**: Workflow automation via MCP server
- **Livekit**: Real-time communication for agent handoff
- **Stripe**: Payment processing (configured)
- **Prometheus/Grafana**: Monitoring and metrics

## Environment Management

### Environment Variables (CRITICAL)
```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# AI Services
GOOGLE_API_KEY=your_gemini_key

# Workflow Automation (n8n MCP Integration)
N8N_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key
MCP_SERVER_URL=http://localhost:3001

# Real-time Communication
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret

# Payment Processing
STRIPE_PUBLISHABLE_KEY=your_stripe_key
STRIPE_SECRET_KEY=your_stripe_secret
```

### Container Configuration
```yaml
# Production Containers (DO NOT MODIFY)
services:
  agentic-frontend-prod:
    ports: ["3000:3000"]
  agentic-backend-prod:
    ports: ["8000:8000"]
  agentic-redis-prod:
    ports: ["6379:6379"]

# Development Containers (Safe to modify)
services:
  agentic-frontend-dev:
    ports: ["3001:3000"]
  agentic-backend-dev:
    ports: ["8001:8000"]
  agentic-redis-dev:
    ports: ["6380:6379"]
```

## Testing Standards

### Test Coverage Requirements
- **Unit Tests**: 70% minimum coverage
- **Integration Tests**: All service connections tested
- **End-to-End Tests**: Critical user journeys covered
- **Performance Tests**: Response time benchmarks

### Testing Tools
```python
# Backend Testing
pytest                    # Test runner
pytest-asyncio           # Async test support
pytest-cov              # Coverage reporting
adk eval                 # ADK evaluation framework
```

```typescript
// Frontend Testing
jest                     # Test runner
@testing-library/react   # Component testing
playwright               # E2E testing
```

## Security Standards

### Authentication & Authorization
- **Frontend**: Supabase Auth with RLS (Row Level Security)
- **Backend**: Service role authentication for agent operations
- **API**: JWT tokens for secure communication
- **Admin**: ADK web UI with environment-based access control

### Data Protection
- **GDPR Compliance**: Implemented in data handling
- **Encryption**: All sensitive data encrypted at rest
- **SSL/TLS**: Cloudflare certificates for all communications
- **Secrets Management**: Environment variables, never in code

## Performance Standards

### Response Time Targets
- **Frontend**: < 1.5s page load time
- **Backend**: < 500ms API response time
- **Agent Processing**: < 2s for customer inquiry analysis
- **Database Queries**: < 100ms for standard operations

### Resource Utilization
- **Memory**: < 80% utilization under normal load
- **CPU**: < 70% utilization under normal load
- **Disk**: < 70% utilization with monitoring alerts
- **Network**: Optimized for minimal bandwidth usage

## Deployment Standards

### Container Strategy
- **Production**: Separate containers for frontend, backend, redis
- **Development**: Offset ports for parallel development
- **Health Checks**: All containers must implement health endpoints
- **Zero Downtime**: Rolling deployments with health validation

### CI/CD Pipeline
- **GitHub Actions**: Automated testing and deployment
- **Security Scanning**: CodeQL, Dependabot, Trivy integration
- **Quality Gates**: Tests must pass before deployment
- **Monitoring**: Comprehensive health checks post-deployment

---

**Last Updated**: January 2025  
**Compliance**: Production-ready standards enforced  
**Review Cycle**: Monthly technology stack assessment