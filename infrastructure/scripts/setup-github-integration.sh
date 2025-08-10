#!/bin/bash
"""
GitHub Integration and Webhook System Setup
Configures automated development deployments with branch-based triggers
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WEBHOOK_PORT=${WEBHOOK_PORT:-9000}
WEBHOOK_SECRET=${WEBHOOK_SECRET:-$(openssl rand -hex 32)}
GITHUB_REPO=${GITHUB_REPO:-""}
DEPLOY_BRANCH=${DEPLOY_BRANCH:-"main"}
DEV_BRANCH=${DEV_BRANCH:-"development"}

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Get configuration from user
get_configuration() {
    log "Configuring GitHub integration..."
    
    # Get GitHub repository
    if [[ -z "$GITHUB_REPO" ]]; then
        read -p "Enter GitHub repository (owner/repo): " GITHUB_REPO
        if [[ -z "$GITHUB_REPO" ]]; then
            error "GitHub repository is required"
            exit 1
        fi
    fi
    
    # Get webhook secret
    if [[ -z "$WEBHOOK_SECRET" ]]; then
        WEBHOOK_SECRET=$(openssl rand -hex 32)
    fi
    
    log "Configuration:"
    log "  Repository: $GITHUB_REPO"
    log "  Webhook Port: $WEBHOOK_PORT"
    log "  Deploy Branch: $DEPLOY_BRANCH"
    log "  Development Branch: $DEV_BRANCH"
    log "  Webhook Secret: ${WEBHOOK_SECRET:0:8}..."
}

# Install required packages
install_dependencies() {
    log "Installing GitHub integration dependencies..."
    
    apt-get update
    apt-get install -y \
        git \
        curl \
        jq \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        supervisor \
        openssl
    
    # Install Python packages
    pip3 install \
        flask \
        gunicorn \
        requests \
        cryptography \
        gitpython \
        pyyaml \
        python-dotenv
    
    log "Dependencies installed successfully"
}

# Setup directories and permissions
setup_directories() {
    log "Setting up directories..."
    
    # Create required directories
    mkdir -p /opt/github-integration
    mkdir -p /var/lib/github-integration/{repos,deployments,logs}
    mkdir -p /var/log/github-integration
    mkdir -p /etc/github-integration
    
    # Set proper permissions
    chmod 755 /opt/github-integration
    chmod 755 /var/lib/github-integration
    chmod 755 /var/lib/github-integration/repos
    chmod 755 /var/lib/github-integration/deployments
    chmod 755 /var/lib/github-integration/logs
    chmod 755 /var/log/github-integration
    chmod 755 /etc/github-integration
    
    log "Directories created successfully"
}

# Create webhook server
create_webhook_server() {
    log "Creating webhook server..."
    
    cat > /opt/github-integration/webhook_server.py << 'EOF'
#!/usr/bin/env python3
"""
GitHub Webhook Server
Handles GitHub webhook events and triggers deployments
"""

import hashlib
import hmac
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
import git
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/etc/github-integration/config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/github-integration/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
GITHUB_REPO = os.getenv('GITHUB_REPO', '')
DEPLOY_BRANCH = os.getenv('DEPLOY_BRANCH', 'main')
DEV_BRANCH = os.getenv('DEV_BRANCH', 'development')
REPO_DIR = Path('/var/lib/github-integration/repos')
DEPLOYMENTS_DIR = Path('/var/lib/github-integration/deployments')

class DeploymentManager:
    """Manages deployment operations"""
    
    def __init__(self):
        self.repo_path = REPO_DIR / GITHUB_REPO.split('/')[-1]
        self.deployment_log = []
    
    def verify_webhook_signature(self, payload_body, signature_header):
        """Verify GitHub webhook signature"""
        if not WEBHOOK_SECRET:
            logger.warning("No webhook secret configured - skipping signature verification")
            return True
        
        if not signature_header:
            return False
        
        hash_object = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            msg=payload_body,
            digestmod=hashlib.sha256
        )
        expected_signature = "sha256=" + hash_object.hexdigest()
        
        return hmac.compare_digest(expected_signature, signature_header)
    
    def clone_or_update_repo(self, branch='main'):
        """Clone repository or update existing clone"""
        try:
            if self.repo_path.exists():
                # Update existing repository
                repo = git.Repo(self.repo_path)
                origin = repo.remotes.origin
                origin.fetch()
                
                # Switch to target branch
                if branch in [ref.name.split('/')[-1] for ref in repo.refs]:
                    repo.git.checkout(branch)
                    origin.pull()
                    logger.info(f"Updated repository to latest {branch}")
                else:
                    logger.error(f"Branch {branch} not found")
                    return False
            else:
                # Clone repository
                repo_url = f"https://github.com/{GITHUB_REPO}.git"
                git.Repo.clone_from(repo_url, self.repo_path, branch=branch)
                logger.info(f"Cloned repository {GITHUB_REPO} branch {branch}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error cloning/updating repository: {e}")
            return False
    
    def trigger_deployment(self, branch, commit_sha, deployment_type='development'):
        """Trigger deployment based on branch and type"""
        try:
            deployment_id = f"deploy-{int(time.time())}"
            deployment_log = {
                'deployment_id': deployment_id,
                'timestamp': datetime.now().isoformat(),
                'branch': branch,
                'commit_sha': commit_sha,
                'deployment_type': deployment_type,
                'status': 'started',
                'steps': []
            }
            
            logger.info(f"Starting {deployment_type} deployment {deployment_id}")
            
            # Step 1: Update repository
            deployment_log['steps'].append({
                'step': 'repository_update',
                'timestamp': datetime.now().isoformat(),
                'status': 'started'
            })
            
            if not self.clone_or_update_repo(branch):
                deployment_log['status'] = 'failed'
                deployment_log['steps'][-1]['status'] = 'failed'
                self.save_deployment_log(deployment_log)
                return False
            
            deployment_log['steps'][-1]['status'] = 'completed'
            
            # Step 2: Run deployment script
            deployment_log['steps'].append({
                'step': 'deployment_execution',
                'timestamp': datetime.now().isoformat(),
                'status': 'started'
            })
            
            if deployment_type == 'production':
                script_path = '/infrastructure/scripts/deploy-to-production.sh'
            else:
                script_path = '/infrastructure/scripts/deploy-development-stack.sh'
            
            # Check if deployment script exists
            if os.path.exists(script_path):
                result = subprocess.run([
                    'bash', script_path
                ], capture_output=True, text=True, cwd=self.repo_path)
                
                if result.returncode == 0:
                    deployment_log['steps'][-1]['status'] = 'completed'
                    deployment_log['steps'][-1]['output'] = result.stdout
                    deployment_log['status'] = 'completed'
                    logger.info(f"Deployment {deployment_id} completed successfully")
                else:
                    deployment_log['steps'][-1]['status'] = 'failed'
                    deployment_log['steps'][-1]['error'] = result.stderr
                    deployment_log['status'] = 'failed'
                    logger.error(f"Deployment {deployment_id} failed: {result.stderr}")
            else:
                deployment_log['steps'][-1]['status'] = 'failed'
                deployment_log['steps'][-1]['error'] = f"Deployment script not found: {script_path}"
                deployment_log['status'] = 'failed'
                logger.error(f"Deployment script not found: {script_path}")
            
            # Step 3: Run validation
            deployment_log['steps'].append({
                'step': 'deployment_validation',
                'timestamp': datetime.now().isoformat(),
                'status': 'started'
            })
            
            validation_script = '/infrastructure/scripts/validate-deployment.sh'
            if os.path.exists(validation_script):
                result = subprocess.run([
                    'bash', validation_script
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    deployment_log['steps'][-1]['status'] = 'completed'
                    deployment_log['steps'][-1]['output'] = result.stdout
                else:
                    deployment_log['steps'][-1]['status'] = 'failed'
                    deployment_log['steps'][-1]['error'] = result.stderr
                    # Don't fail entire deployment for validation issues
                    logger.warning(f"Deployment validation issues: {result.stderr}")
            else:
                deployment_log['steps'][-1]['status'] = 'skipped'
                deployment_log['steps'][-1]['note'] = 'Validation script not found'
            
            # Save deployment log
            self.save_deployment_log(deployment_log)
            
            return deployment_log['status'] == 'completed'
        
        except Exception as e:
            logger.error(f"Error during deployment: {e}")
            deployment_log['status'] = 'failed'
            deployment_log['error'] = str(e)
            self.save_deployment_log(deployment_log)
            return False
    
    def save_deployment_log(self, deployment_log):
        """Save deployment log to file"""
        try:
            log_file = DEPLOYMENTS_DIR / f"{deployment_log['deployment_id']}.json"
            with open(log_file, 'w') as f:
                json.dump(deployment_log, f, indent=2)
            
            # Also append to main deployment log
            main_log = Path('/var/log/github-integration/deployments.json')
            with open(main_log, 'a') as f:
                f.write(json.dumps(deployment_log) + '\n')
        
        except Exception as e:
            logger.error(f"Error saving deployment log: {e}")

# Initialize deployment manager
deployment_manager = DeploymentManager()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle GitHub webhook events"""
    try:
        # Verify signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not deployment_manager.verify_webhook_signature(request.data, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse payload
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        logger.info(f"Received GitHub event: {event_type}")
        
        # Handle push events
        if event_type == 'push':
            ref = payload.get('ref', '')
            branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else ''
            commit_sha = payload.get('after', '')
            
            logger.info(f"Push event on branch: {branch}, commit: {commit_sha[:8]}")
            
            # Determine deployment type based on branch
            if branch == DEPLOY_BRANCH:
                # Production deployment
                logger.info("Triggering production deployment")
                success = deployment_manager.trigger_deployment(branch, commit_sha, 'production')
                
                return jsonify({
                    'status': 'success' if success else 'failed',
                    'message': f'Production deployment {"completed" if success else "failed"}',
                    'branch': branch,
                    'commit': commit_sha[:8]
                })
            
            elif branch == DEV_BRANCH:
                # Development deployment
                logger.info("Triggering development deployment")
                success = deployment_manager.trigger_deployment(branch, commit_sha, 'development')
                
                return jsonify({
                    'status': 'success' if success else 'failed',
                    'message': f'Development deployment {"completed" if success else "failed"}',
                    'branch': branch,
                    'commit': commit_sha[:8]
                })
            
            else:
                logger.info(f"No deployment configured for branch: {branch}")
                return jsonify({
                    'status': 'ignored',
                    'message': f'No deployment configured for branch: {branch}'
                })
        
        # Handle pull request events
        elif event_type == 'pull_request':
            action = payload.get('action', '')
            pr_number = payload.get('number', '')
            
            logger.info(f"Pull request {action}: #{pr_number}")
            
            # Could trigger preview deployments here
            return jsonify({
                'status': 'received',
                'message': f'Pull request {action} received'
            })
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return jsonify({
                'status': 'ignored',
                'message': f'Event type {event_type} not handled'
            })
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/status', methods=['GET'])
def deployment_status():
    """Get deployment status"""
    try:
        # Get recent deployments
        recent_deployments = []
        for log_file in sorted(DEPLOYMENTS_DIR.glob('*.json'), reverse=True)[:10]:
            with open(log_file, 'r') as f:
                deployment = json.load(f)
                recent_deployments.append({
                    'deployment_id': deployment['deployment_id'],
                    'timestamp': deployment['timestamp'],
                    'branch': deployment['branch'],
                    'status': deployment['status'],
                    'deployment_type': deployment['deployment_type']
                })
        
        return jsonify({
            'status': 'operational',
            'recent_deployments': recent_deployments,
            'webhook_endpoint': '/webhook',
            'configured_repo': GITHUB_REPO
        })
    
    except Exception as e:
        logger.error(f"Error getting deployment status: {e}")
        return jsonify({'error': 'Could not retrieve status'}), 500

if __name__ == '__main__':
    # Ensure directories exist
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    DEPLOYMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('WEBHOOK_PORT', 9000)), debug=False)
EOF

    chmod +x /opt/github-integration/webhook_server.py
    
    log "Webhook server created"
}

# Create configuration file
create_configuration() {
    log "Creating configuration file..."
    
    cat > /etc/github-integration/config.env << EOF
# GitHub Integration Configuration
WEBHOOK_SECRET=$WEBHOOK_SECRET
GITHUB_REPO=$GITHUB_REPO
DEPLOY_BRANCH=$DEPLOY_BRANCH
DEV_BRANCH=$DEV_BRANCH
WEBHOOK_PORT=$WEBHOOK_PORT

# Deployment settings
DEPLOYMENT_TIMEOUT=1800
MAX_CONCURRENT_DEPLOYMENTS=2
ENABLE_ROLLBACK=true
ROLLBACK_TIMEOUT=300

# Notification settings
ENABLE_SLACK_NOTIFICATIONS=false
SLACK_WEBHOOK_URL=
ENABLE_EMAIL_NOTIFICATIONS=false
EMAIL_RECIPIENTS=

# Security settings
ENABLE_IP_WHITELIST=false
ALLOWED_IPS=192.30.252.0/22,185.199.108.0/22,140.82.112.0/20
ENABLE_SIGNATURE_VERIFICATION=true
EOF

    chmod 600 /etc/github-integration/config.env
    
    log "Configuration file created"
}

# Setup Nginx reverse proxy
setup_nginx_proxy() {
    log "Setting up Nginx reverse proxy..."
    
    cat > /etc/nginx/sites-available/github-webhook << EOF
server {
    listen 80;
    server_name webhook.$(hostname -d 2>/dev/null || echo "localhost");
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=webhook:10m rate=10r/m;
    
    location /webhook {
        limit_req zone=webhook burst=5 nodelay;
        
        proxy_pass http://127.0.0.1:$WEBHOOK_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for deployments
        proxy_read_timeout 1800s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:$WEBHOOK_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /status {
        proxy_pass http://127.0.0.1:$WEBHOOK_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Basic auth for status endpoint
        auth_basic "Deployment Status";
        auth_basic_user_file /etc/nginx/.htpasswd-webhook;
    }
    
    # Block access to other paths
    location / {
        return 404;
    }
}
EOF

    # Create basic auth file for status endpoint
    if command -v htpasswd >/dev/null 2>&1; then
        echo "admin:\$apr1\$$(openssl rand -base64 6)\$$(openssl passwd -apr1 -salt $(openssl rand -base64 6) admin)" > /etc/nginx/.htpasswd-webhook
    fi
    
    # Enable site
    ln -sf /etc/nginx/sites-available/github-webhook /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    nginx -t && systemctl reload nginx
    
    log "Nginx reverse proxy configured"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/github-webhook.service << 'EOF'
[Unit]
Description=GitHub Webhook Server
After=network.target nginx.service
Wants=network.target
Requires=nginx.service

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/github-integration
Environment=FLASK_APP=webhook_server.py
EnvironmentFile=/etc/github-integration/config.env
ExecStart=/usr/bin/python3 /opt/github-integration/webhook_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=github-webhook

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log /var/lib/github-integration /tmp
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable github-webhook
    
    log "Systemd service created"
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/github-integration << 'EOF'
/var/log/github-integration/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload github-webhook > /dev/null 2>&1 || true
    endscript
}

/var/log/github-integration/deployments.json {
    daily
    rotate 90
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

    log "Log rotation configured"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."
    
    # Status script
    cat > /opt/github-integration/status.sh << 'EOF'
#!/bin/bash
# GitHub Integration Status

echo "🔗 GitHub Integration Status"
echo "============================"

# Check service status
if systemctl is-active --quiet github-webhook; then
    echo "✅ GitHub Webhook Service: RUNNING"
    
    # Check if webhook is responding
    if curl -s http://localhost:$WEBHOOK_PORT/health >/dev/null 2>&1; then
        echo "✅ Webhook Endpoint: RESPONDING"
    else
        echo "❌ Webhook Endpoint: NOT RESPONDING"
    fi
else
    echo "❌ GitHub Webhook Service: STOPPED"
fi

# Check Nginx proxy
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx Proxy: RUNNING"
else
    echo "❌ Nginx Proxy: STOPPED"
fi

# Check recent deployments
RECENT_DEPLOYMENTS=$(find /var/lib/github-integration/deployments -name "*.json" -mtime -7 | wc -l)
echo "📊 Recent Deployments (7 days): $RECENT_DEPLOYMENTS"

# Check repository status
if [[ -d /var/lib/github-integration/repos ]]; then
    REPOS=$(find /var/lib/github-integration/repos -maxdepth 1 -type d | wc -l)
    echo "📁 Cloned Repositories: $((REPOS - 1))"
else
    echo "📁 Cloned Repositories: 0"
fi

# Check configuration
if [[ -f /etc/github-integration/config.env ]]; then
    echo "⚙️  Configuration: PRESENT"
    source /etc/github-integration/config.env
    echo "   Repository: $GITHUB_REPO"
    echo "   Deploy Branch: $DEPLOY_BRANCH"
    echo "   Dev Branch: $DEV_BRANCH"
    echo "   Webhook Port: $WEBHOOK_PORT"
else
    echo "⚙️  Configuration: MISSING"
fi

# System resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
echo
echo "💻 System: CPU ${CPU_USAGE}%, Memory ${MEM_USAGE}%"

# Log file sizes
LOG_SIZE=$(du -sh /var/log/github-integration 2>/dev/null | cut -f1 || echo "0")
echo "📝 Logs: $LOG_SIZE"
EOF

    # Management script
    cat > /opt/github-integration/manage.sh << 'EOF'
#!/bin/bash
# GitHub Integration Management

source /etc/github-integration/config.env 2>/dev/null || true

case "$1" in
    start)
        echo "Starting GitHub Integration..."
        systemctl start github-webhook
        systemctl start nginx
        ;;
    stop)
        echo "Stopping GitHub Integration..."
        systemctl stop github-webhook
        ;;
    restart)
        echo "Restarting GitHub Integration..."
        systemctl restart github-webhook
        systemctl reload nginx
        ;;
    status)
        systemctl status github-webhook
        ;;
    logs)
        journalctl -u github-webhook -f
        ;;
    webhook-logs)
        tail -f /var/log/github-integration/webhook.log
        ;;
    deployment-logs)
        tail -f /var/log/github-integration/deployments.json
        ;;
    deployments)
        echo "Recent deployments:"
        find /var/lib/github-integration/deployments -name "*.json" -mtime -7 | sort -r | head -10 | while read file; do
            echo "$(basename "$file" .json): $(jq -r '.status + " - " + .timestamp' "$file" 2>/dev/null || echo "unknown")"
        done
        ;;
    test-webhook)
        echo "Testing webhook endpoint..."
        curl -X POST http://localhost:${WEBHOOK_PORT:-9000}/webhook \
             -H "Content-Type: application/json" \
             -H "X-GitHub-Event: ping" \
             -d '{"zen": "Non-blocking is better than blocking."}'
        ;;
    health)
        echo "Checking webhook health..."
        curl -s http://localhost:${WEBHOOK_PORT:-9000}/health | jq '.' 2>/dev/null || echo "Health check failed"
        ;;
    deployment-status)
        echo "Getting deployment status..."
        curl -s http://localhost:${WEBHOOK_PORT:-9000}/status | jq '.' 2>/dev/null || echo "Status check failed"
        ;;
    trigger-deploy)
        if [[ -n "$2" ]]; then
            echo "Triggering manual deployment for branch: $2"
            # This would typically be done via the webhook, but we can simulate it
            python3 -c "
import sys
sys.path.append('/opt/github-integration')
from webhook_server import deployment_manager
success = deployment_manager.trigger_deployment('$2', 'manual-trigger', 'development' if '$2' == '$DEV_BRANCH' else 'production')
print('Deployment', 'successful' if success else 'failed')
"
        else
            echo "Usage: $0 trigger-deploy <branch_name>"
        fi
        ;;
    clean-logs)
        echo "Cleaning old deployment logs..."
        find /var/lib/github-integration/deployments -name "*.json" -mtime +30 -delete
        find /var/log/github-integration -name "*.log.*" -mtime +30 -delete
        echo "Old logs cleaned"
        ;;
    show-config)
        echo "GitHub Integration Configuration:"
        if [[ -f /etc/github-integration/config.env ]]; then
            grep -v "SECRET\|PASSWORD" /etc/github-integration/config.env
        else
            echo "Configuration file not found"
        fi
        ;;
    update-repo)
        echo "Updating repository clone..."
        if [[ -d /var/lib/github-integration/repos ]]; then
            cd /var/lib/github-integration/repos/*/ 2>/dev/null && git pull || echo "No repository found"
        else
            echo "No repository directory found"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|webhook-logs|deployment-logs|deployments|test-webhook|health|deployment-status|trigger-deploy|clean-logs|show-config|update-repo}"
        echo
        echo "Commands:"
        echo "  start              - Start GitHub integration service"
        echo "  stop               - Stop GitHub integration service"
        echo "  restart            - Restart GitHub integration service"
        echo "  status             - Show service status"
        echo "  logs               - View live service logs"
        echo "  webhook-logs       - View webhook logs"
        echo "  deployment-logs    - View deployment logs"
        echo "  deployments        - List recent deployments"
        echo "  test-webhook       - Test webhook endpoint"
        echo "  health             - Check webhook health"
        echo "  deployment-status  - Get deployment status"
        echo "  trigger-deploy     - Manually trigger deployment"
        echo "  clean-logs         - Clean old log files"
        echo "  show-config        - Show configuration"
        echo "  update-repo        - Update repository clone"
        exit 1
        ;;
esac
EOF

    # Make scripts executable
    chmod +x /opt/github-integration/status.sh
    chmod +x /opt/github-integration/manage.sh
    
    # Create symlink for easy access
    ln -sf /opt/github-integration/manage.sh /usr/local/bin/github-manage
    
    log "Management scripts created"
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > /opt/github-integration/health-check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check script for GitHub Integration System
"""

import json
import os
import requests
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_service_status():
    """Check if GitHub webhook service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'github-webhook'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_webhook_endpoint():
    """Check if webhook endpoint is responding"""
    try:
        webhook_port = os.getenv('WEBHOOK_PORT', '9000')
        response = requests.get(f'http://localhost:{webhook_port}/health', timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def check_nginx_proxy():
    """Check if Nginx proxy is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception:
        return False

def check_configuration():
    """Check if configuration file exists and is valid"""
    config_file = Path('/etc/github-integration/config.env')
    
    if not config_file.exists():
        return False, "Configuration file not found"
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        required_vars = ['WEBHOOK_SECRET', 'GITHUB_REPO', 'DEPLOY_BRANCH', 'DEV_BRANCH']
        missing_vars = []
        
        for var in required_vars:
            if f'{var}=' not in content:
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing configuration variables: {', '.join(missing_vars)}"
        
        return True, "Configuration is valid"
    
    except Exception as e:
        return False, f"Error reading configuration: {e}"

def check_repository_clone():
    """Check if repository is cloned and accessible"""
    repos_dir = Path('/var/lib/github-integration/repos')
    
    if not repos_dir.exists():
        return False, "Repository directory not found"
    
    repo_dirs = list(repos_dir.glob('*'))
    if not repo_dirs:
        return False, "No repositories cloned"
    
    # Check if at least one repo is a valid git repository
    for repo_dir in repo_dirs:
        if (repo_dir / '.git').exists():
            return True, f"Repository found: {repo_dir.name}"
    
    return False, "No valid git repositories found"

def check_recent_deployments():
    """Check for recent deployment activity"""
    deployments_dir = Path('/var/lib/github-integration/deployments')
    
    if not deployments_dir.exists():
        return False, "Deployments directory not found"
    
    # Check for deployments in the last 30 days
    recent_deployments = []
    for deployment_file in deployments_dir.glob('*.json'):
        mtime = datetime.fromtimestamp(deployment_file.stat().st_mtime)
        if (datetime.now() - mtime).days <= 30:
            recent_deployments.append(deployment_file)
    
    return True, f"Found {len(recent_deployments)} recent deployments"

def check_disk_space():
    """Check available disk space"""
    issues = []
    
    # Check deployments directory space
    deployments_dir = Path('/var/lib/github-integration')
    if deployments_dir.exists():
        result = subprocess.run(['df', str(deployments_dir)], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                usage = lines[1].split()[4].rstrip('%')
                if int(usage) > 90:
                    issues.append(f"GitHub integration directory disk usage high: {usage}%")
    
    return issues

def main():
    """Main health check function"""
    print("🔗 GitHub Integration System Health Check")
    print("=" * 45)
    
    all_good = True
    
    # Check service status
    if check_service_status():
        print("✅ GitHub Webhook Service: RUNNING")
    else:
        print("❌ GitHub Webhook Service: NOT RUNNING")
        all_good = False
    
    # Check webhook endpoint
    if check_webhook_endpoint():
        print("✅ Webhook Endpoint: RESPONDING")
    else:
        print("❌ Webhook Endpoint: NOT RESPONDING")
        all_good = False
    
    # Check Nginx proxy
    if check_nginx_proxy():
        print("✅ Nginx Proxy: RUNNING")
    else:
        print("❌ Nginx Proxy: NOT RUNNING")
        all_good = False
    
    # Check configuration
    config_ok, config_msg = check_configuration()
    if config_ok:
        print(f"✅ Configuration: {config_msg}")
    else:
        print(f"❌ Configuration: {config_msg}")
        all_good = False
    
    # Check repository clone
    repo_ok, repo_msg = check_repository_clone()
    if repo_ok:
        print(f"✅ Repository: {repo_msg}")
    else:
        print(f"⚠️  Repository: {repo_msg}")
    
    # Check recent deployments
    deploy_ok, deploy_msg = check_recent_deployments()
    if deploy_ok:
        print(f"✅ Recent Deployments: {deploy_msg}")
    else:
        print(f"⚠️  Recent Deployments: {deploy_msg}")
    
    # Check disk space
    disk_issues = check_disk_space()
    if not disk_issues:
        print("✅ Disk Space: OK")
    else:
        print("⚠️  Disk Space: WARNINGS")
        for issue in disk_issues:
            print(f"   - {issue}")
    
    # Check required directories
    required_dirs = [
        '/var/lib/github-integration/repos',
        '/var/lib/github-integration/deployments',
        '/var/log/github-integration'
    ]
    
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    if not missing_dirs:
        print("✅ Directory Structure: OK")
    else:
        print(f"❌ Missing Directories: {', '.join(missing_dirs)}")
        all_good = False
    
    print("=" * 45)
    if all_good:
        print("🎉 Overall Status: HEALTHY")
        sys.exit(0)
    else:
        print("🚨 Overall Status: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x /opt/github-integration/health-check.py
    
    log "Health check script created"
}

# Display setup instructions
display_instructions() {
    log "Setup completed successfully!"
    echo
    echo "🎉 GitHub Integration and Webhook System is now configured!"
    echo
    echo "📋 Next Steps:"
    echo "1. Start the service: systemctl start github-webhook"
    echo "2. Check status: github-manage status"
    echo "3. Test webhook: github-manage test-webhook"
    echo "4. Run health check: /opt/github-integration/health-check.py"
    echo
    echo "🔗 GitHub Webhook Configuration:"
    echo "   Payload URL: http://$(hostname -I | awk '{print $1}')/webhook"
    echo "   Content type: application/json"
    echo "   Secret: ${WEBHOOK_SECRET:0:8}..."
    echo "   Events: Push events, Pull requests"
    echo
    echo "🌐 Webhook Endpoints:"
    echo "   Webhook: http://localhost:$WEBHOOK_PORT/webhook"
    echo "   Health: http://localhost:$WEBHOOK_PORT/health"
    echo "   Status: http://localhost:$WEBHOOK_PORT/status"
    echo
    echo "⚙️  Configuration:"
    echo "   Repository: $GITHUB_REPO"
    echo "   Production Branch: $DEPLOY_BRANCH"
    echo "   Development Branch: $DEV_BRANCH"
    echo "   Webhook Port: $WEBHOOK_PORT"
    echo
    echo "📁 Important Files:"
    echo "   Configuration: /etc/github-integration/config.env"
    echo "   Webhook Server: /opt/github-integration/webhook_server.py"
    echo "   Nginx Config: /etc/nginx/sites-available/github-webhook"
    echo "   Service File: /etc/systemd/system/github-webhook.service"
    echo
    echo "🔧 Management Commands:"
    echo "   github-manage start|stop|restart|status"
    echo "   github-manage logs|deployments|health"
    echo "   github-manage trigger-deploy <branch>"
    echo
    echo "⚠️  Security Notes:"
    echo "   - Keep webhook secret secure"
    echo "   - Configure firewall rules for webhook port"
    echo "   - Monitor deployment logs regularly"
    echo "   - Test rollback procedures"
}

# Main setup function
main() {
    log "Starting GitHub Integration setup..."
    
    check_root
    get_configuration
    install_dependencies
    setup_directories
    create_webhook_server
    create_configuration
    setup_nginx_proxy
    create_systemd_service
    setup_log_rotation
    create_management_scripts
    create_health_check
    display_instructions
}

# Run main function
main "$@"