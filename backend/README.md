# 🤖 Backend - Python ADK Agent System

## 📋 Overview

The backend system is built using Python with the ADK (Agent Development Kit) framework and uses **uv** as the modern Python package manager. It provides a comprehensive CustomerJourneyAgent system with service integrations for AI consulting platform operations.

**Package Manager**: `uv` (modern Python package manager)  
**Python Version**: 3.11+  
**Framework**: Google ADK (Agent Development Kit)  
**Status**: ✅ Production Ready

## 🏗️ Architecture

```
backend/
├── agent/                      # Main agent implementation
│   ├── my_adk_agent/          # CustomerJourneyAgent system
│   │   ├── agent.py           # Main agent class
│   │   ├── services/          # Service integrations
│   │   │   ├── supabase_service.py    # Database operations
│   │   │   ├── mcp_service.py         # MCP communication
│   │   │   ├── monitoring_service.py  # Health monitoring
│   │   │   ├── cicd_service.py        # CI/CD operations
│   │   │   ├── auth_service.py        # Authentication
│   │   │   ├── livekit_service.py     # Real-time communication
│   │   │   └── stripe_service.py      # Payment processing
│   │   ├── tools/             # ADK tools and utilities
│   │   └── tests/             # Agent-specific tests
│   ├── n8n_mcp_agent/         # N8N workflow agent
│   ├── specialized_agents/    # Domain-specific agents
│   ├── main.py               # Agent entry point
│   ├── api_server.py         # FastAPI server
│   ├── pyproject.toml        # Agent dependencies
│   └── uv.lock              # Dependency lock file
├── services/                  # Shared services (if any)
├── tests/                    # Backend integration tests
├── pyproject.toml           # Backend package configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (required)
- **uv** (Python package manager) - [Install Guide](https://docs.astral.sh/uv/)

### Install uv

```bash
# Install uv (cross-platform)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with homebrew (macOS)
brew install uv

# Verify installation
uv --version
```

### Setup and Run

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Navigate to agent directory**
   ```bash
   cd agent
   ```

4. **Install agent-specific dependencies**
   ```bash
   uv sync
   ```

5. **Configure environment**
   ```bash
   # Copy environment template (from project root)
   cp ../../.env.example ../../.env
   # Edit with your actual values
   ```

6. **Run the agent**
   ```bash
   uv run python main.py
   ```

## 📦 Package Management with uv

### Why uv?

- **🚀 Fast**: 10-100x faster than pip
- **🔒 Reliable**: Consistent dependency resolution
- **🆕 Modern**: Built for Python 3.11+
- **🔄 Compatible**: Works with existing pip/requirements.txt

### Common Commands

```bash
# Install dependencies from pyproject.toml
uv sync

# Add new dependency
uv add fastapi

# Add development dependency
uv add --dev pytest

# Remove dependency
uv remove package-name

# Run command in project environment
uv run python main.py

# Run with specific Python version
uv run --python 3.11 python main.py

# Create virtual environment
uv venv

# Install from requirements.txt (legacy support)
uv pip install -r requirements.txt
```

### Dependencies Fixed in This Project

The following dependencies were added/fixed during the project cleanup:

#### Core Dependencies
- **psutil>=5.9.0** - System monitoring and metrics
- **google-generativeai>=0.3.0** - Google Gemini AI integration
- **fastapi>=0.104.0** - Web framework for API endpoints
- **uvicorn>=0.24.0** - ASGI server for FastAPI
- **supabase>=2.0.0** - Database client
- **pydantic>=2.0.0** - Data validation and serialization
- **python-dotenv>=1.0.0** - Environment variable management
- **httpx>=0.25.0** - HTTP client for API calls

#### Service Integrations
- **stripe>=7.0.0** - Payment processing
- **livekit>=0.10.0** - Real-time communication
- **google-adk>=0.1.0** - Agent Development Kit framework

#### Development Dependencies
- **pytest>=7.0.0** - Testing framework
- **pytest-asyncio>=0.21.0** - Async testing support
- **black>=23.0.0** - Code formatting
- **isort>=5.12.0** - Import sorting
- **mypy>=1.5.0** - Type checking
- **ruff>=0.1.0** - Fast linting

## 🔧 Configuration

### Environment Variables

The backend uses the same `.env` file as the frontend (located in project root). Key backend variables:

```env
# Backend Configuration
ADK_AGENT_PORT=8000
ADK_LOG_LEVEL=DEBUG
PYTHONPATH=/app/agent

# Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# AI Services
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Payment
STRIPE_SECRET_KEY=your_stripe_secret

# Communication
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret

# Workflow Automation
N8N_URL=http://localhost:5678
N8N_API_KEY=your_n8n_key

# MCP Configuration
MCP_SERVER_URL=http://localhost:8000
N8N_MCP_PORT=8003
```

### pyproject.toml Configuration

The project uses modern Python packaging with `pyproject.toml`:

```toml
[project]
name = "agentic-backend"
version = "1.0.0"
description = "Python ADK agent system for AI consulting platform"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "supabase>=2.0.0",
    "google-generativeai>=0.3.0",
    "psutil>=5.9.0",
    # ... other dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.9.0",
    "mypy>=1.6.0",
    # ... other dev dependencies
]
```

## 🤖 Agent System

### CustomerJourneyAgent

The main agent class that orchestrates customer interactions:

```python
from my_adk_agent.agent import CustomerJourneyAgent

# Initialize agent
agent = CustomerJourneyAgent()

# Process customer inquiry
response = await agent.process_customer_inquiry(
    inquiry="I need help with AI chatbots",
    customer_data={"email": "customer@example.com", "name": "John Doe"}
)

# Create customer record
customer = await agent.create_customer_record({
    "email": "customer@example.com",
    "name": "John Doe",
    "company": "Example Corp"
})

# Health check
health = await agent.health_check()
```

### Service Integrations

#### Supabase Service
```python
from my_adk_agent.services.supabase_service import SupabaseService

service = SupabaseService()
customer = await service.create_customer(customer_data)
```

#### MCP Service
```python
from my_adk_agent.services.mcp_service import MCPService

service = MCPService()
result = await service.execute_n8n_workflow("workflow-name", data)
```

#### Monitoring Service
```python
from my_adk_agent.services.monitoring_service import MonitoringService

service = MonitoringService()
service.record_request("POST", "/api/endpoint", 200, 0.5)
health = await service.get_health()
```

## 📜 Available Scripts

### Development Scripts

```bash
# Install dependencies
uv sync

# Run main agent
uv run python agent/main.py

# Run API server (if available)
uv run python agent/api_server.py

# Run specific agent tests
uv run python agent/test_agent.py
uv run python agent/test_multi_agent_system.py
uv run python agent/test_n8n_mcp_integration.py
```

### Code Quality Scripts

```bash
# Format code with Black
uv run black .

# Sort imports with isort
uv run isort .

# Type checking with mypy
uv run mypy agent/

# Linting with ruff
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

### Testing Scripts

```bash
# Run all tests
uv run pytest tests/

# Run tests with verbose output
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=agent

# Run specific test file
uv run pytest tests/test_agent.py

# Run tests matching pattern
uv run pytest -k "test_customer"
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_agent.py       # Agent unit tests
│   ├── test_services.py    # Service unit tests
│   └── ...
├── integration/            # Integration tests
│   ├── test_supabase.py   # Database integration
│   ├── test_mcp.py        # MCP integration
│   └── ...
├── fixtures/              # Test fixtures
└── conftest.py           # Pytest configuration
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=agent --cov-report=html

# Run specific test categories
uv run pytest -m unit        # Unit tests only
uv run pytest -m integration # Integration tests only
uv run pytest -m slow        # Slow tests only

# Run tests in parallel
uv run pytest -n auto
```

## 🔍 Health Monitoring

The backend includes comprehensive health monitoring:

### Health Check Endpoint

```python
# Check agent health
health = await agent.health_check()

# Returns:
{
    "agent": "healthy",
    "services": {
        "supabase": "healthy",
        "mcp": "healthy", 
        "gemini": "configured"
    },
    "timestamp": "2025-01-27T20:32:20.283535"
}
```

### Metrics Collection

```python
# Record request metrics
monitoring_service.record_request("POST", "/api/chat", 200, 0.5)

# Get Prometheus metrics
metrics = monitoring_service.get_metrics()

# Get system health
health = await monitoring_service.get_health()
```

## 🚀 Deployment

### Local Development

```bash
# Start agent in development mode
cd backend/agent
uv run python main.py
```

### Production Deployment

```bash
# Install production dependencies only
uv sync --no-dev

# Run with production settings
NODE_ENV=production uv run python agent/main.py
```

### Docker Deployment

The backend is containerized with Docker:

```dockerfile
# Use Python 3.11 base image
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Copy project files
COPY . /app
WORKDIR /app

# Install dependencies
RUN uv sync --no-dev

# Run agent
CMD ["uv", "run", "python", "agent/main.py"]
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python path
uv run python -c "import sys; print(sys.path)"

# Verify agent imports
uv run python -c "from my_adk_agent.agent import CustomerJourneyAgent; print('OK')"
```

#### Environment Issues
```bash
# Check environment variables
uv run python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# Test Supabase connection
uv run python -c "from my_adk_agent.services.supabase_service import SupabaseService; s=SupabaseService(); print('Supabase OK')"
```

#### Performance Issues
```bash
# Monitor system resources
uv run python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# Check agent health
uv run python -c "
import asyncio
from my_adk_agent.agent import CustomerJourneyAgent
async def check():
    agent = CustomerJourneyAgent()
    health = await agent.health_check()
    print(health)
asyncio.run(check())
"
```

### Error Solutions

#### "Module not found" errors
- Ensure you're in the correct directory (`backend/agent/`)
- Run `uv sync` to install dependencies
- Check that Python 3.11+ is being used

#### Service connection errors
- Verify environment variables are set correctly
- Check service availability (Supabase, APIs)
- Review service-specific logs

#### Agent startup failures
- Check all required dependencies are installed
- Verify environment configuration
- Review agent logs for specific error messages

## 📚 API Reference

### Agent Methods

#### `process_customer_inquiry(inquiry: str, customer_data: Dict) -> str`
Process a customer inquiry and generate AI response.

#### `create_customer_record(customer_data: Dict) -> Optional[Dict]`
Create a new customer record in the database.

#### `trigger_customer_workflow(customer_id: str, workflow_data: Dict) -> Dict`
Trigger automated workflow for customer.

#### `health_check() -> Dict`
Perform comprehensive health check of all services.

### Service Classes

- **SupabaseService**: Database operations
- **MCPService**: MCP protocol communication
- **MonitoringService**: Health monitoring and metrics
- **CICDService**: CI/CD operations
- **AuthService**: Authentication handling
- **LivekitService**: Real-time communication
- **StripeService**: Payment processing

## 🔗 Related Documentation

- **[Local Testing Guide](../LOCAL_TESTING_GUIDE.md)** - Complete local testing setup
- **[Main README](../README.md)** - Project overview and setup
- **[Frontend README](../frontend/README.md)** - Frontend documentation
- **[Infrastructure README](../infrastructure/README.md)** - Deployment documentation

## 📞 Support

For backend-specific issues:

1. **Check logs**: Agent provides detailed error logging
2. **Verify environment**: Ensure all required variables are set
3. **Test services**: Use health check endpoints
4. **Review dependencies**: Run `uv sync` to ensure all packages are installed

---

**Package Manager**: uv  
**Python Version**: 3.11+  
**Status**: Production Ready  
**Last Updated**: January 27, 2025