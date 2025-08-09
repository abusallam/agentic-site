# 📁 Project Structure & Conventions

## Project Root Structure

```
agentic-site/                    # Root directory
├── .kiro/                       # Kiro configuration and specs
│   ├── specs/                   # Feature specifications
│   ├── steering/                # Project context and standards
│   └── settings/                # Kiro settings and MCP config
├── frontend/                    # Next.js application
├── backend/                     # Python ADK agent (DEPRECATED - use agent/)
├── agent/                       # PRIMARY: Python ADK agent framework
├── infrastructure/              # Deployment and infrastructure
├── docs/                        # Project documentation
├── tests/                       # Cross-system integration tests
├── tools/                       # Utility scripts and tools
├── n8n-mcp/                     # n8n MCP server integration
└── supabase/                    # Database migrations and config
```

## Directory Naming Conventions

### Standard Patterns
- **kebab-case**: For directories and files (`my-component`, `user-service`)
- **PascalCase**: For React components (`UserProfile.tsx`, `CustomerJourney.tsx`)
- **camelCase**: For JavaScript/TypeScript functions and variables
- **snake_case**: For Python files and functions (following PEP 8)
- **UPPER_CASE**: For environment variables and constants

### File Extensions
- **`.tsx`**: React components with JSX
- **`.ts`**: TypeScript files without JSX
- **`.py`**: Python files (agent development)
- **`.md`**: Documentation files
- **`.yml/.yaml`**: Configuration files (Docker, GitHub Actions)
- **`.json`**: Data and configuration files

## Frontend Structure (Next.js App Router)

```
frontend/
├── app/                         # Next.js 15+ App Router
│   ├── (auth)/                  # Route groups
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── admin/
│   │   └── customer/
│   ├── about/                   # Static pages
│   ├── services/
│   ├── consulting/
│   ├── contact/
│   ├── api/                     # API routes
│   │   ├── health/
│   │   ├── agent/
│   │   ├── chat/
│   │   └── customer/
│   ├── globals.css              # Global styles
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── loading.tsx              # Loading UI
│   ├── error.tsx                # Error UI
│   └── not-found.tsx            # 404 page
├── components/                  # React components
│   ├── ui/                      # Shadcn/ui base components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...                  # 40+ UI components
│   ├── features/                # Feature-specific components
│   │   ├── auth/
│   │   ├── chat/
│   │   ├── dashboard/
│   │   └── consulting/
│   ├── layout/                  # Layout components
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   ├── sidebar.tsx
│   │   └── navigation.tsx
│   └── chatbot/                 # Chatbot widget
│       ├── chat-widget.tsx
│       ├── message-list.tsx
│       └── input-form.tsx
├── lib/                         # Utilities and configurations
│   ├── supabase.ts              # Supabase client
│   ├── utils.ts                 # Utility functions
│   ├── brand.ts                 # Brand configuration
│   ├── i18n-enhanced.tsx        # Internationalization
│   └── validations.ts           # Form validation schemas
├── hooks/                       # Custom React hooks
│   ├── use-auth.ts
│   ├── use-chat.ts
│   └── use-mobile.tsx
├── styles/                      # Additional styles
│   ├── globals.css
│   └── animations.css
├── public/                      # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├── tests/                       # Frontend tests
│   ├── components/
│   ├── pages/
│   └── utils/
├── package.json                 # Dependencies and scripts
├── next.config.mjs              # Next.js configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
└── playwright.config.ts         # E2E testing configuration
```

## Backend Structure (Python ADK Agent)

```
agent/                           # PRIMARY backend location
├── my_adk_agent/                # Main agent implementation
│   ├── agent.py                 # CustomerJourneyAgent (main)
│   ├── services/                # Service integrations
│   │   ├── __init__.py
│   │   ├── supabase_service.py  # Database operations
│   │   ├── mcp_service.py       # n8n workflow integration
│   │   ├── monitoring_service.py # Health monitoring
│   │   ├── cicd_service.py      # CI/CD automation
│   │   ├── auth_service.py      # Authentication
│   │   ├── livekit_service.py   # Real-time communication
│   │   └── stripe_service.py    # Payment processing
│   ├── tools/                   # ADK tools
│   │   ├── __init__.py
│   │   ├── customer_analysis.py
│   │   ├── requirements_extraction.py
│   │   ├── workflow_trigger.py
│   │   └── health_check.py
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── conversation.py
│   │   ├── workflow.py
│   │   └── deployment.py
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── validation.py
│   └── __init__.py
├── n8n_mcp_agent/               # N8nMCPAgent (specialized)
│   ├── agent.py
│   ├── tools/
│   └── __init__.py
├── specialized_agents/          # Domain-specific agents
│   ├── technical_agent.py
│   ├── sales_agent.py
│   ├── customer_support_agent.py
│   └── accountant_agent.py
├── tests/                       # Comprehensive test suite
│   ├── unit/                    # Unit tests
│   │   ├── test_services/
│   │   ├── test_tools/
│   │   └── test_models/
│   ├── integration/             # Integration tests
│   │   ├── test_supabase/
│   │   ├── test_mcp/
│   │   └── test_workflows/
│   ├── smoke/                   # Smoke tests
│   │   ├── test_health_checks.py
│   │   └── test_basic_flows.py
│   ├── fixtures/                # Test data and fixtures
│   └── conftest.py              # Pytest configuration
├── api_server.py                # FastAPI server (additional endpoints)
├── main.py                      # Entry point
├── pyproject.toml               # Python dependencies (uv)
├── requirements.txt             # Pip fallback
└── uv.lock                      # Dependency lock file
```

## Infrastructure Structure

```
infrastructure/
├── docker/                      # Container configurations
│   ├── Dockerfile.frontend      # Next.js container
│   ├── Dockerfile.backend       # Python agent container
│   ├── docker-compose.yml       # Base composition
│   ├── docker-compose.production.yml
│   ├── docker-compose.development.yml
│   └── docker-compose.staging.yml
├── nginx/                       # Web server configuration
│   ├── production.conf
│   ├── development.conf
│   └── staging.conf
├── ssl/                         # SSL certificates
│   ├── consulting.sa.crt
│   └── consulting.sa.key
├── monitoring/                  # Monitoring stack
│   ├── prometheus/
│   ├── grafana/
│   ├── alertmanager/
│   └── docker-compose.monitoring.yml
├── scripts/                     # Deployment and utility scripts
│   ├── deploy-production.sh
│   ├── deploy-development.sh
│   ├── health-check.sh
│   ├── backup-database.sh
│   └── validate-deployment.sh
├── ansible/                     # Server provisioning
│   ├── playbooks/
│   └── inventory/
└── config/                      # Environment configurations
    ├── production.env
    ├── development.env
    └── staging.env
```

## Naming Conventions by Context

### React Components
```typescript
// Component files: PascalCase
UserProfile.tsx
CustomerJourney.tsx
ChatWidget.tsx

// Component names: PascalCase
export function UserProfile() { }
export const CustomerJourney = () => { }

// Props interfaces: ComponentNameProps
interface UserProfileProps {
  userId: string;
  onUpdate: (user: User) => void;
}
```

### Python Files (ADK Agent)
```python
# File names: snake_case
supabase_service.py
customer_analysis.py
workflow_trigger.py

# Class names: PascalCase
class SupabaseService:
class CustomerAnalysisTool:
class WorkflowTrigger:

# Function names: snake_case
def analyze_customer_requirements():
def trigger_workflow():
def get_customer_data():
```

### API Routes and Endpoints
```typescript
// Next.js API routes: kebab-case directories
app/api/customer-data/route.ts
app/api/health-check/route.ts
app/api/workflow-trigger/route.ts

// Endpoint paths: kebab-case
/api/customer-data
/api/health-check
/api/workflow-trigger
```

### Database Tables and Columns
```sql
-- Table names: snake_case
customers
conversation_history
workflow_executions

-- Column names: snake_case
customer_id
created_at
workflow_status
```

## Import and Export Conventions

### Frontend Imports
```typescript
// External libraries first
import React from 'react';
import { NextRequest } from 'next/server';

// Internal imports by proximity
import { Button } from '@/components/ui/button';
import { UserService } from '@/lib/services';
import { validateUser } from '@/lib/validations';

// Type imports separately
import type { User, Customer } from '@/types';
```

### Python Imports
```python
# Standard library first
import os
import asyncio
from typing import Dict, List, Optional

# Third-party libraries
from supabase import create_client
from google.adk import Agent, tool

# Local imports
from .services.supabase_service import SupabaseService
from .models.customer import Customer
from .utils.config import get_config
```

## Configuration File Patterns

### Environment Files
```bash
# .env (production)
ENVIRONMENT=production
DATABASE_URL=postgresql://...
API_KEY=prod_key_...

# .env.development
ENVIRONMENT=development
DATABASE_URL=postgresql://...
API_KEY=dev_key_...
```

### Docker Compose Services
```yaml
# Service naming: kebab-case with environment suffix
services:
  agentic-frontend-prod:
  agentic-backend-prod:
  agentic-redis-prod:
  
  agentic-frontend-dev:
  agentic-backend-dev:
  agentic-redis-dev:
```

## Documentation Structure

```
docs/
├── api/                         # API documentation
├── deployment/                  # Deployment guides
├── development/                 # Development setup
├── architecture/                # System architecture
├── troubleshooting/             # Common issues
└── README.md                    # Main documentation
```

## Git Branch Naming

```bash
# Feature branches
feature/user-authentication
feature/workflow-automation
feature/monitoring-dashboard

# Bug fixes
fix/login-redirect-issue
fix/container-health-check

# Hotfixes
hotfix/security-vulnerability
hotfix/production-outage

# Release branches
release/v1.2.0
release/v1.3.0
```

---

**Last Updated**: January 2025  
**Enforcement**: Automated via linting and CI/CD pipeline  
**Review**: Structure conventions reviewed monthly