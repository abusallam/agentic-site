# 🧪 Local Testing Guide - Agentic AI Platform

## 📋 Prerequisites

### Required Software
- **Node.js**: v18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **uv**: Python package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **npm**: Comes with Node.js

### Installation Commands
```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or with pip: pip install uv
# Or with homebrew: brew install uv

# Verify installations
node --version    # Should be v18+
npm --version     # Should be 9+
python --version  # Should be 3.11+
uv --version      # Should be 0.1+
```

## 🚀 Local Development Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
# Core Application
NODE_ENV=development
FRONTEND_PORT=3000
BACKEND_PORT=8000

# Supabase (replace with your actual values)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Services (optional for basic testing)
GEMINI_API_KEY=your_gemini_api_key

# Contact Configuration
NEXT_PUBLIC_CONTACT_EMAIL=your-email@domain.com

# Local URLs
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_ADMIN_URL=http://localhost:8000
```

### 2. Frontend Testing (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Available at: http://localhost:3000
```

**Frontend Testing Commands:**
```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build

# Start production build
npm start
```

### 3. Backend Testing (Python with uv)

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Navigate to agent directory
cd agent

# Run the agent
uv run python main.py

# Available at: http://localhost:8000 (if API server is enabled)
```

**Backend Testing Commands:**
```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run with specific Python version
uv run --python 3.11 python main.py

# Install additional dependencies
uv add package-name

# Remove dependencies
uv remove package-name
```

## 🔧 Package Management with uv

### Why uv?
- **Fast**: 10-100x faster than pip
- **Reliable**: Consistent dependency resolution
- **Modern**: Built for Python 3.11+
- **Compatible**: Works with existing pip/requirements.txt

### Common uv Commands
```bash
# Create new project
uv init my-project

# Install dependencies
uv sync                    # Install from pyproject.toml
uv add fastapi            # Add new dependency
uv add --dev pytest       # Add development dependency

# Run commands
uv run python script.py   # Run with project environment
uv run --python 3.11 app.py  # Run with specific Python version

# Environment management
uv venv                   # Create virtual environment
uv pip install package   # Install in current environment

# Lock file management
uv lock                   # Generate uv.lock file
uv sync --locked          # Install exact versions from lock
```

### Dependencies Fixed in This Project
- **psutil**: Added for system monitoring
- **google-generativeai**: Added for AI capabilities
- **fastapi**: Web framework for API endpoints
- **uvicorn**: ASGI server for FastAPI
- **supabase**: Database client
- **pydantic**: Data validation
- **python-dotenv**: Environment variable management

## 🧪 Testing Procedures

### Full Stack Testing
```bash
# Terminal 1: Start backend
cd backend/agent
uv run python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
./test-organized-structure.sh
```

### Individual Component Testing

#### Frontend Only
```bash
cd frontend
npm install
npm run dev
# Visit: http://localhost:3000
```

#### Backend Only
```bash
cd backend
uv sync
cd agent
uv run python main.py
# Check logs for successful startup
```

#### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test frontend API
curl http://localhost:3000/api/health
```

## 🐛 Troubleshooting

### Common Issues

#### Frontend Issues
```bash
# Clear cache and reinstall
rm -rf .next node_modules package-lock.json
npm install

# Fix port conflicts
npm run dev -- --port 3001

# TypeScript errors
npm run type-check
```

#### Backend Issues
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version
python --version  # Should be 3.11+

# Virtual environment issues
uv venv --python 3.11
source .venv/bin/activate
```

#### Environment Issues
```bash
# Check environment variables
cat .env

# Test Supabase connection
uv run python -c "from supabase import create_client; print('Supabase OK')"

# Test imports
uv run python -c "import my_adk_agent; print('Agent imports OK')"
```

### Error Solutions

#### "Module not found" errors
```bash
# Reinstall with uv
cd backend
uv sync

# Check Python path
uv run python -c "import sys; print(sys.path)"
```

#### "Port already in use"
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
npm run dev -- --port 3001
```

#### Supabase connection errors
- Verify your Supabase URL and keys in `.env`
- Check Supabase project status
- Ensure network connectivity

## 📊 Performance Testing

### Frontend Performance
```bash
# Build and analyze
npm run build
npm run analyze  # If configured

# Lighthouse testing
npx lighthouse http://localhost:3000
```

### Backend Performance
```bash
# Load testing with curl
for i in {1..100}; do curl http://localhost:8000/health; done

# Memory usage monitoring
uv run python -c "
import psutil
import time
while True:
    print(f'Memory: {psutil.virtual_memory().percent}%')
    time.sleep(1)
"
```

## 🚀 Production Preparation

### Frontend Production Build
```bash
cd frontend
npm run build
npm start  # Test production build locally
```

### Backend Production Setup
```bash
cd backend
uv sync --no-dev  # Install only production dependencies
cd agent
uv run python main.py  # Test production startup
```

### Environment Validation
```bash
# Check all required variables
./infrastructure/scripts/validate-deployment.sh

# Test database connections
uv run python -c "
from my_adk_agent.services.supabase_service import SupabaseService
service = SupabaseService()
print('Database connection:', 'OK' if service.health_check() else 'FAILED')
"
```

## 📚 Additional Resources

- **uv Documentation**: https://docs.astral.sh/uv/
- **Next.js Documentation**: https://nextjs.org/docs
- **Supabase Documentation**: https://supabase.com/docs
- **Project Architecture**: See `docs/MAINTENANCE_GUIDE.md`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Both frontend and backend provide detailed error logs
2. **Verify environment**: Ensure all required variables are set
3. **Test dependencies**: Run `uv sync` and `npm install`
4. **Check documentation**: Refer to service-specific docs in `docs/`
5. **Health checks**: Use built-in health endpoints to diagnose issues

---

**Last Updated**: $(date)  
**Project Status**: Production Ready  
**Package Manager**: uv (Python), npm (Node.js)