#!/usr/bin/env node

/**
 * Test Available Services - Test what we can run with current setup
 * Focus on Frontend + n8n MCP (skip n8n platform due to version requirements)
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

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

// Configuration for services we can actually run
const config = {
  frontend: {
    port: 3001,
    dir: './frontend',
    command: 'npm',
    args: ['run', 'dev'],
    healthPath: '/api/health'
  },
  n8nMcp: {
    port: 3002,
    dir: './n8n-mcp',
    command: 'npm',
    args: ['start'],
    healthPath: '/health'
  },
  backend: {
    port: 8001,
    dir: './agent',
    command: 'python',
    args: ['-m', 'my_adk_agent.test_multi_agent_system'],
    healthPath: '/health'
  }
};

async function startService(service, config) {
  return new Promise((resolve, reject) => {
    log(service, `Starting on port ${config.port}...`, colors.green);
    
    const childProcess = spawn(config.command, config.args, {
      cwd: config.dir,
      stdio: 'pipe',
      env: {
        ...process.env,
        PORT: config.port,
        NODE_ENV: 'development',
        // Mock n8n URL since we can't run the full platform
        N8N_URL: 'http://localhost:5678',
        N8N_API_KEY: 'mock_api_key_for_testing',
        MCP_SERVER_URL: 'http://localhost:3002'
      }
    });
    
    let hasStarted = false;
    
    childProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      log(service, output, colors.blue);
      
      // Check for startup success indicators
      if (!hasStarted && (
          output.includes('ready') || 
          output.includes('listening') || 
          output.includes('started') ||
          output.includes(`localhost:${config.port}`) ||
          output.includes(`port ${config.port}`) ||
          output.includes('Local:') ||
          output.includes('Server running')
      )) {
        hasStarted = true;
        log(service, `✅ Service started successfully on port ${config.port}`, colors.green);
        resolve(childProcess);
      }
    });
    
    childProcess.stderr.on('data', (data) => {
      const error = data.toString().trim();
      log(service, error, colors.yellow);
      
      // Some services log startup info to stderr
      if (!hasStarted && (
          error.includes('ready') || 
          error.includes('listening') || 
          error.includes('started') ||
          error.includes(`localhost:${config.port}`) ||
          error.includes(`port ${config.port}`)
      )) {
        hasStarted = true;
        log(service, `✅ Service started successfully on port ${config.port}`, colors.green);
        resolve(childProcess);
      }
    });
    
    childProcess.on('close', (code) => {
      log(service, `Process exited with code ${code}`, colors.red);
    });
    
    childProcess.on('error', (error) => {
      log(service, `Error: ${error.message}`, colors.red);
      reject(error);
    });
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (!hasStarted) {
        log(service, 'Service started (timeout reached)', colors.yellow);
        resolve(childProcess);
      }
    }, 30000);
  });
}

async function healthCheck(service, port, path) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: port,
      path: path,
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

async function testChatAPI() {
  return new Promise((resolve) => {
    const postData = JSON.stringify({
      message: "مرحباً، أريد معرفة خدماتكم"
    });
    
    const options = {
      hostname: 'localhost',
      port: 3001,
      path: '/api/chat',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      },
      timeout: 10000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          log('CHAT-API', `Response: ${JSON.stringify(response, null, 2)}`, colors.green);
          resolve(true);
        } catch (error) {
          log('CHAT-API', `Parse error: ${error.message}`, colors.red);
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      log('CHAT-API', `Request failed: ${error.message}`, colors.red);
      resolve(false);
    });
    
    req.on('timeout', () => {
      log('CHAT-API', 'Request timeout', colors.yellow);
      req.destroy();
      resolve(false);
    });
    
    req.write(postData);
    req.end();
  });
}

async function main() {
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                 AVAILABLE SERVICES TESTING                  ║
║          Frontend + n8n MCP + Backend (Mock n8n)            ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

  const processes = [];
  
  try {
    // Check what we can run
    log('SETUP', 'Checking available services...', colors.cyan);
    
    const availableServices = {};
    
    // Check frontend
    if (fs.existsSync('./frontend/package.json') && fs.existsSync('./frontend/node_modules')) {
      availableServices.frontend = config.frontend;
      log('SETUP', '✅ Frontend ready', colors.green);
    } else {
      log('SETUP', '❌ Frontend not ready', colors.red);
    }
    
    // Check n8n MCP
    if (fs.existsSync('./n8n-mcp/package.json') && fs.existsSync('./n8n-mcp/node_modules')) {
      availableServices.n8nMcp = config.n8nMcp;
      log('SETUP', '✅ n8n MCP ready', colors.green);
    } else {
      log('SETUP', '❌ n8n MCP not ready', colors.red);
    }
    
    // Check backend
    if (fs.existsSync('./agent/my_adk_agent')) {
      availableServices.backend = config.backend;
      log('SETUP', '✅ Backend agent ready', colors.green);
    } else {
      log('SETUP', '❌ Backend agent not ready', colors.red);
    }
    
    if (Object.keys(availableServices).length === 0) {
      throw new Error('No services available for testing');
    }
    
    // Start available services
    log('STARTUP', 'Starting available services...', colors.cyan);
    
    // Start n8n MCP first (if available)
    if (availableServices.n8nMcp) {
      try {
        const mcpProcess = await startService('n8nMcp', availableServices.n8nMcp);
        processes.push({ name: 'n8nMcp', process: mcpProcess });
        await new Promise(resolve => setTimeout(resolve, 3000));
      } catch (error) {
        log('n8nMcp', `Failed to start: ${error.message}`, colors.red);
      }
    }
    
    // Start frontend (if available)
    if (availableServices.frontend) {
      try {
        const frontendProcess = await startService('frontend', availableServices.frontend);
        processes.push({ name: 'frontend', process: frontendProcess });
        await new Promise(resolve => setTimeout(resolve, 5000));
      } catch (error) {
        log('frontend', `Failed to start: ${error.message}`, colors.red);
      }
    }
    
    // Health checks
    log('HEALTH', 'Performing health checks...', colors.cyan);
    
    const healthResults = {};
    for (const [service, serviceConfig] of Object.entries(availableServices)) {
      if (processes.find(p => p.name === service)) {
        healthResults[service] = await healthCheck(service, serviceConfig.port, serviceConfig.healthPath);
      }
    }
    
    // Test chat API if frontend is running
    if (healthResults.frontend) {
      log('TESTING', 'Testing chat API...', colors.cyan);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for frontend to be fully ready
      const chatWorking = await testChatAPI();
      healthResults.chatAPI = chatWorking;
    }
    
    // Summary
    console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                        SERVICE STATUS                       ║
╚══════════════════════════════════════════════════════════════╝${colors.reset}`);
    
    for (const [service, serviceConfig] of Object.entries(availableServices)) {
      const status = healthResults[service] ? '✅ HEALTHY' : '❌ UNHEALTHY';
      const color = healthResults[service] ? colors.green : colors.red;
      console.log(`${color}${service.padEnd(15)} | Port ${serviceConfig.port.toString().padEnd(4)} | ${status}${colors.reset}`);
    }
    
    if (healthResults.chatAPI !== undefined) {
      const status = healthResults.chatAPI ? '✅ WORKING' : '❌ FAILED';
      const color = healthResults.chatAPI ? colors.green : colors.red;
      console.log(`${color}Chat API        | Test      | ${status}${colors.reset}`);
    }
    
    console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                         TEST URLS                           ║
╚══════════════════════════════════════════════════════════════╝${colors.reset}`);
    
    if (availableServices.frontend) {
      console.log(`${colors.green}Frontend:     http://localhost:3001${colors.reset}`);
      console.log(`${colors.green}Chat API:     http://localhost:3001/api/chat${colors.reset}`);
    }
    
    if (availableServices.n8nMcp) {
      console.log(`${colors.green}n8n MCP:      http://localhost:3002${colors.reset}`);
    }
    
    console.log(`${colors.yellow}
Note: n8n Platform skipped (requires Node.js >=22.16, pnpm >=10.2.1)
Current: Node.js v20.19.4, pnpm 9.15.0

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