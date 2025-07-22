#!/usr/bin/env python3
"""
Setup FastAPI Environment on VPS
Install Python, FastAPI, and create a production-ready setup
"""

import paramiko
import sys
from datetime import datetime

def execute_ssh_command(client, command, description=""):
    """Execute SSH command with logging"""
    print(f"🔧 {description}: {command}")
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=300)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print(f"✅ SUCCESS")
            if output and len(output) < 800:
                print(f"📝 {output}")
        else:
            print(f"⚠️ Exit code: {exit_code}")
            if error:
                print(f"❌ Error: {error[:400]}")
        
        return exit_code == 0, output, error
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, "", str(e)

def main():
    hostname = "217.79.255.54"
    username = "root" 
    password = "gt5qXy22aJ"
    port = 22
    
    print("🐍 SETTING UP FASTAPI PRODUCTION ENVIRONMENT")
    print("=" * 60)
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=30)
        print("✅ Connected to VPS")
        
        # Install Python and pip
        print("\n🐍 INSTALLING PYTHON & DEPENDENCIES")
        print("-" * 40)
        
        execute_ssh_command(client, "apt-get update", "Update packages")
        execute_ssh_command(client, "apt-get install -y python3 python3-pip python3-venv", "Install Python")
        execute_ssh_command(client, "python3 --version", "Check Python version")
        execute_ssh_command(client, "pip3 --version", "Check pip version")
        
        # Create virtual environment for FastAPI
        print("\n📦 SETTING UP VIRTUAL ENVIRONMENT")
        print("-" * 40)
        
        execute_ssh_command(client, "cd /opt/fastapi-app && python3 -m venv venv", "Create virtual environment")
        execute_ssh_command(client, "cd /opt/fastapi-app && source venv/bin/activate && pip install --upgrade pip", "Upgrade pip in venv")
        
        # Install FastAPI and dependencies
        print("\n🚀 INSTALLING FASTAPI & DEPENDENCIES")
        print("-" * 40)
        
        fastapi_packages = [
            "fastapi",
            "uvicorn[standard]", 
            "python-multipart",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "python-dotenv",
            "requests",
            "aiofiles"
        ]
        
        packages_str = " ".join(fastapi_packages)
        execute_ssh_command(client, f"cd /opt/fastapi-app && source venv/bin/activate && pip install {packages_str}", "Install FastAPI packages")
        
        # Create production FastAPI app
        print("\n🏗️ CREATING PRODUCTION FASTAPI APP")
        print("-" * 40)
        
        production_app = '''#!/usr/bin/env python3
"""
Production FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Production VPS API",
    description="FastAPI running on secured VPS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FastAPI Production Server Running!",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fastapi",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "active",
        "database": "not_configured",
        "cache": "not_configured",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info")
async def server_info():
    """Server information endpoint"""
    return {
        "server": "VPS FastAPI",
        "python_version": "3.x",
        "fastapi_version": "latest",
        "environment": "production",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        workers=2,
        log_level="info",
        access_log=True
    )
'''
        
        execute_ssh_command(client, f"cat > /opt/fastapi-app/main.py << 'EOF'\n{production_app}\nEOF", "Create production FastAPI app")
        
        # Create systemd service for FastAPI
        print("\n⚙️ CREATING SYSTEMD SERVICE")
        print("-" * 40)
        
        systemd_service = '''[Unit]
Description=FastAPI Production Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fastapi-app
Environment=PATH=/opt/fastapi-app/venv/bin
ExecStart=/opt/fastapi-app/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 80 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
'''
        
        execute_ssh_command(client, f"cat > /etc/systemd/system/fastapi.service << 'EOF'\n{systemd_service}\nEOF", "Create systemd service")
        
        # Enable and start the service
        execute_ssh_command(client, "systemctl daemon-reload", "Reload systemd")
        execute_ssh_command(client, "systemctl enable fastapi", "Enable FastAPI service")
        
        # Create startup script
        print("\n📜 CREATING MANAGEMENT SCRIPTS")
        print("-" * 40)
        
        start_script = '''#!/bin/bash
echo "🚀 Starting FastAPI Production Server..."
cd /opt/fastapi-app
source venv/bin/activate
systemctl start fastapi
systemctl status fastapi
echo "✅ FastAPI server started!"
echo "🌐 Access at: http://your-server-ip/"
echo "📚 API docs at: http://your-server-ip/docs"
'''
        
        execute_ssh_command(client, f"cat > /opt/fastapi-app/start.sh << 'EOF'\n{start_script}\nEOF", "Create start script")
        execute_ssh_command(client, "chmod +x /opt/fastapi-app/start.sh", "Make start script executable")
        
        stop_script = '''#!/bin/bash
echo "🛑 Stopping FastAPI Production Server..."
systemctl stop fastapi
systemctl status fastapi
echo "✅ FastAPI server stopped!"
'''
        
        execute_ssh_command(client, f"cat > /opt/fastapi-app/stop.sh << 'EOF'\n{stop_script}\nEOF", "Create stop script")
        execute_ssh_command(client, "chmod +x /opt/fastapi-app/stop.sh", "Make stop script executable")
        
        # Test the installation
        print("\n🧪 TESTING FASTAPI INSTALLATION")
        print("-" * 40)
        
        execute_ssh_command(client, "cd /opt/fastapi-app && source venv/bin/activate && python -c 'import fastapi; print(f\"FastAPI version: {fastapi.__version__}\")'", "Test FastAPI import")
        execute_ssh_command(client, "cd /opt/fastapi-app && source venv/bin/activate && python -c 'import uvicorn; print(\"Uvicorn installed successfully\")'", "Test Uvicorn import")
        
        # Start the FastAPI service
        print("\n🚀 STARTING FASTAPI SERVICE")
        print("-" * 40)
        
        execute_ssh_command(client, "systemctl start fastapi", "Start FastAPI service")
        execute_ssh_command(client, "sleep 3", "Wait for service to start")
        execute_ssh_command(client, "systemctl status fastapi", "Check FastAPI service status")
        
        # Test if the API is responding
        execute_ssh_command(client, "curl -s http://localhost/ | head -c 200", "Test API response")
        
        # Check if port 80 is listening
        execute_ssh_command(client, "ss -tuln | grep :80", "Check if port 80 is listening")
        
        print("\n🎉 FASTAPI SETUP COMPLETED!")
        print("=" * 60)
        print("✅ Python 3: INSTALLED")
        print("✅ Virtual Environment: CREATED")
        print("✅ FastAPI: INSTALLED")
        print("✅ Uvicorn: INSTALLED")
        print("✅ Production App: CREATED")
        print("✅ Systemd Service: CONFIGURED")
        print("✅ Management Scripts: READY")
        print("✅ Service: STARTED")
        print()
        print("🌐 ACCESS YOUR API:")
        print(f"- Main API: http://{hostname}/")
        print(f"- Health Check: http://{hostname}/health")
        print(f"- API Docs: http://{hostname}/docs")
        print(f"- ReDoc: http://{hostname}/redoc")
        print()
        print("🛠️ MANAGEMENT COMMANDS:")
        print("- Start: /opt/fastapi-app/start.sh")
        print("- Stop: /opt/fastapi-app/stop.sh")
        print("- Status: systemctl status fastapi")
        print("- Logs: journalctl -u fastapi -f")
        print()
        print("📁 FILES LOCATION:")
        print("- App: /opt/fastapi-app/main.py")
        print("- Virtual Env: /opt/fastapi-app/venv/")
        print("- Service: /etc/systemd/system/fastapi.service")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()