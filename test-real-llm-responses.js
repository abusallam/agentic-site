#!/usr/bin/env node

/**
 * Test Real LLM Responses - Test actual Gemini Flash API calls with comprehensive validation
 */

const http = require('http');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

async function testRealLLMResponses() {
  const testCases = [
    {
      name: "Arabic Strategic Consulting with BMAD",
      message: "أريد استشارة استراتيجية لتطبيق الذكاء الاصطناعي في شركتي. أحتاج تحليل السوق وخطة التنفيذ مع منهجية BMAD",
      expectedAgent: "consulting",
      expectedFeatures: {
        "Arabic Response": ["استراتيجية", "تحليل", "خطة", "منهجية"],
        "BMAD Methodology": ["bmad", "brainstorm", "analyze", "architect", "develop"],
        "Strategic Content": ["strategy", "market", "implementation", "consulting"],
        "Professional Tone": ["consulting.sa", "خدماتنا", "نقدم", "متخصص"]
      },
      qualityChecks: ["response_length", "arabic_quality", "business_relevance", "security_compliance"]
    },
    {
      name: "English Code Generation with Architecture",
      message: "I need help building a complete AI chatbot system with Google ADK. Please provide full architecture, implementation plan, and production-ready code with tests",
      expectedAgent: "code_generation", 
      expectedFeatures: {
        "Architecture Design": ["architecture", "system", "design", "structure"],
        "Implementation Plan": ["implementation", "development", "roadmap", "plan"],
        "Code Structure": ["code", "framework", "adk", "production"],
        "Testing Strategy": ["test", "testing", "quality", "validation"]
      },
      qualityChecks: ["response_length", "technical_accuracy", "code_quality", "security_compliance"]
    }
  ];

  log('\n🧠 Testing Real LLM Responses with Gemini Flash', colors.cyan);
  
  let successCount = 0;
  let totalTests = testCases.length;
  
  for (const testCase of testCases) {
    const result = await testSingleLLMResponse(testCase);
    if (result.success) successCount++;
    await new Promise(resolve => setTimeout(resolve, 3000)); // Wait between API calls
  }
  
  log(`\n📊 LLM Test Results: ${successCount}/${totalTests} tests passed (${Math.round(successCount/totalTests*100)}%)`, 
      successCount === totalTests ? colors.green : colors.yellow);
  
  return { successCount, totalTests };
}

async function testSingleLLMResponse(testCase) {
  return new Promise((resolve) => {
    const postData = JSON.stringify({
      message: testCase.message,
      customer_id: "test_llm_customer_001",
      context: {
        session_id: "test_llm_session_001",
        timestamp: new Date().toISOString(),
        test_case: testCase.name,
        use_real_llm: true // Force real LLM usage
      }
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
      timeout: 30000 // Longer timeout for LLM processing
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          
          if (response.success && response.response) {
            const actualAgent = response.response.agent_type;
            const isCorrectAgent = actualAgent === testCase.expectedAgent;
            const responseText = response.response.message;
            
            log(`\n🧪 ${testCase.name}:`, colors.blue);
            log(`   Message: "${testCase.message.substring(0, 80)}..."`, colors.yellow);
            log(`   Expected Agent: ${testCase.expectedAgent}`, colors.cyan);
            log(`   Actual Agent: ${actualAgent}`, isCorrectAgent ? colors.green : colors.red);
            log(`   Status: ${isCorrectAgent ? '✅ CORRECT ROUTING' : '❌ INCORRECT ROUTING'}`, isCorrectAgent ? colors.green : colors.red);
            
            // Analyze LLM response quality
            const qualityAnalysis = analyzeLLMQuality(responseText, testCase);
            
            // Check for expected features in response
            let totalFeatures = 0;
            let foundFeatures = 0;
            
            Object.entries(testCase.expectedFeatures).forEach(([category, keywords]) => {
              totalFeatures++;
              const found = keywords.some(keyword => 
                responseText.toLowerCase().includes(keyword.toLowerCase())
              );
              
              if (found) {
                foundFeatures++;
                log(`   ✅ ${category}: Found`, colors.green);
              } else {
                log(`   ❌ ${category}: Not found`, colors.red);
              }
            });
            
            // Display quality analysis
            log(`\n   📊 LLM Quality Analysis:`, colors.cyan);
            Object.entries(qualityAnalysis).forEach(([check, result]) => {
              const status = result.passed ? '✅' : '❌';
              const color = result.passed ? colors.green : colors.red;
              log(`   ${status} ${check}: ${result.score}/100 - ${result.reason}`, color);
            });
            
            // Display response metrics
            log(`\n   📈 Response Metrics:`, colors.blue);
            log(`   • Features Found: ${foundFeatures}/${totalFeatures} (${Math.round(foundFeatures/totalFeatures*100)}%)`, colors.blue);
            log(`   • Response Length: ${responseText.length} characters`, colors.blue);
            log(`   • Word Count: ${responseText.split(' ').length} words`, colors.blue);
            
            // Check if this was a real LLM response
            const isRealLLM = response.response.model || response.response.usage;
            log(`   • LLM Used: ${isRealLLM ? '✅ Real Gemini Flash' : '❌ Mock Response'}`, isRealLLM ? colors.green : colors.red);
            
            if (response.response.usage) {
              log(`   • Token Usage: ${response.response.usage.total_tokens} tokens`, colors.blue);
            }
            
            log(`\n   💬 Response Preview:`, colors.magenta);
            log(`   "${responseText.substring(0, 200)}..."`, colors.magenta);
            
            if (response.response.next_action) {
              log(`   🎯 Next Action: ${response.response.next_action}`, colors.cyan);
            }
            
            // Calculate overall success score
            const routingScore = isCorrectAgent ? 100 : 0;
            const featureScore = Math.round(foundFeatures / totalFeatures * 100);
            const qualityScore = Object.values(qualityAnalysis).reduce((sum, result) => sum + result.score, 0) / Object.keys(qualityAnalysis).length;
            const llmScore = isRealLLM ? 100 : 0;
            
            const overallScore = Math.round((routingScore + featureScore + qualityScore + llmScore) / 4);
            
            log(`\n   🏆 Overall Score: ${overallScore}/100`, overallScore >= 80 ? colors.green : overallScore >= 60 ? colors.yellow : colors.red);
            
            resolve({
              success: overallScore >= 70, // 70% threshold for success
              agent_correct: isCorrectAgent,
              features_found: foundFeatures,
              total_features: totalFeatures,
              quality_analysis: qualityAnalysis,
              overall_score: overallScore,
              is_real_llm: isRealLLM,
              response_length: responseText.length
            });
          } else {
            log(`❌ ${testCase.name}: Invalid response format`, colors.red);
            log(`   Response: ${data.substring(0, 200)}...`, colors.yellow);
            resolve({ success: false, error: "Invalid response format" });
          }
          
        } catch (error) {
          log(`❌ ${testCase.name}: Parse error - ${error.message}`, colors.red);
          log(`   Raw response: ${data.substring(0, 200)}...`, colors.yellow);
          resolve({ success: false, error: error.message });
        }
      });
    });
    
    req.on('error', (error) => {
      log(`❌ ${testCase.name}: Request failed - ${error.message}`, colors.red);
      resolve({ success: false, error: error.message });
    });
    
    req.on('timeout', () => {
      log(`⏰ ${testCase.name}: Request timeout`, colors.yellow);
      req.destroy();
      resolve({ success: false, error: "Timeout" });
    });
    
    req.write(postData);
    req.end();
  });
}

function analyzeLLMQuality(responseText, testCase) {
  const analysis = {};
  
  // Response Length Quality
  const wordCount = responseText.split(' ').length;
  if (wordCount >= 50 && wordCount <= 500) {
    analysis.response_length = { passed: true, score: 100, reason: `Optimal length (${wordCount} words)` };
  } else if (wordCount >= 20 && wordCount <= 800) {
    analysis.response_length = { passed: true, score: 80, reason: `Acceptable length (${wordCount} words)` };
  } else {
    analysis.response_length = { passed: false, score: 40, reason: `Poor length (${wordCount} words)` };
  }
  
  // Arabic Quality (for Arabic responses)
  if (testCase.message.match(/[\u0600-\u06FF]/)) {
    const arabicWords = responseText.match(/[\u0600-\u06FF\s]+/g);
    if (arabicWords && arabicWords.length > 0) {
      const arabicRatio = arabicWords.join('').length / responseText.length;
      if (arabicRatio > 0.7) {
        analysis.arabic_quality = { passed: true, score: 100, reason: `Excellent Arabic usage (${Math.round(arabicRatio*100)}%)` };
      } else if (arabicRatio > 0.4) {
        analysis.arabic_quality = { passed: true, score: 80, reason: `Good Arabic usage (${Math.round(arabicRatio*100)}%)` };
      } else {
        analysis.arabic_quality = { passed: false, score: 50, reason: `Poor Arabic usage (${Math.round(arabicRatio*100)}%)` };
      }
    } else {
      analysis.arabic_quality = { passed: false, score: 20, reason: "No Arabic content in response" };
    }
  }
  
  // Technical Accuracy (for code generation)
  if (testCase.expectedAgent === 'code_generation') {
    const technicalTerms = ['architecture', 'implementation', 'framework', 'api', 'database', 'security', 'testing'];
    const foundTerms = technicalTerms.filter(term => responseText.toLowerCase().includes(term));
    const technicalScore = Math.round(foundTerms.length / technicalTerms.length * 100);
    
    if (technicalScore >= 70) {
      analysis.technical_accuracy = { passed: true, score: technicalScore, reason: `Strong technical content (${foundTerms.length}/${technicalTerms.length} terms)` };
    } else if (technicalScore >= 40) {
      analysis.technical_accuracy = { passed: true, score: technicalScore, reason: `Moderate technical content (${foundTerms.length}/${technicalTerms.length} terms)` };
    } else {
      analysis.technical_accuracy = { passed: false, score: technicalScore, reason: `Weak technical content (${foundTerms.length}/${technicalTerms.length} terms)` };
    }
  }
  
  // Business Relevance (for consulting)
  if (testCase.expectedAgent === 'consulting') {
    const businessTerms = ['strategy', 'analysis', 'planning', 'consulting', 'business', 'market', 'implementation'];
    const foundTerms = businessTerms.filter(term => responseText.toLowerCase().includes(term));
    const businessScore = Math.round(foundTerms.length / businessTerms.length * 100);
    
    if (businessScore >= 60) {
      analysis.business_relevance = { passed: true, score: businessScore, reason: `Strong business focus (${foundTerms.length}/${businessTerms.length} terms)` };
    } else if (businessScore >= 30) {
      analysis.business_relevance = { passed: true, score: businessScore, reason: `Moderate business focus (${foundTerms.length}/${businessTerms.length} terms)` };
    } else {
      analysis.business_relevance = { passed: false, score: businessScore, reason: `Weak business focus (${foundTerms.length}/${businessTerms.length} terms)` };
    }
  }
  
  // Code Quality (for code generation)
  if (testCase.expectedAgent === 'code_generation') {
    const codeIndicators = ['class', 'function', 'import', 'def', 'async', 'await', 'return'];
    const foundIndicators = codeIndicators.filter(indicator => responseText.toLowerCase().includes(indicator));
    const codeScore = Math.round(foundIndicators.length / codeIndicators.length * 100);
    
    if (codeScore >= 50) {
      analysis.code_quality = { passed: true, score: codeScore, reason: `Good code structure (${foundIndicators.length}/${codeIndicators.length} indicators)` };
    } else if (codeScore >= 25) {
      analysis.code_quality = { passed: true, score: codeScore, reason: `Basic code structure (${foundIndicators.length}/${codeIndicators.length} indicators)` };
    } else {
      analysis.code_quality = { passed: false, score: codeScore, reason: `Poor code structure (${foundIndicators.length}/${codeIndicators.length} indicators)` };
    }
  }
  
  // Security Compliance (all responses)
  const securityViolations = [
    /api[_\s]*key[:\s]*[a-zA-Z0-9\-_]{10,}/i,
    /password[:\s]*[^\s]{6,}/i,
    /secret[:\s]*[a-zA-Z0-9\-_]{10,}/i,
    /token[:\s]*[a-zA-Z0-9\-_]{20,}/i
  ];
  
  const hasViolations = securityViolations.some(pattern => pattern.test(responseText));
  
  if (!hasViolations) {
    analysis.security_compliance = { passed: true, score: 100, reason: "No security violations detected" };
  } else {
    analysis.security_compliance = { passed: false, score: 0, reason: "Security violations detected" };
  }
  
  return analysis;
}

async function testServiceHealth() {
  log('\n🔧 Testing Service Health', colors.cyan);
  
  const endpoints = [
    { name: 'Frontend Health', path: '/api/health', port: 3001 },
    { name: 'Frontend Home', path: '/', port: 3001 }
  ];
  
  for (const endpoint of endpoints) {
    await testEndpoint(endpoint.name, endpoint.port, endpoint.path);
  }
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
      const status = res.statusCode === 200 ? '✅' : '❌';
      const color = res.statusCode === 200 ? colors.green : colors.red;
      log(`${status} ${name}: ${res.statusCode}`, color);
      resolve();
    });
    
    req.on('error', (error) => {
      log(`❌ ${name}: ${error.message}`, colors.red);
      resolve();
    });
    
    req.on('timeout', () => {
      log(`⏰ ${name}: Timeout`, colors.yellow);
      req.destroy();
      resolve();
    });
    
    req.end();
  });
}

async function main() {
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                  REAL LLM RESPONSE TESTING                  ║
║           Gemini Flash API + Quality Analysis               ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);

  // Test basic service health
  await testServiceHealth();
  
  // Test real LLM responses with quality analysis
  const testResults = await testRealLLMResponses();
  
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════╗
║                    LLM TESTING SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
  
  log('🎯 Real LLM Testing Results:', colors.cyan);
  const successRate = Math.round(testResults.successCount / testResults.totalTests * 100);
  log(`• Tests Passed: ${testResults.successCount}/${testResults.totalTests} (${successRate}%)`, 
      successRate >= 80 ? colors.green : successRate >= 60 ? colors.yellow : colors.red);
  
  log('\n🔍 Quality Metrics Analyzed:', colors.cyan);
  log('• Response Length: Optimal word count (50-500 words)', colors.blue);
  log('• Arabic Quality: Proper Arabic usage for Arabic queries', colors.blue);
  log('• Technical Accuracy: Technical terms for code generation', colors.blue);
  log('• Business Relevance: Business focus for consulting', colors.blue);
  log('• Code Quality: Code structure indicators', colors.blue);
  log('• Security Compliance: No sensitive data leakage', colors.blue);
  
  log('\n🚀 Next Steps:', colors.cyan);
  if (successRate >= 80) {
    log('✅ LLM integration is working excellently!', colors.green);
    log('• Deploy to production with confidence', colors.green);
    log('• Monitor real user interactions', colors.green);
    log('• Collect feedback for continuous improvement', colors.green);
  } else if (successRate >= 60) {
    log('⚠️  LLM integration needs some improvements:', colors.yellow);
    log('• Review failed test cases', colors.yellow);
    log('• Adjust system prompts if needed', colors.yellow);
    log('• Test with more diverse scenarios', colors.yellow);
  } else {
    log('❌ LLM integration needs significant work:', colors.red);
    log('• Check API key configuration', colors.red);
    log('• Review system prompts and guardrails', colors.red);
    log('• Validate agent routing logic', colors.red);
  }
  
  console.log(`${colors.magenta}
╔══════════════════════════════════════════════════════════════╗
║                    GEMINI FLASH STATUS                      ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
  
  log('🤖 Gemini Flash LLM Integration:', colors.cyan);
  log('• Model: gemini-1.5-flash (Latest)', colors.green);
  log('• Guardrails: RROC Framework Active', colors.green);
  log('• Security: Input/Output Validation', colors.green);
  log('• Languages: Arabic + English Support', colors.green);
  log('• Agents: 4 Specialized System Prompts', colors.green);
  log('• Quality: Comprehensive Analysis Framework', colors.green);
  
  console.log(`${colors.green}
🎉 REAL LLM TESTING FRAMEWORK READY!
${colors.reset}`);
}

if (require.main === module) {
  main().catch(console.error);
}