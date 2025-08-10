# 🧪 Automated Testing Strategy with Playwright

## Overview

This document outlines the comprehensive automated testing strategy for the agentic platform using Playwright for end-to-end testing, with integration to Context7 MCP for enhanced testing knowledge and capabilities.

## 🎯 Testing Objectives

### Primary Goals
1. **End-to-End Validation**: Complete user journey testing from frontend to backend
2. **Agent Workflow Testing**: Validate all agentic workflows and handoffs
3. **Multi-language Testing**: Test both Arabic and English interfaces
4. **Performance Validation**: Ensure response times and system performance
5. **Integration Testing**: Validate all service integrations (Supabase, LangFuse, N8N)

### Success Criteria
- **Coverage**: 90%+ critical user journeys covered
- **Reliability**: 95%+ test pass rate in CI/CD pipeline
- **Performance**: All tests complete within 10 minutes
- **Maintainability**: Tests are easy to update and maintain

## 🏗️ Testing Architecture

### Test Structure
```
tests/
├── e2e/                    # End-to-end tests
│   ├── user-journeys/      # Complete user workflows
│   ├── agent-interactions/ # AI agent testing
│   ├── billing/           # Billing agent tests
│   └── admin/             # Admin interface tests
├── integration/           # Service integration tests
│   ├── supabase/         # Database integration
│   ├── langfuse/         # AI metrics integration
│   └── n8n/              # Workflow integration
├── performance/          # Performance and load tests
├── visual/              # Visual regression tests
└── fixtures/            # Test data and utilities
```

### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'https://consulting.sa',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
});
```

## 🤖 Agent Testing Framework

### AI Agent Test Suite
```typescript
// tests/e2e/agent-interactions/billing-agent.spec.ts
import { test, expect } from '@playwright/test';
import { BillingAgentTestHelper } from '../helpers/billing-agent-helper';

test.describe('Billing Agent Interactions', () => {
  let billingHelper: BillingAgentTestHelper;

  test.beforeEach(async ({ page }) => {
    billingHelper = new BillingAgentTestHelper(page);
    await billingHelper.navigateToChat();
  });

  test('should handle Arabic billing inquiry', async ({ page }) => {
    // Test Arabic interaction
    await billingHelper.sendMessage('أريد معرفة استخدام الموارد هذا الشهر');
    
    // Verify Arabic response
    const response = await billingHelper.getLastResponse();
    expect(response).toContain('ملخص استخدام الموارد');
    expect(response).toContain('ريال سعودي');
  });

  test('should generate invoice correctly', async ({ page }) => {
    // Login as test customer
    await billingHelper.loginAsTestCustomer();
    
    // Request invoice generation
    await billingHelper.sendMessage('Generate invoice for this month');
    
    // Verify invoice creation
    const response = await billingHelper.getLastResponse();
    expect(response).toContain('Invoice generated successfully');
    expect(response).toMatch(/INV-\d{8}-[A-Z0-9]{8}/);
  });

  test('should setup automated billing', async ({ page }) => {
    await billingHelper.loginAsTestCustomer();
    
    // Request billing setup
    await billingHelper.sendMessage('Setup monthly automated billing');
    
    // Follow setup flow
    await billingHelper.selectBillingCycle('monthly');
    
    // Verify setup completion
    const confirmation = await billingHelper.getLastResponse();
    expect(confirmation).toContain('Automated billing setup');
  });
});
```

### Agent Workflow Testing
```typescript
// tests/e2e/agent-interactions/agent-handoff.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Agent Handoff Workflows', () => {
  test('should route customer to appropriate agent', async ({ page }) => {
    await page.goto('/');
    
    // Start chat
    await page.click('[data-testid="chat-widget"]');
    
    // Send message indicating need for custom solution
    await page.fill('[data-testid="chat-input"]', 'I need a custom AI solution for my business');
    await page.click('[data-testid="send-button"]');
    
    // Verify routing to professional agent
    await expect(page.locator('[data-testid="agent-type"]')).toContainText('Professional Agent');
    
    // Verify appropriate response
    const response = await page.locator('[data-testid="last-message"]').textContent();
    expect(response).toContain('requirement');
  });

  test('should handle live agent handoff', async ({ page }) => {
    await page.goto('/');
    
    // Start chat and request human agent
    await page.click('[data-testid="chat-widget"]');
    await page.fill('[data-testid="chat-input"]', 'I want to talk to a human');
    await page.click('[data-testid="send-button"]');
    
    // Verify handoff options presented
    await expect(page.locator('[data-testid="handoff-options"]')).toBeVisible();
    
    // Click connect now
    await page.click('[data-testid="connect-now"]');
    
    // Verify Livekit integration
    await expect(page.locator('[data-testid="live-session"]')).toBeVisible();
  });
});
```

## 🌐 Multi-language Testing

### Arabic-First Testing
```typescript
// tests/e2e/localization/arabic-interface.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Arabic Interface Testing', () => {
  test('should default to Arabic language', async ({ page }) => {
    await page.goto('/');
    
    // Verify Arabic is default
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    
    // Verify Arabic content
    await expect(page.locator('h1')).toContainText('حوّل عملك بحلول الذكاء الاصطناعي');
  });

  test('should switch to English correctly', async ({ page }) => {
    await page.goto('/');
    
    // Switch to English
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-en"]');
    
    // Verify English content
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('h1')).toContainText('Transform Your Business with AI Solutions');
  });

  test('should maintain language preference', async ({ page }) => {
    await page.goto('/');
    
    // Switch to English
    await page.click('[data-testid="language-switcher"]');
    await page.click('[data-testid="lang-en"]');
    
    // Navigate to another page
    await page.click('[data-testid="nav-services"]');
    
    // Verify language persisted
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });
});
```

## 💰 Billing System Testing

### Comprehensive Billing Tests
```typescript
// tests/e2e/billing/billing-workflows.spec.ts
import { test, expect } from '@playwright/test';
import { BillingTestData } from '../fixtures/billing-data';

test.describe('Billing System Workflows', () => {
  test('should track resource usage accurately', async ({ page }) => {
    // Setup test customer with known usage
    const testCustomer = await BillingTestData.createTestCustomer();
    await BillingTestData.addResourceUsage(testCustomer.id, {
      compute: 10.5,
      storage: 25.0,
      ai_tokens: 1000
    });
    
    // Login and check usage
    await page.goto('/dashboard');
    await page.fill('[data-testid="login-email"]', testCustomer.email);
    await page.fill('[data-testid="login-password"]', 'testpassword');
    await page.click('[data-testid="login-submit"]');
    
    // Navigate to billing
    await page.click('[data-testid="nav-billing"]');
    
    // Verify usage display
    await expect(page.locator('[data-testid="compute-usage"]')).toContainText('10.5 hours');
    await expect(page.locator('[data-testid="storage-usage"]')).toContainText('25.0 GB');
    await expect(page.locator('[data-testid="tokens-usage"]')).toContainText('1000 tokens');
    
    // Verify cost calculation
    const expectedCost = (10.5 * 0.05) + (25.0 * 0.10) + (1 * 0.002);
    await expect(page.locator('[data-testid="total-cost"]')).toContainText(expectedCost.toString());
  });

  test('should generate invoice with correct VAT', async ({ page }) => {
    const testCustomer = await BillingTestData.createTestCustomerWithUsage();
    
    // Login as admin
    await page.goto('/admin');
    await page.fill('[data-testid="admin-login"]', 'admin@consulting.sa');
    await page.fill('[data-testid="admin-password"]', process.env.ADMIN_PASSWORD);
    await page.click('[data-testid="admin-login-submit"]');
    
    // Generate invoice
    await page.click('[data-testid="billing-management"]');
    await page.fill('[data-testid="customer-search"]', testCustomer.email);
    await page.click('[data-testid="generate-invoice"]');
    
    // Verify invoice details
    await expect(page.locator('[data-testid="invoice-subtotal"]')).toBeVisible();
    await expect(page.locator('[data-testid="invoice-vat"]')).toContainText('15%');
    
    // Verify VAT calculation
    const subtotal = await page.locator('[data-testid="invoice-subtotal"]').textContent();
    const vatAmount = await page.locator('[data-testid="invoice-vat-amount"]').textContent();
    const total = await page.locator('[data-testid="invoice-total"]').textContent();
    
    const expectedVat = parseFloat(subtotal) * 0.15;
    expect(parseFloat(vatAmount)).toBeCloseTo(expectedVat, 2);
  });
});
```

## 🔄 Cron Job Testing

### Automation Testing
```typescript
// tests/integration/cron-jobs/billing-automation.spec.ts
import { test, expect } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

test.describe('Billing Automation', () => {
  test('should create cron jobs correctly', async () => {
    // Test cron job creation
    const { stdout } = await execAsync('crontab -l');
    
    // Verify billing cron jobs exist
    expect(stdout).toContain('automated_billing.py');
    expect(stdout).toContain('resource_monitoring.py');
  });

  test('should execute billing script successfully', async () => {
    // Execute billing script manually
    const { stdout, stderr } = await execAsync('/opt/agentic/scripts/automated_billing.py test_customer');
    
    // Verify successful execution
    expect(stderr).toBe('');
    expect(stdout).toContain('Generated invoice');
  });
});
```

## 📊 Performance Testing

### Load Testing with Playwright
```typescript
// tests/performance/load-testing.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Performance Testing', () => {
  test('should handle concurrent users', async ({ browser }) => {
    const contexts = await Promise.all(
      Array.from({ length: 10 }, () => browser.newContext())
    );
    
    const pages = await Promise.all(
      contexts.map(context => context.newPage())
    );
    
    // Simulate concurrent user interactions
    const startTime = Date.now();
    
    await Promise.all(
      pages.map(async (page, index) => {
        await page.goto('/');
        await page.click('[data-testid="chat-widget"]');
        await page.fill('[data-testid="chat-input"]', `Test message ${index}`);
        await page.click('[data-testid="send-button"]');
        
        // Wait for response
        await page.waitForSelector('[data-testid="agent-response"]');
      })
    );
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Verify performance requirements
    expect(duration).toBeLessThan(10000); // 10 seconds max
    
    // Cleanup
    await Promise.all(contexts.map(context => context.close()));
  });

  test('should meet response time requirements', async ({ page }) => {
    await page.goto('/');
    
    // Measure page load time
    const navigationTiming = await page.evaluate(() => {
      return JSON.parse(JSON.stringify(performance.getEntriesByType('navigation')[0]));
    });
    
    const loadTime = navigationTiming.loadEventEnd - navigationTiming.fetchStart;
    expect(loadTime).toBeLessThan(1500); // 1.5 seconds max
  });
});
```

## 🎨 Visual Regression Testing

### Visual Testing Setup
```typescript
// tests/visual/visual-regression.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('should match homepage design', async ({ page }) => {
    await page.goto('/');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Take screenshot and compare
    await expect(page).toHaveScreenshot('homepage.png');
  });

  test('should match Arabic interface', async ({ page }) => {
    await page.goto('/');
    
    // Ensure Arabic is active
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
    
    // Take screenshot
    await expect(page).toHaveScreenshot('homepage-arabic.png');
  });

  test('should match billing dashboard', async ({ page }) => {
    // Login as test user
    await page.goto('/auth/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'testpassword');
    await page.click('[data-testid="submit"]');
    
    // Navigate to billing
    await page.goto('/dashboard/billing');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await expect(page).toHaveScreenshot('billing-dashboard.png');
  });
});
```

## 🔧 Test Utilities and Helpers

### Billing Agent Test Helper
```typescript
// tests/helpers/billing-agent-helper.ts
import { Page, expect } from '@playwright/test';

export class BillingAgentTestHelper {
  constructor(private page: Page) {}

  async navigateToChat() {
    await this.page.goto('/');
    await this.page.click('[data-testid="chat-widget"]');
    await this.page.waitForSelector('[data-testid="chat-interface"]');
  }

  async sendMessage(message: string) {
    await this.page.fill('[data-testid="chat-input"]', message);
    await this.page.click('[data-testid="send-button"]');
    await this.page.waitForSelector('[data-testid="agent-response"]');
  }

  async getLastResponse(): Promise<string> {
    const responses = await this.page.locator('[data-testid="agent-response"]').all();
    const lastResponse = responses[responses.length - 1];
    return await lastResponse.textContent() || '';
  }

  async loginAsTestCustomer() {
    await this.page.goto('/auth/login');
    await this.page.fill('[data-testid="email"]', 'test.customer@example.com');
    await this.page.fill('[data-testid="password"]', 'testpassword123');
    await this.page.click('[data-testid="submit"]');
    await this.page.waitForURL('/dashboard');
  }

  async selectBillingCycle(cycle: 'monthly' | 'quarterly' | 'yearly') {
    const cycleMap = {
      monthly: '1',
      quarterly: '2',
      yearly: '3'
    };
    
    await this.sendMessage(cycleMap[cycle]);
    await this.page.waitForSelector('[data-testid="billing-setup-confirmation"]');
  }

  async verifyInvoiceGenerated(invoiceNumber: string) {
    await expect(this.page.locator(`[data-testid="invoice-${invoiceNumber}"]`)).toBeVisible();
  }
}
```

### Test Data Management
```typescript
// tests/fixtures/billing-data.ts
export class BillingTestData {
  static async createTestCustomer() {
    return {
      id: 'test_customer_' + Date.now(),
      email: 'test.customer@example.com',
      name: 'Test Customer',
      billing_address: {
        street: '123 Test St',
        city: 'Riyadh',
        country: 'Saudi Arabia'
      }
    };
  }

  static async addResourceUsage(customerId: string, usage: any) {
    // Add test resource usage data
    // This would integrate with the actual billing system
  }

  static async createTestCustomerWithUsage() {
    const customer = await this.createTestCustomer();
    await this.addResourceUsage(customer.id, {
      compute: 15.0,
      storage: 50.0,
      ai_tokens: 2500,
      agent_hours: 2.0
    });
    return customer;
  }
}
```

## 🚀 CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-node@v3
      with:
        node-version: 18
        
    - name: Install dependencies
      run: npm ci
      
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
      
    - name: Run Playwright tests
      run: npx playwright test
      env:
        BASE_URL: ${{ secrets.STAGING_URL }}
        
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
```

## 📈 Test Reporting and Analytics

### Test Results Dashboard
- **Test Coverage**: Track test coverage across all features
- **Performance Metrics**: Monitor test execution times
- **Failure Analysis**: Detailed failure reports with screenshots and videos
- **Trend Analysis**: Track test reliability over time

### Integration with Context7 MCP
The testing framework integrates with Context7 MCP to:
- **Knowledge Enhancement**: Access testing best practices and patterns
- **Dynamic Test Generation**: Generate tests based on system changes
- **Intelligent Debugging**: AI-powered test failure analysis
- **Test Optimization**: Optimize test suites for better performance

## 🔄 Maintenance and Updates

### Test Maintenance Strategy
1. **Regular Review**: Monthly review of test effectiveness
2. **Update Automation**: Automatic test updates when UI changes
3. **Performance Monitoring**: Continuous monitoring of test execution times
4. **Coverage Analysis**: Regular analysis of test coverage gaps

### Best Practices
- **Page Object Model**: Use page objects for maintainable tests
- **Data-Driven Testing**: Parameterize tests with different data sets
- **Parallel Execution**: Run tests in parallel for faster feedback
- **Retry Logic**: Implement smart retry logic for flaky tests
- **Environment Management**: Separate test environments for different test types

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: Ready for Implementation  
**Next Steps**: Begin test implementation with Playwright setup