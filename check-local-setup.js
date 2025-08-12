#!/usr/bin/env node

/**
 * Check Local Setup - Verify what we have available for testing
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function checkCommand(command) {
  try {
    execSync(`which ${command}`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function checkDirectory(dir) {
  return fs.existsSync(dir);
}

function checkPackageJson(dir) {
  const packagePath = path.join(dir, 'package.json');
  if (!fs.existsSync(packagePath)) return null;
  
  try {
    const content = fs.readFileSync(packagePath, 'utf8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                    LOCAL SETUP CHECKER                      ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

// Check system requirements
log('\n📋 SYSTEM REQUIREMENTS:', colors.cyan);

const requirements = [
  { name: 'Node.js', command: 'node', check: () => checkCommand('node') },
  { name: 'npm', command: 'npm', check: () => checkCommand('npm') },
  { name: 'pnpm', command: 'pnpm', check: () => checkCommand('pnpm') }
];

requirements.forEach(req => {
  const available = req.check();
  const status = available ? '✅' : '❌';
  const color = available ? colors.green : colors.red;
  log(`${status} ${req.name.padEnd(10)} ${available ? 'Available' : 'Missing'}`, color);
  
  if (available && req.command) {
    try {
      const version = execSync(`${req.command} --version`, { encoding: 'utf8' }).trim();
      log(`   Version: ${version}`, colors.blue);
    } catch {}
  }
});

// Check project directories
log('\n📁 PROJECT STRUCTURE:', colors.cyan);

const directories = [
  { name: 'Frontend', path: './frontend' },
  { name: 'n8n Platform', path: './n8n-platform' },
  { name: 'n8n MCP', path: './n8n-mcp' },
  { name: 'Backend Agent', path: './agent' }
];

directories.forEach(dir => {
  const exists = checkDirectory(dir.path);
  const status = exists ? '✅' : '❌';
  const color = exists ? colors.green : colors.red;
  log(`${status} ${dir.name.padEnd(15)} ${dir.path}`, color);
  
  if (exists) {
    const pkg = checkPackageJson(dir.path);
    if (pkg) {
      log(`   Package: ${pkg.name} v${pkg.version}`, colors.blue);
      
      // Check if node_modules exists
      const nodeModules = path.join(dir.path, 'node_modules');
      const hasNodeModules = fs.existsSync(nodeModules);
      const depStatus = hasNodeModules ? '✅ Installed' : '❌ Missing';
      const depColor = hasNodeModules ? colors.green : colors.yellow;
      log(`   Dependencies: ${depStatus}`, depColor);
    }
  }
});

// Check environment files
log('\n🔧 ENVIRONMENT CONFIGURATION:', colors.cyan);

const envFiles = [
  '.env.development',
  '.env',
  '.env.example'
];

envFiles.forEach(file => {
  const exists = fs.existsSync(file);
  const status = exists ? '✅' : '❌';
  const color = exists ? colors.green : colors.red;
  log(`${status} ${file}`, color);
});

// Check ports availability
log('\n🌐 PORT AVAILABILITY:', colors.cyan);

const ports = [
  { name: 'Frontend', port: 3001 },
  { name: 'n8n Platform', port: 5679 },
  { name: 'n8n MCP', port: 3002 },
  { name: 'Backend', port: 8001 }
];

const net = require('net');

async function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    server.on('error', () => resolve(false));
  });
}

async function checkAllPorts() {
  for (const portInfo of ports) {
    const available = await checkPort(portInfo.port);
    const status = available ? '✅ Available' : '❌ In Use';
    const color = available ? colors.green : colors.yellow;
    log(`${status} Port ${portInfo.port} (${portInfo.name})`, color);
  }
}

// Recommendations
function showRecommendations() {
  log('\n💡 RECOMMENDATIONS:', colors.cyan);
  
  const recommendations = [];
  
  if (!checkCommand('pnpm')) {
    recommendations.push('Install pnpm: npm install -g pnpm');
  }
  
  if (!checkDirectory('./n8n-platform/node_modules')) {
    recommendations.push('Install n8n platform dependencies: cd n8n-platform && pnpm install');
  }
  
  if (!checkDirectory('./n8n-mcp/node_modules')) {
    recommendations.push('Install n8n MCP dependencies: cd n8n-mcp && npm install');
  }
  
  if (!checkDirectory('./frontend/node_modules')) {
    recommendations.push('Install frontend dependencies: cd frontend && npm install');
  }
  
  if (recommendations.length === 0) {
    log('✅ All requirements met! Ready to test locally.', colors.green);
    log('\n🚀 To start testing:', colors.cyan);
    log('   node test-consolidated-local.js', colors.green);
  } else {
    recommendations.forEach((rec, index) => {
      log(`${index + 1}. ${rec}`, colors.yellow);
    });
  }
}

// Run checks
checkAllPorts().then(() => {
  showRecommendations();
  
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                    SETUP CHECK COMPLETE                     ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
});