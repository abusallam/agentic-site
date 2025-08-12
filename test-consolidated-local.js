#!/usr/bin/env node

/**
 * Local Testing Script for Consolidated Architecture
 * Tests Frontend + n8n Platform + n8n MCP without Docker
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const config = {
  frontend: {
    port: 3001,
    dir: './frontend',
    command: 'npm',
    args: ['run', 'dev']
  },
  n8nPlatform: {
    port: 5679,
    dir: './n8n-platform',
    command: 'pnpm',
    args: ['start']
  },
  n8nMcp: {
    port: 3002,
    dir: './n8n-mcp',
    command: 'npm',
    args: ['start']
  }
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(service, message, color = colors.reset) {
  const timestamp = new Date().toISOString().substr(11, 8);
  console.log(`${color}[${timestamp}] [${service.toUpperCase()}]${colors.reset} ${message}`);
}

function checkDirectory(dir) {
  if (!fs.existsSync(dir)) {
    log('ERROR', `Directory ${dir} does not exist`, colors.red);
    return false;
  }
  return true;
}

function checkPackageJson(dir) {
  const packagePath = path.join(dir, 'package.json');
  if (!fs.existsSync(packagePath)) {
    log('ERROR', `package.json not found in ${dir}`, colors.red);
    return false;
  }
  return true;
}

async function installDependencies(service, config) {
  return new Promise((resolve, reject) => {
    log(service, 'Installing dependencies...', colors.yellow);
    
    const installCmd = config.command === 'pnpm' ? 'pnpm' : 'npm';
    const installArgs = ['install'];
    
    const install = spawn(installCmd, installArgs, {
      cwd: config.dir,
      stdio: 'pipe'
    });
    
    install.stdout.on('data', (data) => {
      log(service, data.toString().trim(), colors.cyan);
    });
    
    install.stderr.on('data', (data) => {
      log(service, data.toString().trim(), colors.yellow);
    });
    
    install.on('close', (code) => {
      if (code === 0) {
        log(service, 'Dependencies installed successfully', colors.green);
        resolve();
      } else {
        log(service, `Dependency installation failed with code ${code}`, colors.red);
        reject(new Error(`Installation failed for ${service}`));
      }
    });
  });
}

async function startService(service, config) {
  return new Promise((resolve, reject) => {
    log(service, `Starting on port ${config.port}...`, colors.green);
    
    const process = spawn(config.command, config.args, {
      cwd: config.dir,
      stdio: 'pipe',
      env: {
        ...process.env,
        PORT: config.port,
        NODE_ENV: 'development'
      }
    });
    
    process.stdout.on('data', (data) => {
      const output = data.toString().trim();
      log(service, output, colors.blue);
      
      // Check for startup success indicators
      if (output.includes('ready') || 
          output.includes('listening') || 
          output.includes('started') ||
          output.includes(`localhost:${config.port}`)) {
        log(service, `✅ Service started successfully on port ${config.port}`, colors.green);
        resolve(process);
      }
    });
    
    process.stderr.on('data', (data) => {
      const error = data.toString().trim();
      log(service, error, colors.yellow);
    });
    
    process.on('close', (code) => {
      log(service, `Process exited with code ${code}`, colors.red);
    });
    
    process.on('error', (error) => {
      log(service, `Error: ${error.message}`, colors.red);
      reject(error);
    });
    
    // Timeout after 30 seconds
    setTimeout(() => {
      log(service, 'Service started (timeout reached)', colors.yellow);
      resolve(process);
    }, 30000);
  });
}

async function healthCheck(service, port) {
  const http = require('http');
  
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: port,
      path: service === 'frontend' ? '/api/health' : 
            service === 'n8nPlatform' ? '/healthz' : '/health',
      method: 'GET',
      timeout: 5000
    };
    
    const req = http.request(options, (res) => {
      log(service, `Health check: ${res.statusCode}`, 
          res.statusCode === 200 ? colors.green : colors.yellow);
      resolve(res.statusCode === 200);
    });
    
    req.on('error', (error) => {
      log(service, `Health check failed: ${error.message}`, colors.red);
      resolve(false);
    });
    
    req.on('timeout', () => {
      log(service, 'Health check timeout', colors.yellow);
      req.destroy();
      resolve(false);
    });
    
    req.end();
  });
}

async function main() {
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                 CONSOLIDATED LOCAL TESTING                  ║
║              Frontend + n8n Platform + n8n MCP              ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

  const processes = [];
  
  try {
    // 1. Check directories and dependencies
    log('SETUP', 'Checking project structure...', colors.cyan);
    
    for (const [service, serviceConfig] of Object.entries(config)) {
      if (!checkDirectory(serviceConfig.dir)) {
        throw new Error(`Missing directory: ${serviceConfig.dir}`);
      }
      
      if (!checkPackageJson(serviceConfig.dir)) {
        throw new Error(`Missing package.json in: ${serviceConfig.dir}`);
      }
    }
    
    // 2. Install dependencies (if needed)
    log('SETUP', 'Installing dependencies...', colors.cyan);
    
    for (const [service, serviceConfig] of Object.entries(config)) {
      const nodeModulesPath = path.join(serviceConfig.dir, 'node_modules');
      if (!fs.existsSync(nodeModulesPath)) {
        await installDependencies(service, serviceConfig);
      } else {
        log(service, 'Dependencies already installed', colors.green);
      }
    }
    
    // 3. Start services in order
    log('STARTUP', 'Starting services...', colors.cyan);
    
    // Start n8n Platform first (other services depend on it)
    if (checkDirectory(config.n8nPlatform.dir)) {
      const n8nProcess = await startService('n8nPlatform', config.n8nPlatform);
      processes.push({ name: 'n8nPlatform', process: n8nProcess });
      
      // Wait a bit for n8n to fully start
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
    
    // Start n8n MCP (depends on n8n Platform)
    if (checkDirectory(config.n8nMcp.dir)) {
      const mcpProcess = await startService('n8nMcp', config.n8nMcp);
      processes.push({ name: 'n8nMcp', process: mcpProcess });
      
      // Wait a bit for MCP to connect to n8n
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    
    // Start Frontend last
    if (checkDirectory(config.frontend.dir)) {
      const frontendProcess = await startService('frontend', config.frontend);
      processes.push({ name: 'frontend', process: frontendProcess });
    }
    
    // 4. Health checks
    log('HEALTH', 'Performing health checks...', colors.cyan);
    
    await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for services to be ready
    
    const healthResults = {};
    for (const [service, serviceConfig] of Object.entries(config)) {
      if (processes.find(p => p.name === service)) {
        healthResults[service] = await healthCheck(service, serviceConfig.port);
      }
    }
    
    // 5. Summary
    console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                        SERVICE STATUS                       ║
╚══════════════════════════════════════════════════════════════╝${colors.reset}`);
    
    for (const [service, serviceConfig] of Object.entries(config)) {
      const status = healthResults[service] ? '✅ HEALTHY' : '❌ UNHEALTHY';
      const color = healthResults[service] ? colors.green : colors.red;
      console.log(`${color}${service.padEnd(15)} | Port ${serviceConfig.port.toString().padEnd(4)} | ${status}${colors.reset}`);
    }
    
    console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                         TEST URLS                           ║
╚══════════════════════════════════════════════════════════════╝${colors.reset}`);
    
    console.log(`${colors.green}Frontend:     http://localhost:3001${colors.reset}`);
    console.log(`${colors.green}n8n Platform: http://localhost:5679${colors.reset}`);
    console.log(`${colors.green}n8n MCP:      http://localhost:3002${colors.reset}`);
    
    console.log(`${colors.yellow}
Press Ctrl+C to stop all services...${colors.reset}`);
    
    // Keep the script running
    process.stdin.resume();
    
  } catch (error) {
    log('ERROR', error.message, colors.red);
    process.exit(1);
  }
  
  // Cleanup on exit
  process.on('SIGINT', () => {
    console.log(`${colors.yellow}\nShutting down services...${colors.reset}`);
    
    processes.forEach(({ name, process }) => {
      log(name, 'Stopping...', colors.yellow);
      process.kill('SIGTERM');
    });
    
    setTimeout(() => {
      console.log(`${colors.green}All services stopped.${colors.reset}`);
      process.exit(0);
    }, 2000);
  });
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, config };