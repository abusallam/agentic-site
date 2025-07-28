#!/usr/bin/env python3
"""
Workspace Directory Structure Setup
Creates the new organized directory structure with proper configurations
"""

import os
import json
from pathlib import Path
from typing import Dict, List

class WorkspaceSetup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        
        # Define the new directory structure
        self.directory_structure = {
            'frontend/': {
                'description': 'Next.js application and React components',
                'subdirs': [
                    'app/',
                    'components/',
                    'lib/',
                    'hooks/',
                    'styles/',
                    'public/',
                    'tests/'
                ],
                'readme_content': self._get_frontend_readme(),
                'gitignore_content': self._get_frontend_gitignore(),
                'package_json': self._get_frontend_package_json()
            },
            'backend/': {
                'description': 'Python ADK agent system',
                'subdirs': [
                    'agent/',
                    'services/',
                    'tests/'
                ],
                'readme_content': self._get_backend_readme(),
                'gitignore_content': self._get_backend_gitignore()
            },
            'infrastructure/': {
                'description': 'Deployment, Docker, and infrastructure code',
                'subdirs': [
                    'docker/',
                    'scripts/',
                    'nginx/',
                    'ssl/',
                    'monitoring/',
                    'ansible/',
                    'cleanup/'
                ],
                'readme_content': self._get_infrastructure_readme(),
                'gitignore_content': self._get_infrastructure_gitignore()
            },
            'docs/': {
                'description': 'Documentation and guides',
                'subdirs': [
                    'deployment/',
                    'monitoring/',
                    'troubleshooting/',
                    'api/',
                    'development/'
                ],
                'readme_content': self._get_docs_readme(),
                'gitignore_content': ''
            }
        }
        
        # Root workspace configuration
        self.workspace_config = {
            'name': 'agentic-ai-platform',
            'version': '1.0.0',
            'description': 'AI consulting SaaS platform with dual-agent architecture',
            'type': 'workspace',
            'workspaces': [
                'frontend',
                'backend'
            ],
            'structure': {
                'frontend': 'Next.js application and React components',
                'backend': 'Python ADK agent system',
                'infrastructure': 'Deployment and infrastructure code',
                'docs': 'Documentation and guides',
                'tests': 'Integration and E2E tests',
                'tools': 'Development tools and utilities'
            },
            'scripts': {
                'dev': 'npm run dev --workspace=frontend',
                'build': 'npm run build --workspace=frontend',
                'test': 'npm run test --workspace=frontend && cd backend && python -m pytest',
                'lint': 'npm run lint --workspace=frontend && cd backend && python -m flake8',
                'format': 'npm run format --workspace=frontend && cd backend && python -m black .',
                'deploy': './infrastructure/scripts/deploy.sh',
                'clean': 'npm run clean --workspace=frontend && cd backend && find . -name __pycache__ -exec rm -rf {} +',
                'analyze': 'python infrastructure/cleanup/project_analyzer.py'
            },
            'devDependencies': {
                'concurrently': '^8.2.2',
                'cross-env': '^7.0.3'
            }
        }

    def create_directory_structure(self) -> Dict[str, List[str]]:
        """Create the new directory structure"""
        print("📁 Creating new directory structure...")
        
        created_dirs = {}
        
        for main_dir, config in self.directory_structure.items():
            main_path = self.project_root / main_dir
            
            # Create main directory
            main_path.mkdir(exist_ok=True)
            created_dirs[main_dir] = [str(main_path)]
            
            print(f"✅ Created: {main_dir}")
            
            # Create subdirectories
            for subdir in config['subdirs']:
                sub_path = main_path / subdir
                sub_path.mkdir(parents=True, exist_ok=True)
                created_dirs[main_dir].append(str(sub_path))
                print(f"  ✅ Created: {main_dir}{subdir}")
        
        return created_dirs

    def create_readme_files(self):
        """Create README files for each directory"""
        print("📝 Creating README files...")
        
        for main_dir, config in self.directory_structure.items():
            readme_path = self.project_root / main_dir / 'README.md'
            
            with open(readme_path, 'w') as f:
                f.write(config['readme_content'])
            
            print(f"✅ Created: {main_dir}README.md")

    def create_gitignore_files(self):
        """Create .gitignore files for each directory"""
        print("🚫 Creating .gitignore files...")
        
        for main_dir, config in self.directory_structure.items():
            if config['gitignore_content']:
                gitignore_path = self.project_root / main_dir / '.gitignore'
                
                with open(gitignore_path, 'w') as f:
                    f.write(config['gitignore_content'])
                
                print(f"✅ Created: {main_dir}.gitignore")

    def create_workspace_config(self):
        """Create workspace configuration files"""
        print("⚙️ Creating workspace configuration...")
        
        # Create workspace.json
        workspace_json_path = self.project_root / 'workspace.json'
        with open(workspace_json_path, 'w') as f:
            json.dump(self.workspace_config, f, indent=2)
        
        print(f"✅ Created: workspace.json")
        
        # Update root package.json for workspace management
        root_package_json = self._get_root_package_json()
        package_json_path = self.project_root / 'package.json'
        
        # Read existing package.json if it exists
        existing_package = {}
        if package_json_path.exists():
            with open(package_json_path, 'r') as f:
                existing_package = json.load(f)
        
        # Merge with workspace configuration
        merged_package = {**existing_package, **root_package_json}
        
        with open(package_json_path, 'w') as f:
            json.dump(merged_package, f, indent=2)
        
        print(f"✅ Updated: package.json (workspace configuration)")

    def create_frontend_package_json(self):
        """Create frontend-specific package.json"""
        frontend_package = self.directory_structure['frontend/']['package_json']
        frontend_package_path = self.project_root / 'frontend' / 'package.json'
        
        with open(frontend_package_path, 'w') as f:
            json.dump(frontend_package, f, indent=2)
        
        print(f"✅ Created: frontend/package.json")

    def _get_frontend_readme(self) -> str:
        return """# Frontend - Next.js Application

This directory contains the Next.js application and all React components for the AI consulting platform.

## Structure

- `app/` - Next.js App Router pages and layouts
- `components/` - Reusable React components
- `lib/` - Utility functions and configurations
- `hooks/` - Custom React hooks
- `styles/` - CSS and styling files
- `public/` - Static assets
- `tests/` - Frontend-specific tests

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

## Key Technologies

- Next.js 15+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React 19
- Supabase client

## Configuration Files

- `next.config.mjs` - Next.js configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `postcss.config.mjs` - PostCSS configuration
- `jest.config.js` - Jest testing configuration
- `playwright.config.ts` - Playwright E2E testing
"""

    def _get_backend_readme(self) -> str:
        return """# Backend - Python ADK Agent System

This directory contains the Python ADK agent system with dual-agent architecture for customer journey orchestration and workflow automation.

## Structure

- `agent/` - Main ADK agent implementation (preserved structure)
  - `my_adk_agent/` - CustomerJourneyAgent (main orchestrator)
  - `n8n_mcp_agent/` - N8nMCPAgent (workflow specialist)
  - `specialized_agents/` - Domain-specific agents
- `services/` - External service integrations
- `tests/` - Backend-specific tests

## Development

```bash
# Install dependencies (using uv)
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run agent
python agent/main.py

# Run tests
python -m pytest

# Lint code
python -m flake8

# Format code
python -m black .

# Start ADK web UI
adk web
```

## Key Technologies

- Google ADK (Agent Development Kit)
- Python 3.11+
- FastAPI for additional endpoints
- Google Gemini for AI capabilities
- Supabase for database operations
- n8n via MCP server integration

## Agent Architecture

- **CustomerJourneyAgent**: Main orchestration agent
- **N8nMCPAgent**: Dedicated n8n workflow automation
- **Service Layer**: Supabase, MCP, Monitoring, CI/CD services
"""

    def _get_infrastructure_readme(self) -> str:
        return """# Infrastructure - Deployment and Operations

This directory contains all deployment, Docker, and infrastructure code for the AI consulting platform.

## Structure

- `docker/` - Docker configurations and compose files
- `scripts/` - Deployment and utility scripts
- `nginx/` - Nginx reverse proxy configurations
- `ssl/` - SSL certificates and configurations
- `monitoring/` - Prometheus, Grafana, and monitoring setup
- `ansible/` - Server provisioning playbooks
- `cleanup/` - Project cleanup and analysis tools

## Key Files

- `docker/docker-compose.production.yml` - Production deployment
- `scripts/deploy.sh` - Main deployment script
- `scripts/validate-deployment.sh` - System validation
- `nginx/production.conf` - Nginx configuration
- `monitoring/docker-compose.monitoring.yml` - Monitoring stack

## Deployment

```bash
# Deploy to production
./scripts/deploy.sh

# Validate deployment
./scripts/validate-deployment.sh

# Check system status
./scripts/health-check.sh

# Setup monitoring
./scripts/setup-monitoring.sh
```

## Infrastructure Components

- **Docker**: Container orchestration
- **Nginx**: Reverse proxy with SSL termination
- **Monitoring**: Prometheus + Grafana + N8N
- **Security**: UFW Firewall + Fail2ban
- **SSL**: Cloudflare Origin certificates
"""

    def _get_docs_readme(self) -> str:
        return """# Documentation

This directory contains all project documentation, guides, and API references.

## Structure

- `deployment/` - Deployment guides and procedures
- `monitoring/` - Monitoring and observability documentation
- `troubleshooting/` - Common issues and solutions
- `api/` - API documentation and references
- `development/` - Development guides and standards

## Key Documents

- `installation.md` - Setup and installation guide
- `configuration.md` - Configuration reference
- `api-reference.md` - API endpoints documentation
- `style-guide.md` - Design system and components
- `i18n-guide.md` - Internationalization setup

## Contributing

When adding new documentation:

1. Use clear, descriptive filenames
2. Include table of contents for long documents
3. Use consistent markdown formatting
4. Add code examples where appropriate
5. Keep documentation up to date with code changes
"""

    def _get_frontend_gitignore(self) -> str:
        return """# Frontend specific ignores
.next/
out/
build/
dist/

# Testing
coverage/
.nyc_output/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# Vercel
.vercel

# Storybook
storybook-static/

# Temporary files
*.tsbuildinfo
"""

    def _get_backend_gitignore(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# ADK specific
.adk/
agent_logs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment variables
.env
"""

    def _get_infrastructure_gitignore(self) -> str:
        return """# Infrastructure specific ignores
*.log
*.pid
*.seed
*.pid.lock

# SSL certificates (keep examples)
ssl/*.key
ssl/*.crt
!ssl/*.example

# Terraform
*.tfstate
*.tfstate.*
.terraform/

# Ansible
*.retry

# Monitoring data
monitoring/data/
prometheus_data/
grafana_data/

# Backup files
backup_*/
*.backup
"""

    def _get_root_package_json(self) -> Dict:
        return {
            "name": "agentic-ai-platform",
            "version": "1.0.0",
            "description": "AI consulting SaaS platform with dual-agent architecture",
            "private": True,
            "workspaces": [
                "frontend"
            ],
            "scripts": {
                "dev": "npm run dev --workspace=frontend",
                "build": "npm run build --workspace=frontend",
                "start": "npm run start --workspace=frontend",
                "test": "npm run test --workspace=frontend",
                "lint": "npm run lint --workspace=frontend",
                "format": "npm run format --workspace=frontend",
                "type-check": "npm run type-check --workspace=frontend",
                "clean": "npm run clean --workspace=frontend",
                "deploy": "./infrastructure/scripts/deploy.sh",
                "analyze": "python infrastructure/cleanup/project_analyzer.py",
                "validate": "./infrastructure/scripts/validate-deployment.sh"
            },
            "devDependencies": {
                "concurrently": "^8.2.2",
                "cross-env": "^7.0.3"
            },
            "engines": {
                "node": ">=18.0.0",
                "npm": ">=9.0.0"
            }
        }

    def _get_frontend_package_json(self) -> Dict:
        return {
            "name": "frontend",
            "version": "1.0.0",
            "description": "Next.js frontend for AI consulting platform",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint --fix",
                "lint:check": "next lint",
                "format": "prettier --write .",
                "format:check": "prettier --check .",
                "type-check": "tsc --noEmit",
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
                "e2e": "playwright test",
                "e2e:ui": "playwright test --ui",
                "clean": "rm -rf .next out dist coverage",
                "analyze": "cross-env ANALYZE=true next build"
            },
            "dependencies": {
                "next": "^15.4.1",
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "typescript": "^5.7.3"
            },
            "devDependencies": {
                "@types/node": "^22.0.0",
                "@types/react": "^19.0.0",
                "@types/react-dom": "^19.0.0",
                "eslint": "^9.0.0",
                "eslint-config-next": "^15.4.1",
                "prettier": "^3.0.0",
                "jest": "^29.0.0",
                "@playwright/test": "^1.40.0"
            },
            "engines": {
                "node": ">=18.0.0"
            }
        }

def main():
    """Main function to set up workspace structure"""
    print("🏗️ Setting Up New Workspace Directory Structure")
    print("=" * 50)
    
    try:
        setup = WorkspaceSetup()
        
        # Create directory structure
        created_dirs = setup.create_directory_structure()
        
        # Create README files
        setup.create_readme_files()
        
        # Create .gitignore files
        setup.create_gitignore_files()
        
        # Create workspace configuration
        setup.create_workspace_config()
        
        # Create frontend package.json
        setup.create_frontend_package_json()
        
        print("\n" + "=" * 50)
        print("✅ Workspace structure created successfully!")
        
        print("\n📁 Created directories:")
        for main_dir, subdirs in created_dirs.items():
            print(f"  {main_dir}")
            for subdir in subdirs[1:]:  # Skip the main dir itself
                print(f"    {Path(subdir).name}/")
        
        print("\n📝 Created configuration files:")
        print("  - workspace.json")
        print("  - package.json (updated)")
        print("  - frontend/package.json")
        print("  - README.md files for each directory")
        print("  - .gitignore files for each directory")
        
        print("\nNext steps:")
        print("1. Review the created structure")
        print("2. Move files according to mapping plan")
        print("3. Update import paths and configurations")
        print("4. Test the new structure")
        
    except Exception as e:
        print(f"❌ Workspace setup failed: {e}")
        raise

if __name__ == "__main__":
    main()