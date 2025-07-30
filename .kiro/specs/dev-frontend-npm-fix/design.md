# Design Document

## Overview

This design addresses the npm and Docker container deployment issues preventing the development frontend from running at dev.consulting.sa. The solution focuses on fixing the Next.js 15.4.4 + React 19.1.1 frontend container deployment, ensuring proper integration with the existing development backend services, and establishing a reliable development environment that mirrors production functionality.

## Architecture

### Current Development Environment State
```
VPS (217.79.255.54):
├── ✅ agentic-agent-dev (Python ADK, port 8001, healthy)
├── ✅ agentic-redis-dev (Redis cache, port 6380, healthy)  
├── ✅ agentic-n8n-dev (n8n workflows, port 5679, running)
├── ✅ Static dev page (nginx serving /var/www/dev-consulting/)
└── ❌ agentic-frontend-dev (Next.js container, port 3001, missing)
```

### Target Architecture
```
Complete Development Stack:
├── Frontend Container (agentic-frontend-dev)
│   ├── Next.js 15.4.4 + React 19.1.1
│   ├── Port 3001 (internal) → 443 (nginx proxy)
│   ├── Environment: .env.dev configuration
│   └── API calls → dev.consulting.sa/api (backend)
├── Backend Integration
│   ├── Existing agentic-agent-dev (port 8001)
│   ├── API routing through nginx
│   └── Development database tables (dev_ prefix)
└── Infrastructure
    ├── Docker Compose orchestration
    ├── Nginx reverse proxy configuration
    └── SSL termination (wildcard *.consulting.sa)
```

## Components and Interfaces

### 1. Docker Container Configuration

**Frontend Container (agentic-frontend-dev)**
- **Base Image**: Node.js 20-alpine (matching upgraded requirements)
- **Build Process**: Multi-stage Docker build for optimization
- **Port Mapping**: Internal 3000 → External 3001
- **Environment**: Development-specific variables from .env.dev
- **Health Checks**: HTTP endpoint monitoring
- **Volume Mounts**: Source code for hot reload capability

**Docker Compose Integration**
- **Service Name**: frontend-dev
- **Network**: Shared development network with backend services
- **Dependencies**: redis-dev, backend-dev (startup order)
- **Restart Policy**: unless-stopped for reliability

### 2. Environment Configuration

**Development Environment Variables**
```env
# Core Configuration
NODE_ENV=development
NEXT_PUBLIC_SITE_URL=https://dev.consulting.sa
NEXT_PUBLIC_API_URL=https://dev.consulting.sa/api

# Database Integration
NEXT_PUBLIC_SUPABASE_URL=https://xjkdaimasvoufshspibj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[development_key]

# Service Integration
GEMINI_API_KEY=[shared_with_production]
STRIPE_PUBLISHABLE_KEY=[test_key_for_development]

# Development Features
DEBUG=true
NEXT_TELEMETRY_DISABLED=1
```

### 3. Nginx Reverse Proxy Configuration

**Development Site Routing**
```nginx
server {
    server_name dev.consulting.sa;
    
    # Frontend routing
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API routing
    location /api/ {
        proxy_pass http://localhost:8001/;
    }
    
    # Development tools
    location /n8n/ {
        proxy_pass http://localhost:5679/;
    }
}
```

### 4. Build and Deployment Pipeline

**Build Process**
1. **Dependency Installation**: npm install with proper Node.js 20 environment
2. **TypeScript Compilation**: Ensure all types are resolved
3. **Next.js Build**: Production-ready build for container
4. **Asset Optimization**: Image and CSS optimization
5. **Container Creation**: Multi-stage Docker build

**Deployment Sequence**
1. **Pre-deployment**: Stop existing containers, clean environment
2. **File Transfer**: Copy project files with proper directory structure
3. **Container Build**: Build frontend container with proper environment
4. **Service Startup**: Start services in dependency order
5. **Health Validation**: Verify all services are responding
6. **Nginx Update**: Update reverse proxy configuration

## Data Models

### Frontend-Backend Communication

**API Request Flow**
```
Browser → https://dev.consulting.sa/api/endpoint
       → Nginx (SSL termination)
       → agentic-agent-dev:8001/endpoint
       → Response back through chain
```

**Environment-Specific Data**
- **Database Tables**: Use dev_ prefixed tables in Supabase
- **API Keys**: Development/test keys for external services
- **Logging**: Enhanced debug logging for troubleshooting
- **Caching**: Development Redis instance (port 6380)

### Configuration Management

**Environment Variable Hierarchy**
1. **Container Environment**: Docker compose environment section
2. **File-based Config**: .env.dev file mounted in container
3. **Runtime Config**: Next.js runtime configuration
4. **Build-time Config**: Environment variables during build

## Error Handling

### Container Deployment Errors

**Build Failures**
- **npm install errors**: Clear npm cache, verify Node.js version compatibility
- **TypeScript compilation**: Fix type errors, update dependencies
- **Next.js build errors**: Resolve import issues, check configuration
- **Docker build failures**: Verify Dockerfile syntax, base image availability

**Runtime Errors**
- **Container startup failures**: Check port conflicts, environment variables
- **Service connectivity**: Verify network configuration, service discovery
- **Health check failures**: Validate endpoint responses, service readiness
- **Proxy configuration**: Test nginx routing, SSL certificate validity

### Integration Issues

**Frontend-Backend Communication**
- **CORS errors**: Configure proper CORS headers in backend
- **API endpoint failures**: Verify backend service health, routing configuration
- **Authentication issues**: Check Supabase configuration, API keys
- **Database connectivity**: Validate development database access

**Environment Configuration**
- **Missing variables**: Implement validation and clear error messages
- **Invalid API keys**: Provide fallback mechanisms, clear error reporting
- **Service unavailability**: Implement graceful degradation, retry logic
- **SSL/TLS issues**: Verify certificate configuration, domain routing

## Testing Strategy

### Container Testing

**Build Verification**
- **Local Build Test**: Verify container builds successfully locally
- **Dependency Check**: Ensure all npm packages install correctly
- **TypeScript Validation**: Confirm all types compile without errors
- **Next.js Build**: Validate production build completes successfully

**Deployment Testing**
- **Container Startup**: Verify container starts and stays running
- **Health Endpoints**: Test container health check responses
- **Port Accessibility**: Confirm services are accessible on correct ports
- **Environment Loading**: Validate environment variables are loaded correctly

### Integration Testing

**Frontend-Backend Integration**
- **API Connectivity**: Test all API endpoints from frontend
- **Database Operations**: Verify CRUD operations work correctly
- **Authentication Flow**: Test login/logout functionality
- **Real-time Features**: Validate WebSocket connections, live updates

**End-to-End Testing**
- **User Workflows**: Test complete user journeys
- **Cross-browser Testing**: Verify functionality across browsers
- **Mobile Responsiveness**: Test responsive design and functionality
- **Performance Testing**: Validate page load times, API response times

### Comparison Testing

**Production Parity**
- **Feature Comparison**: Ensure development matches production functionality
- **UI/UX Consistency**: Verify visual and interaction consistency
- **Performance Baseline**: Compare performance metrics with production
- **Data Integrity**: Validate development data operations

## Implementation Approach

### Phase 1: Environment Preparation
- Fix environment variable configuration in .env.dev
- Ensure proper directory structure on VPS
- Validate Docker and Docker Compose setup
- Prepare deployment scripts and configurations

### Phase 2: Container Development
- Create/update Dockerfile.frontend for Next.js 15.4.4
- Configure Docker Compose for development environment
- Implement proper build process and optimization
- Add health checks and monitoring

### Phase 3: Integration Setup
- Configure nginx reverse proxy for full stack
- Set up frontend-backend API routing
- Implement proper CORS and security headers
- Configure SSL and domain routing

### Phase 4: Deployment and Testing
- Deploy complete development environment
- Run comprehensive health checks
- Test all integration points
- Validate against production functionality

### Phase 5: Documentation and Maintenance
- Document deployment process and troubleshooting
- Create maintenance procedures
- Establish monitoring and alerting
- Provide team training and handoff

## Success Criteria

### Technical Success
- ✅ Frontend container builds and runs successfully
- ✅ Development site accessible at https://dev.consulting.sa
- ✅ All API endpoints functional and responsive
- ✅ Frontend-backend integration working correctly
- ✅ Environment variables properly configured
- ✅ SSL and security properly implemented

### Functional Success
- ✅ Development environment mirrors production functionality
- ✅ All major user workflows working correctly
- ✅ Performance meets acceptable standards
- ✅ Error handling and logging implemented
- ✅ Development tools and debugging available
- ✅ Team can effectively use development environment

### Operational Success
- ✅ Deployment process automated and reliable
- ✅ Monitoring and health checks implemented
- ✅ Documentation complete and accessible
- ✅ Troubleshooting procedures established
- ✅ Maintenance processes defined
- ✅ Team trained on development workflow