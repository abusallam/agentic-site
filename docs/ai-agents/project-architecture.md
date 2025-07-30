# Project Architecture Documentation

## Overview

The Agentic AI Platform is a production-ready SaaS platform with dual-agent architecture designed for customer journey orchestration and workflow automation. The system is built with modern technologies and follows best practices for scalability, security, and maintainability.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agentic AI Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Frontend      │    │     Backend      │    │  External   │ │
│  │   (Next.js)     │◄──►│   (Python ADK)   │◄──►│  Services   │ │
│  │                 │    │                  │    │             │ │
│  │ • Website       │    │ • Agent System   │    │ • Supabase  │ │
│  │ • Chatbots      │    │ • Orchestration  │    │ • Gemini AI │ │
│  │ • User UI       │    │ • Integrations   │    │ • Stripe    │ │
│  │ • Admin Panel   │    │ • MCP Server     │    │ • Livekit   │ │
│  └─────────────────┘    └──────────────────┘    │ • n8n       │ │
│                                                 └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Frontend Layer (Next.js)
```
frontend/
├── app/                     # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   └── api/                # API routes
├── components/             # Reusable components
│   ├── ui/                 # shadcn/ui components
│   ├── chatbot/           # Chatbot components
│   ├── features/          # Feature components
│   └── layout/            # Layout components
├── lib/                   # Utility libraries
│   ├── supabase.ts        # Supabase client
│   ├── utils.ts           # Utility functions
│   └── i18n.ts            # Internationalization
└── styles/                # Global styles
    ├── globals.css        # Global CSS
    └── animations.css     # Animation styles
```

#### Backend Layer (Python ADK)
```
backend/agent/my_adk_agent/
├── agent.py               # Main agent class
├── services/              # Service integrations
│   ├── auth_service.py    # Authentication
│   ├── supabase_service.py # Database operations
│   ├── stripe_service.py  # Payment processing
│   ├── livekit_service.py # Real-time communication
│   └── mcp_service.py     # MCP server integration
├── tools/                 # ADK tools
├── tests/                 # Test files
└── __init__.py
```

## Technology Stack

### Frontend Technologies
- **Next.js 15.4.1**: React framework with App Router
- **React 19.1.0**: UI library with latest features
- **TypeScript 5.7.3**: Type-safe JavaScript
- **Tailwind CSS 3.4.17**: Utility-first CSS framework
- **shadcn/ui**: Modern component library
- **Supabase Client**: Database and auth integration

### Backend Technologies
- **Python 3.12.9**: Modern Python runtime
- **Google ADK**: Agent Development Kit
- **FastAPI**: High-performance API framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Supabase Python**: Database client

### Infrastructure
- **Docker**: Containerization
- **Nginx**: Reverse proxy and SSL termination
- **Redis**: Caching and session storage
- **Ubuntu VPS**: Production server
- **Wildcard SSL**: *.consulting.sa certificate

### External Services
- **Supabase**: PostgreSQL database, authentication, real-time
- **Google Gemini**: Primary AI model
- **Stripe**: Payment processing
- **Livekit**: Real-time communication
- **n8n**: Workflow automation
- **MCP Server**: Model Context Protocol

## Environment Architecture

### Production Environment
```
Production (main branch)
├── URL: https://consulting.sa
├── Directory: /opt/agentic-platform
├── Services:
│   ├── Frontend: Port 3000
│   ├── Backend: Port 8000
│   ├── Redis: Port 6379
│   └── n8n: Port 5678
├── SSL: Wildcard certificate
├── Logging: INFO level
└── Database: Production tables
```

### Development Environment
```
Development (develop branch)
├── URL: https://dev.consulting.sa
├── Directory: /opt/agentic-platform-dev
├── Services:
│   ├── Frontend: Port 3001
│   ├── Backend: Port 8001
│   ├── Redis: Port 6380
│   └── n8n: Port 5679
├── SSL: Same wildcard certificate
├── Logging: DEBUG level
└── Database: dev_ prefixed tables
```

## Data Flow Architecture

### Customer Interaction Flow
```
1. Customer visits website (Next.js)
   ↓
2. Interacts with chatbot (Google Gemini)
   ↓
3. Complex queries → ADK Agent (Python)
   ↓
4. Agent processes request
   ↓
5. Integrates with services (Supabase, Stripe, etc.)
   ↓
6. Returns response to customer
   ↓
7. Optional: Live agent handoff (Livekit)
```

### Agent Orchestration Flow
```
1. ADK Agent receives request
   ↓
2. Analyzes customer intent
   ↓
3. Routes to appropriate service
   ↓
4. CustomerJourneyAgent: Main orchestration
   ↓
5. N8nMCPAgent: Workflow automation
   ↓
6. Service integrations execute
   ↓
7. Results aggregated and returned
```

## Security Architecture

### Authentication & Authorization
- **Frontend**: Supabase Auth (JWT tokens)
- **Backend**: Service key authentication
- **API**: Bearer token validation
- **Admin**: Environment-based access control

### Data Security
- **Encryption**: TLS 1.3 in transit
- **Storage**: Encrypted at rest (Supabase)
- **API Keys**: Environment variables only
- **Secrets**: Never committed to code

### Network Security
- **SSL/TLS**: A+ grade encryption
- **HTTPS**: Enforced everywhere
- **CORS**: Properly configured
- **Rate Limiting**: Built-in protection

## Deployment Architecture

### Docker Containerization
```
Production Containers:
├── agentic-frontend-prod (Next.js)
├── agentic-backend-prod (Python ADK)
├── agentic-redis-prod (Redis)
└── agentic-nginx-prod (Nginx)

Development Containers:
├── agentic-frontend-dev (Next.js)
├── agentic-backend-dev (Python ADK)
├── agentic-redis-dev (Redis)
├── agentic-n8n-dev (n8n)
└── agentic-nginx-dev (Nginx)
```

### Network Architecture
```
Internet
    ↓
Nginx (SSL Termination)
    ↓
┌─────────────────────────────────┐
│         Docker Network          │
├─────────────────────────────────┤
│ Frontend ←→ Backend ←→ Redis    │
│    ↓           ↓                │
│ Static      Services            │
│ Assets      Integration         │
└─────────────────────────────────┘
    ↓
External Services
```

## Integration Architecture

### Service Integration Pattern
```python
# Service Layer Pattern
class ServiceBase:
    def __init__(self, config):
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        # Service-specific initialization
        pass
    
    async def execute(self, request):
        # Service-specific logic
        pass
```

### MCP Server Integration
```
ADK Agent ←→ MCP Server ←→ n8n
    ↓              ↓         ↓
Services      Protocol   Workflows
```

## Monitoring & Observability

### Health Checks
- **Frontend**: `/api/health` endpoint
- **Backend**: `/health` endpoint
- **Services**: Individual health checks
- **Infrastructure**: Docker health checks

### Logging Strategy
- **Production**: INFO level, structured logging
- **Development**: DEBUG level, verbose logging
- **Rotation**: Automatic log rotation
- **Storage**: JSON format for parsing

### Performance Monitoring
- **Response Times**: API endpoint monitoring
- **Resource Usage**: CPU, memory, disk
- **Error Rates**: Application error tracking
- **Uptime**: Service availability monitoring

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: Static generation + CDN
- **Backend**: Stateless design
- **Database**: Supabase auto-scaling
- **Caching**: Redis clustering ready

### Performance Optimization
- **Frontend**: Next.js optimizations
- **Backend**: Async/await architecture
- **Database**: Query optimization
- **Caching**: Multi-layer caching strategy

## Development Workflow

### Branch Strategy
```
main (production)
├── develop (development)
│   ├── feature/frontend-updates
│   ├── feature/backend-enhancements
│   └── feature/new-integrations
└── hotfix/* (emergency fixes)
```

### Deployment Process
```
1. Local Development
   ├── Code changes
   ├── Local testing
   └── Push to feature branch

2. Development Environment
   ├── Merge to develop
   ├── Deploy to dev.consulting.sa
   ├── Integration testing
   └── Validation

3. Production Deployment
   ├── Merge develop → main
   ├── Deploy to consulting.sa
   ├── Health checks
   └── Monitoring
```

## Best Practices

### Code Organization
- **Separation of Concerns**: Clear layer separation
- **Single Responsibility**: Each component has one purpose
- **Dependency Injection**: Configurable service dependencies
- **Error Handling**: Comprehensive error management

### Configuration Management
- **Environment Variables**: All configuration externalized
- **Secrets Management**: Secure secret storage
- **Environment Parity**: Dev/prod consistency
- **Configuration Validation**: Startup validation

### Testing Strategy
- **Unit Tests**: Component-level testing
- **Integration Tests**: Service integration testing
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

This architecture provides a solid foundation for building and maintaining a production-ready AI platform with proper separation of concerns, security, and scalability.