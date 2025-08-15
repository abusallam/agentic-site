import { test, expect, Page, BrowserContext } from '@playwright/test';

/**
 * Comprehensive E2E Tests for Agentic Website
 * Tests complete user journeys, chatbot interactions, and multi-language support
 */

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://217.79.255.54:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://217.79.255.54:8001';

// Test data
const TEST_CUSTOMER_DATA = {
  name: 'Test Customer',
  email: 'test@example.com',
  company: 'Test Company',
  phone: '+1234567890',
  requirements: 'Need AI chatbot for customer support'
};

const ARABIC_TEST_MESSAGES = [
  'مرحبا، أحتاج مساعدة في إنشاء موقع إلكتروني',
  'ما هي خدماتكم في مجال الذكاء الاصطناعي؟',
  'أريد تطوير تطبيق جوال للتجارة الإلكترونية',
  'كيف يمكنني أتمتة العمليات التجارية؟'
];

const ENGLISH_TEST_MESSAGES = [
  'Hello, I need help creating a website',
  'What are your AI services?',
  'I want to develop a mobile e-commerce app',
  'How can I automate my business processes?'
];

test.describe('Comprehensive Agentic Website E2E Tests', () => {
  let context: BrowserContext;
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      locale: 'en-US'
    });
    page = await context.newPage();
  });

  test.afterAll(async () => {
    await context.close();
  });

  test.describe('Homepage and Navigation Tests', () => {
    test('should load homepage successfully', async () => {
      await page.goto(BASE_URL);
      
      // Check page loads
      await expect(page).toHaveTitle(/consulting\.sa/i);
      
      // Check main elements are visible
      await expect(page.locator('header')).toBeVisible();
      await expect(page.locator('main')).toBeVisible();
      await expect(page.locator('footer')).toBeVisible();
      
      // Check navigation menu
      await expect(page.locator('nav')).toBeVisible();
      
      // Performance check - page should load within 3 seconds
      const startTime = Date.now();
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(3000);
    });

    test('should navigate to all main pages', async () => {
      await page.goto(BASE_URL);
      
      const pages = [
        { name: 'About', url: '/about' },
        { name: 'Services', url: '/services' },
        { name: 'Contact', url: '/contact' },
        { name: 'Consulting', url: '/consulting' }
      ];
      
      for (const testPage of pages) {
        await page.click(`a[href="${testPage.url}"]`);
        await page.waitForLoadState('networkidle');
        
        // Check URL
        expect(page.url()).toContain(testPage.url);
        
        // Check page content loads
        await expect(page.locator('main')).toBeVisible();
        
        // Check no error messages
        await expect(page.locator('text=Error')).not.toBeVisible();
        await expect(page.locator('text=404')).not.toBeVisible();
      }
    });

    test('should handle language switching', async () => {
      await page.goto(BASE_URL);
      
      // Check for language switcher
      const languageSwitcher = page.locator('[data-testid="language-switcher"]');
      if (await languageSwitcher.isVisible()) {
        // Test Arabic switch
        await languageSwitcher.click();
        await page.click('text=العربية');
        
        // Check RTL layout
        const html = page.locator('html');
        await expect(html).toHaveAttribute('dir', 'rtl');
        
        // Check Arabic content
        await expect(page.locator('text=الرئيسية')).toBeVisible();
        
        // Switch back to English
        await languageSwitcher.click();
        await page.click('text=English');
        
        // Check LTR layout
        await expect(html).toHaveAttribute('dir', 'ltr');
      }
    });
  });

  test.describe('Chatbot Interaction Tests', () => {
    test('should open and close chatbot', async () => {
      await page.goto(BASE_URL);
      
      // Find and click chatbot trigger
      const chatbotTrigger = page.locator('[data-testid="chatbot-trigger"]');
      await expect(chatbotTrigger).toBeVisible();
      await chatbotTrigger.click();
      
      // Check chatbot opens
      const chatbotWidget = page.locator('[data-testid="chatbot-widget"]');
      await expect(chatbotWidget).toBeVisible();
      
      // Check chatbot elements
      await expect(page.locator('[data-testid="chat-messages"]')).toBeVisible();
      await expect(page.locator('[data-testid="chat-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="chat-send-button"]')).toBeVisible();
      
      // Close chatbot
      const closeButton = page.locator('[data-testid="chatbot-close"]');
      await closeButton.click();
      await expect(chatbotWidget).not.toBeVisible();
    });

    test('should handle English chatbot conversations', async () => {
      await page.goto(BASE_URL);
      
      // Open chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      await expect(page.locator('[data-testid="chatbot-widget"]')).toBeVisible();
      
      for (const message of ENGLISH_TEST_MESSAGES) {
        // Type message
        await page.fill('[data-testid="chat-input"]', message);
        await page.click('[data-testid="chat-send-button"]');
        
        // Wait for user message to appear
        await expect(page.locator(`text=${message.substring(0, 20)}`)).toBeVisible();
        
        // Wait for agent response (max 10 seconds)
        await page.waitForSelector('[data-testid="agent-message"]', { timeout: 10000 });
        
        // Check response appears
        const agentMessages = page.locator('[data-testid="agent-message"]');
        await expect(agentMessages.last()).toBeVisible();
        
        // Check response has content
        const responseText = await agentMessages.last().textContent();
        expect(responseText).toBeTruthy();
        expect(responseText!.length).toBeGreaterThan(10);
        
        // Wait a bit between messages
        await page.waitForTimeout(2000);
      }
    });

    test('should handle Arabic chatbot conversations', async () => {
      await page.goto(BASE_URL);
      
      // Switch to Arabic if language switcher exists
      const languageSwitcher = page.locator('[data-testid="language-switcher"]');
      if (await languageSwitcher.isVisible()) {
        await languageSwitcher.click();
        await page.click('text=العربية');
        await page.waitForTimeout(1000);
      }
      
      // Open chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      await expect(page.locator('[data-testid="chatbot-widget"]')).toBeVisible();
      
      for (const message of ARABIC_TEST_MESSAGES) {
        // Type Arabic message
        await page.fill('[data-testid="chat-input"]', message);
        await page.click('[data-testid="chat-send-button"]');
        
        // Wait for user message to appear
        await expect(page.locator(`text=${message.substring(0, 10)}`)).toBeVisible();
        
        // Wait for agent response
        await page.waitForSelector('[data-testid="agent-message"]', { timeout: 15000 });
        
        // Check response appears
        const agentMessages = page.locator('[data-testid="agent-message"]');
        await expect(agentMessages.last()).toBeVisible();
        
        // Check response has Arabic content
        const responseText = await agentMessages.last().textContent();
        expect(responseText).toBeTruthy();
        expect(responseText!.length).toBeGreaterThan(10);
        
        // Check for Arabic characters in response
        const hasArabic = /[\u0600-\u06FF]/.test(responseText!);
        expect(hasArabic).toBeTruthy();
        
        await page.waitForTimeout(2000);
      }
    });

    test('should handle agent routing correctly', async () => {
      await page.goto(BASE_URL);
      
      // Open chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      
      const agentTests = [
        {
          message: 'I need help with workflow automation',
          expectedAgent: 'N8nWorkflowAgent'
        },
        {
          message: 'I want to develop a custom application',
          expectedAgent: 'CodeGenerationAgent'
        },
        {
          message: 'I need business consulting services',
          expectedAgent: 'ConsultingAgent'
        },
        {
          message: 'Hello, I am a new customer',
          expectedAgent: 'InitialCustomerAgent'
        }
      ];
      
      for (const test of agentTests) {
        // Send message
        await page.fill('[data-testid="chat-input"]', test.message);
        await page.click('[data-testid="chat-send-button"]');
        
        // Wait for response
        await page.waitForSelector('[data-testid="agent-message"]', { timeout: 10000 });
        
        // Check agent indicator if available
        const agentIndicator = page.locator('[data-testid="agent-indicator"]');
        if (await agentIndicator.isVisible()) {
          const agentName = await agentIndicator.textContent();
          expect(agentName).toContain(test.expectedAgent);
        }
        
        await page.waitForTimeout(2000);
      }
    });
  });

  test.describe('Form Submission Tests', () => {
    test('should submit contact form successfully', async () => {
      await page.goto(`${BASE_URL}/contact`);
      
      // Fill contact form
      await page.fill('[data-testid="contact-name"]', TEST_CUSTOMER_DATA.name);
      await page.fill('[data-testid="contact-email"]', TEST_CUSTOMER_DATA.email);
      await page.fill('[data-testid="contact-company"]', TEST_CUSTOMER_DATA.company);
      await page.fill('[data-testid="contact-phone"]', TEST_CUSTOMER_DATA.phone);
      await page.fill('[data-testid="contact-message"]', TEST_CUSTOMER_DATA.requirements);
      
      // Submit form
      await page.click('[data-testid="contact-submit"]');
      
      // Check for success message
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible({ timeout: 10000 });
      
      // Check form is reset or redirected
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/(contact|thank-you|success)/);
    });

    test('should handle form validation errors', async () => {
      await page.goto(`${BASE_URL}/contact`);
      
      // Submit empty form
      await page.click('[data-testid="contact-submit"]');
      
      // Check for validation errors
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      
      // Check specific field errors
      await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    });

    test('should submit consultation request', async () => {
      await page.goto(`${BASE_URL}/consulting`);
      
      // Fill consultation form
      await page.fill('[data-testid="consultation-name"]', TEST_CUSTOMER_DATA.name);
      await page.fill('[data-testid="consultation-email"]', TEST_CUSTOMER_DATA.email);
      await page.fill('[data-testid="consultation-company"]', TEST_CUSTOMER_DATA.company);
      await page.selectOption('[data-testid="consultation-service"]', 'ai-development');
      await page.fill('[data-testid="consultation-requirements"]', TEST_CUSTOMER_DATA.requirements);
      
      // Submit consultation request
      await page.click('[data-testid="consultation-submit"]');
      
      // Check for success
      await expect(page.locator('[data-testid="consultation-success"]')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Responsive Design Tests', () => {
    const viewports = [
      { name: 'Desktop', width: 1920, height: 1080 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Mobile', width: 375, height: 667 }
    ];

    for (const viewport of viewports) {
      test(`should work correctly on ${viewport.name}`, async () => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(BASE_URL);
        
        // Check page loads
        await expect(page.locator('main')).toBeVisible();
        
        // Check navigation (mobile might have hamburger menu)
        if (viewport.width < 768) {
          // Mobile navigation
          const mobileMenu = page.locator('[data-testid="mobile-menu-trigger"]');
          if (await mobileMenu.isVisible()) {
            await mobileMenu.click();
            await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
          }
        } else {
          // Desktop navigation
          await expect(page.locator('nav')).toBeVisible();
        }
        
        // Check chatbot works on all devices
        await page.click('[data-testid="chatbot-trigger"]');
        await expect(page.locator('[data-testid="chatbot-widget"]')).toBeVisible();
        
        // Test a quick message
        await page.fill('[data-testid="chat-input"]', 'Hello');
        await page.click('[data-testid="chat-send-button"]');
        await page.waitForSelector('[data-testid="agent-message"]', { timeout: 10000 });
        
        // Close chatbot
        await page.click('[data-testid="chatbot-close"]');
      });
    }
  });

  test.describe('Performance Tests', () => {
    test('should meet performance benchmarks', async () => {
      const startTime = Date.now();
      
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // Page should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
      
      // Check Core Web Vitals if available
      const performanceMetrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const metrics: any = {};
            
            entries.forEach((entry) => {
              if (entry.entryType === 'navigation') {
                const navEntry = entry as PerformanceNavigationTiming;
                metrics.loadTime = navEntry.loadEventEnd - navEntry.loadEventStart;
                metrics.domContentLoaded = navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart;
              }
            });
            
            resolve(metrics);
          }).observe({ entryTypes: ['navigation'] });
          
          // Fallback timeout
          setTimeout(() => resolve({}), 1000);
        });
      });
      
      console.log('Performance metrics:', performanceMetrics);
    });

    test('should handle concurrent chatbot interactions', async () => {
      await page.goto(BASE_URL);
      
      // Open chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      
      // Send multiple messages quickly
      const messages = ['Hello', 'How are you?', 'What services do you offer?'];
      
      for (const message of messages) {
        await page.fill('[data-testid="chat-input"]', message);
        await page.click('[data-testid="chat-send-button"]');
        // Don't wait between messages to test concurrent handling
      }
      
      // Wait for all responses
      await page.waitForFunction(
        () => document.querySelectorAll('[data-testid="agent-message"]').length >= 3,
        {},
        { timeout: 30000 }
      );
      
      // Check all messages received responses
      const agentMessages = page.locator('[data-testid="agent-message"]');
      const messageCount = await agentMessages.count();
      expect(messageCount).toBeGreaterThanOrEqual(3);
    });
  });

  test.describe('Accessibility Tests', () => {
    test('should meet basic accessibility requirements', async () => {
      await page.goto(BASE_URL);
      
      // Check for proper heading structure
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check for alt text on images
      const images = page.locator('img');
      const imageCount = await images.count();
      
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const alt = await img.getAttribute('alt');
        expect(alt).toBeTruthy();
      }
      
      // Check for proper form labels
      const inputs = page.locator('input[type="text"], input[type="email"], textarea');
      const inputCount = await inputs.count();
      
      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const id = await input.getAttribute('id');
        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          await expect(label).toBeVisible();
        }
      }
      
      // Check keyboard navigation
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should support screen reader navigation', async () => {
      await page.goto(BASE_URL);
      
      // Check for ARIA landmarks
      await expect(page.locator('[role="main"], main')).toBeVisible();
      await expect(page.locator('[role="navigation"], nav')).toBeVisible();
      await expect(page.locator('[role="contentinfo"], footer')).toBeVisible();
      
      // Check for proper ARIA labels on interactive elements
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      
      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const ariaLabel = await button.getAttribute('aria-label');
        const textContent = await button.textContent();
        
        // Button should have either aria-label or text content
        expect(ariaLabel || textContent).toBeTruthy();
      }
    });
  });

  test.describe('Error Handling Tests', () => {
    test('should handle network errors gracefully', async () => {
      await page.goto(BASE_URL);
      
      // Simulate network failure
      await page.route('**/api/**', route => route.abort());
      
      // Try to use chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="chat-send-button"]');
      
      // Should show error message
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 10000 });
      
      // Should not crash the application
      await expect(page.locator('main')).toBeVisible();
    });

    test('should handle invalid routes', async () => {
      await page.goto(`${BASE_URL}/invalid-route`);
      
      // Should show 404 page or redirect
      const is404 = await page.locator('text=404').isVisible();
      const isRedirected = !page.url().includes('invalid-route');
      
      expect(is404 || isRedirected).toBeTruthy();
      
      // Should still have navigation
      await expect(page.locator('nav')).toBeVisible();
    });
  });

  test.describe('Security Tests', () => {
    test('should sanitize user input', async () => {
      await page.goto(BASE_URL);
      
      // Open chatbot
      await page.click('[data-testid="chatbot-trigger"]');
      
      // Try XSS attack
      const maliciousScript = '<script>alert("XSS")</script>';
      await page.fill('[data-testid="chat-input"]', maliciousScript);
      await page.click('[data-testid="chat-send-button"]');
      
      // Wait for message to appear
      await page.waitForTimeout(2000);
      
      // Check that script is not executed (no alert dialog)
      const dialogs: string[] = [];
      page.on('dialog', dialog => {
        dialogs.push(dialog.message());
        dialog.dismiss();
      });
      
      await page.waitForTimeout(1000);
      expect(dialogs).toHaveLength(0);
      
      // Check that message is properly escaped
      const messageText = await page.locator('[data-testid="user-message"]').last().textContent();
      expect(messageText).toContain('&lt;script&gt;');
    });

    test('should validate form inputs', async () => {
      await page.goto(`${BASE_URL}/contact`);
      
      // Try SQL injection
      await page.fill('[data-testid="contact-name"]', "'; DROP TABLE users; --");
      await page.fill('[data-testid="contact-email"]', 'invalid-email');
      await page.click('[data-testid="contact-submit"]');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
      
      // Should not crash or show database errors
      await expect(page.locator('text=SQL')).not.toBeVisible();
      await expect(page.locator('text=database')).not.toBeVisible();
    });
  });
});

// Helper functions for complex interactions
async function waitForChatResponse(page: Page, timeout = 10000) {
  await page.waitForSelector('[data-testid="agent-message"]', { timeout });
  
  // Wait for typing indicator to disappear if present
  const typingIndicator = page.locator('[data-testid="typing-indicator"]');
  if (await typingIndicator.isVisible()) {
    await expect(typingIndicator).not.toBeVisible({ timeout: 5000 });
  }
}

async function testAgentResponse(page: Page, message: string, expectedKeywords: string[] = []) {
  await page.fill('[data-testid="chat-input"]', message);
  await page.click('[data-testid="chat-send-button"]');
  
  await waitForChatResponse(page);
  
  const response = await page.locator('[data-testid="agent-message"]').last().textContent();
  expect(response).toBeTruthy();
  expect(response!.length).toBeGreaterThan(10);
  
  // Check for expected keywords if provided
  for (const keyword of expectedKeywords) {
    expect(response!.toLowerCase()).toContain(keyword.toLowerCase());
  }
  
  return response;
}