#!/usr/bin/env node

/**
 * Simple Service Test - Quick verification of running services
 */

const http = require('http');

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

async function testEndpoint(name, port, path) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: port,
      path: path,
      method: 'GET',
      timeout: 5000
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        log(`✅ ${name}: ${res.statusCode} - ${data.substring(0, 100)}`, colors.green);
        resolve(true);
      });
    });
    
    req.on('error', (error) => {
      log(`❌ ${name}: ${error.message}`, colors.red);
      resolve(false);
    });
    
    req.on('timeout', () => {
      log(`⏰ ${name}: Timeout`, colors.yellow);
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
          log(`✅ Chat API: ${res.statusCode} - Agent: ${response.agent || 'Unknown'}`, colors.green);
          log(`   Response: ${response.response?.substring(0, 100) || 'No response'}...`, colors.blue);
          resolve(true);
        } catch (error) {
          log(`❌ Chat API: Parse error - ${data.substring(0, 100)}`, colors.red);
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      log(`❌ Chat API: ${error.message}`, colors.red);
      resolve(false);
    });
    
    req.on('timeout', () => {
      log(`⏰ Chat API: Timeout`, colors.yellow);
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
║                    SIMPLE SERVICE TEST                      ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

  log('Testing running services...', colors.cyan);
  
  // Test basic endpoints
  await testEndpoint('Frontend Health', 3001, '/api/health');
  await testEndpoint('Frontend Home', 3001, '/');
  
  // Test chat API with Arabic message
  log('\nTesting Chat API with Arabic message...', colors.cyan);
  await testChatAPI();
  
  // Test English message
  log('\nTesting Chat API with English message...', colors.cyan);
  const englishTest = new Promise((resolve) => {
    const postData = JSON.stringify({
      message: "I need help building a chatbot"
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
          log(`✅ English Chat: ${res.statusCode} - Agent: ${response.agent || 'Unknown'}`, colors.green);
          log(`   Response: ${response.response?.substring(0, 100) || 'No response'}...`, colors.blue);
          resolve(true);
        } catch (error) {
          log(`❌ English Chat: Parse error - ${data.substring(0, 100)}`, colors.red);
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      log(`❌ English Chat: ${error.message}`, colors.red);
      resolve(false);
    });
    
    req.write(postData);
    req.end();
  });
  
  await englishTest;
  
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                       TEST COMPLETE                         ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
  
  log('Services are running at:', colors.cyan);
  log('• Frontend: http://localhost:3001', colors.green);
  log('• Chat API: http://localhost:3001/api/chat', colors.green);
  log('• Health: http://localhost:3001/api/health', colors.green);
}

if (require.main === module) {
  main().catch(console.error);
}